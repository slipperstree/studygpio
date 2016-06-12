#!/usr/bin/env python
# encoding: utf-8
 
import RPi.GPIO as GPIO
import time
import numpy as np
import struct
import random
import spidev
import json
import datetime
import urllib2

import cStringIO
import zlib
from PIL import Image

cs=23		# 片选
rs=17		# 数据 / 命令 切换
sda=13		# 数据
scl=19		# 时钟
reset=27	# 复位

def spiSendData(bytes):
	spi.xfer2(bytes)

def write_command(cmd):
	GPIO.output(cs, False)
	GPIO.output(rs, False)
	spiSendData(cmd)
	GPIO.output(cs, True)

def write_data(bytes):
	GPIO.output(cs, False)
	GPIO.output(rs, True)
	spiSendData(bytes)
	GPIO.output(cs, True)

def write_data_8bitH_8bitL(bit8DataH, bit8DataL):
	write_data([bit8DataH])
	write_data([bit8DataL])

def write_data_16bitHL(bit16DataHL):
	write_data([bit16DataHL>>8])
	write_data([bit16DataHL&0xff])

def lcd_reset():
    GPIO.output(reset, False)
    time.sleep(0.1)
    GPIO.output(reset, True)
    time.sleep(0.1)

def lcd_init():
	lcd_reset()
	#------------------------------------------------------------------#   
	#-------------------Software Reset-------------------------------# 
	write_command([0x11]) # Exit Sleep
	time.sleep(0.02)
	write_command([0x26]) # Set Default Gamma

	write_data([0x04])
	write_command([0xB1])# Set Frame Rate
	write_data([0x0e])
	write_data([0x10])
	write_command([0xC0]) # Set VRH1[4:0] & VC[2:0] for VCI1 & GVDD
	write_data([0x08])
	write_data([0x00])
	write_command([0xC1]) # Set BT[2:0] for AVDD & VCL & VGH & VGL
	write_data([0x05])
	write_command([0xC5]) # Set VMH[6:0] & VML[6:0] for VOMH & VCOML
	write_data([0x38])
	write_data([0x40])
	write_command([0x3a]) # Set Color Format
	write_data([0x05])
	write_command([0x36]) # RGB
	write_data([0xc8])

	write_command([0x2A]) # Set Column Address
	write_data([0x00])
	write_data([0x00])
	write_data([0x00])
	write_data([0x7F])
	write_command([0x2B]) # Set Page Address
	write_data([0x00])
	write_data([0x00])
	write_data([0x00])
	write_data([0x7F])

	write_command([0xB4]) 
	write_data([0x00])

	write_command([0xf2]) # Enable Gamma bit
	write_data([0x01])
	write_command([0xE0]) 
	write_data([0x3f])# p1
	write_data([0x22])# p2
	write_data([0x20])# p3
	write_data([0x30])# p4
	write_data([0x29])# p5
	write_data([0x0c])# p6
	write_data([0x4e])# p7
	write_data([0xb7])# p8
	write_data([0x3c])# p9
	write_data([0x19])# p10
	write_data([0x22])# p11
	write_data([0x1e])# p12
	write_data([0x02])# p13
	write_data([0x01])# p14
	write_data([0x00])# p15
	write_command([0xE1]) 
	write_data([0x00])# p1
	write_data([0x1b])# p2
	write_data([0x1f])# p3
	write_data([0x0f])# p4
	write_data([0x16])# p5
	write_data([0x13])# p6
	write_data([0x31])# p7
	write_data([0x84])# p8
	write_data([0x43])# p9
	write_data([0x06])# p10
	write_data([0x1d])# p11
	write_data([0x21])# p12
	write_data([0x3d])# p13
	write_data([0x3e])# p14
	write_data([0x3f])# p15

	write_command([0x29]) #  Display On
	write_command([0x2C])

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
	
	write_command([0x2a])
	write_data_16bitHL(startX)
	write_data_16bitHL(endX)

	write_command([0x2b])
	write_data_16bitHL(startY)
	write_data_16bitHL(endY)

	write_command([0x2c])
	dataArray = []

	maxSendBuff = 2048
	if (endX-startX+1) * (endY-startY+1) < 2048:
		maxSendBuff = (endX-startX+1) * (endY-startY+1);

	color_H = color_16bit>>8
	color_L = color_16bit&0xff
	for n in xrange(0,maxSendBuff):
		dataArray.append(color_H)
		dataArray.append(color_L)

	GPIO.output(cs, False)
	GPIO.output(rs, True)

	for n in xrange(0,(endX-startX) * (endY-startY) / maxSendBuff + 1):
		spiSendData(dataArray)

	GPIO.output(cs, True)

