
from enum import Enum


class ERROR_CODES(Enum):
    SESSION_EXISTS = 0,
    INVALID_USERNAME_OR_PASSWORD = 1,
    UNKNOWN_MESSAGE_TYPE = 2,
    WALKIE_IN_USE = 3,
    USER_ALREADY_LOGGED_IN = 4,
    UNAUTHORIZED = 5,
    UNKNOWN_CHANNEL = 6,
    USERNAME_TAKEN = 7
    INVALID_TOKN = 8



class AUTH_SERVER_MESSAGE(Enum):
    LOGIN = 100
    REGISTER = 101

class WALKIE_MESSAGE(Enum):
    LOGIN = 0
    REGISTER = 1
    LIST_MESSAGES = 2
    JOIN_CHANNEL = 3
    SEND_MESSAGE = 4
    