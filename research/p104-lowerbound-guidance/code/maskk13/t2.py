import sys,itertools
sys.path.insert(0,'../intcaller')
import ic1
from ic1 import val,partitions,rowdefs,verify
from fractions import Fraction as Fr
k=13
R=rowdefs(k)
need=ic1.BAR*k/104
H=list(partitions(13,11)); Rt=list(partitions(6,11))
pure=(2,(2,)); chord=(2,(1,1))
def vec(D,P):return [f(D,P) for (nm,f,mc,s,r) in R]
rhs=[r for (nm,f,mc,s,r) in R]; mcs=[mc for (nm,f,mc,s,r) in R]; names=[nm for (nm,f,mc,s,r) in R]
vh={P:vec(13,P) for P in H}; vr={P:vec(6,P) for P in Rt}; vp=vec(*pure); vc=vec(*chord)
ones=lambda P:sum(1 for L in P if L==1)
cnt=0;ok=[]
for i,P1 in enumerate(H):
  for P2 in H[i:]:
    for PR in Rt:
      for c in range(22):
        tot_ones=ones(P1)+ones(P2)+ones(PR)+2*c
        if tot_ones<26:continue
        v=val(13,P1)+val(13,P2)+val(6,PR)+c*val(*chord)+(21-c)*val(*pure)
        if v<=need:continue
        cnt+=1
        good=True
        for ri in range(len(R)):
            lhs=vh[P1][ri]+vh[P2][ri]+vr[PR][ri]+c*vc[ri]+(21-c)*vp[ri]+mcs[ri]*26
            r=rhs[ri];s=R[ri][3]
            if s=='==':
                if lhs!=r:good=False;break
            elif lhs<r:good=False;break
        if good:ok.append((P1,P2,PR,c,float(v*104/k)))
print('pre-row',cnt,'type-level members',len(ok))
import collections
print(collections.Counter(c for *_,c,v in ok))
ok.sort(key=lambda t:-t[4])
for o in ok[:15]:print(o)
import pickle;pickle.dump(ok,open('types13.pkl','wb'))
