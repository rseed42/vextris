#ifndef GLWIDGET_H
#define GLWIDGET_H
//------------------------------------------------------------------------------
#include <QtOpenGL>
#include <QGLWidget>
#include <math.h>
#include "piece.h"
#include "types.h"
//------------------------------------------------------------------------------
#define WIDTH 400
#define HEIGHT 600
#define ROWS 23
#define COLUMNS 13
#define HEX_NUM COLUMNS
#define HALF_HEX_NUM HEX_NUM/2
#define FIELD_WIDTH 0.75f
#define EXTRA_FIELD_ROWS 4
//------------------------------------------------------------------------------
#define _USE_MATH_DEFINES
#define DEG60 (float)(M_PI/3)
#define SQRT3 (float)(sqrt(3))
#define HEIGHT_COEFF (float)(0.5*SQRT3)
//------------------------------------------------------------------------------
#define START_SPEED 400.0f
#define SPEED_MULT 0.99f
//------------------------------------------------------------------------------
// GLWidget
//------------------------------------------------------------------------------
class GLWidget : public QGLWidget{
    Q_OBJECT

public:
    GLWidget(QWidget *parent = 0);
    ~GLWidget();

public slots:
    void newGame();
    void pauseGame();

protected:
    void initializeGL();
    void paintGL();
    void resizeGL(int width, int height);
    void keyPressEvent(QKeyEvent *event);
    void timerEvent(QTimerEvent *);

private:
    // Functions
    Vecf hex2gl(int q, int r, float radius);
    void statusMsg(QString msg){
             ((QMainWindow*)parentWidget())->statusBar()->showMessage(msg);}
    QString msgLine(){
                     return QString().sprintf("Score: %d | %.1f ms | Lines: %d",
                                              score, speed, line_count);}
    QString msgGameOver();
    Vecf2 hexVerticesAt(Vecf pos);
    int selectPiece();
    // GUI Definitions
    QSize wndSize;
    float speed;
    Vecf field;
    Vecf areaSize;
    float previewWidth;
    Vecf previewOffset;
    float hex_radius;
    float hex_height;
    int hex_num_vert;
    Veci topCenter;
    Veci middleCenter;
    Vecf2 hexVertices;
    // Colors
    Vecf Black;
    Vecf Grey;
    Vecf White;
    Vecf Red;
    Vecf Green;
    Vecf Blue;
    Vecf Magenta;
    Vecf Orange;
    Vecf Purple;
    Vecf LBlue;
    Vecf Cyan;
    Vecf Yellow;
    // Selected colors
    Vecf HexGridColor;
    Vecf AreaFrameColor;
    Vecf2 pieceColors;
    Vecf2 arTest;
    Vecf& refBgColor;
    Vecf& refPreviewPieceBorderColor;
    // Data
    Veci scoreTable;
    // Game objects
    Piece* pPiece;
    Piece* pPreviewPiece;
    QBasicTimer timer;
    QTime game_time;
    int score;
    int line_count;
    Vecf3 colorMap;
    Veci2 hexMap;
};
#endif
