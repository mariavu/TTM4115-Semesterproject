import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
from appJar import gui
import base64
import time
#from register_login_gui import *
from pyspeech2 import auditioplay,speak,get_audio,record_p,voice_loop,getduration

from tkinter import *
from tkinter import messagebox, OptionMenu
import os
import time
from uuid import uuid4

Walkie_ID="DeviceID2"
MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_RESPONSE='ttm4115/team_5/semesterprosjekt/walkie/DeviceID2'
MQTT_SERVER='ttm4115/team_5/semesterprosjekt/local_server/1/req'
#MQTT_SERVER='ttm4115/team_5/semesterprosjekt/walkie/66'

filename="mic_recording.wav" #file to send
output_file="output_walkie.wav"
channelvar=''
jchvar=''
loginver=0
emergency_id="CHANNEL-3"
list1 = []
incoming_queue={'emergency':[],'normal':[]}
playing=False

class Voice_component:
    """
    The component to send voice commands.
    """
    def __init__(self):
        # get the logger object for the component
        
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        #self._logger.info('Starting Component')
        self.token=''
        self.p=auditioplay("play audio")
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
        Thread(target=self.guirun).start()
        self.mqtt_client.loop_start()
    
    def speechloop(self):
        while(1):
            dat=voice_loop()
            if(dat[1]!=0 and dat[0]!="channel_0"):
                fo=open("mic_results.wav","rb")
                chunk=fo.read()
                encoded = base64.b64encode(chunk)
                command = {"command": 4, "channel":"CHANNEL-"+dat[0],'duration':dat[1],"emergency":0,'id':str(uuid4()),'token':self.token,"payload": encoded.decode('ascii')}
                payload = json.dumps(command)
                self.mqtt_client.publish(MQTT_SERVER, payload=payload, qos=2)
                speak("ok it is sent")
       

    def guirun(self,call_func=False):
        #channelvar=0
        def publish_command(command):
            payload = json.dumps(command)
            self.mqtt_client.publish(MQTT_SERVER, payload=payload, qos=2)

        def emergency_button_click():
            fo=open("mic_results.wav","rb")
            chunk=fo.read()
            encoded = base64.b64encode(chunk)
            dur=getduration()
            command = {"command": 4, "channel":emergency_id,'duration':dur,"emergency":1,'token':self.token,'id':str(uuid4()),"payload": encoded.decode('ascii')}
            publish_command(command)
            Label(emergency_screen, text="Message sent", fg = "green", font = ("calibri", 11)).pack()
       
        def check_button_click():
            fo=open("mic_results.wav","rb")
            chunk=fo.read()
            encoded = base64.b64encode(chunk)
            dur=getduration()
            command = {"command": 4, "channel":channelvar,'length':dur,"emergency":0,'token':self.token,'id':str(uuid4()),"payload": encoded.decode('ascii')}
            publish_command(command)
            Label(recording_screen, text="Message sent", fg = "green", font = ("calibri", 11)).pack()

        def emergency():
            global emergency_screen
            emergency_screen = Toplevel(home)
            emergency_screen.title("Emergency") 
            emergency_screen.geometry("300x250")
            emergency_screen.grab_set()

            Label(emergency_screen, text="EMERGENCY", bg = "red", width="300", height="2", font= ("Calibri", 20)).pack()
            Button(emergency_screen, text="Press to send", width="10", height="1", command=emergency_button_click).pack()
            
        
        def send_message():
            global recording_screen
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
            
            channels_screen = Toplevel(home)
            channels_screen.title("Choose channel") 
            channels_screen.geometry("300x250")
            channels_screen.grab_set()
            for i in range(len(list1)):
                Button(channels_screen, text=list1[i].get('name'), width="10", height="2", command=lambda j=i:[send_message(),btn1(list1[j].get('id'))]).pack()
            
       
        def list_channel():
            
            global list_screen
            global new_channel
            list_screen = Toplevel(home)
            list_screen.title("Add new channel")
            list_screen.geometry("300x250")
            list_screen.grab_set()
            print(list1)
            for item in list1:
                Button(list_screen, text=item.get('name'), width="10", height="2").pack()
                print(item)

        def join_channel():
            global join_screen
            join_screen = Toplevel(home)
            join_screen.title("Choose channel") 
            join_screen.geometry("300x250")
            join_screen.grab_set()
            for i in range(len(list1)):
                Button(join_screen, text=list1[i].get('name'), width="10", height="2", command=lambda j=i:[self.mqtt_client.publish(MQTT_SERVER, payload=json.dumps({"command": 3, "walkie": Walkie_ID, "channel": list1[j].get('id'),'token':self.token}), qos=2)]).pack()
    
        def leave_channel():
            global leave_screen
            leave_screen = Toplevel(home)
            leave_screen.title("Choose channel") 
            leave_screen.geometry("300x350")
            leave_screen.grab_set()
            for i in range(len(list1)):
                Button(leave_screen, text=list1[i].get('name'), width="10", height="2", command=lambda j=i:[self.mqtt_client.publish(MQTT_SERVER, payload=json.dumps({"command": 5, "walkie": Walkie_ID, "channel": list1[j].get('id'),'token':self.token}), qos=2)]).pack()
           
        def list_mess():
            global listm_screen
            listm_screen = Toplevel(home)
            listm_screen.title("Choose channel") 
            listm_screen.geometry("300x350")
            listm_screen.grab_set()
            self.mqtt_client.publish(MQTT_SERVER, payload=json.dumps({"command": 2, "channel": "CHANNEL-1",'token':self.token}), qos=2)
    
        def logout():
            self.mqtt_client.publish(MQTT_SERVER, payload=json.dumps({"command": 9,'token':self.token}), qos=2)
            home.destroy()
        def home_screen():
            global home
            home = Toplevel(screen)
            home.geometry("300x400")
            home.title("Home page")
            home.grab_set()

            Label(home, text="Choose an action", bg = "dodger blue", width="300", height="2", font= ("Calibri", 13)).pack()
            Label(home, text = "").pack()
            Button(home, text="Emergency", bg="red", fg="white", width = "10", height = "1", command = emergency).pack()
            Label(home, text = "").pack()
            Button(home, text="Record a message", width = "20", height = "1", command = choose_channel).pack()
            Label(home, text = "").pack()
            Button(home, text = "Channel list", width = "10", height = "1", command = list_channel).pack()
            Label(home, text = "").pack()
            Button(home, text = "Join channel", width = "10", height = "1", command = join_channel).pack()
            Label(home, text = "").pack()
            Button(home, text = "Leave channel", width = "10", height = "1", command = leave_channel).pack()
            Label(home, text = "").pack()
            Button(home, text = "list messages", width = "10", height = "1", command = list_mess).pack()
            Label(home, text = "").pack()
            Button(home, text = "log out", width = "10", height = "1", command = logout).pack()
            

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
                command = {"command": 1, "walkie": Walkie_ID, "username": username_info, "password": password_info,"name":full_name_info, "role": role_info}
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
            command = {"command": 0, "walkie": Walkie_ID, "username": username1, "password": password1}
            publish_command(command)
            
            
            """
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
            """

            
        def login():
            global screen2
            screen2 = Toplevel(screen)
            screen2.title("Login") 
            screen2.geometry("300x350")
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
            screen.geometry("300x350")
            screen.title("Welcome")
            Label(screen, text="Welcome", bg = "dodger blue", width="300", height="2", font= ("Calibri", 13)).pack()
            Label(screen, text="").pack()
            Button(screen, text="Login", width = "10", height = "1", command = login).pack()
            Label(screen, text = "").pack()
            Button(screen, text = "Register", width = "10", height = "1", command = register).pack()

            screen.mainloop()
        if(call_func==True):
            return home_screen()
        else:
            main_screen()

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            #print(payload)   
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        
        if(payload.get('command')==7 or payload.get('command')==6 ):
            chunk = payload.get('payload')
            decoded = base64.b64decode(chunk)
            fout=open(output_file,"wb")
            fout.write(decoded)
            print("new message")
            self.p.play(output_file, 4)
        elif(payload.get('command')==1 and payload.get('status')==200):  
            Label(screen1, text="Registration successfull", fg = "green", font = ("calibri", 11)).pack()
        elif(payload.get('command')==1 and payload.get('error')!=200):
            Label(screen1, text="Registration unsuccessfull corde"+str(payload.get('error')), fg = "red", font = ("calibri", 11)).pack()
        elif(payload.get("command") == 0 and payload.get('token')):
            self.token=payload.get('token')
            self.mqtt_client.publish(MQTT_SERVER, payload=json.dumps({"command": 8,'token':self.token}), qos=2) 
            Thread(target=self.speechloop).start()
            screen2.destroy()
            time.sleep(1)
            t.guirun(True)
        elif(payload.get('command')==3 and payload.get('error')!=None):
            Label(join_screen, text="error "+payload.get('error'), fg = "blue", font = ("calibri", 11)).pack()
        elif(payload.get('command')==3 and payload.get('error')==None):
            Label(join_screen, text="joined "+payload.get('channel'), fg = "blue", font = ("calibri", 11)).pack()
        elif(payload.get('command')==5):
            Label(leave_screen, text="left "+payload.get('channel'), fg = "blue", font = ("calibri", 11)).pack()
        elif(payload.get('command')==2):
            #{'channel': 'CHANNEL-1', 'messages': [{'id': 'MESSAGE-1', 'duration': 200, 'timestamp': '1619798001'}], 'command': 2}
            data=payload.get('messages')
            Label(listm_screen, text="press to get", fg = "green", font = ("calibri", 11)).pack()
            for i in range(len(data)):
               Button(listm_screen, text=data[i].get('id'), width="10", height="2", command=lambda j=i:[self.mqtt_client.publish(MQTT_SERVER, payload=json.dumps({"command": 6, "id": data[j].get('id'),'token':self.token}), qos=2)]).pack()
        elif(payload.get('command')==8):
            global list1
            list1=payload.get('channels')
            print(list1)
        



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

