# line_profiler: kernprof -l -v leapdryer.py

import sys
import os
import pyaudio
import threading
import time
import argparse
import audioop
import csv
import datetime
from servosendval import findPort as getArduinoPort

# find Windows/Unix Leap libraries
if os.name == "nt":
    src_dir = sys.path[0]
    arch_dir = "/lib/x64" if sys.maxsize > 2 ** 32 else "lib/x86"
    sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
else:
    src_dir = "/Users/James/Dropbox/ES410 Group Project/LeapDryer"
    lib_dir = os.path.abspath(os.path.join(src_dir, "lib/osx"))
    sys.path.insert(0, lib_dir)
import Leap

s = getArduinoPort()
audio = []
rms = []
t0 = time.clock()
p = pyaudio.PyAudio()
parser = argparse.ArgumentParser()
parser.add_argument("-d", "--debug", help="show print statements",
                    type=int, default=0)
args = parser.parse_args()
debug = args.debug
lock = threading.Lock()
prevFrame = 0
csvData = []


# BEGIN COPIED FROM PYSOUNDRECORD
def callback(in_data, frame_count, time_info, status):
    audio.append(in_data)
    return (in_data, pyaudio.paContinue)


def startRecord():
    stream = p.open(format=pyaudio.paInt16,
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
    t = time.clock()
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
# END COPIED FROM PYSOUNDRECORD


def audioCode(audio, stream, t0):
    # check recording started and > 0.1 s of audio
    if (stream.is_stopped() == False and time.clock() - t0 > 0.01):
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
    for hand in frame.hands:

        handType = "Left hand" if hand.is_left else "Right hand"
        normal = hand.palm_normal
        direction = hand.direction
        pitch = direction.pitch * Leap.RAD_TO_DEG
        roll = normal.roll * Leap.RAD_TO_DEG
        yaw = direction.yaw * Leap.RAD_TO_DEG

        # Value Smoothing
        # Average a finger position for the last 10 frames
        # currently supports 1 hand only
        count = 0
        averageP = 0.0
        averageR = 0.0
        averageY = 0.0

        global prevFrame
        frameDiff = frame.id - prevFrame
        for i in range(0, frameDiff):
            hand_from_frame = controller.frame(i).hand(hand.id)
            if(hand_from_frame.is_valid):
                averageP = averageP + hand_from_frame.direction.pitch
                averageR = averageR + hand_from_frame.palm_normal.roll
                averageY = averageY + hand_from_frame.direction.yaw
                count += 1
        averageP = averageP * Leap.RAD_TO_DEG / count
        averageR = averageR * Leap.RAD_TO_DEG / count
        averageY = averageY * Leap.RAD_TO_DEG / count

        if (debug):
            lock.acquire()
            print "frameDiff: %i" % frameDiff
            print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d" % \
                (frame.id, frame.timestamp,
                 len(frame.hands), len(frame.fingers))
            print "  %s, id %d, position: %s" % (
                handType, hand.id, hand.palm_position)
            print "  Pitch: %f *, Roll: %f *, Yaw: %f *" % (
                roll, pitch, yaw)
            print "  Av P: %f *, Av R: %f *, Av Y: %f *" % (
                averageP, averageR, averageY)
            lock.release()

        x = hand.palm_position[0]
        y = hand.palm_position[1]
        z = hand.palm_position[2]
        csvLine = [frame.id, frame.timestamp, len(frame.hands),
                   len(frame.fingers), handType, hand.id, x, y, z,
                   averageP, averageR, averageY]
        csvData.append(csvLine)

        prevFrame = frame.id
        # send data to over serial port
        if s != 0:
            payload = str(int(averageY + 80))
            print payload
            s.write(payload)
            s.write('\n')
            # print s.readline()


class Listener(Leap.Listener):

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

    def on_disconnect(self, controller):
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

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
        fileName = datetime.datetime.now().strftime('%Y-%m-%d@%H-%M-%S')
        headers = ["frame.id", "frame.timestamp", "len(frame.hands)",
                   "len(frame.fingers)", "handType", "hand.id",
                   "hand.palm_position", "averageP", "averageR", "averageY"]
        with open('%s.csv' % fileName, 'wb') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(csvData)
        # Remove the listener when done
        controller.remove_listener(listener)
        p.terminate()

if __name__ == "__main__":
    main()
