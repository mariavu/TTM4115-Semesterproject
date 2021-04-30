
from enum import Enum


class ERROR_CODES(Enum):
    SESSION_EXISTS = 0
    INVALID_USERNAME_OR_PASSWORD = 1
    UNKNOWN_MESSAGE_TYPE = 2
    WALKIE_IN_USE = 3
    USER_ALREADY_LOGGED_IN = 4
    UNAUTHORIZED = 5
    UNKNOWN_CHANNEL = 6
    USERNAME_TAKEN = 7
    INVALID_TOKEN = 8
    NOT_PARTICIPATING_IN_CHANNEL = 9
    ACCESS_DENIED = 10
    #INVALID_SERVER = 11
    #INVALID_WALKIE = 12
    #Er dette greit??? Man sjekker om authentication server har den serveren eller walkien som prøver å logge inn en bruker er i databasen


class AUTH_SERVER_MESSAGE(Enum):
    LOGIN = 100
    REGISTER = 101

class WALKIE_MESSAGE(Enum):
    LOGIN = 0
    REGISTER = 1
    LIST_MESSAGES = 2
    JOIN_CHANNEL = 3
    SEND_MESSAGE = 4
    LEAVE_CHANNEL = 5
    
