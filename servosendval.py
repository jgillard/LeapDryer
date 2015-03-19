from serial.tools import list_ports
from time import sleep
import serial
from twitter import *
import string


# def twitAuth():
#     t = Twitter(
#         auth = OAuth('2261857933-6osWHs9QAdpl69yMHLCSpNcty2voBhA1uaEcwue',
#                      '96ue1lqn9uetCeISQZKtA1ahsODU1tU7VZ8o4xGzWZlYm',
#                      '9VtsP5VUEuWOgQ4wkiXQ',
#                      '3x7IyiJqdqPfS1T17xg41eASz0LMZgQFnSoMnUBnUk')
#     )
#     return t


# def getDM(t):
#     msg = t.direct_messages(count=1)
#     return msg[0]['text']


def findPort():

    ports = [s for s in zip(*list_ports.comports())[0] if 'usbmodem' in s]

    if not ports:
        print "Arduino not detected"
        print s
        return 0
    else:
        print "Found port: %s" % ports[0]
        port = string.replace(ports[0], "cu", "tty", 1)
        print "New port: %s" % port
        s = serial.Serial(port, 9600)
        sleep(1)
        return s


def main():

    s = findPort()

    # t = twitAuth()
    # while True:
    #     msg = getDM(t)
    #     if(msg.lower() == "louder"):
    #         s.write("130")
    #         s.write('\n')
    #     elif(msg.lower() == "shut up"):
    #         s.write("80")
    #         s.write('\n')
    #     sleep(5)

    while True:
        degrees = raw_input("Enter degree value: ")
        s.write(degrees)
        print "%s written" % degrees

if __name__ == "__main__":
    main()
