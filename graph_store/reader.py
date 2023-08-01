"""
Reader class for neo4j DB.
"""

from neo4j import GraphDatabase

class Reader:
    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self._driver.close()

    def get_documents(self):

