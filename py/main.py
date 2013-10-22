#!/usr/bin/env python
#-------------------------------------------------------------------------------
#import pygame
import sys
from PyQt4 import QtCore, QtGui, QtOpenGL
try:
    from OpenGL import GL
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL 2dpainting",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)

import numpy as np
#-------------------------------------------------------------------------------
WND_TITLE = 'VexTris'
GOLDEN_RATIO = 0.5*(1+np.sqrt(5))
FPS_RATE = 30
# Dimensions
FIELD_WIDTH = 320
FIELD_HEIGHT = FIELD_WIDTH*GOLDEN_RATIO
FIELD_SIZE = np.array([FIELD_WIDTH, FIELD_HEIGHT])
FIELD_CENTER = 0.5*FIELD_SIZE
# Top, left, right, bottom
MARGINS = np.array([20,20,120,40])
#WND_SIZE = FIELD_SIZE + MARGINS[:2] + MARGINS[2:]
FIELD = np.concatenate((MARGINS[:2], FIELD_SIZE))
# Draw borders around the field so that figures inside are not affected
FIELD_BORDER = FIELD.copy() + np.array([-1,-1,2,2])
FIELD_BORDER_COL = np.array([64,64,64], dtype=np.uint8)
# Colors
WHITE = np.array([255,255,255], dtype=np.uint8)
BLACK = np.zeros(3, dtype=np.uint8)
RED = np.array([196, 0, 0], dtype=np.uint8)
GREEN = np.array([0, 196, 0], dtype=np.uint8)
HEXGRID_COL = np.array([48,48,48], dtype=np.uint8)
BLUE = np.array([0, 0, 196], dtype=np.uint8)
MAGENTA = np.array([128,0,128], dtype=np.uint8)
ORANGE = np.array([255, 128, 0], dtype=np.uint8)
VIOLETT = np.array([122, 32, 184], dtype=np.uint8)
DARK_CYAN = np.array([0, 128, 128], dtype=np.uint8)
CYAN = np.array([0, 196, 196], dtype=np.uint8)
YELLOW = np.array([196, 196, 0], dtype=np.uint8)
GREY = np.array([96, 96, 96], dtype=np.uint8)

BGCOL = BLACK
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
CENTER = np.array([HEX_NUM_VERT/2-1, HEX_NUM_HORIZ/2], dtype=np.int64)
TOP = np.array([2, HEX_NUM_HORIZ/2], dtype=np.int64)
# Remeber, coordinates are (v,h) due to hexmap structure
SHAPES = []
# 0 - Tetra
SHAPES.append( np.array([[[0,0],[-1,0],[0,1],[0,-1]],
                         [[0,0],[-1,1],[1,0],[-1,-1]]],
               dtype=np.int64))
# 1 - Rod
SHAPES.append( np.array([[[0,0],[-1,0],[1,0],[2,0]],
                         [[0,0],[-1,1],[0,-1],[1,-2]],
                         [[0,0],[-1,-1],[0,1],[1,2]]],
               dtype=np.int64))
# 2 - Solid
SHAPES.append( np.array([[[0,0],[0,-1],[1,0],[0,1]],
                         [[0,0],[-1,-1],[0,-1],[1,0]],
                         [[0,0],[-1,0],[-1,-1],[0,-1]],
                         [[0,0],[-1,1],[-1,0],[-1,-1]],
                         [[0,0],[0,1],[-1,1],[-1,0]],],
               dtype=np.int64))
# 3 - C
SHAPES.append( np.array([[[-1,0],[-1,-1],[0,-1],[1,0]],
                         [[-1,1],[-1,0],[-1,-1],[0,-1]],
                         [[0,1],[-1,1],[-1,0],[-1,-1]],
                         [[1,0],[0,1],[-1,1],[-1,0]],
                         [[0,-1],[1,0],[0,1],[-1,1]],
                         [[-1,-1],[0,-1],[1,0],[0,1]],],
               dtype=np.int64))
# 4 - RL-Rod
SHAPES.append( np.array([[[0,0],[-1,0],[1,0],[1,1]],
                         [[0,0],[-1,1],[0,-1],[1,-1]],
                         [[0,0],[0,1],[-1,-1],[0,-2]],
                         [[0,0],[1,0],[-1,0],[-2,-1]],
                         [[0,0],[0,-1],[-1,1],[-2,1]],
                         [[0,0],[-1,-1],[0,1],[0,2]],],
               dtype=np.int64))
# 5 - LL-Rod
SHAPES.append( np.array([[[0,0],[-1,0],[1,0],[1,-1]],
                         [[0,0],[-1,1],[0,-1],[0,-2]],
                         [[0,0],[0,1],[-1,-1],[-2,-1]],
                         [[0,0],[1,0],[-1,0],[-2,1]],
                         [[0,0],[0,-1],[-1,1],[0,2]],
                         [[0,0],[-1,-1],[0,1],[1,1]],],
               dtype=np.int64))
