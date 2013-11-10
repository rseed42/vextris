#ifndef WINDOW_H
#define WINDOW_H
#include <QMainWindow>
//------------------------------------------------------------------------------
class GLWidget;
//------------------------------------------------------------------------------
// Main Window
//------------------------------------------------------------------------------
class Window : public QMainWindow{
    Q_OBJECT

public:
    Window();

private slots:
    void aboutVexTris();

private:
    void createActions();
    void createMenus();
    void createStatusBar();
    //
    QSize* wndSize;
    GLWidget* glWidget;
    QMenu* pFileMenu;
    QAction* pNewGame;
    QAction* pPauseGame;
    QAction* pQuitGame;
    QMenu* pHelpMenu;
    QAction* pAboutGame;
};

#endif
