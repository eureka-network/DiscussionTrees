"""
Reader class for neo4j DB.
"""

from neo4j import GraphDatabase
from .connection import ConnectionSingleton

class Reader:

    ALL_DOCUMENTS_STATIC = """
        MATCH (d:Document)
        RETURN d.identifier as identifier, d.name as name
        """
    
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
    
    UNITS_BY_POSITION_TEMPLATE = """
        MATCH (d:Document {identifier: $document_id})
        MATCH (u:Unit)-[:IN]->(d)
        WHERE u.position >= $position_start AND u.position <= $position_end
        RETURN u.position as position, u.digest as digest, u.content as content
        ORDER BY u.position
        """

    ALL_SESSION_DOCUMENTS_TEMPLATE = """
        MATCH (sc:SessionController)-[:SESSION_FOR]->(d:Document)
        WHERE sc.session_id = $session_id
        RETURN d.identifier as identifier, d.name as name
        """
    
    STEPS_FOR_SESSION_DOCUMENT_TEMPLATE = """
        MATCH (sc:SessionController)-[:SESSION_FOR]->(d:Document)
        WHERE sc.session_id = $session_id AND d.identifier = $document_id
        MATCH (sc)-[:HAS_STEP]->(s:Step)
        RETURN s.identifier as identifier, s.type as type, s.status as status
        ORDER BY s.identifier
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
    
    def get_units_by_position(self, document_id: str, position_start: int, position_end: int):
        parameters = {"document_id": document_id, "position_start": position_start, "position_end": position_end}
        result = self._connection.execute_query(self.UNITS_BY_POSITION_TEMPLATE, parameters)
        return list(result)

    # todo: deprecate for lazy evaluations only
    def get_all_documents(self):
        result = self._connection.execute_query(self.ALL_DOCUMENTS_STATIC)
        return list(result)
    
    def get_all_session_documents(self, session_id: str):
        parameters = {"session_id": session_id}
        result = self._connection.execute_query(self.ALL_SESSION_DOCUMENTS_TEMPLATE, parameters)
        return list(result)
    
    def get_state_for_session_documents(self, session_id: str, document_id: str):
        parameters = {"session_id": session_id, "document_id": document_id}
        result = self._connection.execute_query(self.STEPS_FOR_SESSION_DOCUMENT_TEMPLATE, parameters)
        return list(result)

    def close(self):
        self._connection.close()
