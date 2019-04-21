from flask import Flask,render_template,Response
from flask import request
import json
from camera import Camera
import socket
import struct
import io
import cv2
import thread
import time
import random
app = Flask(__name__)




selector = 0

fps =None
res = None
brightness = None
frameTwo = None
frameThree = None
settingChange = False


def createSocketOne(): # thread for client one camera socket
	global frameTwo
	clientOneSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	clientOneSocket.bind(('0.0.0.0',10000))
	clientOneSocket.listen(0)
	connectionOne = clientOneSocket.accept()[0].makefile('rb')
	try:
		while True:
			frameTwo = getImage(connectionOne)
	finally:
		clientOneSocket.close()
		connectionOne.close()




def createSocketTwo(): # thread for client two camera socket
	global frameThree
	clientTwoSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	
	clientTwoSocket.bind(('0.0.0.0',10001))
	clientTwoSocket.listen(0)
	connectionTwo = clientTwoSocket.accept()[0].makefile('rb')
	try:
		while True:
			frameThree = getImage(connectionTwo)
	finally:
		clientTwoSocket.close()
		connectionTwo.close()



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
	
	
@app.route("/checkStatus",methods= ['GET'])
def getStatus():
	global selector 
	if not settingChange:
		response = {"status": settingChange , "fps":None, "resolution": None, "bright":None, 'selector': selector}
		return json.dumps(response)
	else:
		temp = res.split('x')
		response = {"status":settingChange, "fps": int(str(fps)), "resolution": (int(str(temp[0])),int(str(temp[1]))),"brightness": int(str(brightness)), 'selector': selector}
		return json.dumps(response)

@app.route("/changeStatus",methods=['POST'])
def changeStatus():
	global settingChange
	settingChange = False
	return json.dumps({"OK":200})
	
@app.route("/api",methods=['POST'])
def getSettings():
	global settingChange
	global fps
	global res
	global brightness
	data = request.get_json()
	fps = data['fps']
	
	res = data['res']
	
	brightness = data['brightness']
	
	settingChange = True

	
	return json.dumps({'OK':200})
	
	
	



def getImage(connection):
	image_len = struct.unpack('<L',connection.read(struct.calcsize('<L')))[0]

	return connection.read(image_len)


def generator(camera):
	global settingChange
	global fps
	global brightness
	global res

	while True:
		if(selector == 1):
			yield (b'--frame\r\n'
			   		b'Content-Type: image/jpeg\r\n\r\n' + frameTwo + b'\r\n')

		elif(selector == 2):
			yield (b'--frame\r\n'
			   		b'Content-Type: image/jpeg\r\n\r\n' + frameThree + b'\r\n')	

		else:
			yield (b'--frame\r\n'
			   		b'Content-Type: image/jpeg\r\n\r\n' + camera.get_frame() + b'\r\n')


@app.route('/live_feed')
def live_feed():
	return Response(generator(Camera()),mimetype='multipart/x-mixed-replace; boundary=frame')
 

if __name__ == '__main__':
	thread.start_new_thread(createSocketOne,())
	thread.start_new_thread(createSocketTwo, ())
	app.run(host='0.0.0.0',port=5000,debug=True,threaded=True,use_reloader=False)
