# LOWD residual test: lossless frame-row dual terms j (x_j = e_i, i in I = [8]\Ic) with outside columns of compatible non-frame class z_j,
# eta_j in span(e_i, e_Ic), eta_j[i] != 0, pairwise eta_j - eta_j' ⟂ c_t for t in O_zj ∩ O_zj'.  Find all sets of >= KMIN such terms.
import sys, json, itertools, pickle, numpy as np
from fractions import Fraction as Fr
import sympy as sp
from lib import bounded_integer_rank
D=json.load(open('data.json')); LAB=D['LAB']; FC=np.array(D['FC'],dtype=np.int64); v=112
Lf=np.array(D['L']); F0=np.array(D['F0'])
# Omega: Bd[t][s] = LAB[t]^T G LAB[s] over F2 (Bd = 1 iff t = s or t orthogonal to s); solve the 81 unknowns of G exactly
def _solve_G():
    rows=[]
    for t in range(v):
        for s_ in range(v):
            b=1 if (t==s_ or abs(Lf[t]@Lf[s_])<1e-9) else 0
            eq=0
            for a in range(9):
                for c in range(9):
                    if (LAB[t]>>a)&1 and (LAB[s_]>>c)&1: eq|=1<<(9*a+c)
            rows.append(eq|(b<<81))
    piv={}
    for r in rows:
        for p,pr in piv.items():
            if (r>>p)&1: r^=pr
        low=[i for i in range(81) if (r>>i)&1]
        if not low:
            assert not (r>>81)&1, 'inconsistent'; continue
        p=low[0]
        for q in list(piv):
            if (piv[q]>>p)&1: piv[q]^=r
        piv[p]=r
    assert len(piv)==81, 'G not determined'
    G=np.zeros((9,9),dtype=np.int64)
    for p,pr in piv.items(): G[p//9,p%9]=(pr>>81)&1
    return G
G=_solve_G()
par=lambda x: bin(x).count('1')&1
O={z:[t for t in range(v) if par(z&LAB[t])] for z in range(1,512)}
framez=set()   # classes of the 8 frame roots: O_z = lines orthogonal to f_i
for f in F0:
    S_=set(t for t in range(v) if abs(Lf[t]@f)<1e-9)
    framez|={z for z in range(1,512) if set(O[z])==S_}
assert len(framez)==8
def rk2(rows):
    B=[]
    for r in rows:
        for b in B: r=min(r,r^b)
        if r: B.append(r)
    return len(B)
def bits(vec): return sum(int(b)<<i for i,b in enumerate(vec))
# solve G x = z (mod 2)
import itertools
Ginv={}
for x in range(512):
    xv=np.array([(x>>i)&1 for i in range(9)]); z=bits(G@xv%2); Ginv[z]=x
assert len(Ginv)==512
off=[[t for t in range(v) if FC[t][i]!=0] for i in range(8)]
compat={i:[z for z in range(1,512) if z not in framez and rk2([LAB[t] for t in off[i]]+[Ginv[z]])==8] for i in range(8)}
print('compatible nonframe classes per i:',[len(compat[i]) for i in range(8)],flush=True)
# sanity: compat <=> rank Bd[Off f_i, L\O_z] == 7
Bd=lambda t,s: par(bits(G@np.array([(LAB[s]>>k)&1 for k in range(9)])%2)&LAB[t])
# nullspace of FC[Theta] for every pair z<z2 (exact, sympy only when needed)
null={}
def nullspace(Th):
    if not Th: return 'ALL'
    M=sp.Matrix(FC[Th].tolist()); ns=M.nullspace()
    return [np.array([int(sp.nsimplify(c)*sp.ilcm(*[sp.fraction(sp.nsimplify(cc))[1] for cc in n])) for c in n],dtype=np.int64) for n in ns]
cand=set(z for i in range(8) for z in compat[i])
cl=sorted(cand)
for a in range(len(cl)):
    z=cl[a]; Oz=set(O[z])
    for b in range(a+1,len(cl)):
        z2=cl[b]; Th=[t for t in O[z2] if t in Oz]
        if Th and bounded_integer_rank(FC[Th])==8: continue
        null[(z,z2)]=nullspace(Th)
print('pairs with nontrivial Theta-perp:',len(null),flush=True)
pickle.dump((compat,null),open('null.pkl','wb'))
