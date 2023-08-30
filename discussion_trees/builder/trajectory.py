"""Build a trajectory for all the tasks to be done in a session.
    Phases are executed in order, while tasks inside a phase can be
    executed in any order.
    Later: add decision points to call back to strategy about what to do next."""

from discussion_trees.document_store import Document, UnitData
from .group import GroupList

class Trajectory:
    def __init__(self):
        self._phases_order = []
        self._current_phase = None
        self._phases = {}

    def add_phase(self,
                  phase_id: str,
                  document_id: str,
                  step: str,
                  groups: GroupList):
        """Add a phase to the trajectory.
           A phase takes a specific prompt from a step 
           and a list of groups of units over which to run the prompt."""
        assert isinstance(groups, GroupList), "Groups must be a GroupList instance"
        assert phase_id not in self._phases, f"Phase {phase_id} already added to trajectory"
        self._phases_order.append(phase_id)
        self._phases[phase_id] = {
            "document_id": document_id,
            "step": step,
            "groups": groups,
        }

