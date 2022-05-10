import numpy
from OpenGL.GL import *
import pygame
from pygame.locals import *

try:
    from texturelib import Texture, WrappedTexture
except ImportError:
    from .texturelib import Texture, WrappedTexture

class PygameOpenGLWin:
    def __init__(self, dimensions, caption='Pygame OpenGL'):
        self.dimensions = dimensions

        pygame.init()
        pygame.display.set_mode(tuple(dimensions), HWSURFACE | OPENGL | DOUBLEBUF)
        pygame.display.set_caption(caption)

        glViewport(0, 0, *dimensions)

        self.config()

        #self.screen = pygame.Surface(dimensions)
        self.screen = pygame.Surface((dimensions[0], dimensions[1]), pygame.SRCALPHA)

        self.texcoords = [
            0.0, 1.0,
            0.0, 0.0,
            1.0, 0.0,
            1.0, 1.0
        ]

        self.base_vertices = [
            -1.0, 1.0,
            -1.0, -1.0,
            1.0, -1.0,
            1.0, 1.0,
        ]

        self.base_vertices = numpy.array(self.base_vertices, dtype=numpy.float32)
        self.texcoords = numpy.array(self.texcoords, dtype=numpy.float32)

        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, self.base_vertices)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, self.texcoords)

        self.fg_queue = []

    def config(self):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    def render_bg(self, wtex, pos, config={}):
        wtex.draw(pos, config=config)

    def render_fg(self, wtex, pos, config={}):
        self.fg_queue.append((wtex, pos, config))

    def update_clear(self, color=(0, 0, 0), config={}, shader=None):
        screen_tex = WrappedTexture(self.screen, self)
        if shader:
            screen_tex.set_shader(shader)
        screen_tex.draw((0, 0), config=config)

        for task in self.fg_queue:
            task[0].draw(task[1], config=task[2])

        screen_tex.delete()
        self.fg_queue = []

        pygame.display.flip()

        glClearColor(color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255 if len(color) > 3 else 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    def clear(self, color=(0, 0, 0)):
        pygame.display.flip()

        glClearColor(color[0] / 255, color[1] / 255, color[2] / 255, color[3] / 255 if len(color) > 3 else 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
