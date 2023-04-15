#version 330 core

uniform sampler2D display_surface;

in vec2 uvs;
out vec4 entire_screen_color;

void main() {
    entire_screen_color = vec4(
        texture(display_surface, uvs).rgb, 1.0);
}