import os
import together

from dotenv import load_dotenv

class MeaningFunctionConfig:

    def __init__(self):
        pass

    def load_environment_variables(self):
        load_dotenv()
        self._TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
        self._OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self._together_model_list = None

    # Together API

    @property
    def together_api_key(self):
        if not hasattr(self, '_TOGETHER_API_KEY') or self._TOGETHER_API_KEY is None:
            self.load_environment_variables()

        assert self._TOGETHER_API_KEY is not None, "Together.ai API key not set in env variables."
        return self._TOGETHER_API_KEY

    @property
    def together_model_list(self):
        if self._together_model_list is not None:
            return self._together_model_list
        
        if not hasattr(self, '_TOGETHER_API_KEY'):
            self.load_environment_variables()

        assert self._TOGETHER_API_KEY is not None, "Together.ai API key not set in env variables."

        together.api_key = self._TOGETHER_API_KEY
        self._together_model_list = together.Models.list()

        return self._together_model_list
    
    # OpenAI API

    @property
    def openai_api_key(self):
        if not hasattr(self, '_OPENAI_API_KEY') or self._OPENAI_API_KEY is None:
            self.load_environment_variables()

        assert self._OPENAI_API_KEY is not None, "OpenAI API key not set in env variables."
        return self._OPENAI_API_KEY
   