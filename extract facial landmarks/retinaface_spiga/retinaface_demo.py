import cv2
import os
import json
import insightface
from insightface.app import FaceAnalysis

# FaceAnalysis 객체 초기화
app = FaceAnalysis(providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
app.prepare(ctx_id=0, det_size=(640, 640)) #ctx_id=0으로 설정해야 0번째 gpu사용

input_folder = 'omg_1min'  # 입력 이미지가 있는 폴더
bbox_folder = 'bbox_data'  # bbox 정보를 저장할 폴더

# bbox 폴더가 없으면 생성
if not os.path.exists(bbox_folder):
    os.makedirs(bbox_folder)

# 입력 폴더에서 이미지 파일 목록 가져오기
image_files = [f for f in os.listdir(input_folder) if f.endswith('.jpg') or f.endswith('.png')]

# 각 이미지에 대한 처리 및 bbox 정보 저장
for image_file in image_files:
    image_path = os.path.join(input_folder, image_file)
    img = cv2.imread(image_path)
    
    # 얼굴 감지
    faces = app.get(img)
    
    # 감지된 얼굴에 대한 bbox 정보 저장
    bboxes = [face.bbox.astype(int).tolist() for face in faces]
    
    # bbox 정보 저장
    bbox_file_path = os.path.join(bbox_folder, image_file.replace('.jpg', '.json'))
    with open(bbox_file_path, 'w') as f:
        json.dump({"bbox": bboxes}, f)

print("모든 이미지에 대한 bbox 정보 저장 완료")
