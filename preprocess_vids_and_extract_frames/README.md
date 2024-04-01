# 설명
아이돌 무대영상을 입력 받아 오디오 싱크를 맞춘 프레임을 추출합니다.

1. intput_videos의 폴더에 들어있는 mp4 영상들에 대해 길이가 짧은 순서로 정렬합니다.
2. 길이가 짧은 순서대로 1.mp4 2.mp4 ...로 이름을 변경한 후 output_videos에 저장합니다.
3. output_videos에 있는 영상들로부터 audio track을 추출합니다
4. 추출한 audio track을 cross-correlation을 활용하여 1.mp4와 나머지 영상들간의 음악이 시작하는 부분의 time delay를 계산합니다.
5. 계산한 time delay를 활용하여 오디오 싱크를 맞춘 후 frames을 추출합니다.

# 조건
input_videos는 동일한 가수의 동일한 음악으로 이루어진 무대영상이어야 합니다.(29.97fps, 44100Hz)

# 주의
moviepy를 설치해야 합니다.
input_videos, output_videos, output_audios, output_frames 폴더가 존재해야 합니다.(추후 폴더 생성하도록 수정 예정)

 
# 디렉토리 구조
```
├── preprocess_vides_and_extract_frames
    ├── preprocess_vides_and_extract_frames.ipynb
    ├── trim_vids_and_extract_frames.py
    ├── input_videos
    ├── output_videos
    ├── output_audios
    └── output_frames
```
