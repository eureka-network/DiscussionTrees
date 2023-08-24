from discussion_trees.graph_store import Graph

from .state import DocumentState

class Store:
    def __init__(self, graph: Graph, session_id: str):
        self._document_state = DocumentState(graph, session_id)
        pass