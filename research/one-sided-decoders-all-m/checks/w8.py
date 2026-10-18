# which hyperplane label-flats have complement of real rank <=7 (=> weight-8 codewords p_h)
from base import *
par=lambda x: bin(x).count('1')&1
Lnp=np.array([[float(c) for c in r] for r in L])
for z in range(1,512):
    inn=[t for t in range(v) if not par(z&LAB[t])]
    out=[t for t in range(v) if par(z&LAB[t])]
    r=np.linalg.matrix_rank(Lnp[out]) if out else 0
    if r<=7:
        # normal h
        _,_,Vt=np.linalg.svd(Lnp[out]); h=Vt[-1]
        off=[t for t in range(v) if abs(Lnp[t]@h)>1e-9]
        isF=[i for i,f in enumerate(F0) if abs(abs(np.array([float(c) for c in f])@h)/np.linalg.norm(h)-np.sqrt(2))<1e-6]
        print('z',z,'flat lines',len(inn),'compl rank',r,'|Off(h)|',len(off),'Off inside flat',set(off)<=set(inn),'h~f_i',isF)
# max hyperplane section of P112 (lines in a real hyperplane spanned by roots): check via 7-subsets is heavy; use flats of E7 type
