from array import array

import moderngl


class Shader:
    def __init__(self):
        self.ctx = moderngl.create_context()
        self.textures = {}
        self.programs = {}
        self.vaos = {}
        self.buffer = self.ctx.buffer(data=array("f", [
            # x, y, u ,v
            -1.0, 1.0, 0.0, 0.0,  # top left
            1.0, 1.0, 1.0, 0.0,  # top right
            -1.0, -1.0, 0.0, 1.0,  # bottom left
            1.0, -1.0, 1.0, 1.0,  # bottom right
        ]))
