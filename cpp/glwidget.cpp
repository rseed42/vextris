#include <QtGui>
#include "glwidget.h"
//------------------------------------------------------------------------------
// GL Widget
//------------------------------------------------------------------------------
GLWidget::GLWidget(QWidget *parent) : QGLWidget(parent),
    wndSize(WIDTH, HEIGHT), speed(START_SPEED),
    Black(3,0),Grey(3,0.18),White(3,1),Red{1,0,0},Green{0,1,0},Blue{0,0,1},
    Magenta{1,0,1},Orange{1,0.5,0},Purple{0.63,0.12,0.94},LBlue{0.68,0.85,0.9},
    Cyan{0,1,1},Yellow{1,1,0},HexGridColor(3,0.1),AreaFrameColor(3,0.25),
    pieceColors{Orange,Blue,Purple,Green,Magenta,Cyan,Yellow,Red,LBlue,Grey},
    scoreTable{100,200,400,800},score(0), line_count(0),
    colorMap(HEX_NUM), hexMap(HEX_NUM)
    {
    // Assign special colors
    pBgColor = &Black;
    // Initialize GUI variables
    field = {FIELD_WIDTH, (float)(wndSize.height()) / wndSize.width()};
    areaSize = {1, field[1]};
    previewWidth = 1. - field[0];
    previewOffset = {0.5f*(field[0] + previewWidth), -0.25f*field[1]};
    hex_radius = 2.*(field[0]/(3.*HEX_NUM + 1.));
    hex_height = SQRT3 * hex_radius;
    hex_num_vert = (int)(floor(field[1]/hex_height));
    topCenter = {HALF_HEX_NUM, hex_num_vert};
    // Calculate the hexagon vertices
    float angle = 0;
    for(int i=0; i<6; i++){
        angle = i*DEG60;
        hexVertices.append({(float)(hex_radius * cos(angle)),
                            (float)(hex_radius * sin(angle))});
    }
    // need to prepare the maps
    for(int i=0; i<HEX_NUM; i++){
        for(int j=0; j< hex_num_vert + EXTRA_FIELD_ROWS; j++)
            colorMap[i].append(*pBgColor);
        hexMap[i].fill(0, hex_num_vert + EXTRA_FIELD_ROWS);
    }
    // Fill in the ground
    for(int i=0; i<HEX_NUM; i++){
        colorMap[i][0] = HexGridColor;
        hexMap[i][0] = 1;
    }
    // Pieces get created on a new game
    pPiece = NULL;
    pPreviewPiece = NULL;
    qsrand((uint)QTime::currentTime().msec());
}
//------------------------------------------------------------------------------
GLWidget::~GLWidget(){
}
//------------------------------------------------------------------------------
QString GLWidget::msgGameOver(){
    int play_time = game_time.elapsed()/1000;
    int pt_min = play_time/60;
    int pt_sec = play_time % 60;
    return QString().sprintf("Game Over | Score: %d | Lines: %d | Time: %02d:%02d",
                     score, line_count, pt_min, pt_sec);
}
//------------------------------------------------------------------------------
Vecf GLWidget::hex2gl(int q, int r, float radius){
    return {radius*1.5f*q + radius, radius*SQRT3*(r-0.5f*(q&1))};
}
//------------------------------------------------------------------------------
Vecf2 GLWidget::hexVerticesAt(Vecf pos){
    Vecf2 hex(6);
    for(int i=0; i<6; i++){
        hex[i] = {hexVertices[i][0]+pos[0], hexVertices[i][1]+pos[1]};
    }
    return hex;
}
//------------------------------------------------------------------------------
int GLWidget::selectPiece(){
    return qrand() % 10;
}
//------------------------------------------------------------------------------
void GLWidget::initializeGL(){
    glShadeModel(GL_SMOOTH);
    glClearColor((*pBgColor)[0], (*pBgColor)[1], (*pBgColor)[2], 0.0);
    glClearDepth(1.0);
    glEnable(GL_DEPTH_TEST);
    glDepthFunc(GL_LEQUAL);
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST);
    // Create display lists
    hexgridList = createHexGrid();
    hexList = createHexagons();
}
//------------------------------------------------------------------------------
GLuint GLWidget::createHexGrid(){
    GLuint list = glGenLists(1);
    glNewList(list, GL_COMPILE);
    // Draw the hexagon grid
    glColor3f(HexGridColor[0], HexGridColor[1], HexGridColor[2]);
    for(int i=0; i<HEX_NUM; i++){
        for(int j=0; j<hex_num_vert+EXTRA_FIELD_ROWS; j++){
            glBegin(GL_LINE_STRIP);
            Vecf2 hex = hexVerticesAt(hex2gl(i,j,hex_radius));
            for(int k=0; k<6; k++)
                glVertex2f(hex[k][0], hex[k][1]);
            glVertex2f(hex[0][0], hex[0][1]);
            glEnd();
        }
    }
    glEndList();
    return list;
}
//------------------------------------------------------------------------------
GLuint GLWidget::createHexagons(){
    GLuint list = glGenLists(1);
    glNewList(list, GL_COMPILE);
    for(int i=0; i<HEX_NUM; i++){
        for(int j=0; j<hex_num_vert+EXTRA_FIELD_ROWS; j++){
            glBegin(GL_TRIANGLE_FAN);
            glColor3f(colorMap[i][j][0], colorMap[i][j][1], colorMap[i][j][2]);
            Vecf2 hex = hexVerticesAt(hex2gl(i,j,hex_radius));
            for(int k=0; k<6; k++)
                glVertex2f(hex[k][0], hex[k][1]);
            glEnd();
        }
    }
    glEndList();
    return list;
}
//------------------------------------------------------------------------------
void GLWidget::paintGL(){
    // Set up
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    // Draw the hexagons
/*
    for(int i=0; i<HEX_NUM; i++){
        for(int j=0; j<hex_num_vert+EXTRA_FIELD_ROWS; j++){
            glBegin(GL_TRIANGLE_FAN);
            glColor3f(colorMap[i][j][0], colorMap[i][j][1], colorMap[i][j][2]);
            Vecf2 hex = hexVerticesAt(hex2gl(i,j,hex_radius));
            for(int k=0; k<6; k++)
                glVertex2f(hex[k][0], hex[k][1]);
            glEnd();
        }
    }
*/
    glCallList(hexList);
    // Draw the piece
    if(pPiece != NULL){
        Vecf* pCol = pPiece->getColor();
        glColor3f((*pCol)[0], (*pCol)[1], (*pCol)[2]);
        int i,j;
        Veci2* pHexagons = pPiece->getHexagons();
        for(int k=0; k<4; k++){
            glBegin(GL_TRIANGLE_FAN);
            i = (*pHexagons)[k][0];
            j = (*pHexagons)[k][1];
            Vecf2 hex = hexVerticesAt(hex2gl(i,j,hex_radius));
            for(int l=0; l<6; l++)
                glVertex2f(hex[l][0], hex[l][1]);
            glEnd();
        }
    }
    // Draw the preview piece
    if(pPreviewPiece != NULL){
        Vecf* pCol = pPreviewPiece->getColor();
        glColor3f((*pCol)[0], (*pCol)[1], (*pCol)[2]);
        int i,j;
        Veci2* pHexagons = pPreviewPiece->getHexagons();
        for(int k=0; k<4; k++){
            glBegin(GL_TRIANGLE_FAN);
            i = (*pHexagons)[k][0];
            j = (*pHexagons)[k][1];
            Vecf2 hex = hexVerticesAt(hex2gl(i,j,hex_radius));
            Vecf v(2);
            for(int l=0; l<6; l++){
                v = addf(hex[l], previewOffset);
                glVertex2f(v[0], v[1]);
            }
            glEnd();
        }
    }
/*
    // Draw the hexagon grid
    glColor3f(HexGridColor[0], HexGridColor[1], HexGridColor[2]);
    for(int i=0; i<HEX_NUM; i++){
        for(int j=0; j<hex_num_vert+EXTRA_FIELD_ROWS; j++){
            glBegin(GL_LINE_STRIP);
            Vecf2 hex = hexVerticesAt(hex2gl(i,j,hex_radius));
            for(int k=0; k<6; k++)
                glVertex2f(hex[k][0], hex[k][1]);
            glVertex2f(hex[0][0], hex[0][1]);
            glEnd();
        }
    }

*/
    glCallList(hexgridList);
    // Draw piece border hexagons
    if(pPiece != NULL){
        glColor3f(White[0], White[1], White[2]);
        int i,j;
        Veci2* hexagons = pPiece->getHexagons();
        for(int k=0; k<4; k++){
            glBegin(GL_LINE_STRIP);
            i = (*hexagons)[k][0];
            j = (*hexagons)[k][1];
            Vecf2 hex = hexVerticesAt(hex2gl(i,j,hex_radius));
            for(int l=0; l<6; l++)
                glVertex2f(hex[l][0], hex[l][1]);
            glVertex2f(hex[0][0], hex[0][1]);
            glEnd();
        }
    }
    // Draw preview piece border hexagons
    if(pPreviewPiece != NULL){
        glColor3f(White[0], White[1], White[2]);
        int i,j;
        Veci2* hexagons = pPreviewPiece->getHexagons();
        for(int k=0; k<4; k++){
            glBegin(GL_LINE_STRIP);
            i = (*hexagons)[k][0];
            j = (*hexagons)[k][1];
            Vecf2 hex = hexVerticesAt(hex2gl(i,j,hex_radius));
            Vecf v(2);
            for(int l=0; l<6; l++){
                v = addf(hex[l], previewOffset);
                glVertex2f(v[0], v[1]);
            }
            v = addf(hex[0], previewOffset);
            glVertex2f(v[0], v[1]);
            glEnd();
        }
    }
    // Draw the open gl viewport area
    glColor3f(Grey[0], Grey[1], Grey[2]);
    glBegin(GL_LINE_STRIP);
    glVertex2f(0,0);
    glVertex2f(areaSize[0], 0);
    glVertex2f(areaSize[0], areaSize[1]);
    glVertex2f(0, areaSize[1]);
    glVertex2f(0, 0);
    glEnd();
    // Draw field separator
    glBegin(GL_LINES);
    glVertex2f(field[0], 0);
    glVertex2f(field[0], areaSize[1]);
    glEnd();
}
//------------------------------------------------------------------------------
void GLWidget::resizeGL(int width, int height){
    float glWidth = width;
    float glHeight = height;
    float wdgRatio = (float)(height)/width;
    // Correct gl width/height
    if (wdgRatio > field[1])
        glHeight = (int)(glWidth * field[1]);
    else if (wdgRatio < field[1])
        glWidth = (int)(glHeight / field[1]);
    // Paint within the whole window
    glViewport(0, 0, glWidth, glHeight);
    // Set orthographic projection where (0,0) is down left
    glMatrixMode(GL_PROJECTION);
    glLoadIdentity();
    glOrtho(0, 1, 0, field[1], -1, 1);
}
//------------------------------------------------------------------------------
void GLWidget::newGame(){
    speed = START_SPEED;
    // clean up the field
    for(int i=0; i<HEX_NUM; i++){
        for(int j=1; j<hex_num_vert+EXTRA_FIELD_ROWS; j++){
            colorMap[i][j] = *pBgColor;
            hexMap[i][j] = 0;
        }
    }
    glDeleteLists(hexList, 1);
    hexList = createHexagons();
    delete pPiece;
    delete pPreviewPiece;
    int type_id = selectPiece();
    pPiece = new Piece(type_id, topCenter, pieceColors[type_id]);
    type_id = selectPiece();
    pPreviewPiece = new Piece(type_id, topCenter, pieceColors[type_id]);
    repaint();
    score = 0;
    line_count = 0;
    statusMsg(msgLine());
    timer.start((int)speed, this);
    game_time.start();
}
//------------------------------------------------------------------------------
void GLWidget::pauseGame(){
    if(timer.isActive()){
        timer.stop();
        statusMsg(QString("Paused"));
    }
    else if(pPiece != NULL){
        timer.start((int)speed, this);
        statusMsg(msgLine());
    }
}
//------------------------------------------------------------------------------
void GLWidget::keyPressEvent(QKeyEvent *e){
    int key = e->key();
    if(!timer.isActive()) return;
    // USE ENUMS FOR COLLISION RESULTS!
    if(key == Qt::Key_Left){
        coll_check result = pPiece->move_left(hexMap);
        if(result == PIECE_HEAP){
            if(pPiece->move_down_left(hexMap) == NO_COLLISION) repaint();
        }else if(result == NO_COLLISION) repaint();
    }
    else if(key == Qt::Key_Right){
        coll_check result = pPiece->move_right(hexMap);
        if(result == PIECE_HEAP){
            if(pPiece->move_down_right(hexMap) == NO_COLLISION) repaint();
        }else if(result == NO_COLLISION) repaint();
    }
    else if(key == Qt::Key_Down){
        if(pPiece->rotate_left(hexMap)) repaint();
    }
    else if(key == Qt::Key_Up){
        if(pPiece->rotate_right(hexMap)) repaint();
    }
    else if(key == Qt::Key_Space){
         while(pPiece->fall(hexMap));
         repaint();
    }
}
//------------------------------------------------------------------------------
void GLWidget::timerEvent(QTimerEvent *){
    if(pPiece == NULL && (!timer.isActive())) return;
    // Check for collision
    if(pPiece->fall(hexMap)){
        repaint();
        return;
    }
    // Collision occurred, rasterize piece to map
    int i,j,k,l;
    bool gameOver = false;
    Veci2 *hexagons = pPiece->getHexagons();
    for(k=0; k<4; k++){
        i = (*hexagons)[k][0];
        j = (*hexagons)[k][1];
        hexMap[i][j] = 1;
        colorMap[i][j] = *pPiece->getColor();
        // Game Over
        if(j >= hex_num_vert-1) gameOver = true;
    }
    // Game Over
    if(gameOver){
        statusMsg(msgGameOver());
        timer.stop();
        glDeleteLists(hexList, 1);
        hexList = createHexagons();
        repaint();
        return;
    }
    timer.stop();
    j = 1;
    int rm_lines_count = 0;
    int row_sum;
    // Imaging a vertical line going from left to right
    while(j < hex_num_vert){
        row_sum = 0;
        for(i=0; i<HEX_NUM; i++) row_sum += hexMap[i][j];
        if(row_sum != HEX_NUM){
            j++;
            continue;
        }
        // Pull up all lines above this one
        for(k=j; k<hex_num_vert-1; k++){
            for(l=0; l<HEX_NUM; l++){
                hexMap[l][k] = hexMap[l][k+1];
                colorMap[l][k] = colorMap[l][k+1];
            }
        }
        rm_lines_count++;
    }
    // Check this
    timer.stop();
    // Update hexagon display list
    glDeleteLists(hexList, 1);
    hexList = createHexagons();
    // Generate next piece
    delete pPiece;
    pPiece = pPreviewPiece;
    int type_id = selectPiece();
    pPreviewPiece = new Piece(type_id, topCenter, pieceColors[type_id]);

    repaint();
    timer.start((int)speed, this);
    // Calculate score & speedup
    if(rm_lines_count == 0) return;

    line_count += rm_lines_count;
    // Lookup in table
    int lines_mult = scoreTable[scoreTable.size()-1];
    if (rm_lines_count <= scoreTable.size())
        lines_mult = scoreTable[rm_lines_count-1];
    score += lines_mult * rm_lines_count;
    // Speedup
    speed = pow(SPEED_MULT, rm_lines_count) * speed;
    statusMsg(msgLine());
}
