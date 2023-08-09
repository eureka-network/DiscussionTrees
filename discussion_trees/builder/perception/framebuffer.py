from .frame import Frame
from discussion_trees.graph_store import Reader, Graph

class FrameBuffer:

    def __init__(self, graph_reader: Reader, task_document_id: str = None):
        self._task_document_id: str = task_document_id
        self._height: int = 0
        self._terminated: bool = False
        self._frames: list[Frame] = []
        self._current_level = 1 # 0: intra-post, ie. sentences; 1 post-level; 2 inter-posts; possibly 3. threads
        self._graph_reader = graph_reader
   
    def step(self):
        if self._terminated:
            return
        new_height = self._height + 1
        group = self.get_next_group(new_height)
        if group is None:
            self.terminate_sequence()
            return
        frame = Frame(self._height, self._current_level, group)
        self.frames.push(frame)
        self._height = new_height

    def terminate_sequence(self):
        self._terminated = True

    def close(self):
        self._graph_reader.close()

    def get_next_group(self, new_height: int):
        # for now stay on level 1 and simply iterate over all the posts
        # return self.neo4j_reader.get_positioned_post(self.thread_id, new_height)
        pass