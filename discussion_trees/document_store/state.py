"""Document state machine"""

from collections import namedtuple
from dataclasses import dataclass
import cbor2

from discussion_trees.graph_store import Graph
from discussion_trees.hasher import calculate_sha256


PREPOPULATION_QUERIES = {
    "incomplete_cleanup": {"template": "incomplete_step",
                           "parameters": {"step_type": "cleanup"},
                           "requires": ["session_id"],
                          },
    "incomplete_structure": {"template": "incomplete_step",
                             "parameters": {"step_type": "structure"},
                             "requires": ["session_id"],
                          },
    "incomplete_content": {"template": "incomplete_step",
                           "parameters": {"step_type": "content"},
                           "requires": ["session_id"],
                          },
    }


DOCUMENT_PREPOPULATION_TEMPLATES = {
    "incomplete_step": (
        "MATCH (sc:SessionController)-[:SESSION_FOR]->(d:Document) "
        "WHERE sc.session_document_id = $specific_session_id "
        "OPTIONAL MATCH (sc)-[:HAS_STEP]->(s:Step) "
        "WHERE s.type = $step_type AND (NOT EXISTS(s.completed) OR s.completed = false) "
        "RETURN d.identifier as document_id, s.identifier as step_id "
        ),
    }


TouchedStep = namedtuple('TouchedStep', ['identifier', 'type', 'session_document_id'])


@dataclass
class Action:
    """Action stores the execution of a skill in a step."""
    step_id: str
    trajectory_id: str
    run: int
    timestamp: int
    skill_description: str
    inputs: list # list of unit or action identifiers
    outputs: list # list of output from skill
    identifier: str = None
    # todo: add extra metadata, runtime, skill details, phase etc

    def __post_init__(self):
        assert all(isinstance(item, str) for item in self.inputs), "All items in 'inputs' must be strings."
        self.identifier = self.calculate_identifier()

    def calculate_identifier(self) -> str:
        """Return the identifier for the action."""
        serialized_data = cbor2.dumps({
            "trajectory_id": self.trajectory_id,
            "run": self.run,
            "timestamp": self.timestamp,
            "skill_description": self.skill_description,
            "inputs": self.inputs,
        })
        return calculate_sha256(serialized_data)

