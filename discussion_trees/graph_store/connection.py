"""
Singleton pattern for connection to the graph database.
First used the classical pattern, but using the metaclass allows for better readability and testing.
"""

from neo4j import GraphDatabase

# define a singleton to be used as metaclass
class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(type(cls), cls).__call__(*args, **kwargs)
        return cls._instances[cls]

# _Connection defines the core behaviour, and can be used for testing
class _Connection():
    def __init__(self, uri: str, user: str, password: str):
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def execute_query(self, query: str):
        with self._driver.session() as session:
            return session.run(query)

    def close(self):
        self._driver.close()

# ConnectionSingleton ensures a single instance of the connection exists in the code
class ConnectionSingleton(_Connection, metaclass=Singleton):
    pass
