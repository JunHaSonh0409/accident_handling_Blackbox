import RPi.GPIO as IO
import time
import datetime
from moviepy.video.io.VideoFileClip import VideoFileClip
import os

# 디렉토리 경로
dir_path = "videos"
cut_path = "ShockVideos"
# os.chdir("psw")


def find_path():
    print(os.getcwd())

    # 디렉토리 내 모든 파일과 디렉토리의 이름을 얻습니다.
    file_list = os.listdir(dir_path)

    # 가장 최근에 수정된 파일의 이름과 수정 시간을 저장할 변수를 초기화합니다.
    recent_file_name = ""
    recent_mod_time = 0.0

    # 파일 목록을 반복하면서 수정 시간이 가장 최근인 파일을 찾습니다.
    for file_name in file_list:
        file_path = os.path.join(dir_path, file_name)
        mod_time = os.path.getmtime(file_path)
        if mod_time > recent_mod_time:
            recent_file_name = file_name
            recent_mod_time = mod_time

    return recent_file_name


def cut_video(file_name):
    # 비디오 클립 객체 생성
    video = VideoFileClip(os.path.join(dir_path, file_name))

    # 동영상의 총 길이(초) 계산
    total_seconds = video.duration

    # 자를 시작 시간과 끝 시간
    start_time = total_seconds - 10  # 초
    end_time = total_seconds  # 초

    # 자를 부분 추출
    cut_video = video.subclip(start_time, end_time)

    return cut_video


def save_video(video):
    now = datetime.datetime.now()
    filename = now.strftime("%Y%m%d_%H%M%S") + ".mp4"

    # 자른 비디오 파일 저장
    # moviepy를 사용해 동영상을 저장할때는 꼭 코덱 설정을 해줘야 한다
    # 코덱 설정을 안해주면 이상한 디렉토리가 맞지 않는다고 나오거나
    # keyerror: codec
    # 2개중에 무슨 에러가 나올지 모름
    video.write_videofile(os.path.join(cut_path, filename), codec="mpeg4")


def button(channel):
    recent_file_name_button = find_path()

    cut = cut_video(recent_file_name_button)

    save_video(cut)


def setting_pin():
    IO.setmode(IO.BCM)
    IO.setwarnings(False)
    button_pin = 14

    IO.setup(button_pin, IO.IN, pull_up_down=IO.PUD_DOWN)
    IO.add_event_detect(button_pin, IO.RISING, callback=button, bouncetime=300)


def main():
    setting_pin()
    while 1:
        time.sleep(0.1)


main()
