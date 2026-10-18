# independent E8 geometry (audit). roots in standard coords (x2 to stay integral)
import itertools, numpy as np
def e8_lines():
    R=[]
    for i,j in itertools.combinations(range(8),2):
        for si in (1,-1):
            for sj in (1,-1):
                v=[0]*8; v[i]=2*si; v[j]=2*sj; R.append(tuple(v))
    for signs in itertools.product((1,-1),repeat=8):
        if signs.count(-1)%2==0: R.append(tuple(signs))
    assert len(R)==240
    L=[]
    for r in R:
        nz=[x for x in r if x][0]
        if nz>0: L.append(r)
    assert len(L)==120
    return np.array(L)  # norm 8 (= 2*4)
L=e8_lines(); G=L@L.T//4   # Gram with roots of norm 2
n=120
ORTH=(G==0)
def orth_masks(idx):
    m=len(idx); o=[0]*m
    for a in range(m):
        for b in range(m):
            if a!=b and G[idx[a],idx[b]]==0: o[a]|=1<<b
    return o
def all_orth_sets(idx):
    o=orth_masks(idx); m=len(idx); out=[]
    def rec(mm,cand,start):
        out.append(mm); c=cand>>start; i=start
        while c:
            if c&1: rec(mm|1<<i,cand&o[i],i+1)
            c>>=1;i+=1
    for i in range(m): rec(1<<i,o[i],i+1)
    return out,o
def maximal(sets,o,m):
    res=[]
    for c in sets:
        com=(1<<m)-1
        for i in range(m):
            if c>>i&1: com&=o[i]
        if com&~c==0: res.append(c)
    return res
def f2rank(rows):
    rows=[int(''.join(map(str,r)),2) for r in rows]; r=0
    while rows:
        p=max(rows)
        if p==0: break
        rows.remove(p); r+=1; hb=p.bit_length()-1
        rows=[x^p if x>>hb&1 else x for x in rows]
    return r
