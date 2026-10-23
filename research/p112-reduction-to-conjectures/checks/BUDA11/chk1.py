# BUDA11 impl 1 (TWINSWAP lib coords: c_t = FC rows, frame f_i = e_i, labels LAB, Bd from Gram).
import sys,os; H=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,os.path.join(H,'../TWINSWAP')); os.chdir(os.path.join(H,'../TWINSWAP'))
from lib import *
import sympy as sp
def rk(rows): return sp.Matrix(rows).rank() if rows else 0
def w(S): return f2rank([LAB[s] for s in S])
def off(x): return [s for s in range(n) if sum(C[s][i]*x[i] for i in range(8))!=0]
assert len(set(LAB))==n and all(sum(1 for v in C[t] if v)==4 for t in range(n))
# (A) e_t not in col C
assert all(rk([C[s]+[1 if s==t else 0] for s in range(n)])==9 for t in range(n)); print('A ok')
# (B) q=C'y+y2 e_t' vanishing on Z_t: ranks
for t in range(n):
    Z=[s for s in range(n) if Bd[t][s]]
    assert rk([C[s] for s in Z])==8 and rk([C[s] for s in Z if s!=t])==7
    for tp in Z:
        if tp!=t: assert rk([C[s] for s in Z if s!=tp])==8
    h=[round(G[s][t])-(2 if s==t else 0) for s in range(n)]   # N0[:,t]-e_t
    assert w([s for s in range(n) if h[s]!=0])==8
print('B ok')
# (C) all x with w(Off(x)\{t}) <= 8: kernel K_{H,t} for each hyperplane H=ker(phi)
viol=0; seen=Counter() if False else {}
from collections import Counter; kinds=Counter()
for t in range(n):
    for phi in range(1,512):
        O=[s for s in range(n) if s!=t and bin(phi&LAB[s]).count('1')%2]
        K=sp.Matrix([C[s] for s in O]).nullspace() if O else [sp.eye(8)[:,i] for i in range(8)]
        if not K: kinds['0']+=1; continue
        Km=sp.Matrix.hstack(*K)
        okc = len(K)==1 and sp.Matrix.hstack(Km,sp.Matrix(C[t])).rank()==1
        okf = len(K)==1 and sum(1 for v in K[0] if v!=0)==1
        if okc: kinds['c_t']+=1
        elif okf: kinds['frame']+=1
        else: viol+=1; print('VIOL',t,phi,len(K))
print('C kinds',dict(kinds),'violations',viol)
# (D) frame/frame terms: cost >= 8 when both weights 8
mn=99; ex7=0
for t in range(n):
    Rs=[]
    for i in range(8):
        Of=set(off([1 if k==i else 0 for k in range(8)]))
        for R in (sorted(Of-{t}),sorted(Of|{t})):
            if w(R)==8: Rs.append(R)
    for R in Rs:
        for A in Rs: mn=min(mn,bdrank(R,A))
    # control: frame row vs root column Off(c_t)\{t} can be lossless (cost 7)
    A=[s for s in off(C[t]) if s!=t]
    ex7+=sum(1 for R in Rs if bdrank(R,A)==7)
print('D min frame/frame cost',mn,'| control: #(frame row, root col) pairs with cost 7:',ex7)
