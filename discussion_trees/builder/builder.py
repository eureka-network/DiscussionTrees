from discussion_trees.graph_store import Graph
from .perception import FrameBuffer

class Builder:
    def __init__(self, config):
        print("Hello, builder !")
        self._config = config
        # graph
        self._graph = Graph(
            self._config.neo4j_credentials[0], # uri
            self._config.neo4j_credentials[1], # user
            self._config.neo4j_credentials[2]) # password

        # perception
        self.frame_buffer = FrameBuffer(self._graph.new_reader(), self._config.builder_task_document)

    def run(self):
        pass

    def step(self):
        self.frame_buffer.step()