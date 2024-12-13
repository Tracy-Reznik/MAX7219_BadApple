# MAX7219_BadApple

本项目是基于Arduino框架和Python语言，采用MAX7219实现的BadApple点阵屏



## 项目结构

- 项目根目录
  - python_host/ （上位机程序）
    - badapple.py（badapple程序）
    - canva.py（网页点阵绘画面板）
    - config.py（参数配置文件）
    - lib/
      - lib.py（公共函数文件）
  - slave/（下位机程序）
    - slave.ino

## 使用方法

### 下位机程序

在Arduino IDE里依次打开文件/首选项/其他开发板管理器地址，将https://github.com/stm32duino/BoardManagerFiles/raw/main/package_stmicroelectronics_index.json粘贴到里面，搭建STM32开发环境，然后在开发板管理器里选择STM32F1 Boards，安装好后在上方选择STM32F103C开头的开发板，准备一块STM32C8T6，将本程序烧录到开发板内

烧录完成后，将MAX7219模块的输入端引脚依次连接到开发板的PA4，PA5，PA7，顺序如下
```
VCC ---- 3.3
GND ---- GND
DIN ---- PA6
CS  ---- PA4
CLK ---- PA5
```

然后通过USB连接STM32即可

### 上位机程序

准备Python环境，依次安装代码里所需的包，然后修改config.py内的各种参数，双击badapple.py，即可欣赏badapple了
