
import time
import io
import threading
import picamera
import socket
import struct
import time
import numpy
import math

client_socket = None
#connection = client_socket.makefile('wb')
address = ('10.0.0.8',10000)
client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
connection = client_socket.makefile('wb')
client_socket.connect(address)
try:
	with picamera.PiCamera() as camera:
		camera.resolution = (640, 480)
		# Start a preview and let the camera warm up for 2 seconds
		camera.start_preview()
		time.sleep(2)
		# Note the start time and construct a stream to hold image data
		# temporarily (we could write it directly to connection but in this
		# case we want to find out the size of each capture first to keep
		# our protocol simple)
		stream = io.BytesIO()
		for foo in camera.capture_continuous(stream, 'jpeg'):
		# Write the length of the capture to the stream and flush to
		# ensure it actually gets sent
			connection.write(struct.pack('<L',stream.tell()))
			connection.flush()
			stream.seek(0)
			connection.write(stream.read())
			stream.seek(0)
			stream.truncate()
	connection.write(struct.pack('<L',0))

finally:
	connection.close()
	client_socket.close()

