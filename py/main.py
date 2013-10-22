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
#GOLDEN_RATIO = 0.5*(1+np.sqrt(5))
GOLDEN_RATIO = 2.
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
def hex2pix(q,r, radius, offset):
    x = radius * 1.5 * q + 0.5*radius
    y = radius * SQRT3 * (r + 0.5*q)
    return np.array([x,y]) + offset

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

#-------------------------------------------------------------------------------
# GL Widget
#-------------------------------------------------------------------------------
class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.lastPos = QtCore.QPoint()
        self.setFixedSize(*FIELD_SIZE)



        # ---------- RECODE ----------
        self.hex_num = 13
        # Maybe should make sure the result is an integer
        self.half_hex_num = self.hex_num/2
        self.hex_radius = 2.*(1./(3.*self.hex_num  + 1.))
        # Whole height
        self.hex_height = SQRT3*self.hex_radius
        # We also need to calculate how many fit in horizontally
        self.hex_num_vert = int(np.floor(GOLDEN_RATIO/self.hex_height))
        # Offset vertically by the empty space due to imprecise number of hexes
        self.offset = np.array([0.5*self.hex_radius,
                                HEIGHT_COEFF*self.hex_radius + \
                                GOLDEN_RATIO - \
                                self.hex_num_vert*self.hex_height])

        self.hexagon = np.zeros((6,2))
        for i in xrange(6):
            angle = i*DEG60
            self.hexagon[i][0] = self.hex_radius * np.cos(angle)
            self.hexagon[i][1] = self.hex_radius * np.sin(angle)

        # The hexmap is a width x height matrix so that it can be
        # for coordinate conversion in a more natural way
        self.colmap = np.zeros((self.hex_num, self.hex_num_vert, 3))

        self.colmap[:,0] = (0,0,0.3)
        self.hexmap = np.zeros((self.hex_num, self.hex_num_vert))

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

        # Draw the hexagons
        for q in xrange(self.hex_num):
            for r in xrange(self.hex_num_vert):
                # Coordinates for r must be corrected due to romboidal
                # (non-perpendicular angle between the axes) shape.
                s = r - q/2
                pos = hex2pix(q,s, self.hex_radius, self.offset)
                GL.glBegin(GL.GL_TRIANGLE_FAN)
                col = self.colmap[q, r]
                GL.glColor3f(*self.colmap[q,r])
                hex = self.hexagon + pos
                for v in hex:
                    GL.glVertex3f(v[0],v[1],0)
                v = hex[0]
                GL.glVertex3f(v[0], v[1], 0)
                GL.glEnd()

        # Draw the hexagon grid
        GL.glColor3f(0.2,0.2,0.2)
        for q in xrange(self.hex_num):
            for r in xrange(self.hex_num_vert):
                # Coordinates for r must be corrected due to romboidal
                # (non-perpendicular angle between the axes) shape.
                s = r - q/2
                pos = hex2pix(q,s, self.hex_radius, self.offset)
                GL.glBegin(GL.GL_LINE_STRIP)
                hex = self.hexagon + pos
                for v in hex:
                    GL.glVertex3f(v[0],v[1],0)
                v = hex[0]
                GL.glVertex3f(v[0], v[1], 0)
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
        GL.glOrtho(0, 1.0, 0, GOLDEN_RATIO, -1.0, 1.0)
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

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            print 'left'
        elif key == QtCore.Qt.Key_Right:
            pass
        elif key == QtCore.Qt.Key_Down:
            pass
        elif key == QtCore.Qt.Key_Up:
            pass
        elif key == QtCore.Qt.Key_Space:
            pass
        elif key == QtCore.Qt.Key_Q:
            QtGui.qApp.quit()

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
        self.glWidget.setFocusPolicy(QtCore.Qt.StrongFocus)

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