# 6 - R-Bent
SHAPES.append( np.array([[[0,0],[-1,0],[0,1],[1,1]],
                         [[0,0],[-1,1],[1,0],[1,-1]],
                         [[0,0],[0,1],[0,-1],[0,-2]],],
               dtype=np.int64))
# 7 - L-Bent
SHAPES.append( np.array([[[0,0],[-1,0],[0,-1],[1,-1]],
                         [[0,0],[-1,1],[-1,-1],[0,-2]],
                         [[0,0],[0,1],[-1,0],[-2,-1]],],
               dtype=np.int64))
# 8 - R-T
SHAPES.append( np.array([[[0,0],[-1,0],[0,1],[1,0]],
                         [[0,0],[-1,1],[0,-1],[1,0]],
                         [[0,0],[0,1],[-1,-1],[0,-1]],
                         [[0,0],[1,0],[-1,0],[-1,-1]],
                         [[0,0],[0,-1],[-1,1],[-1,0]],
                         [[0,0],[-1,-1],[0,1],[-1,1]],],
               dtype=np.int64))
# 9 - R-T
SHAPES.append( np.array([[[0,0],[-1,0],[0,-1],[1,0]],
                         [[0,0],[-1,1],[-1,-1],[0,-1]],
                         [[0,0],[0,1],[-1,0],[-1,-1]],
                         [[0,0],[1,0],[-1,0],[-1,1]],
                         [[0,0],[0,-1],[-1,1],[0,1]],
                         [[0,0],[-1,-1],[0,1],[1,0]],],
               dtype=np.int64))
PIECE_COLS = [ORANGE,BLUE,VIOLETT,GREEN,MAGENTA,DARK_CYAN,YELLOW,RED,CYAN,GREY]
SPEED = 0.05

#-------------------------------------------------------------------------------

# Use a matrix
def hex2pix(q,r):
    x = RADIUS * 1.5 * q + 0.5*RADIUS
    y = RADIUS * SQRT3 * (r + 0.5*q)
    return np.array([x,y]) + OFFSET
#-------------------------------------------------------------------------------
# Piece Class: Describes piece type, position, and orientation
#-------------------------------------------------------------------------------
class Piece(object):
    def __init__(self, type_id, pos, rot_id=0, color=None):
        self.type_id = type_id
        self.pos = pos
        # Use height for slower fall
        self.height = self.pos[0]
        self.rot_id = rot_id
        self.color = color
        if not self.color:
            self.color = PIECE_COLS[self.type_id]

    def hexagons(self):
        return SHAPES[self.type_id][self.rot_id].copy() + self.pos

    def rotate_left(self):
        self.rot_id = (self.rot_id - 1) % len(SHAPES[self.type_id])

    def rotate_right(self):
        self.rot_id = (self.rot_id + 1) % len(SHAPES[self.type_id])

    def fall(self, speed):
        self.height += speed
        self.pos[0] = int(np.floor(self.height))

#-------------------------------------------------------------------------------
# GAME Class: Handles logic and graphics
#-------------------------------------------------------------------------------