# startX, startY, endX, endY:0-127
def drawRectFrame(startX, startY, endX, endY, width, color_16bit):
	width -= 1
	drawRect(startX, startY, endX, startY+width, color_16bit)
	drawRect(endX-width, startY, endX, endY, color_16bit)
	drawRect(startX, endY-width, endX, endY, color_16bit)
	drawRect(startX, startY, startX+width, endY, color_16bit)

def drawLine(startX, startY, endX, endY, color_16bit):
	for x in range(startX, endX):
            y=int((x-startX)*(endY-startY)/(endX-startX))+startY
            setDotColor(x, y, color_16bit)

def drawText(startX, startY, text, bit16Backcolor, bit16Fontcolor):
	p = Point()
	p.x = startX
	p.y = startY
	
	# 先将汉字从utf-8方式解码成unicode形式
	if isinstance(text, unicode):
		utext = text
	else:
		utext = unicode(text, "utf8")

	# 取得文本的字数
	cnt=len(utext)

	for i in range(0, cnt):
		#逐字调用绘制单个汉字的函数
		#第一次调用时设置一个初始位置
		#每次绘制完一个汉字，返回值里存放的是下一个汉字的绘制开始位置
		#如此循环往复，直到所有汉字全部显示完毕或者显示到边界无法继续显示为止

		#由于全角汉字和半角ASCII字符的点阵字库是分开的，所以要先判断当前是全角汉字还是半角字符
		#判断方法是将当前的unicode编码的字符或汉字转换成gb2312码，再判断长度，全角汉字为2，半角字符为1
		gb2312Char = utext[i].encode("gb2312")
		if (len(gb2312Char) == 2):
			# 16 X 16 汉字点阵
			p = drawHz(p, getHZ_32Bytes(gb2312Char), 16, 16, bit16Backcolor, bit16Fontcolor)
		else:
			# 16 X 8 ASCII点阵
			p = drawHz(p, getASC_16Bytes(gb2312Char), 16, 8, bit16Backcolor, bit16Fontcolor)


# 从读取到内存里的字库中取得单个汉字的点阵信息，并保存在一个字节数组里
# 某个汉字的点阵信息在字库里的开始位置(字节偏移值)可以通过以下公式计算出来，这个是固定的
# 某汉字的字节偏移值 = ((汉字的区码 - 0xa1) * 94 + 汉字的位码 - 0xa1) * 32
# 而汉字的区码和位码其实就是该汉字以GB2312码编码时的第一和二个字节
# 我们使用的字库是16x16的点阵字库，所以每一个汉字的点阵信息可以
def getHZ_32Bytes(gb):
	retBytes32 = []

	print '汉字:' + unicode(gb, "gb2312").encode("utf8"),
	
	# 区码
	codeQu = struct.unpack('B', gb[0])[0]
	print '区码:' + str(codeQu) + ', ',

	# 位码
	codeWei = struct.unpack('B', gb[1])[0]
	print '位码:' + str(codeWei) + ', ',

	# 字节偏移值（非位偏移值）
	offset = ((codeQu - 0xa1) * 94 + codeWei - 0xa1) * 32
	print '偏移值:' + str(offset)
	
	# 从偏移值位置开始，向后连续取32个字节数据，即该汉字的点阵数据。
	# 每个汉字的点阵数据共16行，每行由两个字节的数据组成（16位）
	# 比如汉字“三”的点阵数据应该是下面这个样子的，0表示空像素，1表示有效像素
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （第1行，点阵数据字节1，字节2）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （第2行，点阵数据字节3，字节4）
	# 0 0 1 1 1 1 1 1 1 1 1 1 1 0 0 0 （第3行，点阵数据字节5，字节6）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （第4行，点阵数据字节7，字节8）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （第5行，点阵数据字节9，字节10）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 1 1 1 1 1 1 1 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 1 1 1 1 1 1 1 1 1 1 1 1 1 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （...）
	# 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 （第16行，点阵数据字节31，字节32）
	# 我们取到了这个点阵数据后，0的对应的像素绘制背景色，1对应的像素绘制文字色就可以了。
	for i in range(offset, offset+32):
		retBytes32.append(zk[i])
	return retBytes32

