from flask import Flask, render_template, request, jsonify
import numpy as np
import serial
import time

from config import SERIAL_PORT, BAUD_RATE
from lib.lib import matrix_to_dot_matrix



# 初始化串口
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# 初始化 Flask 应用
app = Flask(__name__)

# 通过串口发送点阵数据
def send_to_screen(dot_matrix):
    for row in dot_matrix:
        ser.write(row.tobytes())
    ser.flush()

# 首页路由
@app.route('/')
def index():
    return render_template('index.html')

# 接收自定义图案
@app.route('/update', methods=['POST'])
def update():
    data = request.json.get('matrix')
    if not data or len(data) != 16 or any(len(row) != 32 for row in data):
        return jsonify({'error': 'Invalid matrix format'}), 400
    # 转换为 NumPy 矩阵
    matrix = np.array(data, dtype=np.uint8)
    # 转换为点阵数据并发送
    dot_matrix = matrix_to_dot_matrix(matrix)
    send_to_screen(dot_matrix)
    return jsonify({'message': 'Matrix updated successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
