# line_profiler: kernprof -l -v leapdryer.py

import sys
import os
import serial
import pyaudio
import threading
from time import sleep, clock
import argparse
import audioop
import csv
import datetime
from serial.tools import list_ports
import requests

# find Windows/Unix Leap libraries
src_dir = os.getcwd()
if os.name == "nt":
    arch_dir = "/lib/x64" if sys.maxsize > 2 ** 32 else "lib/x86"
    sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
else:
    lib_dir = os.path.abspath(os.path.join(src_dir, "lib/osx"))
    sys.path.insert(0, lib_dir)
import Leap


# def getArduinoPort():
#     port = [s for s in zip(*list_ports.comports())[0] if 'usbmodem' in s]
#     if not port:
#         print "Arduino not detected"
#         return 0
#     else:
#         if (raw_input("ArduiYes or ArduiNo?").lower()) == "y":
#             s = serial.Serial(port[0], 9600)
#             sleep(1)
#             s.write('110\n')
#             return s
#         else:
#             return 0


def callback(in_data, frame_count, time_info, status):
    audio.append(in_data)
    return (in_data, pyaudio.paContinue)


def startRecord():
    if debug:
        print "Why does removing this hang the program?"
    stream = p.open(format=pyaudio.paInt8,
                    channels=1,
                    rate=44100,
                    input=True,
                    stream_callback=callback)
    stream.start_stream()
    return stream


def stopStream(s, x):
    s.stop_stream()
    s.close()


def audioStopStart(s):
    thrStop = threading.Thread(target=stopStream,
                               args=(s, 0))
    thrStop.daemon = True
    thrStop.start()
    s = startRecord()
    t = clock()
    return s, t


def processData(audio, rms):
    # finds index of previous 'newFrame'
    try:
        frameStart = (len(audio) - 1) - audio[::-1].index("newFrame")
    except ValueError:
        if len(audio) < 100:
            frameStart = 0
        else:
            print "Error finding 'newFrame'"
            frameStart = 0
    # add new marker
    audio.append("newFrame")
    frameEnd = len(audio) - 1
    # make sure there is sufficient data (problem with 1st frame)
    if frameEnd > 1:
        # extract audio chunk and rms()
        frameAudio = ''.join(audio[frameStart:frameEnd])
        rms.append(audioop.rms(frameAudio, 2))
        lock.acquire()
        print "\nAudio Chunk: ", frameStart, frameEnd
        print "RMS:", rms[-1]
        lock.release()
    return rms


def audioCode(audio, stream, t0):
    # check recording started and > 0.1 s of audio
    if (stream.is_stopped() == False and clock() - t0 > 0.005):
        # restart stream and start clock
        stream, t0 = audioStopStart(stream)
        # start processing thread
        t = threading.Thread(target=processData,
                             args=(audio, rms))
        t.daemon = True
        t.start()
        return audio, stream, t0, 0
    else:
        return audio, stream, t0, 1


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
            lock.acquire()
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
            lock.release()

        csvLine = [frame.id, frame.timestamp, len(frame.hands),
                   len(frame.fingers), handType, hand.id, avX, avY, avZ,
                   avR, avP, avYw, rms[-1]]
        csvData.append(csvLine)

        if len(handlist) == 1:
            prevFrame = frame.id
        elif len(handlist) == 2 and hand.id == handlist[1].id:
            prevFrame = frame.id

        # send data to over serial port
        # if s != 0:
        #     payload = str(int(avZ/10 + 110))
        #     print payload
        #     s.write(payload)
        #     s.write('\n')
        #     # print s.readline()

        if arduino:
            nozzleMaxMin = [110, 96]
            motorMaxMin = [75, 25]
            URL = "http://192.168.240.1/arduino/servo/"
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

            URL += "%.0f/%.0f" % (nozzleVal, motorVal)
            if debug:
                print URL
            requests.post(URL)


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
        global audio, stream, t0
        # Get the most recent frame and return if no hands detected
        frame = controller.frame()
        if frame.hands.is_empty:
            return
        # AUDIO
        audio, stream, t0, skip = audioCode(audio, stream, t0)
        if skip:
            return
        # LEAP
        leapCode(controller, frame)


# s = getArduinoPort()
audio = []
rms = []
t0 = clock()
p = pyaudio.PyAudio()
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="show print statements",
                    type=int, default=0)
args = parser.parse_args()
debug = args.debug
lock = threading.Lock()
prevFrame = 0
csvData = []
arduino = True if raw_input("ArduiYes or ArduiNo? ").lower() == "yes" else False
stream = startRecord()


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
        # read in arff header data
        header = []
        with open('arffHeader.csv', 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                header.append(row)
        # write out header and data to csv
        fileName = datetime.datetime.now().strftime('%Y-%m-%d@%H-%M-%S')
        with open('%s/testData/%s.arff' % (src_dir, fileName), 'wb') as f:
            writer = csv.writer(f)
            writer.writerows(header)
            writer.writerows(csvData)
        print "Data written out"

        # Remove the listener when done
        controller.remove_listener(listener)
        p.terminate()

if __name__ == "__main__":
    main()
