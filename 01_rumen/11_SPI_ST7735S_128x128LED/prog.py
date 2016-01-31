#!/usr/bin/env python
 
import RPi.GPIO as GPIO
import time

cs=23		# 片选
rs=17		# 数据 / 命令 切换
sda=13		# 数据
scl=19		# 时钟
reset=27	# 复位

# 传输byte
def setByteData(data):
	# print ""
	# print "S-----------setByte---------------:", hex(data)
	for bit in range(0,8):
		# 传入的数字从高位到低位依次判断是否为1，若为1则设置高电平，否则设置低电平
		# 判断的方法是先向左移位，把要判断的位移动到最高位然后跟0x80（1000 0000）相与，
		# 如果结果仍然是0x80（1000 0000）就表示最高位是1，否则最高位就是0
		if ((data<<bit) & 0x80 == 0x80):
			setBitData(True)
			# print "1",
		else:
			setBitData(False)
			# print "0",
	# print ""
	# print "E-----------setByte---------------"

def setBitData(data):
	GPIO.output(scl, False)
	GPIO.output(sda, data)
	GPIO.output(scl, True)

def LCD_CtrlWrite_IC(ctlData):
	GPIO.output(cs, False)
	GPIO.output(rs, False)
	setByteData(ctlData)
	GPIO.output(cs, True)

def LCD_DataWrite_IC(data):
	GPIO.output(cs, False)
	GPIO.output(rs, True)
	setByteData(data)
	GPIO.output(cs, True)

def LCD_DataWrite(LCD_DataH, LCD_DataL):
	LCD_DataWrite_IC(LCD_DataH)
	LCD_DataWrite_IC(LCD_DataL)

def write_command(cmd):
	GPIO.output(cs, False)
	GPIO.output(rs, False)
	setByteData(cmd)
	GPIO.output(cs, True)

def write_data(data):
	GPIO.output(cs, False)
	GPIO.output(rs, True)
	setByteData(data)
	GPIO.output(cs, True)

def Reset():
    GPIO.output(reset, False)
    time.sleep(0.1)
    GPIO.output(reset, True)
    time.sleep(0.1)

def lcd_initial():
	GPIO.output(reset, False)
	time.sleep(0.1)
	GPIO.output(reset, True)
	time.sleep(0.1)

	#------------------------------------------------------------------#   
	#-------------------Software Reset-------------------------------# 
	write_command(0x11) # Exit Sleep
	time.sleep(0.02)
	write_command(0x26) # Set Default Gamma
	write_data(0x04)
	write_command(0xB1)# Set Frame Rate
	write_data(0x0e)
	write_data(0x10)
	write_command(0xC0) # Set VRH1[4:0] & VC[2:0] for VCI1 & GVDD
	write_data(0x08)
	write_data(0x00)
	write_command(0xC1) # Set BT[2:0] for AVDD & VCL & VGH & VGL
	write_data(0x05)
	write_command(0xC5) # Set VMH[6:0] & VML[6:0] for VOMH & VCOML
	write_data(0x38)
	write_data(0x40)

	write_command(0x3a) # Set Color Format
	write_data(0x05)
	write_command(0x36) # RGB
	write_data(0xc8)

	write_command(0x2A) # Set Column Address
	write_data(0x00)
	write_data(0x00)
	write_data(0x00)
	write_data(0x7F)
	write_command(0x2B) # Set Page Address
	write_data(0x00)
	write_data(0x00)
	write_data(0x00)
	write_data(0x7F)

	write_command(0xB4) 
	write_data(0x00)

	write_command(0xf2) # Enable Gamma bit
	write_data(0x01)
	write_command(0xE0) 
	write_data(0x3f)# p1
	write_data(0x22)# p2
	write_data(0x20)# p3
	write_data(0x30)# p4
	write_data(0x29)# p5
	write_data(0x0c)# p6
	write_data(0x4e)# p7
	write_data(0xb7)# p8
	write_data(0x3c)# p9
	write_data(0x19)# p10
	write_data(0x22)# p11
	write_data(0x1e)# p12
	write_data(0x02)# p13
	write_data(0x01)# p14
	write_data(0x00)# p15
	write_command(0xE1) 
	write_data(0x00)# p1
	write_data(0x1b)# p2
	write_data(0x1f)# p3
	write_data(0x0f)# p4
	write_data(0x16)# p5
	write_data(0x13)# p6
	write_data(0x31)# p7
	write_data(0x84)# p8
	write_data(0x43)# p9
	write_data(0x06)# p10
	write_data(0x1d)# p11
	write_data(0x21)# p12
	write_data(0x3d)# p13
	write_data(0x3e)# p14
	write_data(0x3f)# p15

	write_command(0x29) #  Display On
	write_command(0x2C)

def dsp_single_colour(DH,DL):
	for i in xrange(0,128):
		for j in xrange(0,128):
			LCD_DataWrite(DH,DL)

try:
	GPIO.setmode(GPIO.BCM)
	
	lcd_initial()
    write_command(0x2C)
    dsp_single_colour(0x00,0x1f) # 蓝色背景

except KeyboardInterrupt:
	pass

# 清理GPIO口
GPIO.cleanup()