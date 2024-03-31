import cv2
import random
import numpy as np

import data.loaders.dl_config as dl_cfg
import data.loaders.dataloader as dl
import data.visualize.plotting as plot


def inspect_parser():
    import argparse
    pars = argparse.ArgumentParser(description='Data augmentation and dataset visualization. '
                                               'Press Q to quit,'
                                               'N to visualize the next image'
                                               ' and any other key to visualize the next default data.')
    pars.add_argument('database', type=str,
                      choices=['wflw', '300wpublic', '300wprivate', 'cofw68', 'merlrav', 'sftl54'], help='Database name')
    pars.add_argument('-a', '--anns', type=str, default='train', help='Annotation type: test, train or valid')
    pars.add_argument('-np', '--nopose', action='store_false', default=True, help='Avoid pose generation')
    pars.add_argument('-c', '--clean', action='store_true', help='Process without data augmentation for train')
    pars.add_argument('--shape', nargs='+', type=int, default=[256, 256], help='Image cropped shape (W,H)')
    pars.add_argument('--img', nargs='+', type=int, default=None, help='Select specific image ids')
    return pars.parse_args()


class DatasetInspector:

    def __init__(self, database, anns_type, data_aug=True, pose=True, image_shape=(256,256)):

        data_config = dl_cfg.AlignConfig(database, anns_type)
        data_config.image_size = image_shape
        data_config.ftmap_size = image_shape
        data_config.generate_pose = pose

        if not data_aug:
            data_config.aug_names = []

        self.data_config = data_config
        dataloader, dataset = dl.get_dataloader(1, data_config, debug=True)
        self.dataset = dataset
        self.dataloader = dataloader
        self.colors_dft = {'lnd': (plot.GREEN, plot.RED), 'pose': (plot.BLUE, plot.GREEN, plot.RED)}

    def show_dataset(self, ids_list=None):

        if ids_list is None:
            ids = self.get_idx(shuffle=self.data_config.shuffle)
        else:
            ids = ids_list

        for img_id in ids:
            data_dict = self.dataset[img_id]
            crop_imgs, full_img = self.plot_features(data_dict)

            # Plot crop
            if 'merge' in crop_imgs.keys():
                crop = crop_imgs['merge']
            else:
                crop = crop_imgs['lnd']
            cv2.imshow('crop', crop)

            # Plot full
            cv2.imshow('image', full_img['lnd'])

            key = cv2.waitKey()
            if key == ord('q'):
                break

    def plot_features(self, data_dict, colors=None):

        # Init variables
        crop_imgs = {}
        full_imgs = {}
        if colors is None:
            colors = self.colors_dft

        # Cropped image
        image = data_dict['image']
        landmarks = data_dict['landmarks']
        visible = data_dict['visible']
        if np.any(np.isnan(visible)):
            visible = None
        mask = data_dict['mask_ldm']

        # Full image
        if 'image_ori' in data_dict.keys():
            image_ori = data_dict['image_ori']
        else:
            image_ori = cv2.imread(data_dict['imgpath'])
        landmarks_ori = data_dict['landmarks_ori']
        visible_ori = data_dict['visible_ori']
        if np.any(np.isnan(visible_ori)):
            visible_ori = None
        mask_ori = data_dict['mask_ldm_ori']

        # Plot landmarks
        crop_imgs['lnd'] = self._plot_lnd(image, landmarks, visible, mask, colors=colors['lnd'])
        full_imgs['lnd'] = self._plot_lnd(image_ori, landmarks_ori, visible_ori, mask_ori, colors=colors['lnd'])

        if self.data_config.generate_pose:
            rot, trl, cam_matrix = self._extract_pose(data_dict)

            # Plot pose
            crop_imgs['pose'] = plot.draw_pose(image, rot, trl, cam_matrix, euler=True, colors=colors['pose'])

            # Plot merge features
            crop_imgs['merge'] = plot.draw_pose(crop_imgs['lnd'], rot, trl, cam_matrix, euler=True, colors=colors['pose'])

        return crop_imgs, full_imgs

    def get_idx(self, shuffle=False):
        ids = list(range(len(self.dataset)))
        if shuffle:
            random.shuffle(ids)
        return ids

    def reload_dataset(self, data_config=None):
        if data_config is None:
            data_config = self.data_config
        dataloader, dataset = dl.get_dataloader(1, data_config, debug=True)
        self.dataset = dataset
        self.dataloader = dataloader

    def _extract_pose(self, data_dict):
        # Rotation and translation matrix
        pose = data_dict['pose']
        rot = pose[:3]
        trl = pose[3:]

        # Camera matrix
        cam_matrix = data_dict['cam_matrix']

        # Check for ground truth anns
        if 'headpose_ori' in data_dict.keys():
            if len(self.data_config.aug_names) == 0:
                print('Image headpose generated by ground truth data')
                pose_ori = data_dict['headpose_ori']
                rot = pose_ori

        return rot, trl, cam_matrix

    def _plot_lnd(self, image, landmarks, visible, mask, max_shape_thr=720, colors=None):

        if colors is None:
            colors = self.colors_dft['lnd']

        # Full image plots
        W, H, C = image.shape

        # Original image resize if need it
        if W > max_shape_thr or H > max_shape_thr:
            max_shape = max(W, H)
            scale_factor = max_shape_thr / max_shape
            resize_shape = (int(H * scale_factor), int(W * scale_factor))
            image_out = plot.draw_landmarks(image, landmarks, visible=visible, mask=mask,
                                            thick_scale=1 / scale_factor, colors=colors)
            image_out = cv2.resize(image_out, resize_shape)
        else:
            image_out = plot.draw_landmarks(image, landmarks, visible=visible, mask=mask, colors=colors)

        return image_out


if __name__ == '__main__':
    args = inspect_parser()
    data_aug = True
    database = args.database
    anns_type = args.anns
    pose = args.nopose
    select_img = args.img
    if args.clean:
        data_aug = False

    if len(args.shape) != 2:
        raise ValueError('--shape requires two values: width and height. Ej: --shape 256 256')
    else:
        img_shape = tuple(args.shape)

    visualizer = DatasetInspector(database, anns_type, data_aug=data_aug, pose=pose, image_shape=img_shape)
    visualizer.show_dataset(ids_list=select_img)

