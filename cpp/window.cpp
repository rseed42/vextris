#include <QtGui>
#include "glwidget.h"
#include "window.h"
//------------------------------------------------------------------------------
// Main Window
//------------------------------------------------------------------------------
Window::Window() : icon(ICON_FILE){
    wndSize = new QSize(400,600);
    glWidget = new GLWidget(this);
    glWidget->setMinimumWidth(wndSize->width());
    glWidget->setMinimumHeight(wndSize->height());
    setCentralWidget(glWidget);
    glWidget->setFocusPolicy(Qt::StrongFocus);
    setWindowTitle(tr("OpenGL Qt4 C++ Template"));
    createActions();
    createMenus();
    createStatusBar();
    setWindowIcon(icon);
}
//------------------------------------------------------------------------------
void Window::createActions(){
    pNewGame = new QAction("&New Game", this);
    pNewGame->setShortcut(QKeySequence(Qt::Key_N));
    pNewGame->setStatusTip("Start a new game");
    connect(pNewGame, SIGNAL(triggered()), glWidget, SLOT(newGame()));

    pPauseGame = new QAction("&Pause Game", this);
    pPauseGame->setShortcut(QKeySequence(Qt::Key_P));
    pPauseGame->setStatusTip("Pause the current game");
    connect(pPauseGame, SIGNAL(triggered()), glWidget, SLOT(pauseGame()));

    pQuitGame = new QAction("&Quit", this);
    pQuitGame->setShortcut(QKeySequence(Qt::Key_Q));
    pQuitGame->setStatusTip("Quit VexTris");
    connect(pQuitGame, SIGNAL(triggered()), this, SLOT(close()));

    pAboutGame = new QAction("&About", this);
    pAboutGame->setShortcut(QKeySequence(Qt::Key_A));
    pAboutGame->setStatusTip("About VexTrix");
    connect(pAboutGame, SIGNAL(triggered()), this, SLOT(aboutVexTris()));
}
//------------------------------------------------------------------------------
void Window::createMenus(){
    pFileMenu = menuBar()->addMenu("&Game");
    pFileMenu->addAction(pNewGame);
    pFileMenu->addAction(pPauseGame);
    pFileMenu->addSeparator();
    pFileMenu->addAction(pQuitGame);

    pHelpMenu = menuBar()->addMenu("&Help");
    pHelpMenu->addAction(pAboutGame);
}
//------------------------------------------------------------------------------
void Window::createStatusBar(){
  statusBar()->showMessage("VexTris");
}
//------------------------------------------------------------------------------
void Window::aboutVexTris(){
   QString msg("<h4>VexTris (c) 2013 Venelin Petkov</h4>"\
   "<h5>Directions</h5>"\
   "<p>Use the arrow keys to rotate and move the falling piece.</p>"\
   "<h5>Score Table</h5>"\
   "<table><tr><th>#Lines</th><th>Score</th>"\
   "<tr><td>1</td><td>100</td>"\
   "<tr><td>2</td><td>200</td>"\
   "<tr><td>3</td><td>400</td>"\
   "<tr><td>>=4</td><td>800</td></table>"\
   "<h5>More Information</h5>"\
   "<p>Homepage: <a href='https://github.com/rseed42/vextris/wiki'>"\
   "http://github.com/rseed42/vextris</a></p>"\
   );
   QMessageBox::about(this, "About VexTris", msg);
}
