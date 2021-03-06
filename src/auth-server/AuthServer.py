import stmpy
import sys
import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
import random
from datetime import datetime
from datetime import date

# Define MQTTT broker and port
MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

#Define MQTT topics
MQTT_TOPIC_INPUT = 'ttm4115/team_5/semesterprosjekt/auth_server'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_5/semesterprosjekt/local_server/1/res'

class AuthenticationServer_MQTT:
    """
        The class is initialized with data fields and database dictionaries.
    """
    def __init__(self, broker, port, driver, inputTopic, outputTopic):
        self.driver = driver
        self.port = port
        self.broker = broker
        self.input = inputTopic
        self.output = outputTopic
        self._logger = logging.getLogger(__name__)

        #Database for all registered users
        # The format is "username": ["Name", "Password", "LocalServer"],
        self.registeredUsers = {
            "user1": ["Name1", "Password1", "1"],
            "Brad123": ["Brad McBradface", "123abc", "1"],
            "Team5": ["Jon Pedersen", "SyltetøyErGodt", "1"]
        }
        #Database for all registered walkie talkies
        # The format is "Device ID": ["Private Key", "Which local server it is connected to", "Current user"]
        self.registeredWalkies = {
            "DeviceID1": ["PrivKey1", "1", "CurUser1"],
            "DeviceID2": ["PrivKey2", "1", "CurUser2"],
            "DeviceID3": ["PrivKey3", "1", "CurUser3"],
            "DeviceID4": ["PrivKey4", "1", "CurUser4"],
            "DeviceID5": ["PrivKey5", "1", "CurUser5"]
        }
        #Database for all local servers connected to the authentication server
        #  "Local server ID": ["ConnectionDetails", "Current network", "Private key", "Location"]
        self.localServerInfo = {
            "1": ["Connected", "Trondheim", "PrivKey", "St. Olavs"]
        }

    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug('MQTT connected to {}'.format(client))
        self.mqtt_client.subscribe(self.input)
        #self.mqtt_client.subscribe(self.output)

    """
        The MQTT commands are listened to and appropriate actions are taken for each.
    """
    def on_message(self, client, userdata, msg):
        self._logger.debug('Incoming message to topic {}'.format(msg.topic))
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            #print(payload)
        except Exception as err:
            print('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            self.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": 2}), 2, False)
            return

        command = payload.get('command')
        if command == 101:
            username = payload.get('username')
            name = payload.get('name')
            password = payload.get('password')
            walkieId = payload.get('walkie')
            role = payload.get('role')
            localServer = payload.get('local_server')
            self.driver.send('registrationRequest','Authentication_server', args=[username, name, password, walkieId, role, localServer])
            
        if command == 100:
            username = payload.get('username')
            password = payload.get('password')
            walkieId = payload.get('walkie')
            localServer = payload.get('local_server')
            self.driver.send('loginRequest', 'Authentication_server', args = [username, password, walkieId, localServer])

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

"""
    This class is for validating registration and login credentials and sending confirmation messages via MQTT.
"""
class AuthenticationServer_Sender:
    def __init__(self, authMqtt):
        self.authMqtt = authMqtt

    def sendMessageReg(self, username, name, password, walkieId, role, localServer):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": 101, "walkie": walkieId, "name": name, "role": role}), 2, False)

    def sendErrorRegistration(self, error, walkieId):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": 101, "error":error, "walkie":walkieId}), 2, False)

    def sendMessageLogin(self, username, password, walkieId, token, localServer):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": 100, "walkie":walkieId, "token":token}), 2, False)

    def sendErrorLogin(self, error, walkieId):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": 100, "error": error, "walkie":walkieId}), 2, False)

    def sendLogOut(self):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "logout_successful"}), 2, False)
    
    def sendDelete(self):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "deletion_successful"}), 2, False)
    
    """
        A number of loops are used to validate the passed registration credentials. If one of the given fields are not vaild, the registration fails.
    """
    def validateRegistration(self, username, name, password, walkieId, role, localServer):
        usernameInUse = False
        validServer = False
        validWalkie = False
        error = 0
        for x in self.authMqtt.registeredUsers.keys():
            if username == x:
                usernameInUse = True
                error = 7

        for x in self.authMqtt.localServerInfo.keys():
            if x == localServer:
                validServer = True

        for x in self.authMqtt.registeredWalkies.keys():
            if x == walkieId:
                validWalkie = True


        if usernameInUse:
            self.authMqtt.driver.send('notValidReg', 'Authentication_server', args=[error,walkieId])
        elif not validServer:
            error = 13
            self.authMqtt.driver.send('notValidReg', 'Authentication_server', args=[error,walkieId])
        elif not validWalkie:
            error = 14
            self.authMqtt.driver.send('notValidReg', 'Authentication_server', args=[error,walkieId])
        else:
            self.authMqtt.driver.send('validReg', 'Authentication_server', args=[username, name, password, walkieId, role, localServer])

    """
        Adds the user that wants to register to the "database"
    """       
    def registration(self, username, name, password, walkieId, role, localServer):
        self.authMqtt.registeredUsers.update({username: [name, password,localServer]})

    """
        Validates if the user can log in or not by checking if the username and password given matches a user in the database.
        Also checks if the walkieId given belongs to a valid walkie.
        If the user is valid to log in a message is sent to the driver with the username, password, walkieId, localServer and token.
        If a user is not valid the driver is notified and the incident is logged.
        Token is a unique string of hexadecimal numbers used for message authentication.
    """ 
    def validateLogin(self, username, password, walkieId, localServer):
        sentValid = False
        validWalkie = False
        token = ""
        error = None
        
        for i in range(32):
            del i
            randomNr = random.randint(0, 1)
            if randomNr == 0:
                randomUpperLetter = chr(random.randint(ord('A'), ord('F')))
                token += randomUpperLetter
            elif randomNr == 1:
                number = str(random.randint(1, 9))
                token += number

        for x in self.authMqtt.registeredWalkies.keys():
            if x == walkieId:
                validWalkie = True

        for x, y in self.authMqtt.registeredUsers.items():
            if x == username and y[1] == password and y[2]== localServer and validWalkie:
                self.authMqtt.driver.send('validLog', 'Authentication_server', args=[username, password, walkieId, token, localServer])
                sentValid = True
            else:
                error = 1

            
        if not sentValid:
            f = open("UnsuccessfulLoginsLog.txt", "a")
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            today = date.today()
            dateToday = today.strftime("%B %d, %Y")
            txt = "Date: {}. Time: {}. \nUser with username {} tried to login using {} as password with walkieId {}. This returned the error message {}.\n \n"
            f.write(txt.format(dateToday, current_time, username,password, walkieId, error))
            f.close()
            self.authMqtt.driver.send('notValidLog', 'Authentication_server', args = [error, walkieId])
            
    """
        Updates the database of registered walkie talkies to contain the current user field of the user logged in.
    """ 
    def login(self, username, password, walkieId, token, localServer):
        self.authMqtt.registeredWalkies[walkieId][2] = username

