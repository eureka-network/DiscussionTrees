from enum import Enum


class ContextClassifier(Enum):
    SUPPORTS = 1
    AGAINST = 2
    UNDETERMINED = 3

    def from_message(cls, message: str):
        match message.lower():
            case "supports" | "support":
                return cls.SUPPORTS
            case "against":
                return cls.AGAINST
            case "undetermined":
                return cls.UNDETERMINED
