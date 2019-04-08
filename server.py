from flask import Flask,render_template,Response
from celery import Celery
import socket
import struct
import io
import random
app = Flask(__name__)


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task
    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

app.config.update(
    CELERY_BROKER_URL='redis://localhost:6379',
    CELERY_RESULT_BACKEND='redis://localhost:6379'
)
celery = make_celery(app)






@app.route("/")
def hello():
    return render_template('home.html')


def generator():
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.bind(('0.0.0.0',10000))
	server_socket.listen(3)
	connection = server_socket.accept()[0].makefile('rb')
    
	try:
		while True:

			image_len = struct.unpack('<L',connection.read(struct.calcsize('<L')))[0]
			if not image_len:
				break
			image_stream = io.BytesIO()
			image_stream.write(connection.read(image_len))
			image_stream.seek(0)
			yield (b'--frame\r\n'
				   b'Content-Type: image/jpeg\r\n\r\n' + image_stream.read() + b'\r\n')
			
	finally:
		server_socket.close()
		connection.close()

def generatorTwo():
	print("generatorTwo")
	server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	server_socket.bind(('0.0.0.0',10001))
	connection = server_socket.accept()[0].makefile('rb')
	try:
		while True:
			yield(connection.read(4))
	except:
		server_socket.close()
		connection.close()


@app.route('/live_feed')
def live_feed():
    return Response(generator(),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/live_feedTwo')
def live_feedTwo():
	return Response(generatorTwo(), mimetype= 'multipart/x-mixed-replace; boundary =frame')



    
    

    

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True,threaded=True)
