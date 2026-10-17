# SC-A2 D7 plane fact, independent: 32 directions served by one D7 8-set; planes through pairs.
import pickle, numpy as np, sympy, itertools
import p112 as p
from collections import Counter
D=pickle.load(open('formF.pkl','rb'))['A']
inv={g:i for i,g in enumerate(p.P)}
F,ms=max(D.items(),key=lambda t:len(t[1]))
print('4-flat lines',sum(1 for i in range(112) if p.PL[i] in F),' directions served',len(ms))
H=[]
for gm in ms:
    perp=[p.P[i] for i in range(112) if not gm>>i&1]
    M=sympy.Matrix([list(p.LINES[i]) for i in perp]); ns=M.nullspace(); assert len(ns)==1
    h=ns[0]; h=h*sympy.ilcm(*[x.q for x in h]); H.append([int(x) for x in h])
Hm=sympy.Matrix(H)
E8=[list(l) for l in p.LINES]
c3=Counter(); cE=Counter()
for a,b in itertools.combinations(range(len(H)),2):
    third=sum(1 for c in range(len(H)) if c not in (a,b) and sympy.Matrix([H[a],H[b],H[c]]).rank()==2)
    e8=sum(1 for l in E8 if sympy.Matrix([H[a],H[b],l]).rank()==2)
    c3[third]+=1; cE[e8]+=1
print('third directions in plane:',dict(c3),' E8 lines in plane:',dict(cE))
