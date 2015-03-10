from serial.tools import list_ports
from time import sleep
import serial
from twitter import *

# def twitAuth():
#     t = Twitter(
#         auth = OAuth('2261857933-6osWHs9QAdpl69yMHLCSpNcty2voBhA1uaEcwue', 
#             '96ue1lqn9uetCeISQZKtA1ahsODU1tU7VZ8o4xGzWZlYm',
#             '9VtsP5VUEuWOgQ4wkiXQ',
#             '3x7IyiJqdqPfS1T17xg41eASz0LMZgQFnSoMnUBnUk')
#         )
#     return t

# def getDM(t):
#     msg = t.direct_messages(count=1)
#     return msg[0]['text']


def findPort():

    port = [s for s in zip(*list_ports.comports())[0] if 'usbmodem' in s]

    if not port:
        print "Arduino not detected"
        return 0
    else:
        s = serial.Serial(port[0], 9600)
        sleep(1)
        s.write('110\n')
        return s


def main():

    s = findPort()

    # t = twitAuth()
    # while True:
    #     msg = getDM(t);
    #     if(msg.lower() =="louder"):
    #         s.write("130")
    #         s.write('\n')
    #     elif(msg.lower() =="shut up"):
    #         s.write("80")
    #         s.write('\n')
    #     sleep(60)
    
    while True:
        degrees = raw_input("Enter degree value: ")
        s.write(degrees)
        s.write('\n')

if __name__ == "__main__":
    main()
