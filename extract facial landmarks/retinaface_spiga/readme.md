face detection: Retinaface
facial landmarks 및 head position 추출: SPIGA

preprocess_vids_and_extract_frames의 결과로 생성된 프레임 폴더를 input 폴더로 설정
retinaface_demo.py와 spiga_demo.py의 input 폴더에 경로 설정 해줘야 함.
실행순서: retinaface_demo.py 실행 -> spiga_demo.py 실행

Retinaface 실행시 주의
- onnxruntime말고 onnxruntime-gpu로 설치해야 cuda 동작 가능
- insightface, opencv-python 설치하기
- https://forums.developer.nvidia.com/t/could-not-load-library-cudnn-cnn-infer64-8-dll-error-code-193/218437/16<br>
여기서 zlib123dllx64.zip 파일 다운 받은 후에 압축 풀어서 zlibwapi.dll파일을  c:/program files/nvidia gpu computin toolkit/cuda/v11.6/bin폴더에 복사해서 넣어줘야 cuda 동작됨. (v11.6은 우리가 설치한 버전)

Spiga 실행시 주의
dataset으로 300wpublic을 사용했음.
