from .frame import Frame
from discussion_trees.graph_store import Graph

class FrameBuffer:

    def __init__(self, document_id: str = None, graph: Graph = None):
        self.document_id: str = document_id
        self.height: int = 0
        self.terminated: bool = False
        self.frames: list[Frame] = []
        self.current_level = 1 # 0: intra-post, ie. sentences; 1 post-level; 2 inter-posts; possibly 3. threads
        # self.neo4j_reader = Neo4jReader('neo4j://localhost:7687', 'neo4j', 'IlGOk+9SoTmmeQ==')
    
    def step(self):
        if self.terminated:
            return
        new_height = self.height + 1
        group = self.get_next_group(new_height)
        if group is None:
            self.terminate_sequence()
            return
        frame = Frame(self.height, self.current_level, group)
        self.frames.push(frame)
        self.height = new_height

    def terminate_sequence(self):
        self.terminated = True

    def close(self):
        self.neo4j_reader.close()

    def get_next_group(self, new_height: int):
        # for now stay on level 1 and simply iterate over all the posts
        # return self.neo4j_reader.get_positioned_post(self.thread_id, new_height)
        pass