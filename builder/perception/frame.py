from .classifier_agent import ClassifierAgent


class Frame:
    def __init__(self, height: int, level: int, group: str):
        self.height = height
        self.level = level
        self.group = group
        self._agent = ClassifierAgent()

    def execute_input(self, input: str):
        print("continue here")
