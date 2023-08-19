"""
Reader class for neo4j DB.
"""

from neo4j import GraphDatabase
from .connection import ConnectionSingleton

class Reader:

    DOCUMENT_EXISTS_TEMPLATE = """
        MATCH (d:Document {identifier: $document_id})
        RETURN d.identifier as identifier, d.name as name
        """
    
    DOCUMENT_NUMBER_OF_UNITS_TEMPLATE = """
        MATCH (d:Document {identifier: $document_id})
        MATCH (u:Unit)-[:IN]->(d)
        RETURN count(u) as numberOfUnits
        """
    
    DOCUMENT_UNIT_DIGESTS_TEMPLATE = """
        MATCH (d:Document {identifier: $document_id})
        MATCH (u:Unit)-[:IN]->(d)
        RETURN u.position as position, u.digest as digest
        ORDER BY u.position
        """

    def __init__(self, connection: ConnectionSingleton):
        self._connection = connection
    
    def document_exists(self, document_id: str):
        parameters = {"document_id": document_id}
        result = self._connection.execute_query(self.DOCUMENT_EXISTS_TEMPLATE, parameters)
        return len(result) > 0
    
    def get_number_of_stored_units(self, document_id: str):
        parameters = {"document_id": document_id}
        result = self._connection.execute_query(self.DOCUMENT_NUMBER_OF_UNITS_TEMPLATE, parameters)
        return result[0]["numberOfUnits"]

    def get_document_properties(self, document_id: str):
        parameters = {"document_id": document_id}
        result = self._connection.execute_query(self.DOCUMENT_EXISTS_TEMPLATE, parameters)
        return result[0]
    
    def get_list_of_unit_digests(self, document_id: str):
        parameters = {"document_id": document_id}
        result = self._connection.execute_query(self.DOCUMENT_UNIT_DIGESTS_TEMPLATE, parameters)
        return result

    # todo: deprecate for lazy evaluations only
    def get_all_documents(self):
        query: str = """
                        MATCH (d:Document)
                        RETURN d.id as id, d.name as name, d.datePublished as datePublished, d.dateIngested as dateIngested
                    """
        result = self._connection.execute_query(query)
        return list(result)
    
    def close(self):
        self._connection.close()

