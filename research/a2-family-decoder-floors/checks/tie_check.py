# Exact check of the tie decoders (HUNT-A2): a square (9-term) decoder of an A2-family member at a special parameter point, over Q.
#   * member: rows a_u = (r_u,0) off X, a_{u_i} = (r_i + g_i, 1); columns b_s = (r_s, z_s)  (a2lib.build; theta = (al2,be2,al3,be3), g_2 = al2 r_1 + be2 r_2, g_3 = al3 r_1 + be3 r_2, zX = z on X)
#   * decoder: row normals x_j (data/tie_<UNIT>.json), column normals y_j = dual basis; P = A X, Q = B Y, so  sum_j P[u,j] Q[s,j] = M[u,s] exactly.
# Independent of a2lib.evaluate: matrix inverse, products, the iff pattern (from raw root coordinates), the dense B (B[t,s] = 1 iff t = s or r_t . r_s = 0) and the F2 ranks are recomputed here.
# usage: UNIT=P112|E8 python tie_check.py
import json, os, sys
from fractions import Fraction as Fr
from a2lib import UNIT, L, v, X, build
D=json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','data','tie_%s.json'%UNIT)))
assert D['unit']==UNIT
th=tuple(Fr(x) for x in D['theta']); zX=tuple(Fr(x) for x in D['zX'])
A,B=build(th,zX)
xs=[[Fr(x) for x in r] for r in D['xs']]
def mat_inv(Mx):
    n=len(Mx); W=[list(r)+[Fr(int(i==j)) for j in range(n)] for i,r in enumerate(Mx)]
    for c in range(n):
        p=next(i for i in range(c,n) if W[i][c]!=0); W[c],W[p]=W[p],W[c]
        pv=W[c][c]; W[c]=[x/pv for x in W[c]]
        for i in range(n):
            if i!=c and W[i][c]!=0:
                f=W[i][c]; W[i]=[a-f*b for a,b in zip(W[i],W[c])]
    return [r[n:] for r in W]
Xm=[[xs[j][k] for j in range(9)] for k in range(9)]          # columns are the x_j
Xi=mat_inv(Xm)                                                # X^{-1}
Ym=[[Xi[j][k] for j in range(9)] for k in range(9)]           # Y = X^{-T}: column j of Y is row j of X^{-1}
P=[[sum(A[u][k]*Xm[k][j] for k in range(9)) for j in range(9)] for u in range(v)]
Q=[[sum(B[s][k]*Ym[k][j] for k in range(9)) for j in range(9)] for s in range(v)]
dot=lambda a,b: sum(x*y for x,y in zip(a,b))
M=[[dot(A[u],B[s]) for s in range(v)] for u in range(v)]
assert all(sum(P[u][j]*Q[s][j] for j in range(9))==M[u][s] for u in range(v) for s in range(v))
print('PASS exact: P Q^T = M over Q (9 terms, X invertible)')
# iff pattern from raw integer coordinates (2*root coordinates are integers)
Ri=[[int(2*x) for x in r] for r in L]
G=[[sum(a*b for a,b in zip(Ri[i],Ri[j])) for j in range(v)] for i in range(v)]
assert all((M[i][j]==0)==(G[i][j]==0 and i!=j) for i in range(v) for j in range(v))
print('PASS iff pattern: M[i][j]=0 exactly on orthogonal pairs i!=j, nonzero diagonal (%s lines)'%v)
# rank M = 9: A, B have rank 9 (X invertible, P=AX has rank = rank A)
def rank(rows):
    W=[list(r) for r in rows]; r=0
    for c in range(len(W[0])):
        p=next((i for i in range(r,len(W)) if W[i][c]!=0),None)
        if p is None: continue
        W[r],W[p]=W[p],W[r]; pv=W[r][c]; W[r]=[x/pv for x in W[r]]
        for i in range(len(W)):
            if i!=r and W[i][c]!=0:
                f=W[i][c]; W[i]=[a-f*b for a,b in zip(W[i],W[r])]
        r+=1
    return r
assert rank(A)==9 and rank(B)==9
print('PASS rank M = 9 (A and B have exact rank 9)')
# dense B and F2 ranks
Bd=[sum(1<<s for s in range(v) if s==t or G[t][s]==0) for t in range(v)]
def rank_f2(rows):
    basis={}; r=0
    for x in rows:
        while x:
            h=x.bit_length()-1
            if h in basis: x^=basis[h]
            else: basis[h]=x; r+=1; break
    return r
costs=[]
for j in range(9):
    Rj=[u for u in range(v) if P[u][j]!=0]; Aj=[s for s in range(v) if Q[s][j]!=0]; mask=sum(1<<s for s in Aj)
    costs.append(rank_f2([Bd[u]&mask for u in Rj]) if Rj and Aj else 0)
print('term costs',costs,'total',sum(costs))
assert costs==D['recorded_costs'] and sum(costs)==D['recorded_cost']
EXP={'P112':64,'E8':72}[UNIT]
assert sum(costs)==EXP
print('PASS %s tie decoder: exact cost %d (= the floor proved in this package)'%(UNIT,EXP))
