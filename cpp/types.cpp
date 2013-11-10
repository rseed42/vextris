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
