#include <LedControl.h>

// 定义 MAX7219 的连接引脚
#define DIN_PIN PA7   // 数据输入引脚 (MOSI)
#define CLK_PIN PA5   // 时钟引脚 (SCK)
#define CS_PIN PA4    // 片选引脚 (SS)

// 定义串联的 MAX7219 数量
#define NUM_MAX7219 8

// 创建 LedControl 实例
LedControl lc = LedControl(DIN_PIN, CLK_PIN, CS_PIN, NUM_MAX7219);

// 定义16x32点阵图片的二值矩阵 (每字节8个像素，高位在上)
byte image[16][4] = {0};

// 初始化 MAX7219
void setup() {
  Serial.begin(2000000); // 初始化串口通信，波特率为115200
  for (int i = 0; i < NUM_MAX7219; i++) {
    lc.shutdown(i, false);      // 打开显示
    lc.setIntensity(i, 8);      // 设置亮度（0-15）
    lc.clearDisplay(i);         // 清空显示
  }
}

// 显示图片
void displayImage() {
  for (int row = 0; row < 16; row++) {
    for (int colGroup = 0; colGroup < 4; colGroup++) {
      byte data = image[row][colGroup];
      int chip = colGroup + (row / 8) * 4;   // 计算芯片编号
      int rowInChip = row % 8;               // 芯片内行号
      lc.setRow(chip, 7-rowInChip, data);    // 写入数据
    }
  }
}

// 接收并解析串口数据
void receiveMatrix() {
  if (Serial.available() >= 64) { // 确保有完整一帧的数据（16x4字节）
    for (int row = 0; row < 16; row++) {
      for (int col = 0; col < 4; col++) {
        image[row][col] = Serial.read(); // 从串口读取数据
      }
    }
  }
}

void loop() {
  static unsigned long lastUpdate = 0;
  receiveMatrix(); // 从串口接收新数据
  displayImage();  // 刷新显示
}
