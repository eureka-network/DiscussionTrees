from .alphabert import Alphabert


# from dotenv import load_dotenv
# import os
# from langchain.llms import OpenAI
# from langchain.prompts import PromptTemplate

# import asyncio
# import time

# from neo4j import GraphDatabase

# async def build_curriculum(history_point):
#     """Builds a curriculum of exploration tasks for a given history-point"""

# async def run_agent():
#     """Run the agent"""
#     while True:
#         # todo
#         print("running agent")
#         time.sleep(5)

# def load_llm():
#     """Creates a new OpenAI LLM instance"""
#     load_dotenv()

#     OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
#     return OpenAI(openai_api_key=OPENAI_API_KEY)

# class Neo4jReader(object):
#     def __init__(self, uri, user, password):
#         self._driver = GraphDatabase.driver(uri, auth=(user, password))

#     def close(self):
#         self._driver.close()

#     def get_threads(self):
#         with self._driver.session() as session:
#             query = """
#             MATCH (t:Thread)
#             RETURN t.id as id, t.title as title, t.datePublished as datePublished
#             """
#             result = session.run(query)
#             # iterate over the stream before exiting the session
#             return list(result)
        
#     def get_posts_from_thread(self, thread_id):
#         with self._driver.session() as session:
#             query = """
#             MATCH ((p:Post)-[:IN]->(t:Thread {id: $thread_id}))
#             RETURN p.id as id, p.content as content, p.date as date, p.position as position
#             ORDER BY p.position ASC
#             """
#             result = session.run(query, thread_id=thread_id)
#             # iterate over the stream before exiting the session
#             return list(result)

#     def get_positioned_post(self, thread_id, post_position):
#         with self._driver.session() as session:
#             query = """
#             MATCH (p:Post {position: $post_position})-[:IN]->(t:Thread {id: $thread_id})
#             RETURN p.id as id, p.content as content, p.date as date, p.position as position
#             """
#             result = session.run(query, thread_id=thread_id, post_position=post_position)
#             # iterate over the stream before exiting the session
#             return list(result)

# if __name__ == "__main__": 
#     # llm = load_llm()

#     neo4j = Neo4jReader('neo4j://localhost:7687',
#                         'neo4j', 'IlGOk+9SoTmmeQ==')
    
#     # threads = neo4j.get_threads()
#     # print(f"number of threads: {len(threads)}")
#     # for thread in threads:
#     #     print(f"thread: {thread}")

#     # thread: <Record id='320fff84' title='[SEP #5] Redistributing Unredeemed Tokens From User Airdrop Allocation' datePublished='2022-12-27T12:47:48+00:00'>
#     # posts = neo4j.get_posts_from_thread('320fff84')
#     # print(f"number of posts: {len(posts)}")
#     # for post in posts:
#     #     print(f"post: {post['position']} {post['date']} {post['id']}")

#     asyncio.run(run_agent())
#     opening_post = neo4j.get_positioned_post('320fff84', str(1))
#     print(f"opening post: {opening_post[0]['content']}")

#     neo4j.close()
