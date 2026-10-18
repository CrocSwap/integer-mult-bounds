import sys
from common import *
hpe_word=rd(sys.argv[1]); recipe=rd(sys.argv[2])
w=BCE.apply(copy.deepcopy(hpe_word),recipe)
v,R=w['report']['v'],w['report']['R'];n=2*v+R
start,endB=frames_endB(w)
hf={int(k):span(f) for k,f in w['helper_final'].items()}
P,Pinv,comp=main_maps(w)
H0=[h for h in range(2*v,n) if start[h]==() and h not in hf]
colsupp={h:[g for g in range(n) if P[g].get(h)] for h in H0}
out=[]
for a in range(1,512):
    U=span([x for x in range(1,512) if bin(x&a).count('1')%2==0])  # hyperplane = a-perp
    QU={g for g in range(n) if inside(endB[g],U)}
    K=[h for h in H0 if h in QU]
    if not K: continue
    S=sorted({g for h in H0 for g,x in Pinv[h].items() if x and g not in QU})
    Sset=set(S)
    rr=modrank([{g:x for g,x in Pinv[h].items() if g in Sset} for h in H0])
    Nr=len(H0)-rr
    # column condition: m over H0 with P[g,:]m=0 for g not in QU: nullity = |H0| - rank of the (rows not in QU) restricted to H0 columns
    rowsC=sorted({g for h in H0 for g in colsupp[h] if g not in QU})
    H0s=set(H0)
    rc=modrank([{h:x for h,x in P[g].items() if h in H0s} for g in rowsC])
    Nc=len(H0)-rc
    out.append((min(Nr,Nc),Nr,Nc,len(K),a,U))
out.sort(reverse=True)
for o in out[:25]: print(o)
