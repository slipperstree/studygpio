#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO
import time

# 串行数据输入
DIN = 13

# 时钟脉冲信号——上升沿有效
LOAD = 26

# 打入信号————上升沿有效
CLK = 19

RPi.GPIO.setmode(RPi.GPIO.BCM)

RPi.GPIO.setup(DIN, RPi.GPIO.OUT)
RPi.GPIO.setup(LOAD, RPi.GPIO.OUT)
RPi.GPIO.setup(CLK, RPi.GPIO.OUT)

# 译码模式设置
def setDecodeMode(mode = 4):
	RPi.GPIO.output(LOAD, False)

	# 指令寄存器地址设置：0xX9
	# D15-D12:任意
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	# D11,10,9,8: 1,0,0,1
	setBitData(True)
	setBitData(False)
	setBitData(False)
	setBitData(True)
	
	if (mode == 1) :
		# TODO
		print "TODO"
		pass
	elif (mode == 2) :
		# TODO
		print "TODO"
		pass
	elif (mode == 3) :
		# TODO
		print "TODO"
		pass
	elif (mode == 4) :
		# 数码管7－0全部采用译码模式
		# D7－D0： 1，1，1，1，1，1，1，1
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(True)

	RPi.GPIO.output(LOAD, True)

# 亮度设置
def setIntensity(mode = 15):
	RPi.GPIO.output(LOAD, False)

	# 指令寄存器地址设置：0xXA
	# D15-D12:任意
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	# D11,10,9,8: 1,0,1,0
	setBitData(True)
	setBitData(False)
	setBitData(True)
	setBitData(False)
	
	# 亮度从0到15共16个等级，指令的D3－D0就是数字0－15的二进制编码
	# D7-D4:任意
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	
	if (mode == 15) :
		setBitData(True)
		setBitData(True)
		setBitData(True)
		setBitData(True)
	else :
		# TODO
		print "TODO"
		pass

	RPi.GPIO.output(LOAD, True)

# 扫描显示位数设置
def setScanLimit(mode = 4):
	RPi.GPIO.output(LOAD, False)

	# 指令寄存器地址设置：0xXB
	# D15-D12:任意
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	# D11,10,9,8: 1,0,1,1
	setBitData(True)
	setBitData(False)
	setBitData(True)
	setBitData(True)
	
	# 扫描位数可设置0－7共8种选择，指令的D2－D0就是数字0－7的二进制编码
	# D7-D3:任意
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	
	if (mode == 4) :
		setBitData(False)
		setBitData(True)
		setBitData(True)
	else :
		# TODO
		print "TODO"
		pass

	RPi.GPIO.output(LOAD, True)

# 关断模式设置
def setShutdownMode(mode = 1):
	RPi.GPIO.output(LOAD, False)

	# 指令寄存器地址设置：0xXC
	# D15-D12:任意
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	# D11,10,9,8: 1,1,0,0
	setBitData(True)
	setBitData(True)
	setBitData(False)
	setBitData(False)
	
	# 关断模式可设置0－1共2种选择，设置D0即可
	# D7-D1:任意
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	
	if (mode == 1) :
		# 正常运行模式
		setBitData(True)
	else :
		# 关断模式
		setBitData(False)

	RPi.GPIO.output(LOAD, True)

# 测试模式设置
def setDisplayTestMode(mode = 0):
	RPi.GPIO.output(LOAD, False)

	# 指令寄存器地址设置：0xXF
	# D15-D12:任意
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	# D11,10,9,8: 1,1,1,1
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	
	# 测试模式可设置0－1共2种选择，设置D0即可
	# D7-D1:任意
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	setBitData(True)
	
	if (mode == 0) :
		# 正常运行模式
		setBitData(False)
	else :
		# 测试模式
		setBitData(True)

	RPi.GPIO.output(LOAD, True)

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

	RPi.GPIO.output(LOAD, True)
	RPi.GPIO.output(LOAD, False)

def setBitData(data):
	RPi.GPIO.output(CLK, False)
	RPi.GPIO.output(DIN, data)
	RPi.GPIO.output(CLK, True)

try:
	t=0.005
	setShutdownMode()
	setDecodeMode()
	setIntensity()
	setScanLimit()
	
	setDisplayTestMode(1)
	
	#while True:
	#	time.sleep(1)
	#while True:
	#	time.sleep(t)
	#	showDigit(1, int(time.strftime("%H",time.localtime(time.time()))) / 10, False)
	#	time.sleep(t)
	#	showDigit(2, int(time.strftime("%H",time.localtime(time.time()))) % 10, True)
	#	time.sleep(t)
	#	showDigit(3, int(time.strftime("%M",time.localtime(time.time()))) / 10, False)
	#	time.sleep(t)
	#	showDigit(4, int(time.strftime("%M",time.localtime(time.time()))) % 10, False)
			
except KeyboardInterrupt:
	pass

# 最后清理GPIO口（不做也可以，建议每次程序结束时清理一下，好习惯）
RPi.GPIO.cleanup()
