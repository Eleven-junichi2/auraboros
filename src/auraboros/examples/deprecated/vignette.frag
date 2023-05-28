#version 330 core

in vec2 uvs;
out vec4 out_color;

uniform sampler2D display_texture;
uniform vec2 resolution;
uniform float radius;
uniform float softness;

void main() {
    vec4 color = texture(display_texture, uvs);

    float dist = length(uvs - vec2(0.5));
    float vignette = smoothstep(radius, radius - softness, dist);

    out_color = color * vignette;
}
