import time

import numpy as np
import serial

import config
import lib.lib


matrix = np.zeros((16, 32), dtype=np.uint8)
with serial.Serial(config.SERIAL_PORT, config.BAUD_RATE, timeout=1) as ser:
    while True:
        for i in range(16):
            matrix[i].fill(int(1))
            lib.lib.send_matrix(ser, lib.lib.matrix_to_dot_matrix(matrix=matrix))
            # time.sleep(0.1)
        for j in range(32):
            matrix[:, j].fill(int(0))
            lib.lib.send_matrix(ser, lib.lib.matrix_to_dot_matrix(matrix=matrix))
            # time.sleep(0.02)
        for i in range(16):
            matrix[15 - i].fill(int(1))
            lib.lib.send_matrix(ser, lib.lib.matrix_to_dot_matrix(matrix=matrix))
            # time.sleep(0.01)
        for j in range(32):
            matrix[:, 31 - j].fill(int(0))
            lib.lib.send_matrix(ser, lib.lib.matrix_to_dot_matrix(matrix=matrix))
            # time.sleep(0.2)

        for i in range(16):
            for j in range(32):
                matrix = np.zeros((16, 32), dtype=np.uint8)
                matrix[i, j] = 1
                lib.lib.send_matrix(ser, lib.lib.matrix_to_dot_matrix(matrix=matrix))
        matrix = np.zeros((16, 32), dtype=np.uint8)
        lib.lib.send_matrix(ser, lib.lib.matrix_to_dot_matrix(matrix=matrix))
        for i in range(16):
            for j in range(32):
                matrix[i, j] = 1
                lib.lib.send_matrix(ser, lib.lib.matrix_to_dot_matrix(matrix=matrix))

        for i in range(16):
            matrix[15 - i].fill(int(0))
            lib.lib.send_matrix(ser, lib.lib.matrix_to_dot_matrix(matrix=matrix))
            # time.sleep(0.01)
        for j in range(32):
            matrix[:, 31 - j].fill(int(1))
            lib.lib.send_matrix(ser, lib.lib.matrix_to_dot_matrix(matrix=matrix))