class Actions:
    def __init__(self,
                 graph: Graph,
                 document_identifier: str,
                 session_document_identifier: str):
        self._document_identifier = document_identifier
        self._session_document_identifier = session_document_identifier
        self._actions = {}
        self._reader = graph.new_reader()
        self._writer = graph.new_writer()
        self._graph = graph
        self._unstored_actions = []
        self._touched_steps = set()
        self._existing_steps = {} # steps that already exist in the database
        self._lookup_step_identifiers = {} # lookup table for step identifiers from step types
        self._flushed = True
        self._loaded = False

    def merge_actions_under_step(
            self,
            step_type: str,
            actions: list,
            autoFlush=True
        ):
        
        step_identifier = self.get_step_identifier(step_type)
        # steps from DB have a status field,
        # touching steps does not tell us about status so omit it here
        # note: use a named tuple because a set requires a hashable object
        self._touched_steps.add(TouchedStep(step_identifier, step_type, self._session_document_identifier))
        
        for action in actions:
            assert isinstance(action, Action), "Action must be an Action instance"
            assert action.step_id == step_identifier, f"Action {action.identifier} does not belong to step {step_identifier}"
            if action.identifier in self._actions:
                raise Exception(f"Action {action.identifier} already added to Actions")
            self._actions[action.identifier] = action
            self._unstored_actions.append(action.identifier)

        self._flushed = False
        if autoFlush:
            self.flush()

    def load_steps(self):
        """Load the steps for the session document."""
        if self._loaded:
            return
        
        steps = self._reader.get_state_for_session_documents(
            self._session_document_identifier,
            self._document_identifier,
        )
        for step in steps:
            step_identifier_calc = self.get_step_identifier(step["type"])
            assert step_identifier_calc == step["identifier"], f"Step identifier {step_identifier_calc} does not match {step['identifier']}"
            if step["identifier"] not in self._existing_steps:
                self._existing_steps[step["identifier"]] = step
            else:
                # todo: this is not a real error, but asserting for now that we're
                # not loading the same step twice
                raise Exception(f"Step {step['identifier']} already loaded")
        self._loaded = True

    def get_status(self):
        """Return the status of the session document."""
        # todo: for now the status on all steps is "incomplete, so simply return "incomplete"
        return "incomplete"

    def flush(self):
        """Flush the actions to the graph store."""
        if self._flushed:
            return
        
        # if we touched steps, we need to check if they exist in the database
        if self._touched_steps:
            if not self._existing_steps:
                # get existing steps from database
                # todo: we also query state of steps in document store, investigate duplication/deadcode
                steps = self._reader.get_state_for_session_documents(
                    self._session_document_identifier,
                    self._document_identifier,
                )
                for step in steps:
                    self._existing_steps[step["identifier"]] = step.deepcopy()
        
            # iterate over the named tuples in touched steps
            for touched_step in self._touched_steps:
                if touched_step.identifier not in self._existing_steps:
                    # if the step does not exist, we need to persist it in the database
                    self._writer.merge_step(
                        self._session_document_identifier,
                        self._document_identifier,
                        touched_step.identifier,
                        touched_step.type,
                        "incomplete",
                    )
                    # and write to memory in existing steps
                    self._existing_steps[touched_step.identifier] = {
                        "identifier": touched_step.identifier,
                        "type": touched_step.type,
                        "status": "incomplete",
                    }
                else:
                    print(f"Step {touched_step.identifier} already exists in database")
            
        # flush actions
        for unstored_action_id in self._unstored_actions:
            action = self._actions[unstored_action_id]
            self._writer.merge_action(
                step_id=action.step_id,
                action_id=action.identifier,
                trajectory_id=action.trajectory_id,
                run=action.run,
                timestamp=action.timestamp,
                skill_description=action.skill_description,
                inputs=action.inputs,
                outputs=action.outputs,
            )
        self._touched_steps.clear()
        self._unstored_actions = []
        self._flushed = True

    def get_step_identifier(self, step_type: str):
        """Return the identifier for the step."""
        # calculate step identifier from step type,
        # as we want to enforce a single step per type per session
        if step_type in self._lookup_step_identifiers:
            step_identifier = self._lookup_step_identifiers[step_type]
        else:
            step_digest = calculate_sha256(
                cbor2.dumps({
                    "session_document_id": self._session_document_identifier,
                    "step_type": step_type,
                }))
            step_identifier = f"{self._session_document_identifier}-{step_digest[:8]}"
            self._lookup_step_identifiers[step_type] = step_identifier
        return step_identifier


class DocumentState:

    def __init__(self, session_document_id: str):
        # query library matches a query key to query templates and initial parameters
        # for retrieving and updating document state
        self._query_library = {}
        self._session_document_id = session_document_id
        self._prepopulate_manual_steps()

    def _prepopulate_manual_steps(self):
        # gather all possible required parameters
        required_parameters = {"session_id": self._session_id}

        for query_key, query in PREPOPULATION_QUERIES.items():
            # dynamically set addional required parameters
            dynamic_parameters = {}
            for required_parameter in query["requires"]:
                dynamic_parameters[required_parameter] = required_parameters[required_parameter]
            # set parameters for the query first with the prepopulation parameters,
            # then with the dynamic parameters
            set_parameters = query["parameters"].copy()
            if dynamic_parameters:
                set_parameters.update(dynamic_parameters)
            self._query_library[query_key] = {
                "template": DOCUMENT_PREPOPULATION_TEMPLATES[query["template"]],
                "parameters": set_parameters
            }

    # def _formulate_query(self, transaction, query_key: str, specific_parameters: dict):
    #     query = self._query_library[query_key]["template"]
        
    #     # make a local copy of the parameters
    #     parameters = self._query_library.get(query_key, {}).get("parameters", {}).copy()
    #     if not parameters:
    #         raise Exception(f"Query key {query_key} not found in query library")
    #     parameters.update({"specific_session_id": self._session_id})

    #     # update parameters with specific parameters
    #     if specific_parameters:
    #         parameters.update(specific_parameters)

    #     # continue here TODO
    #     result = transaction.run(query, parameters)
    #     return list(result)
