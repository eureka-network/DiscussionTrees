import os

from dotenv import load_dotenv

class BuilderConfig:

    def __init__(self):
        pass

    def load_environment_variables(self):
        load_dotenv()
        self._OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self._BUILDER_TASK_DOCUMENT = os.getenv("BUILDER_TASK_DOCUMENT")

    @property
    def openai_api_key(self):
        if not hasattr(self, '_OPENAI_API_KEY') or self._OPENAI_API_KEY is None:
            self.load_environment_variables()

        assert self._OPENAI_API_KEY is not None, "OpenAI API key not set in env variables."
        return self._OPENAI_API_KEY
    
    @property
    def builder_task_document(self):
        if not hasattr(self, '_BUILDER_TASK_DOCUMENT'):
            self.load_environment_variables()

        return self._BUILDER_TASK_DOCUMENT