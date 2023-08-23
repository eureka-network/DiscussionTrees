from .connection import ConnectionSingleton
from .reader import Reader
from .writer import Writer

"""
Graph provides reader and writer to access graph operations over connection.
"""

class Graph:

    def __init__(self, uri: str, user: str, password: str):
        self._connection = ConnectionSingleton(uri, user, password)

    def new_reader(self):
        return Reader(self._connection.clone())
    
    def new_writer(self):
        return Writer(self._connection.clone())