"""
Reader class for neo4j DB.
"""

from neo4j import GraphDatabase
from .connection import ConnectionSingleton

class Reader:

    DOCUMENT_EXISTS_TEMPLATE = """
        MATCH (d:Document {identifier: $document_id})
        RETURN d
        """
    
    def __init__(self, connection: ConnectionSingleton):
        self._connection = connection
    
    def document_exists(self, document_id: str):
        parameters = {"document_id": document_id}
        result = self._connection.execute_query(self.DOCUMENT_EXISTS_TEMPLATE, parameters)
        print(result)
        return len(result) > 0

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

