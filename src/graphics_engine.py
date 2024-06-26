import os
from abc import ABC, abstractmethod
from typing import Optional

import moderngl as mgl
import numpy as np
from glm import mat4, vec2, vec3  # noqa: F401
from moderngl import Buffer, Context, Program, VertexArray  # noqa: F401

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame as pg  # noqa: E402


class GraphicsEngine:
    def __init__(self):
        self.window_size: tuple[int, int] = (1600, 900)
        self.aspect_ratio = self.window_size[0] / self.window_size[1]
        self.setup_pygame_and_opengl()

        self.screen_offset: vec2 = vec2(0.0, 0.0)
        self.screen_offset_floating: vec2 = vec2(0.0, 0.0)
        self.screen_move_anchor: Optional[tuple[int, int]] = None

        self.panning_speed = 1.5

        self.setup_objects()
        self.is_running = True

        self.animations = []
        if False:

            def screen_offset_right(self):
                self.screen_offset -= vec2(0.2 / 60.0, 0.0)

            self.animations.append((lambda: screen_offset_right(self), self.time + 2.0))

    def setup_pygame_and_opengl(self) -> None:
        pg.init()

        self.clock = pg.time.Clock()
        self.time = 0.0

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

        def screen_offset_anim_func(self, offset: vec2):
            self.screen_offset += offset

        match event.type:
            case pg.KEYDOWN:
                match event.key:
                    case pg.K_RIGHT:
                        self.animations.append(
                            (
                                lambda: screen_offset_anim_func(
                                    self, -vec2(1.0 / 50.0, 0.0) / self.aspect_ratio
                                ),
                                self.time + 2.0,
                            )
                        )
                    case pg.K_LEFT:
                        self.animations.append(
                            (
                                lambda: screen_offset_anim_func(
                                    self, vec2(1.0 / 50.0, 0.0) / self.aspect_ratio
                                ),
                                self.time + 2.0,
                            )
                        )
                    case pg.K_UP:
                        self.animations.append(
                            (
                                lambda: screen_offset_anim_func(
                                    self, vec2(0.0, 1.0 / 50.0)
                                ),
                                self.time + 2.0,
                            )
                        )
                    case pg.K_DOWN:
                        self.animations.append(
                            (
                                lambda: screen_offset_anim_func(
                                    self, -vec2(0.0, 1.0 / 50.0)
                                ),
                                self.time + 2.0,
                            )
                        )
            case pg.MOUSEBUTTONDOWN:
                if event.button == pg.BUTTON_RIGHT:
                    self.screen_move_anchor = pg.mouse.get_pos()
            case pg.MOUSEBUTTONUP:
                if event.button == pg.BUTTON_RIGHT:
                    self.mouse_delta: vec2 = vec2(pg.mouse.get_pos()) - vec2(
                        self.screen_move_anchor
                    )
                    self.screen_offset += (
                        self.panning_speed * self.mouse_delta / vec2(self.window_size)
                    )
                    self.screen_offset_floating = vec2(0.0, 0.0)
                    self.screen_move_anchor = None

    def update(self) -> None:
        self.background.update()
        self.scene.update()

        if self.screen_move_anchor is not None:
            self.mouse_delta: vec2 = vec2(pg.mouse.get_pos()) - vec2(
                self.screen_move_anchor
            )
            self.screen_offset_floating = (
                self.panning_speed * self.mouse_delta / vec2(self.window_size)
            )

        self.animations = [anim for anim in self.animations if anim[1] > self.time]
        for anim in self.animations:
            anim[0]()

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
            self.time = pg.time.get_ticks() / 1000.0


class Scene:
    """Handles the rendering and updating of objects in the scene."""

    def __init__(self, app: GraphicsEngine):
        self.app: GraphicsEngine = app
        self.ctx: Context = app.ctx

        self.objects: list[BaseObject] = [
            Candle(self.app, vec2(0.0, 0.0), vec2(0.1, 0.3), is_positive=True),
            Candle(self.app, vec2(0.2, -0.1), vec2(0.1, 0.4), is_positive=False),
            Candle(self.app, vec2(0.4, -0.3), vec2(0.1, 0.2), is_positive=True),
            Candle(self.app, vec2(0.6, 0.1), vec2(0.1, 0.2), is_positive=True),
            Candle(self.app, vec2(0.8, 0.0), vec2(0.1, 0.3), is_positive=False),
        ]
        for obj in self.objects:
            if isinstance(obj, Candle):
                print(f"<{obj.start_position.x:.2f}, {obj.start_position.y:.2f}>")
                print(f"<{obj.end_position.x:.2f}, {obj.end_position.y:.2f}>")
                print()

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
        return np.load("data/quad_vertex_data.npy")


