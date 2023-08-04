from neo4j import GraphDatabase
from typing import Optional


class Neo4jReader:
    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def get_threads(self):
        with self._driver.session() as session:
            query: str = """
                            MATCH (t:Thread)
                            RETURN t.id as id, t.title as title, t.datePublished as datePublished
                        """
            result = session.run(query)
            # iterate over the stream before exiting the session
            return list(result)

    def get_posts_from_thread(self, thread_id: str):
        with self._driver.session() as session:
            query: str = """
                            MATCH ((p:Post)-[:IN]->(t:Thread {id: $thread_id}))
                            RETURN p.id as id, p.content as content, p.date as date, p.position as position
                            ORDER BY p.position ASC
                        """
            result = session.run(query, thread_id=thread_id)
            # iterate over the stream before exiting the session
            return list(result)

    def get_positioned_post(self, thread_id: str, post_position: int):
        """Returns a single post from a thread, given the thread id and the post position, or None if no post is found"""
        with self._driver.session() as session:
            # assume position is unique in the thread
            query: str = """
                            MATCH (p:Post)-[:IN]->(t:Thread {id: $thread_id})
                        """
            query += f" WHERE p.position='{post_position}'"
            query += """
                            RETURN p.id as id, p.content as content, p.date as date, p.position as position
                            LIMIT 1
                        """
            result = session.run(query, thread_id=thread_id,
                                 post_position=post_position)
            # retrieve the first result and return post, or None if no result is found
            return result.single()['content']
