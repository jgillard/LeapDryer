from serial.tools import list_ports
from time import sleep 
import serial

port = [s for s in zip(*list_ports.comports())[0] if 'iPhone' in s]

if not port:
	print "Arduino not detected"
else:
	s  = serial.Serial(port[0], 9600)

sleep(2)
s.write('0\n')

while True: 
	degrees = raw_input("Enter degree value: ")
	s.write(degrees)
	s.write('\n')