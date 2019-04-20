from flask import Flask,render_template,Response
from flask import request
import json
from camera import Camera
import socket
import struct
import io
import time
import random
app = Flask(__name__)

selector = 0

fps =None
res = None
brightness = None
settingChange = False





@app.route("/")
def hello():
    return render_template('home.html')
	
 
	
@app.route("/switch",methods = ['POST'])
def videoFeedSwitch():
	global selector
	selector +=1
	
	if(selector > 2):
		selector = 0
	print(selector)
	return json.dumps("OK")
	
@app.route("/api",methods=['POST'])
def getSettings():
	global settingChange
	data = request.get_json()
	fps = data['fps']
	res = data['res']
	brightness = data['brightness']
	settingChange = True
	
	return json.dumps({'OK':200})
	
	
	
# def generatorTwo():
# 	while True:
		
# 		yield (b'--frame\r\n'
# 				   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def getImage(connection):
	image_len = struct.unpack('<L',connection.read(struct.calcsize('<L')))[0]

	return connection.read(image_len)
#	image_stream = io.BytesIO()
#	image_stream.write(connection.read(image_len))
#	image_stream.seek(0)
#	yield (b'--frame\r\n'
#			   b'Content-Type: image/jpeg\r\n\r\n' + image_stream.read() + b'\r\n')

def generator(camera):
	global settingChange
	clientOneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientTwoSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	clientThreeSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	clientFourSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	clientOneSocket.bind(('0.0.0.0',10000))
	clientTwoSocket.bind(('0.0.0.0',10001))
	clientThreeSocket.bind(('0.0.0.0',10002))
	clientFourSocket.bind(('0.0.0.0',10003))
	
	clientOneSocket.listen(2)
	clientTwoSocket.listen(2)
	clientThreeSocket.listen(2)
	clientFourSocket.listen(2)
	connectionOne = clientOneSocket.accept()[0].makefile('rb')
	connectionThree= clientThreeSocket.accept()[0]
	connectionTwo = clientTwoSocket.accept()[0].makefile('rb')
	connectionFour  = clientFourSocket.accept()[0]

	try:
		while True:
			if(selector == 1):
				frame = getImage(connectionTwo)

			elif(selector == 2):
				frame = getImage(connectionOne)

			else:
				frame = camera.get_frame()
				if(settingChange):
					camera.framerate = int(fps)
					temp = res.split('x')
					camera.resolution = (int(temp[0]),int(temp[1]))
					camera.brightness = int(brightness)

			if(settingChange):
				settingChange = False
				if(selector):
					connectionThree.send((fps + '-' + res + '-' + brightness).encode())
					
				else:
					connectionFour.sned((fps + '-' + res + '-' + brightness).encode())
					
			else:
				if(selector):
					connectionThree.send(b'1')
		
				elif(selector==2):
					connectionFour.send(b'1')
			
			yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
	finally:
		clientOneSocket.close()
		clientTwoSocket.close()
		connectionOne.close()
		connectionTwo.close()

# def generatorThree():
# 	server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
# 	server_socket.bind(('0.0.0.0',10001))
# 	connection = server_socket.accept()[0].makefile('rb')
# 	try:
# 		while True:
# 			yield(connection.read(4))
# 	except:
# 		server_socket.close()
# 		connection.close()




@app.route('/live_feed')
def live_feed():
    return Response(generator(Camera()),mimetype='multipart/x-mixed-replace; boundary=frame')
 

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True,threaded=True,use_reloader=False)
