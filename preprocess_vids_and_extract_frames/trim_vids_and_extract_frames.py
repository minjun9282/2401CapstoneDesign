from moviepy.editor import VideoFileClip
from PIL import Image
import os
import numpy as np
from concurrent.futures import ProcessPoolExecutor

# 비디오 처리를 수행하는 함수를 정의
def process_video(video_path, output_frame_path, base_video_frames, front_adjustment, resize_size, fps):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    frames_folder = os.path.join(output_frame_path, video_name + '_frames')
    os.makedirs(frames_folder, exist_ok=True)

    with VideoFileClip(video_path) as video:
        # 영상의 앞부분이 기준 영상보다 짧을 경우 시작 부분에 추가될 검은색 프레임의 수 계산
        front_black_frames = int(abs(front_adjustment) * fps) if front_adjustment < 0 else 0

        # 영상의 앞부분이 기준 영상보다 짧을 경우 시작 부분에 추가될 검은색 프레임
        black_frame = np.zeros((video.size[1], video.size[0], 3), dtype=np.uint8)

        for i in range(base_video_frames): #추출될 프레임의 갯수를 base_video_frames의 갯수에 맞춰줌
            if front_black_frames != 0 and i < front_black_frames:
                frame = black_frame
            else:
                frame_time = i / fps - abs(front_adjustment) if front_adjustment < 0 else i / fps + front_adjustment
                frame = video.get_frame(frame_time)

            frame_image = Image.fromarray(frame).resize(resize_size, Image.Resampling.LANCZOS)
            frame_path = os.path.join(frames_folder, f"frame_{i:05d}.jpg")
            frame_image.save(frame_path, 'JPEG', quality=95)

def trim_and_extract_frames_parallel(input_video_paths, output_frame_paths, front_adjustment_lst, back_adjustment_lst, resize_size, fps=30):
    video_files = [f for f in os.listdir(input_video_paths) if f.endswith('.mp4')]
    video_paths = [os.path.join(input_video_paths, f) for f in video_files]

    base_video = VideoFileClip(video_paths[0])
    base_video_frames = int((base_video.duration - back_adjustment_lst[0]) * fps)

    # 병렬 처리를 위해 ProcessPoolExecutor 사용
    with ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(process_video, video_path, output_frame_paths, base_video_frames, front_adjustment_lst[idx], resize_size, fps)
            for idx, video_path in enumerate(video_paths)
        ]

        # 모든 작업이 완료될 때까지 기다림
        for future in futures:
            future.result()  # 에러가 발생하면 여기서 발생함

