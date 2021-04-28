import stmpy
from enum import Enum

class SESSION_STATUS(Enum):
    PENDING_REGISTRATION = 0
    PENDING_LOGIN = 1
    AUTHENTICATED = 2
    REGISTERED = 3

class Session:
    #Walkie
    #User
    #JoinedChannels
    #Authenticated

    def __init__(self, walkie, userName, initialStatus):
        self._walkie = walkie
        self._userName = userName
        self._authenticated = False
        self._joinedChannels = {}
        self._status = initialStatus


    @property
    def walkie(self):
        return self._walkie
    @property
    def userName(self):
        return self._userName
    @property
    def status(self):
        return self._status
    @property
    def joinedChannels(self):
        return self._joinedChannels

    @property
    def token(self):
        return self._token

    def setToken(self, token):
        self._token = token
        self._status = SESSION_STATUS.AUTHENTICATED
"""
#states:
    #idle
    #validation

#transitions:
    #response / handleResponse()
    #notValis / sendError()
    #valid / sendMessage()
    #request / go to state validating

#States
validating = {
    'name': 'validating',
    'entry': 'validate'
}

#Transitions

t0 = {
    'source': 'initial',
    'target': 'validating',
    'trigger': 'request' 
}

t1 = {
    'source': 'validating',
    'target': 'idle',
    'trigger': 'notValid',
    'effect': 'sendError'
}

t2 = {
    'source': 'validating',
    'target': 'idle',
    'trigger': 'valid',
    'effect': 'sendMessage'
}

t3 = {
    'source': 'idle',
    'target': 'idle',
    'trigger': 'response',
    'effect': 'handleResponse'
}

self.stm = stmpy.Machine(name=name, states=[validating], transitions=[t0, t1, t2, t3], obj=self)


#functions
    #handleResponse()
    #sendError()
    #sendMessage()
    #validate()


def validate(self):
    #TODO implment logic to validate command
    return result
   
def handleResponse(self, result):
    if result == False:
        #sendError()
    elif result == True:
        #sendMessage()


def sendMessage(self):
   pass 

def sendError(self):
    pass
    
"""