def getASC_16Bytes(gb):
	retBytes16 = []

	print 'ASCII字符:' + unicode(gb, "gb2312").encode("utf8"),

	# 字节偏移值 = ASCII码 × 16
	offset = ord(gb) * 16
	print '偏移值:' + str(offset)
	
	# 从偏移值位置开始，向后连续取16个字节数据，即该ASCII的点阵数据。
	for i in range(offset, offset+16):
		retBytes16.append(zkASC16[i])
	return retBytes16

class Point:
    def __init__(self):
        self.x = -1
        self.y = -1

class Weather:
    def __init__(self):
    	self.datetime = -1
        self.temp = -1
        self.temp_min = -1
        self.temp_max = -1
        self.description = -1
        self.icon = -1
        self.iconPixArray = -1
        self.cloudiness = -1
        self.windspeed = -1

# 显示单个汉字函数
# 为方便调用，第一个参数是一个简单的class，包含了x和y两个信息，用于返回下一个汉字的显示位置
def drawHz(pStart, byteArrayHz, fontH, fontW, bit16Backcolor, bit16Fontcolor):
	pNext = Point()

	# 检查显示位置是否有效，如果超出显示范围直接退出
	if (pStart.x<0):
		pStart.x=0
	if (pStart.y<0):
		pStart.y=0

	# 如果右侧已经无法显示一个完整的文字则试图换行
	if (pStart.x>128-fontW):
		# 换行前还要检查下方有无空位显示一行
		if (pStart.y>128-fontH):
			# 若下方已不足一行的行高则显示结束
			return pNext
		else:
			# 若下方可以继续显示新行，则换行。x坐标移到最左边0，y坐标下移一个汉字的高度
			pStart.x = 0
			pStart.y = pStart.y + fontH
	# 如果右侧还有空位则不换行在当前指定位置显示
	else:
		pass

	# 命令：0X2A
	# 设置绘图区域左上角的x坐标和右下角的x坐标（注意都是x坐标）
	write_command([0x2a])
	write_data_16bitHL(pStart.x)
	write_data_16bitHL(pStart.x+fontW-1)

	# 命令：0X2B
	# 设置绘图区域左上角的y坐标和右下角的y坐标（注意都是y坐标）
	write_command([0x2b])
	write_data_16bitHL(pStart.y)
	write_data_16bitHL(pStart.y+fontH-1)

	# 命令：0X2C
	# 开始在绘图区域绘图，每次绘制一个像素点的颜色，指针会自动移动到下一个像素点
	# 指针的移动顺序是，从左到右，从上到下（指针的移动顺序可以通过发送另外一个命令进行修改，请自己翻datasheet）
	# 由于之前使用命令2a和2b限制了绘图区域，所以指针到达右侧边界时会自动回到最左边并向下移动一个像素（像素换行）
	# 我们把汉字的点阵数据进行逐位判断，0的时候像素点绘制背景色，1的时候像素点绘制字体色即可。
	write_command([0x2c])
	for i in range(0, len(byteArrayHz)):
		byteHz=byteArrayHz[i]
		for j in range(0, 8):
			if ((byteHz << j) & 0x80):
				# TODO 性能有待提高，不要一个像素一个像素的传输，应该全部缓存在一个大字节数组里一次性用spi
				write_data_16bitHL(bit16Fontcolor)
			else:
				# TODO 性能有待提高，不要一个像素一个像素的传输，应该全部缓存在一个大字节数组里一次性用spi
				write_data_16bitHL(bit16Backcolor)

	# 返回当前汉字显示的结束位置，便于下一个汉字计算开始位置，判断换行等。。。
	pNext.x = pStart.x + fontW
	pNext.y = pStart.y

	return pNext

