import os

from dotenv import load_dotenv

class IngesterConfig:

    def __init__(self):
        pass

    def load_environment_variables(self):
        load_dotenv()
        self._INGESTER_TASK_DOCUMENT = os.getenv("INGESTER_TASK_DOCUMENT")
        self._KNOWLEDGE_BASE_DIR = os.getenv("KNOWLEDGE_BASE_DIR")
        self._NEO4J_URI = os.getenv("NEO4J_URI")
        self._NEO4J_USER = os.getenv("NEO4J_USER")
        self._NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    
    @property
    def ingester_task_document(self):
        if not hasattr(self, '_INGESTER_TASK_DOCUMENT'):
            self.load_environment_variables()

        # return None if it is set to empty string
        if self._INGESTER_TASK_DOCUMENT == "":
            return None
        # INGESTER_TASK_DOCUMENT can be None
        return self._INGESTER_TASK_DOCUMENT
    
    @property
    def knowledge_base_dir(self):
        if not hasattr(self, "_KNOWLEDGE_BASE_DIR"):
            self.load_environment_variables()
        
        assert self._KNOWLEDGE_BASE_DIR is not None, "KNOWLEDGE_BASE_DIR not set in env variables."
        return self._KNOWLEDGE_BASE_DIR

    @property
    def neo4j_credentials(self):
        if not hasattr(self, '_NEO4J_URI'):
            self.load_environment_variables()

        assert self._NEO4J_URI is not None, "NEO4J_URI not set in env variables."
        assert self._NEO4J_USER is not None, "NEO4J_USER not set in env variables."
        assert self._NEO4J_PASSWORD is not None, "NEO4J_PASSWORD not set in env variables."

        return self._NEO4J_URI, self._NEO4J_USER, self._NEO4J_PASSWORD