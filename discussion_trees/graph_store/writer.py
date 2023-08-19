"""
Writer class for neo4j DB.
"""

from neo4j import GraphDatabase
from .connection import ConnectionSingleton

class Writer:

    ADD_DOCUMENT_TEMPLATE = """
        MERGE (d:Document {identifier: $document_id})
        SET d.name = $name
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

    def __init__(self, connection: ConnectionSingleton):
        self._connection = connection

    def add_document(self, document_id: str, name: str):
        parameters = {"document_id": document_id, "name": name}
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
    
    def close(self):
        self._connection.close()
