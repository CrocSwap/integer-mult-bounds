"""Exact replay (nested frames, F2 endpoint on every column) and local paid profile for bitE8/1+mut words, punctured or not.
Prepared with Claude Opus 5.5 (Anthropic), via Claude Code; Apache-2.0."""
import json,gzip,hashlib,copy
from fractions import Fraction as Q
from collections import Counter

def load(p):
    return json.load(gzip.open(p,'rt'))

def canon(w):
    return json.dumps(w,sort_keys=True,separators=(',',':')).encode()

def save(w,p):
    data=gzip.compress(canon(w),compresslevel=9,mtime=0); data=data[:9]+bytes([255])+data[10:]
    open(p,'wb').write(data); return hashlib.sha256(data).hexdigest()

def basis(vecs):
    B={}
    for rr in vecs:
        row=list(map(Q,rr))
        for c in sorted(B):
            q=row[c];row=[a-q*b for a,b in zip(row,B[c])]
        c=next((i for i,x in enumerate(row) if x),None)
        if c is not None:
            q=row[c];B[c]=[x/q for x in row]
    return B

class Frames:
    def __init__(self,w):
        self.w=w
        self.lines=w['lines']
        self.fb=[basis(self.lines[i] for i in f) for f in w['frames']]
        self.dim=[len(b) for b in self.fb]
        self.mask=[sum(1<<i for i in f) for f in w['frames']]
    def le(self,a,b):
        return self.mask[a]&self.mask[b]==self.mask[a]

def replay(w,F=None,check=True):
    """returns (H profile without copies, copy ranks). Asserts exact endpoint and nesting."""
    V=w['v'];N=2*V+w['R']
    F=F or Frames(w)
    dim,mask=F.dim,F.mask
    val=[1<<i for i in range(N)];cur=list(w['start']);H=Counter();tops=[]
    def climb(r,f):
        a=cur[r]
        if a==f: return
        assert mask[a]&mask[f]==mask[a],(r,a,f)
        if dim[f]>dim[a]: H[dim[f]-dim[a]]+=1
        cur[r]=f
    def gates(sec):
        for f,t,ss in w[sec]:
            assert len({t,*ss})==1+len(ss)
            for r in [t,*ss]: climb(r,f)
            for s in ss: val[t]^=val[s]
    gates('D');gates('A')
    tops.extend(dim[cur[q]] for q in w['ret']);snap=[val[q] for q in w['ret']]
    for t,ks in enumerate(w['scatter']):
        for k in ks: val[V+t]^=snap[k]
    gates('B');gates('C')
    for r,f in enumerate(w['final']): climb(r,f)
    if check:
        for r in range(N):
            assert val[r]==((1<<r)^(1<<(r-V)) if V<=r<2*V else 1<<r),r
    return H,tops

def paid(w,F=None):
    H,tops=replay(w,F)
    return dict(sorted((H+Counter(tops)).items()))

def rebuild_C(w):
    """C = literal reverse of z-destination gates of A then B, each at the full frame"""
    V=w['v']
    full=next(i for i,f in enumerate(w['frames']) if len(f)==V)
    z=[g for g in w['A']+w['B'] if g[1]<V or g[1]>=2*V]
    return [[full,t,list(ss)] for f,t,ss in reversed(z)]
