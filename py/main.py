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
# Dimensions
FIELD_WIDTH = 300
FIELD_HEIGHT = FIELD_WIDTH*GOLDEN_RATIO
FIELD_SIZE = np.array([FIELD_WIDTH, FIELD_HEIGHT])
#-------------------------------------------------------------------------------
# Colors
BLACK = np.zeros(3)
GREY = np.array([0.18,0.18,0.18])
WHITE = np.ones(3)
RED = np.array([1.0,0,0])
GREEN = np.array([0,1.0,0])
BLUE = np.array([0,0,1.0])
MAGENTA = np.array([1.0,0,1.0])
ORANGE = np.array([1.0,0.5,0])
PURPLE = np.array([0.63,0.12,0.94])
LBLUE = np.array([0.68,0.85,0.9])
CYAN = np.array([0,1.0,1.0])
YELLOW = np.array([1.0,1.0,0])
PIECE_COLS = [ORANGE,BLUE,PURPLE,GREEN,MAGENTA,CYAN,YELLOW,RED,LBLUE,GREY]
# blue,yellow,red,orange,green,purple,cyan,gray45,magenta,lightblue
HEXGRID_COL = np.array([0.1,0.1,0.1])
BGCOL = BLACK
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
# The neighbors are enumerated from 1 (top neighbor) to 6 on the
# inner circle and 7 (second top neighbor) to 18 on the second one.
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
# Rows/sec
SPEED = 6.
#-------------------------------------------------------------------------------
def hex2pix(q,r, radius):
    """ Hexagons are in an even-q vertical layout
    """
    x = radius * 1.5 * q + radius
    y = radius * SQRT3 * (r - 0.5*(q&1))
    return np.array([x,y])
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

    def hexagons(self, pos=None):
        if pos == None: pos = self.pos
        neighbors = NLOC[self.pos[0]&1][SHAPES[self.type_id][self.rot_id]]
        return neighbors + pos

    def rotate_left(self):
        self.rot_id = (self.rot_id - 1) % len(SHAPES[self.type_id])

    def rotate_right(self):
        self.rot_id = (self.rot_id + 1) % len(SHAPES[self.type_id])

    def fall(self, speed):
        self.height += speed
        self.pos[0] = int(np.floor(self.height))

    def collision(self, newpos, hexmap):
        # Piece collides with left border
        if self.hexagons(newpos)[:,0].min() < 0:
            return True
        # Piece collides with right border
        if self.hexagons(newpos)[:,0].max() > hexmap.shape[0]-1:
            return True
        # Piece collides with the piece heap
        for hexpos in self.hexagons(newpos):
            if hexmap[hexpos[0],hexpos[1]]: return True
        return False

