"""Build a trajectory for all the tasks to be done in a session.
    Phases are executed in order, while tasks inside a phase can be
    executed in any order.
    Later: add decision points to call back to strategy about what to do next."""

import time
import secrets
import cbor2

from discussion_trees.hasher import calculate_sha256
from discussion_trees.document_store import Document, UnitData
from .group import GroupList
from .steps import Step

class Trajectory:
    def __init__(self, trajectory_id: str):
        self._phases_order = []
        self._current_phase = None
        self._phases = {}
        self._trajectory_id = trajectory_id
        # generate unqiue identifiers for different runs of this trajectory
        self._runs = [
            # first run added by default
            self.generate_run_identifier(1),
        ]

    def add_phase(self,
                  phase_id: str,
                  document_id: str,
                  step: Step,
                  groups: GroupList):
        """Add a phase to the trajectory.
           A phase takes a specific prompt from a step 
           and a list of groups of units over which to run the prompt."""
        assert isinstance(step, Step), "Step must be a Step instance"
        assert isinstance(groups, GroupList), "Groups must be a GroupList instance"
        assert phase_id not in self._phases, f"Phase {phase_id} already added to trajectory"
        self._phases_order.append(phase_id)
        self._phases[phase_id] = {
            "document_id": document_id,
            "step": step,
            "groups": groups,
        }

    def get_run_identifier(self, run: int):
        assert run > 0, "Run must be a positive integer"
        assert run <= len(self._runs), f"Run {run} not yet generated"
        return self._runs[run - 1]

    def __iter__(self):
        """Iterate over the phases in the trajectory."""
        for phase_id in self._phases_order:
            yield self._phases[phase_id]

    def generate_run_identifier(self, run: int):
        timestamp = str(int(time.time())) # seconds since epoch
        salt = secrets.token_hex(8) # generate random 8 byte hex string
        digest = calculate_sha256(
            cbor2.dumps({
                "trajectory_id": self._trajectory_id,
                "run": run,
                "timestamp": timestamp,
                "salt": salt,
            }))
        return f"{self._trajectory_id}-{run}-{digest[:8]}"
