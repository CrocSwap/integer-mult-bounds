"""[C] exact replays (dyadic, finals checked): R, H (halving increments), E; R + H >= E must hold.
(a) 2-clique Hadamard decoder, n=3, Q={001,111} (odd pair): rows w=(1,+-1), u=(1/2,+-1/2); loads at A=<110>, climb 1 each.
(b) integral per-port witness on the same Q (H=0)."""
from fractions import Fraction as Fr
from z4pot import z4len, tens_pre, span, dimS, dot, compress
def replay(n, Q, prog):
    k=len(Q); d=2*k; N=n*d; V=frozenset(range(1<<n)); perp=lambda q: frozenset(v for v in range(1<<n) if not dot(v,q))
    e=lambda i:[Fr(int(t==i)) for t in range(d)]
    ch={}; val={}; pub={}
    for p in range(k):
        ch['X%d'%p]=span([Q[p]]); val['X%d'%p]=e(p); pub['X%d'%p]=V
        ch['Y%d'%p]=frozenset([0]); val['Y%d'%p]=e(k+p); pub['Y%d'%p]=perp(Q[p])
    S0=[g for r in ch for g in tens_pre(ch[r],val[r],n)]; Sg=list(S0); lam=z4len(Sg,N); R=H=pc=HP=0; psi=lam-z4len([[2*x%4 for x in g] for g in Sg],N)
    for op in prog:
        if op[0]=='add':
            a,b,l=op[1],op[2],Fr(op[3]); assert ch[a]==ch[b]
            val[a]=[x+l*y for x,y in zip(val[a],val[b])]; kind='halv' if l.denominator==2 else 'add'
        elif op[0]=='init': ch[op[1]]=op[2]; val[op[1]]=[Fr(0)]*d; kind='init'
        else:
            r,D=op[1],op[2]; assert ch[r]<=D or D<=ch[r]
            c=max(0,dimS(D)-dimS(ch[r]))
            if r in pub: assert ch[r]<=D; pc+=c
            else: R+=c
            ch[r]=D; kind='mv'
        for r in ch:
            assert all((2*x).denominator==1 for x in val[r])
            for p in range(k): assert val[r][p]==0 or Q[p] in ch[r]
        Sg=compress(Sg+[g for r in ch for g in tens_pre(ch[r],val[r],n)],N); ln=z4len(Sg,N)
        ps=ln-z4len([[2*x%4 for x in g] for g in Sg],N)
        if kind=='halv': H+=ln-lam; HP+=ps-psi
        lam=ln; psi=ps
    for p in range(k):
        assert ch['X%d'%p]==V and ch['Y%d'%p]==perp(Q[p]) and val['Y%d'%p]==e(k+p)
    M=[[val['X%d'%t][k+s] for s in range(k)] for t in range(k)]
    assert all(val['X%d'%t][p]==(p==t) for t in range(k) for p in range(k))
    T=[g for r in pub for g in tens_pre(ch[r],val[r],n)]
    E=z4len(S0+T,N)-z4len(S0,N)-pc
    return dict(R=R,H_lam=H,H_psi=HP,E=E,M=[[str(x) for x in r] for r in M])
n=3; Q=[1,7]; A=span([6]); B=span([6,1]); V=frozenset(range(8)); perp=lambda q: frozenset(v for v in range(8) if not dot(v,q))
P=[('mv','Y0',A),('mv','Y1',A)]
for kk,sg in ((0,1),(1,-1)):
    O='O%d'%kk
    P+=[('init',O,A),('add',O,'Y0',Fr(1,2)),('add',O,'Y1',Fr(sg,2)),('mv',O,B)]
P+=[('mv','X0',B),('mv','X1',B)]
P+=[('add','X0','O0',1),('add','X0','O1',1),('add','X1','O0',1),('add','X1','O1',-1)]
P+=[('mv','X0',V),('mv','X1',V),('mv','Y0',perp(1)),('mv','Y1',perp(7))]
print('(a) Hadamard 2-clique decoder: R,H,E,M =',replay(n,Q,P))
W=[]
for p,q in enumerate(Q):
    W+=[('mv','Y%d'%p,perp(q)),('init','P%d'%p,perp(q)),('add','P%d'%p,'Y%d'%p,1),('mv','P%d'%p,V),('mv','X%d'%p,V),('add','X%d'%p,'P%d'%p,1)]
print('(b) integral witness: R,H,E,M =',replay(n,Q,W))
# (c) same decoder but halving done at the TOP (X += O/2 at B, O integral)
P2=[('mv','Y0',A),('mv','Y1',A)]
for kk,sg in ((0,1),(1,-1)):
    O='O%d'%kk
    P2+=[('init',O,A),('add',O,'Y0',1),('add',O,'Y1',sg),('mv',O,B)]
P2+=[('mv','X0',B),('mv','X1',B)]
P2+=[('add','X0','O0',Fr(1,2)),('add','X0','O1',Fr(1,2)),('add','X1','O0',Fr(1,2)),('add','X1','O1',Fr(-1,2))]
P2+=[('mv','X0',V),('mv','X1',V),('mv','Y0',perp(1)),('mv','Y1',perp(7))]
print('(c) halving at the top: R,H,E,M =',replay(n,Q,P2))
