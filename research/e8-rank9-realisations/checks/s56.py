# 56-problem: rows u -> points P_u, columns s -> lines l_s in a projective plane, P_u on l_s whenever u ⊥ s (u,s in Nbar(f1)).
# Abstraction (sound): equality vars f[u,u'] (same point), e[s,s'] (same line); transitivity; incidence axiom:
#   distinct points u,u' with two common lines s,s' (both in Γ(u)∩Γ(u')) => e[s,s']; dually.
# Negated conclusion: no point-class A0 meeting Γ(s) for every column s, and no line-class B0 meeting Γ(u) for every row u.
import sys, itertools, os as _o; sys.path.insert(0,_o.path.dirname(_o.path.abspath(__file__)))
from e8lib import *
f1=int(sys.argv[2]) if len(sys.argv)>2 else 0
import os
LU=UNITS[os.environ.get('UNIT','E8')]
assert f1 in LU
S=[u for u in sorted(LU) if G[u][f1]!=0 and u!=f1]; n=len(S)
Gam=[[j for j in range(n) if S[j] in O[S[i]]] for i in range(n)]
nv=[0]; cl=[]
def new(): nv[0]+=1; return nv[0]
def eqvars():
    V={}
    for i in range(n):
        for j in range(i+1,n): V[(i,j)]=V[(j,i)]=new()
    for i,j,k in itertools.combinations(range(n),3):
        a,b,c=V[(i,j)],V[(j,k)],V[(i,k)]
        cl.extend([[-a,-b,c],[-a,-c,b],[-b,-c,a]])
    return V
Fp=eqvars(); El=eqvars()
for P,Q in ((Fp,El),(El,Fp)):
    for i in range(n):
        for j in range(i+1,n):
            com=sorted(set(Gam[i])&set(Gam[j]))
            for s,t in itertools.combinations(com,2): cl.append([P[(i,j)],Q[(s,t)]])
def negdom(P):
    # for every row-class representative i: exists column s with no Γ(s)-row equal to i (and i not in Γ(s))
    for i in range(n):
        opts=[]
        for s in range(n):
            if i in Gam[s]: continue
            w=new(); opts.append(w)
            for u in Gam[s]: cl.append([-w,-P[(i,u)]])
        cl.append(opts)
import os
if os.environ.get("SIDE","both") in ("both","rows"): negdom(Fp)
if os.environ.get("SIDE","both") in ("both","cols"): negdom(El)
with open(sys.argv[1],'w') as fh:
    fh.write(f'p cnf {nv[0]} {len(cl)}\n')
    for c in cl: fh.write(' '.join(map(str,c))+' 0\n')
print(nv[0],len(cl))
