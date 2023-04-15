from array import array
from pathlib import Path

import moderngl
import pygame

# from . import global_


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Shader2D(metaclass=Singleton):

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
        vertex, fragment = None, None
        with open(Path(__file__).parent / "default.vert", "r") as f:
            vertex = f.read()
        with open(Path(__file__).parent / "default.frag", "r") as f:
            fragment = f.read()
        self.compile_and_register_program(
            vertex=vertex,
            fragment=fragment,
            program_name="display_surface")

    def compile_and_register_program(self, vertex, fragment, program_name):
        vert_raw = vertex
        frag_raw = fragment
        program = self.ctx.program(
            vertex_shader=vert_raw, fragment_shader=frag_raw)
        self.programs[program_name] = program
        self.vaos[program_name] = self.ctx.vertex_array(
            program, [(self.buffer, "2f 2f", "in_vert", "in_texcoord")])

    def _surface_to_texture(self, surface: pygame.surface.Surface):
        texture = self.ctx.texture(surface.get_size(), 4)
        texture.filter = (moderngl.NEAREST, moderngl.NEAREST)
        return texture

    def register_surface_as_texture(
            self, surface: pygame.surface.Surface, texture_name):
        if texture_name not in self.textures:
            texture = self._surface_to_texture(surface)
            self.textures[texture_name] = texture
        buffer = surface.get_view("1")
        self.textures[texture_name].write(buffer)

    def use_texture(self, texture_name, id):
        self.textures[texture_name].use(id)

    def set_uniform(self, program_name, uniform, value):
        self.programs[program_name][uniform].value = value

    def let_render(self, program_name):
        pass

    def render(self):
        for program_name in self.programs:
            self.vaos[program_name].render(mode=moderngl.TRIANGLE_STRIP)
