class Database:
    def __init__(self):
        self._users = {}
        self._channels = {}
        self._roles = {}
        self._messages = {}


    #Only need add/remove methods; we are esentially following the 'ActiveRecord'-pattern, except we never actually persist any data.

    def addUser(self, toAdd):
        self._users[toAdd.id] = toAdd
    
    def removeUser(self, toRemove):
        del self._users[toRemove.id]
    
    def addChannel(self, toAdd):
        self._channels[toAdd.id] = toAdd
    
    def removeChannel(self, toRemove):
        del self._channels[toRemove.id]
    
    def addRole(self, toAdd):
        self._roles[toAdd.id] = toAdd
    
    def removeRole(self, toRemove):
        del self._roles[roRemove.id]
        
    def getUsersCount(self):
       # return self._users.count()
        return len(self._users)

    def findChannel(self, channelId):
        if not channelId in self._channels:
            return None
        return self._channels[channelId]

    def findUser(self, username):
        for user in self._users.values():
            if user.username == username:
                return user
        return None
    def addMessage(self, toAdd):
        self._messages[toAdd.id] = toAdd

    def findMessage(self, messageId):
        if not messageId in self._messages:
            return None
        return self._messages[messageId]

    def findAllChannels(self):
        return self._channels