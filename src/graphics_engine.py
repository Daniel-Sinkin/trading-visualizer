import os
from abc import ABC, abstractmethod
from typing import Optional

import moderngl as mgl
import numpy as np
from glm import mat4, vec2, vec3
from moderngl import Buffer, Context, Program, VertexArray  # noqa: F401

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame as pg  # noqa: E402


class GraphicsEngine:
    def __init__(self):
        self.window_size: tuple[int, int] = (1600, 900)
        self.setup_pygame_and_opengl()

        self.setup_objects()

        self.screen_move_anchor: Optional[tuple[int, int]] = None

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
            self.window_size, flags=pg.OPENGL | pg.DOUBLEBUF
        )

        self.ctx: Context = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)

    def setup_objects(self) -> None:
        self.background = Background(self)
        self.scene = Scene(self)

    def handle_event(self, event) -> None:
        if event.type == pg.QUIT or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            self.is_running = False

        match event.type:
            case pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_RIGHT:
                    self.screen_move_anchor = pg.mouse.get_pos()
            case pg.MOUSEBUTTONUP:
                if event.button == pg.BUTTON_RIGHT:
                    self.screen_move_anchor = None

    def update(self) -> None:
        self.background.update()
        self.scene.update()

    def render(self) -> None:
        self.ctx.clear(1.0, 0.0, 1.0)

        self.scene.render()
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

        self.objects: list[BaseObject] = [
            Candle(self.app, vec2(0.0, 0.0), vec2(0.1, 0.3), is_positive=True),
            Candle(self.app, vec2(0.2, -0.1), vec2(0.1, 0.4), is_positive=False),
            Candle(self.app, vec2(0.4, -0.3), vec2(0.1, 0.2), is_positive=True),
        ]

    def update(self) -> None:
        for obj in self.objects:
            obj.update()

    def render(self) -> None:
        for obj in self.objects:
            obj.render()


class BaseObject(ABC):
    def __init__(self, app: GraphicsEngine):
        self.app: GraphicsEngine = app
        self.ctx: Context = app.ctx

        self.render_mode = 0
        self.create_vao()

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
    def __init__(self, app: GraphicsEngine) -> None:
        super().__init__(app)
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
    def get_vertex_shader(self) -> str:
        return """
        #version 330
        in vec2 in_position;
        void main() {
            gl_Position = vec4(in_position, 0.0, 1.0);
        }
        """

    def get_fragment_shader(self) -> str:
        return """
        #version 330
        out vec4 fragColor;
        void main() {
            fragColor = vec4(vec3(0.17, 0.17, 0.25), 1.0);
        }
        """


class Candle(QuadObject):
    def __init__(self, app: GraphicsEngine, pos: vec2, scale: vec2, is_positive: bool):
        super().__init__(app)
        self.program["u_screen_size"] = self.app.window_size
        self.program["u_position"] = pos
        self.program["u_scale"] = scale
        self.program["u_is_positive"] = is_positive

        self.outline_program: Program = self.get_outline_program()
        self.outline_program["u_screen_size"] = self.app.window_size
        self.outline_program["u_position"] = pos
        self.outline_program["u_scale"] = scale
        self.outline_program["u_line_width"] = 0.005

        self.outline_vao: VertexArray = self.create_outline_vao()

    def create_outline_vao(self) -> VertexArray:
        outline_vbo: Buffer = self.ctx.buffer(self.get_outline_vertex_data())
        return self.ctx.vertex_array(
            self.outline_program,
            [
                (outline_vbo, self.get_buffer_format(), *self.get_attributes()),
            ],
        )

    def get_vertex_shader(self) -> str:
        return """
        #version 330
        in vec2 in_position;

        uniform vec2 u_screen_size;
        uniform vec2 u_position;
        uniform vec2 u_scale;

        void main() {
            float aspect_ratio = u_screen_size.x / u_screen_size.y;

            // Apply scale and position
            vec2 scaled_position = in_position * u_scale;
            vec2 transformed_position = scaled_position + u_position;

            vec4 position = vec4(transformed_position / vec2(aspect_ratio, 1.0), 0.0, 1.0);

            gl_Position = position;
        }
        """

    def get_fragment_shader(self) -> str:
        return """
        #version 330
        out vec4 fragColor;
        
        uniform bool u_is_positive;

        void main() {
            if (u_is_positive) {
                fragColor = vec4(vec3(0.0, 0.8, 0.05), 1.0);
            } else {
                fragColor = vec4(vec3(0.8, 0.0, 0.05), 1.0);
            }
        }
        """

    def get_outline_program(self) -> Program:
        return self.ctx.program(
            vertex_shader=self.get_vertex_shader(),
            fragment_shader=self.get_outline_fragment_shader(),
            geometry_shader=self.get_outline_geometry_shader(),
        )

    def get_outline_fragment_shader(self) -> str:
        return """
        #version 330
        out vec4 fragColor;

        void main() {
            fragColor = vec4(0.0, 0.0, 0.0, 1.0);  // Black color for outline
        }
        """

    def get_outline_geometry_shader(self) -> str:
        return """
        #version 330 core
        layout(lines) in;
        layout(triangle_strip, max_vertices = 4) out;

        uniform float u_line_width;
        uniform vec2 u_screen_size;

        void main() {
            float aspect_ratio = u_screen_size.x / u_screen_size.y;
            vec2 aspect_correction = vec2(aspect_ratio, 1.0);

            for (int i = 0; i < 2; ++i) {
                vec2 direction = normalize((gl_in[(i + 1) % 2].gl_Position.xy - gl_in[i].gl_Position.xy) * aspect_correction);
                vec2 normal = vec2(-direction.y, direction.x) * u_line_width / 2.0;

                gl_Position = gl_in[i].gl_Position + vec4(normal / aspect_correction, 0.0, 0.0);
                EmitVertex();

                gl_Position = gl_in[i].gl_Position - vec4(normal / aspect_correction, 0.0, 0.0);
                EmitVertex();

                gl_Position = gl_in[(i + 1) % 2].gl_Position + vec4(normal / aspect_correction, 0.0, 0.0);
                EmitVertex();

                gl_Position = gl_in[(i + 1) % 2].gl_Position - vec4(normal / aspect_correction, 0.0, 0.0);
                EmitVertex();

                EndPrimitive();
            }
        }
        """

    def get_outline_vertex_data(self) -> np.ndarray:
        # Define the vertex data for a quad
        # fmt: off
        vertex_data = np.array([
            -1.0, -1.0,
             1.0, -1.0,
             1.0,  1.0,
            -1.0,  1.0,
        ], dtype=np.float32)
        # fmt: on
        return vertex_data

    def render(self) -> None:
        self.outline_vao.render(mgl.LINE_LOOP)

        self.vao.render(self.render_mode)
