class Message:

    def __init__(self, id, sender, channel, duration, isEmergency, payload, timestamp):
        self._id = id
        self._sender = sender
        self._channel = channel
        self._duration = duration
        self._payload = payload
        self._timestamp = timestamp
        self._emergency = isEmergency
    
    @property
    def id(self):
        return self._id
    
    @property
    def sender(self):
        return self._sender
    
    @property
    def channel(self):
        return self._channel
    @property
    def duration(self):
        return self._duration
    @property
    def payload(self):
        return self._payload
    @property
    def timestamp(self):
        return self._timestamp
    @property
    def isEmergency(self):
        return self._emergency