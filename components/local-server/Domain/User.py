class User:

    def __init__(self, id, username, name, roles,newMessages):
        self._id = id
        self._username = username
        self._name = name
        self._newMesages = newMessages
        self._roles = roles

    @property
    def id(self):
        return self._id
    @property
    def username(self):
        return self._username
    @property
    def name(self):
        return self._name
    @property
    def newMessages(self):
        return self._newMesages
    @property
    def roles(self):
        return self._roles
        
    @name.setter
    def name(self, value):
        self._name = value