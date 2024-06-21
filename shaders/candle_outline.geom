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