#class Game(object):
#    """ Display and interact with the world
#    """
#    def __init__(self):
#        pygame.display.set_caption(WND_TITLE)
#        self.fps_clock = pygame.time.Clock()
#        self.surface = pygame.display.set_mode(WND_SIZE)
#        self.fsb_font = pygame.font.SysFont('Ubuntu-L', 16, bold=False,
#                                            italic=False)
#        self.pause = False
#        self.hexagon = np.zeros((6,2))
#        for i in xrange(6):
#            angle = i*DEG60
#            self.hexagon[i][0] = RADIUS * np.cos(angle)
#            self.hexagon[i][1] = RADIUS * np.sin(angle)
#
#        self.piece = Piece(np.random.randint(10), TOP)
#        # Draw active piece
#        # Find a way to index array directly
#        for h in self.piece.hexagons():
#            HEXMAP[h[0], h[1]] = self.piece.color
#        # Speed
#        self.speed = SPEED
#
#    def update(self):
#        if self.piece == None:
#            return
#
#        # Erase piece first
#        for h in self.piece.hexagons():
#            HEXMAP[h[0], h[1]] = BGCOL
#        self.piece.fall(self.speed)
#        # Redraw
#        for h in self.piece.hexagons():
#            HEXMAP[h[0], h[1]] = self.piece.color
#
#        # Collision detection
#        for hex in self.piece.hexagons():
#            if hex[0] >= HEXMAP.shape[0] - 2:
#                self.piece = None
#
#
#
#
#    def draw(self):
#        """ Update visual objects
#        """
#        self.surface.fill(BGCOL)
#        self.field = self.surface.subsurface(FIELD)
#
#
#        for r in xrange(-1, HEXMAP.shape[0]):
#            for q in xrange(HEXMAP.shape[1]):
#                # Coordinates for r must be corrected due to romboidal
#                # (non-perpendicular angle between the axes) shape.
#                s = r - q/2
#                if r >= 0:
#                    hexpoly = pygame.draw.polygon(self.field,
#                                                  HEXMAP[r, q],
#                                                  self.hexagon + hex2pix(q,s),
#                                                  0
#                    )
#                hexborder = pygame.draw.aalines(self.field,
#                                                HEXGRID_COL,
#                                                True,
#                                                self.hexagon + hex2pix(q,s))
##        if self.piece:
##            for h in self.piece.hexagons():
##                HEXMAP[h[0], h[1]] = BGCOL
##            for h in self.piece.hexagons():
##                HEXMAP[h[0], h[1]] = self.piece.color
#
#
#        self.field_border = pygame.draw.rect(self.surface,
#                                             FIELD_BORDER_COL,
#                                             FIELD_BORDER,
#                                             1
#        )
#
#
#    def run(self):
#        while True:
#            for event in pygame.event.get():
#                if event.type == QUIT:
#                    pygame.quit()
#                    sys.exit()
#
#                elif event.type == KEYDOWN:
#                    if event.key in (K_LEFT, K_RIGHT, K_UP, K_DOWN):
#                        if not self.piece: continue
#                        # Erase piece first
#                        for h in self.piece.hexagons():
#                            HEXMAP[h[0], h[1]] = BGCOL
#
#                        if event.key == K_UP:
#                            self.piece.rotate_right()
#                        elif event.key == K_DOWN:
#                            self.piece.rotate_left()
#                        elif event.key == K_LEFT:
#                            if self.piece.hexagons()[:,1].min() <= 0:
#                                continue
#                            self.piece.pos[1] -= 1
#                        elif event.key == K_RIGHT:
#                            if self.piece.hexagons()[:,1].max() >= \
#                               HEXMAP.shape[1]-1:
#                                continue
#                            self.piece.pos[1] += 1
#                        # Redraw
#                        for h in self.piece.hexagons():
#                            HEXMAP[h[0], h[1]] = self.piece.color
#
#                    if event.key == K_p:
#                        self.pause = not self.pause
#                    if event.key == K_s:
#                        pass
#                    if event.key == K_q:
#                        pygame.quit()
#                        sys.exit()
#                    if event.key == K_ESCAPE:
#                        pygame.event.post(pygame.event.Event(QUIT))
#
#            # Game update
#            self.update()
#            # Graphics update
#            self.draw()
#            pygame.display.update()
#            self.fps_clock.tick(FPS_RATE)
#-------------------------------------------------------------------------------
# Game?
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# GL Widget
#-------------------------------------------------------------------------------
class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.lastPos = QtCore.QPoint()

    def sizeHint(self):
        return QtCore.QSize(*FIELD_SIZE)

    def initializeGL(self):
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glClearColor(0.0,0.0,0.0,0.0)
        GL.glClearDepth(1.0)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glDepthFunc(GL.GL_LEQUAL)
        GL.glHint(GL.GL_PERSPECTIVE_CORRECTION_HINT, GL.GL_NICEST)


    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GL.glTranslatef(0.0, 0.0, -1)

        # Paint the coordinate system x,y,z : r, g, b first
        GL.glBegin(GL.GL_LINES)
        # x axis
        GL.glColor3f(0.2, 0.2, 0.2)
        GL.glVertex3f(-0.5, 0, 0)
        GL.glVertex3f(0.5, 0, 0)
        # y axis
        GL.glVertex3f(0, -0.5*GOLDEN_RATIO, 0)
        GL.glVertex3f(0, 0.5*GOLDEN_RATIO, 0)
        GL.glEnd()



    def resizeGL(self, width, height):
        side = min(width, height)
        hr = 0.5*height/width
        if side < 0:
            return
        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        ortho_height = GOLDEN_RATIO*0.5
        GL.glOrtho(-0.5, 0.5, ortho_height, -ortho_height, -1.0, 1.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glViewport(0,0,width,height)

    def mousePressEvent(self, event):
        self.lastPos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & QtCore.Qt.LeftButton:
            pass
        elif event.buttons() & QtCore.Qt.RightButton:
            pass
        self.lastPos = event.pos()

#-------------------------------------------------------------------------------
# Window
#-------------------------------------------------------------------------------
class Window(QtGui.QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.glWidget = GLWidget()
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.glWidget)
        self.setLayout(layout)
        self.setWindowTitle("PyQt4 OpenGL Template")

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