#-------------------------------------------------------------------------------
# GL Widget
#-------------------------------------------------------------------------------
class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.lastPos = QtCore.QPoint()
        self.setFixedSize(*FIELD_SIZE)
        self.speed = SPEED
        self.hex_num = 13
        # Maybe should make sure the result is an integer
        self.half_hex_num = self.hex_num/2
        self.hex_radius = 2.*(1./(3.*self.hex_num  + 1.))
        # Whole height
        self.hex_height = SQRT3*self.hex_radius
        # We also need to calculate how many fit in horizontally
        self.hex_num_vert = int(np.floor(GOLDEN_RATIO/self.hex_height))
        # Offset vertically by the empty space due to imprecise number of hexes
        self.center = np.array([self.hex_num/2, self.hex_num_vert/2],
                               dtype=np.int64)
        self.top = np.array([self.hex_num/2,self.hex_num_vert+2],dtype=np.int64)
        self.hexagon = np.zeros((6,2))
        for i in xrange(6):
            angle = i*DEG60
            self.hexagon[i][0] = self.hex_radius * np.cos(angle)
            self.hexagon[i][1] = self.hex_radius * np.sin(angle)

        # The hexmap is a width x height matrix so that it can be
        # for coordinate conversion in a more natural way
        self.colmap = np.zeros((self.hex_num, self.hex_num_vert+4, 3))
        self.colmap[:,0] = HEXGRID_COL
        self.hexmap = np.zeros((self.hex_num, self.hex_num_vert+4))
        self.hexmap[:,0] = 1
        self.timer = QtCore.QBasicTimer()
        self.piece = None
        self.score = 0

    def status_message(self, s):
        self.parent().status_bar.showMessage(s)

    def initializeGL(self):
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glClearColor(BGCOL[0], BGCOL[1], BGCOL[2], 0)
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
            for j in xrange(self.hex_num_vert+4):
                # Coordinates for r must be corrected due to romboidal
                # (non-perpendicular angle between the axes) shape.
                pos = hex2pix(i,j, self.hex_radius)
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
        GL.glColor3f(*HEXGRID_COL)
        for i in xrange(self.hex_num):
            for j in xrange(self.hex_num_vert+4):
                # Coordinates for r must be corrected due to romboidal
                # (non-perpendicular angle between the axes) shape.
                pos = hex2pix(i,j, self.hex_radius)
                GL.glBegin(GL.GL_LINE_STRIP)
                hex = self.hexagon + pos
                for v in hex:
                    GL.glVertex3f(v[0],v[1],0)
                v = hex[0]
                GL.glVertex3f(v[0], v[1], 0)
                GL.glEnd()

    def new_game(self):
        self.status_message('New Game')
        self.colmap[:,1:] = BGCOL
        self.hexmap[:,1:] = 0
        self.piece = Piece(np.random.randint(10), self.top.copy())
        self.rasterize_piece()
        self.timer.start(1000./self.speed, self)
        self.score = 0

    def pause_game(self):
        if self.timer.isActive():
            self.timer.stop()
        elif self.piece:
            self.timer.start(1000./self.speed, self)

    def timerEvent(self, e):
        if not self.piece and not self.timer.isActive(): return
        self.erase_piece()

        if self.piece.collision(self.piece.pos, self.hexmap):
            # Must check where the piece came from
            check_pos = self.piece.pos.copy()
            # Piece came from above
            check_pos[1] -= 1
            if not self.piece.collision(check_pos, self.hexmap):
                self.piece.pos = check_pos
                self.rasterize_piece()
                self.repaint()
                return
            check_pos[1] += 1
            # Piece came from left
            check_pos[0] -= 1
            if not self.piece.collision(check_pos, self.hexmap):
                self.piece.pos = check_pos
                self.rasterize_piece()
                self.repaint()
                return
            check_pos[0] += 2
            if not self.piece.collision(check_pos, self.hexmap):
                self.piece.pos = check_pos
                self.rasterize_piece()
                self.repaint()
                return

        # Look ahead first
        newpos = self.piece.pos + np.array([0,-1])
        if self.piece.collision(newpos, self.hexmap):
            # Check wether the current piece touches the top (game over)
            hexagons = self.piece.hexagons()
            if self.hex_num_vert-1 in hexagons[:,1]:
                self.status_message('Game Over')
                self.timer.stop()
            # Take care of the current piece
            for hexpos in hexagons:
                self.hexmap[hexpos[0],hexpos[1]] = 1
            self.rasterize_piece()
            # Scan for full lines
            i = 1
            while i < self.hex_num_vert:
                if self.hexmap[:,i].sum() == self.hex_num:
                    self.score += 1
                    self.status_message('Score: {0}'.format(self.score))
                    # Pull down all the rows above i
                    for j in xrange(i, self.hex_num_vert-1):
                        for k in xrange(self.hex_num):
                            self.colmap[k,j] = self.colmap[k,j+1]
                            self.hexmap[k,j] = self.hexmap[k,j+1]
                i += 1

            # Generate a new piece
            self.piece = Piece(np.random.randint(10), self.top.copy())
        else:
            self.piece.pos[1] -= 1

        self.rasterize_piece()
        self.repaint()

    def rasterize_piece(self):
        for h in self.piece.hexagons():
            self.colmap[h[0],h[1]] = self.piece.color

    def erase_piece(self):
        for h in self.piece.hexagons():
            self.colmap[h[0],h[1]] = BGCOL

    def resizeGL(self, width, height):
        side = min(width, height)
        hr = 0.5*height/width
        if side < 0:
            return
        GL.glViewport((width - side) / 2, (height - side) / 2, side, side)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
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
        if key == QtCore.Qt.Key_Q:
            QtGui.qApp.quit()
        elif key == QtCore.Qt.Key_N:
            self.new_game()
        elif key == QtCore.Qt.Key_P:
            self.pause_game()

        if not self.timer.isActive(): return
        self.erase_piece()
        if key == QtCore.Qt.Key_Left:
            newpos = self.piece.pos + np.array([-1,0])
            if not self.piece.collision(newpos, self.hexmap):
                self.piece.pos = newpos
        elif key == QtCore.Qt.Key_Right:
            newpos = self.piece.pos + np.array([1,0])
            if not self.piece.collision(newpos, self.hexmap):
                self.piece.pos = newpos
        elif key == QtCore.Qt.Key_Down:
            # Need to check for rotations (maybe implement move, rot
            # functions in the piece
            self.piece.rotate_left()
            if self.piece.collision(self.piece.pos, self.hexmap):
                self.piece.rotate_right()
        elif key == QtCore.Qt.Key_Up:
            self.piece.rotate_right()
            if self.piece.collision(self.piece.pos, self.hexmap):
                self.piece.rotate_left()
        elif key == QtCore.Qt.Key_Space:
           while not self.piece.collision(self.piece.pos, self.hexmap):
                self.piece.pos[1] -= 1
           self.piece.pos[1] += 1

        # Rasterize
        self.rasterize_piece()
        self.repaint()
#-------------------------------------------------------------------------------
# Window
#-------------------------------------------------------------------------------
#class Window(QtGui.QWidget):
class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.glWidget = GLWidget()
        self.setCentralWidget(self.glWidget)
        self.setWindowTitle("PyQt4 OpenGL Template")
        self.glWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('VexTris')
        # Menu
        self.menu_bar = self.menuBar()
        self.create_menus()

    def create_menus(self):
        fileMenu = self.menu_bar.addMenu('&Game')

        newAction = QtGui.QAction('&New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New Game')
        newAction.triggered.connect(self.glWidget.new_game)

        pauseAction = QtGui.QAction('&Pause', self)
        pauseAction.setShortcut('Ctrl+P')
        pauseAction.setStatusTip('Pause Game')
        pauseAction.triggered.connect(self.glWidget.pause_game)

        quitAction = QtGui.QAction('&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit Game')
        quitAction.triggered.connect(QtGui.qApp.quit)

        fileMenu.addAction(newAction)
        fileMenu.addAction(pauseAction)
        fileMenu.addAction(quitAction)

#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
