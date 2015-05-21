#!/usr/bin/env python
# encoding: utf-8

import RPi.GPIO
import time

# LED正极连接的GPIO口
LED = 17

# 声音感应器OUT口连接的GPIO口
SENSOR = 4

# 当前LED灯的开关状态
flg = False

RPi.GPIO.setmode(RPi.GPIO.BCM)

# 指定GPIO4（声音感应器的OUT口连接的GPIO口）的模式为输入模式
# 默认拉高到高电平，低电平表示OUT口有输出
RPi.GPIO.setup(SENSOR, RPi.GPIO.IN, pull_up_down=RPi.GPIO.PUD_UP)

# 指定GPIO17（LED长针连接的GPIO针脚）的模式为输出模式
RPi.GPIO.setup(LED, RPi.GPIO.OUT)

try:
	while True:
		# 检测声音感应器是否输出低电平，若是低电平，表示声音被检测到，点亮或关闭LED灯
		if (RPi.GPIO.input(SENSOR) == 0):
			flg = not flg
			RPi.GPIO.output(LED, flg)
			# 稍微延时一会，避免刚点亮就熄灭，或者刚熄灭就点亮。
			time.sleep(0.5)

except KeyboardInterrupt:
	pass

RPi.GPIO.cleanup()
