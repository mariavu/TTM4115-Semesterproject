class Database:
    def __init__(self):
        self._walkies = {}
        self._users = {}
        self._channels = {}
        self._roles = {}

    #Only need add/remove methods; we are esentially following the 'ActiveRecord'-pattern, except we never actually persist any data.

    def addUser(self, toAdd):
        self._users[toAdd.id] = toAdd
    
    def removeUser(self, toRemove):
        del self._users[toRemove.id]

    def addWalkie(self, toAdd):
        self._walkies[toAdd.id] = toAdd

    def existsWalkie(self, walkieId):
        for walkie in self._walkies:
            if walkie.id == walkieId:
                return True
        return False
    
    def removeWalkie(self, toRemove):
        del self.__walkies[toRemove.id]
    
    def addChannel(self, toAdd):
        self._channels[toAdd] = toAdd
    
    def removeChannel(self, toRemove):
        del self._channels[toRemove.id]
    
    def addRole(self, toAdd):
        self._roles[toAdd] = toAdd
    
    def removeRole(self, toRemove):
        del self._roles[roRemove.id]
        
    def getUsersCount(self):
       # return self._users.count()
        return len(self._users))

    def findChannel(self, channelId):
        return self._channels[channelId]