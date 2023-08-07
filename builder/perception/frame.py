from .classifier_agent import ClassifierAgent, ContextClassifier


class Frame:
    def __init__(self, height: int, level: int, group: str, agent: ClassifierAgent):
        self.height = height
        self.level = level
        self.group = group
        self._agent = agent

    def execute_input(self, input: str) -> ContextClassifier:
        """Executes a `ContextAgent` on a specific group over some level. The agent
            is responsible for classifying the given group context at the current level"""
        return self._agent.classify_context(input, self.group)
