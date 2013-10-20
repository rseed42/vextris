#!/usr/bin/env python
#-------------------------------------------------------------------------------
import pygame
import sys
from pygame.locals import *
import numpy as np
#-------------------------------------------------------------------------------
WND_TITLE = 'VexTris'
FPS_RATE = 30
# Dimensions
FIELD_SIZE = np.array([320, 600])
# Top, left, right, bottom
MARGINS = np.array([20,20,120,40])
WND_SIZE = FIELD_SIZE + MARGINS[:2] + MARGINS[2:]
FIELD = np.concatenate((MARGINS[:2], FIELD_SIZE))
# Draw borders around the field so that figures inside are not affected
FIELD_BORDER = FIELD.copy() + np.array([-1,-1,2,2])
FIELD_BORDER_COL = pygame.Color(120, 120, 120)
# Colors
WHITE = pygame.Color(255,255,255)
BLACK = pygame.Color(0,0,0)
RED = pygame.Color(255,0,0)
GREEN = pygame.Color(0,255,0)
BLUE = pygame.Color(0,0,255)
#-------------------------------------------------------------------------------
# GAME Class: Handles logic and graphics
#-------------------------------------------------------------------------------
class Game(object):
    """ Display and interact with the world
    """
    def __init__(self):
        pygame.display.set_caption(WND_TITLE)
        self.fps_clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode(WND_SIZE)
        self.fsb_font = pygame.font.SysFont('Ubuntu-L', 16, bold=False,
                                            italic=False)

    def draw_world(self):
        """ Update visual objects
        """
        self.surface.fill(BLACK)
        self.field = self.surface.subsurface(FIELD)



        self.world_rect = pygame.draw.rect(self.surface,
                                           FIELD_BORDER_COL,
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
