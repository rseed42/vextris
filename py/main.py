#!/usr/bin/env python
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
#===============================================================================
# GUI Definitions
WND_TITLE = 'VexTris'
GOLDEN_RATIO = 2.
FPS_RATE = 30
# Dimensions
FIELD_WIDTH = 320
FIELD_HEIGHT = FIELD_WIDTH*GOLDEN_RATIO
FIELD_SIZE = np.array([FIELD_WIDTH, FIELD_HEIGHT])
# Top, left, right, bottom
MARGINS = np.array([20,20,120,40])
#WND_SIZE = FIELD_SIZE + MARGINS[:2] + MARGINS[2:]
FIELD = np.concatenate((MARGINS[:2], FIELD_SIZE))
# Draw borders around the field so that figures inside are not affected
FIELD_BORDER = FIELD.copy() + np.array([-1,-1,2,2])
FIELD_BORDER_COL = np.array([64,64,64], dtype=np.uint8)
#-------------------------------------------------------------------------------
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
GREY = np.array([0.5, 0.5, 0.5])
BGCOL = BLACK
PIECE_COLS = [ORANGE,BLUE,VIOLETT,GREEN,MAGENTA,DARK_CYAN,YELLOW,RED,CYAN,GREY]
#-------------------------------------------------------------------------------
# Math
DEG60 = np.pi/3
SQRT3 = np.sqrt(3)
HEIGHT_COEFF = 0.5*SQRT3
#-------------------------------------------------------------------------------
# Shapes are defined as the first and second order neighbors of
# the pos variable in a piece. Due to position-dependent distance
# on the hex grid, we need to calculate their relative position
# when the center of the piece changes its location.
# The neighbors are enumerated from 0 (top neighbor) to 5 on the
# inner circle and 6 (second top neighbor) to 17 on the second one.
# The locations depending on odd/even location of the center are
# defined in an array for the odd and even situation.

# Neighborhood map, depending on whether the position horizontal
# coordinate is [even, odd]
NLOC = np.array([[[0,0],[0,1],[1,1],[1,0],[0,-1],[-1,0],[-1,1],[0,2],[1,2],
                  [2,1],[2,0],[2, -1],[1,-1],[0,-2],[-1,-1],[-2,-1],[-2,0],
                  [-2, 1],[-1,2]],
                 [[0,0],[0,1],[1,0],[1,-1],[0,-1],[-1,-1],[-1,0],[0,2],[1,1],
                  [2,1],[2,0],[2,-1],[1,-2],[0,-2],[-1,-2],[-2,-1],[-2,0],
                  [-2,1],[-1,1]]], dtype=np.int64)
SHAPES = []
SHAPES.append(np.array([[0,1,3,5],[0,2,4,6]],dtype=np.int64))
SHAPES.append( np.array([[0,1,4,13],[0,2,5,15],[0,3,6,17],[0,4,1,7],
                         [0,5,2,9],[0,6,3,11]],dtype=np.int64))
SHAPES.append( np.array([[0,3,4,5],[0,4,5,6],[0,5,6,1],[0,6,1,2],[0,1,2,3],
                         [0,2,3,4]],dtype=np.int64))
SHAPES.append( np.array([[1,4,5,6],[2,5,6,1],[3,6,1,2],[4,1,2,3],[5,2,3,4],
                         [6,3,4,5],],dtype=np.int64))
SHAPES.append( np.array([[0,1,4,12],[0,2,5,14],[0,3,6,16],[0,4,1,18],
                         [0,5,2,8],[0,6,3,10],],dtype=np.int64))
SHAPES.append( np.array([[0,1,4,14],[0,2,5,16],[0,3,6,18],[0,4,1,8],
                         [0,5,2,10],[0,6,3,12],],dtype=np.int64))
SHAPES.append( np.array([[0,1,3,12],[0,2,4,14],[0,3,5,16],[0,4,6,18],
                         [0,5,1,8],[0,6,2,10],],dtype=np.int64))
SHAPES.append( np.array([[0,1,5,14],[0,2,6,16],[0,3,1,18],[0,4,2,8],
                         [0,5,3,10],[0,6,4,12],],dtype=np.int64))
SHAPES.append( np.array([[0,1,3,4],[0,2,4,5],[0,3,5,6],[0,4,6,1],
                         [0,5,1,2],[0,6,2,3],],dtype=np.int64))
SHAPES.append( np.array([[0,1,5,4],[0,2,6,5],[0,3,1,6],[0,4,2,1],[0,5,3,2],
                         [0,6,4,3],],dtype=np.int64))
