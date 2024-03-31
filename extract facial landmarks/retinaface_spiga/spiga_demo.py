# 이미지 처리 및 저장을 위한 함수 정의
import cv2
import json
import numpy as np
import os
import torch

from inference.config import ModelConfig
from inference.framework import SPIGAFramework
from demo.visualize.plotter import Plotter

# SPIGA 프로세스 실행
dataset = '300wpublic' #wflw는 오류가 발생하여 이거 사용함.
processor = SPIGAFramework(ModelConfig(dataset))

def process_and_save_image(image_path, bbox_path, output_path, dataset, processor):
    # 이미지와 bbox 정보 로드
    image = cv2.imread(image_path)
    with open(bbox_path) as jsonfile:
        bbox_data = json.load(jsonfile)
    
    # bbox가 없으면 처리 중단
    if not bbox_data['bbox']:
        print(f"{image_path}에서 bbox가 검출되지 않음")
        cv2.imwrite(output_path, image) #bbox 검출되지 않을 경우 원본 이미지 저장
        return

    canvas = image.copy()
    
    # SPIGA 프로세스 실행 (모든 bbox 처리)
    for bbox in bbox_data['bbox']:
        
        # 결과 이미지 준비
        x0, y0, w, h = bbox
        bbox_corrected = (int(x0), int(y0), int(w-x0), int(h-y0))
        features = processor.inference(image, [bbox_corrected])

        x0,y0,w,h = bbox_corrected

        landmarks = np.array(features['landmarks'][0])
        headpose = np.array(features['headpose'][0])
        
        # 특징 시각화
        plotter = Plotter()
        canvas = plotter.landmarks.draw_landmarks(canvas, landmarks, thick=3)
        canvas = plotter.hpose.draw_headpose(canvas, [x0, y0, x0 + w, y0 + h], headpose[:3], headpose[3:], euler=True)
    
    # 결과 이미지 저장
    cv2.imwrite(output_path, canvas)

# 입력 및 출력 폴더 설정
input_folder = 'omg_1min'
bbox_data_folder = 'bbox_data'
output_folder = 'processed_images'  # 처리된 이미지를 저장할 폴더

# 출력 폴더가 없으면 생성
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# bbox data 입력 폴더에서 JSON 파일 목록 가져오기
bbox_files = [f for f in os.listdir(bbox_data_folder) if f.endswith('.json')]

# 이미지 입력 폴더에서 jpg 파일 목록 가져오기
img_files = [f for f in os.listdir(input_folder) if f.endswith('.jpg')]

# 각 bbox 파일에 대한 처리
for img_file in img_files:
    bbox_file = img_file.replace('jpg', 'json')
    process_and_save_image(os.path.join(input_folder, img_file),
                           os.path.join(bbox_data_folder, bbox_file),
                           os.path.join(output_folder, img_file),
                           dataset,
                           processor)
                        

print("모든 이미지의 처리 및 저장 완료")