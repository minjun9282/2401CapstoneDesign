# 다중 무대 영상의 시각적 특징을 활용한 자동 교차편집 시스템
# 프로젝트 소개
- 전문적인 편집 기술과 긴 편집 시간의 노력 없어도 다수의 무대 영상을 활용하여 자연스러운 교차편집 영상을 만들 수 있는 프로젝트입니다. <br>

# 프로젝트 배경
- K-pop 아이돌의 무대 영상을 교차 편집한 영상은 팬들이 좋아하는 가수의 콘텐츠를 재생산해가며 즐기는 K-pop 문화의 일종입니다.
- 그러나 하나의 교차편집 영상을 만드는 데는 전문적인 편집자가 수동으로 10시간 내외의 시간을 들여야하는 고된 작업입니다.
- 이런 제약 때문에 교차편집 영상은 전문적인 편집자들에게도 부담이 되고 직접 교차편집 영상을 만들고 싶어 하는 팬들에게는 더욱이 시도하기 어려운 작업이다.
  이에 저희는 사용자가 여러 무대 영상을 업로드하면 자동으로 교차편집 영상을 생성해주는 서비스를 개발했습니다.

# 핵심 기능 소개
## 무대 영상 입력시 전처리 과정 자동화
- 입력 영상에서 오디오를 추출한 후 waveform의 correlation 비교를 통해 모든 영상의 오디오 싱크를 맞춘 후 영상 길이를 동일하게 조정합니다.
- 조정된 길이의 입력 영상들로부터 1920*1080 사이즈의 프레임을 29.97fps 속도로 추출합니다.

## RetinaFace 및 SPIGA를 활용한 feature 추출
- RetinaFace를 활용하여 프레임에서 얼굴을 식별합니다
- 식별된 얼굴에 대해 SPIGA를 활용하여 headpose estimation을 진행합니다.
- 추출한 headpose feature은 서로 다른 무대의 프레임에서 유사한 얼굴을 찾은 후 얼굴을 기반으로한 장면 전환 편집에 활용됩니다.

## Histogram correlation과 식별된 얼굴의 IoU 비교를 통한 샷 경계 검출
- 각 무대에서 샷 경계를 검출한 후 해당 장면을 앞뒤로 얼굴 기반 장면 전환이 포함되지 않도록 합니다.

## Dijkstra algorithm을 활용한 편집 경로 생성
- 교차편집에서 사용하는 전환 유형을 크게 4가지로 구분합니다. Face based transition, inter-stage cutting, intra-stage cutting, None.
- 각 프레임을 (현재 무대 번호, 현재 프레임 번호): (다음 무대 번호, 다음 프레임 번호, 전환 유형, 전환 비용)의 그래프 구조로 표현합니다.
- Dijkstra algorithm을 활용하여 최소 비용을 갖는 편집 경로를 생성합니다.

## 편집 경로를 활용한 편집 수행
- Face based transition이 이뤄지는 구간을 pre-blending, blending, post-blending의 세 구간으로 나눕니다.
- blending 구간에서는 alpha composting과 눈의 랜드마크를 활용한 얼굴 정렬을 활용해 서로 다른 두 무대 영상을 자연스럽게 연결합니다.
- inter-stage cutting과 intra-stage cutting, None은 편집 효과 없이 다음 프레임으로 전환합니다.


<br>

# 프로젝트 구조<br>
- 추후 다시 업데이트 할 예정입니다.
```
├── preprocess vids and extract frames
│   ├── preprocess_vids_and_extract_frames.ipynb
│   └── trim_vids_and_extract_frames.py
└── extract_facial_landmarks
    ├── retinaface_demo.py
    ├── spiga_feature_extract_demo.py
    ├── shot_boundaries_detection.py
    ├── find_editing_path.py
    └── make_stagemix.py


```
# 데모 영상
aespa - supernova: https://drive.google.com/drive/folders/1uiYlu6Nvfont8vSe_Zlp0IDtdWysA9_e
newjeans - how sweet: https://drive.google.com/drive/folders/1uiYlu6Nvfont8vSe_Zlp0IDtdWysA9_e
ive - heya: https://drive.google.com/drive/folders/1uiYlu6Nvfont8vSe_Zlp0IDtdWysA9_e

<br><br>
