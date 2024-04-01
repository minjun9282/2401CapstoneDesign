face detection: Retinaface<br>
facial landmarks 및 head position 추출: SPIGA<br>

<br>
preprocess_vids_and_extract_frames의 결과로 생성된 프레임 폴더를 retinaface_spiga에 복사하여 input 폴더로 설정<br>
retinaface_demo.py와 spiga_demo.py의 input 폴더에 경로 설정 위에 복사한걸로 바꿔줘야 함.<br>
실행순서: retinaface_demo.py 실행 -> spiga_demo.py 실행<br>
결과물: retinaface_demo.py -> bbox_data(annotation 폴더), spiga_demo.py -> processed_image(inference 결과물)<br>

추후에는 inference 결과물을 이미지로 저장하지 않고 값만 받아서 사용할 것임.<br>

<br>
Retinaface 실행시 주의<br>
- onnxruntime말고 onnxruntime-gpu로 설치해야 cuda 동작 가능<br>
- insightface, opencv-python 설치하기<br>
- https://forums.developer.nvidia.com/t/could-not-load-library-cudnn-cnn-infer64-8-dll-error-code-193/218437/16<br>
여기서 zlib123dllx64.zip 파일 다운 받은 후에 압축 풀어서 zlibwapi.dll파일을  c:/program files/nvidia gpu computin toolkit/cuda/v11.6/bin폴더에 복사해서 넣어줘야 cuda 동작됨. (v11.6은 우리가 설치한 버전)
<br>
<br>
Spiga 실행시 주의<br>
- dataset으로 300wpublic을 사용했음.<br>
- models/weights 폴더를 만든 후 spiga_300wpublic.pt 파일을 추가해줘야함.<br>
- 모델 weights 불러오는데 계속 오류가 발생한다면 아래의 링크에서 직접 다운 받은 후 models/weights 폴더에 넣기
- https://drive.google.com/drive/folders/1olrkoiDNK_NUCscaG9BbO3qsussbDi7I
