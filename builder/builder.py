from .perception.classifier_frame_buffer import ClassifierFrameBuffer


class Builder:
    def __init__(
        self,
    ):
        print("Hello, world !")
        # perception
        self.frame_buffer = ClassifierFrameBuffer()

    def run(
        self,
    ):
        print("Hello world")

    def step(self):
        self.frame_buffer.step()
