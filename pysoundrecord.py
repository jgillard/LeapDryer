"""
Record Loop Speed Test
Currently got 6-7 Hz loop
"""

import pyaudio, audioop, time, math

t1 = []
audio = []
rms = []
repeats = 10
recordReady = 1

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

def stopRecord(stream):
	stream.stop_stream()
	stream.close()

def newFrame(s):
	recordReady = 0
	t1.append(time.time())
	stopRecord(s)
	# finds index of previous 'newFrame'
	try:
		frameStart = (len(audio) - 1) - audio[::-1].index('newFrame')
	except ValueError:
		if len(audio) < 100:
			frameStart = 0
		else: 
			print "Error finding 'newFrame'"
	# add new marker
	audio.append('newFrame')
	frameEnd = len(audio)-1
	print 'Frame:', frameStart, frameEnd
	# make sure there is sufficient data (problem with 1st frame)
	if frameEnd > 1:
		# extract audio chunk and rms()
		frameAudio = ''.join(audio[frameStart:frameEnd])
		rms.append(audioop.rms(frameAudio, 2))
	#restart recording
	s = startRecord()
	recordReady = 1
	return s
		
# MAIN PROGRAM
def main():
	print "Starting"
	t0 = time.time()
	stream = startRecord()
	#simulate newFrame() function calls
	for i in range (1, repeats + 1):
		time.sleep(1)
		stream = newFrame(stream)
	print "Finished"
	p.terminate()
	# normalise loop times
	t2 = [t-t0 for t in t1]
	print t2
	print 'Av. loop time:', (t2[len(t2)-1] - repeats)/repeats
	print 'RMS values:', rms
	print 'Current FPS:', math.trunc(1/((t2[len(t2)-1] - repeats)/repeats)), 'Hz'

if __name__ == "__main__":
    main()