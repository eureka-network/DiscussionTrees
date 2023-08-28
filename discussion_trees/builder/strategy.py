from enum import Enum, auto
from .steps import StepContinuations, Step, StepCleanup, StepStructure, StepContent
from discussion_trees.document_store import Store
from .trajectory import Trajectory

# A strategy forms a dynamic trajectory given the steps
# and the state of the knowledge graph


# Define ordering policy for the strategy
# whether to execute all steps for each document first
# or whether to first execute each step for all documents
class OrderingPolicy(Enum):
    DocumentFirst = auto() # execute all steps for each document
    StepsFirst = auto() # execute for each step all documents


# Define steps for the strategy
STEPS = [
    StepCleanup(),
    #StepStructure(),
    #StepContent()
]


# Define ordering policy for the strategy
ORDERING_POLICY = OrderingPolicy.StepsFirst


class Strategy:
    def __init__(self, document_store: Store):
        self._document_store = document_store

    def start_trajectory(self):
        trajectory = Trajectory()

        for step in STEPS:
            step_continuations = step.execute(self._graph)
            trajectory.add_step_continuations(step_continuations)
        pass

