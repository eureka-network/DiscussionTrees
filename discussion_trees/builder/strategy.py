import copy
from enum import Enum, auto
import cbor2

from discussion_trees.document_store import Store
from discussion_trees.hasher import calculate_sha256

from .steps import StepContinuations, Step, StepCleanup, StepStructure, StepContentOnePoint, StepEntitiesOnePoint, StepEventsOnePoint
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
    # StepCleanup(),
    # StepStructure(),
    StepContentOnePoint(),
    # StepEntitiesOnePoint(),
    # StepEventsOnePoint()
]


# Define ordering policy for the strategy
ORDERING_POLICY = OrderingPolicy.StepsFirst


class Strategy:
    def __init__(self, document_store: Store, ordering_policy: OrderingPolicy=ORDERING_POLICY):
        self._document_store = document_store
        self._ordering_policy = ordering_policy
        self._trajectories = {}

    def construct_trajectory(self, trajectory_id: str):
        """Construct a trajectory for the strategy and configuration."""
        if not trajectory_id:
            raise ValueError("Trajectory id must be specified")
        if trajectory_id in self._trajectories:
            raise ValueError(f"Trajectory {trajectory_id} already constructed")
        
        trajectory = Trajectory()

        if self._ordering_policy == OrderingPolicy.StepsFirst:
            for step in STEPS:
                print(f"Building trajectory for step {step.step_type}")
                incomplete_documents = self._document_store.get_incompleted_document_ids_for_step(step.step_type)
                for document_id in incomplete_documents:
                    print(f"Adding phase for document {document_id} to trajectory")
                    # get all units for the document
                    # todo: step continuations are not implemented; simply rerun over all units
                    document = self._document_store.get_document(document_id)
                    number_of_units = document.get_number_of_stored_units()
                    # call on step to form the operands to go into the trajectory from the units
                    # for now, simply form a group list from the unit positions
                    group_list = step.build_group_list_from_unit_positions(range(1, number_of_units + 1))
                    # phase id is not written to DB, but we might write it to file later,
                    # so already work with unique identifier (todo: should we include session_id?)
                    phase_id = calculate_sha256(
                        cbor2.dumps({
                            "step_type": step.step_type,
                            "document_id": document_id,
                        }))[:8]
                    # add the phase to the trajectory
                    # note: steps are effectively static, but still deepcopy for later
                    #       if they become stateful
                    trajectory.add_phase(
                        phase_id=phase_id,
                        document_id=document_id,
                        step=copy.deepcopy(step),
                        groups=group_list,
                    )
                    print(f"Added phase for document {document_id} to trajectory with {len(group_list)} groups of order {group_list._order}")
        else:
            raise NotImplementedError("Document first ordering policy not implemented yet")

        # hold on to trajectory
        self._trajectories[trajectory_id] = trajectory

        return trajectory

