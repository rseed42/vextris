#include "types.h"
//------------------------------------------------------------------------------
// Of course, a and b must have the same size
template <class T>
T addT(T a, T b){
    Q_ASSERT(a.size() == b.size());
    T res(a.size());
    for(int i=0; i<a.size(); i++)
        res[i] = a[i] + b[i];
    return res;
}
Vecf addf(Vecf a, Vecf b){
    return addT<Vecf>(a, b);
}
Veci addi(Veci a, Veci b){
    return addT<Veci>(a, b);
}
//------------------------------------------------------------------------------
/*
Vecf*  getVecf(int len){
    Vecf* pVec = new Vecf(len);
    return pVec;
}
Vecf2* getVecf2(int d0, int d1){
    Vecf2* pVec = new Vecf2(d0);
    for(int i=0; i<d0; i++)
        *pVec[i]->resize(d1);
    return pVec;
}
Vecf3* getVecf3(int d0, int d1, int d2){
    Vecf3* pVec = new Vecf3(d0);
    for(int i=0; i<d0; i++){
        for(int j=0; j<d1; j++)
            *pVec[i][j]->resize(d2);
    }
    return pVec;
}*/
