import paho.mqtt.client as mqtt
import stmpy
import logging
import json

from threading import Thread


class Controller:
    def onConnect(self):
        pass

    def handleJoinChannel(self, message):
        pass

    def handleRegister(self, message):
        pass

    def onMessage(self, message):
        if(message.type in self._messageHandlers):
            self._messageHandlers.get(message.type)(message)
        else:
            raise Exception("Unknown message type")
    

        #These may either be messages from auth server or walkie;
        #TODO Implement logic for handling incoming messages.
        pass

    def registerWithAuthServer(self):
        #TODO send MQTT message to establish connection with authentication server and sync.
        pass

    def start(self):
        self._mqtt.connect(self._host, self._port)
        self._mqtt.subscribe(f"{self._rootTopic}/{self._id}") #Input topic
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
        self._sessions = []
        self._messageHandlers = {'joinChannel' : self.handleJoinChannel} #This dictionary will contain all message_type => message_handler()

  

