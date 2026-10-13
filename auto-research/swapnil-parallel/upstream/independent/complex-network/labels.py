"""Exact binary label checks over F2^h (dot product) for a Side circuit.
labels: input -> <t_T>; node whose triples share one common pair and >=2 triples
-> span of its indicators (pair-star label); otherwise coordinate space of covered points."""
import sys
from side import Side

def echelon(vs):
    b={}
    for x in vs:
        for p,y in b.items():
            if x&p: x^=y
        if not x: continue
        p=x&-x
        for q in list(b):
            if b[q]&p: b[q]^=x
        b[p]=x
    return b
def red(b,x):
    for p,y in b.items():
        if x&p: x^=y
    return x
def dot(a,b): return bin(a&b).count('1')&1
def perp_in(V,U):
    """basis of V ∩ U^perp (V,U lists of basis vectors)"""
    k=len(U); rows=[]
    for i,v in enumerate(V):
        rows.append((sum(dot(v,u)<<j for j,u in enumerate(U)), 1<<i))
    out=[];piv=[]
    # gaussian elimination on first component
    rs=rows
    for col in range(k):
        bit=1<<col
        idx=next((i for i,(a,_) in enumerate(rs) if a&bit),None)
        if idx is None: continue
        pa,pb=rs.pop(idx)
        rs=[(a^pa,b^pb) if a&bit else (a,b) for a,b in rs]
    for a,b in rs:
        assert a==0
        x=0
        for i,v in enumerate(V):
            if b>>i&1: x^=v
        out.append(x)
    return out
def nondeg(B):
    g=[sum(dot(a,b)<<j for j,b in enumerate(B)) for a in B]
    return len(echelon(g))==len(B)
def ok_res(R):
    return (not R) or (nondeg(R) and any(bin(x).count('1')&1 for x in R))

class Checker:
    def __init__(s,c):
        s.c=c; s.h=c.h; s.full=(1<<c.h)-1; s.cache={}; s.lab={}
    def tvec(s,i): return sum(1<<p for p in s.c.triples[i])
    def label(s,n):
        if n in s.lab: return s.lab[n]
        c=s.c; sp=c.sup[n]; idx=[]
        while sp:
            lo=sp&-sp; idx.append(lo.bit_length()-1); sp^=lo
        if len(idx)==1: B=[s.tvec(idx[0])]
        else:
            common=set(c.triples[idx[0]])
            for i in idx[1:]: common&=set(c.triples[i])
            if len(common)>=2: B=list(echelon([s.tvec(i) for i in idx]).values()); assert len(B)==len(idx)
            else: X=c.cover(n); B=[1<<p for p in range(s.h) if X>>p&1]
        B=sorted(echelon(B).values()); assert nondeg(B); s.lab[n]=B; return B
    def edge(s,U,V):
        key=(tuple(U),tuple(V))
        if key not in s.cache:
            bV=echelon(V); good=all(red(bV,u)==0 for u in U)
            s.cache[key]=good and ok_res(perp_in(V,U))
        return s.cache[key]
    def run(s):
        c=s.c; bad=0; n_e=0
        F=[1<<p for p in range(s.h)]
        for n in c.active:
            L=s.label(n)
            assert ok_res(L)                      # entry residual from the early frame
            assert ok_res(perp_in(F,L))           # exit residual to the late frame
            if c.args[n]:
                for a in c.args[n]:
                    n_e+=1
                    if not s.edge(s.label(a),L): bad+=1
        for S,n,_ in c.pieces:
            tS=sum(1<<p for p in S)
            TS=[x for x in perp_in(F,[tS])]
            n_e+=1
            if not s.edge(s.label(n),TS): bad+=1
        return dict(edges=n_e,bad=bad,labels=len(s.lab))

if __name__=='__main__':
    h=int(sys.argv[1])
    c=Side(h)
    print(c.stats(),flush=True)
    print(Checker(c).run())
