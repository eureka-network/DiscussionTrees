import os

from dotenv import load_dotenv

class BuilderConfig:

    def __init__(self):
        pass

    def load_environment_variables(self):
        load_dotenv()
        self._BUILDER_TASK_DOCUMENT = os.getenv("BUILDER_TASK_DOCUMENT")
        self._NEO4J_URI = os.getenv("NEO4J_URI")
        self._NEO4J_USER = os.getenv("NEO4J_USER")
        self._NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    
    @property
    def builder_task_document(self):
        if not hasattr(self, '_BUILDER_TASK_DOCUMENT'):
            self.load_environment_variables()

        # return None if it is set to empty string
        if self._BUILDER_TASK_DOCUMENT == "":
            return None
        # BUILDER_TASK_DOCUMENT can be None
        return self._BUILDER_TASK_DOCUMENT
    
    @property
    def neo4j_credentials(self):
        if not hasattr(self, '_NEO4J_URI'):
            self.load_environment_variables()

        assert self._NEO4J_URI is not None, "NEO4J_URI not set in env variables."
        assert self._NEO4J_USER is not None, "NEO4J_USER not set in env variables."
        assert self._NEO4J_PASSWORD is not None, "NEO4J_PASSWORD not set in env variables."

        return self._NEO4J_URI, self._NEO4J_USER, self._NEO4J_PASSWORD