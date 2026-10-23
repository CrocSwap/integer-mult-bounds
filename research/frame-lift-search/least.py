import frame_lift as L, gzip, json, sys
from collections import Counter
def least(word, ch, ngates):
    X=[None]*ngates
    pos=[[] for _ in range(ngates)]
    for r,c in enumerate(ch):
        for k,(kind,v) in enumerate(c):
            if kind=='g': pos[v].append((r,k))
    for g in range(ngates):
        m=1
        for r,k in pos[g]:
            k2=k-1
            while ch[r][k2][0]=='cap': k2-=1
            kind,x=ch[r][k2]; m|= X[x] if kind=='g' else x
        m=L.span_mask([x for x in range(512) if m>>x&1])
        for r,k in pos[g]:
            if ch[r][k+1][0]=='a': m=ch[r][k+1][1]
        X[g]=m
    return X,pos
if __name__=='__main__':
    w=json.load(gzip.open(sys.argv[1]))
    ch=L.chains(w); G,o=L.greatest(w)
    lo,pos=least(w,ch,len(o))
    assert all(a & ~b==0 for a,b in zip(lo,o)) and all(a&~b==0 for a,b in zip(o,G))
    print('gap dims', Counter(L.dim(g)-L.dim(l) for l,g in zip(lo,G)))
    print('orig==least', sum(a==b for a,b in zip(lo,o)), 'orig==greatest', sum(a==b for a,b in zip(o,G)), len(o))
