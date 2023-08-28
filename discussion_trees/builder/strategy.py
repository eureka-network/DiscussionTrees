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
    StepStructure(),
    StepContent()
]


# Define ordering policy for the strategy
ORDERING_POLICY = OrderingPolicy.StepsFirst


class Strategy:
    def __init__(self, document_store: Stor, ordering_policy: OrderingPolicy=ORDERING_POLICY):
        self._document_store = document_store
        self._ordering_policy = ordering_policy

    def start_trajectory(self):
        trajectory = Trajectory()

        if self._ordering_policy == OrderingPolicy.StepsFirst:
            for step in STEPS:
                incomplete_documents = self._document_store.get_incompleted_documents_for_step(step.step_type)
                for document_id in incomplete_documents:
                    # call on step to form the operands to go into the trajectory from the units
                    pass
                print(f"Found {len(incomplete_documents)} incomplete documents for step {step.step_type}")
                print(f"Doc ids: {incomplete_documents}")
        else:
            raise NotImplementedError("Document first ordering policy not implemented yet")


