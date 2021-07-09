from enum import Enum


class ActivityEventStatusType(Enum):
    START = 'START'
    END = 'END'
    INPROGRESS = 'INPROGRESS'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'