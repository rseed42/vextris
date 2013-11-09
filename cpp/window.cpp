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
    pNewGame = new QAction(tr("&New Game"), this);
    pNewGame->setShortcuts(QKeySequence::New);
    pNewGame->setStatusTip(tr("Start a new game"));
//    connect(pNewGame, SIGNALS(triggered()), this, SLOT(startGame()));

    pPauseGame = new QAction(tr("&Pause Game"), this);
    pPauseGame->setStatusTip(tr("Pause the current game"));

    pQuitGame = new QAction(tr("&Quit"), this);
    pQuitGame->setStatusTip(tr("Quit VexTris"));

    pAboutGame = new QAction(tr("&About"), this);
    pAboutGame->setStatusTip(tr("About VexTrix"));
}
//------------------------------------------------------------------------------
void Window::createMenus(){
    pFileMenu = menuBar()->addMenu(tr("&Game"));
    pFileMenu->addAction(pNewGame);
    pFileMenu->addAction(pPauseGame);
    pFileMenu->addSeparator();
    pFileMenu->addAction(pQuitGame);

    pHelpMenu = menuBar()->addMenu(tr("&Help"));
    pHelpMenu->addAction(pAboutGame);

}
//------------------------------------------------------------------------------
void Window::createStatusBar(){
  statusBar()->showMessage(tr("VexTris (c) 2013 Venelin Petkov"));

}
