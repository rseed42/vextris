#!/usr/bin/env python
#-------------------------------------------------------------------------------
import pygame
import sys
from pygame.locals import *
import numpy as np
#-------------------------------------------------------------------------------
DEBUG = True
FIELD_SIZE = np.array([400, 600])
# Top, left, right, bottom
MARGINS = np.array([10,10,10,10])
WND_SIZE = FIELD_SIZE + MARGINS[:2] + MARGINS[2:]
WORLD_SIZE = np.array([660, 660])
WORLD_CENTER = 0.5*WORLD_SIZE
WORLD_OFFSET = np.array([20, 20])
WORLD_BORDER_COL = pygame.Color(255,255,255)
FIELD_BORDER = np.concatenate((MARGINS[:2], FIELD_SIZE))
WINCAPT = 'VexTris'
FPS_RATE = 30
INT_STEP = 1./FPS_RATE
BGCOL = pygame.Color(0,0,0)
WHITE = pygame.Color(255,255,255)
BLACK = pygame.Color(0,0,0)
RED = pygame.Color(170,10,10)
BLUE = pygame.Color(10,10,90)
ORANGE = pygame.Color(157,31,6)
GREEN = pygame.Color(10,90,10)
GRAY = pygame.Color(16,16,16)

#-------------------------------------------------------------------------------
# WORLD Class: The central object in the simulation
#-------------------------------------------------------------------------------
class World(object):
    def __init__(self, size, offset):
        self.objects = []
        self.pause = False

    def populate(self):
        """ Naive algorithm that has to be improved later.
            Do not use with a great number of objects!
        """
        pass

    def handle_object_collision(self, obj):
        pass

    def update(self):
        pass

#-------------------------------------------------------------------------------
# GAME Class: The GUI that allows us a glimpse into the world
#-------------------------------------------------------------------------------
class Game(object):
    """ Display and interact with the world
    """
    def __init__(self, world):
        pygame.display.set_caption(WINCAPT)
        self.fps_clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode(WND_SIZE)
        self.fsb_font = pygame.font.SysFont('Ubuntu-L', 16, bold=False,
                                            italic=False)
        self.world = world

    def draw_world(self):
        """ Update visual objects
        """
        self.surface.fill(BGCOL)
        self.world_rect = pygame.draw.rect(self.surface,
                                           WORLD_BORDER_COL,
                                           FIELD_BORDER,
                                           1
        )

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == KEYDOWN:
                    if event.key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
                        pass
                    if event.key == K_p:
                        self.world.pause = not self.world.pause
                    if event.key == K_s:
                        pass
                    if event.key == K_q:
                        pygame.quit()
                        sys.exit()
                    if event.key == K_ESCAPE:
                        pygame.event.post(pygame.event.Event(QUIT))

            # Dynamics update
            self.world.update()
            # Graphics update
            self.draw_world()
            pygame.display.update()
            self.fps_clock.tick(FPS_RATE)

if __name__ == '__main__':
    pygame.init()
    world = World(WORLD_SIZE, WORLD_OFFSET)
    world.populate()
    game = Game(world)
    game.run()
