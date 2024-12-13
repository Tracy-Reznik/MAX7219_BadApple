import os

import cv2
import numpy as np
import serial
import time
import pygame  # 用于音频播放
from config import BAUD_RATE, SERIAL_PORT
from lib.lib import send_matrix, matrix_to_dot_matrix


# device_name = ""
# os.environ['SDL_AUDIODRIVER'] = device_name

def video_to_binary_frames_with_padding(video_path, target_size=(32, 16), output_path=None):
    """
    读取视频文件，将所有帧缩放为目标高度，在两侧填充黑边后转为二值化 32×16 矩阵帧。
    """
    target_width, target_height = target_size

    # 打开视频文件
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"无法打开视频文件: {video_path}")

    # 获取视频帧率
    fps = cap.get(cv2.CAP_PROP_FPS)

    # 初始化存储帧的列表
    frame_list = []

    while True:
        # 读取每一帧
        ret, frame = cap.read()
        if not ret:
            break  # 视频读取结束

        # 转为灰度图
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 缩放并填充/裁剪为目标尺寸
        scale = target_height / gray_frame.shape[0]
        new_width = int(gray_frame.shape[1] * scale)
        resized_frame = cv2.resize(gray_frame, (new_width, target_height), interpolation=cv2.INTER_AREA)
        if new_width < target_width:
            padding = (target_width - new_width) // 2
            padded_frame = cv2.copyMakeBorder(
                resized_frame, 0, 0, padding, target_width - new_width - padding, cv2.BORDER_CONSTANT, value=0
            )
        else:
            start_x = (new_width - target_width) // 2
            padded_frame = resized_frame[:, start_x:start_x + target_width]

        # 二值化处理
        _, binary_frame = cv2.threshold(padded_frame, 128, 1, cv2.THRESH_BINARY)

        # 转换为点阵格式并存入列表
        frame_list.append(binary_frame)

    # 释放视频对象
    cap.release()

    # 保存帧数据和帧率到文件
    if output_path:
        data = {'frames': frame_list, 'fps': fps}  # 使用字典存储帧数据和帧率
        np.save(output_path, data, allow_pickle=True)  # 保存为 .npy 文件

    return frame_list, fps


def load_binary_frames(file_path):
    """
    从文件加载二值化的帧数据和帧率。
    """
    data = np.load(file_path, allow_pickle=True).item()  # 加载并转换为字典
    frames = data['frames']
    fps = data['fps']
    return frames, fps


def play_audio(audio_path):
    """
    播放伴音文件。
    """
    pygame.mixer.init()  # 初始化音频模块
    pygame.mixer.music.load(audio_path)
    pygame.mixer.music.play()


def main():
    # 设置路径
    video_path = 'badapple.mp4'
    audio_path = f'{video_path}_audio.mp3'
    frame_data_path = f'{video_path}_frames.npy'

    # 加载或生成帧数据
    try:
        frames, fps = load_binary_frames(frame_data_path)
        if not os.path.isfile(audio_path):
            raise FileNotFoundError("Audio is not a file")
    except FileNotFoundError:
        frames, fps = video_to_binary_frames_with_padding(video_path, output_path=frame_data_path)

    # 打开串口并发送视频帧
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
            play_audio(audio_path)
            print("串口已打开，开始发送数据...")

            # 使用音频时间控制视频帧发送
            frame_interval = 1 / fps  # 每帧间隔时间
            total_frames = len(frames)

            while pygame.mixer.music.get_busy():  # 当音乐还在播放时
                audio_time = pygame.mixer.music.get_pos() / 1000.0  # 获取音频播放时间（秒）
                current_frame = int(audio_time / frame_interval)  # 计算应发送的当前帧

                if current_frame < total_frames:
                    send_matrix(ser, matrix_to_dot_matrix(frames[current_frame]))
                else:
                    break  # 如果当前帧超出总帧数，停止发送
    except serial.SerialException as e:
        print(f"串口打开失败: {e}")


if __name__ == "__main__":
    while True:
        try:
            main()
            time.sleep(2)
        except KeyboardInterrupt:
            print("播放已中断")
            exit()
