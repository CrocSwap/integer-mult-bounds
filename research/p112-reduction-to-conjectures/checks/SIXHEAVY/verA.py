# impl A re-check of the 9 negative facts used by GRRC kills + positive controls
import time, json, sys
from cov import *
FL={w:flats(w) for w in (4,5,6,7)}
for w in (1,2,3):   # small flats: dual-kernel enumeration too (fast)
    FL[w]=flats(w)
T={'E7':(0,1,2,3,4,5,6),'D7':(1,2,3,4,5,6,7)}
facts=" ".join(sys.argv[1:]).split()
out={}
for f in facts:
    t,ds=f.split(':'); O=off_parab(T[t]); t0=time.time()
    r=cover2(O,[int(x) for x in ds.split(',')],FL)
    out[f]='COVER' if r is not None else 'NONE'
    if r is not None:  # validate witness independently: union covers O and each mask is a genuine flat mask
        U=0
        for w,m in r: U|=m; assert any((F & O)==m for F in FL[w])
        assert O & ~U == 0
    print(f,out[f],round(time.time()-t0,1),flush=True)
