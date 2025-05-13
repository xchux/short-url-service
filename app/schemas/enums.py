from enum import Enum


class BlacklistReasonEnum(Enum):
    """
    Enum for the reasons a user may be blacklisted.
    """

    RATE_LIMIT = "rate_limit"
