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
        reset = "%0.d,%0.d" % (100, 50)
        s.write(reset)
        s.write('\n')
        sleep(1)
        return s


def leapCode(controller, frame):
    # Process hand(s)
    handlist = frame.hands
    for hand in handlist:

        handType = 0 if hand.is_left else 1
        normal = hand.palm_normal
        direction = hand.direction
        pitch = direction.pitch * Leap.RAD_TO_DEG
        roll = normal.roll * Leap.RAD_TO_DEG
        yaw = direction.yaw * Leap.RAD_TO_DEG

        # Value Smoothing - average over the last frameDiff frames
        count = 0
        avP = 0.0
        avR = 0.0
        avYw = 0.0
        avX = 0.0
        avY = 0.0
        avZ = 0.0

        global prevFrame
        frameDiff = frame.id - prevFrame
        for i in range(0, frameDiff):
            hand_from_frame = controller.frame(i).hand(hand.id)
            if(hand_from_frame.is_valid):
                avR = avR + hand_from_frame.palm_normal.roll
                avP = avP + hand_from_frame.direction.pitch
                avYw = avYw + hand_from_frame.direction.yaw
                avX = avX + hand.palm_position[0]
                avY = avY + hand.palm_position[2]
                avZ = avZ + hand.palm_position[1]
                count += 1
        avR = avR * Leap.RAD_TO_DEG / count
        avP = avP * Leap.RAD_TO_DEG / count
        avYw = avYw * Leap.RAD_TO_DEG / count
        avX = avX / count
        avY = avY / count
        avZ = avZ / count

        if debug:
            print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % \
                (frame.id, frame.timestamp,
                 len(frame.hands), len(frame.fingers))
            print "handType: %s, id %d, position: %s" % (
                handType, hand.id, hand.palm_position)
            print "  Roll: %f *, Pitch: %f *, Yaw: %f *" % (
                roll, pitch, yaw)
            print "  Av R: %f *, Av P: %f *, Av Y: %f *" % (
                avR, avP, avYw)
            print "  Av X: %f *, Av Y: %f *, Av Z: %f *" % (
                avX, avY, avZ)


        if len(handlist) == 1:
            prevFrame = frame.id
        elif len(handlist) == 2 and hand.id == handlist[1].id:
            prevFrame = frame.id

        if arduino:
            nozzleMaxMin = [110, 96]
            motorMaxMin = [75, 25]
            nozzleVal = 0.0875*avZ + 92.5
            motorVal = -0.3438*avZ + 88.75

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
            return
        leapCode(controller, frame)


s = getArduinoPort()
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="show print statements",
                    type=int, default=0)
args = parser.parse_args()
debug = args.debug
prevFrame = 0
arduino = True if raw_input("ArduiYes or ArduiNo? ").lower() == "yes" else False


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
        # Remove the listener when done
        controller.remove_listener(listener)
        p.terminate()

if __name__ == "__main__":
    main()
