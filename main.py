import select
import usocket as socket
import time
import os
import lcd_2004
import machine
import lcd_2004
from time import sleep, sleep_ms

server_address = ('192.168.1.217', 8099)
i2c=lcd_2004.lcd(39,22,21) #Change to match your device (Address, SCL Pin, SDA Pin)
backlight_timer = 0

led = machine.Pin(4, machine.Pin.OUT)
button1 = machine.Pin(5, machine.Pin.IN)
button2 = machine.Pin(12, machine.Pin.IN)
button3 = machine.Pin(13, machine.Pin.IN)
button4 = machine.Pin(14, machine.Pin.IN)
button5 = machine.Pin(15, machine.Pin.IN)

i2c.lcd_print(">>>   G P I O   <<< ",1,0)
i2c.lcd_print("  General Purpose   ",2,0)
i2c.lcd_print("Information Orifice",3,0)


def connect():
	global s
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	connected=False
	while not connected:
		try:
			s.connect(server_address)
			connected=True;
			print("connected")
			return True
		except OSError as exc:
			sleep(1)
			print(exc.args[0])
			s.close()
			return False

def display_msg(message):
	response = message.split("&")
	i2c.lcd_clear()
	i = 0
	for lines in response:
		i2c.lcd_print(response[i],i+1,0)
		i = i + 1

def get_data(data_type):
	led.on()
	connected=connect()
	while connected:
		s.send(data_type)
		from_server = s.recv(4096)
		message = from_server.decode("ascii")
		display_msg(message)
		s.close()
		connected=False
	led.off()
	

def do_forever():
	starttime = round(time.time())
	maxidle = 30

	while True:
		b1 = button1.value()
		b2 = button2.value()
		b3 = button3.value()
		b4 = button4.value()
		b5 = button5.value()
		sleep(0.1)

		if b1 == 1:
			get_data("button1")
			i2c.lcd_backlight(True)
			starttime = round(time.time())
		if b2 == 1:
			get_data("button2")
			i2c.lcd_backlight(True)
			starttime = round(time.time())
		if b3 == 1:
			get_data("button3")
			i2c.lcd_backlight(True)
			starttime = round(time.time())
		if b4 == 1:
			get_data("button4")
			i2c.lcd_backlight(True)
			starttime = round(time.time())
		if b5 == 1:
			get_data("button5")
			i2c.lcd_backlight(True)
			starttime = round(time.time())

		if (round(time.time()) - starttime) > maxidle:
			i2c.lcd_backlight(False)
		

do_forever()
