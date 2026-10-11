# Lemma (two-hyperplane): E7 roots are a spherical 4-design => no two hyperplanes of t^perp contain all 63 lines.
import os; os.environ['E8COORD']='ham'
import numpy as np, itertools
from fractions import Fraction as Fr
import e8lib as E
L=np.array(E.LINES,dtype=np.int64); V=120
t=0
P=[s for s in range(V) if E.G[t][s]==0]; assert len(P)==63
X=L[P].astype(object)
# exact 4th-moment tensor check: sum_r (r.u)^2 (r.v)^2 == c*(|u|^2|v|^2+2(u.v)^2) for u,v in t^perp, on a basis-pair grid
# use exact integers over random integer u,v in t^perp (project via combos of roots)
rng=np.random.default_rng(1)
def rand_in_perp():
    c=rng.integers(-3,4,size=63); return (c[:,None]*L[P]).sum(0)
def ip(a,b): return int(np.dot(a,b))   # unscaled coords; ratio test only
vals=[]
for _ in range(200):
    u=rand_in_perp(); v=rand_in_perp()
    lhs=sum(ip(r,u)**2*ip(r,v)**2 for r in L[P])
    rhs=ip(u,u)*ip(v,v)+2*ip(u,v)**2
    if rhs: vals.append(Fr(lhs,rhs))
print('4-design ratio constant over 200 random pairs:',len(set(vals))==1, vals[0])
# 2nd moment: sum (r.u)(r.v) = c2 (u.v)
v2=set()
for _ in range(100):
    u=rand_in_perp(); v=rand_in_perp()
    a=sum(ip(r,u)*ip(r,v) for r in L[P]); b=ip(u,v)
    if b: v2.add(Fr(a,b))
print('2-design constant:',v2)
