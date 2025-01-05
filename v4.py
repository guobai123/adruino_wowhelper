import time
from PIL import ImageEnhance, Image, ImageOps
import pytesseract
import mss
import random
from pynput.keyboard import Listener as KeyboardListener, Key
import threading
import serial
import serial.tools.list_ports
import tkinter as tk
import re
import pyautogui
from inputs import get_gamepad

# 设置 Tesseract 路径
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# 全局变量
arduino = None  # 初始化串口为 None
running = False  # 程序运行状态
rt_pressed = False  # 手柄 RT 键状态
current_thread = None  # 用于监控线程

# UI 初始化
root = tk.Tk()
root.title("Magic Box")
root.geometry("400x200")
root.attributes('-toolwindow', True)

# 状态标签
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

# 更新状态到 UI
def update_ui_status():
    if running:
        status_label.config(text="RUNNING", fg="black")
    else:
        status_label.config(text="PAUSE", fg="black")

# 切换运行状态
def toggle_running():
    global running
    running = not running
    update_ui_status()
    print("Running:", running)

# 找到 Arduino 串口
def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'Arduino' in port.description:
            return port.device
        elif port.vid and port.pid:
            if (port.vid, port.pid) == (0x2341, 0x0043):  # Arduino Uno 的 VID 和 PID
                return port.device
    return None

# 打开串口
def open_serial():
    global arduino
    if arduino is None or not arduino.is_open:
        arduino = serial.Serial(port=find_arduino_port(), baudrate=9600, timeout=.1)
        print("串口已打开")

# 关闭串口
def close_serial():
    global arduino
    if arduino is not None and arduino.is_open:
        arduino.close()
        print("串口已关闭")

# 发送命令到 Arduino
def send_command(command):
    if arduino is not None and arduino.is_open:
        arduino.write(bytes(command, 'utf-8'))
        time.sleep(0.05)

# 图像预处理
def preprocess_image(image):
    gray_image = image.convert('L')
    inverted_image = ImageOps.invert(gray_image)
    enhancer = ImageEnhance.Contrast(inverted_image)
    enhanced_image = enhancer.enhance(2)
    binary_image = enhanced_image.point(lambda x: 0 if x < 128 else 255, '1')
    return binary_image

# OCR 识别文字
def recognize_text(image, psm_mode):
    config = f'--psm {psm_mode} --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHNPRTUVWXYZ'
    text = pytesseract.image_to_string(image, config=config)
    return text

# AHK 颜色判断功能
def execute_ahk_code(ahk_code):
    pattern = r'GetColor\((\d+),(\d+)\)="([0-9A-F]{4})"'
    matches = re.findall(pattern, ahk_code)
    with mss.mss() as sct:
        for match in matches:
            x, y, color = int(match[0]), int(match[1]), match[2]
            bbox = {'left': x - 5, 'top': y - 5, 'width': 10, 'height': 10}
            screenshot = sct.grab(bbox)
            pixel = screenshot.pixel(5, 5)
            if f'{pixel[1]:02X}{pixel[2]:02X}' != color:
                return False
    return True

# 监控屏幕区域
def monitor_region(bbox):
    with mss.mss() as sct:
        pre_text = '123'
        while running:


            # 截取屏幕指定区域
            screenshot = sct.grab(bbox)
            img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
            # img.show()
            # 预处理图像
            processed_image = preprocess_image(img)
            # 识别字符（指定PSM）
            text = recognize_text(processed_image, 10).strip()

            # 清毒N5
            if execute_ahk_code('if (GetColor(2249,85)="CB9D") && (GetColor(2248,85)="ECDE") && (GetColor(2250,85)="B877") && (GetColor(2249,84)="DDBF") && (GetColor(2249,86)="D0A9")'):
                send_command('<N5>')
                print('N5')
                time.sleep(0.1 * random.random() + 0.1)

            # 打断F 骑士
            elif execute_ahk_code(
                    'if (GetColor(76,180)="B229") && (GetColor(75,180)="B820") && (GetColor(77,180)="B22A") && (GetColor(76,179)="B01F") && (GetColor(76,181)="B229")'):
                send_command('<F>')
                print('F')
            # 法师打断
            elif execute_ahk_code(
                    'if (GetColor(69,188)="C504") && (GetColor(68,188)="D32B") && (GetColor(70,188)="C300") && (GetColor(69,187)="C507") && (GetColor(69,189)="C503")'):
                send_command('<F>')
                print('F')

            # 保护
            elif execute_ahk_code('if (GetColor(1967,1074)="183B") && (GetColor(1966,1074)="173E") && (GetColor(1968,1074)="1D3D") && (GetColor(1967,1073)="183B") && (GetColor(1967,1075)="183B")'):
                send_command('<F12>')
                print('F12')
                time.sleep(0.1 * random.random() + 0.1)

            # 寒冰护盾 Z
            elif execute_ahk_code('if (GetColor(52,1482)="3734") && (GetColor(51,1482)="B8AE") && (GetColor(53,1482)="0808") && (GetColor(52,1481)="3735") && (GetColor(52,1483)="3632")'):
                send_command('<Z>')
                print('Z')
                time.sleep(0.1 * random.random() + 0.2)
            else:

                if text != pre_text and text != 'N3' and text != '2' and text != '8' and text != 'F10':
                    time.sleep(0.1 * random.random())
                pre_text = text
                if text != '':
                    print(text)

                key_list = ['1', '2', '3', '4', '5', '6', '8', '9', '0', 'F1', 'F2', 'F3', 'F4', 'F5',
                            'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', '=', 'N1', 'N2',
                            'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N0', 'Q', 'W', 'E', 'R', 'T', 'Y',
                            'U', 'I', 'O', 'P', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'Z', 'X', 'C', 'V',
                            'B', 'N', 'M', '=']

                if text in key_list:
                    send_command('<' + text + '>')
                if text == 'FH':
                    send_command('<F5>')
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
                if text == 'F110':
                    send_command('<F10>')

                # 随机延时
                time.sleep(0.1 * random.random() + 0.1)

# 主运行函数
def run_program():
    global running, current_thread
    screen_width, screen_height = pyautogui.size()
    bbox = {'left': int(2421 * screen_width / 3840), 'top': int(1750 * screen_height / 2160),
            'width': int(147 * screen_width / 3840), 'height': int(80 * screen_height / 2160)}
    while True:
        if running:
            if current_thread is None or not current_thread.is_alive():
                open_serial()
                current_thread = threading.Thread(target=monitor_region, args=(bbox,))
                current_thread.start()
                print("监控程序启动...")
        else:
            if current_thread is not None and current_thread.is_alive():
                running = False
                current_thread.join()
                close_serial()
                print("监控程序已暂停...")
                current_thread = None
        update_ui_status()
        time.sleep(0.05)

# 键盘监听
def on_press(key):
    if key == Key.ctrl_l or key == Key.ctrl_r:
        toggle_running()

# 手柄监听
def listen_gamepad():
    global rt_pressed
    while True:
        events = get_gamepad()
        for event in events:
            if event.code == 'ABS_RZ':  # RT 键
                if event.state > 0 and not rt_pressed:
                    toggle_running()
                    rt_pressed = True
                elif event.state == 0:
                    rt_pressed = False
        time.sleep(0.01)

# 启动线程
keyboard_listener = KeyboardListener(on_press=on_press)
keyboard_listener.start()

gamepad_thread = threading.Thread(target=listen_gamepad, daemon=True)
gamepad_thread.start()

program_thread = threading.Thread(target=run_program)
program_thread.start()

root.mainloop()

keyboard_listener.stop()
