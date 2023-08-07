from ..perception import FrameBuffer

class Builder:
    def __init__(
        self,
    ):
        print("Hello, world !")
        # perception
        self.frame_buffer = FrameBuffer()

    def run(
        self,
    ):
        pass

    def step(self):
        self.frame_buffer.step()