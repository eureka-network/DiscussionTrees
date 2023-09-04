import together
from .config import MeaningFunctionConfig
from .meaning_function import MeaningFunction

DEFAULT_MODEL_NAME: str = "togethercomputer/llama-2-70b-chat"
DEFAULT_MAX_TOKENS: int = 512
DEFAULT_TEMPERATURE: float = 0.6
DEFAULT_TOP_K: int = 90
DEFAULT_TOP_P: float = 0.8
DEFAULT_REPITITION_PENALTY: float = 1.1
DEFAULT_STOP: list = ['</s>']

SYSTEM_PROMPT_PREFIX: str = "<s>[INST] <<SYS>>\n"
SYSTEM_PROMPT_SUFFIX: str = "\n<</SYS>>\n\n"
PROMPT_CLOSURE: str = "[/INST]"
DEFAULT_SYSTEM_PROMPT: str = "You are a helpful assistent excellent at extracting semantical meaning from text. Always answer completely, correctly and to the point as asked."


class TogetherLlm(MeaningFunction):
    # define class dictionary to track instances of a given model
    _instances = {}

    def __init__(self, 
                 config: MeaningFunctionConfig,
                 model_name: str = DEFAULT_MODEL_NAME,
                 max_tokens: int = DEFAULT_MAX_TOKENS,
                 temperature: float = DEFAULT_TEMPERATURE,
                 top_k: int = DEFAULT_TOP_K,
                 top_p: float = DEFAULT_TOP_P,
                 repetition_penalty: float = DEFAULT_REPITITION_PENALTY):
        self._config = config
        self._config.load_environment_variables()
        together.api_key = self._config.together_api_key

        model_list = self._config.together_model_list
        if not any(model["name"] == model_name for model in model_list):
            raise ValueError(f"Model {model_name} not available in Together.ai")
        if TogetherLlm._instances.get(model_name) is None:
            # initialize the model instance counter
            TogetherLlm._instances[model_name] = 0
        self._model_name = model_name
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._top_k = top_k
        self._top_p = top_p
        self._repetition_penalty = repetition_penalty
        self._started = False

    def start(self):
        # check if we already started our instance
        if self._started:
            return
        assert TogetherLlm._instances.get(self._model_name) >= 0, "TogetherLlm instance counter not initialized"

        # check if the model is already running remotely
        refreshed_instances = together.Models.instances()
        # check whether remote instance is not already running
        if not refreshed_instances.get(self._model_name):
            assert TogetherLlm._instances.get(self._model_name) == 0, (
                f"Model {self._model_name} is not running remotely, "
                f"but {TogetherLlm._instances.get(self._model_name)} local instances accounted for")
            print(f"Starting TogetherLlm model {self._model_name}")
            result = together.Models.start(self._model_name)
            assert result["success"] == True, f"Failed to start TogetherLlm model {self._model_name}"
            print(f"Started TogetherLlm model {self._model_name}")

        TogetherLlm._instances[self._model_name] += 1
        self._started = True

    def stop(self):
        # check if the model instance is started
        if not self._started:
            raise ValueError(f"Model instance {self._model_name} has not been started")
        
        # stop the remote instance only if this is the last local instance
        assert TogetherLlm._instances.get(self._model_name) > 0, f"Instance counter for model {self._model_name} is not positive"
        if TogetherLlm._instances.get(self._model_name) == 1:
            print(f"Stopping TogetherLlm model {self._model_name}")
            result = together.Models.stop(self._model_name)
            assert result["success"] == True, f"Failed to stop TogetherLlm model {self._model_name}"
            print(f"Stopped TogetherLlm model {self._model_name}")
        else:
            print(f"Skipping stopping TogetherLlm model {self._model_name}, "
                  f"because {TogetherLlm._instances.get(self._model_name) - 1} local instances still accounted for")

        TogetherLlm._instances[self._model_name] -= 1
        self._started = False

    def prompt(self,
               prompt: str,
               wrap_system_prompt: bool = False,
               max_tokens: int = None,
               temperature: float = None,
               top_k: int = None,
               top_p: float = None,
               repetition_penalty: float = None
        ):
        if not self._started:
            raise ValueError(f"Model instance {self._model_name} has not been started")
        if prompt is None or prompt == "":
            raise ValueError("Prompt must be a non-empty string")
        if max_tokens is None:
            max_tokens = self._max_tokens
        if temperature is None:
            temperature = self._temperature
        if top_k is None:
            top_k = self._top_k
        if top_p is None:
            top_p = self._top_p
        if repetition_penalty is None:
            repetition_penalty = self._repetition_penalty

        # wrap the system prompt if requested
        if wrap_system_prompt:
            prompt = self.wrap_system_prompt(prompt)
        
        output = together.Complete.create(
            prompt = prompt,
            model = self._model_name,
            max_tokens = max_tokens,
            temperature = temperature,
            top_k = top_k,
            top_p = top_p,
            repetition_penalty = repetition_penalty,
            stop = DEFAULT_STOP
        )

        print(f"Full output:\n\n {output}\n\n")

        # print generated text
        print(output['prompt'][0]+output['output']['choices'][0]['text'])
        print("\n\n")
        
        return output
       
    def wrap_system_prompt(self, prompt: str):
        return (SYSTEM_PROMPT_PREFIX + 
                DEFAULT_SYSTEM_PROMPT + 
                SYSTEM_PROMPT_SUFFIX + 
                prompt + 
                PROMPT_CLOSURE)
