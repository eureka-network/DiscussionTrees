from .neo4j_reader import Neo4jReader
from .context_agent import ContextAgent
from .context_classifier import ContextClassifier
from langchain import PromptTemplate


GROUP_ONE_TEMPLATE_PROMPT = """Is this reply post: 
            
            ---
                {message}
            ---         
    
            in support or against the original post, 
                        or undetermined? Only reply with either ["SUPPORT", "AGAINST", "UNDETERMINED"]?
            """


GROUP_TWO_TEMPLATE_PROMPT = """
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


class Frame:
    _internal_message = {1: GROUP_ONE_TEMPLATE_PROMPT,
                         2: GROUP_TWO_TEMPLATE_PROMPT}

    def __init__(self, height: int, level: int, group: list[str], agent: ContextAgent):
        self.height = height
        if level in [1, 2] & len(group) == level:
            self._level = level
            self._group = group
        else:
            raise ValueError(
                "Invalid level, supported values are either 1 or 2, for now.")
        self._agent = agent

    def _generate_prompt(self) -> str:
        prompt_message = self._internal_message[self._level]
        prompt = PromptTemplate(prompt_message)
        if self._level == 1:
            return prompt.format(message=self._group[0])
        else:
            # check validity: at this point, we are guaranteed from the initialization
            # logic that we can't have level != len(group) and len must be either [1, 2]
            return prompt.format(message_1=self._group[0], message_2=self._group[1])

    def execute_group(self) -> ContextClassifier:
        """Executes a `ContextAgent` on a specific group over some level. The agent
            is responsible for classifying the given group context at the current level"""

        prompt = self._generate_prompt()

        classification_class = self._agent.classify_context(prompt)
        return classification_class
