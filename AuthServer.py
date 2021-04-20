import stmpy
import sys
import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json

# TODO: choose proper MQTT broker address
MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

# TODO: choose proper topics for communication
MQTT_TOPIC_INPUT = 'ttm4115/team_5/autentication/requests'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_5/autentication/responses'

class AutenticationServer:
    self.registeredUsers = {
        "user1": ["Name1", "Password1", "ID1", "Hospital1"],
        "Brad123": ["Brad McBradface", "123abc", "12345678901", "St. Olavs"]
    }
    self.registeredWalkies = {
        "walkie1": ["DeviceID1", "PrivKey1", "LocalServerContext1", "CurUser"]
    }
    self.localServerInfo = {
        "server": ["DeviceID", "ConnectionDetails", "CurNet", "PrivKey", "Location"]
    }

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
           
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        
        command = payload.get('command')

        if command == "register_user":
            username = payload.get('username')
            name = payload.get('name')
            password = payload.get('password')
            userId = payload.get('id')
            hospital = payload.get('hospital')
            self.registerUser(self, username, name, password, userId, hospital)
            self.stm_driver.send('registrationRequest', fix senere)
        
    
    def registerUser(self, username, name, password, userId, hospital):
        thisdict = {}
    
    def on_init(self):
        print('Init!')
        self.walkieID = 0
        self.walkiePrivKey = 0

    def updateDatabaseLogin(self):
        thisdict.update({"color": "red"}) 
        
    def validateRegistration():
        

    def sendMessageReg(self):
        

    def registration(self, username, name, password, id, hospital):
        registeredUsers.update({"username": "red"}) 
    
    def sendErrorRegistration():
        .

    def validateLogin():
        .
    
    def sendMessageLogin(self):
        

    def updateDatabaseLogin(self):
        thisdict.update({"color": "red"}) 
        

    def sendErrorLogin():
        .



autenticationServer = AutenticationServer()

t0 = {
    'source': 'initial',
    'target': 'idle',
    'effect': '__init__'}
      
t1 = {
    'trigger': 'loginRequest',
    'source': 'idle',
    'target': 'validating_login'}

t2 = {
    'trigger': 'notValid', 
    'source': 'validating_login', 
    'effect': 'sendErrorLogin'
    'target': 'idle'}

t3 = {
    'trigger': 'valid',
    'source': 'validating_login',
    'target': 'idle',
    'effect': 'sendMessageLogin; updateDatabaseLogin'}

t4 = {
    'trigger': 'registrationRequest',
    'source': 'idle',
    'target': 'validating_registration'}

t5 = {
    'trigger': 'notValid', 
    'source':' validating_registration', 
    'effect': 'sendErrorRegistration'
    'target': 'idle'}

t6 = {
    'trigger': 'valid',
    'source': 'validating_registration',
    'target': 'idle',
    'effect': 'sendMessageReg; registration'}

idle = {'name': 'idle'}

validating_login = {
    'name': 'validating_login',
    'entry': 'validateLogin',
    'defer': 'registationRequest',
    'defer': 'loginRequest'
    }

validating_registration = {
    'name': 'validation_registration',
    'entry': 'validateRegistration',
    'defer': 'registationRequest',
    'defer': 'loginRequest'
    }

# Change 4: We pass the set of states to the state machine
machine = Machine(name='Authentication_server', transitions=[t0, t1, t2, t3, t4, t5, t6], obj=authentication_server, states=[idle, validating_registration, validating_registration])
authentication_server.stm = machine

driver = Driver()
driver.add_machine(machine)
driver.start()