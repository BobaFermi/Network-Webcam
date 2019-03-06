#!/usr/bin/env python

import cv2
import numpy as np
import socket
import sys
import pickle
import struct

cap1 = cv2.VideoCapture(0) 
fps1 = cap1.set(5, 15)
cap2 = cv2.VideoCapture(1) 
fps2 = cap2.set(5, 15)

print "Created Video connection"

clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
clientsocket.connect(('172.16.1.10',8089))
cv2.namedWindow('Camera 1', cv2.WINDOW_FREERATIO)
cv2.namedWindow('Camera 2', cv2.WINDOW_FREERATIO)

cv2.setWindowProperty('Camera 2', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

print "Created Network socket and figures."


while(True):
	ret, frame1 = cap1.read()
	gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)
	ret, frame2 = cap2.read()
	gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)
	
	cv2.imshow('Camera 1',gray1)
	cv2.imshow('Camera 2',gray2)
	gray1[0,0] = gray2[0,0] = 172
	gray1[0,1] = gray2[0,1] = 16
	gray1[0,2] = gray2[0,2] = 1
	gray1[0,3] = gray2[0,3] = 20
	gray1[0,4] = 201
	gray2[0,4] = 202
	
	data1 = pickle.dumps(gray1)
	clientsocket.sendall(struct.pack("=L", len(data1))+data1)
	data2 = pickle.dumps(gray2)
	clientsocket.sendall(struct.pack("=L", len(data2))+data2)

	if cv2.waitKey(1) == ord('q'):
		break

cap1.release()
cap2.release()
cv2.destroyAllWindows()
