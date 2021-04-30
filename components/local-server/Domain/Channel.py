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
        self._messages.append(newMessage)
    
    #Id
    #Name
    #Roles:
    #Department
    #Participants:

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
    