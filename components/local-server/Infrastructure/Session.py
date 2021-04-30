from enum import Enum

class SESSION_STATUS(Enum):
    IDLE = 0
    PENDING_REGISTRATION = 1
    PENDING_LOGIN = 2
    AUTHENTICATED = 3

class Session:

    def __init__(self, walkie, userName, controller):
        self._walkie = walkie
        self._userName = userName
        self._authenticated = False
        self._joinedChannels = {}
        self._status = SESSION_STATUS.IDLE
        self._controller = controller


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
        print("Setting token: ", token)
        self._token = token
        self._status = SESSION_STATUS.AUTHENTICATED
    def destroy(self):
        print("Went into final state")
        self._controller.removeSession(self)
    def addChannel(self, channel):
        self._joinedChannels[channel.id] = channel
    def removeChannel(self, channel):
        del self._joinedChannels[channel.id]

    def beginLogin(self):
        self._status = SESSION_STATUS.PENDING_LOGIN

    def beginRegister(self):
        self._status = SESSION_STATUS.PENDING_REGISTRATION


        """
debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

"""
"""
#states:
    #idle
    #PendingReg
    #PendingAuth
    #Authenticated
    #Final

    #Triggers:
    #joinedChannel
    #leftChannel
    #authBegin
    #regBegin
    #authSuccessful
    #authFail
    #regSuccess
    #regFail
"""
#States
idle = {
    'name': 'Idle'
}

pendingReg = {
    'name': 'pendingReg',
    'entry': 'start_timer("t",5000);beginRegister',
}

pendingAuth = {
    'name': 'pendingAuth',
    'entry': 'start_timer("t",5000);beginLogin'
}

authenticated = {
    'name': 'authenticated',
    'entry': 'stop_timer("t")'
}

final = {
    'name': 'final'
}

#Transitions

t11 = {
    'source': 'initial',
    'target': 'idle'
}
t0 = {
    'source': 'idle',
    'target': 'pendingReg',
    'trigger': 'regBegin' 
}

t1 = {
    'source': 'idle',
    'target': 'pendingAuth',
    'trigger': 'authBegin'
}
t2 = {
    'source': 'pendingReg',
    'target': 'final',
    'trigger': 'regSuccess',
    'effect' : 'destroy;stop_timer("t")'
}
t3 = {
    'source': 'pendingAuth',
    'target': 'authenticated',
    'trigger': 'authSuccess',
    'effect' : 'setToken(*)'
}
t4 = {
    'source': 'authenticated',
    'target': 'authenticated',
    'trigger': 'joinedChannel',
    'effect' : 'addChannel(*)'
}
t5 = {
    'source': 'authenticated',
    'target': 'authenticated',
    'trigger': 'leftChannel',
    'effect' : 'removeChannel(*)'
}
t6 = {
    'source': 'authenticated',
    'target': 'final',
    'trigger': 'signOut',
    'effect': 'destroy'
}
t7 = {
    'source': 'pendingAuth',
    'target': 'final',
    'trigger': 't',
    'effect': 'destroy'
}
t8 = {
    'source': 'pendingReg',
    'target': 'final',
    'trigger': 't',
    'effect': 'destroy'
}

t9 = {
    'source': 'pendingReg',
    'target': 'final',
    'trigger': 'regFail',
    'effect' : 'stop_timer("t");destroy'
}
t10 = {
    'source': 'pendingAuth',
    'target': 'final',
    'trigger': 'authFail',
    'effect': 'stop_timer("t");destroy'
}

SessionStateMachineConfig = {
    'states': [idle, pendingReg, pendingAuth, authenticated, final],
    'transitions' : [t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11]
}