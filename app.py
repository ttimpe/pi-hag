#!/usr/bin/env python3
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import serial
import re
import pygame
import os.path
import sys

REGEX_DS036 = re.compile(r"hP\d{4}")
REGEX_DS033 = re.compile(r"hR")
REGEX_DS031 = re.compile(r"hM")
REGEX_DS032 = re.compile(r"hN")
REGEX_DS030 = re.compile(r"hS")
REGEX_DS301 = re.compile(r"hV")
LAST_PLAYED_ANNOUNCEMENT_ID=''



def process_special_characters(self, telegram):
	"""
	Replace IBIS special characters and strip unsupported characters.
		
		telegram:
		The telegram as a string
		
		Returns:
		The processed telegram
		"""
		
	telegram = telegram.replace("ä", "{")
	telegram = telegram.replace("ö", "|")
	telegram = telegram.replace("ü", "}")
	telegram = telegram.replace("ß", "~")
	telegram = telegram.replace("Ä", "[")
	telegram = telegram.replace("Ö", "\\")
	telegram = telegram.replace("Ü", "]")
	telegram = telegram.encode('ascii', errors = 'replace')
	return telegram






def wrap_telegram(self, telegram):
	telegram.append(0x0D)
	checksum = 0x7F
	for byte in telegram:
		checksum ^= byte
		telegram.append(checksum)
		return telegram

def send_telegram(self, telegram, reply_length = 0):
	if type(telegram) is str:
		telegram = process_special_characters(telegram)
		telegram = bytearray(telegram)
	elif type(telegram) is bytes:
		telegram = bytearray(telegram)

		telegram = wrap_telegram(telegram)
		print(telegram)


def process_incoming_line(line):
	# check checksum
	# match to type
	print(len(line))
	print(str(line))

	if chr(line[-1]) == '\r':
		stripped_telegram = line[:-1].decode('ascii')
		print(stripped_telegram)
		print(REGEX_DS036.match(stripped_telegram))
		if REGEX_DS036.match(stripped_telegram) is not None:
			process_DS036(stripped_telegram)
	else:
		print("Telegram unknown")
def process_DS036(line):
	global LAST_PLAYED_ANNOUNCEMENT_ID
	number = line[2:6]
	if number != LAST_PLAYED_ANNOUNCEMENT_ID:
		file_path = 'audio/' + number + '.wav'
		if os.path.isfile(file_path):

			sound = pygame.mixer.Sound(file_path)
			sound.play()
			print("Playing announcement with ID " + number)
			LAST_PLAYED_ANNOUNCEMENT_ID = number
		else:
			print("Did not find announcement file with ID " + number)


pygame.init()


port = serial.Serial()
port.baudrate = 1200
port.port = '/dev/tty.usbserial-1420'
port.bytesize = serial.SEVENBITS
port.parity = serial.PARITY_EVEN
port.stopbits=serial.STOPBITS_TWO
port.timeout = 10.0

port.open()

port.flushInput()

while True:
	try:
		input_bytes = port.read_until(b'\r')
		process_incoming_line(input_bytes[1:])
	except Exception as error:
		print("Error",error)
