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
MQTT_TOPIC_INPUT = 'ttm4115/team_5/authentication/requests'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_5/authentication/responses'

class AuthenticationServer:
    def __init__(self):
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
            self.stm_driver.send('registrationRequest')

        if command == "login":
            username = payload.get('username')
            password = payload.get('password')
            self.validateLogin(self, username, password)
            self.stm_driver.send('loginRequest')        
    
    def registerUser(self, username, name, password, userId, hospital):
        thisdict = {
            username: [name, password, userId, hospital]
        }
        return thisdict

        self.validateRegistration(thisdict)
    
    def on_init(self):
        print('Init!')
        self.walkieID = 0
        self.walkiePrivKey = 0

    def updateDatabaseLogin(self):
        thisdict.update({"color": "red"}) 
        
    def validateRegistration(self, newUser):
        counterBad = 0
        username = ''
        name = ''
        password = ''
        userId = ''
        hospital = ''
        
        for x, y in self.registeredUsers.items():
            for key, value in newUser.items():
                if key == x:
                    counterBad += 1
                    
                if value[2]== y[2]:
                    counterBad += 1
                
                username = key
                name = value[0]
                password = value[1]
                userId = value[2]
                hospital = value[3]
                
        if counterBad != 0:
            self.stm.send('notValid')
        else:
            self.stm.send('valid')
            self.registration(username, name, password, userId, hospital)

    def registration(self, username, name, password, userId, hospital):
        self.registeredUsers.update({username: [name, password, userId, hospital]}) 
    
    def sendMessageReg(self):
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "registration_successful"}))
    
    def sendErrorRegistration():
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "registration_failed"})) 
    
    def validateLogin(self, username, password):
        sentValid = False

        for x, y in self.registeredUsers.items():
            if x == username and y[1] == password:
                self.stm.send('valid')
                sentValid = True
        
        if not sentValid:
            self.stm.send('notValid')
    
    def sendMessageLogin(self):
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "login_successful"})) 

    def sendErrorLogin():
        self.component.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "login_failed"})) 



authentication_server = AuthenticationServer()

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
    'effect': 'sendErrorLogin',
    'target': 'idle'}

t3 = {
    'trigger': 'valid',
    'source': 'validating_login',
    'target': 'idle',
    'effect': 'sendMessageLogin'} # TODO: add updateDatabaseLogin

t4 = {
    'trigger': 'registrationRequest',
    'source': 'idle',
    'target': 'validating_registration'}

t5 = {
    'trigger': 'notValid', 
    'source':' validating_registration', 
    'effect': 'sendErrorRegistration',
    'target': 'idle'}

t6 = {
    'trigger': 'valid',
    'source': 'validating_registration',
    'target': 'idle',
    'effect': 'sendMessageReg'}

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
machine = stmpy.Machine(name='Authentication_server', transitions=[t0, t1, t2, t3, t4, t5, t6], obj=authentication_server, states=[idle, validating_registration, validating_registration])
authentication_server.stm = machine

driver = stmpy.Driver()
driver.add_machine(machine)
driver.start()