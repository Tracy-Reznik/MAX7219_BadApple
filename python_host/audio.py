import time

import numpy as np
import sounddevice as sd
import serial

from config import SERIAL_PORT, BAUD_RATE
from lib.lib import matrix_to_dot_matrix, send_matrix


def get_channel_frequency_levels(data, samplerate, num_bands=16, freq_range=(20, 20000)):
    """
    计算音频数据在指定频率范围内每个频率段的能量。
    """
    fft_data = np.fft.rfft(data)  # 计算FFT（只取正频部分）
    fft_magnitude = np.abs(fft_data)  # 取FFT的幅值
    freq_bins = np.fft.rfftfreq(len(data), 1 / samplerate)  # 计算频率对应的频率范围

    # 筛选目标频率范围
    min_freq, max_freq = freq_range
    valid_indices = np.where((freq_bins >= min_freq) & (freq_bins <= max_freq))[0]
    fft_magnitude = fft_magnitude[valid_indices]
    freq_bins = freq_bins[valid_indices]

    # 将目标频率范围划分为 num_bands 个频率段
    levels = np.zeros(num_bands)
    band_edges = np.linspace(min_freq, max_freq, num_bands + 1)  # 每个频率段的边界
    for i in range(num_bands):
        # 在当前频率段内计算平均能量值
        indices = np.where((freq_bins >= band_edges[i]) & (freq_bins < band_edges[i + 1]))[0]
        if len(indices) > 0:
            levels[i] = np.mean(fft_magnitude[indices])
    return levels


import numpy as np

def audio_to_matrix(left_levels, right_levels, rows=16, cols=32):
    """
    将左右声道频率范围的能量转换为点阵矩阵。
    每段频率范围占两列，左声道占左 16 列，右声道占右 16 列。
    音量越大，亮的部分越多（从顶部开始填充），并进行高度动态缩放。
    """
    matrix = np.zeros((rows, cols), dtype=np.uint8)

    # 每段占两列，共 8 段
    segments = 8
    cols_per_segment = 2

    # 动态范围压缩函数
    def scale_level(level, max_level):
        if max_level <= 0:
            return 0
        return np.log10(1 + level) / np.log10(1 + max_level)

    # 左声道
    max_left = np.max(left_levels) if len(left_levels) > 0 else 1  # 使用 np.max()
    for i, level in enumerate(left_levels):
        scaled_height = scale_level(level, max_left) * rows
        height = int(scaled_height)
        start_col = i * cols_per_segment
        matrix[:height, start_col:start_col + cols_per_segment] = 1  # 从顶部填充两列

    # 右声道
    max_right = np.max(right_levels) if len(right_levels) > 0 else 1  # 使用 np.max()
    for i, level in enumerate(right_levels):
        scaled_height = scale_level(level, max_right) * rows
        height = int(scaled_height)
        start_col = 16 + i * cols_per_segment  # 右声道从第 16 列开始
        matrix[:height, start_col:start_col + cols_per_segment] = 1  # 从顶部填充两列

    # 反转矩阵值：0 -> 1, 1 -> 0
    matrix = 1 - matrix

    return matrix




def main():
    # 打开串口
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
        print("串口已打开，开始显示音频频谱...")

        # 初始化音频流
        stream = sd.InputStream(channels=2, samplerate=44100, dtype='float32', blocksize=1024)
        stream.start()

        try:
            while True:
                # 读取左右声道数据
                audio_data = stream.read(stream.blocksize)[0]
                left_channel = audio_data[:, 0]
                right_channel = audio_data[:, 1]

                # 获取左右声道频率范围的能量
                left_levels = get_channel_frequency_levels(left_channel, stream.samplerate, freq_range=(0, 20000))
                right_levels = get_channel_frequency_levels(right_channel, stream.samplerate, freq_range=(0, 20000))

                # 转换为点阵矩阵
                matrix = audio_to_matrix(left_levels, right_levels)
                dot_matrix = matrix_to_dot_matrix(matrix)

                # 发送到点阵屏
                send_matrix(ser, dot_matrix)
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("显示已中断")
        finally:
            stream.stop()


if __name__ == "__main__":
    main()
