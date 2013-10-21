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
FIELD_CENTER = 0.5*FIELD_SIZE
# Top, left, right, bottom
MARGINS = np.array([20,20,120,40])
WND_SIZE = FIELD_SIZE + MARGINS[:2] + MARGINS[2:]
FIELD = np.concatenate((MARGINS[:2], FIELD_SIZE))
# Draw borders around the field so that figures inside are not affected
FIELD_BORDER = FIELD.copy() + np.array([-1,-1,2,2])
FIELD_BORDER_COL = pygame.Color(64,64,64)
# Colors
WHITE = pygame.Color(255,255,255)
BLACK = pygame.Color(0,0,0)
RED = pygame.Color(255,0,0)
GREEN = pygame.Color(0,255,0)
HEXGRID_COL = pygame.Color(48,48,48)
BLUE = pygame.Color(0,0,255)
# Math
DEG60 = np.pi/3
# Better be odd!
HEX_NUM_HORIZ = 13
# Maybe should make sure the result is an integer
HALF_HEX_NUM = HEX_NUM_HORIZ/2
SQRT3 = np.sqrt(3)
HEIGHT_COEFF = 0.5*SQRT3
RADIUS = 2.*(FIELD_SIZE[0]/(3.*HEX_NUM_HORIZ  + 1.))
# Whole height
HEIGHT = SQRT3*RADIUS
# We also need to calculate how many fit in horizontally
HEX_NUM_VERT = int(np.floor(FIELD_SIZE[1]/HEIGHT))
# Offset vertically by the empty space due to imprecise number of hexagons
OFFSET = np.array([0.5*RADIUS,
                   HEIGHT_COEFF*RADIUS + FIELD_SIZE[1] - HEX_NUM_VERT*HEIGHT])
print HEX_NUM_HORIZ, HEX_NUM_VERT
HEXMAP = np.zeros((HEX_NUM_VERT, HEX_NUM_HORIZ, 3))
#HEXMAP[0,0,:] = (16, 16, 128)
HEXMAP[HEX_NUM_VERT-1,:,:] = (16, 16, 128)
#-------------------------------------------------------------------------------
# GAME Class: Handles logic and graphics
#-------------------------------------------------------------------------------
# Use a matrix
def hex2pix(q,r):
    x = RADIUS * 1.5 * q + 0.5*RADIUS
    y = RADIUS * SQRT3 * (r + 0.5*q)
    return np.array([x,y]) + OFFSET

class Game(object):
    """ Display and interact with the world
    """
    def __init__(self):
        pygame.display.set_caption(WND_TITLE)
        self.fps_clock = pygame.time.Clock()
        self.surface = pygame.display.set_mode(WND_SIZE)
        self.fsb_font = pygame.font.SysFont('Ubuntu-L', 16, bold=False,
                                            italic=False)
        self.hexagon = np.zeros((6,2))
        for i in xrange(6):
            angle = i*DEG60
            self.hexagon[i][0] = RADIUS * np.cos(angle)
            self.hexagon[i][1] = RADIUS * np.sin(angle)


    def draw_world(self):
        """ Update visual objects
        """
        self.surface.fill(BLACK)
        self.field = self.surface.subsurface(FIELD)


        for r in xrange(-1, HEXMAP.shape[0]):
            for q in xrange(HEXMAP.shape[1]):
                # Coordinates for r must be corrected due to romboidal
                # (non-perpendicular angle between the axes) shape.
                s = r - q/2
                if r >= 0:
                    hexpoly = pygame.draw.polygon(self.field,
                                                  HEXMAP[r, q],
                                                  self.hexagon + hex2pix(q,s),
                                                  0
                    )
                hexborder = pygame.draw.aalines(self.field,
                                                HEXGRID_COL,
                                                True,
                                                self.hexagon + hex2pix(q,s))


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
