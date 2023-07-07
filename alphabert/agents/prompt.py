from langchain.prompts import StringPromptTemplate
from pydantic import BaseModel, validator


def get_thread_contents(thread_id: str):
    """From a thread id, obtains the thread contents from a Graph database"""
    # TODO: implement it
    return


class KnowledgeGraphPromptTemplate(StringPromptTemplate, BaseModel):
    """A custom prompt template for initial summarization of the contents of a given thread."""

    @validator("input_variables")
    def validate_input_variables(cls, input_variables) -> list[str]:
        """Validates the input variables."""
        if len(input_variables) != 1 or "thread_id" not in input_variables:
            raise ValueError("User must provide a thread_id")
        return input_variables

    def __init__(self, input_variables: list[str], **kwargs):
        self.validate_input_variables(input_variables)
        super().__init__(input_variables=input_variables, **kwargs)

    def format(self, **kwargs) -> str:
        thread_id = kwargs["thread_id"]
        thread_contents = get_thread_contents(thread_id)

        prompt = f"""
        Given the thread_id and its contents, generate an English language summarization of the thread contents.

        Thread Id: {kwargs["thread_id"].__name__}
        Contents: {thread_contents}
        
        Summary:
        """
        return prompt
