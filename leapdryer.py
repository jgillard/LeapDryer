import sys, os, inspect, thread, time

# find Windows/Unix libraries
if os.name == "nt":
    src_dir = sys.path[0]
    arch_dir = "/lib/x64" if sys.maxsize > 2**32 else "lib/x86"
    sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
else:
    src_dir = "/Users/James/Dropbox/ES410 Group Project/LeapDryer"
    lib_dir = os.path.abspath(os.path.join(src_dir, "lib/osx"))
    sys.path.insert(0, lib_dir)

from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

# initialise Arduino serial connection
import serial
s = serial.Serial('/dev/tty.usbmodemfd121', 9600)
time.sleep(2)
s.write('0\n')


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
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" \
            % (frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

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
            print "  pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
                roll, pitch, yaw)            

            # Value Smoothing
            # Average a finger position for the last 10 frames
            # currently supports 1 hand only
            count = 0
            averageP = 0.0
            averageR = 0.0
            averageY = 0.0
            for i in range(0,10):
                hand_from_frame = controller.frame(i).hand(hand.id)
                if(hand_from_frame.is_valid):
                    averageP = averageP + hand_from_frame.direction.pitch
                    averageR = averageR + hand_from_frame.palm_normal.roll
                    averageY = averageY + hand_from_frame.direction.yaw
                    count += 1
            averageP = averageP* Leap.RAD_TO_DEG / count
            averageR = averageR * Leap.RAD_TO_DEG / count
            averageY = averageY Leap.RAD_TO_DEG / count
            print "  Av. pitch: %f degrees, Av. roll: %f degrees, Av. yaw: %f degrees" % (
                averageP, averageR , averageY)

            # send data to over serial port
            payload = str(int(averageY  + 80))
            print payload
            s.write(payload)
            s.write('\n')
            # print s.readline()

        # if no hands detected
        if not (frame.hands.is_empty and frame.gestures().is_empty):
            print "where da hands man?"
        

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

if __name__ == "__main__":
    main()