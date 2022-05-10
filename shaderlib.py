from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader

try:
    from texturelib import Texture, WrappedTexture
    from shader_constants import *
except ImportError:
    from .texturelib import Texture, WrappedTexture
    from .shader_constants import *

def read_f(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return data

class Uniform:
    def __init__(self, shader_obj, name, datatype):
        self.shader_obj = shader_obj
        self.datatype = datatype
        self.name = name
        self.uniform = glGetUniformLocation(shader_obj.program, name)

        self.tex_id = -1
        if datatype == UNIFORM_TEX:
            self.tex_id = shader_obj.tex_ids[name]

    def apply(self, value):
        if self.datatype != UNIFORM_TEX:
            if self.datatype in [UNIFORM_VEC2, UNIFORM_VEC3, UNIFORM_VEC4]:
                UNIFORM_MAP[self.datatype](self.uniform, *value)
            else:
                UNIFORM_MAP[self.datatype](self.uniform, value)
        else:
            # value is a Texture in this case
            UNIFORM_MAP[self.datatype](self.uniform, self.tex_id)
            glActiveTexture(GL_TEXTURES[self.tex_id])
            value.set()

class Shader:
    def __init__(self, frag_shader, vert_shader=None):
        self.frag_path = frag_shader + '.frag'
        self.vert_path = (vert_shader if vert_shader else frag_shader) + '.vert'

        self.vert_shader = compileShader(read_f(self.vert_path), GL_VERTEX_SHADER)
        self.frag_shader = compileShader(read_f(self.frag_path), GL_FRAGMENT_SHADER)

        self.program = glCreateProgram()
        glAttachShader(self.program, self.vert_shader)
        glAttachShader(self.program, self.frag_shader)
        glLinkProgram(self.program)

        self.uniforms = []
        self.tex_ids = {}
        self.next_tex_id = 0
        self.primary_tex = None

        self.rect_uniform = Uniform(self, 'rectVec', UNIFORM_VEC4)
        self.rect = (0.0, 0.0, 1.0, 1.0)

    def add_uniform(self, uniform_name, datatype):
        if datatype == UNIFORM_TEX:
            if not self.primary_tex:
                self.primary_tex = uniform_name

            self.tex_ids[uniform_name] = self.next_tex_id
            self.next_tex_id += 1

        self.uniforms.append(Uniform(self, uniform_name, datatype))

    def add_uniforms(self, uniform_map):
        for uniform in uniform_map:
            self.add_uniform(uniform, uniform_map[uniform])

    def apply_rect(self, vec4):
        self.rect = vec4

    def apply(self, config):
        glUseProgram(self.program)
        self.rect_uniform.apply(self.rect)
        for uniform in self.uniforms:
            if uniform.name in config:
                uniform.apply(config[uniform.name])

def shade_surf(surf, shader, config={}):
    tex = WrappedTexture(surf)
    tex.set_shader(shader)
    surf = tex.to_surf(config=config)
    tex.delete()
    return surf
