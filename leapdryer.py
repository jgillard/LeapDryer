import sys
import os
import pyaudio
import threading
import time
from pysoundrecord import processData
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


def audioStopStart(s):
    s.stop_stream()
    s.close()
    s = startRecord()
    t = time.clock()
    return s, t
# END COPIED FROM PYSOUNDRECORD


def audioCode(audio, stream, t0):
    # check recording started and > 0.1 s of audio
    if (stream.is_stopped() == False
            and (time.clock() - t0) > 0.05):
        # print audio XXX
        # restart stream and start clock
        stream, t0 = audioStopStart(stream)
        # start processing thread
        t = threading.Thread(target=processData,
                             args=(audio, rms))
        t.start()
        return audio, stream, t0, 0
    else:
        # return if not recording or audio segment < 0.1 s
        # print "Skipping frame", "\t", "isStopped:", \
        #     stream.is_stopped(), "\t", time.clock() - t0
        skip = 1
        return audio, stream, t0, skip


stream = startRecord()


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

        # BEGIN AUDIO CODE
        audio, stream, t0, skip = audioCode(audio, stream, t0)
        if skip:
            return
        # END AUDIO CODE

        # Report some basic frame information
        frame = controller.frame()
        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d" \
            % (frame.id, frame.timestamp, len(frame.hands), len(frame.fingers))

        # Process hand(s)
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"
            print "  %s, id %d, position: %s" % (
                handType, hand.id, hand.palm_position)

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

            # Calculate the hand's pitch, roll, and yaw angles
            pitch = direction.pitch * Leap.RAD_TO_DEG
            roll = normal.roll * Leap.RAD_TO_DEG
            yaw = direction.yaw * Leap.RAD_TO_DEG
            print "  Pitch: %f *, Roll: %f *, Yaw: %f *" % (
                roll, pitch, yaw)

            # Value Smoothing
            # Average a finger position for the last 10 frames
            # currently supports 1 hand only
            count = 0
            averageP = 0.0
            averageR = 0.0
            averageY = 0.0
            for i in range(0, 10):
                hand_from_frame = controller.frame(i).hand(hand.id)
                if(hand_from_frame.is_valid):
                    averageP = averageP + hand_from_frame.direction.pitch
                    averageR = averageR + hand_from_frame.palm_normal.roll
                    averageY = averageY + hand_from_frame.direction.yaw
                    count += 1
            averageP = averageP * Leap.RAD_TO_DEG / count
            averageR = averageR * Leap.RAD_TO_DEG / count
            averageY = averageY * Leap.RAD_TO_DEG / count
            print "  Av P: %f *, Av R: %f *, Av Y: %f *" % (
                averageP, averageR, averageY)

            # send data to over serial port
            if s != 0:
                payload = str(int(averageY + 80))
                print payload
                s.write(payload)
                s.write('\n')
                # print s.readline()

            # if no hands detected
            # if (frame.hands.is_empty):


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
