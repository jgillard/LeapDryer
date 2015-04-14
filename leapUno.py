# line_profiler: kernprof -l -v leapdryer.py

import sys
import os
import serial
from time import clock, sleep
import argparse
import datetime
from serial.tools import list_ports

# find Windows/Unix Leap libraries
src_dir = os.getcwd()
if os.name == "nt":
    arch_dir = "/lib/x64" if sys.maxsize > 2 ** 32 else "lib/x86"
    sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
else:
    lib_dir = os.path.abspath(os.path.join(src_dir, "lib/osx"))
    sys.path.insert(0, lib_dir)
import Leap


def getArduinoPort():
    port = [s for s in zip(*list_ports.comports())[0] if 'usbmodem' in s]
    if not port:
        print "Arduino not detected"
        return 0
    else:
        s = serial.Serial(port[0], 115200)
        reset = "%0.d,%0.d" % (90, 50)
        s.write(reset)
        s.write('\n')
        sleep(1)
        return s


def leapCode(controller, frame):
    # Process hand(s)
    handlist = frame.hands
    # z = []
    # if len(handlist) != 1:
    #     for hand in handlist:
    #         z.append(hand.palm_position[1])
    #     if z[0] >= z[1]:
    #         handlist = handlist[1]
    #     else:
    #         handlist = handlist[0]
    # else:
    #     hand = handlist[0]

    z = 0
    avgZ = 0
    if len(handlist) != 1:
        for hand in handlist:
            print int(hand.palm_position[1])
            z += int(hand.palm_position[1])
        avgZ = z/2
    else:
        avgZ = int(handlist[0].palm_position[1])
        payload = "%0.d,%0.d" % (92, 92)
        s.write(payload)
        s.write('\n')

    handslost = 0

    if avgZ != 0:

        if arduino:
            nozzleMaxMin = [110, 80]
            motorMaxMin = [90, 1]
            nozzleVal = 0.21*avgZ + 63
            motorVal = -0.6*avgZ + 120

            if nozzleVal > nozzleMaxMin[0]:
                nozzleVal = nozzleMaxMin[0]
            elif nozzleVal < nozzleMaxMin[1]:
                nozzleVal = nozzleMaxMin[1]
            if motorVal > motorMaxMin[0]:
                motorVal = motorMaxMin[0]
            elif motorVal < motorMaxMin[1]:
                motorVal = motorMaxMin[1]

            # send data to over serial port
            if s != 0:
                # payload = str(nozzleVal) + ',' + str(motorVal)
                payload = "%0.d,%0.d" % (nozzleVal, motorVal)
                print payload
                s.write(payload)
                s.write('\n')
                # print s.readline()


class Listener(Leap.Listener):

    def on_init(self, controller):
        print "Leap Listener Initialized"

    def on_connect(self, controller):
        print "Leap Motion Connected"

    def on_disconnect(self, controller):
        print "Leap Motion Disconnected"

    def on_exit(self, controller):
        print "Leap Listener Exited"

    def on_frame(self, controller):
        # Get the most recent frame and return if no hands detected
        frame = controller.frame()
        if frame.hands.is_empty:
            if handslost == 1:
                payload = "%0.d,%0.d" % (90, 90)
                s.write(payload)
                s.write('\n')
                handlost = 0
        leapCode(controller, frame)


s = getArduinoPort()
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="show print statements",
                    type=int, default=0)
args = parser.parse_args()
debug = args.debug
prevFrame = 0
arduino = True if raw_input("ArduiYes or ArduiNo? ").lower() == "yes" else False
handslost = 1


def main():

    # Create a listener and controller
    listener = Listener()
    controller = Leap.Controller()

    # Have the listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        payload = "%0.d,%0.d" % (91, 91)
        print payload
        s.write(payload)
        s.write('\n')
        # Remove the listener when done
        controller.remove_listener(listener)
        p.terminate()

if __name__ == "__main__":
    main()
