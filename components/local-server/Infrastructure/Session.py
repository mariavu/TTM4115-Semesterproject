import stmpy

class Session:
    def __init__(self):
        pass

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
    

def sendError(self):
    
    
    
