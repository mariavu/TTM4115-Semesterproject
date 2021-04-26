import paho.mqtt.client as mqtt
import stmpy
import logging
import json

from threading import Thread
from Infrastructure.Session import Session, SESSION_STATUS
from Domain.User import User

from enum import Enum

class ERROR_CODES(enum):
    SESSION_EXISTS = 0
    INVALID_USERNAME_OR_PASSWORD = 1
    UNKNOWN_MESSAGE_TYPE = 2
    WALKIE_IN_USE = 3
    USER_ALREADY_LOGGED_IN = 4

class AUTH_SERVER_MESSAGE(enum):
    LOGIN = 100
    REGISTER = 101,
   # REGISTER_LOCAL_SERVER = 102 (Not necessary)

class WALKIE_MESSAGE(enum):
    LOGIN = 0
    REGISTER = 1
    




class Controller:


    # Setup

    def registerWithAuthServer(self):
        #TODO send MQTT message to establish connection with authentication server and sync.
        pass

    def start(self):
        self._mqtt.connect(self._host, self._port)
        self._mqtt.subscribe(f"{self._rootTopic}/{self._id}/request") #Request topic
        self._mqtt.subscribe(f"{self._rootTopic}/{self._id}/response")

        self.registerWithAuthServer()

    def __init__(self, db, host, port, id, rootTopic):
        self._db = db
        self._authenticated = False #Not yet authenticated with authentication server.
        self._mqtt = mqtt.Client()
        self._mqtt.on_connect = self.onConnect
        self._mqtt.on_message = self.onMessage
        self._host = host
        self._id = id
        self._port = port
        self._rootTopic = rootTopic
        self._sessions = {}
        
        self._messageHandlers = {'joinChannel' : self.handleJoinChannel} #This dictionary will contain all message_type => message_handler()

  


    # Event handlers

    def onConnect(self):

        pass

    def onMessage(self, message):
        #TODO Determine if message is from authentication server or walkie and forward to handleRequest/handleResponse
        pass

   


    # Message Handlers

    def handleRegisterRequest(self, message):
        walkie = message.get("walkieId")
        username = message.get("username")
        name = message.get("name")
        password = message.get("password")
        self.ensureWalkieNotInUse(walkie)

        newSession = self.createSession(SESSION_STATUS.PENDING_REGISTRATION, walkie, user)
        self._sessions.append(newSession)

        self.sendToAuthServer(AUTH_SERVER_MESSAGE.REGISTER,{'walkie': walkie, 'username': username, 'name': name, 'password': password})

        #TODO Send all relevant fields to authentication server.


    def handleRegisterResponse(self, message):
        if message.get("error") is not None:
            return #TODO SEND ERROR RESPONSE
    
        session = self._sessions.get((message.get("session")))
        session.setStatus(SESSION_STATUS.REGISTERED)


        name = message.get("name")
        role = message.get("role")


        newUserId = f"USER-{self._db.getUsersCount() + 1}"

        self._db.addUser(User(newUserId, session.userName, name, [role], []))

        #TODO Send register successful

        


    def handleLoginRequest(self, message): #Request from walkie
        #TODO Send authentication request to AuthServer

        walkie = message.get("walkieId")
        username = message.get("username")
        password = message.get("password")

        self.ensureUserNotLoggedIn(username)
        self.ensureWalkieNotInUse(walkie)

        newSession = self.createSession(SESSION_STATUS.PENDING_LOGIN, walkie, username)
        self._sessions.append(newSession)

        #TODO SEND AUTHENTICATION REQUEST
    

    def handleLoginResponse(self, message): #Response from auth_server
        if message.get("error") is not None:
            return #TODO SEND ERROR RESPONSE
    
        session = self._sessions.get((message.get("session")))
        session.authenticated = True

        #TODO Send login successful


    def handleJoinChannel(self, message): #{command: JOIN_CHANNEL, channel: <Id>, session: <Id>}
        channel = message.get("channel")
        session = self._sessions.get(message.get("session"))

        #TODO Use database to find channel object. If not exists, raise exception

        pass

    def handleLeaveChannel(self, message): #{command: LEAVE_CHANNEL, channel: <Id>, session: <Id>}
        #TODO Use database to find channel object. If not exists, raise exception
        pass

    def handleSendMessage(self, message): #{command: SEND_MESSAGE, message: <MESSAGE_DATA>, channel: <Id>, session: <Id>}
        #TODO Use database to find channel object. If not exists, raise exception, make sure user has joined channel if it is GroupChannel
        #TODO Lookup all participants and add message newMessages
        #TODO For each participant, if active session: Relay message
        pass

    def handleListMessages(self, message): #{command: LIST_MESSAGES, channel: <Id>}
        #TODO Return messages...
        pass

    def handleGetMessage(self, message):
        pass


    def handleRequest(self, message): #from walkie  #{error: {code: <CODE>, description: <string>}}

        #TODO Convert message to JSON and pass it to message handlers
        if(message.type in self._messageHandlers):
            if not (message.type in [WALKIE_MESSAGE.LOGIN, WALKIE_MESSAGE.REGISTER]):
                self.ensureAuthenticated(message.get("session"))
            
            self._messageHandlers.get(message.type)(message)
        else:
            raise Exception(ERROR_CODES.UNKNOWN_MESSAGE_TYPE)
        pass
    
        # TODO Make sure to ensure that the user is authenticated if the message is not REGISTER/LOGIN

    def handleResponse(self, message): #from auth. server
        pass
    

     # Helper methods
    
    def sendToAuthServer(self, message_type, message):
        # TODO Implement
        return

    def ensureAuthenticated(self, session): # TODO
        return

    def ensureWalkieNotInUse(self, walkie):
        for session in self._sessions.values():
            if session.walkie == walkie:
                raise Exception(ERROR_CODES.WALKIE_IN_USE)

    def ensureUserNotLoggedIn(self, username):
        for session in self._sessions.values():
            if session.status == SESSION_STATUS.AUTHENTICATED and session.user.username == username:
                raise Exception(ERROR_CODES.USER_ALREADY_LOGGED_IN)

    
    def createSession(self, initialStatus, walkie, user):
        return Session(walkie, user)
    
    def destroySession(self, session):
        del self._sessions[session.id]
        #TODO Maybe send session_teardown messaage?
        del session






