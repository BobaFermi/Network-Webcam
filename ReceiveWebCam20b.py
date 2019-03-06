#!/usr/bin/python

import socket
import sys
import cv2
import pickle
import numpy as np
import struct
concat = None
frame1 = frame2 = np.array([])
HOST = ''
PORT=8089
camnum = 0
camcycle = 2


s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print 'Socket created'
s.bind((HOST,PORT))
print 'Socket bind complete'
s.listen(10)
print 'Socket now listening'
conn,addr=s.accept()

data = ""
payload_size = struct.calcsize("=L")

comcam = cv2.VideoCapture(0)

cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)
cv2.setWindowProperty('stream', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

while True:
	while len(data) < payload_size:
		data += conn.recv(4096)
	packed_msg_size = data[:payload_size]

	data = data[payload_size:]
	msg_size = struct.unpack("=L", packed_msg_size)[0]
	while len(data) < msg_size:
		data += conn.recv(4096)
	frame_data = data[:msg_size]	
	data = data[msg_size:]

	ret, comframe = comcam.read()
	gray = cv2.cvtColor(comframe, cv2.COLOR_BGR2GRAY)

	frame=pickle.loads(frame_data)
	IPID = '%r.%r.%r.%r.%r'%(frame[0,0],frame[0,1],frame[0,2],frame[0,3],frame[0,4])
	if IPID == '172.16.1.20.201':
		frame2 = frame
	if IPID == '172.16.1.20.202':
		frame1 = frame
	if (frame1.size == 0 or frame2.size == 0):
		pass
	else:
		if camnum == 0:
			if camcycle == 0:
				smallframes = np.concatenate((frame1, frame2), axis=0)
#				concat = np.concatenate((smallframes,gray.repeat(2, axis=0)), axis=1)
				concat = np.concatenate((smallframes,cv2.resize(gray, (0,0), fx=1.5,fy=2)), axis=1)
			if camcycle == 1:
				smallframes = np.concatenate((frame2, gray), axis=0)
#				concat = np.concatenate((smallframes,frame1.repeat(2, axis=0)), axis=1)
				concat = np.concatenate((smallframes,cv2.resize(frame1, (0,0), fx=1.5,fy=2)), axis=1)
			if camcycle == 2:
				smallframes = np.concatenate((gray, frame1), axis=0)
#				concat = np.concatenate((smallframes,frame2.repeat(2, axis=0)), axis=1)
				concat = np.concatenate((smallframes,cv2.resize(frame2, (0,0), fx=1.5,fy=2)), axis=1)
		elif camnum == 1:
			concat = frame1
		elif camnum == 2:
			concat = frame2
		elif camnum == 3:
			concat = gray
		cv2.imshow('stream', concat)
	k = cv2.waitKey(1)
	if k == ord('q'):
		break
	elif k == ord('a'):
		camnum = 0
		cv2.destroyAllWindows()
		cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)
		cv2.setWindowProperty('stream', cv2.WND_PROP_FULLSCREEN,  cv2.WINDOW_FULLSCREEN)
	elif k == ord('s'):
		camnum = 1
		cv2.destroyAllWindows()
		cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)
		cv2.setWindowProperty('stream', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	elif k == ord('d'):
		camnum = 2
		cv2.destroyAllWindows()
		cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)
		cv2.setWindowProperty('stream', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	elif k == ord('f'):
		camnum = 3
		cv2.destroyAllWindows()
		cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)
		cv2.setWindowProperty('stream', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	elif k == ord('g'):
		camnum = 0
		cv2.destroyAllWindows()
		cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)
	elif k == ord('l'):
		if camcycle == 2:
			camcycle = 0
		else:
			camcycle += 1

comcam.release()
s.close()
cv2.destroyAllWindows()
