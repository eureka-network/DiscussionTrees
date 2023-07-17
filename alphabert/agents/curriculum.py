# todo: use vLLM to switch between OpenAI and OSS LLM models https://github.com/vllm-project/vllm

from langchain.chat_models import ChatOpenAI

class CurriculumAgent:
    def __init__(
        self,
        model_name="gpt-3.5-turbo",
        qa_model_name="gpt-3.5-turbo",
        temperature=0,
        qa_temperature=0,
        request_timeout=120,
        mode="auto"
    ):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            request_timeout=request_timeout,
        )
        self.qa_llm = ChatOpenAI(
            model_name=qa_model_name,
            temperature=qa_temperature,
            request_timeout=request_timeout,
        )
        if mode not in ["auto", "manual"]:
            raise ValueError(f"mode {mode} is not supported")
        
        self.mode = mode

    