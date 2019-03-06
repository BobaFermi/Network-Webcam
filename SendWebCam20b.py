#!/usr/bin/env python

import cv2
import numpy as np
import socket
import sys
import pickle
import struct

#initialise both cameras, attempt to set frame rate to 15 fps to make things easier on the network
cap1 = cv2.VideoCapture(0) 
fps1 = cap1.set(5, 15)
cap2 = cv2.VideoCapture(1) 
fps2 = cap2.set(5, 15)

print "Created Video connection" #debug

clientsocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM) #set up socket for transmission
clientsocket.connect(('172.16.1.10',8089))		      #connect using specified IP address and port

#create windows to display the image, set freeratio so they can be resized however the user likes
cv2.namedWindow('Camera 1', cv2.WINDOW_FREERATIO)
cv2.namedWindow('Camera 2', cv2.WINDOW_FREERATIO)

#make window 2 fullscreen (this is the important one for our purpose)
cv2.setWindowProperty('Camera 2', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

print "Created Network socket and figures." #debug


while(True):
	ret, frame1 = cap1.read()		#read single frame from webcam 1
	gray1 = cv2.cvtColor(frame1, cv2.COLOR_BGR2GRAY)	#convert to grayscale, less data to transmit and colour isn't important to us
	ret, frame2 = cap2.read()		#read single frame from webcam 2
	gray2 = cv2.cvtColor(frame2, cv2.COLOR_BGR2GRAY)	#convert to grayscale
	
	#display both cameras in their respective windows
	cv2.imshow('Camera 1',gray1)
	cv2.imshow('Camera 2',gray2)
	
	#Adjust some pixel values to behave as identifier pixels (previously the recipient 
	#computer could not tell which frame came from which webcam, so the frames were switching like mad).
	#Chose IP address of send computer because initial idea was to have a couple of send computers
	gray1[0,0] = gray2[0,0] = 172
	gray1[0,1] = gray2[0,1] = 16
	gray1[0,2] = gray2[0,2] = 1
	gray1[0,3] = gray2[0,3] = 20	
	gray1[0,4] = 201		#webcam 1
	gray2[0,4] = 202		#webcam 2
	
	data1 = pickle.dumps(gray1)	#Serialise data
	clientsocket.sendall(struct.pack("=L", len(data1))+data1) #send data with preamble to give expected data length
	data2 = pickle.dumps(gray2)	
	clientsocket.sendall(struct.pack("=L", len(data2))+data2)

	if cv2.waitKey(1) == ord('q'):		#This command actually allows the image to display, doubling up as a wait for input
		break				#If the user presses 'q', exit this while loop

cap1.release()			#release webcam 1
cap2.release()			#release webcam 2
cv2.destroyAllWindows()		#destroy any OpenCV windows
