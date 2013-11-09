VPATH += ../shared
INCLUDEPATH += ../shared

HEADERS       = types.h \
                glwidget.h \
                window.h \
                piece.h
SOURCES       = types.cpp \
                glwidget.cpp \
                main.cpp \
                window.cpp \
                piece.cpp
QT           += opengl

QMAKE_CXXFLAGS += -std=c++11
