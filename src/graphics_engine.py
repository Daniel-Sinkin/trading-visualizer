import os
from abc import ABC, abstractmethod

import moderngl as mgl
import numpy as np
from glm import mat4, vec3  # noqa: F401
from moderngl import Buffer, Context, Program, VertexArray  # noqa: F401

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame as pg  # noqa: E402


class GraphicsEngine:
    def __init__(self):
        self.setup_pygame_and_opengl()

        self.setup_objects()

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

    def setup_objects(self) -> None:
        self.background = Background(self)
        self.scene = Scene(self)

    def handle_event(self, event) -> None:
        if event.type == pg.QUIT:
            self.is_running = False

    def update(self) -> None:
        self.background.update()
        self.scene.update()

    def render(self) -> None:
        self.ctx.clear(1.0, 0.0, 1.0)

        self.background.render()
        pg.display.flip()

    def iteration(self) -> None:
        for event in pg.event.get():
            self.handle_event(event)
        self.update()
        self.render()

    def run(self) -> None:
        while self.is_running:
            self.iteration()

            self.clock.tick(60.0)


class Scene:
    """Handles the rendering and updating of objects in the scene."""

    def __init__(self, app: GraphicsEngine):
        self.app: GraphicsEngine = app
        self.ctx: Context = app.ctx

        self.objects: list[BaseObject] = [Candle(self.app)]

    def update(self):
        for obj in self.objects:
            obj.update()

    def render(self):
        for obj in self.objects:
            obj.render()


class BaseObject(ABC):
    def __init__(self, app: GraphicsEngine):
        self.app: GraphicsEngine = app
        self.ctx: Context = app.ctx

        self.render_mode = 0

        self.on_init()

        self.create_vao()

    @abstractmethod
    def on_init(self) -> None:
        """Called when the object is initialized but before the VAO is created."""
        pass

    def render(self) -> None:
        self.vao.render(self.render_mode)

    def update(self) -> None:
        pass

    def create_vao(self) -> None:
        self.vbo: Buffer = self.ctx.buffer(self.get_vertex_data())
        self.program: Program = self.get_program()

        self.vao: VertexArray = self.ctx.vertex_array(
            self.program,
            [
                (self.vbo, self.get_buffer_format(), *self.get_attributes()),
            ],
        )

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


class QuadObject(BaseObject):
    def on_init(self) -> None:
        """Initialization tasks specific to QuadObject."""
        self.render_mode = mgl.TRIANGLE_STRIP

    def get_buffer_format(self) -> str:
        return "2f"

    def get_attributes(self) -> list[str]:
        return ["in_position"]

    def get_vertex_data(self) -> np.ndarray:
        # Define the vertex data for a quad
        # fmt: off
        vertex_data = np.array([
            -1.0, -1.0,
             1.0, -1.0,
            -1.0,  1.0,
             1.0,  1.0,
        ], dtype=np.float32)
        # fmt: on
        return vertex_data


class Background(QuadObject):
    def get_fragment_shader(self) -> str:
        return """
        #version 330
        out vec4 fragColor;
        void main() {
            fragColor = vec4(vec3(0.17, 0.17, 0.25), 1.0);
        }
        """

    def get_vertex_shader(self) -> str:
        return """
        #version 330
        in vec2 in_position;
        void main() {
            gl_Position = vec4(in_position, 0.0, 1.0);
        }
        """


class Candle(QuadObject):
    def get_fragment_shader(self) -> str:
        return """
        #version 330
        out vec4 fragColor;
        void main() {
            fragColor = vec4(vec3(1.0, 0.5, 0.0), 1.0);
        }
        """

    def get_vertex_shader(self) -> str:
        return """
        #version 330
        in vec2 in_position;
        void main() {
            gl_Position = vec4(0.25 * in_position, 0.0, 1.0);
        }
        """
