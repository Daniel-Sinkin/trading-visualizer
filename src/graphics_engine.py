import os
from abc import ABC, abstractmethod

import moderngl as mgl
import numpy as np
from moderngl import Buffer, Context, Program, VertexArray  # noqa: F401

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame as pg  # noqa: E402


class GraphicsEngine:
    def __init__(self):
        self.setup_pygame_and_opengl()

        self.is_running = True

    def setup_pygame_and_opengl(self) -> None:
        pg.init()

        self.clock = pg.time.Clock()

        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(
            pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE
        )
        pg.display.gl_set_attribute(pg.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)

        self.pg_window: pg.Surface = pg.display.set_mode(
            (1600, 900), flags=pg.OPENGL | pg.DOUBLEBUF
        )

        self.ctx: Context = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

    def handle_events(self) -> None:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False

    def update(self) -> None:
        pass

    def render(self) -> None:
        self.ctx.clear(1.0, 0.0, 1.0)

        pg.display.flip()

    def iteration(self) -> None:
        self.handle_events()
        self.update()
        self.render()

    def run(self) -> None:
        while self.is_running:
            self.iteration()

            self.clock.tick(60.0)


class BaseObject(ABC):
    def __init__(self, app: GraphicsEngine):
        self.app: GraphicsEngine = app
        self.ctx = self.app.ctx

    def render(self) -> None:
        self.vao.render()

    def create_vao(self) -> None:
        self.vbo = self.ctx.buffer(self.get_vertex_data())
        self.program = self.get_program()

        self.vao = self.ctx.vertex_array(
            self.program,
            [
                (self.vbo, self.get_buffer_format(), *self.get_attributes()),
            ],
        )

    @abstractmethod
    def update(self) -> None: ...

    @abstractmethod
    def get_buffer_format(self) -> str: ...

    @abstractmethod
    def get_attributes(self) -> list[str]: ...

    @abstractmethod
    def get_vertex_data(self) -> np.ndarray: ...

    def get_program(self) -> Program:
        return self.ctx.program(
            vertex_shader=self.get_vertex_shader(),
            fragment_shader=self.get_fragment_shader(),
        )

    @abstractmethod
    def get_vertex_shader(self) -> str: ...

    @abstractmethod
    def get_fragment_shader(self) -> str: ...


class QuadBaseObject(ABC):
    pass
