"""
Currently got 6-7 Hz loop
"""

import pyaudio, audioop, time

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100

t1 = []
data = []

p = pyaudio.PyAudio()

def callback(in_data, frame_count, time_info, status):
	data.append(in_data)
	return (in_data, pyaudio.paContinue)

def startRecord():
	stream = p.open(format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            stream_callback=callback)

	stream.start_stream()
	print "Started"
	return stream

def stopRecord(stream):
	stream.stop_stream()
	stream.close()
	print "Stopped"
	

t0 = time.time()
s = startRecord()

# for i in range(1,6):
# 		time.sleep(2)
# 		t1.append(time.time())

time.sleep(5)

stopRecord(s)
t1.append(time.time())
print "FINISHED"

p.terminate()
# for i in range(len(t1)):
# 	t1[i] -= t0
# print t1
print t1[0] - t0 - 5

rms = []
data = ''.join(data)
rms.append(audioop.rms(data, 2))
print rms