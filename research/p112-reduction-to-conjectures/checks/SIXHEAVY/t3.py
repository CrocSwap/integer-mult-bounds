from sa import *
FL={w:flats(w) for w in (4,5,6,7)}
O=off_parab((0,1,2,3,4,5,6)); print('root Off',pc(O))
for w in (4,5,6,7):
    from collections import Counter
    c=Counter(pc(m&O) for m in FL[w]); print(w, sorted(c.items())[-4:])
