from symlp import lp
from collections import Counter
for I in [0,1,2,4,8]:
    for p in [[7]*9+[1],[7]*9,[7]*10,[7]*10+[1],[7]*8+[6,1],[7]*8+[6]+[1]*2,[7]*9+[2],[7]*8+[6,6]]:
        if sum(p)<=63+I:
            v,b=lp(Counter(p),0,112+I,exact=False); print(I,sum(p),p,round(v,2),'need',112+I, 'OK' if v<112+I else 'FAIL')
