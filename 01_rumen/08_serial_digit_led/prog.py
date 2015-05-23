#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO
import time

# 串行数据输入
DIO = 13

# 时钟脉冲信号——上升沿有效
RCLK = 19

# 打入信号————上升沿有效
SCLK = 26

RPi.GPIO.setmode(RPi.GPIO.BCM)

RPi.GPIO.setup(DIO, RPi.GPIO.OUT)
RPi.GPIO.setup(RCLK, RPi.GPIO.OUT)
RPi.GPIO.setup(SCLK, RPi.GPIO.OUT)

RPi.GPIO.output(RCLK, False)
RPi.GPIO.output(SCLK, False)

# 指定no(1-4)号数码管显示数字num(0-9)，第三个参数是显示不显示小数点（true/false）
def showDigit(no, num, showDotPoint):
	
	if (num == 0) :
		setBitData(not showDotPoint)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
	elif (num == 1) :
		setBitData(not showDotPoint)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(True)
	elif (num == 2) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
		setBitData(False)
	elif (num == 3) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(True)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
	elif (num == 4) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(True)
	elif (num == 5) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
	elif (num == 6) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
	elif (num == 7) :
		setBitData(not showDotPoint)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(False)
	elif (num == 8) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
	elif (num == 9) :
		setBitData(not showDotPoint)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
	
	if (no == 1) :
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
		setBitData(False)
		setBitData(False)
	elif (no == 2) :
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
		setBitData(False)
	elif (no == 3) :
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(True)
		setBitData(False)
	elif (no == 4) :
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(False)
		setBitData(True)

	RPi.GPIO.output(RCLK, True)
	RPi.GPIO.output(RCLK, False)

def setBitData(data):
	RPi.GPIO.output(DIO, data)
	RPi.GPIO.output(SCLK, False)
	RPi.GPIO.output(SCLK, True)

try:
	t=0.005
	while True:
		time.sleep(t)
		showDigit(1, int(time.strftime("%H",time.localtime(time.time()))) / 10, False)
		time.sleep(t)
		showDigit(2, int(time.strftime("%H",time.localtime(time.time()))) % 10, True)
		time.sleep(t)
		showDigit(3, int(time.strftime("%M",time.localtime(time.time()))) / 10, False)
		time.sleep(t)
		showDigit(4, int(time.strftime("%M",time.localtime(time.time()))) % 10, False)
			
except KeyboardInterrupt:
	pass

# 最后清理GPIO口（不做也可以，建议每次程序结束时清理一下，好习惯）
RPi.GPIO.cleanup()
