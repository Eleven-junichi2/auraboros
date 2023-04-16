from array import array
from pathlib import Path
from typing import Any
import os


import moderngl
import pygame

# from . import global_

with open(Path(__file__).parent / "default.vert", "r") as f:
    VERTEX_DEFAULT = f.read()
with open(Path(__file__).parent / "default.frag", "r") as f:
    FRAGMENT_DEFAULT = f.read()


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Shader2D(metaclass=Singleton):
    """2Dシェーダーを表すシングルトンクラス。

    Attributes:
        ctx (moderngl.Context): ModernGLのコンテキストオブジェクト。
        textures (dict): テクスチャオブジェクトを格納する辞書。
        programs (dict): シェーダープログラムオブジェクトを格納する辞書。
        vaos (dict): 頂点配列オブジェクトを格納する辞書。
        buffer (moderngl.Buffer): 頂点バッファオブジェクト。
    """

    def __init__(self):
        self.ctx = moderngl.create_context()
        self.textures: dict[Any, moderngl.Texture] = {}
        self.programs: dict[Any, moderngl.Program] = {}
        self.vaos: dict[Any, moderngl.VertexArray] = {}
        self.buffer: dict[Any, moderngl.Buffer] = self.ctx.buffer(
            data=array("f", [
                # x, y, u ,v
                -1.0, 1.0, 0.0, 0.0,  # top left
                1.0, 1.0, 1.0, 0.0,  # top right
                -1.0, -1.0, 0.0, 1.0,  # bottom left
                1.0, -1.0, 1.0, 1.0,  # bottom right
            ]))

        self.compile_and_register_program(
            vertex=VERTEX_DEFAULT,
            fragment=FRAGMENT_DEFAULT,
            program_name="display_surface")

    def compile_and_register_program(self, vertex, fragment, program_name):
        """

        Args:
            vertex (str): 頂点シェーダーのソースコード。
            fragment (str): フラグメントシェーダーのソースコード。
            program_name (str): シェーダープログラムの名前。
        """
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
        if os.name == 'nt':
            # Windows
            texture.swizzle = 'BGRA'
        return texture

    def register_surface_as_texture(
            self, surface: pygame.surface.Surface, texture_name):
        """PygameのSurfaceオブジェクトをテクスチャとして登録する。

        Args:
            surface (pygame.surface.Surface): PygameのSurfaceオブジェクト。
            texture_name (str): テクスチャの名前。

        Notes:
            テクスチャが辞書に登録されていない場合は、
            PygameのSurfaceオブジェクトからテクスチャオブジェクトを作成し、
            辞書に登録する。
            テクスチャオブジェクトにSurfaceオブジェクトのデータを書き込む。
        """
        if texture_name not in self.textures:
            texture = self._surface_to_texture(surface)
            self.textures[texture_name] = texture
        buffer = surface.get_view("1")
        self.textures[texture_name].write(buffer)

    def use_texture(self, texture_name, id):
        """texture_nameでtextures辞書に登録されたテクスチャを指定し、使用を切り替えます。
        renderメソッドを実行した際、これで指定したテクスチャに描画されます。

        Args:
            texture_name (str): テクスチャの名前。
            id (int): テクスチャのID。
        """
        self.textures[texture_name].use(id)

    def set_uniform(self, program_name, uniform, value):
        """シェーダープログラムのuniformに値を設定する。

        Args:
            program_name (str): シェーダープログラムの名前。
            uniform (str): uniform変数の名前。
            value (any): uniform変数に設定する値。
        """
        self.programs[program_name][uniform].value = value

    def render(self):
        for program_name in self.programs:
            self.vaos[program_name].render(mode=moderngl.TRIANGLE_STRIP)
