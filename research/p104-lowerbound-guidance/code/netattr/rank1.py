from inst5 import *
from fractions import Fraction as Fr
# is there w,v with T[t][p] = w_t v_p on all odd cells of readers x gathers?
cells=[(t,p) for t in readers for p in gathers if Q[t][p]]
bad=[]
for (t,p) in cells:
    for (t2,p2) in cells:
        if Q[t][p2] and Q[t2][p] and T[t][p]*T[t2][p2]!=T[t][p2]*T[t2][p]:
            bad.append(((labs[t],labs[p]),(labs[t2],labs[p2]),T[t][p],T[t2][p2],T[t][p2],T[t2][p]))
print('2x2 minors of fully-odd 2x2 subgrids violated:',len(bad)); print(bad[:3])
actR={t for t,p in nz}; actC={p for t,p in nz}
zero_conflict=[(labs[t],labs[p]) for (t,p) in cells if t in actR and p in actC and T[t][p]==0]
print('odd cells with active row&col but zero target:',len(zero_conflict),zero_conflict[:6])
# propagate
w={};v={}
t0=min(actR); w[t0]=Fr(1); changed=True; inc=0
while changed:
    changed=False
    for (t,p) in nz:
        if t in w and p not in v: v[p]=Fr(T[t][p])/w[t]; changed=True
        elif p in v and t not in w: w[t]=Fr(T[t][p])/v[p]; changed=True
        elif t in w and p in v and w[t]*v[p]!=T[t][p]: inc+=1
print('components covered rows',len(w),'/',len(actR),'cols',len(v),'/',len(actC),'inconsistent',inc)
print('w',{labs[t]:str(x) for t,x in w.items()}); print('v',{labs[p]:str(x) for p,x in v.items()})
