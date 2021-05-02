class Channel:

    def __init__(self, id, messages):
        self._id = id
        if messages is None:
            messages = []
        self._messages = messages
        

    @property
    def id(self):
        return self._id
  
    @property
    def messages(self):
        return self._messages
    
    def publishMessage(self, newMessage):
        if newMessage.duration > 60:
            return -1
        user = newMessage.sender
        lastMinuteCount = 0
        for msg in self._messages:
            if msg.sender == user and (newMessage.timestamp - msg.timestamp).minute < 1:
                lastMinuteCount += 1
                if lastMinuteCount == 10: #No need to search further
                    break 
        
        if lastMinuteCount == 10:
            return 0
        self._messages.append(newMessage)
        return 1

class GroupChannel(Channel): #This class inherits from Channel and extends its functionality.
    def __init__(self, id, messages, name, roles):
        Channel.__init__(self ,id, messages)
        self._name = name
        self._roles = roles
    
    @property
    def name(self):
        return self._name
    @property
    def roles(self):
        return self._roles
    
    def hasAccess(self, user):
        for role in user.roles:
            if role in self._roles:
                return True
        return False
    