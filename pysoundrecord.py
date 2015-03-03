"""
Record Loop Speed Test
Currently got 6-7 Hz loop
"""

import pyaudio
import audioop
import time
import math
import threading

t1 = []
audio = []
rms = []
repeats = 10

p = pyaudio.PyAudio()


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


def processData(audio, rms):
    # finds index of previous 'newFrame'
    try:
        frameStart = (len(audio) - 1) - audio[::-1].index("newFrame")
    except ValueError:
        if len(audio) < 100:
            frameStart = 0
        else:
            print "Error finding 'newFrame'"
    # add new marker
    audio.append("newFrame")
    frameEnd = len(audio) - 1
    print "\nAudio Chunk: ", frameStart, frameEnd
    # make sure there is sufficient data (problem with 1st frame)
    if frameEnd > 1:
        # extract audio chunk and rms()
        frameAudio = ''.join(audio[frameStart:frameEnd])
        rms.append(audioop.rms(frameAudio, 2))
        print "RMS:", rms[-1]
    return rms


def main():
    print "Starting"
    t0 = time.time()
    s = startRecord()
    # simulate newFrame() function calls
    for i in range(1, repeats + 1):
        time.sleep(1)
        # next two lines may not be working
        s, t0 = audioStopStart(s)
        t = threading.Thread(target=processData, args=(audio, rms))
        t.start()
    print "Finished"
    p.terminate()
    # normalise loop times
    if 't2' in locals() or 't2' in globals():
        t2 = [t - t0 for t in t1]
        print t2
        print "Av. loop time:", (t2[len(t2) - 1] - repeats) / repeats
        print "RMS values:", rms
        print "Rate:", math.trunc(1 / ((t2[len(t2) - 1] - repeats) / repeats)), "Hz"
    else:
        "Timer not working"
if __name__ == "__main__":
    main()
