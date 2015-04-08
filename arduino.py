import serial

class Arduino(object):
	'''
    
	Class that handles acquiring the serial data 
	from the arduino for Data Acquisiton.
    
    Modified from Kevin Hughes at  https://github.com/kevinhughes27/arduinoDAQ
    by Juan Beiroa.

	'''

	def __init__(self, usbport, baud):
		self.ser = serial.Serial(
		port=usbport,
		baudrate=baud,
		bytesize=serial.EIGHTBITS,
		parity=serial.PARITY_NONE,
		stopbits=serial.STOPBITS_ONE,
		timeout=1,
		xonxoff=0,
		rtscts=0,
		interCharTimeout=None
		)

	#retrieve data from Arduino
	def poll(self):
		self.ser.flush() #flush before sending signal

		self.ser.write('w') #send signal telling Arduino to send data

		#read analog channels
		data = [float(self.ser.readline()[0:-2]) for i in range(0,1+1)]

		return data
