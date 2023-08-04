from neo4j import GraphDatabase
from typing import Optional


class Neo4jWriter:
    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def store_new_post_relation(self, thread_id: str, head_post_id: str, tail_post_id: str, relation: str):
        with self._driver.session() as session:
            query = """
                MATCH (p1:Post {id: $head_post_id})
                MATCH (p2:Post {id: $tail_post_id})
                MATCH (t:Thread {id: $thread_id})
                WHERE (p1)-[:IN]->(t) AND (p2)-[:IN]->(t)
            """
            query += f"""
                MERGE (p1)-[:{relation}]->(p2)
            """
            session.run(query, head_post_id=head_post_id,
                        tail_post_id=tail_post_id, thread_id=thread_id)
