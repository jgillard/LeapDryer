from serial.tools import list_ports
from time import sleep 
import serial

def findPort():

	port = [s for s in zip(*list_ports.comports())[0] if 'usbmodem' in s]

	if not port:
		print "Arduino not detected"
		return 0
	else:
		s  = serial.Serial(port[0], 9600)
		sleep(1)
		s.write('0\n')
		return s

def main():

	s = findPort()
	while True: 
		degrees = raw_input("Enter degree value: ")
		s.write(degrees)
		s.write('\n')

if __name__ == "__main__":
    main()