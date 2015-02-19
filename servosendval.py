import serial
from time import sleep
s = serial.Serial('/dev/tty.usbmodemfa131', 9600)
sleep(2)
s.write('0\n')

while True: 
	degrees = raw_input("Gimmee numberz: ")
	s.write(degrees)
	s.write('\n')