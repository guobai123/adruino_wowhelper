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
import re

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
        else:
            print('未找到设备')
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
    config = f'--psm {psm_mode} --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPRSTUVWXYZ'
    text = pytesseract.image_to_string(image, config=config)
    return text

# 获取某个像素的颜色
# 参数screenshot是整个屏幕截图，x, y是屏幕坐标，返回颜色值的字符串形式（后四位）
def get_color(screenshot, x, y):
    pixel = screenshot.getpixel((x, y))
    return f'{pixel[1]:02X}{pixel[2]:02X}'


# 将 AHK 代码转化并执行相应的颜色判断功能
# 参数ahk_code是包含颜色判断逻辑的字符串，返回True或False
def execute_ahk_code(ahk_code):
    pattern = r'GetColor\((\d+),(\d+)\)="([0-9A-F]{4})"'
    matches = re.findall(pattern, ahk_code)

    # 进行一次屏幕截图
    screenshot = pyautogui.screenshot()

    for match in matches:
        x, y, color = int(match[0]), int(match[1]), match[2]
        if get_color(screenshot, x, y) != color:
            return False
    return True


# 获取某个某个像素的颜色并判断是否为指定的颜色
# 参数x, y是屏幕坐标，target_color是目标颜色的元组形式（RGB格式，如(255, 255, 255)）
# 返回True或False
def is_color_at_position(x, y, target_color):
    # 获取屏幕截图并获取指定坐标的像素颜色
    screenshot = pyautogui.screenshot()
    pixel = screenshot.getpixel((x, y))

    # 比较当前颜色和目标颜色
    return pixel == target_color


# 全局变量，用于控制程序运行状态
running = False
current_thread = None

def monitor_region(bbox):
    with mss.mss() as sct:
        pre_text = '123'
        while running:

            if not is_color_at_position(2394,1904,(255,26,26)):

                # 截取屏幕指定区域
                screenshot = sct.grab(bbox)
                img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)

                # 预处理图像
                processed_image = preprocess_image(img)
                #processed_image.show()
                # 识别字符（指定PSM）
                text = recognize_text(processed_image, 10).strip()
                text = text.replace('.', '')
                text = text.replace(')', '')
                text = text.replace('(', '')
                start_time = time.perf_counter()
                #清毒N5
                if execute_ahk_code('if (GetColor(2207,114)="FEFD") && (GetColor(2206,114)="FEFD") && (GetColor(2208,114)="E9D9") && (GetColor(2207,113)="FBF7") && (GetColor(2207,115)="FCF6")'):
                    send_command('<N5>')
                    print('N5')
                end_time = time.perf_counter()
                print(f"代码执行时间: {end_time - start_time:.4f} 秒")
                #打断F
                if execute_ahk_code('if (GetColor(76,180)="B229") && (GetColor(75,180)="B820") && (GetColor(77,180)="B22A") && (GetColor(76,179)="B01F") && (GetColor(76,181)="B229")'):
                    send_command('<F>')
                    print('F')

                if text != pre_text and text != 'N3' and text != '2' and text != '8' and text != 'F10':
                    time.sleep(0.1 * random.random())
                pre_text = text
                if text != '':
                    print(text)

                key_list = ['1', '2', '3', '4', '5', '6', '8', '9', '0', 'F1', 'F2', 'F3', 'F4', 'F5',
                            'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', '=', 'N1', 'N2',
                            'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N0', 'Q', 'W', 'E', 'R', 'T', 'Y',
                            'U', 'I', 'O', 'P', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Z', 'X', 'C', 'V', 'B', 'N', 'M','=']

                if text in key_list:
                    send_command('<' + text + '>')
                if text == 'FO' or text == 'FS':
                    send_command('<F9>')
                if text == '6)':
                    send_command('<6>')
                if text == '—':
                    send_command('<=>')
                if text == 'FE.' or text == 'FE':
                    send_command('<F6>')
                if text == '0.':
                    send_command('<Q>')

                # 随机延时
                time.sleep(0.1 * random.random())

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
