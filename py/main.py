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
# GAME Class: Handles logic and graphics
#-------------------------------------------------------------------------------
class Game(object):
    """ Display and interact with the world
    """
    def __init__(self):
        pygame.display.set_caption(WINCAPT)
        self.fps_clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode(WND_SIZE)
        self.fsb_font = pygame.font.SysFont('Ubuntu-L', 16, bold=False,
                                            italic=False)

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

            # Graphics update
            self.draw_world()
            pygame.display.update()
            self.fps_clock.tick(FPS_RATE)

if __name__ == '__main__':
    pygame.init()
    game = Game()
    game.run()
