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
    UNAUTHORIZED = 5
    UNKNOWN_CHANNEL = 6

class AUTH_SERVER_MESSAGE(enum):
    LOGIN = 100
    REGISTER = 101
   # REGISTER_LOCAL_SERVER = 102 (Not necessary)

class WALKIE_MESSAGE(enum):
    LOGIN = 0
    REGISTER = 1
    LIST_MESSAGES = 2
    




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


    def handleRegisterResponse(self, message):
        if message.get("error") is not None:
            self.sendErrorResponse(message.get("session"), message.get("error"))
    
        session = self._sessions.get((message.get("session")))
        session.setStatus(SESSION_STATUS.REGISTERED)


        name = message.get("name")
        role = message.get("role")


        newUserId = f"USER-{self._db.getUsersCount() + 1}"

        self._db.addUser(User(newUserId, session.userName, name, [role], []))
        self.sendToWalkie(session.id, WALKIE_MESSAGE.REGISTER, {status: 200})
        


    def handleLoginRequest(self, message): #Request from walkie
        walkie = message.get("walkieId")
        username = message.get("username")
        password = message.get("password")

        self.ensureUserNotLoggedIn(username)
        self.ensureWalkieNotInUse(walkie)

        newSession = self.createSession(SESSION_STATUS.PENDING_LOGIN, walkie, username)
        self._sessions.append(newSession)

        self.sendToAuthServer(AUTH_SERVER_MESSAGE.LOGIN, {"walkie": walkie, "username" : username, "password" : password})
    

    def handleLoginResponse(self, message): #Response from auth_server
        if message.get("error") is not None:
            self.sendErrorResponse(message.get("session"), ERROR_CODES.INVALID_USERNAME_OR_PASSWORD)

        session = self._sessions.get((message.get("session")))
        session.authenticated = True

        self.sendToWalkie(session.id, WALKIE_MESSAGE.LOGIN, {status: 200}) # 200 OK

        


    def handleJoinChannel(self, message): #{command: JOIN_CHANNEL, channel: <Id>, session: <Id>}
        channel = self._db.findChannel(message.get("channel"))
        session = self._sessions.get(message.get("session"))

        if channel is None:
            raise Exception(ERROR_CODES.UNKNOWN_CHANNEL)
        if channel in session.joinedChannels:
            return # * Already joined channel; do nothing.

        # Check for roles and ensure user has appropriate role for joining channel
        
        
        session.joinedChannels.append(session)

    def handleLeaveChannel(self, message): #{command: LEAVE_CHANNEL, channel: <Id>, session: <Id>}
        channel = self._db.findChannel(message.get("channel"))
        session = self._sessions.get(message.get("session"))
        if channel is None:
            raise Exception(ERROR_CODES.UNKNOWN_CHANNEL)
    

    def handleSendMessage(self, message): #{command: SEND_MESSAGE, message: <MESSAGE_DATA>, channel: <Id>, session: <Id>}
        
        #TODO Use database to find channel object. If not exists, raise exception, make sure user has joined channel if it is GroupChannel
        #TODO Lookup all participants and add message newMessages
        #TODO For each participant, if active session: Relay message
        pass

    def handleListMessages(self, message): #{command: LIST_MESSAGES, channel: <Id>}
        channel = self._db.findChannel(message.get("channel"))
        session = self._sessions.get(message.get("session"))
        # TODO Send to 
        self.sendToWalkie(session, WALKIE_MESSAGE.LIST_MESSAGES,{channel: channel.id, messages: message})
        pass

    def handleGetMessage(self, message):
        channel = self.d
        pass


    def handleRequest(self, message): #from walkie  #{error: {code: <CODE>, description: <string>}}

        try:
            #TODO Convert message to JSON and pass it to message handlers
            if(message.type in self._messageHandlers):
                if not (message.type in [WALKIE_MESSAGE.LOGIN, WALKIE_MESSAGE.REGISTER]):
                    self.ensureAuthenticated(message.get("session"))
                
                self._messageHandlers.get(message.type)(message)
            else:
                raise Exception(ERROR_CODES.UNKNOWN_MESSAGE_TYPE)
        except Exception as exception:
            self.sendErrorResponse(message.get("session"), exception)
            

    def handleResponse(self, message): #from auth. server
        # TODO 
        pass
    

     # Helper methods
    
    def sendToAuthServer(self, message_type, message):
        # TODO Implement
        return
    
    def sendToWalkie(self, session, message_type, message):
        # TODO Implement
        return

    def sendErrorResponse(self, session, error):
        # TODO convert error to Payload and dispatch to MQTT.
        return

    def ensureAuthenticated(self, sessionId):
        for session in self._sessions.values():
            if session.id == sessionId:
                raise Exception(ERROR_CODES.UNAUTHORIZED)

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
        del session






