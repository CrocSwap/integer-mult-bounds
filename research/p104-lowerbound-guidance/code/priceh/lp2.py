import sys, numpy as np
from scipy.optimize import linprog
h=int(sys.argv[1]); L=int(sys.argv[2]); beta=float(sys.argv[3])
n=h+1
sets=[S for S in range(1<<n) if not (S&1)]
pairs=[(i,j) for i in range(n) for j in range(i+1,n)]
sep=np.array([1.0 if (((S>>1)&1)==((S>>h)&1) and ((S>>0)&1)==((S>>(h-1))&1) and ((S>>1)&1)!=((S>>0)&1)) else 0.0 for S in sets])
A=np.array([[1.0 if ((S>>i)&1)!=((S>>j)&1) else 0.0 for S in sets] for (i,j) in pairs])
b=np.array([min(L,j-i)+beta for (i,j) in pairs],float)
r=linprog(np.zeros(len(sets)),A_ub=-sep.reshape(1,-1),b_ub=[-(1+beta)/2],A_eq=A,b_eq=b,bounds=[(0,None)]*len(sets),method='highs-ds')
print(r.status)
for S,w in zip(sets,r.x):
    if w>1e-9: print(w, ''.join('X' if (S>>i)&1 else '.' for i in range(n)), 'SEP' if sep[sets.index(S)] else '')
