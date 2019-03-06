# Remote-Webcam-Feed

Python 2.7 script for transmitting webcam images through a network for remote viewing, and another script for receiveing and displaying images. Used for monitoring parts of a lab where powerful lasers do not permit direct observation by eye. 

The code uses OpenCV and numpy to capture, manipulate and display the images; pickle to serialise the data before transmission and socket to send it. 
