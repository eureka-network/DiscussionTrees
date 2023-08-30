from enum import Enum, auto

from .group import GroupList, Group

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

    def build_group_list_from_unit_positions(self, units):
        raise NotImplementedError("Step must implement build_group_list_from_units")

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


class StepContentOnePoint(Step):
    def __init__(self):
        super().__init__("content", StepContinuations.CONTINUE)

    def build_group_list_from_unit_positions(self, unit_positions):
        group_list = GroupList(1)
        for position in unit_positions:
            # simple one-point group
            group = Group(1, [position])
            group_list.add_group(group)
        return group_list


    def execute(self):
        print("Hello, content !")
        pass