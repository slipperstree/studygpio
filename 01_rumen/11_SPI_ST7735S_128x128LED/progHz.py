#!/usr/bin/env python
 
import RPi.GPIO as GPIO
import time
import random

cs=23		# Ƭѡ
rs=17		# ���� / ���� �л�
sda=13		# ����
scl=19		# ʱ��
reset=27	# ��λ

# ����byte
def setByteData(data):
	# print ""
	# print "S-----------setByte---------------:", hex(data)
	for bit in range(0,8):
		# ��������ִӸ�λ����λ�����ж��Ƿ�Ϊ1����Ϊ1�����øߵ�ƽ���������õ͵�ƽ
		# �жϵķ�������������λ����Ҫ�жϵ�λ�ƶ������λȻ���0x80��1000 0000�����룬
		# ��������Ȼ��0x80��1000 0000���ͱ�ʾ���λ��1���������λ����0
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

def write_command(cmd):
	GPIO.output(cs, False)
	GPIO.output(rs, False)
	setByteData(cmd)
	GPIO.output(cs, True)

def write_data(byteData):
	GPIO.output(cs, False)
	GPIO.output(rs, True)
	setByteData(byteData)
	GPIO.output(cs, True)

def write_data_8bitH_8bitL(bit8DataH, bit8DataL):
	write_data(bit8DataH)
	write_data(bit8DataL)

def write_data_16bitHL(bit16DataHL):
	write_data(bit16DataHL>>8)
	write_data(bit16DataHL&&0xff)

def lcd_reset():
    GPIO.output(reset, False)
    time.sleep(0.1)
    GPIO.output(reset, True)
    time.sleep(0.1)

def lcd_init():
	lcd_reset()

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

def show_single_color(DH,DL):
	for i in xrange(0,128):
		for j in xrange(0,128):
			write_data_8bitH_8bitL(DH,DL)

def setDotColor(x, y, color):
	drawRect(x,y, x,y, color)

# startX, startY, endX, endY:0-127
def drawRect(startX, startY, endX, endY, color_16bit):
	if (startX > 127):
		startX = 127
	if (startY > 127):
		startY = 127
	if (endX > 127):
		endX = 127
	if (endY > 127):
		endY = 127
	if (endX < startX):
		endX = startX
	if (endY < startY):
		endY = startY
	
	write_command(0x2a)
	write_data_16bitHL(startX)
	write_data_16bitHL(endX)

	write_command(0x2b)
	write_data_16bitHL(startY)
	write_data_16bitHL(endY)

	write_command(0x2c)
	for i in xrange(startX, endX+1):
		for j in xrange(startY, endY+1):
			write_data_16bitHL(color_16bit)

def getHZ_32Bytes(hz):
	retBytes32 = []
	
	gb=hz.decode('utf-8').encode('gb2312')

	print '����:' + hz,
	
	# ����
	codeQu = struct.unpack('B', gb[0])[0]
	print '����:' + str(codeQu) + ', ',

	# λ��
	codeWei = struct.unpack('B', gb[1])[0]
	print 'λ��:' + str(codeWei) + ', ',

	# �ֽ�ƫ��ֵ����λƫ��ֵ��
	offset = ((codeQu - 0xa1) * 94 + codeWei - 0xa1) * 32
	print 'ƫ��ֵ:' + str(offset)
	
	for i in range(offset, offset+32):
		retBytes32.append(zk[i])
	return retBytes32

class Point:
    def __init__(self):
        self.x = -1
        self.y = -1

def drawHz16x16(pStart, byteArray32Hz, bit16Backcolor, bit16Fontcolor):
	pNext = Point()
	if (pStart.x<0 or pStart.y<0 or pStart.x>127-16 or pStart.y>127-16):
		return pNext

	write_command(0x2a)
	write_data_16bitHL(pStart.x)
	write_data_16bitHL(pStart.x+16)

	write_command(0x2b)
	write_data_16bitHL(pStart.y)
	write_data_16bitHL(pStart.y+16)

	write_command(0x2c)
	for i in range(0, 32):
		byteHz=byteArray32Hz[i]
		for j in range(0, 8):
			if ((byteHz << j) & 0x80):
				write_data_16bitHL(bit16Fontcolor)
			else:
				write_data_16bitHL(bit16Backcolor)

	if (pStart.y + 16 > 127 - 16):
		return pNext

	if (pStart.x + 16 > 127 - 16):
		pNext.x = 0
		pNext.y = pStart.y + 16

	return pNext

try:
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(cs, GPIO.OUT)
	GPIO.setup(rs, GPIO.OUT)
	GPIO.setup(sda, GPIO.OUT)
	GPIO.setup(scl, GPIO.OUT)
	GPIO.setup(reset, GPIO.OUT)
	
	# read zk to memory
	zk=np.fromfile('HZK16.dat', dtype='b')
	
	s = "��"

	lcd_init()
	write_command(0x2c)

	p = Point()
	p.x = 0
	p.y = 0
	drawHz16x16(p, getHZ_32Bytes(s), 0xffff, 0x0000)

except KeyboardInterrupt:
	pass

# ����GPIO��
#GPIO.cleanup()
