#!/usr/bin/env python
 
import RPi.GPIO as GPIO
import time
from threading import Timer

A=12
status=True

GPIO.setmode(GPIO.BOARD)
GPIO.setup(A,GPIO.OUT)
GPIO.output(A,status)

for x in xrange(1,500):
	status = not status
	GPIO.output(A,status)
	time.sleep(0.05)

