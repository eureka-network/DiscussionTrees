from dotenv import load_dotenv
import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate



def load_llm():
    """Creates a new OpenAI LLM instance"""
    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    return OpenAI(openai_api_key=OPENAI_API_KEY)


if __name__ == "__main__": 
    llm = load_llm()