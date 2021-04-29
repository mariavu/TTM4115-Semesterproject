import pyaudio
import speech_recognition as sr
import subprocess
import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()
    engine.stop()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone(device_index=1) as source:
        audio = r.listen(source)
        said = ""

        try:
            said = r.recognize_google(audio)
            print(said)
        except Exception as e:
            print("Exception: " + str(e))

    with open("mic_results.wav","wb") as f:
        f.write(audio.get_wav_data())

    return said.lower()

def record_p(text):
    text=text.lower()
    textlist=text.split()
    for word in textlist:
        if word =="channel" or word=="Channel":
            return textlist[textlist.index(word)+1]

    
WAKE="monkey"

def voice_loop():
        print("Listening")
        text = get_audio()
        if text.count(WAKE) > 0:
            speak("I am ready")
            text = get_audio()

            to_send = ["send to"]
            for phrase in to_send:
                if phrase in text:
                    a=record_p(text)
                    if a==None:
                        speak("I don't understand")  
                    else:
                        if(a=="one"):
                            a=1
                        speak("ok")
                        return str(a),1
        return "channel_0",0

#voice_loop()
