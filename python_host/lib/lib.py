import numpy as np


def send_matrix(serial_port, dot_matrix):
    """
    通过串口发送点阵矩阵数据。
    """
    for row in dot_matrix:
        serial_port.write(row.tobytes())
def matrix_to_dot_matrix(matrix):
    """
    将16x32的二值矩阵转换为点阵数据格式。
    每4列数据压缩成1个字节，共4列形成一个8位的点阵。
    """
    if matrix.shape != (16, 32):
        raise ValueError("矩阵尺寸必须为16x32")

    dot_matrix = np.zeros((16, 4), dtype=np.uint8)
    for row in range(16):  # 遍历16行
        for col_group in range(4):  # 每8列分为一组，共4组
            byte_value = 0  # 初始化字节
            for bit in range(8):  # 遍历当前组的8位
                # 直接拼接成8位的字符串
                byte_value = byte_value * 2 + matrix[row, col_group * 8 + bit]
            binary_str = f"{byte_value:08b}"  # 补齐到8位
            reversed_str = binary_str[::-1]
            reversed_n = int(reversed_str, 2)
            dot_matrix[row, col_group] = reversed_n
    return dot_matrix
