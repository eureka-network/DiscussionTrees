import openai

from .config import MeaningFunctionConfig
from .meaning_function import MeaningFunction


DEFAULT_TEMPERATURE: float = 0.1

DEFAULT_MODEL_NAME =  "gpt-3.5-turbo-0613" # "gpt-4-0613"
DEFAULT_SYSTEM_PROMPT: str = "You are a helpful assistent."

class OpenAiLlm(MeaningFunction):
    def __init__(self,
                 config: MeaningFunctionConfig,
                 model_name: str = DEFAULT_MODEL_NAME,
                 temperature: float = DEFAULT_TEMPERATURE):
        self._config = config
        self._config.load_environment_variables()
        openai.api_key = self._config.openai_api_key

        model_list = self._config.openai_model_list
        if not any(item['id'] == model_name for item in model_list['data']):
            raise ValueError(f"Model {model_name} not available in OpenAI")
        self._model_name = model_name
        self._temperature = temperature

    def start(self):
        pass

    def stop(self):
        pass

    def prompt(self,
               prompt: str,
               wrap_system_prompt: bool = False,
               temperature: float = None,
        ):
        if prompt is None or prompt == "":
            raise ValueError("Prompt must be a non-empty string")
        if temperature is None:
            temperature = self._temperature
        
        messages = []
        if wrap_system_prompt:
            messages.append(
                {"role": "system", "content": DEFAULT_SYSTEM_PROMPT}
            )
        messages.append(
            {"role": "user", "content": prompt}
        )

        output = openai.ChatCompletion.create(
            model = DEFAULT_MODEL_NAME,
            messages =  messages,
            temperature = temperature)
        
        print(f"Full output:\n\n {output}\n\n")
        
        print("Response:\n")
        print(output["choices"][0]["message"]["content"])
        print("\n\n")

        # return output
        # todo: for now default to this as response
        return output["choices"][0]["message"]["content"]
    
    @property
    def description(self):
        return f"OpenAI LLM {self._model_name} (default temperature {self._temperature})"

        