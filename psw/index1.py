import requests
import os
import time

os.chdir("psw")

url_video = "http://43.201.154.195:5000/normalvideo/upload"
video_dir = "videos"

# 이전에 보낸 비디오 파일 목록 가져오기
prev_video_files = [
    os.path.join(video_dir, f) for f in os.listdir(video_dir) if f.endswith(".mp4")
]

while True:
    # 전송하기전 5분간 기다림
    # time.sleep(300)

    # 새 비디오 파일 목록 가져오기
    new_video_files = [
        os.path.join(video_dir, f)
        for f in os.listdir(video_dir)
        if f.endswith(".mp4") and f not in prev_video_files
    ]

    # 중복되지 않은 비디오 파일만 업로드
    for video_file in new_video_files:
        file_name = os.path.basename(video_file)
        video = {"normalvideo": open(video_file, "rb")}
        response = requests.post(url_video, files=video)
        print(f"{file_name} uploaded. Server response: {response.text}")

        # 업로드한 비디오 파일을 이전에 업로드한 비디오 파일 목록에 추가
        prev_video_files.append(file_name)

    time.sleep(374)

    # 통신 결과 및 내용 확인용
    print(response.status_code)
    print(response.text)