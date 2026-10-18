# exact check of the root-swap family (k=1 and k=2) + pair-coloop fact for root targets
import sys
from base import *
from fractions import Fraction as Fr
import itertools, sympy as sp
n=112; C=[[int(x) for x in row] for row in FC]
Ti=[list(map(int,l.split())) for l in open('targets.txt') if l.strip()]
# pair fact: for root targets (|Off|=53), rank(Off\{t,u})<=8 iff the coloop is in {t,u}
bad=0
for off in Ti:
    if len(off)!=53: continue
    col=[t for t in off if f2rank([LAB[u] for u in off if u!=t])<=8]; assert len(col)==1
    for t,u in itertools.combinations(off,2):
        if f2rank([LAB[x] for x in off if x not in (t,u)])<=8 and col[0] not in (t,u): bad+=1
print('root targets: pairs dropping rank without the coloop:',bad)
def check(J,roots):
    # columns: c^(l) l not in J ; p'_m = p_{r_m} - p_{r_m}(r_m) delta_{r_m} ; delta_{r_m}
    cols=[]; names=[]
    for l in range(8):
        if l not in J: cols.append([C[t][l] for t in range(n)]); names.append(('c',l))
    for r in roots:
        h=[sp.Integer(x) for x in C[r]]   # functional h = c_r (F0 coords): p_r(t)=<c_t,c_r>
        pr=[sum(C[t][i]*C[r][i] for i in range(8)) for t in range(n)]
        pp=pr[:]; pp[r]=0; cols.append(pp); names.append(('p',r))
        d=[0]*n; d[r]=1; cols.append(d); names.append(('d',r))
    P=sp.Matrix(n,len(cols),lambda t,k: cols[k][t]); Cm=sp.Matrix(C)
    # solve P Y = C exactly
    Y=sp.Matrix.zeros(len(cols),8)
    sol=P.gauss_jordan_solve(Cm)[0]; Y=sol.subs({s:0 for s in sol.free_symbols})
    assert P*Y==Cm
    cost=0; corr=0
    for k,(nm,col) in enumerate(zip(names,cols)):
        supp=[t for t in range(n) if col[t]!=0]; w=f2rank([LAB[t] for t in supp])
        y=list(Y.row(k)); nz=[i for i in range(8) if y[i]!=0]
        U=[LAB[t] for t in supp]
        eps= 1 if (len(nz)==1 and f2rank(U+[Z[nz[0]]])==w) else 0
        cost+=w; corr+=eps
        if nm[0]!='c': print('  col',nm,'weight',w,'y support',nz,'corrected',eps, 'full' if w==9 else '')
    print('J',J,'roots',roots,'eps-free',cost,'corrections',corr,'corrected cost',cost-corr)
# k=1
r1=[t for t in range(n) if C[t][0]!=0][0]; check([0],[r1])
# k=2: roots with supp∩J={j_m}
J=[0,1]
ra=[t for t in range(n) if C[t][0]!=0 and C[t][1]==0][0]; rb=[t for t in range(n) if C[t][1]!=0 and C[t][0]==0][0]
check(J,[ra,rb])
# general k: choose J with, for each j in J, a root whose F0-support meets J exactly in {j} (distinct roots); tried for k = 3 and the first feasible J for k = 4, 5
import itertools as _it
for k in (3,4,5):
    done=False
    for J in _it.combinations(range(8),k):
        rs=[]
        for m in J:
            cand=[t for t in range(n) if C[t][m]!=0 and all(C[t][j]==0 for j in J if j!=m) and t not in rs]
            if not cand: break
            rs.append(cand[0])
        else:
            check(list(J),rs); done=True; break
    if not done: print('no feasible J for k =',k)
