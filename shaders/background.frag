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