"""B-linear class: v_k(s)=c_s.y_k mod 4. Decoder <=> for all t: sum_k w_k(t) y_k = +-G c_t mod 4.
Pool Y (m x 8 over Z4). Enumerate per-port minimal supports, local search on cost."""
from ncore import *
import random
def chk_span():
    bad=0
    for t in range(n):
        O=[s for s in np.nonzero(Q[t])[0] if s!=t]
        M=Cb[O]; bad+= f2rank(np.vstack([M,Cb[t]]))!=f2rank(M)
    return bad
def sols(Y,t):
    """all w in Z4^m (as tuples) with w Y = +-G c_t mod 4; brute force over Z4-kernel."""
    m=Y.shape[0]; tgt=(G@C[t])%4
    out=[]
    for w in itertools.product(range(4),repeat=m):
        r=(np.array(w)@Y)%4
        if (r==tgt).all() or (r==(-tgt)%4).all(): out.append(w)
    return out
def minimal_supports(Y,t):
    S=set()
    for w in sols(Y,t):
        S.add(sum(1<<k for k in range(len(w)) if w[k]))
    S=sorted(S,key=lambda x:bin(x).count('1'))
    mins=[]
    for s in S:
        if not any((m_&s)==m_ for m_ in mins): mins.append(s)
    return mins
def Ssup(Y):
    return [np.nonzero((C@Y[k])%4)[0] for k in range(Y.shape[0])]
def price(D,S):
    if len(D)==0 or len(S)==0: return 0
    return f2rank(Q[np.ix_(D,S)])
def cost(Kt,Y,SS):
    m=Y.shape[0]; tot=0; pr=[]
    for k in range(m):
        D=[t for t in range(n) if Kt[t]>>k&1]
        p=price(D,SS[k]); pr.append(p); tot+=p
    return tot,pr
if __name__=='__main__':
    print('c_t in span(O_t minus t) failures:',chk_span())