#-------------------------------------------------------------------------------
# Dynamics
SPEED = 0.05
KEYMAP = {QtCore.Qt.Key_0:0, QtCore.Qt.Key_1:1, QtCore.Qt.Key_2:2,
          QtCore.Qt.Key_3:3, QtCore.Qt.Key_4:4, QtCore.Qt.Key_5:5,
          QtCore.Qt.Key_6:6, QtCore.Qt.Key_7:7, QtCore.Qt.Key_8:8,
          QtCore.Qt.Key_9:9}
#-------------------------------------------------------------------------------
# Use a matrix
def hex2pix(q,r, radius, offset):
    """ Hexagons are in an even-q vertical layout
    """
    x = radius * 1.5 * q
    y = radius * SQRT3 * (r - 0.5*(q&1))
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
        neighbors = NLOC[self.pos[0]&1][SHAPES[self.type_id][self.rot_id]]
        return neighbors + self.pos

    def rotate_left(self):
        self.rot_id = (self.rot_id - 1) % len(SHAPES[self.type_id])

    def rotate_right(self):
        self.rot_id = (self.rot_id + 1) % len(SHAPES[self.type_id])

    def fall(self, speed):
        self.height += speed
        self.pos[0] = int(np.floor(self.height))
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

        self.center = np.array([self.hex_num/2, self.hex_num_vert/2],
                               dtype=np.int64)
        self.hexagon = np.zeros((6,2))
        for i in xrange(6):
            angle = i*DEG60
            self.hexagon[i][0] = self.hex_radius * np.cos(angle)
            self.hexagon[i][1] = self.hex_radius * np.sin(angle)

        # The hexmap is a width x height matrix so that it can be
        # for coordinate conversion in a more natural way
        self.colmap = np.zeros((self.hex_num, self.hex_num_vert, 3))

        self.colmap[:,0] = (0,0,0.6)
        self.hexmap = np.zeros((self.hex_num, self.hex_num_vert))


        self.hexlist = np.array([[1,-1],])
        self.hexpos = np.array([4,8])

        # Piece
        self.piece = Piece(np.random.randint(10), self.center)
        self.update_game()


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
        for i in xrange(self.hex_num):
            for j in xrange(self.hex_num_vert):
                # Coordinates for r must be corrected due to romboidal
                # (non-perpendicular angle between the axes) shape.
                pos = hex2pix(i,j, self.hex_radius, self.offset)
                GL.glBegin(GL.GL_TRIANGLE_FAN)
                col = self.colmap[i, j]
                GL.glColor3f(*self.colmap[i,j])
                hex = self.hexagon + pos
                for v in hex:
                    GL.glVertex3f(v[0],v[1],0)
                v = hex[0]
                GL.glVertex3f(v[0], v[1], 0)
                GL.glEnd()

        # Draw the hexagon grid
        GL.glColor3f(0.2,0.2,0.2)
        for i in xrange(self.hex_num):
            for j in xrange(self.hex_num_vert):
                # Coordinates for r must be corrected due to romboidal
                # (non-perpendicular angle between the axes) shape.
                pos = hex2pix(i,j, self.hex_radius, self.offset)
                GL.glBegin(GL.GL_LINE_STRIP)
                hex = self.hexagon + pos
                for v in hex:
                    GL.glVertex3f(v[0],v[1],0)
                v = hex[0]
                GL.glVertex3f(v[0], v[1], 0)
                GL.glEnd()

    def update_game(self):
        for h in self.piece.hexagons():
            self.colmap[h[0],h[1]] = self.piece.color

    def erase_piece(self):
        for h in self.piece.hexagons():
            self.colmap[h[0],h[1]] = (0,0,0)

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
        self.erase_piece()
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            if self.piece.hexagons()[:,0].min() > 0:
                self.piece.pos[0] -= 1

        elif key == QtCore.Qt.Key_Right:
            if self.piece.hexagons()[:,0].max() < self.hex_num-1:
                self.piece.pos[0] += 1

        elif key == QtCore.Qt.Key_Down:
            if self.piece.hexagons()[:,1].min() > 1:
                self.piece.pos[1] -= 1

        elif key == QtCore.Qt.Key_Up:
            if self.piece.hexagons()[:,1].max() < self.hex_num_vert-1:
                self.piece.pos[1] += 1

        elif key == QtCore.Qt.Key_R:
            self.piece.rotate_right()

        elif key == QtCore.Qt.Key_L:
            self.piece.rotate_left()

        elif key in KEYMAP:
            self.piece = Piece(KEYMAP[key], self.piece.pos)

        elif key == QtCore.Qt.Key_Space:
            pass
        elif key == QtCore.Qt.Key_Q:
            QtGui.qApp.quit()

        self.update_game()
        self.repaint()
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
