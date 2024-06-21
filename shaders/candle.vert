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