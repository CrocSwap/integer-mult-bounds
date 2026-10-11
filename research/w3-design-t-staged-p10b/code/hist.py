"""One-stage local child histogram of a PR249 records.bin (MOVE rank>0, COPY rank). usage: hist.py A.bin [B.bin] -> prints H(A) and delta B-A"""
import sys,collections,numpy as np
def H(p):
    r=np.fromfile(p,dtype='<i4').reshape(-1,6);c=collections.Counter()
    m=r[(r[:,0]==0)&(r[:,4]>0)];c.update(m[:,4].tolist())
    cp=r[r[:,0]==2];c.update(cp[:,5].tolist())
    return c,len(r)
a,na=H(sys.argv[1]);print('A',na,dict(sorted(a.items())))
if len(sys.argv)>2:
    b,nb=H(sys.argv[2]);d={k:b[k]-a[k] for k in sorted(set(a)|set(b)) if b[k]-a[k]}
    print('B',nb,dict(sorted(b.items())));print('delta',','.join('%d:%d'%kv for kv in d.items()))
