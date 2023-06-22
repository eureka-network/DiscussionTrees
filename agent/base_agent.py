from dotenv import load_dotenv
import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

from neo4j import GraphDatabase


def load_llm():
    """Creates a new OpenAI LLM instance"""
    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    return OpenAI(openai_api_key=OPENAI_API_KEY)

class Neo4jReader(object):
    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def get_threads(self):
        with self._driver.session() as session:
            query = """
            MATCH (t:Thread)
            RETURN t.id as id, t.title as title, t.date_published as date_published
            """
            result = session.run(query)
            return result


if __name__ == "__main__": 
    llm = load_llm()

    neo4j = Neo4jReader('neo4j://localhost:7687',
                        'neo4j', 'IlGOk+9SoTmmeQ==')
    
    threads = neo4j.get_threads()
    print(f"threads: {threads}")
