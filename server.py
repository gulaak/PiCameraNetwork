from flask import Flask,render_template,Response
from flask import request
from camera import Camera
import socket
import struct
import io
import time
import random
app = Flask(__name__)

selector = 0







@app.route("/")
def hello():
    return render_template('home.html')
	
	
@app.route("/switch",methods = ['POST'])
def videoFeedSwitch():
	global selector
	selector +=1
	
	if(selector > 1):
		selector = 0
	print(selector)
	return "OK"
	
	
def generatorTwo():
	while True:
		
		yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


def getImage(connection):
	image_len = struct.unpack('<L',connection.read(struct.calcsize('<L')))[0]

	return connection.read(image_len)
#	image_stream = io.BytesIO()
#	image_stream.write(connection.read(image_len))
#	image_stream.seek(0)
#	yield (b'--frame\r\n'
#			   b'Content-Type: image/jpeg\r\n\r\n' + image_stream.read() + b'\r\n')

def generator(camera):
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(('0.0.0.0',10000))
	server_socket.listen(0)
	connection = server_socket.accept()[0].makefile('rb')
	x = time.time()
	while True:
		if(selector):
			frame = getImage(connection)
		else:
			frame = camera.get_frame()
		yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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




@app.route('/live_feedTwo')
def live_feedTwo():
	return Response(generatorTwo(), mimetype= 'multipart/x-mixed-replace; boundary =frame')

@app.route('/live_feed')
def live_feed():
    return Response(generator(Camera()),mimetype='multipart/x-mixed-replace; boundary=frame')

    
    

    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True,threaded=True,use_reloader=False)
