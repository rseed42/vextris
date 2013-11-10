#include <QtGui>
#include "glwidget.h"
#include "window.h"
//------------------------------------------------------------------------------
// Main Window
//------------------------------------------------------------------------------
Window::Window(){
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
   QString msg("<h4>VexTris</h4><div>Copyright (c) 2013 Venelin Petkov</div>");
   QMessageBox::about(this, "About VexTris", msg);
}
