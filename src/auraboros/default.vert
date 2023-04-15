#version 330 core

in vec2 in_vert;
in vec2 in_texcoord;
out vec2 uvs;

void main() {
    uvs = in_texcoord;
    gl_Position = vec4(in_vert, 0.0, 1.0);
}
