#!/usr/bin/env python
 
import RPi.GPIO as GPIO
import time

VPRG=17
SIN=13
SCLK=19
XLAT=27
BLANK=23
DCPRG=18
GSCLK=4

# 传输GSData(0-4095)
def setGSData(data):
	# print ""
	# print "S-----------setByte---------------:", hex(data)
	for bit in range(0,12):
		# 传入的数字从高位到低位依次判断是否为1，若为1则设置高电平，否则设置低电平
		# 判断的方法是先向左移位，把要判断的位移动到最高位然后跟0x800（1000 0000 0000）相与，
		# 如果结果仍然是0x80（1000 0000 0000）就表示最高位是1，否则最高位就是0
		if ((data<<bit) & 0x800 == 0x800):
			setBitData(True)
			# print "1",
		else:
			setBitData(False)
			# print "0",
	# print ""
	# print "E-----------setByte---------------"

def setBitData(data):
	GPIO.output(SCLK, False)
	GPIO.output(SIN, data)
	GPIO.output(SCLK, True)

# 输出GSCLK时钟信号
def runGSCLK():
	i=0
	while(1):
		i+=1
		if i>=4096:
			# 注意，每次计数到4095时需要手动重置一次芯片的计数器
			GPIO.output(BLANK, True)
			#time.sleep(0.001);
			GPIO.output(BLANK, False)
			i=0

try:
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(VPRG, GPIO.OUT)
	GPIO.setup(SIN, GPIO.OUT)
	GPIO.setup(SCLK, GPIO.OUT)
	GPIO.setup(XLAT, GPIO.OUT)
	GPIO.setup(BLANK, GPIO.OUT)
	GPIO.setup(DCPRG, GPIO.OUT)
	
	GPIO.setup(GSCLK, GPIO.ALT0)
	GPIO.setclock(GSCLK, 9600000)
	GPIO.output(GSCLK, True)

	# VPRG设置为L，使其工作在GS mode
	GPIO.output(VPRG, False)

	# BLANK设置为H，关闭所有输出
	GPIO.output(BLANK, True)

	GPIO.output(DCPRG, True)

	# 传送12bit X 16组PWM数值GSn(n=0-15)，共192bit
	# 每组数据的值范围是0-4095
	# 因为是通过移位寄存器传输，所以传送顺序是倒序的：GS15，GS14。。。GS0
	# GSn决定了OUTn的PWM调宽。（GSn / 4095 = 0% - 100%）
	setGSData(0) # GS15 本文不使用15-3号输出，设为0
	setGSData(0) # GS14
	setGSData(0) # GS13
	setGSData(0) # GS12
	setGSData(0) # GS11
	setGSData(0) # GS10
	setGSData(0) # GS9
	setGSData(0) # GS8
	setGSData(0) # GS7
	setGSData(0) # GS6
	setGSData(0) # GS5
	setGSData(0) # GS4
	setGSData(0) # GS3
	
	# print "GS2"
	setGSData(4095) # GS2

	# print "GS1"
	setGSData(2500) # GS1

	# print "GS0"
	setGSData(500) # GS0

	# 送完GS数据后，创造XLAT的上升沿，将移位寄存器的数据一次性送入GS寄存器
	GPIO.output(XLAT, False)
	GPIO.output(XLAT, True)

	# BLANK设置为L，打开所有输出
	# GPIO.output(BLANK, False)

	# 准备工作完毕，下面向GSCLK输送时钟信号（高低电平交互的方波信号）
	# TLC5940会根据这个时钟信号进行从0-4095的计数，一边计数一边检查各GSn的设定值，一旦到达GSn的值，则切换OUTn的电平
	# 一直计数到4095为止，再从0开始重新计数。从0计数到4095就是一个高低电平的切换周期。
	# 所以我们给5940提供的时钟频率越快，最后输出的PWM频率就越快
	# 最后输出的PWM的频率 = 时钟信号的频率 / 4095
	# 比如时钟频率是8M，则最后从各OUT口输出的PWM频率是8MHz / 4095 = 1.953KHz
	# 根据TLC5940的官方文档，GSCLK可支持最高30MHz的时钟频率，也就是最高可以输出7.3KHz的PWM信号。
	# 如果是控制LED的亮度，那么让人眼感觉不到闪烁的最低频率应该是50Hz以上，
	# 所以我们应该至少给GSCLK提供不低于50 X 4095 = 200KHz的方波。
	# 树莓派Python的GPIO库翻转IO口的速度不高，实测速度只能达到60KHz，
	# 导致最后输出的PWM频率只有14Hz，会有明显的闪烁感
	runGSCLK()

except KeyboardInterrupt:
	pass

# 清理GPIO口
GPIO.cleanup()