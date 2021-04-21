class Role:

    def __init__(self, id, name):
        self._id = id
        self._name = name

    @property
    def id(self):
        return self._id
    @property
    def name(self):
        return self._name
 
    @name.setter
    def name(self, val):
        self._name = val

    