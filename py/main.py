#!/usr/bin/env python
import sys
import time
from datetime import timedelta
from PyQt4 import QtCore, QtGui, QtOpenGL
try:
    from OpenGL import GL as gl
except ImportError:
    app = QtGui.QApplication(sys.argv)
    QtGui.QMessageBox.critical(None, "OpenGL 2dpainting",
            "PyOpenGL must be installed to run this example.")
    sys.exit(1)
import numpy as np
#===============================================================================
# GUI Definitions (defaults)
WND_TITLE = 'VexTris'
ROWS, COLUMNS = 23, 13
WDG_SIZE = np.array([400, 600])
FIELD_WIDTH = 0.75
FIELD_HEIGHT = float(WDG_SIZE[1])/WDG_SIZE[0]
AREA_SIZE = np.array([1, FIELD_HEIGHT])
PREVIEW_WIDTH = 1. - FIELD_WIDTH
PREVIEW_OFFSET = np.array([0.5*(FIELD_WIDTH + PREVIEW_WIDTH),
                           -0.25*FIELD_HEIGHT])
#-------------------------------------------------------------------------------
# General Colors
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
# Color config
PIECE_COLS = [ORANGE,BLUE,PURPLE,GREEN,MAGENTA,CYAN,YELLOW,RED,LBLUE,GREY]
HEXGRID_COL = np.array([0.1,0.1,0.1])
BGCOL = BLACK
AREA_FRAME = np.ones(3)*0.25
PREVIEW_PIECE_BORDER_COL = WHITE
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
print NLOC.shape
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
# row / ms
START_SPEED = 0.4
# Timeout interval shrinks by SPEED_MULT for each cleaned line
SPEED_MULT = 0.99
# Score for a number of simultaneously destroyed lines
SCORE_TABLE = [100,200,400,800]
#-------------------------------------------------------------------------------
# Messages
MSG_EG = 'Game Over | Score: {0} | Lines: {1} | Time: {2:0>2}:{3:0>2} s'
MSG_LN = 'Score: {0} | {1:.1f} ms | Lines: {2}'
MSG_PAUSE = 'Paused'
MSG_EG = 'Game Over | Score: {0} | Lines: {1} | Time: {2:0>2}:{3:0>2} s'
MSG_LN = 'Score: {0} | {1:.1f} ms | Lines: {2}'
MSG_PAUSE = 'Paused'
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
        self.hexagons = self.get_hexagons(pos, rot_id)

    def get_hexagons(self, pos, rot_id):
        neighbors = NLOC[pos[0]&1][SHAPES[self.type_id][rot_id]]
        return neighbors + pos

    def rotate(self, left_right, hexmap):
        """ left: -1, right: +1 """
        rot_id = (self.rot_id + left_right) % len(SHAPES[self.type_id])
        hexagons = self.get_hexagons(self.pos, rot_id)
        if self.collision(hexagons, hexmap):
            return False
        self.rot_id = rot_id
        self.hexagons = hexagons
        return True

    def rotate_left(self, hexmap):
        return self.rotate(-1, hexmap)

    def rotate_right(self, hexmap):
        return self.rotate(1, hexmap)

    def move(self, left_right, hexmap, vert=0):
        """ left: -1, right: +1 """
        # Have to select neighbors due to hex coordinates dependencies
        pos = self.pos + np.array([left_right, vert])
        hexagons = self.get_hexagons(pos, self.rot_id)
        coll_code = self.collision(hexagons, hexmap)
        if coll_code:
            return coll_code
        self.pos = pos
        self.hexagons = hexagons
        # Piece moved (code 0)
        return 0

    def move_left(self, hexmap):
        return self.move(-1, hexmap)

    def move_down_left(self, hexmap):
        return self.move(-1, hexmap, vert=-1)

    def move_right(self, hexmap):
        return self.move(1, hexmap)

    def move_down_right(self, hexmap):
        return self.move(1, hexmap, vert=-1)

    def fall(self, hexmap):
        # Have to select neighbors due to hex coordinates dependencies
        pos = self.pos + np.array([0, -1])
        neighbors = NLOC[pos[0]&1][SHAPES[self.type_id][self.rot_id]]
        hexagons = neighbors + pos
        if self.collision(hexagons, hexmap):
            return False
        self.pos = pos
        self.hexagons = hexagons
        return True

    def collision(self, hexagons, hexmap):
        # Piece collides with left border
        if hexagons[:,0].min() < 0:
            return 1
        # Piece collides with right border
        if hexagons[:,0].max() > hexmap.shape[0]-1:
            return 2
        # Piece collides with the piece heap
        for (i,j) in hexagons:
            if hexmap[i,j]: return 3
        return False

