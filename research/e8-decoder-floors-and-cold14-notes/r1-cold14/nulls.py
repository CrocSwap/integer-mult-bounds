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
    H=sorted(int(k) for k,f in w['start_extra'].items() if span(f)==E )
    QU={g for g in range(n) if inside(endB[g],U)}
    K=[h for h in H if h in QU]
    rowsC=sorted({g for g in range(n) if g not in QU for h in H if P[g].get(h)})
    C=sympy.Matrix([[P[g].get(h,0) for h in H] for g in rowsC]) if rowsC else sympy.zeros(0,len(H))
    colsD=sorted({g for h in H for g,x in Pinv[h].items() if x and g not in QU})
    D=sympy.Matrix([[Pinv[h].get(g,0) for g in colsD] for h in H])
    ncol=C.nullspace() if rowsC else [sympy.eye(len(H))[:,i] for i in range(len(H))]
    nrow=D.T.nullspace()
    print('E',E,'U',U,'|H|',len(H),'candidates K',K,'ended',[h for h in H if h in hf])
    print('  C rows',len(rowsC),'nullity',len(ncol),' D cols',len(colsD),colsD,'left-nullity',len(nrow))
    def supp(vs): return [[H[i] for i in range(len(H)) if v[i]!=0] for v in vs]
    print('  col-null supports',supp(ncol)[:12])
    print('  row-null supports',supp(nrow)[:12])
