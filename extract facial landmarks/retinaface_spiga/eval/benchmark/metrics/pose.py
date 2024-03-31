import numpy as np
from sklearn.metrics import confusion_matrix

from eval.benchmark.metrics.metrics import Metrics


class MetricsHeadpose(Metrics):

    def __init__(self, name='headpose'):
        super().__init__(name)

        # Angles
        self.angles = ['yaw', 'pitch', 'roll']
        # Confusion matrix intervals
        self.pose_labels = [-90, -75, -60, -45, -30, -15, 0, 15, 30, 45, 60, 75, 90]
        # Percentile reference angles
        self.error_labels = [2.5, 5, 10, 15, 30]
        # Cumulative plot axis length
        self.bins = 1000

    def compute_error(self, data_anns, data_pred, database, select_ids=None):

        # Initialize global logs and variables of Computer Error function
        self.init_ce(data_anns, data_pred, database)

        # Generate annotations if needed
        if data_anns[0]['headpose'] is None:
            print('Database anns generated by posit...')
            data_anns = self._posit_anns()
            print('Posit generation done...')

        # Dictionary variables
        self.error['data_pred'] = []
        self.error['data_anns'] = []
        self.error['data_pred_trl'] = []
        self.error['data_anns_trl'] = []
        self.error['mae_ypr'] = []
        self.error['mae_mean'] = []

        # Order data
        for img_id, img_anns in enumerate(data_anns):
            pose_anns = img_anns['headpose'][0:3]
            self.error['data_anns'].append(pose_anns)
            pose_pred = data_pred[img_id]['headpose'][0:3]
            self.error['data_pred'].append(pose_pred)

        # Compute MAE error
        anns_array = np.array(self.error['data_anns'])
        pred_array = np.array(self.error['data_pred'])
        mae_ypr = np.abs((anns_array-pred_array))
        self.error['mae_ypr'] = mae_ypr.tolist()
        self.error['mae_mean'] = np.mean(mae_ypr, axis=-1).tolist()

        # Quantize labeled data
        label_anns = self._nearest_label(anns_array)
        label_pred = self._nearest_label(pred_array)
        self.error['label_anns'] = label_anns
        self.error['label_pred'] = label_pred

        for angle_id, angle in enumerate(self.angles):
            # Confusion matrix
            self.error['cm_%s' % angle] = confusion_matrix(label_anns[:, angle_id], label_pred[:, angle_id])
            # Cumulative error
            self.error['cumulative_%s' % angle] = self._cumulative_error(mae_ypr[:, angle_id], bins=self.bins)

        return self.error

    def metrics(self):

        # Initialize global logs and variables of Metrics function
        self.init_metrics()

        # Mean Absolute Error
        mae_ypr = np.array(self.error['mae_ypr'])
        mae_ypr_mean = np.mean(mae_ypr, axis=0)
        self.metrics_log['mae_ypr'] = mae_ypr_mean.tolist()
        self.metrics_log['mae_mean'] = np.mean(mae_ypr_mean)
        print('MAE [yaw, pitch, roll]: [%.3f, %.3f, %.3f]' % (mae_ypr_mean[0], mae_ypr_mean[1], mae_ypr_mean[2]))
        print('MAE mean: %.3f' % self.metrics_log['mae_mean'])

        # Per angle measurements
        self.metrics_log['acc_label'] = []
        self.metrics_log['acc_adj_label'] = []

        for angle_id, angle in enumerate(self.angles):

            # Accuracy per label
            cm = self.error['cm_%s' % angle]
            diagonal = np.diagonal(cm, offset=0).sum()
            acc_main = diagonal / cm.sum().astype('float')
            self.metrics_log['acc_label'].append(acc_main)

            # Permissive accuracy
            diagonal_adj = diagonal.sum() + np.diagonal(cm, offset=-1).sum() + np.diagonal(cm, offset=1).sum()
            acc_adj = diagonal_adj / cm.sum().astype('float')
            self.metrics_log['acc_adj_label'].append(acc_adj)

            # Percentile of relevant angles
            self.metrics_log['sr_%s' % angle] = {}
            for angle_num in self.error_labels:
                if max(mae_ypr[:, angle_id]) > angle_num:
                    [cumulative, base] = self.error['cumulative_%s' % angle]
                    perc = [cumulative[x[0] - 1] for x in enumerate(base) if x[1] > angle_num][0]
                else:
                    perc = 1.

                self.metrics_log['sr_%s' % angle][angle_num] = perc

        print('Accuracy [yaw, pitch, roll]: ', self.metrics_log['acc_label'])
        print('Accuracy [yaw, pitch, roll] (adjacency as TP): ', self.metrics_log['acc_adj_label'])
        for angle in self.angles:
            print('Success Rate %s: ' % angle, self.metrics_log['sr_%s' % angle])

        return self.metrics_log

    def get_pimg_err(self, data_dict, img_select=None):
        mae_mean = self.error['mae_mean']
        mae_ypr = self.error['mae_ypr']
        if img_select is not None:
            mae_mean = [mae_mean[img_id] for img_id in img_select]
            mae_ypr = [mae_ypr[img_id] for img_id in img_select]
        name_dict = self.name + '/%s'
        data_dict[name_dict % 'mae'] = mae_mean
        mae_ypr = np.array(mae_ypr)
        data_dict[name_dict % 'mae_yaw'] = mae_ypr[:, 0].tolist()
        data_dict[name_dict % 'mae_pitch'] = mae_ypr[:, 1].tolist()
        data_dict[name_dict % 'mae_roll'] = mae_ypr[:, 2].tolist()
        return data_dict

    def _posit_anns(self):

        import data.loaders.dl_config as dl_config
        import data.loaders.dataloader as dl

        # Load configuration
        data_config = dl_config.AlignConfig(self.database, self.data_type)
        data_config.image_size = (256, 256)
        data_config.generate_pose = True
        data_config.aug_names = []
        data_config.shuffle = False
        dataloader, _ = dl.get_dataloader(1, data_config, debug=True)

        data_anns = []
        for num_batch, batch_dict in enumerate(dataloader):
            pose = batch_dict['pose'].numpy()
            data_anns.append({'headpose': pose[0].tolist()})
        return data_anns

    def _nearest_label(self, data):
        data_tile = data[:, :, np.newaxis]
        data_tile = np.tile(data_tile, len(self.pose_labels))
        diff_tile = np.abs(data_tile - self.pose_labels)
        label_idx = diff_tile.argmin(axis=-1)
        return label_idx

    def _cumulative_error(self, error, bins=1000):
        num_imgs, base = np.histogram(error, bins=bins)
        cumulative = [x / float(len(error)) for x in np.cumsum(num_imgs)]
        return [cumulative[:bins], base[:bins]]
