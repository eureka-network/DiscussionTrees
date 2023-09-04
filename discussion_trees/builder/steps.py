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

    @property
    def step_type(self):
        return self._type


class StepCleanup(Step):

    def __init__(self):
        super().__init__("cleanup", StepContinuations.CONTINUE)


class StepStructure(Step):
    def __init__(self):
        super().__init__("structure", StepContinuations.CONTINUE)


class StepOnePoint(Step):
    def __init__(
            self,
            type,
            continuation: StepContinuations=StepContinuations.CONTINUE
        ):
        super().__init__(type, continuation)
        
    # note: steps are largely static atm, but likely they might not remain so
    def build_group_list_from_unit_positions(self, unit_positions):
        group_list = GroupList(1)
        for position in unit_positions:
            # simple one-point group
            group = Group(1, [position])
            group_list.add_group(group)
        return group_list


class StepContentOnePoint(StepOnePoint):
    def __init__(self):
        super().__init__("contentOnePointJSON", StepContinuations.CONTINUE)


class StepEntitiesOnePoint(StepOnePoint):
    def __init__(self):
        super().__init__("entitiesOnePointJSON", StepContinuations.CONTINUE)


class StepEventsOnePoint(StepOnePoint):
    def __init__(self):
        super().__init__("eventsOnePoint", StepContinuations.CONTINUE)
