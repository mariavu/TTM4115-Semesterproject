from Channel import Channel

class GroupChannel(Channel): #This class inherits from Channel and extends its functionality.
    def __init__(self, id, messages, name, roles, participants):
        Channel.__init__(id, messages)
        self._name = name
        self._roles = roles
        self._participants = participants
    
    @property
    def name(self):
        return self._id
    @property
    def roles(self):
        return self._roles
    @property
    def participants(self):
        return self._participants
    
    def addParticipant(self, user):
        if(user.id in self._participants):
            raise Exception("Cannot add participant; already participating")
    
        if(self._roles.count() == 0): #Anybody can participate; no specific roles.
            self._participants.append(user.id) 
            return

        for role in user.roles:
            if not role in self._roles:
                continue
            self._participants.append(user.id)
            return
        raise Exception("Participant does not have a role with permission.")

    def hasParticipant(self, userId):
        return userId in self._participants