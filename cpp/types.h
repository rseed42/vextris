#ifndef TYPES_H
#define TYPES_H
//------------------------------------------------------------------------------
#include <QtOpenGL>
//------------------------------------------------------------------------------
enum coll_check { NO_COLLISION, LEFT_BORDER, RIGHT_BORDER, PIECE_HEAP};
//------------------------------------------------------------------------------
// We could use smaller integers, but this program doesn't take up that many
// resources anyway and the code is easier to read.
using Veci = QVector<GLint>;
using Veci2 = QVector<QVector<GLint> >;
using Veci3 = QVector<QVector<QVector<GLint> > >;
using Vecf = QVector<GLfloat>;
using Vecf2 = QVector<QVector<GLfloat> >;
using Vecf3 = QVector<QVector<QVector<GLfloat> > >;
//------------------------------------------------------------------------------
template <class T>
T addT(T a, T b);
Vecf addf(Vecf a, Vecf b);
Veci addi(Veci a, Veci b);
//------------------------------------------------------------------------------
// Create arrays of defined size
Vecf*  getVecf(int len);
Vecf2* getVecf2(int d0, int d1);
Vecf3* getVecf3(int d0, int d1, int d2);
//------------------------------------------------------------------------------
#endif
