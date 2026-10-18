# Is the order-2 diagonal Q_t of an immovable line in the F2-span of the solvability quadrics (as polynomials)?
import sys, json, numpy as np
import os; PKG=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PKG+'/lib'); sys.path.insert(0, PKG+'/scripts')
from kit import *; from phi import classify; from jet2 import *
def polyvec(M):
    d=M.shape[0]; out=[]
    for i in range(d):
        for j in range(i,d):
            out.append(int(M[i,i]) if i==j else int(M[i,j]^M[j,i]))
    return int(''.join(map(str,out)),2) if out else 0
def inspan(x, vecs):
    piv=[]
    for r in vecs:
        for p in piv: r=min(r,r^p)
        if r: piv.append(r); piv.sort(reverse=True)
    for p in piv: x=min(x,x^p)
    return x==0
for i in range(3):
    P,Q=json.load(open(PKG+'/data/jf%d.json'%i)); v=len(P); R,A,free=setup(P,Q); w,H=classify(P,Q)
    an=analyse(P,Q,free,H); E=an['E']
    deps=[polyvec(quad_matrix(an,[E[k] for k in range(len(E)) if z>>k&1])) for z in an['deps']]
    for t,c in an['imm'].items():
        q=polyvec(quad_matrix(an,[(t,t)]+[E[k] for k in range(len(E)) if c>>k&1]))
        print('jf%d line %d: Q_t identically 0: %s; Q_t in span of solvability quadrics: %s'%(i,t,q==0,inspan(q,deps)))
