import time
from PIL import ImageEnhance, Image, ImageOps
import pytesseract
import mss
import random
from pynput.keyboard import Listener as KeyboardListener, Key
import threading
import serial
import pyautogui
import serial.tools.list_ports
import tkinter as tk
from tkinter import ttk

# 设置Tesseract路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

arduino = None  # 初始化串口为 None

# UI 相关
root = tk.Tk()
root.title("Magic Box")
root.geometry("400x200")
root.attributes('-toolwindow', True)  # 禁用窗口最大化按钮

# 顶部状态标签
status_label = tk.Label(root, text="PAUSE", font=("Arial", 20), fg="black")
status_label.pack(pady=30)

# 置顶功能
def toggle_topmost():
    if root.attributes('-topmost'):
        root.attributes('-topmost', False)
        pin_button.config(text="Pin")
    else:
        root.attributes('-topmost', True)
        pin_button.config(text="Unpin")

pin_button = tk.Button(root, text="Pin", command=toggle_topmost)
pin_button.pack()

# 状态更新
def update_ui_status():
    if running:
        status_label.config(text="RUNNING", fg="black")
    else:
        status_label.config(text="PAUSE", fg="black")

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description:
            return port.device
        elif port.vid and port.pid:
            if (port.vid, port.pid) == (0x2341, 0x0043):  # Arduino Uno 的 VID 和 PID
                return port.device
            # 可在此添加其他 Arduino 型号的 VID 和 PID
    return None

def open_serial():
    global arduino
    if arduino is None or not arduino.is_open:
        arduino = serial.Serial(port=find_arduino_port(), baudrate=9600, timeout=.1)
        print("串口已打开")

def close_serial():
    global arduino
    if arduino is not None and arduino.is_open:
        arduino.close()
        print("串口已关闭")

def send_command(command):
    if arduino is not None and arduino.is_open:
        arduino.write(bytes(command, 'utf-8'))
        time.sleep(0.05)

def preprocess_image(image):
    # 转换为灰度图像
    gray_image = image.convert('L')

    # 反转颜色
    inverted_image = ImageOps.invert(gray_image)

    # 提高对比度
    enhancer = ImageEnhance.Contrast(inverted_image)
    enhanced_image = enhancer.enhance(2)

    # 应用二值化
    binary_image = enhanced_image.point(lambda x: 0 if x < 128 else 255, '1')

    return binary_image

def recognize_text(image, psm_mode):
    # 进行OCR
    config = f'--psm {psm_mode}'
    text = pytesseract.image_to_string(image, config=config)
    return text

# 全局变量，用于控制程序运行状态
running = False
current_thread = None

def monitor_region(bbox):
    with mss.mss() as sct:
        pre_text = '123'
        while running:
            # 截取屏幕指定区域
            screenshot = sct.grab(bbox)
            img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)

            # 预处理图像
            processed_image = preprocess_image(img)

            # 识别字符（指定PSM）
            text = recognize_text(processed_image, 10).strip()
            if text != pre_text and text != 'N3' and text != '2' and text != '8':
                time.sleep(0.1 * random.random() + 0.2)
            pre_text = text

            print(text)

            key_list = ['1', '2', '3', '4', '5', '6', '8', '9', '0', 'F1', 'F2', 'F3', 'F4', 'F5',
                        'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', '=', 'N1', 'N2',
                        'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N0', 'Q', 'W', 'E', 'R', 'T', 'Y',
                        'U', 'I', 'O', 'P', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M']
            if text in key_list:
                send_command('<' + text + '>')
            if text == 'FO' or text == 'FS':
                send_command('<F9>')
            if text == '6)':
                send_command('<6>')
            if text == '—':
                send_command('<=>')
            if text == 'FE.':
                send_command('<F6>')
            if text == '0.':
                send_command('<Q>')

            # 随机延时
            time.sleep(0.3 * random.random())

def run_program():
    global running, current_thread
    screen_width, screen_height = pyautogui.size()
    bbox = {'left': int(2421 * screen_width / 3840), 'top': int(1750 * screen_height / 2160), 'width': int(147 * screen_width / 3840), 'height': int(80 * screen_height / 2160)}  # 根据你的需要调整区域
    while True:
        if running:
            if current_thread is None or not current_thread.is_alive():
                open_serial()  # 启动监控时打开串口
                current_thread = threading.Thread(target=monitor_region, args=(bbox,))
                current_thread.start()
                print("监控程序启动...")
        else:
            if current_thread is not None and current_thread.is_alive():
                running = False
                current_thread.join()
                close_serial()  # 暂停监控时关闭串口
                print("监控程序已暂停...")
                current_thread = None
        # 更新UI状态
        update_ui_status()
        # 适当延时，避免频繁检测
        time.sleep(0.05)

def toggle_running():
    global running
    running = not running

def on_press(key):
    if key == Key.ctrl_l or key == Key.ctrl_r:  # 监听左Ctrl或右Ctrl按下
        toggle_running()

# 监听键盘事件
keyboard_listener = KeyboardListener(on_press=on_press)
keyboard_listener.start()

# 启动程序运行的线程
thread = threading.Thread(target=run_program)
thread.start()

# 启动UI主循环
root.mainloop()

# 清理工作
running = False
if current_thread is not None and current_thread.is_alive():
    current_thread.join()
close_serial()  # 关闭串口
keyboard_listener.stop()
