"""ORBITLP verify_dual.py: exact re-check of a saved symmetrized LP dual against ALL rectangle profiles (prof.npy from rect.c).
Checks: y >= 0; for every profile sum_c y_c*coef_c <= price (exact, integers); prints the certified bound."""
import numpy as np, json, sys, math
from fractions import Fraction as Fr
d=json.load(open(sys.argv[1])); y=[Fr(s) for s in d['y']]; cols=d['cols']; b=d['b']
assert all(v>=0 for v in y)
D=1
for v in y: D=D*v.denominator//math.gcd(D,v.denominator)
yi=np.array([int(v*D) for v in y],dtype=object)
P=np.load('prof.npy')
lhs=np.zeros(len(P),dtype=object)
for c,v in zip(cols,yi):
    if v: lhs=lhs+P[:,c].astype(object)*v
rhs=P[:,23].astype(object)*D
viol=int((lhs>rhs).sum())
bound=sum(v*bb for v,bb in zip(y,b))
print(sys.argv[1],'profiles',len(P),'violations',viol,'certified LP lower bound',bound,'=',float(bound))