#-------------------------------------------------------------------------------
# GL Widget
#-------------------------------------------------------------------------------
class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super(GLWidget, self).__init__(parent)
        self.speed = START_SPEED
        self.rows, self.columns = ROWS, COLUMNS
        self.hex_num = self.columns
        self.half_hex_num = self.hex_num/2
        # Maybe should make sure the result is an integer
        self.hex_radius = 2.*(FIELD_WIDTH/(3.*self.hex_num  + 1.))
        self.hex_height = SQRT3*self.hex_radius
        # We also need to calculate how many fit in horizontally
        self.hex_num_vert = int(np.floor(FIELD_HEIGHT/self.hex_height))
        # Offset vertically by the empty space due to imprecise number of hexes
        self.top_center = np.array([self.half_hex_num, self.hex_num_vert],
                                   dtype=np.int32)
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
        self.preview_piece = None
        self.score = 0
        self.play_time = 0
        self.line_count = 0

    def select_piece(self):
        """ To be used by friendly/adversary AI
        """
        return np.random.randint(10)

    def status_message(self, s):
        self.parent().status_bar.showMessage(s)

    def initializeGL(self):
        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glClearColor(BGCOL[0], BGCOL[1], BGCOL[2], 0)
        gl.glClearDepth(1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT, gl.GL_NICEST)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        # Draw the hexagons
        for i in xrange(self.hex_num):
            for j in xrange(self.hex_num_vert+4):
                # Coordinates for r must be corrected due to romboidal
                # (non-perpendicular angle between the axes) shape.
                pos = hex2pix(i,j, self.hex_radius)
                gl.glBegin(gl.GL_TRIANGLE_FAN)
                col = self.colmap[i, j]
                gl.glColor3f(*self.colmap[i,j])
                hex = self.hexagon + pos
                for v in hex:
                    gl.glVertex2f(v[0],v[1])
                v = hex[0]
                gl.glVertex2f(v[0], v[1])
                gl.glEnd()
        # Draw piece
        if self.piece:
            gl.glColor3f(*self.piece.color)
            for (i,j) in self.piece.hexagons:
                pos = hex2pix(i, j, self.hex_radius)
                gl.glBegin(gl.GL_TRIANGLE_FAN)
                hex = self.hexagon + pos
                for v in hex:
                    gl.glVertex2f(v[0], v[1])
                v = hex[0]
                gl.glVertex2f(v[0], v[1])
                gl.glEnd()
        # Draw preview piece
        if self.preview_piece:
            gl.glColor3f(*self.preview_piece.color)
            for (i,j) in self.preview_piece.hexagons:
                pos = hex2pix(i, j, self.hex_radius) + PREVIEW_OFFSET
                gl.glBegin(gl.GL_TRIANGLE_FAN)
                hex = self.hexagon + pos
                for v in hex:
                    gl.glVertex2f(v[0], v[1])
                v = hex[0]
                gl.glVertex2f(v[0], v[1])
                gl.glEnd()
        # Draw the hexagon grid
        gl.glColor3f(*HEXGRID_COL)
        for i in xrange(self.hex_num):
            for j in xrange(self.hex_num_vert+4):
                pos = hex2pix(i,j, self.hex_radius)
                gl.glBegin(gl.GL_LINE_STRIP)
                hex = self.hexagon + pos
                for v in hex:
                    gl.glVertex2f(v[0],v[1])
                v = hex[0]
                gl.glVertex2f(v[0], v[1])
                gl.glEnd()
        # Draw piece border hexagons
        if self.piece:
            gl.glColor3f(*WHITE)
            for (i,j) in self.piece.hexagons:
                pos = hex2pix(i,j, self.hex_radius)
                gl.glBegin(gl.GL_LINE_STRIP)
                hex = self.hexagon + pos
                for v in hex:
                    gl.glVertex2f(v[0],v[1])
                v = hex[0]
                gl.glVertex2f(v[0], v[1])
                gl.glEnd()
        # Draw preview piece border hexagons
        if self.preview_piece:
            gl.glColor3f(*PREVIEW_PIECE_BORDER_COL)
            for (i,j) in self.preview_piece.hexagons:
                pos = hex2pix(i,j, self.hex_radius) + PREVIEW_OFFSET
                gl.glBegin(gl.GL_LINE_STRIP)
                hex = self.hexagon + pos
                for v in hex:
                    gl.glVertex2f(v[0],v[1])
                v = hex[0]
                gl.glVertex2f(v[0], v[1])
                gl.glEnd()
        # Draw the open gl viewport area
        gl.glColor3f(*GREY)
        gl.glBegin(gl.GL_LINE_STRIP)
        gl.glVertex2f(0,0)
        gl.glVertex2f(AREA_SIZE[0], 0)
        gl.glVertex2f(AREA_SIZE[0], AREA_SIZE[1])
        gl.glVertex2f(0, AREA_SIZE[1])
        gl.glVertex2f(0, 0)
        gl.glEnd()
        # Draw field separator
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(FIELD_WIDTH, 0)
        gl.glVertex2f(FIELD_WIDTH, AREA_SIZE[1])
        gl.glEnd()

    def resizeGL(self, width, height):
        """Called upon window resizing: reinitialize the viewport.
        """
        gl_width, gl_height = width, height
        wdg_ratio = float(height) / width
        # Correct gl width/height
        if wdg_ratio > FIELD_HEIGHT:
            gl_height = int(gl_width * FIELD_HEIGHT)
        elif wdg_ratio < FIELD_HEIGHT:
            gl_width = int(gl_height / FIELD_HEIGHT)
        # Paint within the whole window
        gl.glViewport(0, 0, gl_width, gl_height)
        # Set orthographic projection where (0,0) is down left
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(0, 1, 0, FIELD_HEIGHT, -1, 1)

    def new_game(self):
        self.speed = START_SPEED
        self.colmap[:,1:] = BGCOL
        self.hexmap[:,1:] = 0
        self.piece = Piece(self.select_piece(), self.top_center.copy())
        self.preview_piece = Piece(self.select_piece(), self.top_center.copy())
        self.repaint()
        self.timer.start(self.speed*1000., self)
        self.score = 0
        self.play_time = time.time()
        self.line_count = 0
        self.status_message(self.msg_line())

    def pause_game(self):
        if self.timer.isActive():
            self.timer.stop()
            self.status_message(MSG_PAUSE)
        elif self.piece:
            self.timer.start(self.speed*1000, self)
            self.status_message(self.msg_line())

    def msg_end_game(self):
        play_time = time.time() - self.play_time
        pt_min = int(play_time)/60
        pt_sec = int(play_time) % 60
        return MSG_EG.format(self.score, self.line_count, pt_min, pt_sec)

    def msg_line(self):
        return MSG_LN.format(self.score, self.speed*1000, self.line_count)

    def timerEvent(self, e):
        if not self.piece and not self.timer.isActive(): return
        # Check for collision
        if self.piece.fall(self.hexmap):
            self.repaint()
            return
        # Fill in the grid with current piece
        for (i,j) in self.piece.hexagons:
            self.hexmap[i,j] = 1
            self.colmap[i,j] = self.piece.color
        # Check if game is over
        if self.hex_num_vert-1 in self.piece.hexagons[:,1]:
            self.status_message(self.msg_end_game())
            self.timer.stop()
            self.repaint()
            return
        # Scan for complete lines, starting one above the ground
        i = 1
        rm_lines_count = 0
        while i < self.hex_num_vert:
            if self.hexmap[:,i].sum() == self.hex_num:
                rm_lines_count += 1
                # Pull down all the rows above i
                for j in xrange(i, self.hex_num_vert-1):
                    for k in xrange(self.hex_num):
                        self.colmap[k,j] = self.colmap[k,j+1]
                        self.hexmap[k,j] = self.hexmap[k,j+1]
            i += 1
        # Generate new piece
        self.piece = self.preview_piece
        self.preview_piece = Piece(self.select_piece(), self.top_center.copy())
        self.repaint()
        # Calculate score & speedup
        if not rm_lines_count:
            return
        self.line_count += rm_lines_count
        # Lookup in table
        lines_mult = SCORE_TABLE[-1]
        if rm_lines_count <= len(SCORE_TABLE):
            lines_mult = SCORE_TABLE[rm_lines_count-1]
        self.score += lines_mult*rm_lines_count
        # Speedup
        self.speed = (SPEED_MULT**rm_lines_count)*self.speed
        self.status_message(self.msg_line())
        self.timer.stop()
        self.timer.start(self.speed*1000., self)

    def keyPressEvent(self, event):
        key = event.key()
        # GUI controls
        if key == QtCore.Qt.Key_Q:
            QtGui.qApp.quit()
        elif key == QtCore.Qt.Key_N:
            self.new_game()
        elif key == QtCore.Qt.Key_P:
            self.pause_game()
        # Piece control
        if not self.timer.isActive(): return
        if key == QtCore.Qt.Key_Left:
            res = self.piece.move_left(self.hexmap)
            # Avoid wall collisions
            if res == 3:
                if self.piece.move_down_left(self.hexmap) == 0:
                    self.repaint()
            elif res == 0:
                self.repaint()
        elif key == QtCore.Qt.Key_Right:
            res = self.piece.move_right(self.hexmap)
            # Avoid wall collisions
            if res == 3:
                if self.piece.move_down_right(self.hexmap) == 0:
                    self.repaint()
            elif res == 0:
                self.repaint()
        elif key == QtCore.Qt.Key_Down:
            if self.piece.rotate_left(self.hexmap):
                self.repaint()
        elif key == QtCore.Qt.Key_Up:
            if self.piece.rotate_right(self.hexmap):
                self.repaint()
        elif key == QtCore.Qt.Key_Space:
           while self.piece.fall(self.hexmap):
               pass
           self.repaint()

