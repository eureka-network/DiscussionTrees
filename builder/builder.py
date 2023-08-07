from .perception.frame_buffer import FrameBuffer


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
        print("Hello world")

    def step(self):
        self.frame_buffer.step()
