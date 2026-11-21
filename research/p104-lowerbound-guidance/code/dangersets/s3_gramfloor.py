# Gram-class per-term floor: rho(u,w) >= min over hyperplane flats F1,F2 of rank Q[P\F1, P\F2].
import pickle, numpy as np, collections, sys
from ds_lib import *; from ds_rank import *
L=e8_lines(); fl=pickle.load(open('flats.pkl','rb'))
for nm,P in (('halfspin',halfspin(L)),('E7A1',e7a1(L))):
    n=len(P); Q=Qmat(P); lab=Labels(Q); full=(1<<n)-1
    spans=collections.Counter()
    for m in fl[nm]:
        A=[i for i in range(n) if not (m>>i)&1]
        spans[lab.span(A)]+=1
    S=list(spans)
    print(nm,'h',lab.h,'flats',len(fl[nm]),'distinct complement label spans',len(S),'dims',sorted(collections.Counter(len(s) for s in S).items()))
    best=99; arg=None; hist=collections.Counter()
    for a in S:
        for b in S:
            r=lab.pair_rank(a,b); hist[r]+=1
            if r<best: best=r; arg=(len(a),len(b))
    print(' min pairing rank over flat pairs',best,arg,'hist',sorted(hist.items()))
    sys.stdout.flush()
