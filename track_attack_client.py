#!/usr/bin/env python3
import socket

socket_address = '127.0.0.1'
socket_port = 61234

try:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.settimeout(10)
		s.connect((socket_address, socket_port))
		s.sendall(b'supersneakylocation')
		data = s.recv(1024)
		print('Received', repr(data))
		resp = data.decode('utf-8');
		respcount = len(resp.split('\n'))
		if respcount == 3:
			#elevation, longitude, latitude = [i for i in resp.split('\n')]
			elevation, longitude, latitude = [i for i in data.decode('utf-8').split('\n')]
			elevation = int(elevation)
			print("Elevation: "+str(elevation))
			print("Longitude: "+longitude)
			print("Latitude: "+latitude)
		elif respcount == 1:
			if resp == 'invalid':
				print("INVALID LOCATION")
			elif resp == 'bad secret':
				print("BAD SECRET")
			else:
				print("NOPE 1")
		else:
			print("NOPE")
except:
	print("Caught exception while connecting to server")
