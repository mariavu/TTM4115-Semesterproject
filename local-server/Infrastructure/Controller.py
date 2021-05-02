import paho.mqtt.client as mqtt
import stmpy
import logging
import json
import traceback
import datetime



from threading import Thread
from Infrastructure.Session import Session, SESSION_STATUS
from Domain.User import User
from Domain.Message import Message
from uuid import uuid4

from Config.Constants import AUTH_SERVER_MESSAGE, ERROR_CODES, WALKIE_MESSAGE
from Infrastructure.Session import SessionStateMachineConfig



class Controller:


# Setup

    def registerWithAuthServer(self):
        self._authenticated = True
        pass

    def start(self):
        self._mqtt.connect(self._host, self._port)
        self._mqtt.subscribe(f"{self._rootTopic}/local_server/{self._id}/req") #Request topic
        self._mqtt.subscribe(f"{self._rootTopic}/local_server/{self._id}/res")
        self.registerWithAuthServer()
        self._mqtt.loop_start()
        self._driver.start(keep_active=True)
        
       


    def __init__(self, db, host, port, id, rootTopic, tpm):
        self._db = db
        self._authenticated = False #Not yet authenticated with authentication server.
        self._mqtt = mqtt.Client()
        self._mqtt.on_connect = self.onConnect
        self._mqtt.on_message = self.onMessage
        self._host = host
        self._id = id
        self._port = port
        self._rootTopic = rootTopic
        self._sessions = []
        self._tpm = tpm
        self._driver = stmpy.Driver()


        self._walkieHandlers = {
            WALKIE_MESSAGE.JOIN_CHANNEL.value : self.handleJoinChannel,
            WALKIE_MESSAGE.LOGIN.value: self.handleLoginRequest,
            WALKIE_MESSAGE.REGISTER.value: self.handleRegisterRequest,
            WALKIE_MESSAGE.LEAVE_CHANNEL.value: self.handleLeaveChannel,
            WALKIE_MESSAGE.LIST_MESSAGES.value : self.handleListMessages,
            WALKIE_MESSAGE.GET_MESSAGE.value : self.handleGetMessage,
            WALKIE_MESSAGE.SEND_MESSAGE.value : self.handleSendMessage,
            WALKIE_MESSAGE.SIGN_OUT.value: self.handleLogoutRequest,
            WALKIE_MESSAGE.LIST_CHANNELS.value: self.handleListChannels
            }
        
        self._authHandlers = {
            AUTH_SERVER_MESSAGE.REGISTER.value: self.handleRegisterResponse,
            AUTH_SERVER_MESSAGE.LOGIN.value: self.handleLoginResponse,
        }
  
# Event handlers

    def onConnect(self, client, userdata, flags, rc):
        print("connected")
        pass

    def onMessage(self, client, userdata, message):
        try:
            payload = json.loads(message.payload.decode("utf-8"))
            command = payload.get("command")
            walkie = payload.get("walkie", None)
            session = None
            try:
                if command in self._authHandlers:
                    session = self.findSessionFromWalkie(walkie)
                    self._authHandlers[command](session, payload)
                    return
                if command in self._walkieHandlers:
                    if command not in [WALKIE_MESSAGE.REGISTER.value, WALKIE_MESSAGE.LOGIN.value]:
                        #Authenticated request; must verify token
                        token = payload.get("token", None)
                        self.ensureValidToken(token)
                        session = self.findSessionFromToken(token)
                    self._walkieHandlers[command](session, payload)
                    return
                raise Exception(ERROR_CODES.UNKNOWN_MESSAGE_TYPE)
            except Exception as error:
                details = None
                if len(error.args) == 2:
                    details = error.args[1]
                if session is not None:
                    walkie = session.walkie
                if walkie is not None:
                    self.sendErrorResponse(command, walkie, error.args[0], details)#command.payload.get("walkie"), error.args[0])
                return
        except Exception as err:
            print("Unhandled exception occurred ", traceback.print_exc(err))
            return

