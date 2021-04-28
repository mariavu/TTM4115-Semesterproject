import paho.mqtt.client as mqtt
import stmpy
import logging
import json

from threading import Thread
from Infrastructure.Session import Session, SESSION_STATUS
from Domain.User import User
from Config.Constants import AUTH_SERVER_MESSAGE, WALKIE_MESSAGE, ERROR_CODES
from enum import Enum






class Controller:


    # Setup

    def registerWithAuthServer(self):
        self._authenticated = True #TODO send MQTT message to establish connection with authentication server and sync.
        pass

    def start(self):
        self._mqtt.connect(self._host, self._port)
        self._mqtt.subscribe(f"{self._rootTopic}/local_server/{self._id}/req") #Request topic
        self._mqtt.subscribe(f"{self._rootTopic}/local_server/{self._id}/res")
        self.registerWithAuthServer()
        self._mqtt.loop_start()
        

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
        
        self._messageHandlers = {
            WALKIE_MESSAGE.JOIN_CHANNEL : self.handleJoinChannel,
            WALKIE_MESSAGE.LOGIN: self.handleLoginRequest,
            WALKIE_MESSAGE.REGISTER: self.handleRegisterRequest
            }
  


    # Event handlers

    def onConnect(self, client, userdata, flags, rc):

        pass

    def onMessage(self, client, userdata, message):
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
        walkie = message.get("walkie")
        
        if message.get("error") is not None:
            self.sendErrorResponse(walkie, ERROR_CODES.INVALID_USERNAME_OR_PASSWORD)
        
        token = message.get("token")

        session = self._sessions.get(walkie)
        session.setToken(token)

        self.sendToWalkie(session.id, WALKIE_MESSAGE.LOGIN, {token: message.get("token")})

        


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
        channel = self.id
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
        message["command"] = message_type
        self.sendToMQTT(self.getAuthTopic(), message)

    
    def sendToMQTT(self, topic, payload):
        self._mqtt.publish(topic, json.dumps(payload))

    def getWalkieTopic(self, walkie):
        return f"{self._rootTopic}/walkie/{walkie}"

    def getAuthTopic(self):
        return f"{self._rootTopic}/auth_server"

    def sendToWalkie(self, walkie, message_type, message):
        message["command"] = message_type
        self.sendToMQTT(self.getWalkieTopic(walkie), message)


    def sendErrorResponse(self, walkie, error):
        self.sendToMQTT(self.getWalkieTopic(walkie), {error: error})

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





