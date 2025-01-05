#include <Keyboard.h>

String commandBuffer = "";  // 用来存储命令的缓冲区
bool isCommandActive = false;  // 用来标记是否正在接收一个完整的命令

// 手动定义 Numpad 键的 HID 键码
#define HID_KEYPAD_1 0xE1
#define HID_KEYPAD_2 0xE2
#define HID_KEYPAD_3 0xE3
#define HID_KEYPAD_4 0xE4
#define HID_KEYPAD_5 0xE5
#define HID_KEYPAD_6 0xE6
#define HID_KEYPAD_7 0xE7
#define HID_KEYPAD_8 0xE8
#define HID_KEYPAD_9 0xE9

void setup() {
  Serial.begin(9600);  // 初始化串口
  Keyboard.begin();    // 初始化键盘
  randomSeed(analogRead(0));  // 初始化随机数生成器
}

void loop() {
  // 如果串口有可用的数据
  if (Serial.available() > 0) {
    char incomingChar = Serial.read();  // 读取串口中的单个字符

    // 检查是否是起始符或终止符
    if (incomingChar == '<') {
      // 起始符，开始接收命令
      commandBuffer = "";
      isCommandActive = true;
      return;
    } else if (incomingChar == '>') {
      // 终止符，结束接收命令并执行
      isCommandActive = false;
    }

    // 如果正在接收命令，则将字符添加到缓冲区
    if (isCommandActive && incomingChar != '<' && incomingChar != '>') {
      commandBuffer += incomingChar;
      return;
    }

    // 打印接收到的命令
    Serial.print("Received command: ");
    Serial.println(commandBuffer);

    // 生成 10 到 50 之间的随机延迟
    int randomDelay = random(20, 111);

    // 处理命令
    if (commandBuffer.equals("N1")) {
      Keyboard.press(HID_KEYPAD_1);
      delay(randomDelay);
      Keyboard.release(HID_KEYPAD_1);
    } else if (commandBuffer.equals("N2")) {
      Keyboard.press(HID_KEYPAD_2);
      delay(randomDelay);
      Keyboard.release(HID_KEYPAD_2);
    } else if (commandBuffer.equals("N3")) {
      Keyboard.press(HID_KEYPAD_3);
      delay(randomDelay);
      Keyboard.release(HID_KEYPAD_3);
    } else if (commandBuffer.equals("N4")) {
      Keyboard.press(HID_KEYPAD_4);
      delay(randomDelay);
      Keyboard.release(HID_KEYPAD_4);
    } else if (commandBuffer.equals("N5")) {
      Keyboard.press(HID_KEYPAD_5);
      delay(randomDelay);
      Keyboard.release(HID_KEYPAD_5);
    } else if (commandBuffer.equals("N6")) {
      Keyboard.press(HID_KEYPAD_6);
      delay(randomDelay);
      Keyboard.release(HID_KEYPAD_6);
    } else if (commandBuffer.equals("N7")) {
      Keyboard.press(HID_KEYPAD_7);
      delay(randomDelay);
      Keyboard.release(HID_KEYPAD_7);
    } else if (commandBuffer.equals("N8")) {
      Keyboard.press(HID_KEYPAD_8);
      delay(randomDelay);
      Keyboard.release(HID_KEYPAD_8);
    } else if (commandBuffer.equals("N9")) {
      Keyboard.press(HID_KEYPAD_9);
      delay(randomDelay);
      Keyboard.release(HID_KEYPAD_9);
    } else if (commandBuffer.equals("F1")) {
      Keyboard.press(KEY_F1);
      delay(randomDelay);
      Keyboard.release(KEY_F1);
    } else if (commandBuffer.equals("F2")) {
      Keyboard.press(KEY_F2);
      delay(randomDelay);
      Keyboard.release(KEY_F2);
    } else if (commandBuffer.equals("F3")) {
      Keyboard.press(KEY_F3);
      delay(randomDelay);
      Keyboard.release(KEY_F3);
    } else if (commandBuffer.equals("F4")) {
      Keyboard.press(KEY_F4);
      delay(randomDelay);
      Keyboard.release(KEY_F4);
    } else if (commandBuffer.equals("F5")) {
      Keyboard.press(KEY_F5);
      delay(randomDelay);
      Keyboard.release(KEY_F5);
    } else if (commandBuffer.equals("F6")) {
      Keyboard.press(KEY_F6);
      delay(randomDelay);
      Keyboard.release(KEY_F6);
    } else if (commandBuffer.equals("F7")) {
      Keyboard.press(KEY_F7);
      delay(randomDelay);
      Keyboard.release(KEY_F7);
    } else if (commandBuffer.equals("F8")) {
      Keyboard.press(KEY_F8);
      delay(randomDelay);
      Keyboard.release(KEY_F8);
    } else if (commandBuffer.equals("F9")) {
      Keyboard.press(KEY_F9);
      delay(randomDelay);
      Keyboard.release(KEY_F9);
    } else if (commandBuffer.equals("F10")) {
      Keyboard.press(KEY_F10);
      delay(randomDelay);
      Keyboard.release(KEY_F10);
    } else if (commandBuffer.equals("F11")) {
      Keyboard.press(KEY_F11);
      delay(randomDelay);
      Keyboard.release(KEY_F11);
    } else if (commandBuffer.equals("F12")) {
      Keyboard.press(KEY_F12);
      delay(randomDelay);
      Keyboard.release(KEY_F12);
    } else if (commandBuffer.length() == 1) {
      // 处理其他单字符命令
      char command = commandBuffer.charAt(0);
      Keyboard.press(command);
      delay(randomDelay);
      Keyboard.release(command);
    }

    // 清空缓冲区以准备处理下一个命令
    commandBuffer = "";
  }
}
