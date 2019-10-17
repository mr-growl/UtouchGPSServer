#!/usr/bin/env python3
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; version 3.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

#This is a modified version of the code found here:

#https://framagit.org/ernesst/gps-utouch-tracker/blob/master/GPS_tracking.py

#The following is the original header from the original code

#Copyright (C) 2019 Ernesst <ernesst@posteo.net>
#This program is free software; you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation; version 3.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 0.1 intial release 
# 0.2 update UI

import subprocess
import re
import sys
import socket

import math as mod_math

release = "0.2"

socket_address = '127.0.0.1'
socket_port = 61234
socket_secret = b'supersneakylocation'

location_valid = False

s = None

def read_gps():
	retry_limit = 10
	retry_count = 0

	global latitude
	global longitude
	global accuracy
	global elevation
	global location_valid
	latitude = str("")
	longitude = str("")
	elevation = str("")
	accuracy = str("")
	elevation_a = []
	last_frame_good = False

	cmd = ['sudo test_gps']
	p = subprocess.Popen(cmd, stdout = subprocess.PIPE,
	stderr = subprocess.STDOUT, shell = True)
	for line in p.stdout:
		line = line.decode('utf-8')
		# search for "*** sv status" to signal start of new frame"
		if re.search("^\*\*\* sv status", line):
				print("START OF NEW FRAME")
				retry_count = retry_count + 1
				if retry_count > retry_limit:
					print("MAX RETRYS HIT... LEAVING")
					location_valid = False
					p.kill()
					return elevation,longitude,latitude
					
				#if the last frame ended without an accuracy value then set the current location as not valid
				if last_frame_good is False:
					    location_valid = False
				#reset the 
				last_frame_good = False

		if re.search("^latitude", line):
				latitude = line.split()
				latitude = latitude[1]

		if re.search("^longtide", line): #bug in test_gps
				longitude = line.split()
				longitude = longitude[1]

		if re.search("^accuracy", line): #bug in test_gps
				accuracy = line.split()
				accuracy= accuracy[1]

		if re.search("elevation", line): #bug in test_gps
				elevation_T = line.split()
				#print(elevation)
				elevation_a.append(elevation_T[1])
				#print(elevation)

		if accuracy != "":
			location_valid = True
			print("GOOD FRAME!!!")
			#print(line + "=> accuracy : "  + accuracy)
			#print(line + "=> longitude : "  + longitude)
			#print(line + "=> latitude : "  + latitude)
			for i in range(len(elevation_a)):
				elevation_a[i] = float(elevation_a[i])
			#elevation = int(sum(elevation_a) / float(len(elevation_a)))
			elevation = str(int(sum(elevation_a) / float(len(elevation_a))))
			p.kill()
			return elevation,longitude,latitude

try:
	while True:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.bind((socket_address, socket_port))
			s.listen()
			conn, addr = s.accept()
			with conn:
				print('Connected by', addr)
				while True:
					data = conn.recv(1024)
					if not data:
						break
					#check if the secret was sent
					if socket_secret == data:
						print("SECRET ACCEPTED")
						read_gps()
						if location_valid is True:
							print("SENDING GOOD LOCATION")
							print(type(elevation))
							print(type(longitude))
							print(type(latitude))
							conn.sendall(str.encode("\n".join([elevation,longitude,latitude])))
						else:
							print("SENDING BAD LOCATION")
							conn.sendall(str.encode("\n".join(["invalid","invalid","invalid"])))
					else:
						print("BAD SECRET")
						conn.sendall(str.encode("\n".join(["bad secret","bad secret","bad secret"])))

except KeyboardInterrupt:
	try:
		s.close()
	except:
		print("Problem closing socket")
	sys.exit()