def drawImg(x, y, width, height, rgb565Array):
	# 命令：0X2A
	# 设置绘图区域左上角的x坐标和右下角的x坐标（注意都是x坐标）
	write_command([0x2a])
	write_data_16bitHL(x)
	write_data_16bitHL(x+width-1)

	# 命令：0X2B
	# 设置绘图区域左上角的y坐标和右下角的y坐标（注意都是y坐标）
	write_command([0x2b])
	write_data_16bitHL(y)
	write_data_16bitHL(y+height-1)

	# 命令：0X2C
	write_command([0x2c])
	buffSize = 2000
	GPIO.output(cs, False)
	GPIO.output(rs, True)
	for x in xrange(0,len(rgb565Array) / buffSize+1):
		spiSendData(rgb565Array[x*buffSize:x*buffSize+buffSize])

	GPIO.output(cs, True)

# Ret: "height", "width", "rgb565Array[]"
def getWebImageByteArray(url):
	content=urllib2.urlopen(url)
	file = cStringIO.StringIO(content.read())
	img = Image.open(file)
	pix = img.load()

	h = img.size[1]
	w = img.size[0]
	ret = {"height" : h , "width" : w, "rgb565Array" : []}
	for y in xrange(0, h):
		for x in xrange(0, w):
			r = pix[x, y][0] # 0xFF 1111 1111 -> 1111 1000
			g = pix[x, y][1] # 0x64 0110 0100 -> 0110 0000
			b = pix[x, y][2] # 0x32 0011 0010 -> 0011 0000

			# Desired result:
			#           R      G     B
			# 0xFB26 |11111 011|001 00110|
			#          BYTE1      BYTE2
			ret["rgb565Array"].append((r & 0xF8) | (g >> 5))
			ret["rgb565Array"].append((g<<3 & 0xE0) | (b >> 3))

	return ret

def getWeather():
	# 这样取得的字符串是unicode类型
	ret=urllib2.urlopen("http://api.openweathermap.org/data/2.5/forecast?q=Tokyo&units=metric&lang=zh_cn&APPID=db392ef3a3478e0a62cdfca71ef82b1d")
	oJson = json.load(ret)

	oWeather = Weather()
	oWeather.datetime = datetime.datetime.fromtimestamp(oJson["list"][0]["dt"])
	oWeather.temp = int(oJson["list"][0]["main"]["temp"])
	oWeather.temp_min = int(oJson["list"][0]["main"]["temp_min"])
	oWeather.temp_max = int(oJson["list"][0]["main"]["temp_max"])
	oWeather.description = oJson["list"][0]["weather"][0]["description"]
	
	oWeather.icon = oJson["list"][0]["weather"][0]["icon"]
	oWeather.iconPixArray = getWebImageByteArray("http://openweathermap.org/img/w/%s.png" % (oWeather.icon))

	oWeather.cloudiness = oJson["list"][0]["clouds"]["all"]
	oWeather.windspeed = oJson["list"][0]["wind"]["speed"]
	print "datetime:%s, temp:%s, temp_min:%s, temp_max:%s, description:%s, icon:%s, cloudiness:%s, windspeed:%s" % (oWeather.datetime, oWeather.temp, oWeather.temp_min, oWeather.temp_max, oWeather.description, oWeather.icon, oWeather.cloudiness, oWeather.windspeed)
	return oWeather

