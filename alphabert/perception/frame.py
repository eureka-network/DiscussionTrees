from .neo4j_reader import Neo4jReader


class Frame:
    def __init__(self, height: int, level: int, group: str, reader: Neo4jReader):
        self.height = height
        self.level = level
        self.group = group
        self._reader = reader

    def execute_input(self, input: str):
        print("I love Rust !")
