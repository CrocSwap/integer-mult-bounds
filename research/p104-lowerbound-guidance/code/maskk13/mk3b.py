import sys,mk3
from ic1 import BAR
for k in range(9,21):
    out=[]
    for d in range(k-8,k-1):
        if d<3:continue
        v=mk3.fam(k,d)
        out.append('d%d=%s'%(d,'%.3f'%v if v else 'inf'))
    print('k',k,' '.join(out),flush=True)
