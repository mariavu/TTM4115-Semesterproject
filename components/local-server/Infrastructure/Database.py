class Database:
    def __init__(self):
        self._walkies = []
        self._users = []
        self._channels = []
        self._roles = []

    #Only need add/remove methods; we are esentially following the 'ActiveRecord'-pattern, except we never actually persist any data.

    def addUser(self, toAdd):
        self._users.append(toAdd)
    
    def removeUser(self, toRemove):
        self._users.remove(toRemove)

    def addWalkie(self, toAdd):
        self._walkies.append(toAdd)
    
    def removeWalkie(self, toRemove):
        self._walkies.remove(toRemove)
    
    def addChannel(self, toAdd):
        self._channels.append(toAdd)
    
    def removeChannel(self, toRemove):
        self._channels.remove(toRemove)
    
    def addRole(self, toAdd):
        self._roles.append(toAdd)
    
    def removeRole(self, toAdd):
        self._roles.remove(toAdd)
        
    