from .frame import Frame
from .neo4j_reader import Neo4jReader
from .context_agent import ContextAgent


class FrameBuffer:

    def __init__(self, thread_id: str, agent: ContextAgent):
        self.thread_id: str = thread_id
        self.height: int = 0
        self.terminated: bool = False
        self.frames: list[Frame] = []
        # 0: intra-post, ie. sentences; 1 post-level; 2 inter-posts; possibly 3. threads
        self.current_level = 1

        self.neo4j_reader = Neo4jReader(
            'neo4j://localhost:7687', 'neo4j', 'IlGOk+9SoTmmeQ==')

    def step(self):
        if self.terminated:
            raise ValueError("The current `FrameBuffer` is already terminated")
        new_height = self.height + 1
        group = self.get_next_group(new_height)
        if group is None:
            self.terminate_sequence()
            return
        frame = Frame(self.height, self.current_level, group, self.agent)
        self.frames.push(frame)
        self.height = new_height

    def run(self):
        while not self.terminated:
            self.step()

    def execute(self):
        for frame_height, frame in enumerate(self.frames):
            relation = frame.execute_group()
            self._store_new_relation(relation, frame_height)

    def terminate_sequence(self):
        self.terminated = True

    def close(self):
        self.neo4j_reader.close()

    def _store_new_relation(self, relation: str, post_id: int):
        # For now, we stay on level 1, and simply iterate over all the posts
        original_post_id = 1
        with self._driver.session() as session:
            query = f"""
                     MATCH (p1:Post {id: $post_id})
                     MATCH (p2:Post {id: $original_post_id_2})
                     MERGE (p1)-[:{relation}]->(p2)
                    """
            session.run(query, post_id_1=post_id, post_id_2=original_post_id)

    def get_next_group(self, new_height: int):
        # for now stay on level 1 and simply iterate over all the posts
        return self.neo4j_reader.get_positioned_post(self.thread_id, new_height)
