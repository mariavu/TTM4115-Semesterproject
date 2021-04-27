import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
from appJar import gui
import base64
import time
from audioapp import auditiorecord, auditioplay

from pyspeech import speak,get_audio,record_p,voice_loop

from multiprocessing import Process

MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

MQTT_TOPIC_INPUT = 'ttm4115/team_5/channel_66'
MQTT_TOPIC_V2 = 'ttm4115/team_5/'

filename="mic_results.wav" #file to send
output_file="1out.wav"

WAKE="monkey"

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
        
        if(payload.get('command')=="new_voice_message"):
            chunk = payload.get('Payload')
            decoded = base64.b64decode(chunk)
            fout=open(output_file,"wb")
            fout.write(decoded)
            print("new message")
            self.p.play("1out.wav")

        elif(payload.get('command')=="new_text"):
            print(payload.get('Payload'))
    

    def __init__(self):
        # get the logger object for the component
        
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        #self._logger.info('Starting Component')
        self.r=auditiorecord("haha")
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
        self.mqtt_client.subscribe(MQTT_TOPIC_INPUT)
        self.mqtt_client.loop_start()
        
        
    

    def create_gui(self):
        self.app = gui()

        def extract_timer_name(label):
            label = label.lower()
            if 'spaghetti' in label: return 'spaghetti'
            
            return None

        def extract_duration_seconds(label):
            label = label.lower()
            if 'spaghetti' in label: return 600
        
            return None

        def publish_command(command):
            payload = json.dumps(command)
            #print(payload)
            #self._logger.info(command)
            self.mqtt_client.publish(MQTT_TOPIC_INPUT, payload=payload, qos=2)

        self.app.startLabelFrame('send latest recording')
        def on_button_pressed_start(title):
            name = extract_timer_name(title)
            fo=open("mic_results.wav","rb")
            chunk=fo.read()
            encoded = base64.b64encode(chunk)
            command = {"command": "new_voice_message", "name": name, "Payload": encoded.decode('ascii')}
            publish_command(command)
       
            

        self.app.addButton('send latest recording', on_button_pressed_start)
        
        self.app.stopLabelFrame()
        self.app.startLabelFrame('send text')
        def enterbtn(title):
            if(title=="Cancel"):
                self.app.stop()
            a=self.app.getEntry("userEnt")
            command = {"command": "new_text", "name": "text", "Payload": a}
            publish_command(command)
            
            
        self.app.addLabel("userLab", "enter", 0, 0)
        self.app.addEntry("userEnt",0,1)
        self.app.addButton('Submit', enterbtn)
        self.app.stopLabelFrame()

        self.app.go()


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
Thread(target=t.create_gui).start()

def a():
    while(1):
        dat=voice_loop()
        if(dat[1]==1 and dat[0]!="channel_0"):
            print(dat[0])
            fo=open("mic_results.wav","rb")
            chunk=fo.read()
            encoded = base64.b64encode(chunk)
            command = {"command": "new_voice_message", "name": "voice_test", "Payload": encoded.decode('ascii')}
            payload = json.dumps(command)
            print(MQTT_TOPIC_V2+dat[0])
            t.mqtt_client.publish(MQTT_TOPIC_V2+dat[0], payload=payload, qos=2)
            speak("ok it is sent")
    
Thread(target=a).start()

