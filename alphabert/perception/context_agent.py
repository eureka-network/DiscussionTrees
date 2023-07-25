from langchain.chat_models import ChatOpenAI
from context_classifier import ContextClassifier


class ContextAgent:
    def __init__(
        self,
        model_name="gpt-3.5-turbo",
        temperature=0,
        request_timeout=120,
        mode="auto",
    ):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            request_timeout=request_timeout,
        )
        if mode not in ["auto", "manual"]:
            raise ValueError(f"mode {mode} is not supported")

    def classify_context(self, prompt_message: str) -> ContextClassifier:
        llm = self.llm
        prediction = llm.predict(prompt_message)
        return ContextClassifier.from_message(prediction)
