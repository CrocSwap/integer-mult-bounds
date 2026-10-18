# D=4 case A filter: in KMIN=4 cliques, all classes must be line classes u_w with eta_j ∝ c_w, supp c_w ⊆ {i_j} ∪ Ic
import sys, pickle, json, itertools, numpy as np
from lib import Bd, LAB, C, n
par=lambda x: bin(x).count('1')&1
lineclass={}
for w in range(n):
    S=set(t for t in range(n) if Bd[t][w]==1)
    zs=[z for z in range(1,512) if set(t for t in range(n) if par(z&LAB[t]))==S]
    assert len(zs)==1; lineclass[zs[0]]=w
for f in sys.argv[1:]:
    Ic=tuple(int(x) for x in f[6:-4].split('_')) if f!='found_none.pkl' else ()
    cl=pickle.load(open(f,'rb'))
    good=[]
    for c in cl:
        if all(z in lineclass for i,z in c):
            ws=[lineclass[z] for i,z in c]
            if all(set(np.nonzero(C[w])[0])<=set([i])|set(Ic) and C[w][i]!=0 for (i,z),w in zip(c,ws)): good.append((c,ws))
    print(f,'cliques',len(cl),'all-line-class',sum(all(z in lineclass for i,z in c) for c in cl),'column-swap-compatible',len(good))
    for g in good[:5]: print('  ',g)
# filters on column-swap-compatible cliques: (1) swap lines pairwise non-orthogonal (Bd=0), (2) joint pair system with eta_j = beta_j c_wj
import sympy as sp
O={z:set(t for t in range(n) if par(z&LAB[t])) for z in range(1,512)}
for f in sys.argv[1:]:
    Ic=tuple(int(x) for x in f[6:-4].split('_'))
    cl=pickle.load(open(f,'rb')); surv=[]
    for c in cl:
        if not all(z in lineclass for i,z in c): continue
        ws=[lineclass[z] for i,z in c]
        if not all(set(np.nonzero(C[w])[0])<=set([i])|set(Ic) and C[w][i]!=0 for (i,z),w in zip(c,ws)): continue
        f1=all(Bd[w][w2]==0 for w,w2 in itertools.combinations(ws,2))
        rows=[]
        for a,b in itertools.combinations(range(4),2):
            for t in sorted(O[c[a][1]]&O[c[b][1]]):
                r=[0]*4; r[a]=sum(C[t][k]*C[ws[a]][k] for k in range(8)); r[b]=-sum(C[t][k]*C[ws[b]][k] for k in range(8)); rows.append(r)
        ker=sp.Matrix(rows).nullspace() if rows else [sp.eye(4)[:,k] for k in range(4)]
        f2=bool(ker) and all(any(k[j]!=0 for k in ker) for j in range(4))
        if f1 and f2: surv.append((c,ws))
    print(f,'survive (non-orth swap lines + joint beta system):',len(surv))
    pickle.dump(surv,open('d4A_surv.pkl','wb'))
    for s in surv[:4]: print('  ',s)
