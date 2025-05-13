from enum import Enum, auto


class TimestampDefaultEnum(Enum):
    CURRENT_TIMESTAMP = auto()
    MAX = "2038-01-19 03:14:17"
    ZERO = "0"