t0 = {
    'source': 'initial',
    'target': 'idle'}

t1 = {
    'trigger': 'loginRequest',
    'source': 'idle',
    'target': 'validating_login',
    'effect': 'validateLogin(*)'} # Variables are passed to the state machines with the (*) notation.

t2 = {
    'trigger': 'notValidLog',
    'source': 'validating_login',
    'effect': 'sendErrorLogin(*)',
    'target': 'idle'}

t3 = {
    'trigger': 'validLog',
    'source': 'validating_login',
    'target': 'idle',
    'effect': 'sendMessageLogin(*); login(*)'}

t4 = {
    'trigger': 'registrationRequest',
    'source': 'idle',
    'target': 'validating_registration',
    'effect': 'validateRegistration(*)'}

t5 = {
    'trigger': 'notValidReg',
    'source': 'validating_registration',
    'effect': 'sendErrorRegistration(*)',
    'target': 'idle'}

t6 = {
    'trigger': 'validReg',
    'source': 'validating_registration',
    'target': 'idle',
    'effect': 'registration(*); sendMessageReg(*)'}

idle = {'name': 'idle'}

validating_login = {
    'name': 'validating_login',
    'defer': 'registationRequest; loginRequest; delete_user; log_out'
}

validating_registration = {
    'name': 'validation_registration',
    'defer': 'registationRequest; loginRequest; delete_user; log_out'
}

driver = stmpy.Driver()
server = AuthenticationServer_MQTT(MQTT_BROKER, MQTT_PORT, driver, MQTT_TOPIC_INPUT, MQTT_TOPIC_OUTPUT)

authenticationSender = AuthenticationServer_Sender(server)
machine = stmpy.Machine(name='Authentication_server', transitions=[t0, t1, t2, t3, t4, t5, t6],
                        obj=authenticationSender, states=[idle, validating_login, validating_registration])
authenticationSender.stm = machine


driver.add_machine(machine)
server.start()
driver.start()
