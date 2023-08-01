from .builder import Builder

from dotenv import load_dotenv
import os
# from langchain.llms import OpenAI
# from langchain.prompts import PromptTemplate

# import asyncio
# import time

# async def run_agent():
#     """Run the agent"""
#     while True:
#         # todo
#         print("running agent")
#         time.sleep(5)

def load_llm():
    """Creates a new OpenAI LLM instance"""
    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    return OpenAI(openai_api_key=OPENAI_API_KEY)

async def main():
    


if __name__ == "__main__": 
    asyncio.run(main())
    # llm = load_llm()

    # builder = new Builder()

    # neo4j = Neo4jReader('neo4j://localhost:7687',
    #                     'neo4j', 'IlGOk+9SoTmmeQ==')
    
    # # threads = neo4j.get_threads()
    # # print(f"number of threads: {len(threads)}")
    # # for thread in threads:
    # #     print(f"thread: {thread}")

    # # thread: <Record id='320fff84' title='[SEP #5] Redistributing Unredeemed Tokens From User Airdrop Allocation' datePublished='2022-12-27T12:47:48+00:00'>
    # # posts = neo4j.get_posts_from_thread('320fff84')
    # # print(f"number of posts: {len(posts)}")
    # # for post in posts:
    # #     print(f"post: {post['position']} {post['date']} {post['id']}")

    # asyncio.run(run_agent())
    # opening_post = neo4j.get_positioned_post('320fff84', str(1))
    # print(f"opening post: {opening_post[0]['content']}")

    # neo4j.close()