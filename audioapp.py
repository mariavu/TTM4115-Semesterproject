import pyaudio
import wave
import time
import sys
import base64
import json

class auditiorecord():
    
    def __init__(self,name):
        self.name=name

    def record(self, seconds, filename):
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 1
        fs = 44100  # Record at 44100 samples per second

        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        print('Recording')

        stream = p.open(format=sample_format,
                        channels=channels,
                        rate=fs,
                        frames_per_buffer=chunk,
                        input=True, input_device_index=1)

        frames = []  # Initialize array to store frames

        # Store data in chunks for 3 seconds
        for i in range(0, int(fs / chunk * seconds)):
            data = stream.read(chunk)
            frames.append(data)

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the PortAudio interface
        p.terminate()

        print('Finished recording')

        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

class auditioplay():
    def __init__(self,name):
        self.name=name

    def play(self, filename):
        wf = wave.open(filename, 'rb') 
        p = pyaudio.PyAudio()

        # define callback (2)
        def callback(in_data, frame_count, time_info, status):
            data = wf.readframes(frame_count)
            return (data, pyaudio.paContinue)

        # open stream using callback (3)
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=callback)

        # start the stream (4)
        stream.start_stream()

        # wait for stream to finish (5)
        while stream.is_active():
            time.sleep(0.1)

        # stop stream (6)
        stream.stop_stream()
        stream.close()
        wf.close()

        # close PyAudio (7)
        p.terminate()

#p=auditiorecord("haha")
#p.record(2)
#p=auditioplay("haha")
#p.play()

audio = pyaudio.PyAudio()

info = audio.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')
for i in range(0, numdevices):
        if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
            print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))
            print(audio.get_device_info_by_host_api_device_index(0,i))
            #print(audio.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels'))
print("-------------------------------------------------------------")
