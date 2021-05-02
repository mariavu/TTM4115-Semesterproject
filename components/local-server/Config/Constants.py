
from enum import Enum


class ERROR_CODES(Enum):
    SESSION_EXISTS = 0
    INVALID_USER_CREDENTIALS = 1 #GUI
    UNKNOWN_MESSAGE_TYPE = 2 
    WALKIE_IN_USE = 3
    USER_ALREADY_LOGGED_IN = 4 #GUI
    UNAUTHORIZED = 5
    UNKNOWN_CHANNEL = 6
    USERNAME_TAKEN = 7 # GUI 
    INVALID_TOKEN = 8
    NOT_PARTICIPATING_IN_CHANNEL = 9 # GUI (If LeaveChannel is sent when user is not participating in channel)
    ACCESS_DENIED = 10
    UNKNOWN_VOICE_MESSAGE = 11
    ALREADY_PARTICIPATING_IN_CHANNEL = 12 # GUI (If JoinChannel is sent when user is already participating in channel)
    INVALID_SERVER = 13
    INVALID_WALKIE = 14


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
    GET_MESSAGE = 6
    INCOMING_MESSAGE = 7
    LIST_CHANNELS = 8
    SIGN_OUT = 9    

