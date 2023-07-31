class Builder:
    def __init__(
        self,
    ):
        print("Hello, world !")
        # perception
        self.frame_buffer = FrameBuffer()

    def step(self):
        
        self.frame_buffer.step()