try:
	### 主程序开始 ###################################################
	# 打开spi设备，此处设备为/dev/spi-decv0.0
	bus=0
	device=0
	spi = spidev.SpiDev()
	spi.open(bus,device)
	spi.max_speed_hz=16000000

	GPIO.setmode(GPIO.BCM)
	GPIO.setup(cs, GPIO.OUT)
	GPIO.setup(rs, GPIO.OUT)
	GPIO.setup(sda, GPIO.OUT)
	GPIO.setup(scl, GPIO.OUT)
	GPIO.setup(reset, GPIO.OUT)

	backcolor = 0xffff

	lcd_init()

	zk=np.fromfile('HZK16.dat', dtype='b')
	zkASC16=np.fromfile('ASC16.dat', dtype='b')

	# backcolor
	drawRect(0, 0, 127, 127, backcolor)

	# date
	drawText(0,5, "2016/06/12 00:57", backcolor, 0xf800)
	#drawRect(0, 20, 127, 20, 0xffff)

	oWeather = getWeather()
	drawImg(0,20,oWeather.iconPixArray["width"], oWeather.iconPixArray["height"], oWeather.iconPixArray["rgb565Array"])

	drawText(50,25, oWeather.description, backcolor, 0xe8c4)
	drawText(50,45, "%s-%s度" % (oWeather.temp_min, oWeather.temp_max), backcolor, 0x7497)
	drawText(0,65, "风力：%s米/秒" % (oWeather.windspeed), backcolor, 0x7497)
	drawRect(0, 110, 127, 110, 0x0000)

	# drawRectFrame(40, 40, 80, 80, 6, 0xf800)
	# drawRectFrame(20, 50, 70, 90, 1, 0x7497)
	# drawLine(0, 0 , 127, 127, 0xffff)
	# drawLine(0, 0 , 127, 100, 0xffff)
	# drawLine(0, 0 , 127, 80, 0xffff)
	# drawLine(0, 0 , 127, 60, 0xffff)
	# drawLine(0, 0 , 127, 40, 0xffff)

	# drawRect(0, 0, 127, 20, 0xfd79)
	# drawRect(0, 21, 127, 40, 0x07e0)
	# drawRect(0, 41, 127, 60, 0xff80)
	# drawRect(0, 61, 127, 80, 0x9edd)
	# drawRect(0, 81, 127, 100, 0xe8c4)
	# drawRect(0, 101, 127, 127, 0x7497)

	# # moving cube test ------------------------------
	# drawRect(0, 0, 127, 127, 0xffff)
	# drawRect(0, 0, 20, 20, 0xff80)
	# drawRect(0, 0, 20, 20, 0xff80)

	# for z in xrange(1,5):
	# 	for x in xrange(1,107):
	# 		time.sleep(0.01)
	# 		drawRect(x-1, 0, x-1, 20, 0xffff)
	# 		drawRect(x+21, 0, x+21, 20, 0xff80)

	# 	for x in xrange(107,1,-1):
	# 		time.sleep(0.01)
	# 		drawRect(x-1, 0, x-1, 20, 0xff80)
	# 		drawRect(x+21, 0, x+21, 20, 0xffff)
	# # moving cube test ------------------------------
	

	# for x in xrange(100,0,-1):
	# 	time.sleep(0.1)
	# 	drawRect(0, 0, 127, 127, 0xffff)
	# 	drawRect(x, 0, x+20, 20, 0xFBE4)
	
	#drawPic()
	#time.sleep(3)
	#drawMario()
	#time.sleep(3)
	#drawPic()
	#time.sleep(3)
	#drawMario()
	#time.sleep(3)

	# 一次性将字库全部读入内存
	#zk=np.fromfile('HZK16.dat', dtype='b')

	#p = Point()
	#p.x = 0
	#p.y = 30
	#text = "使用树莓派的ＧＰＩＯ来驱动一块液晶显示屏的例子。Ｂｙ：芒果爱吃胡萝卜"
	# 取得文本的字数
	#cnt=len(text.decode('utf-8'))
	#for i in range(0, cnt):
		# 逐字调用绘制单个汉字的函数
		# 第一次调用时设置一个初始位置
		# 每次绘制完一个汉字，返回值里存放的是下一个汉字的绘制开始位置
		# 如此循环往复，直到所有汉字全部显示完毕或者显示到边界无法继续显示为止
	#	p = drawHz16x16(p, getHZ_32Bytes(text[i*3:i*3+3]), 0x0000, 0xff80)

	spi.close()


except KeyboardInterrupt:
	pass

# 清理GPIO口
#GPIO.cleanup()
