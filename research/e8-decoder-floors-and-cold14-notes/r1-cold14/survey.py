"""survey entering helpers: start frame, end frame, cone violations for Lean (E,U) pairs."""
import sys
from common import *
hpe_word=rd(sys.argv[1]); recipe=rd(sys.argv[2])
w=BCE.apply(copy.deepcopy(hpe_word),recipe)
v,R=w['report']['v'],w['report']['R'];n=2*v+R
start,endB=frames_endB(w)
tau=lambda x: x^(43 if bin(x&43).count('1')%2 else 0)
LEAN={(30,):(256,128,64,32,18,10,6,1),(45,):(256,128,64,33,16,9,5,2),(51,):(256,128,64,33,17,8,4,3)}
LEANRAW={span([tau(x) for x in E]):span([tau(x) for x in U]) for E,U in LEAN.items()}
print('raw lean pairs',LEANRAW)
hf={int(k):span(f) for k,f in w['helper_final'].items()}
ent=Counter();groups=defaultdict(list)
for k,f in w['start_extra'].items():
    E=span(f);h=int(k);ent[(len(E),E in LEANRAW, h in hf)]+=1
    if len(E)==1 and h not in hf: groups[E].append(h)
print(ent)
for E,hs in groups.items(): print('E',E,'lean' if E in LEANRAW else '', len(hs), hs)
P,Pinv,comp=main_maps(w)
premixed={r for e in recipe['premix'] for r in regs(e)}
for E,hs in groups.items():
    if E not in LEANRAW: continue
    U=LEANRAW[E]
    QU={g for g in range(n) if inside(endB[g],U)}
    for h in hs:
        rowv=[g for g,x in Pinv[h].items() if x and g not in QU]
        colv=[g for g in range(n) if g!=h and P[g].get(h) and g not in QU]
        print(h,'premixed' if h in premixed else '','row',len(rowv),rowv[:8],'col',len(colv),colv[:8],'endB',endB[h])
