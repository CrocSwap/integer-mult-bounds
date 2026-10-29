# independent check of the [7,7,1] cell: S = span(C rows p_g (8), q, delta_r) as explicit 120-vectors; V8 = sum_phi {v in S : v|O_phi = 0}; dim V8 should be 3 (=T)
import pickle, sys
from fractions import Fraction as Fr
from lib import *
from cell771 import rref, nullspace, ip8, Opar, C
pairs=pickle.load(open('pairs771.pkl','rb'))
r0=0
# generators of S as 120-vectors: p_{e_i} for coordinate unit vectors g=e_i (doubled coords /4 handled by ip8)
def pg(g): return [sum(Fr(x)*Fr(y) for x,y in zip(g,lines[t]))/4 for t in range(n)]
gens0=[pg([Fr(int(i==j)) for j in range(8)]) for i in range(8)]
dr=[Fr(int(t==r0)) for t in range(n)]
def span_dim(vs): return len(rref(vs,n)[0])
c0,K=int(sys.argv[1]),int(sys.argv[2]); out=[]
for i,(Ma,Mb) in enumerate(pairs):
    if i%K!=c0: continue
    q=[ip8(lines[r0],lines[t]) if Ma>>t&1 else Fr(0) for t in range(n)]
    S=gens0+[q,dr]          # 10 generators
    V8=[]
    for phi in range(1,512):
        O=Opar[phi]
        # coefficients x in K^10 with sum x_k S_k vanishing on O
        rows=[[S[k][t] for k in range(10)] for t in O]
        for x in nullspace(rows,10):
            V8.append([sum(x[k]*S[k][t] for k in range(10)) for t in range(n)])
    print(i,'dim V8',span_dim(V8),flush=True)
