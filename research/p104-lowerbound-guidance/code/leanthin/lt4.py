# variants of lt1 LP: cmax rows, TR on/off.  usage lt4.py cmax tr k...
import sys,numpy as np
import lt1
from math import comb
cmax=int(sys.argv[1]); tr=int(sys.argv[2])
lt1.rowlist.__defaults__=(cmax,)
orig_rhs=lt1.rhs; orig_rv=lt1.role_vec
if not tr:
    # neutralise TRIPLE row: rhs 0 (row stays, trivially satisfied since coefficients >= 0)
    def rhs2(k,rows):
        b=orig_rhs(k,rows); b[-1]=0; return b
    lt1.rhs=rhs2
s=.99
for k in map(int,sys.argv[3:]):
    v,sup,y,rows=lt1.solve(k)
    hub=lambda D:(8*D+1)**s-D*8**s
    v1=9**s-8**s; v2p=17**s-16**s
    d1=k*k/(k-1); F=2*k-2+2*(hub(k)-1)+d1*(v1-1)+(k-4)*(v2p-1)
    print(f'cmax{cmax} tr{tr} k{k}: LP {v:.4f}  chart(2 hubs,k^2/(k-1) leaves,k-4 pairs) {104*F/k:.4f}',flush=True)
    for x in sorted(sup,key=lambda t:-t[0])[:6]: print('   ',round(x[0],4),x[1],x[2] if len(x[2])<6 else (x[2][:3],'..',len(x[2])))
