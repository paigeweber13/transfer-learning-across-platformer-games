import cv2

CapLeft = 512
CapRight = 640
CapTop = 334
CapBottom = 366

ColorDepth = 3

CapDevice = 6

class screen_cap(object):
	def __init__(self):
		self.cap = cv2.VideoCapture(cv2.CAP_DSHOW + CapDevice)
		
	def get(self):
		_, frame = self.cap.read()
	
		frame = frame[CapTop:CapBottom, CapLeft:CapRight]
		
		return frame
		
	def __del__(self):
		# When everything done, release the capture
		self.cap.release()
	
	def size(self):
		return [CapBottom-CapTop, CapRight-CapLeft, ColorDepth]