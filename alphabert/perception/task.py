from enum import Enum


class WorldBuildingTask(Enum):
    """A world building task class. Its purpose is to provide contextual tasks
        (or more precisely, questions in a discourse forum or document setting) to enhance
        the current understanding of the corpus being analyzed (being a discourse
        forum or a lengthy document). 

        For now, we use a simple hardcoded instruction set of [SUPPORT, AGAINST, UNDETERMINED].
    """
    SUPPORT = 1
    AGAINST = 2
    UNDETERMINED = 3

    def set_message(self, message: str):
        self._message = message

    @property
    def message(self) -> str:
        return self._message

    def get_prompt_message(self) -> str:
        match self:
            case WorldBuildingTask.AGREE:
                if self._message is None:
                    return "Does current post agree with previous post ?"
                else:
                    return f"Does current post agree with assertion: {self._message}"
            case WorldBuildingTask.DISAGREE:
                if self._message is None:
                    return "Does current post disagree with previous post ?"
                else:
                    return f"Does current post disagree with assertion: {self._message}"
            case WorldBuildingTask.NEUTRAL:
                if self._message is None:
                    return "Is current post neutral with respect to previous post ?"
                else:
                    return "Is current post neutral with respect to assertion: {self._message}"
            case _:
                raise ValueError("Invalid opinion value.")
