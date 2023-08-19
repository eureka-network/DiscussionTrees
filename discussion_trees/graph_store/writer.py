"""
Writer class for neo4j DB.
"""

from neo4j import GraphDatabase
from .connection import ConnectionSingleton

class Writer:

    ADD_DOCUMENT_TEMPLATE = """
        MERGE (d:Document {{id: {document_id}}})
        SET d.name = {name}, d.cid = {cid}, d.meta_cid = {meta_cid}
        """
    ADD_UNIT_TEMPLATE = """
        MERGE (u:Unit {{id: {unit_id}}})
        SET u.document_id = {document_id}, u.position = {position}, u.content = {content}
        MATCH (d:Document {{id: {document_id}}})
        MERGE (u)-[:IN]->(d)
        """
    FOLLOW_UNIT_TEMPLATE = """
        MATCH (u1:Unit {{id: {unit_id_1}}})
        MATCH (u2:Unit {{id: {unit_id_2}}})
        MERGE (u2)-[:FOLLOWS]->(u1)
        """

    def __init__(self, connection: ConnectionSingleton):
        self._connection = connection

    def add_units_segment(self, unit):
        """Add a segment of units to the graph store."""

    # def format_add_unit_template(self, )
    
    def close(self):
        self._connection.close()
