#!/usr/bin/python

import socket
import sys
import cv2
import pickle
import numpy as np
import struct

concat = None			#will be a numpy array that contains all images stitched together
frame1 = frame2 = np.array([])	#initialise a numpy array
HOST = ''			#for binding to the send computer
PORT=8089			#port used by other computer for sending
camnum = 0			#keep track of number of cameras for sizing on screen
camcycle = 2			#used to change order of images in case of three frames being stitched

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)		#instantiate a socket
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)		#set some options 
print 'Socket created'						#debug
s.bind((HOST,PORT))						#bind to port and empty 'host' dude
print 'Socket bind complete'					#debug
s.listen(10)							#allows 10 connection requests, probably overkill
print 'Socket now listening'					#debug
conn,addr=s.accept()						#accept connection to a computer that connects

data = ""							#no data yet
payload_size = struct.calcsize("=L")	#use same code as send computer to interpret payload length (=L - unsigned long)

comcam = cv2.VideoCapture(0)					#instantiate webcam connected to this computer

cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)			#create window for all webcam feeds
cv2.setWindowProperty('stream', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)		#make window fullscreen

while True:
	while len(data) < payload_size:				#while the received data is shorter than length of payload number
		data += conn.recv(4096)				#receive length of data and start of data, 4096 bytes at a time
	packed_msg_size = data[:payload_size]			#read payload length from start of data

	data = data[payload_size:]				#everything else is the start of the data
	msg_size = struct.unpack("=L", packed_msg_size)[0]
	while len(data) < msg_size:				#while received data is less than we expect to receive
		data += conn.recv(4096)				#keep receiving data, 4096 at a time
	frame_data = data[:msg_size]				#the amount of data that constitutes one frame
	data = data[msg_size:]					#the rest of the data afterwards

	ret, comframe = comcam.read()				#read from the connected webcam
	gray = cv2.cvtColor(comframe, cv2.COLOR_BGR2GRAY)	#convert to grayscale

	frame=pickle.loads(frame_data)				#unserialise data
	IPID = '%r.%r.%r.%r.%r'%(frame[0,0],frame[0,1],frame[0,2],frame[0,3],frame[0,4])	#read identifier pixels
	if IPID == '172.16.1.20.201':			#webcam 1 from the send computer
		frame2 = frame				
	if IPID == '172.16.1.20.202':			#webcam 2 from the send computer
		frame1 = frame
	if (frame1.size == 0 or frame2.size == 0): #if we haven't received both frames from the send computer
		pass				   #do nothing
	else:
		if camnum == 0:			#0 means all images are stitched together on the screen
			if camcycle == 0:	#0 makes the webcam connected to this computer the largest image
				smallframes = np.concatenate((frame1, frame2), axis=0)	#stitch frames from network together vertically
				concat = np.concatenate((smallframes,cv2.resize(gray, (0,0), fx=1.5,fy=2)), axis=1)	#stitch webcam image to network images horizontally
			if camcycle == 1:	#1 makes webcam 1 from other computer the largest image
				smallframes = np.concatenate((frame2, gray), axis=0)	#webcam 2 from other computer and webcam from this computer
				concat = np.concatenate((smallframes,cv2.resize(frame1, (0,0), fx=1.5,fy=2)), axis=1)	#stitch all images together
			if camcycle == 2:	#2 makes webcam 2 from other computer the largest image
				smallframes = np.concatenate((gray, frame1), axis=0)
				concat = np.concatenate((smallframes,cv2.resize(frame2, (0,0), fx=1.5,fy=2)), axis=1)
		elif camnum == 1:		#1 means only webcam 1 from other computer is displayed
			concat = frame1
		elif camnum == 2:		#2 means only webcam 2 from other computer is displayed
			concat = frame2
		elif camnum == 3:		#3 means only the webcam from this computer is displayed
			concat = gray		
		cv2.imshow('stream', concat)	#display the selected image(s) in the window
	k = cv2.waitKey(1)			#allows the image to display and allows a wait for keyboard input
	if k == ord('q'):			#if 'q' is pressed, exit while loop and quit
		break
	elif k == ord('a'):			#if 'a' is pressed, show all images stitched together in fullscreen
		camnum = 0
		cv2.destroyAllWindows()		#destroy and open the window again so we can set fullscreen properties
		cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)
		cv2.setWindowProperty('stream', cv2.WND_PROP_FULLSCREEN,  cv2.WINDOW_FULLSCREEN) 
	elif k == ord('s'):			#if 's' is pressed, show only cam 1 from other computer on fullscreen
		camnum = 1			
		cv2.destroyAllWindows()
		cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)
		cv2.setWindowProperty('stream', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	elif k == ord('d'):			#if 'd' is pressed, show only cam 2 from other computer on fullscreen
		camnum = 2
		cv2.destroyAllWindows()
		cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)
		cv2.setWindowProperty('stream', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	elif k == ord('f'):			#if 'f' is pressed, show only the webcam connected to this computer on fullscreen
		camnum = 3
		cv2.destroyAllWindows()
		cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)
		cv2.setWindowProperty('stream', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	elif k == ord('g'):			#if 'g' is pressed, show all images stitched together, in a windowed mode
		camnum = 0
		cv2.destroyAllWindows()
		cv2.namedWindow('stream', cv2.WINDOW_FREERATIO)
	elif k == ord('l'):			#if 'l' is pressed, rotate selection in stitched mode to make one image bigger than others
		if camcycle == 2:
			camcycle = 0
		else:
			camcycle += 1

comcam.release()		#release webcam connected to this computer	
s.close()			#close socket
cv2.destroyAllWindows()		#destroy all windows operated by OpenCV
