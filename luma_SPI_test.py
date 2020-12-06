#Matrix libraries
#Para correr utilizar sudo python3 luma_SPI_test.py
from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi,noop
from luma.core.render import canvas
#sudo pip3 install keyboard
import keyboard
import time
global puntox
global puntoy
puntox=3
puntoy=3


def key_press(key):
	global puntox
	global puntoy
	#print(key.name)
	if key.name == 'left' and puntox != 7:
		puntox+=1
	if key.name == 'right' and puntox != 0:
		puntox-=1
	if key.name == 'up' and puntoy != 7:
		puntoy+=1
	if key.name == 'down' and puntoy != 0:
		puntoy-=1
	print((puntox,puntoy))



def main():
	global puntox
	global puntoy
	matrix = Matrix()
	keyboard.on_press(key_press)
	while 1:
		matrix.draw_point(puntox,puntoy)

class Matrix(object):
	def __init__(self):
		super(Matrix,self).__init__()
		self.device=self.create_matrix_device(1,0,0)
	def create_matrix_device(self,n,block_orientation,rotate):
		#Create matrix device
		print("Creating device...")
		serial=spi(port=0,device=0,gpio=noop())
		device=max7219(serial,cascaded=n,block_orientation=block_orientation,rotate=rotate)
		print("Device created.")
		return device
	def draw_point(self,x,y):
		with canvas(self.device) as draw:
			draw.point((x,y),fill="green")
if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass

