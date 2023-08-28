from enum import Enum, auto


class StepContinuations(Enum):
    CONTINUE = auto() # continue for all incompleted documents
    REDO = auto() # redo for all documents
    SKIP = auto() # skip for all incompleted documents


class Step:
    def __init__(
            self,
            type,
            continuation: StepContinuations=StepContinuations.CONTINUE
        ):
        self._type = type
        self._continuation = continuation

    def get_all_incompleted_documents(self):
        # default behaviour
        pass

    def execute(self):
        # default behaviour
        pass

    @property
    def step_type(self):
        return self._type


class StepCleanup(Step):

    def __init__(self):
        super().__init__("cleanup", StepContinuations.CONTINUE)

    def execute(self):
        print("Hello, cleanup !")
        pass


class StepStructure(Step):
    def __init__(self):
        super().__init__("structure", StepContinuations.CONTINUE)

    def execute(self):
        print("Hello, structure !")
        pass


class StepContent(Step):
    def __init__(self):
        super().__init__("content", StepContinuations.CONTINUE)

    def execute(self):
        print("Hello, content !")
        pass