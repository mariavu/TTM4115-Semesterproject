import pyaudio
import wave
import time
import speech_recognition as sr
import subprocess
import pyttsx3
import contextlib
mic_file="fi/dover/mic_recording.wav"
class auditioplay():
    def __init__(self,name):
        self.name=name

    def play(self, filename, device_index):
        wf = wave.open(filename, 'rb') 
        p = pyaudio.PyAudio()
      
        # define callback (2)
        def callback(in_data, frame_count, time_info, status):
            data = wf.readframes(frame_count)
            return (data, pyaudio.paContinue)
        #print(str(p.get_format_from_width(wf.getsampwidth()))+"    "+str(wf.getnchannels())+"   "+str(wf.getframerate()))
        # open stream using callback (3)
        self.stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True,
                        stream_callback=callback,output_device_index=device_index)

        # start the stream (4)
        self.stream.start_stream()

        # wait for stream to finish (5)
        while self.stream.is_active():
            time.sleep(0.1)

        # stop stream (6)
        self.stream.stop_stream()
        self.stream.close()
        wf.close()

        # close PyAudio (7)
        p.terminate()
    

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def get_audio(store,device_ind):
    r = sr.Recognizer()
    with sr.Microphone(device_index=device_ind) as source:
        audio = r.listen(source)
        said = ""
        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))
    
    with open(mic_file,"wb") as f:
        f.write(audio.get_wav_data())

    return said.lower()

def record_p(text):
    text=text.lower()
    textlist=text.split()
    for word in textlist:
        if word =="channel" or word=="Channel":
            return textlist[textlist.index(word)+1]

def getduration():
    fname = mic_file
    with contextlib.closing(wave.open(fname,'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration

def voice_loop():
    a=''
    tet=0
    WAKE="monkey"
    print("Listening")
    text = get_audio(1,1)
    if text.count(WAKE) > 0:
        speak("I am ready")
        text = get_audio(1,1)
        to_send = ["send to"]
        for phrase in to_send:
            if phrase in text:
                a=record_p(text)
        text = get_audio(1,1)
        if "emergency" in text:
            tet=1
        if a==None:
            speak("I don't understand")
        else:
            if(a=="one"):
                a=1
            speak("ok")
            dur=getduration()
            return str(a),dur,tet
    return "channel_0",0,0