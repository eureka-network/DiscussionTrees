from neo4j import GraphDatabase
from typing import Optional


class Neo4jWriter:
    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def store_new_post_relation(self, thread_id: str, head_post_position: int, tail_post_position: int, relation: str):
        with self._driver.session() as session:
            query = """
                MATCH (p1:Post {position: $head_post_position})
                MATCH (p2:Post {position: $tail_post_position})
                MATCH (t:Thread {id: $thread_id})
                WHERE (p1)-[:IN]->(t) AND (p2)-[:IN]->(t)
            """
            query += f"""
                MERGE (p1)-[:{relation}]->(p2)
            """
            session.run(query, head_post_id=head_post_position,
                        tail_post_id=tail_post_position, thread_id=thread_id)
