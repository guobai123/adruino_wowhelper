本项目用的是Tesseract ocr，在识别某些字符时经常出错，但是我懒得弄了，在代码里面改改错误的映射就可以了，将就一下吧


0.运行tesseract-ocr-w64-setup-5.4.0.20240606.exe，安装ocr到默认路径 （C:\Program Files\Tesseract-OCR\tesseract.exe）


1.买一个adruino leonard的板子 淘宝20多块钱


2.下载Adruino IDE （https://www.arduino.cc/en/software）


3.连接好板子后用Adruino IDE 打开HID_input.ino.ino, 把代码写进板子里面


4.运行wow, 把hekili_style.txt的字符串导入hekili style, background_wa.txt的字符串导入wa


5.运行main.py,第一次运行时要选择ocr识别区域，识别错了的话删掉screen_config.json,重新运行main.py即可


6.按一下ctrl键或者鼠标侧键（mouse4）运行程序,再按一下暂停
