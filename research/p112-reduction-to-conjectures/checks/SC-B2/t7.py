from cov4 import *
gens=load_gens('grp.out')
comp=[6,6,6,6,4,1,1,1,1]
for I in itertools.combinations(range(8),6):
    P_=parabolic(I); T=[t for t in range(n) if t not in set(P_)]
    if len(T)>92: continue
    print(I,len(P_),end=' ',flush=True)
    if I==(0,1,2,3,4,5): print(cover_set4(T,comp,gens,verbose=False,tmo=1000))
    else: print(cover_set3(T,comp))
