class Channel:

    def __init__(self, id, messages):
        self._id = id
        self._messages = messages
        

    @property
    def id(self):
        return self._id
  
    @property
    def messages(self):
        return self._messages
    
    #Id
    #Name
    #Roles:
    #Department
    #Participants: