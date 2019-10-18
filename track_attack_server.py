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
import threading
import re
import sys
import socket
import time

#############################################
# SOCKET SETTINGS
# socket_address: address to listen on
# socket_port: the port to listen on
# socket_secret: a shared secret that clients
#   use to prove that they are allowed to
#   grab the location.
socket_address = '127.0.0.1'
socket_port = 61234
socket_secret = b'supersneakylocation'
#############################################


############################################
# SHARED VARIABLES (things used by both
#   threads)
#epoch time time of last locationrequest
last_request_seconds = 0
#current "valid" location formatted for network
current_location = str.encode("invalid")
############################################

#How long, in seconds,  to keep the GPS running after last request
request_runout_seconds = 300

#set to True to enable debug messages
debug = False

#the Socket
s = None

###########################
# THE GPS THREAD FUNCTION
###########################
def read_gps():
	global latitude
	global longitude
	global accuracy
	global elevation
	global last_request_seconds
	global request_runout_seconds
	global current_location

	latitude = str("")
	longitude = str("")
	elevation = str("")
	accuracy = str("")
	elevation_a = []

	location_expiry_seconds = 10
	last_valid_location_seconds = 0

	last_frame_good = False
	running = False

	cmd = ['sudo test_gps']

	#this is the main loop
	while True:
		#if we are not running, keep an eye out for requests and sleep for a second if no requests have been received
		if running is False:
			if int(time.time()) - last_request_seconds < request_runout_seconds:
				if debug:
					print("GPS SERVER WAKING UP")
				p = subprocess.Popen(cmd, stdout = subprocess.PIPE,
				stderr = subprocess.STDOUT, shell = True)
				running = True
			else:
				time.sleep(1)
		#if we are running then parse the output of the test_gps command
		if running is True:
			for line in p.stdout:
				line = line.decode('utf-8')
				# search for "*** sv status" to signal start of new frame"
				if re.search("^\*\*\* sv status", line):
					if debug:
						print("START OF NEW FRAME")
							
					#if the last frame ended without an accuracy value then set the current location as not valid
					if last_frame_good is False:
						if int(time.time()) - last_valid_location_seconds > location_expiry_seconds:
							current_location = str.encode("invalid")
					#reset the 
					last_frame_good = False
					if int(time.time()) - last_request_seconds > request_runout_seconds:
						if debug:
							print("GPS SERVER GOING TO SLEEP")
						running = False
						p.kill()
						current_location = str.encode("invalid")
						break;
		
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
					last_frame_good = True
					last_valid_location_seconds = int(time.time())
					if debug:
						print("GOOD FRAME!!!")
					for i in range(len(elevation_a)):
						elevation_a[i] = float(elevation_a[i])
					elevation = str(int(sum(elevation_a) / float(len(elevation_a))))
					current_location = str.encode("\n".join([elevation,longitude,latitude]))
					accuracy = ""




if __name__ == "__main__":
	location_thread = threading.Thread(target=read_gps, daemon=True)
	location_thread.start()
	try:
		while True:
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
				try:
					s.bind((socket_address, socket_port))
					s.listen()
					conn, addr = s.accept()
					with conn:
						if debug:
							print('Connected by', addr)
						while True:
							data = conn.recv(1024)
							if not data:
								break
							#check if the secret was sent
							if socket_secret == data:
								if debug:
									print("SECRET ACCEPTED")
								last_request_seconds = int(time.time())
								conn.sendall(current_location)
							else:
								if debug:
									print("BAD SECRET")
								conn.sendall(str.encode("bad secret"))
					s.close()
				except KeyboardInterrupt:
					try:
						s.close()
					except:
						if debug:
							print("Problem closing socket")
					sys.exit()
				except:
					dummy = True
					#if debug:
						#print("Problem Binding Server")
	
	
	except KeyboardInterrupt:
		try:
			s.close()
		except:
			if debug:
				print("Problem closing socket")
		sys.exit()
