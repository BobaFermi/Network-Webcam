# Network-Webcam

This project consists of two python 2.7 scripts which use OpenCV, Numpy, Pickle and Socket to capture, manipulate, transfer and display a webcam feed over a network. Used for monitoring parts of a lab where powerful lasers do not permit direct observation by eye. 

One script continuously grabs frames from two Webcams, converts them to grayscale and serialises them to be sent over the network. 

The other script receives the grayscale frames through the network and grabs frames from a webcam itself, displaying the images fullscreen. The user can decide whether the three images are stitched together and all displayed at once, and which image takes priority over the other two; or whether a single webcam image is just displayed fullscreen by itself. 
