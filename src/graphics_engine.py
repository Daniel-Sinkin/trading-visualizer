import os

import moderngl as mgl
from moderngl import Buffer, Context, Program, VertexArray  # noqa: F401

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame as pg  # noqa: E402


class GraphicsEngine:
    def __init__(self):
        self.setup_pygame_and_opengl()

        self.is_running = True

    def setup_pygame_and_opengl(self):
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

    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.is_running = False

    def update(self):
        pass

    def render(self):
        self.ctx.clear(1.0, 0.0, 1.0)

        pg.display.flip()

    def iteration(self) -> None:
        self.handle_events()
        self.update()
        self.render()

    def run(self) -> None:
        while self.is_running:
            self.iteration()

            self.clock.tick(15.0)
