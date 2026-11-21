"""E(M) = lam(S0+T) - lam(S0) - public climbs for toy finals (X_t: <q_t> -> V, x_t + M_t y ; Y_s: {0} -> q_s^perp, y_s)."""
from fractions import Fraction as Fr
from z4pot import z4len, tens_pre, span, dimS, dot
def E(n, Q, M):
    k=len(Q); d=2*k; V=frozenset(range(1<<n)); perp=lambda q: frozenset(v for v in range(1<<n) if not dot(v,q))
    e=lambda i:[Fr(int(t==i)) for t in range(d)]
    S0=[]; T=[]
    for t in range(k):
        S0+=tens_pre(span([Q[t]]),e(t),n)
        T+=tens_pre(V,[a+sum(M[t][s]*b for s,b in enumerate([e(k+s) for s in range(k)]) ) if False else 0 for a in [0]] and [e(t)[i]+sum(M[t][s]*e(k+s)[i] for s in range(k)) for i in range(d)],n)
        T+=tens_pre(perp(Q[t]),e(k+t),n)
    N=n*d; pc=k*(n-1)+k*(n-1)
    return z4len(S0+T,N)-z4len(S0,N)-pc
h=Fr(1,2)
for n,Q in [(3,[1,2]),(3,[1,2,4]),(4,[1,2,4,8]),(3,[1,7])]:
    k=len(Q); I=[[Fr(int(i==j)) for j in range(k)] for i in range(k)]
    print(n,Q,'E(I)=',E(n,Q,I))
    even=[(i,j) for i in range(k) for j in range(k) if i!=j and not dot(Q[i],Q[j])]
    if even:
        M=[r[:] for r in I]
        for (i,j) in even: M[i][j]=h
        print('   halves on all even cells: E=',E(n,Q,M))
        M=[r[:] for r in I]; i,j=even[0]; M[i][j]=h
        print('   one half on even cell',(i,j),': E=',E(n,Q,M))
        M=[r[:] for r in I]; i,j=even[0]; M[i][j]=Fr(1)
        print('   integral 1 on even cell: E=',E(n,Q,M))
import random
rng=random.Random(3); worst={}
for it in range(300):
    n=rng.choice([3,4]); odd=[v for v in range(1,1<<n) if dot(v,v)]
    Q=rng.sample(odd,rng.randint(2,min(5,len(odd)))); k=len(Q)
    M=[[Fr(int(i==j)) if (i==j or dot(Q[i],Q[j])) else Fr(rng.choice([0,1,-1,1,3]),rng.choice([1,2])) for j in range(k)] for i in range(k)]
    e=E(n,Q,M); key=(n,k); worst[key]=min(worst.get(key,99),e-k)
print('min E-|Q| by (n,|Q|):',worst)
