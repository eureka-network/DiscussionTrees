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
        # this is super hacky and relies on not being misused in the code... 
        # but I don't know if there's a proper way in Python and this is just a demo code
        self.copies = 1
    
    def execute_query(self, query: str, parameters: dict = None):
        with self._driver.session() as session:
            # todo: for now we iterate all results with list()
            #       we should expose an active lazy iterator later
            return list(session.run(query, parameters))
    
    def execute_multiple_queries(self, queries: list, parameter_list: list = None):
        with self._driver.session() as session:
            for query, parameters in zip(queries, parameter_list):
                session.run(query, parameters)

    def execute_multiple_identical_queries(self, query: str, parameter_list: list):
        with self._driver.session() as session:
            for parameters in parameter_list:
                session.run(query, parameters)

    def clone(self):
        self.copies += 1
        return self

    def close(self):
        self.copies -= 1
        assert self.copies >= 0, "Connection closed too many times"
        if self.copies == 0:
            self._driver.close()

# ConnectionSingleton ensures a single instance of the connection exists in the code
class ConnectionSingleton(_Connection, metaclass=Singleton):
    pass
