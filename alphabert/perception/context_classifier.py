from enum import Enum


class ContextClassifier(Enum):
    SUPPORTS = 1
    AGAINST = 2
    UNDETERMINED = 3

    @classmethod
    def from_message(cls, message: str):
        match message.lower():
            case "supports" | "support":
                return cls.SUPPORTS
            case "against":
                return cls.AGAINST
            case "undetermined":
                return cls.UNDETERMINED
            case _:
                raise ValueError(
                    "Invalid message, should be of the form ['SUPPORT', 'AGAINST', 'UNDETERMINED']")

    def to_string(self) -> str:
        match self:
            case self.SUPPORTS:
                return "SUPPORTS"
            case self.AGAINST:
                return "AGAINST"
            case self.UNDETERMINED:
                return "UNDETERMINED"
            case _:
                raise ValueError("Invalid state")
