#!/usr/bin/env python3
import socket

socket_address = '127.0.0.1'
socket_port = 61234

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((socket_address, socket_port))
    s.sendall(b'supersneakylocation')
    data = s.recv(1024)

print('Received', repr(data))
