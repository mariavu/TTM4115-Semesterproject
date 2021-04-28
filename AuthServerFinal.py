import stmpy
import sys
import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
import random

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
        self.registeredUsers = {
            "user1": ["Name1", "Password1", "ID1", "Hospital1"],
            "Brad123": ["Brad McBradface", "123abc", "12345678901", "St. Olavs"],
            "Nora": ["Nora Syltetøy", "SyltetøyErGodt", "908976453", "St. Olavs"],
            "Jo": ["Jo Ho", "Godteri", "85733727281", "St. Olavs"],
            "Ricola": ["Ricola Drops", "Hals", "727274615", "St. Olavs"]
        }
        #Database for all registered walkie talkies
        self.registeredWalkies = {
            "DeviceID1": ["PrivKey1", "LocalServerContext1", "CurUser1"],
            "DeviceID2": ["PrivKey2", "LocalServerContext2", "CurUser2"],
            "DeviceID3": ["PrivKey3", "LocalServerContext3", "CurUser3"],
            "DeviceID4": ["PrivKey4", "LocalServerContext4", "CurUser4"],
            "DeviceID5": ["PrivKey5", "LocalServerContext5", "CurUser5"]
        }
        #Database for all local servers connected to the authentication server
        self.localServerInfo = {
            "server": ["DeviceID", "ConnectionDetails", "CurNet", "PrivKey", "Location"]
        }
        #Database for all logged in users
        self.loggedInUsers ={
            "user1": ["Password1", "DeviceID1", "token"],
            "Brad123": ["123abc", "DeviceID2", "D1BBBF7E7BB55E62ED4AC9CDD9B74645"],
            "Nora": ["SyltetøyErGodt", "DeviceID3", "F173D9195C86E93B64C156E2436CC2AB"],
            "Jo": ["Godteri", "DeviceID4", "A1A177F31F1F2C39B887548A5DA9BFA6"],
        }

    def on_connect(self, client, userdata, flags, rc):
        self._logger.debug('MQTT connected to {}'.format(client))
        self.mqtt_client.subscribe(self.input)
        #self.mqtt_client.subscribe(self.output)

    """
        The MQTT commands are listened to and appropriate actions are taken for each.
        There are no states for the log_out and delete_user commands, as these operations are straightforward.
    """
    def on_message(self, client, userdata, msg):
        self._logger.debug('Incoming message to topic {}'.format(msg.topic))
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            #print(payload)
        except Exception as err:
            print('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            self.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": 2}))
            return

        command = payload.get('command')
        
        if command == 100:
            username = payload.get('username')
            name = payload.get('name')
            password = payload.get('password')
            userId = payload.get('id')
            hospital = payload.get('hospital')
            self.driver.send('registrationRequest','Authentication_server', args=[username, name, password, userId, hospital])
            
        if command == 101:
            username = payload.get('username')
            password = payload.get('password')
            walkieId = payload.get('walkieId')
            self.driver.send('loginRequest', 'Authentication_server', args = [username, password, walkieId])

        """
            When a log_out command is received it checks if there are any users with that username logged in already.
            If there are this user is removed from the loggedInUsers database and the current user of that walkie talkie is set to None.
            Then the driver is informed of the incomming request for log_out. 
            If there are no such user logged in a MQTT message is sent to inform the sender.
        """
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

        """
            Before deleting a user, it is first checked whether the user is registered or logged in, and error messages are sent accordingly.
            A user is deleted by removing it from the registeredUsers dictionary and dissasociating its walkie.
        """
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

"""
    This class is for validating registration and login credentials and sending confirmation messages via MQTT.
"""
class AuthenticationServer_Sender:
    def __init__(self, authMqtt):
        self.authMqtt = authMqtt

    def sendMessageReg(self):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": 101}))

    def sendErrorRegistration(self, error):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": 101, "error_message":error}))

    def sendMessageLogin(self, username, password, walkieId, token):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": 100, "username":username, "token":token}))

    def sendErrorLogin(self, error):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": 100, "error_message": error}))

    def sendLogOut(self):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "logout_successful"}))
    
    def sendDelete(self):
        self.authMqtt.mqtt_client.publish(MQTT_TOPIC_OUTPUT, json.dumps({"command": "deletion_successful"}))
    
    """
        A counter is used to validate the passed registration credentials. A new dictionary for the newly registered user is made,
        and it is compared with the already registered users. If one or more fields in the dictionaries are the same, the registration fails.
    """
    def validateRegistration(self, username, name, password, userId, hospital):
        counterBad = 0
        newUser = {
            username: [name, password, userId, hospital]
        }
        for x, y in self.authMqtt.registeredUsers.items():
            for key, value in newUser.items():
                if key == x:
                    counterBad += 1

                if value[2] == y[2]:
                    counterBad += 1

        if counterBad != 0:
            self.authMqtt.driver.send('notValidReg', 'Authentication_server', args=[7])
        else:
            self.authMqtt.driver.send('validReg', 'Authentication_server', args=[username, name, password, userId, hospital])

    """
        Adds the user that wants to register to the "database"
    """       
    def registration(self, username, name, password, userId, hospital):
        self.authMqtt.registeredUsers.update({username: [name, password, userId, hospital]})

    """
        Validates if the user can log in or not by checking if the username and password given matches a user in the database.
        If the user is valid to log in a message is sent to the driver with the username, password, walkieId and token.
        If a user is not valid the driver is notified.
        Token is a unique string of hexadecimal numbers used for message authentication.
    """ 
    def validateLogin(self, username, password, walkieId):
        sentValid = False
        token = ""
        error = None
        if username in self.authMqtt.loggedInUsers:
            error = 4
        else:
            for i in range(32):
                randomNr = random.randint(0, 1)
                if randomNr == 0:
                    randomUpperLetter = chr(random.randint(ord('A'), ord('F')))
                    token += randomUpperLetter
                elif randomNr == 1:
                    number = str(random.randint(1, 9))
                    token += number

            for x, y in self.authMqtt.registeredUsers.items():
                if x == username and y[1] == password:
                    self.authMqtt.driver.send('validLog', 'Authentication_server', args=[username, password, walkieId, token])
                    sentValid = True
                else:
                    error = 1
            
        if not sentValid:
            self.authMqtt.driver.send('notValidLog', 'Authentication_server', args = [error])
            
    """
        Adds the user to the database of logged in users and updates the database of registered walkie talkies to contain the current user field of the user logged in.
    """ 
    def login(self, username, password, walkieId, token):
        self.authMqtt.loggedInUsers.update({username: [password, walkieId, token]})
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
    'trigger': 'notValidLog',
    'source': 'validating_login',
    'effect': 'sendErrorLogin(*)',
    'target': 'idle'}

t5 = {
    'trigger': 'validLog',
    'source': 'validating_login',
    'target': 'idle',
    'effect': 'sendMessageLogin(*); login(*)'}

t6 = {
    'trigger': 'registrationRequest',
    'source': 'idle',
    'target': 'validating_registration',
    'effect': 'validateRegistration(*)'}

t7 = {
    'trigger': 'notValidReg',
    'source': 'validating_registration',
    'effect': 'sendErrorRegistration(*)',
    'target': 'idle'}

t8 = {
    'trigger': 'validReg',
    'source': 'validating_registration',
    'target': 'idle',
    'effect': 'registration(*); sendMessageReg'}

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
machine = stmpy.Machine(name='Authentication_server', transitions=[t0, t1, t2, t3, t4, t5, t6, t7, t8],
                        obj=authenticationSender, states=[idle, validating_login, validating_registration])
authenticationSender.stm = machine


driver.add_machine(machine)
server.start()
driver.start()
