from .neo4j_reader import Neo4jReader
from .context_agent import ContextAgent
from .context_classifier import ContextClassifier


def group_one_template_message(message: str) -> str:
    return f"""Is this reply post: 
            
            ---
                {message}
            ---         
    
            in support or against the original post, 
                        or undetermined? Only reply with either ["SUPPORT", "AGAINST", "UNDETERMINED"]?
            """


def group_two_template_message(message_1: str, message_2: str) -> str:
    return f"""
        Is this reply post:

        ---
            {message_2}
        ---

        in support, against or undetermined regarding the previous post: 

        ---
            {message_1}
        ---

        Only reply with either ["SUPPORT", "AGAINST", "UNDETERMINED"]?
    """


def group_level_template_message(*args) -> str:
    match len(args):
        case 1:
            message = args[0]
            group_one_template_message(message)
        case 2:
            message_1 = args[0]
            message_2 = args[1]
            group_two_template_message(message_1, message_2)
        case _:
            raise ValueError(
                "Invalid number of *args, currently only supported either 1 or 2.")


class Frame:
    def __init__(self, height: int, level: int, group: list[str], agent: ContextAgent):
        self.height = height
        if level in [1, 2] & len(group) == level:
            self._level = level
            self._group = group
        else:
            raise ValueError(
                "Invalid level, supported values are either 1 or 2, for now.")
        self._agent = agent

    def execute_group(self) -> ContextClassifier:
        """Executes a `ContextAgent` on a specific group over some level. The agent
            is responsible for classifying the given group context at the current level"""

        message = group_level_template_message(
            self._group[0]) if self._level == 1 else group_level_template_message(self._group[0], self._group[1])
