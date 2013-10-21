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
FIELD_BORDER_COL = np.array([64,64,64], dtype=np.uint8)
# Colors
WHITE = np.array([255,255,255], dtype=np.uint8)
BLACK = np.zeros(3, dtype=np.uint8)
RED = np.array([255, 0, 0], dtype=np.uint8)
GREEN = np.array([0, 255, 0], dtype=np.uint8)
HEXGRID_COL = np.array([48,48,48], dtype=np.uint8)
BLUE = np.array([0, 0, 255], dtype=np.uint8)
MAGENTA = np.array([128,0,128], dtype=np.uint8)
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
HEXMAP = np.zeros((HEX_NUM_VERT, HEX_NUM_HORIZ, 3))
# The bottom
HEXMAP[HEX_NUM_VERT-1,:,:] = (48,48,48)
# Define shapes

#CENTER = np.array([HEX_NUM_HORIZ/2, HEX_NUM_VERT/2], dtype=np.int64)
CENTER = np.array([HEX_NUM_VERT/2, HEX_NUM_HORIZ/2], dtype=np.int64)
# Remeber, coordinates are (v,h) due to hexmap structure
SHAPES = np.array([
    # 0 - Tetra
    [[0,0],[-1,0],[0,1],[0,-1]],
    # 1 - Rod
    [[0,0],[-1,0],[1,0],[2,0]],
    # 2 - Solid
    [[0,0],[0,1],[0,-1],[1,0]],
    # 3 - C
    [[-1,0],[-1,-1],[0,-1],[1,0]],
    # 4 - RL-Rod
    [[0,0],[-1,0],[1,0],[1,1]],
    # 5 - LL-Rod
    [[0,0],[-1,0],[1,0],[1,-1]],
    # 6 - R-Bent
    [[0,0],[-1,0],[0,1],[1,1]],
    # 7 - L-Bent
    [[0,0],[-1,0],[0,-1],[1,-1]],
    # 8 - R-T
    [[0,0],[-1,0],[0,1],[1,0]],
    # 9 - L-T
    [[0,0],[-1,0],[0,-1],[1,0]],
], dtype = np.int64)

pos =  SHAPES[9] + CENTER
print CENTER
# Find a way to index array directly
for p in pos:
    HEXMAP[p[0], p[1]] = BLUE


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
