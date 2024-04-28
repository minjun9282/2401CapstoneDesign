import cv2
import json
import numpy as np
import os
import torch

from inference.config import ModelConfig
from inference.framework import SPIGAFramework

#GPU 사용 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# SPIGA 프로세스 실행
dataset = '300wpublic'
processor = SPIGAFramework(ModelConfig(dataset))

def process_and_save_features(image_path, bbox_path, output_path, processor, min_size=20000): #일단 min_size = 20000으로 두고 모든 얼굴 크기에 대해서 추출(1280*720 기준)
    # 이미지와 bbox 정보 로드
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    image_center = np.array([width / 2, height / 2])

    with open(bbox_path) as jsonfile:
        bbox_data = json.load(jsonfile)
    
    # bbox가 없거나 빈 리스트인 경우 처리 중단
    if not bbox_data['bbox']:
        print(f"{image_path}에서 bbox가 검출되지 않음")
        return

    # bbox 중심과 크기 조건을 충족하는지 확인
    selected_bbox = None
    min_distance_to_center = float('inf')
    num_faces = 0
    for bbox in bbox_data['bbox']:
        num_faces += 1
        x_min, y_min, x_max, y_max = bbox
        if (x_max - x_min) * (y_max - y_min) < min_size:
            continue  # 크기가 min_size보다 작은 경우 건너뛰기
        
        bbox_center = np.array([(x_min + x_max) / 2, (y_min + y_max) / 2])
        distance = np.linalg.norm(bbox_center - image_center)

        if distance < min_distance_to_center:
            selected_bbox = (x_min, y_min, x_max, y_max)
            min_distance_to_center = distance

    # 선택된 bbox가 있는 경우만 처리
    if selected_bbox:
        x_min, y_min, x_max, y_max = selected_bbox
        bbox_corrected = (int(x_min), int(y_min), int(x_max-x_min), int(y_max-y_min)) #x, y, w, h형태로 변환
        features = processor.inference(image, [bbox_corrected])

        headpose = features['headpose'][0]

        landmarks_data = [{
            'num_faces': num_faces,
            'bbox': [x_min, y_min, x_max, y_max],
            'headpose': headpose
        }]

        with open(output_path, 'w') as outfile:
            json.dump(landmarks_data, outfile, indent=4)
    else:
        print(f"{image_path}에서 조건에 맞는 bbox가 없습니다.")
        
# 입력 및 출력 폴더 설정
input_folder = 'output_frames'
bbox_data_folder = 'bbox_data'
output_folder = 'features_data'  # Landmark 데이터를 저장할 폴더

# 각 서브폴더의 이미지에 대해 처리
subfolders = [f for f in os.listdir(input_folder) if os.path.isdir(os.path.join(input_folder, f))]
for subfolder in subfolders:
    subfolder_path = os.path.join(input_folder, subfolder)
    bbox_subfolder_path = os.path.join(bbox_data_folder, subfolder)
    output_subfolder_path = os.path.join(output_folder, subfolder)
    
    if not os.path.exists(output_subfolder_path):
        os.makedirs(output_subfolder_path)
    
    img_files = [f for f in os.listdir(subfolder_path) if f.endswith('.jpg')]
    for img_file in img_files:
        bbox_file = img_file.replace('jpg', 'json')
        json_output_path = os.path.join(output_subfolder_path, bbox_file)
        image_path = os.path.join(subfolder_path, img_file)
        bbox_path = os.path.join(bbox_subfolder_path, bbox_file)
        
        process_and_save_features(image_path, bbox_path, json_output_path, processor)

print("모든 이미지의 랜드마크 데이터 처리 및 저장 완료")
