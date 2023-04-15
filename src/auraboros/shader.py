from array import array
from typing import Any

import moderngl
import pygame


class Shader2D:

    # def __init__(self):
    #     self.ctx = moderngl.create_context()
    #     self.textures: dict[Any, moderngl.Texture] = {}
    #     self.programs: dict[Any, moderngl.Program] = {}
    #     self.vaos: dict[Any, moderngl.VertexArray] = {}
    #     self.buffer = self.ctx.buffer(data=array("f", [
    #         # x, y, u ,v
    #         -1.0, 1.0, 0.0, 0.0,  # top left
    #         1.0, 1.0, 1.0, 0.0,  # top right
    #         -1.0, -1.0, 0.0, 1.0,  # bottom left
    #         1.0, -1.0, 1.0, 1.0,  # bottom right
    #     ]))

    _instance = None
    ctx: moderngl.Context
    textures: dict[Any, moderngl.Texture]
    programs: dict[Any, moderngl.Program]
    vaos: dict[Any, moderngl.VertexArray]
    buffer: moderngl.Buffer

    def __new__(cls) -> "Shader2D":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.ctx = moderngl.create_context()
            cls._instance.textures = {}
            cls._instance.programs = {}
            cls._instance.vaos = {}
            cls._instance.buffer = cls._instance.ctx.buffer(data=array("f", [
                # x, y, u ,v
                -1.0, 1.0, 0.0, 0.0,  # top left
                1.0, 1.0, 1.0, 0.0,  # top right
                -1.0, -1.0, 0.0, 1.0,  # bottom left
                1.0, -1.0, 1.0, 1.0,  # bottom right
            ]))
        return cls._instance

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
        # texture.swizzle = "BGRA" if windows
        return texture

    def register_surface_as_texture(
            self, surface: pygame.surface.Surface, texture_name):
        if texture_name not in self.textures:
            texture = self._surface_to_texture(surface)
            self.textures[texture_name] = texture
        buffer = surface.get_view("1")
        self.textures[texture_name].write(buffer)

    # def update_shader(self, program_name, uniform):
    #     texture_id = 0
    #     for texture_name in self.textures:
    #         self.textures[texture_name].use(texture_id)
    #         self.programs[program_name][uniform].value = texture_id
    #         texture_id += 1

    def use_texture(self, texture_name, id):
        self.textures[texture_name].use(id)

    def set_uniform(self, program_name, uniform, value):
        self.programs[program_name][uniform].value = value

    def render(self, program_name, uniform):
        # self.textures[texture_name].use(0)
        # self.programs[program_name][uniform].value = 0
        # self.update_shader(program_name, uniform)
        self.vaos[program_name].render(mode=moderngl.TRIANGLE_STRIP)
