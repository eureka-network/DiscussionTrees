"""
Reader class for neo4j DB.
"""

from neo4j import GraphDatabase
from .connection import ConnectionSingleton

class Reader:
    def __init__(self, connection: ConnectionSingleton):
        self._connection = connection
    
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
        pass
