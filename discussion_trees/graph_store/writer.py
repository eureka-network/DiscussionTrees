"""
Writer class for neo4j DB.
"""

import json
from neo4j import GraphDatabase

from discussion_trees.hasher import calculate_sha256

from .connection import ConnectionSingleton


class Writer:

    ADD_DOCUMENT_TEMPLATE = """
        MERGE (d:Document {identifier: $document_id})
        SET d.name = $name, d.sha256 = $sha256
        """

    ADD_UNIT_TEMPLATE = """
        MERGE (u:Unit {identifier: $unit_id})
        SET u.document_id = $document_id,
            u.position = $position,
            u.content = $content,
            u.digest = $digest
        WITH u
        MATCH (d:Document {identifier: $document_id})
        MERGE (u)-[:IN]->(d)
        """

    FOLLOW_UNIT_TEMPLATE = """
        MATCH (u1:Unit {identifier: $unit_id_1})
        MATCH (u2:Unit {identifier: $unit_id_2})
        MERGE (u2)-[:FOLLOWS]->(u1)
        """
    
    ADD_SESSION_CONTROLLER_TEMPLATE = """
        MERGE (sc:SessionController {session_document_id: $session_document_id})
        SET sc.session_id = $session_id
        WITH sc
        MATCH (d:Document {identifier: $document_id})
        MERGE (sc)-[:SESSION_FOR]->(d)
        """
    
    ADD_STEP_TEMPLATE = """
        MERGE (s:Step {identifier: $step_id})
        SET s.type = $type, s.status = $status
        WITH s
        MATCH (sc:SessionController {session_document_id: $session_document_id})
        MERGE (sc)-[:HAS_STEP]->(s)
        """
    
    ADD_ACTION_TEMPLATE = """
        MERGE (a:Action {identifier: $action_id})
        SET a.trajectory_id = $trajectory_id,
            a.run = $run,
            a.index = $index,
            a.timestamp = $timestamp,
            a.skill_description = $skill_description,
            a.inputs = $inputs,
            a.json_output = $json_output
        WITH a
        MATCH (s:Step {identifier: $step_id})
        MERGE (a)-[:COMPUTED_UNDER]->(s)
        """

    def __init__(self, connection: ConnectionSingleton):
        self._connection = connection

    def add_document(self, document_id: str, name: str, sha256: str):
        parameters = {"document_id": document_id, "name": name, "sha256": sha256}
        self._connection.execute_query(self.ADD_DOCUMENT_TEMPLATE, parameters)
    
    def add_units_segment(self, units_segment: list):
        """Add a segment of units to the graph store."""
        parameters_list = []
        for unit in units_segment:
            parameters = {
                "unit_id": unit["unit_id"],
                "document_id": unit["document_id"],
                "position": unit["position"],
                "content": unit["content"],
                "digest": unit["digest"]
            }
            parameters_list.append(parameters)
        self._connection.execute_multiple_identical_queries(
            self.ADD_UNIT_TEMPLATE, parameters_list)
    
    def merge_session_controller(self, session_id: str, document_id: str):
        print(f"Storing session controller for session {session_id} and document {document_id}")
        short_document_id = calculate_sha256(document_id)[:8]
        session_document_id = f"{session_id}_{short_document_id}"
        parameters = {"session_document_id": session_document_id,
                      "session_id": session_id, "document_id": document_id}
        self._connection.execute_query(self.ADD_SESSION_CONTROLLER_TEMPLATE, parameters)

    def merge_step(self, session_document_id: str, document_id: str, step_id: str, step_type: str, step_status: str):
        print(f"Storing step {step_id} for session document id {session_document_id} and document {document_id} as {step_type} with status {step_status}")
        parameters = {"session_document_id": session_document_id,
                      "step_id": step_id, "type": step_type, "status": step_status}
        self._connection.execute_query(self.ADD_STEP_TEMPLATE, parameters)

    def merge_action(self,
                     step_id: str,
                     action_id: str,
                     trajectory_id: str,
                     run: int,
                     index: int,
                     timestamp: int,
                     skill_description: str,
                     inputs: list,
                     outputs: list):
        # store inputs as a list of strings,
        # but store outputs as a JSON serialised string
        serialised_outputs = json.dumps(outputs)
        print(f"Storing action {action_id} for step {step_id} with skill {skill_description}")
        parameters = {"step_id": step_id, "action_id": action_id,
                        "trajectory_id": trajectory_id, "run": run, "index": index, "timestamp": timestamp,
                        "skill_description": skill_description, "inputs": inputs,
                        "json_output": serialised_outputs}
        self._connection.execute_query(self.ADD_ACTION_TEMPLATE, parameters)

    def close(self):
        self._connection.close()
