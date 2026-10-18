# symbolic duality products for a catalogue pickle (gen or zX-special), returns variable (dir_i,dir_j) pairs
import sympy as sp, pickle, collections, sys
from a2lib import *
cat=sys.argv[1]; D=pickle.load(open(cat,'rb')); out=D['out']; th0=D['th']; zX0=D['zX']
rd,cd,f=pickle.load(open(cat.replace('cat_','tab_'),'rb'))
al2,be2,al3,be3,z1,z2,z3=sp.symbols('al2 be2 al3 be3 z1 z2 z3')
a=al2; c=al3+be3
key=cat[4:-4]
if key=='gen': zsub=(z1,z2,z3)
else:
    ZA=pickle.load(open('zaff.pkl','rb'))[key]; zl=[z1,z2,z3]
    for k_,e_ in ZA.items(): zl[k_]=e_.subs({sp.Symbol('al2'):al2,sp.Symbol('be2'):be2,sp.Symbol('al3'):al3,sp.Symbol('be3'):be3})
    zsub=tuple(zl)
g=[[0]*8,[al2*x+be2*y for x,y in zip(r1,r2)],[al3*x+be3*y for x,y in zip(r1,r2)]]
zs=[None]*v
for s in range(v):
    for i in range(3):
        if Gm[X[i]][s]==0: zs[s]=-sum(sp.Rational(x)*y for x,y in zip(R[s],g[i])); break
for i in range(3): zs[X[i]]=zsub[i]
A=[[sp.Rational(x) for x in R[s]]+[0] for s in range(v)]
for i in range(3): A[X[i]]=[sp.Rational(x)+y for x,y in zip(R[X[i]],g[i])]+[1]
Bv=[[sp.Rational(x) for x in R[s]]+[zs[s]] for s in range(v)]
def norm(x):
    i=next(k for k in range(9) if x[k]!=0); return tuple(t/x[i] for t in x)
subs={al2:th0[0],be2:th0[1],al3:th0[2],be3:th0[3],z1:zX0[0],z2:zX0[1],z3:zX0[2]}
def symdir(rows):
    ns=sp.Matrix(rows).nullspace(); assert len(ns)==1; return ns[0]
rowsym={}; colsym={}
for co,(sz,nr,nc) in out.items():
    Os=bits(cls[co])
    if nr:
        d=symdir([A[t] for t in Os]); dn=norm([Fr(str(sp.nsimplify(x.subs(subs)))) for x in d]); rowsym.setdefault(rd.index(dn),d)
    if nc:
        e=symdir([Bv[t] for t in Os]); en=norm([Fr(str(sp.nsimplify(x.subs(subs)))) for x in e]); colsym.setdefault(cd.index(en),e)
free=set(); kinds=collections.Counter(); EX={}
for i,d in rowsym.items():
    for j,e in colsym.items():
        p=sp.factor(sp.simplify((d.T*e)[0])); EX[(i,j)]=p
        if p==0: kinds['zero']+=1
        elif p.free_symbols: free.add((i,j)); kinds['var']+=1; print(i,j,p)
        else: kinds['const']+=1
print(cat,len(rowsym),len(colsym),kinds)
pickle.dump(free,open(cat.replace('cat_','free_'),'wb')); pickle.dump(EX,open(cat.replace('cat_','expr_'),'wb'))
