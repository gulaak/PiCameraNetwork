
from cameraSocket import Camera

camera = Camera('134.88.49.135',10001)

try:
	while True:
		camera.get_frame()

finally:
	camera.closeConnection()


