from discussion_trees.graph_store import Graph
from discussion_trees.meaning_function import TogetherLlm, MeaningFunctionConfig
from discussion_trees.document_store import Store
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
        
        # document store
        self._document_store = Store(self._graph, self._config.builder_session_id)
        self._document_store.load_documents()

        # include task document if no documents are in session,
        # and a task document was specified, or
        # if no task document was specified, include all documents
        if self._document_store.number_of_documents_in_session() == 0:
            if self._config.builder_task_document:
                print(f"Current session has no documents. Including task document '{self._config.builder_task_document}' in session.")
                self._document_store.include_document_in_session(self._config.builder_task_document)
            else:
                print("Current session has no documents and no task document was specified. Including all documents in session.")
                self._document_store.include_all_documents_in_session()
            print(f"Session now has {self._document_store.number_of_documents_in_session()} documents.")

        # meaning function
        meaning_function_config = MeaningFunctionConfig()
        meaning_function_config.load_environment_variables()
        self._together_llm = TogetherLlm(meaning_function_config)

        # strategy
        self._strategy = Strategy(self._document_store)
        self._strategy.start_trajectory()

        # perception
        self.frame_buffer = FrameBuffer(self._graph.new_reader(), self._config.builder_task_document)

    def run(self):
        pass

    def step(self):
        self.frame_buffer.step()

    def quick_dirty_test(self):
        # test LLM
        self._together_llm.start()
        # self._together_llm.prompt("""Isaac Asimov's Three Laws of Robotics are:\n\n1. """)
        # prompt = (
        #     'Given the paragraph:\n\n'
        #     '"Iran’s Anti-Access/Area Denial (A2AD) strategy is a vital part of its modern military doctrine, '
        #     'designed to keep potential adversaries at bay by denying them the ability to freely operate within the region."\n\n'
        #     'Extract all the entities and the relations between them in a structured JSON format. Only use the information '
        #     'provided in the paragraph. Do not infer or hallucinate any data outside of the paragraph\'s content. Your response '
        #     'should be in the following format: { "entities": [ { "entity_id": "e1", "type": "EntityType", "value": "EntityName" }, ... ], '
        #     '"relations": [ { "relation_id": "r1", "type": "RelationType", "from": "e1", "to": "e2", "evidence": "Textual evidence from the paragraph" }, ... ] }'
        #     )
        prompt = [
        "Given the two nearby paragraphs",
        "'These capabilities are intended to exploit the vulnerabilities of technologically advanced foes, especially the US, creating a layered defense that could severely damage or destroy an adversary’s forces before they reach Iran’s mainland.'",
        "and",
        "'This approach presents an ongoing challenge for US policymakers, as US military strategy rests on the assumption that it would enjoy relatively unopposed lines of communication and freedom of movement in the Persian Gulf to enable rapid global and regional force projection.'",
        "from the same document, extract all the entities and the relations between them. Only use the information provided in the paragraphs. Do not infer or hallucinate any data outside of the paragraph's content. Considering the proximity of the paragraphs, there might be overlapping or related content between them, but treat each piece of information based on its specific context in the given paragraph.",
        "Your response should be in the following format:",
        "Entities:",
        "EntityID, EntityType, EntityName, Textual evidence from the paragraphs",
        "...",
        "Relations:",
        "RelationID, RelationType, FromEntityID, ToEntityID, Textual evidence from the paragraphs",
        "...",
        "Only respond with the flat comma delimited list, no other output surrounding it."
        ]
        joined_prompt = '\n'.join(prompt)

        self._together_llm.prompt(joined_prompt)
        self._together_llm.stop()