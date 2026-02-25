from enum import Enum


class EventType(str, Enum):
    ENROLL = "ENROLL"
    VERIFY = "VERIFY"
    LOCK_CMD = "LOCK_CMD"
    ERROR = "ERROR"
    INFO = "INFO"