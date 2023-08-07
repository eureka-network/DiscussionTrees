import os
from dotenv import load_dotenv
from enum import Enum
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate


def generate_classifier_prompt(message_1: str, message_2: str):
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

    input_variables = {"message_1": message_1,
                       "message_2": message_2}
    prompt_template = PromptTemplate.from_template(unformatted_prompt_text)
    return prompt_template.format(**input_variables).format()


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


class ClassifierAgent:
    def __init__(self, **kwargs):
        load_dotenv()
        OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

        kwargs.setdefault("model_name", "gpt-3.5-turbo")
        kwargs.setdefault("temperature", 0)
        kwargs.setdefault("request_timeout", 120)

        self.llm = ChatOpenAI(model_name=kwargs["model_name"], temperature=kwargs["temperature"],
                              request_timeout=kwargs["request_timeout"], openai_api_key=OPENAI_API_KEY)

    def classify_context(self, message_1: str, message_2: str) -> ContextClassifier:
        prompt_message = generate_classifier_prompt(message_1, message_2)
        prediction = self.llm.predict(prompt_message)
        return ContextClassifier.from_message(prediction)
