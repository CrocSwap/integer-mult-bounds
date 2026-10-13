import sys,sympy
from common import *
hpe_word=rd(sys.argv[1]); recipe=rd(sys.argv[2])
w=BCE.apply(copy.deepcopy(hpe_word),recipe)
v,R=w['report']['v'],w['report']['R'];n=2*v+R
start,endB=frames_endB(w)
tau=lambda x: x^(43 if bin(x&43).count('1')%2 else 0)
LEAN={(30,):(256,128,64,32,18,10,6,1),(45,):(256,128,64,33,16,9,5,2),(51,):(256,128,64,33,17,8,4,3)}
LEANRAW={span([tau(x) for x in E]):span([tau(x) for x in U]) for E,U in LEAN.items()}
hf={int(k):span(f) for k,f in w['helper_final'].items()}
P,Pinv,comp=main_maps(w)
for E,U in LEANRAW.items():
    QU={g for g in range(n) if inside(endB[g],U)}
    # any helper whose start frame is inside E (cold or E itself)
    H=sorted(h for h in range(2*v,n) if inside(start[h],E))
    ended=[h for h in H if h in hf]
    colsD=sorted({g for h in H for g,x in Pinv[h].items() if x and g not in QU})
    S=set(colsD);rk=modrank([{g:x for g,x in Pinv[h].items() if g in S} for h in H])
    Hp=[h for h in H if not (start[h]==E and h not in hf)]
    rk2=modrank([{g:x for g,x in Pinv[h].items() if g in S} for h in Hp])
    print('  without nonended E helpers: |H|',len(Hp),'nullity',len(Hp)-rk2)
    Hc=[h for h in H if start[h]==()]
    rk3=modrank([{g:x for g,x in Pinv[h].items() if g in S} for h in Hc]);print('  cold only',len(Hc),'nullity',len(Hc)-rk3,'cold ended',len([h for h in Hc if h in hf]))
    print(E,'|H|',len(H),'ended',len(ended),'left-nullity',len(H)-rk)
