import stmpy
import sys
import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
import random

# TODO: choose proper MQTT broker address
MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

# TODO: choose proper topics for communication
MQTT_TOPIC_INPUT = 'ttm4115/team_5/authentication/requests'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_5/authentication/responses'

class AuthenticationServer_MQTT:
    def __init__(self, broker, port, driver, inputTopic, outputTopic):
        self.driver = driver
        self.port = port
        self.broker = broker
        self.input = inputTopic
        self.output = outputTopic
        self._logger = logging.getLogger(__name__)
        self.walkieID = 0
        self.walkiePrivKey = 0

        self.registeredUsers = {
            "user1": ["Name1", "Password1", "ID1", "Hospital1"],
            "Brad123": ["Brad McBradface", "123abc", "12345678901", "St. Olavs"]
        }
        self.registeredWalkies = {
            "DeviceID1": ["PrivKey1", "LocalServerContext1", "CurUser1"],
            "DeviceID2": ["PrivKey2", "LocalServerContext2", "CurUser2"],
            "DeviceID3": ["PrivKey3", "LocalServerContext3", "CurUser3"]
        }
        self.localServerInfo = {
            "server": ["DeviceID", "ConnectionDetails", "CurNet", "PrivKey", "Location"]
        }
        self.loggedInUsers ={
            "username": ["password", "walkieId", "token"]
        }

    def validateRegistration(self, username, name, password, userId, hospital):
        counterBad = 0
        newUser = {
            username: [name, password, userId, hospital]
        }

        for x, y in self.registeredUsers.items():
            for key, value in newUser.items():
                if key == x:
                    counterBad += 1

                if value[2] == y[2]:
                    counterBad += 1

        if counterBad != 0:
            self.driver.send('notValid', 'Authentication_server')
        else:
            self.driver.send('valid', 'Authentication_server')
            print("\n In Validate registration:   ","username:", username, "name:", name, "password:", password, "userId:", userId, "hospital:", hospital)
            self.registeredUsers.update({username: [name, password, userId, hospital]})

    def validateLogin(self, username, password, walkieId):
        sentValid = False
        '''{"command": "register_user",  "username": "Bob", "name": "Bob", "password": "123abc1", "id":"121qwerqw", "hospital":"St. Olavs"}
        {"command": "login",  "username": "Bob", "password": "123abc1","walkieId": "DeviceID1"}'''
        token = ""
        for i in range(32):
            randomNr = random.randint(0, 1)
            if randomNr == 0:
                randomUpperLetter = chr(random.randint(ord('A'), ord('F')))
                token += randomUpperLetter
            elif randomNr == 1:
                number = str(random.randint(1, 9))
                token += number

        for x, y in self.registeredUsers.items():
            if x == username and y[1] == password:
                self.loggedInUsers.update({username: [password, walkieId, token]})
                self.registeredWalkies[walkieId][2] = username
                self.driver.send('valid', 'Authentication_server')
                print(self.loggedInUsers)
                print(self.registeredWalkies)
                '''AuthenticationServer_Sender.sendMessageLogin(self, token)'''
                sentValid = True
        
        if not sentValid:
            self.driver.send('notValid', 'Authentication_server')
        

    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))
        self.mqtt_client.subscribe(self.input)
        self.mqtt_client.subscribe(self.output)

    def on_message(self, client, userdata, msg):
        self._logger.debug('Incoming message to topic {}'.format(msg.topic))
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            print(payload)
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
            self.driver.send('registrationRequest','Authentication_server')
            print("\n username:", username, "name:", name, "password:", password, "userId:", userId, "hospital:", hospital)
            self.validateRegistration(username, name, password, userId, hospital)
        

        if command == "login":
            username = payload.get('username')
            password = payload.get('password')
            walkieId = payload.get('walkieId')
            self.driver.send('loginRequest', 'Authentication_server')
            print("username:", username, "password:", password, "")
            self.validateLogin(username, password, walkieId)

        if command == "log_out":
            username = payload.get('username')
            try:
                values = self.loggedInUsers.get(username)
                walkieId = values[1]
                self.loggedInUsers.pop(username)
                self.registeredWalkies[walkieId][2] = None 
                self.driver.send('log_out','Authentication_server')
            except Exception as err:
                self.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "logout_unsuccessful", "username": username, "error_message": "user not logged in"}))
                return

        if command == "delete_user":
            username = payload.get('username')
            if username not in self.registeredUsers:
                self.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "delete_unsuccessful", "username": username, "error_message": "no such user registered"}))
            elif username not in self.loggedInUsers:
                self.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "delete_unsuccessful", "username": username, "error_message": "no such user logged in"}))
            else:
                values = self.loggedInUsers.get(username)
                walkieId = values[1]
                self.registeredWalkies[walkieId][2] = None
                self.loggedInUsers.pop(username)
                self.registeredUsers.pop(username)
                self.driver.send('delete_user','Authentication_server')           
                   
    def start(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_connect = self.on_connect
        
        self.mqtt_client.connect(self.broker, self.port)
        try:
            thread = Thread(target=self.mqtt_client.loop_forever)
            thread.start()
        except KeyboardInterrupt:
            print("Interrupted")
            self.mqtt_client.disconnect()


class AuthenticationServer_Sender:
    def __init__(self, authMqtt):
        self.authMqtt = authMqtt

    def sendMessageReg(self):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "registration_successful"}))
        print(self.authMqtt.registeredUsers)

    def sendErrorRegistration(self):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "registration_failed"}))
        print(self.authMqtt.registeredUsers)

    def sendMessageLogin(self):
        username = ""
        for key in self.authMqtt.loggedInUsers.keys():
            username = key
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "login_successful", "token":self.authMqtt.loggedInUsers[username][2]}))

    def sendErrorLogin(self):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "login_failed"}))

    def sendLogOut(self):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "logout_successful"}))
    
    def sendDelete(self):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "deletion_successful"}))

