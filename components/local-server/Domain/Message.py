class Message:

    def __init__(self, id, sender, to, length, contents, timestamp):
        self._id = id
        self._sender = sender
        self._to = to
        self._length = length
        self._contents = contents
        self._timestamp = timestamp
    
    @property
    def id(self):
        return self._id
    
    @property
    def sender(self):
        return self._sender
    
    @property
    def to(self):
        return self._to
    @property
    def length(self):
        return self._length
    @property
    def contents(self):
        return self._contents
    @property
    def timestamp(self):
        return self._timestamp
    
    #from <UserId>
    #to <ChannelId>
    #length
    #contents