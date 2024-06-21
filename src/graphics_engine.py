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

        self.screen_offset: vec2 = vec2(0.0, 0.0)
        self.screen_offset_floating: vec2 = vec2(0.0, 0.0)
        self.screen_move_anchor: Optional[tuple[int, int]] = None

        self.panning_speed = 1.5

        self.setup_objects()
        self.is_running = True

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

        match event.type:
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

        print(self.screen_offset_floating)

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
    def update(self):
        self.program["u_mouse_position"] = pg.mouse.get_pos()
        self.program["u_time"] = self.app.time

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

        uniform vec2 u_mouse_position;
        uniform float u_time;
        
        void main() {
            float dist = distance(gl_FragCoord.xy * vec2(1.0, -1.0) + vec2(0.0, 900), u_mouse_position);
            float time_factor = 50.0 + 25.0 * sin(u_time * 3.14159);
            dist = clamp(dist, 0.0, time_factor) / time_factor;
            fragColor = vec4(vec3(0.17, 0.17, 0.25), 1.0) * vec4(vec3(dist), 1.0);
        }
        """


class Candle(QuadObject):
    def __init__(self, app: GraphicsEngine, pos: vec2, scale: vec2, is_positive: bool):
        super().__init__(app)
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
        return """
        #version 330
        in vec2 in_position;

        uniform vec2 u_screen_size;
        uniform vec2 u_position;
        uniform vec2 u_scale;

        uniform vec2 u_screen_offset;
        uniform vec2 u_screen_offset_floating;

        void main() {
            float aspect_ratio = u_screen_size.x / u_screen_size.y;

            // Apply scale and position
            vec2 scaled_position = in_position * u_scale;
            vec2 transformed_position = scaled_position + u_position;

            vec4 position = vec4(transformed_position / vec2(aspect_ratio, 1.0), 0.0, 1.0);

            position.xy += u_screen_offset * vec2(1.0, -1.0) + u_screen_offset_floating * vec2(1.0, -1.0);

            gl_Position = position;
        }
        """

    def get_fragment_shader(self) -> str:
        return """
        #version 330
        out vec4 fragColor;
    
        uniform bool u_is_positive;
        uniform float u_time;

        // Simplex noise function declarations
        vec3 mod289(vec3 x) {
            return x - floor(x * (1.0 / 289.0)) * 289.0;
        }

        vec4 mod289(vec4 x) {
            return x - floor(x * (1.0 / 289.0)) * 289.0;
        }

        vec4 permute(vec4 x) {
            return mod289(((x*34.0)+1.0)*x);
        }

        vec4 taylorInvSqrt(vec4 r) {
            return 1.79284291400159 - 0.85373472095314 * r;
        }

        float snoise(vec3 v) {
            const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
            const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);

            vec3 i  = floor(v + dot(v, C.yyy) );
            vec3 x0 =   v - i + dot(i, C.xxx) ;

            vec3 g = step(x0.yzx, x0.xyz);
            vec3 l = 1.0 - g;
            vec3 i1 = min( g.xyz, l.zxy );
            vec3 i2 = max( g.xyz, l.zxy );

            vec3 x1 = x0 - i1 + C.xxx;
            vec3 x2 = x0 - i2 + C.yyy;
            vec3 x3 = x0 - D.yyy;

            i = mod289(i);
            vec4 p = permute( permute( permute(
                        i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
                    + i.y + vec4(0.0, i1.y, i2.y, 1.0 ))
                    + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));

            vec4 j = p - 49.0 * floor(p * (1.0 / 49.0));
            vec4 x_ = floor(j * (1.0 / 7.0));
            vec4 y_ = floor(j - 7.0 * x_);

            vec4 x = x_ * (1.0 / 7.0);
            vec4 y = y_ * (1.0 / 7.0);
            vec4 h = 1.0 - abs(x) - abs(y);

            vec4 b0 = vec4(x.xy, y.xy);
            vec4 b1 = vec4(x.zw, y.zw);

            vec4 s0 = floor(b0)*2.0 + 1.0;
            vec4 s1 = floor(b1)*2.0 + 1.0;
            vec4 sh = -step(h, vec4(0.0));

            vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
            vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;

            vec3 p0 = vec3(a0.xy,h.x);
            vec3 p1 = vec3(a0.zw,h.y);
            vec3 p2 = vec3(a1.xy,h.z);
            vec3 p3 = vec3(a1.zw,h.w);

            vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
            p0 *= norm.x;
            p1 *= norm.y;
            p2 *= norm.z;
            p3 *= norm.w;

            vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
            m = m * m;
            return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1),
                                        dot(p2,x2), dot(p3,x3) ) );
        }

        void main() {
            float noise = snoise(vec3(gl_FragCoord.xy * 0.01, u_time * 1.5));
            vec3 baseColor = u_is_positive ? vec3(0.2, 0.7, 0.05) : vec3(0.9, 0.0, 0.25);
            fragColor = vec4(baseColor + noise * 0.2, 1.0);
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
