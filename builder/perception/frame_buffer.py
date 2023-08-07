from .classifier_agent import ClassifierAgent
from .frame import Frame
from ..neo4j.neo4j_reader import Neo4jReader
from ..neo4j.neo4j_writer import Neo4jWriter


class FrameBuffer:

    def __init__(self, thread_id: str, **kwargs):
        self.thread_id: str = thread_id
        self.height: int = 0
        self.terminated: bool = False
        self.frames: list[Frame] = []
        # 0: intra-post, ie. sentences; 1 post-level; 2 inter-posts; possibly 3. threads
        self.current_level = 1
        self.neo4j_reader = Neo4jReader(
            'neo4j://localhost:7687', 'neo4j', 'IlGOk+9SoTmmeQ==')
        self.neo4j_writer = Neo4jWriter(
            'neo4j://localhost:7687', 'neo4j', 'IlGOk+9SoTmmeQ==')
        # get the model parameters for the classifier agent, if any
        self._agent = ClassifierAgent(**kwargs)

    def step(self):
        if self.terminated:
            return
        new_height: int = self.height + 1
        group = self.get_next_group(new_height)
        if group is None:
            self.terminate_sequence()
            return
        frame: Frame = Frame(
            self.height, self.current_level, group, self._agent)
        self.frames.push(frame)
        self.height = new_height

    def run(self):
        while not self.terminated:
            self.step()

    def terminate_sequence(self):
        self.terminated = True

    def close(self):
        self.neo4j_reader.close()

    def get_next_group(self, new_height: int):
        # for now stay on level 1 and simply iterate over all the posts
        return self.neo4j_reader.get_positioned_post(self.thread_id, new_height)

    def store_new_relation(self, head_post_position: int, tail_post_position: int, relation: str):
        self.neo4j_writer.store_new_post_relation(
            self.thread_id, head_post_position, tail_post_position, relation)

    def execute(self):
        """Executes the whole internal sequence of `Frame`'s. Currently, the input to a `Frame`'s `execute_input` corresponds to the
            original thread post"""
        original_thread_post_position = 1
        original_thread_post = self.neo4j_reader.get_positioned_post(
            original_thread_post_position)
        for frame_height, frame in enumerate(self.frames):
            relation = frame.execute_input(original_thread_post)
            # Given the current post p_current, it is in relation with respect to the original thread post
            self.neo4j_writer.store_new_post_relation(
                self.thread_id, frame_height, original_thread_post_position, relation)