# Message Handlers

    def handleRegisterRequest(self, session, message):
        walkie = message.get("walkie")
        username = message.get("username")
        name = message.get("name")
        password = message.get("password")
        role = message.get("role")
        
        self.ensureWalkieNotInUse(walkie)
        self.createSession(walkie, username)

        self._driver.send("regBegin", walkie)

        self.sendToAuthServer(AUTH_SERVER_MESSAGE.REGISTER,{'walkie': walkie, 'username': username, 'name': name, 'password': password, 'role' : role, 'local_server' : self._id})


    def handleRegisterResponse(self, session, message):
        if message.get("error") is not None:
            print("was error")
            self._driver.send("regFail", session.walkie)
            raise Exception(message.get("error"), {})
        
        self._driver.send("regSuccess", session.walkie)

        name = message.get("name")
        role = message.get("role")

        newUserId = f"USER-{self._db.getUsersCount() + 1}"

        self._db.addUser(User(newUserId, session.userName, name, [role], []))
        self.sendToWalkie(session.walkie, WALKIE_MESSAGE.REGISTER, {'status': 200})
        
    def handleLogoutRequest(self, session, message):
        self._driver.send("signOut", session.walkie)


    def handleLoginRequest(self, session, message): #Request from walkie
        
        walkie = message.get("walkie")
        username = message.get("username")
        password = message.get("password")


        self.ensureUserNotLoggedIn(username)
        self.ensureWalkieNotInUse(walkie)

        self.createSession(walkie, username)
        self._driver.send("authBegin", walkie)
        self.sendToAuthServer(AUTH_SERVER_MESSAGE.LOGIN, {"walkie": walkie, "username" : username, "password" : password, 'local_server': self._id})
    

    def handleLoginResponse(self, session, message): #Response from auth_server
        walkie = message.get("walkie")
        
        if message.get("error") is not None:
            self._driver.send("authFail", walkie)
            raise Exception(message.get("error"))

        token = message.get("token")
        self._driver.send("authSuccess", walkie, [token])
        self.sendToWalkie(walkie, WALKIE_MESSAGE.LOGIN, {'token': token})


    def handleJoinChannel(self, session, message): #{command: JOIN_CHANNEL, channel: <Id>, session: <Id>}
        channel = self._db.findChannel(message.get("channel"))

        if channel is None:
            raise Exception(ERROR_CODES.UNKNOWN_CHANNEL)
        if channel in session.joinedChannels:
            raise Exception(ERROR_CODES.ALREADY_PARTICIPATING_IN_CHANNEL)
        user = self._db.findUser(session.userName)
        if not channel.hasAccess(user):
            raise Exception(ERROR_CODES.ACCESS_DENIED)

        self._driver.send("joinedChannel", session.walkie, [channel])
        self.sendToWalkie(session.walkie, WALKIE_MESSAGE.JOIN_CHANNEL, {'channel': channel.id})
    
    def handleListChannels(self, session, message):
        channels = self._db.findAllChannels()
        user = self._db.findUser(session.userName)
        result = []
        for channel in channels.values():
            if not channel.hasAccess(user):
                continue
            result.append({'id' : channel.id, 'name' : channel.name})
        self.sendToWalkie(session.walkie, WALKIE_MESSAGE.LIST_CHANNELS, {'channels' : result})



    def handleLeaveChannel(self, session, message):
        channelId = message.get("channel")
        channel = self._db.findChannel(channelId)

        if channel is None:
            raise Exception(ERROR_CODES.UNKNOWN_CHANNEL)

        if not channelId in session.joinedChannels:
            raise Exception(ERROR_CODES.NOT_PARTICIPATING_IN_CHANNEL)
    
        self._driver.send("leftChannel", session.walkie , [channel])
        self.sendToWalkie(session.walkie, WALKIE_MESSAGE.LEAVE_CHANNEL, {'channel' : channelId})

    def handleSendMessage(self, session, message): 
        channelId = message.get("channel")
        payload = message.get("payload")
        duration = message.get("duration")
        messageId = message.get("id")
        emergency = message.get("emergency")

        channel = self._db.findChannel(channelId)
        if channel is None:
            raise Exception(ERROR_CODES.UNKNOWN_CHANNEL)
        sender = self._db.findUser(session.userName)
        if not channel.hasAccess(sender):
            raise Exception(ERROR_CODES.ACCESS_DENIED)



        newMessage = Message(messageId, sender.id,  channelId, duration, emergency,payload, datetime.datetime.now())
        result = channel.publishMessage(newMessage)
        if result == -1:
            raise Exception(ERROR_CODES.VOICE_MESSAGE_TOO_LONG)
        if result == 0:
            raise Exception(ERROR_CODES.VOICE_MESSAGE_LIMIT_EXCEEDED)
        self._db.addMessage(newMessage)
        for otherSession in self._sessions: #Broadcasting to other walkies
            if otherSession.walkie == session.walkie:
                continue            
            if not (channel.id in otherSession.joinedChannels):
                continue
            print("Sending to ", otherSession.userName)
            self.sendToWalkie(otherSession.walkie, WALKIE_MESSAGE.INCOMING_MESSAGE, {'id' : messageId, 'duration' : newMessage.duration, 'emergency': newMessage.isEmergency, 'payload': newMessage.payload, 'timestamp' : newMessage.timestamp.strftime("%Y-%m-%d %H:%M:%S")})

        self.sendToWalkie(session.walkie, WALKIE_MESSAGE.SEND_MESSAGE, {'id' : messageId})

    def handleListMessages(self, session, message):
        channel = self._db.findChannel(message.get("channel"))
        messageDetails = []
        user = self._db.findUser(session.userName)
        if not channel.hasAccess(user):
            raise Exception(ERROR_CODES.ACCESS_DENIED)
     
        for i in range(len(channel.messages)):
            msg = channel.messages[i]
            messageDetails.append({'id' : msg.id, 'duration': msg.duration, 'timestamp' : msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"), 'from': msg.sender})

        self.sendToWalkie(session.walkie, WALKIE_MESSAGE.LIST_MESSAGES,{'channel': channel.id, 'messages': messageDetails})
        

    def handleGetMessage(self, session, message):
        messageId = message.get("id")

        messageDetails = self._db.findMessage(messageId)
        if messageDetails is None:
            raise Exception(ERROR_CODES.UNKNOWN_VOICE_MESSAGE)
        channel = self._db.findChannel(messageDetails.channel)
        user = self._db.findUser(session.userName)
        if not channel.hasAccess(user):
            raise Exception(ERROR_CODES.ACCESS_DENIED)
        self.sendToWalkie(session.walkie, WALKIE_MESSAGE.GET_MESSAGE, {'id' : messageId, 'duration' : messageDetails.duration, 'emergency': messageDetails.isEmergency, 'payload': messageDetails.payload, 'timestamp' : messageDetails.timestamp.strftime("%Y-%m-%d %H:%M:%S")})

# Helper methods
    

    def ensureValidToken(self, token):
        if token is None:
            raise Exception(ERROR_CODES.INVALID_TOKEN)
        if not self._tpm.validateToken(token):
            raise Exception(ERROR_CODES.INVALID_TOKEN)

    def findSessionFromToken(self, token):
        for session in self._sessions:
            if session.token == token:
                return session
        return None

    def findSessionFromWalkie(self, walkie):
        for session in self._sessions:
            if session.walkie == walkie:
                return session
        return None

    
    def sendToAuthServer(self, message_type, message):
        message["command"] = message_type.value
        self.sendToMQTT(self.getAuthTopic(), message)

    
    def sendToMQTT(self, topic, payload):
        self._mqtt.publish(topic, json.dumps(payload))

    def getWalkieTopic(self, walkie):
        return f"{self._rootTopic}/walkie/{walkie}"

    def getAuthTopic(self):
        return f"{self._rootTopic}/auth_server"

    def sendToWalkie(self, walkie, message_type, message):
        message["command"] = message_type.value
        self.sendToMQTT(self.getWalkieTopic(walkie), message)


    def sendErrorResponse(self, type, walkie, error, details):
        if not isinstance(error, int): #Is not of instance ENUM
            error = error.value
        self.sendToMQTT(self.getWalkieTopic(walkie), {'error': error, 'command' : type, 'details': details})

    def ensureAuthenticated(self, session):
        if session is None or session.status != SESSION_STATUS.AUTHENTICATED:
            raise Exception(ERROR_CODES.UNAUTHORIZED)

    def ensureWalkieNotInUse(self, walkie):
        for session in self._sessions:
            if session.status == SESSION_STATUS.AUTHENTICATED and session.walkie == walkie:
                raise Exception(ERROR_CODES.WALKIE_IN_USE)

    def ensureUserNotLoggedIn(self, username):
        for session in self._sessions:
            if session.status == SESSION_STATUS.AUTHENTICATED and session.userName == username:
                raise Exception(ERROR_CODES.USER_ALREADY_LOGGED_IN)
    

    
    def createSession(self, walkie, user):
        session = Session(walkie, user, self)
        print("Session created, id: ", walkie)
        sessionMachine = stmpy.Machine(walkie, SessionStateMachineConfig["transitions"], session, SessionStateMachineConfig["states"])
        self._driver.add_machine(sessionMachine)
        self._sessions.append(session)
        return session
    
    def removeSession(self, session):
        self._sessions.remove(session)






