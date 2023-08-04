import os
from dotenv import load_dotenv
from enum import Enum
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate


class ContextClassifier(Enum):
    SUPPORTS = 1
    AGAINST = 2
    UNDETERMINED = 3

    @classmethod
    def from_message(cls, message: str) -> 'ContextClassifier':
        match message.lower():
            case "supports" | "support":
                return cls.SUPPORTS
            case "against":
                return cls.AGAINST
            case "undetermined":
                return cls.UNDETERMINED
            case _:
                raise ValueError(
                    "Invalid message, should be one of ['SUPPORTS', 'AGAINST', 'UNDETERMINED']")

    def to_string(self) -> str:
        match self:
            case self.SUPPORTS:
                return "SUPPORTS"
            case self.AGAINST:
                return "AGAINST"
            case self.UNDETERMINED:
                return "UNDETERMINED"
            case _:
                raise ValueError("Invalid state")


class ClassifierPrompt(PromptTemplate):
    def __init__(self, message_1: str, message_2: str):
        self._message_1 = message_1
        self._message_2 = message_2
        super().__init__()

    def generate_prompt(self):
        unformatted_prompt_text = """
            Is this reply post:
            
            ---
            {message_2}
            ---

            in support, against or its relation is undetermined, regarding post:

            ---
            {message_1}
            ---

            Your reply should be a single value of the following allowed options ["SUPPORTS", "AGAINST", "UNDETERMINED"]
        """

        input_variables = {"message_1": self._message_1,
                           "message_2": self._message_2}
        prompt_template = self.from_template(unformatted_prompt_text)
        return prompt_template.format(**input_variables).format()


class ClassifierAgent:
    def __init__(self, model_name="gpt-3.5-turbo", temperature=0, request_timeout=120):
        load_dotenv()
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature,
                              request_timeout=request_timeout, openai_api_key=OPENAI_API_KEY)

    def classify_context(self, promp_message: str) -> ContextClassifier:
        prediction = self.llm.predict(promp_message)
        return ContextClassifier.from_message(prediction)