class Background(QuadObject):
    def update(self):
        self.program["u_mouse_position"] = pg.mouse.get_pos()
        self.program["u_time"] = self.app.time

    def get_vertex_shader(self) -> str:
        with open("shaders/background.vert", "r") as file:
            return file.read()

    def get_fragment_shader(self) -> str:
        with open("shaders/background.frag", "r") as file:
            return file.read()


class Candle(QuadObject):
    def __init__(self, app: GraphicsEngine, pos: vec2, scale: vec2, is_positive: bool):
        super().__init__(app)
        self.position: vec2 = pos  # Center position
        self.scale: vec2 = scale
        self.is_positive: bool = is_positive

        self.program["u_screen_size"] = self.app.window_size
        self.program["u_position"] = pos
        self.program["u_scale"] = scale
        self.program["u_is_positive"] = is_positive
        self.program["u_screen_offset"] = self.app.screen_offset
        self.program["u_screen_offset_floating"] = self.app.screen_offset_floating
        self.program["u_time"] = 0.0

        self.outline_program: Program = self.get_outline_program()
        self.outline_program["u_screen_size"] = self.app.window_size
        self.outline_program["u_position"] = pos
        self.outline_program["u_scale"] = scale
        self.outline_program["u_line_width"] = 0.005
        self.outline_program["u_screen_offset"] = self.app.screen_offset
        self.outline_program["u_screen_offset_floating"] = (
            self.app.screen_offset_floating
        )

        self.outline_vao: VertexArray = self.create_outline_vao()

    def update(self) -> None:
        self.program["u_screen_offset"] = self.app.screen_offset
        self.program["u_screen_offset_floating"] = self.app.screen_offset_floating
        self.program["u_time"] = self.app.time
        self.outline_program["u_screen_offset"] = self.app.screen_offset
        self.outline_program["u_screen_offset_floating"] = (
            self.app.screen_offset_floating
        )

    def create_outline_vao(self) -> VertexArray:
        outline_vbo: Buffer = self.ctx.buffer(self.get_outline_vertex_data())
        return self.ctx.vertex_array(
            self.outline_program,
            [
                (outline_vbo, self.get_buffer_format(), *self.get_attributes()),
            ],
        )

    def get_vertex_shader(self) -> str:
        with open("shaders/candle.vert", "r") as file:
            return file.read()

    def get_fragment_shader(self) -> str:
        with open("shaders/candle.frag", "r") as file:
            return file.read()

    def get_outline_program(self) -> Program:
        return self.ctx.program(
            vertex_shader=self.get_vertex_shader(),
            fragment_shader=self.get_outline_fragment_shader(),
            geometry_shader=self.get_outline_geometry_shader(),
        )

    def get_outline_fragment_shader(self) -> str:
        with open("shaders/candle_outline.frag", "r") as file:
            return file.read()

    def get_outline_geometry_shader(self) -> str:
        with open("shaders/candle_outline.geom", "r") as file:
            return file.read()

    def get_outline_vertex_data(self) -> np.ndarray:
        return np.load("data/outline_vertex_data.npy")

    def render(self) -> None:
        self.outline_vao.render(mgl.LINE_LOOP)

        self.vao.render(self.render_mode)

    @property
    def top_left_position(self) -> vec2:
        return self.position - self.scale / 2.0

    @property
    def bottom_right_position(self) -> vec2:
        return self.position + self.scale / 2.0

    @property
    def top_right_position(self) -> vec2:
        return vec2(self.bottom_right_position.x, self.top_left_position.y)

    @property
    def bottom_left_position(self) -> vec2:
        return vec2(self.top_left_position.x, self.bottom_right_position.y)

    @property
    def start_position(self) -> vec2:
        if self.is_positive:
            return self.bottom_left_position
        else:
            return self.top_left_position

    @property
    def end_position(self) -> vec2:
        if self.is_positive:
            return self.top_right_position
        else:
            return self.bottom_right_position
