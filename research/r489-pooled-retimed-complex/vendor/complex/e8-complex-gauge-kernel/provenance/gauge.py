from kern import *
import random
def span(F):
    s={0}
    for b in F:s|={x^b for x in s}
    return frozenset(s)
def perp(x):return basis([z for z in range(1,512) if not (x&z).bit_count()%2])
def prep(w):
    col,first=setup(w);R=len(col);P=w['ports']
    A,B=w['A'],w['B'];FB={}
    for seq in (A,B):
        for e in seq:
            for r in ([e[1]]+([e[2]] if e[0]=='add' else [])):
                if v<=r<2*v and e[-1] is not None:FB.setdefault(r-v,basis(e[-1]))
    cap={t:span(FB[t]) if t in FB else span(perp(P[t])) for t in range(v)}
    cands={}
    for h in range(R):
        S=list(col[h]);inter=set(span(first[h]))
        for t in S:inter&=cap[t]
        # candidate subspaces of first[h] inside inter
        cs=[]
        for E in subspaces(first[h]):
            if span(E)<=inter:cs.append(E)
        cands[h]=sorted(cs,key=lambda E:-len(E))
    return col,first,cap,cands,P
def nested(sa,sb):return sa<=sb or sb<=sa
def greedy(col,cands,seed=0,order=None):
    R=len(col);rnd=random.Random(seed)
    chain={t:[] for t in range(v)}  # list of span-sets
    E_of={}
    hs=list(range(R))
    if order is None:
        hs.sort(key=lambda h:(len(col[h]),rnd.random()))
    else:hs=order
    eps=0
    for h in hs:
        for E in cands[h]:
            sE=span(E)
            if all(all(nested(sE,c) for c in chain[t]) for t in col[h]):
                E_of[h]=E;eps+=len(E)
                for t in col[h]:chain[t].append(sE)
                break
    return E_of,eps
if __name__=='__main__':
    w=load();col,first,cap,cands,P=prep(w)
    print('cands sizes',Counter(len(c) for c in cands.values()).most_common(6))
    print('upper (sum of max cand rank)',sum(len(c[0]) if c else 0 for c in cands.values()))
    best=0
    for seed in range(30):
        E_of,eps=greedy(col,cands,seed)
        if eps>best:best=eps;print(seed,eps,len(E_of),Counter(len(E) for E in E_of.values()))