#-------------------------------------------------------------------------------
# Window
#-------------------------------------------------------------------------------
class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.glWidget = GLWidget()
        self.glWidget.setMinimumWidth(WDG_SIZE[0])
        self.glWidget.setMinimumHeight(WDG_SIZE[1])
        self.setCentralWidget(self.glWidget)
        self.glWidget.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setWindowTitle("VexTris")
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('VexTris')
        # Menu
        self.menu_bar = self.menuBar()
        self.create_menus()

    def create_menus(self):
        fileMenu = self.menu_bar.addMenu('&Game')
        # Start a new game
        newAction = QtGui.QAction('&New', self)
        newAction.setShortcut('Ctrl+N')
        newAction.setStatusTip('New Game')
        newAction.triggered.connect(self.glWidget.new_game)
        fileMenu.addAction(newAction)
        # Pause the game
        pauseAction = QtGui.QAction('&Pause', self)
        pauseAction.setShortcut('Ctrl+P')
        pauseAction.setStatusTip('Pause Game')
        pauseAction.triggered.connect(self.glWidget.pause_game)
        fileMenu.addAction(pauseAction)
        # Quit
        quitAction = QtGui.QAction('&Quit', self)
        quitAction.setShortcut('Ctrl+Q')
        quitAction.setStatusTip('Quit Game')
        quitAction.triggered.connect(QtGui.qApp.quit)
        fileMenu.addAction(quitAction)
#-------------------------------------------------------------------------------
# Main
#-------------------------------------------------------------------------------
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
