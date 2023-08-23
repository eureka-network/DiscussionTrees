from discussion_trees.graph_store import Graph
from discussion_trees.meaning_function import TogetherLlm, MeaningFunctionConfig
from .strategy import Strategy
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
        
        # strategy
        self._strategy = Strategy(self._graph)

        # meaning function
        meaning_function_config = MeaningFunctionConfig()
        meaning_function_config.load_environment_variables()
        self._together_llm = TogetherLlm(meaning_function_config)

        # test LLM
        self._together_llm.start()
        self._together_llm.prompt("Isaac Asimov's Three Laws of Robotics are:\n\n1. ")
        self._together_llm.stop()

        # perception
        self.frame_buffer = FrameBuffer(self._graph.new_reader(), self._config.builder_task_document)

    def run(self):

        
        pass

    def step(self):
        self.frame_buffer.step()