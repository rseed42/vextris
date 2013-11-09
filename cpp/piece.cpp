#include "piece.h"
//------------------------------------------------------------------------------
const Veci3 Piece::NEIGHBORS = {
    {{0,0},{0,1},{1,1},{1,0},{0,-1},{-1,0},{-1,1},{0,2},{1,2},{2,1},{2,0},
     {2,-1},{1,-1},{0,-2},{-1,-1},{-2,-1},{-2,0},{-2,1}, {-1,2}},
    {{0,0},{0,1},{1,0},{1,-1},{0,-1},{-1,-1},{-1,0},{0,2},{1,1},{2,1},{2,0},
     {2,-1},{1,-2},{0,-2},{-1,-2},{-2,-1},{-2,0},{-2,1},{-1,1}}};
const Veci3 Piece::SHAPES = {
    {{0,1,3,5},{0,2,4,6}},
    {{0,1,4,13},{0,2,5,15},{0,3,6,17},{0,4,1,7},{0,5,2,9},{0,6,3,11}},
    {{0,3,4,5},{0,4,5,6},{0,5,6,1},{0,6,1,2},{0,1,2,3},{0,2,3,4}},
    {{1,4,5,6},{2,5,6,1},{3,6,1,2},{4,1,2,3},{5,2,3,4},{6,3,4,5}},
    {{0,1,4,12},{0,2,5,14},{0,3,6,16},{0,4,1,18},{0,5,2,8},{0,6,3,10}},
    {{0,1,4,14},{0,2,5,16},{0,3,6,18},{0,4,1,8},{0,5,2,10},{0,6,3,12}},
    {{0,1,3,12},{0,2,4,14},{0,3,5,16},{0,4,6,18},{0,5,1,8},{0,6,2,10}},
    {{0,1,5,14},{0,2,6,16},{0,3,1,18},{0,4,2,8},{0,5,3,10},{0,6,4,12}},
    {{0,1,3,4},{0,2,4,5},{0,3,5,6},{0,4,6,1},{0,5,1,2},{0,6,2,3}},
    {{0,1,5,4},{0,2,6,5},{0,3,1,6},{0,4,2,1},{0,5,3,2},{0,6,4,3}}};
//------------------------------------------------------------------------------
Piece::Piece(int type_id, Veci pos, Vecf color, int rot_id):
    type_id(type_id), pos(pos), color(color), rot_id(rot_id),
    hexagons(buildHexagons(pos, rot_id)){
}
//------------------------------------------------------------------------------
Piece::~Piece(){
}
//------------------------------------------------------------------------------
Veci2 Piece::translate(Veci2 &hexagons, Veci &new_pos){
    Veci2 newHexagons(4);
    for(int i=0; i<4; i++)
        newHexagons[i] = addi(hexagons[i], new_pos);
    return newHexagons;
}
//------------------------------------------------------------------------------
Veci2 Piece::buildHexagons(Veci &new_pos, int new_rot_id){
    Veci2 newHexagons;
    int hex_id;
    for(int i=0; i<4; i++){
        hex_id = SHAPES[type_id][new_rot_id][i];
        newHexagons.append(NEIGHBORS[new_pos[0]&1][hex_id]);
    }
    return translate(newHexagons, new_pos);
}
//------------------------------------------------------------------------------
int Piece::collision(Veci2& hexagons, Veci2& hexMap){
    // Somewhat different from the Python version due to lack of syntax
    // Check border collisions first
    for(int i=0; i<4; i++){
        if (hexagons[i][0] < 0) return 1;
        // Don't forget that hexMap is transposed to what we imagine
        if (hexagons[i][0] > hexMap.size()-1) return 2;
    }
    // Collision with the piece heap
    int i, j;
    for (int k=0; k<4; k++){
        i = hexagons[k][0];
        j = hexagons[k][1];
        if(hexMap[i][j] > 0) return 3;
    }
    return 0;
}
//------------------------------------------------------------------------------
bool Piece::rotate(int left_right, Veci2& hexMap){
    int rid = rot_id + left_right;
    int rot_shapes = SHAPES[type_id].size();
    int new_rot_id = rid < 0 ? rot_shapes - 1 : rid % rot_shapes;
    Veci2 newHexagons = buildHexagons(pos, new_rot_id);
    if(collision(newHexagons, hexMap)) return false;
    rot_id = new_rot_id;
    hexagons = newHexagons;
    return true;
}
//------------------------------------------------------------------------------
int Piece::move(int left_right, Veci2& hexMap, int vert){
    Veci new_pos = addi(pos, Veci{left_right, vert});
    Veci2 newHexagons = buildHexagons(new_pos, rot_id);
    int coll_code = collision(newHexagons, hexMap);
    if (coll_code > 0) return coll_code;
    pos = new_pos;
    hexagons = newHexagons;
    return 0;
}
//------------------------------------------------------------------------------
bool Piece::fall(Veci2& hexMap){
    Veci new_pos = {pos[0], pos[1] - 1};
    Veci2 newHexagons = buildHexagons(new_pos, rot_id);
    if(collision(newHexagons, hexMap)) return false;
    pos = new_pos;
    hexagons = newHexagons;
    return true;
}
