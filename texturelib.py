from ctypes import *

import numpy
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GL.ARB.framebuffer_object import *
from OpenGL.GL.EXT.framebuffer_object import *

import pygame

class Texture:
    def __init__(self, src):
        if type(src) == str: # file source
            self.img = pygame.image.load(src)
        else: # surface source
            self.img = src

        self.tex_data = pygame.image.tostring(self.img, 'RGBA', 1)
        self.width = self.img.get_width()
        self.height = self.img.get_height()
        self.tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST) # GL_LINEAR_MIPMAP_LINEAR
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.tex_data)

    def set(self):
        glBindTexture(GL_TEXTURE_2D, self.tex_id)

    def delete(self):
        glDeleteTextures(1, [self.tex_id])

class WrappedTexture:
    def __init__(self, src, window=None):
        self.texture = Texture(src)
        self.window = window
        self.wdimensions = window.dimensions if window else self.texture.img.get_size()

        self.scale = [self.texture.width / self.wdimensions[0], self.texture.height / self.wdimensions[1]]

        self.shader = None

    def set_shader(self, shader):
        self.shader = shader

    def draw(self, pos, config={}):
        vec_rect = (pos[0] / self.wdimensions[0] * 2, pos[1] / self.wdimensions[1] * 2, self.scale[0], self.scale[1])

        if self.shader:
            self.shader.apply_rect(vec_rect)
            if self.shader.primary_tex:
                config[self.shader.primary_tex] = self.texture
            self.shader.apply(config)

        glDrawArrays(GL_QUADS, 0, 4) # the 4 is the vertex count

    def to_surf(self, config={}):
        # generate target texture and parameters
        render_target = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, render_target)
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.texture.width, self.texture.height, 0, GL_RGBA, GL_UNSIGNED_INT, None)

        # generate framebuffer
        fbo=c_uint(1)
        glGenFramebuffers(1, fbo)
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, fbo)
        glFramebufferTexture2DEXT(GL_FRAMEBUFFER_EXT, GL_COLOR_ATTACHMENT0_EXT, GL_TEXTURE_2D, render_target, 0)
        glPushAttrib(GL_VIEWPORT_BIT)

        glViewport(0, 0, self.texture.width, self.texture.height)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        self.draw((0, 0), config=config)

        # switch back to normal rendering
        glPopAttrib()
        glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)

        glBindTexture(GL_TEXTURE_2D, render_target)
        raw_tex_data = glGetTexImage(GL_TEXTURE_2D, 0, GL_RGBA, GL_UNSIGNED_BYTE)
        pg_surf = pygame.image.fromstring(raw_tex_data, (self.texture.width, self.texture.height), 'RGBA', True)

        glDeleteTextures(1, [render_target])
        glDeleteFramebuffers(1)

        return pg_surf

    def delete(self):
        self.texture.delete()
