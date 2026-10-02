from enum import StrEnum, auto

class MessengerType(StrEnum):
    DISCORD = auto()
    STOAT= auto()

class PickModeType(StrEnum):
    RATING = auto()
    NO_TEAMS = auto()
    CAPTAINS = auto()
    RANDOM = auto()