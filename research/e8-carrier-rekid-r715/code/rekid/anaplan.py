import sys,pickle
from collections import Counter
import hx, frames as Fm
h,atoms=hx.load(); base=hx.default_plans(atoms)
plans=pickle.load(open(sys.argv[1],'rb'))
def name(t,x):
    A=atoms[t]
    for k,v in A.items():
        if k!='fo' and v==x: return k
    sz=bin(h.content[x]).count('1') if x>=0 else 0
    return ('src%d'%x) if x<120 else 'S[%d|d%d|#%d]'%(sz,h.dim[x],x)
diff=0; kinds=Counter()
for t in sorted(plans):
    if [sorted(s) for s in plans[t]]==[sorted(s) for s in base[t]] : continue
    # canonical compare as set of frozensets
    if set(frozenset(s) for s in plans[t])==set(frozenset(s) for s in base[t]): continue
    diff+=1
    if diff<=12:
        print('t',t,'base',[[name(t,x) for x in s] for s in base[t]])
        print('   new ',[[name(t,x) for x in s] for s in plans[t]])
    ncancel=sum(1 for c in Counter(x for s in plans[t] for x in s).values() if c>1)
    kinds[(len(plans[t]),ncancel)]+=1
print('targets changed',diff,'of',len(plans)); print(sorted(kinds.items()))
h2=h
for t in plans: h2.need[t]=hx.need_of(h2,plans[t]); assert hx.check_target(h2,t)
R,W=hx.R_of(h2); print('R',R,W.stats)
