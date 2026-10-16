"""Z^9 / L for L = integer span of a pattern set (vector = cap one-hot (8,16,32,48) ++ counts of widths 4,5,7,8,9)."""
CAPS=[8,16,32,48];W=[4,5,7,8,9]
def vec(c,p):return [1 if c==k else 0 for k in CAPS]+list(p)
def hnf(rows):
    A=[list(r) for r in rows];n=len(A[0]);H=[];col=0
    for col in range(n):
        piv=[r for r in A if r[col]!=0]
        if not piv:continue
        rest=[r for r in A if r[col]==0]
        while len(piv)>1:
            piv.sort(key=lambda r:abs(r[col]))
            a=piv[0];new=[a]
            for r in piv[1:]:
                q=r[col]//a[col];r2=[x-q*y for x,y in zip(r,a)]
                (new if r2[col]!=0 else rest).append(r2)
            piv=new
        a=piv[0]
        if a[col]<0:a=[-x for x in a]
        H.append((col,a));A=rest
    assert all(all(x==0 for x in r) for r in A)
    return H
def reducer(H):
    def red(v):
        v=list(v)
        for col,a in H:
            q=v[col]//a[col]
            if q:v=[x-q*y for x,y in zip(v,a)]
        return tuple(v)
    return red
