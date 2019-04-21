

from cameraSocket import Camera

camera = Camera("134.88.49.135",10000)
try:
	while True:
		camera.get_frame()
finally:
		camera.closeConnection()





