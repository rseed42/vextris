#ifndef PIECE_H
#define PIECE_H
//------------------------------------------------------------------------------
#include <QtCore>
#include "types.h"
//------------------------------------------------------------------------------
class Piece{
public:
    Piece(int type_id, Veci pos, Vecf color, int rot_id=0);
    ~Piece();
    Vecf* getColor(){ return &color; }
    Veci2* getHexagons(){ return pHexagons; }
    bool rotate_left(Veci2& hexMap){ return rotate(-1, hexMap); }
    bool rotate_right(Veci2& hexMap){ return rotate(1, hexMap); }
    coll_check move_left(Veci2& hexMap){ return move(-1, hexMap); }
    coll_check move_down_left(Veci2& hexMap){ return move(-1, hexMap, -1); }
    coll_check move_right(Veci2& hexMap){ return move(1, hexMap); }
    coll_check move_down_right(Veci2& hexMap){ return move(1, hexMap, -1); }
    bool fall(Veci2& hexMap);

private:
    // Have to think a bit how to pass by reference, since we are
    // basically using the same thing
    static const Veci3 NEIGHBORS;
    static const Veci3 SHAPES;
    Veci2* translateHexagons(Veci2 *hexagons, Veci &new_pos);
    Veci2* buildHexagons(Veci &pos, int rot_id);
    coll_check collision(Veci2* hexagons, Veci2& hexMap);
    bool rotate(int left_right, Veci2& hexMap);
    coll_check move(int left_right, Veci2& hexMap, int vert=0);
    int type_id;
    Veci pos;
    Vecf color;
    int rot_id;
    Veci2* pHexagons;
};
#endif