t0 = {
    'source': 'initial',
    'target': 'idle'}

t1 = {
    'trigger': 'loginRequest',
    'source': 'idle',
    'target': 'validating_login'}

t2 = {
    'trigger': 'log_out',
    'source': 'idle',
    'target': 'idle',
    'effect':'sendLogOut'}

t3 = {
    'trigger': 'delete_user',
    'source': 'idle',
    'target': 'idle',
    'effect':'sendDelete'}

t4 = {
    'trigger': 'notValid',
    'source': 'validating_login',
    'effect': 'sendErrorLogin',
    'target': 'idle'}

t5 = {
    'trigger': 'valid',
    'source': 'validating_login',
    'target': 'idle',
    'effect': 'sendMessageLogin'}

t6 = {
    'trigger': 'registrationRequest',
    'source': 'idle',
    'target': 'validating_registration'}

t7 = {
    'trigger': 'notValid',
    'source': 'validating_registration',
    'effect': 'sendErrorRegistration',
    'target': 'idle'}

t8 = {
    'trigger': 'valid',
    'source': 'validating_registration',
    'target': 'idle',
    'effect': 'sendMessageReg'}

idle = {'name': 'idle'}

validating_login = {
    'name': 'validating_login',
    'defer': 'registationRequest; loginRequest'
}

validating_registration = {
    'name': 'validation_registration',
    'entry': 'validateRegistration',
    'defer': 'registationRequest;loginRequest'
}

driver = stmpy.Driver()
server = AuthenticationServer_MQTT(MQTT_BROKER, MQTT_PORT, driver, MQTT_TOPIC_INPUT, MQTT_TOPIC_OUTPUT)

authenticationSender = AuthenticationServer_Sender(server)
machine = stmpy.Machine(name='Authentication_server', transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8],
                        obj=authenticationSender, states=[idle, validating_login, validating_registration])
authenticationSender.stm = machine


driver.add_machine(machine)
server.start()
driver.start()