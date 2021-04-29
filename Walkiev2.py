import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
from appJar import gui
import base64
import time
#from register_login_gui import *
from pyspeech2 import auditioplay,speak,get_audio,record_p,voice_loop

from tkinter import *
from tkinter import messagebox, OptionMenu
from main_page_gui import home_screen
import os
import time

Walkie_ID=66
MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_RESPONSE='ttm4115/team_5/semesterprosjekt/walkie/66'
#MQTT_SERVER='ttm4115/team_5/semesterprosjekt/local_server/1/res'
MQTT_SERVER='ttm4115/team_5/semesterprosjekt/walkie/66'

filename="mic_recording.wav" #file to send
output_file="output_walkie.wav"
channelvar=0
class Voice_component:
    """
    The component to send voice commands.
    """

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
           
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        print(payload.get('command'))
        if(payload.get('command')=="new_voice_message"):
            chunk = payload.get('Payload')
            decoded = base64.b64decode(chunk)
            fout=open(output_file,"wb")
            fout.write(decoded)
            print("new message")
            self.p.play("1out.wav", 4)

        elif(payload.get('command')=="new_text"):
            print(payload.get('Payload'))
        elif(payload.get('command')=="new_registration"):
            
            Label(screen1, text="Registration successfull", fg = "green", font = ("calibri", 11)).pack()
            



    def __init__(self):
        # get the logger object for the component
        
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        #self._logger.info('Starting Component')
        
        self.p=auditioplay("haha")
        # create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.subscribe(MQTT_RESPONSE)
        self.mqtt_client.loop_start()
        
    def guirun(self):
        #channelvar=0
        def publish_command(command):
            payload = json.dumps(command)
            self.mqtt_client.publish(MQTT_SERVER, payload=payload, qos=2)

        def emergency_button_click():
            fo=open("mic_results.wav","rb")
            chunk=fo.read()
            encoded = base64.b64encode(chunk)
            command = {"command": "emergency","Walkie_ID":Walkie_ID, "Payload": encoded.decode('ascii'),'Length':str(len(chunk))}
            publish_command(command)
            Label(Toplevel(home), text="Message sent", fg = "green", font = ("calibri", 11)).pack()
       
        def check_button_click():
            fo=open("mic_results.wav","rb")
            chunk=fo.read()
            encoded = base64.b64encode(chunk)
            command = {"command": "New_message","Walkie_ID":Walkie_ID,"channel":channelvar, "Payload": encoded.decode('ascii'),'Length':str(len(chunk))}
            print(command["channel"])
            publish_command(command)
            Label(Toplevel(home), text="Message sent", fg = "green", font = ("calibri", 11)).pack()

        def emergency():
            emergency_screen = Toplevel(home)
            emergency_screen.title("Emergency") 
            emergency_screen.geometry("300x250")
            emergency_screen.grab_set()

            Label(emergency_screen, text="EMERGENCY", bg = "red", width="300", height="2", font= ("Calibri", 20)).pack()
            Button(emergency_screen, text="Press to send", width="10", height="1", command=emergency_button_click).pack()
            
        
        def send_message():
            recording_screen = Toplevel(channels_screen)
            recording_screen.title("Record message")
            recording_screen.geometry("300x250")
            recording_screen.grab_set()
            

            Label(recording_screen, text="Record message", bg = "dodger blue", width="300", height="2", font= ("Calibri", 15)).pack()
            Button(recording_screen, text="Press to send", width="10", height="1", command=check_button_click).pack()
        
        def btn1(value):
            global channelvar
            channelvar=value
            print("btn1")
     
        def choose_channel():
            global channels_screen
            list1 = ["1", "2", "3"]
            channels_screen = Toplevel(home)
            channels_screen.title("Choose channel") 
            channels_screen.geometry("300x250")
            channels_screen.grab_set()
            for item in list1:

               Button(channels_screen, text=item, width="10", height="2", command=lambda:[send_message(),btn1(list1.index(item))]).pack()
            
       
        def list_channel():
            list1 = ["1", "2", "3"]
            global list_screen
            global new_channel
            list_screen = Toplevel(home)
            list_screen.title("Add new channel")
            list_screen.geometry("300x250")
            list_screen.grab_set()

            for item in list1:
                Button(list_screen, text=item, width="10", height="2").pack()
                new_channel = item


        def home_screen():
            global home
            home = Tk()
            home.geometry("300x250")
            home.title("Home page")
            home.grab_set()

            Label(home, text="Choose an action", bg = "dodger blue", width="300", height="2", font= ("Calibri", 13)).pack()
            Label(home, text = "").pack()
            Button(home, text="Emergency", bg="red", fg="white", width = "10", height = "1", command = emergency).pack()
            Label(home, text = "").pack()
            Button(home, text="Record a message", width = "10", height = "1", command = choose_channel).pack()
            Label(home, text = "").pack()
            Button(home, text = "Channel list", width = "10", height = "1", command = list_channel).pack()

        def register_user():
            full_name_info = full_name.get()
            role_info = role.get()
            username_info = username.get()
            password_info = password.get()
            password2_info = password2.get()

            if full_name_info == "" or username_info == "" or role_info == "Select a role":
                messagebox.showinfo('Walkie','Please fill out the required fields')
            
            elif password_info != password2_info:
                messagebox.showinfo('Walkie','Passwords did not match')

            else:
                file = open(username_info, "w")
                file.write(full_name_info+"\n")
                file.write(role_info+"\n")
                file.write(username_info+"\n")
                file.write(password_info+"\n")
                file.close
                command = {"command": 'new_registration', "walkie": Walkie_ID, "username": username_info, "password": password_info, "role": role_info}
                publish_command(command)
                full_name_entry.delete(0, END)
                username_entry.delete(0, END)
                password_entry.delete(0, END)
                password2_entry.delete(0, END)
            

        def register():
            global screen1
            screen1 = Toplevel(screen)
            screen1.title("Register") 
            screen1.geometry("300x400")
            screen1.grab_set()

            global full_name
            global role
            global username
            global password
            global password2
            global full_name_entry
            global username_entry
            global password_entry
            global password2_entry

            full_name = StringVar()
            role = StringVar(screen1)
            username = StringVar()
            password = StringVar()
            password2 = StringVar()

            # enter full name
            Label(screen1, text="Please enter details below").pack()
            Label(screen1, text="").pack()
            Label(screen1, text="Full Name * ").pack()
            full_name_entry = Entry(screen1, textvariable=full_name)
            full_name_entry.pack()

            # choose role
            Label(screen1, text="").pack()
            roles = ["Select a role","doctor", "nurse"]
            role.set(roles[0])
            Label(screen1, text="Choose role * ").pack()
            OptionMenu(screen1, role, *roles).pack()
            Label(screen1, text="").pack()

            # enter username
            Label(screen1, text="Username * ").pack()
            username_entry = Entry(screen1, textvariable=username)
            username_entry.pack()

            # enter password
            Label(screen1, text="Password * ").pack()
            password_entry = Entry(screen1, textvariable=password, show="*")
            password_entry.pack()

            # repeat password
            Label(screen1, text="Reapeat Password * ").pack()
            password2_entry = Entry(screen1, textvariable=password2, show="*")
            password2_entry.pack()

            Label(screen1, text="").pack()
            Button(screen1, text= "Register", width="10", height="1", command=register_user).pack()


        def login_verify():
            username1 = username_verify.get()
            password1 = password_verify.get()

            username_entry1.delete(0, END)
            password_entry1.delete(0, END)

            list_of_files = os.listdir()
            if username1 in list_of_files:
                file = open(username1, "r")
                verify = file.read().splitlines()

                if password1 in verify:
                    #print("Login successfull!")
                   screen2.destroy()
                   time.sleep(1)
                   home_screen()   
                    

                else:
                    #print("Password is not found")
                    messagebox.showinfo('Walkie','Invalid username or password')
            
            else:
                #print("User not found")
                messagebox.showinfo('Walkie','Invalid username or password')


            
        def login():
            global screen2
            screen2 = Toplevel(screen)
            screen2.title("Login") 
            screen2.geometry("300x250")
            screen2.grab_set()

            global username_verify
            global password_verify
            global username_entry1
            global password_entry1

            username_verify = StringVar()
            password_verify = StringVar()

            # enter username
            Label(screen2, text="Username * ").pack()
            username_entry1 = Entry(screen2, textvariable=username_verify)
            username_entry1.pack()

            # enter password
            Label(screen2, text="Password * ").pack()
            password_entry1 = Entry(screen2, textvariable=password_verify, show="*")
            password_entry1.pack()

            Label(screen2, text="").pack()
            Button(screen2, text= "Log in", width="10", height="1", command=login_verify).pack()


        def main_screen():
            global screen
            screen = Tk()
            screen.geometry("300x250")
            screen.title("Welcome")
            Label(screen, text="Welcome", bg = "dodger blue", width="300", height="2", font= ("Calibri", 13)).pack()
            Label(screen, text="").pack()
            Button(screen, text="Login", width = "10", height = "1", command = login).pack()
            Label(screen, text = "").pack()
            Button(screen, text = "Register", width = "10", height = "1", command = register).pack()

            screen.mainloop()

        main_screen()

    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()


# logging.DEBUG: Most fine-grained logging, printing everything
# logging.INFO:  Only the most important informational log items
# logging.WARN:  Show only warnings and errors.
# logging.ERROR: Show only error messages.
debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = Voice_component()
Thread(target=t.guirun).start()

def a():
    while(1):
        dat=voice_loop()
        if(dat[1]==1 and dat[0]!="channel_0"):
            fo=open("mic_results.wav","rb")
            chunk=fo.read()
            encoded = base64.b64encode(chunk)
            command = {"command": "new_voice_message", "to_channel":dat[0], "Payload": encoded.decode('ascii'),'Length':str(len(chunk))}
            payload = json.dumps(command)
            t.mqtt_client.publish(MQTT_SERVER, payload=payload, qos=2)
            speak("ok it is sent")
    
Thread(target=a).start()

