# row 19 [7^5,4], d=4: if E_S=Q then 10 distinct roots r_ab in Q u Roots(Q), all in the 4-dim h(R). max #lines of Q u Roots(Q) in a 4-dim subspace?
import sys,pickle,itertools; sys.path.insert(0,'../CARRIER')
from lib import lines
import numpy as np, sympy
Q2r=pickle.load(open('Q2r.pkl','rb'))
r0Q=[Q for Q,v in Q2r.items() if 0 in v]
print('Qs of r0',len(r0Q))
best=0
for Q in r0Q:
    X=[t for t in range(120) if Q>>t&1]+sorted(Q2r[Q]); V=np.array([lines[t] for t in X])
    m=0
    for B4 in itertools.combinations(range(12),4):
        Bm=V[list(B4)]
        if np.linalg.matrix_rank(Bm)<4: continue
        cnt=sum(1 for i in range(12) if np.linalg.matrix_rank(np.vstack([Bm,V[i]]))==4)
        m=max(m,cnt)
    # exact check of the maximiser rank via sympy on max subset size: also rank of whole set
    best=max(best,m)
print('max lines of Q u Roots(Q) in a 4-dim subspace:',best,'(need >=10 for row 19)')
print('rank of Q (real) for first Q:',sympy.Matrix([lines[t] for t in range(120) if r0Q[0]>>t&1]).rank(),' Roots(Q) rank:',sympy.Matrix([lines[t] for t in sorted(Q2r[r0Q[0]])]).rank())
