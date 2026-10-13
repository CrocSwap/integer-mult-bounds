import sys
from common import *
hpe_word=rd(sys.argv[1]); recipe=rd(sys.argv[2])
w=BCE.apply(copy.deepcopy(hpe_word),recipe)
v,R=w['report']['v'],w['report']['R'];n=2*v+R
start,endB=frames_endB(w)
first={}
for part in ('A','B'):
    for e in w[part]:
        for r in regs(e): first.setdefault(r,span(e[-1]))
tau=lambda x: x^(43 if bin(x&43).count('1')%2 else 0)
LEAN={(30,):(256,128,64,32,18,10,6,1),(45,):(256,128,64,33,16,9,5,2),(51,):(256,128,64,33,17,8,4,3)}
LEANRAW={span([tau(x) for x in E]):span([tau(x) for x in U]) for E,U in LEAN.items()}
hf={int(k):span(f) for k,f in w['helper_final'].items()}
P,Pinv,comp=main_maps(w)
for E,U in LEANRAW.items():
    QU={g for g in range(n) if inside(endB[g],U)}
    Hc=[h for h in range(2*v,n) if start[h]==() and h not in hf and inside(E,first.get(h,span([511]*0) or E))]
    HE=[h for h in range(2*v,n) if start[h]==E]
    H=HE+Hc
    S={g for h in H for g,x in Pinv[h].items() if x and g not in QU}
    rk=modrank([{g:x for g,x in Pinv[h].items() if g in S} for h in H])
    rk2=modrank([{g:x for g,x in Pinv[h].items() if g in S} for h in [h for h in HE if h in hf]+Hc])
    print(E,'E-group',len(HE),'ended',len([h for h in HE if h in hf]),'mixable cold',len(Hc),'nullity',len(H)-rk,'nullity without nonended E',len(H)-len([h for h in HE if h not in hf])-rk2)
    print('   cold mixable:',[(h,first.get(h),endB[h],h in hf) for h in Hc])
    if not Hc: continue
    rb=nullspace_rows([Pinv[h] for h in H],S)
    for pv,r in rb.items():
        hs={H[j]:str(c) for j,c in r.items()}
        if any(H[j] in HE and H[j] not in hf for j in r):
            print('   null vec',hs)
