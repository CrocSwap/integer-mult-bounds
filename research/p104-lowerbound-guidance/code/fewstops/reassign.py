# FEWSTOPS: re-assign public-public gate charts to the greatest consistent assignment (U) and rebuild the word.
# Owned-register gates/moves pinned; public endpoints, gate order, rows unchanged.
from load import *
from collections import Counter
import copy
def smask(S):
    m=0
    for v in S: m|=1<<v
    return m
SM=[smask(s) for s in SP]
mask2id={}
for i,m in enumerate(SM): mask2id.setdefault(m,i)
def basis_of(m):
    vs=[v for v in range(512) if m>>v&1]; B=[]; S={0}
    for v in vs:
        if v not in S:
            B.append(v); S|={x^v for x in S}
    return B
def dimm(m): return bin(m).count('1').bit_length()-1
def build(W, mode='U'):
    N=n+W['owned_fields']
    frames=[list(f) for f in W['frames']]; m2i=dict(mask2id)
    def fid(m):
        if m not in m2i: m2i[m]=len(frames); frames.append(basis_of(m))
        return m2i[m]
    # which registers are owned at each event: r>=n
    ceil=[SM[W['final'][r]] for r in range(n)]
    G=[None]*len(P)
    for i in range(len(P)-1,-1,-1):
        e=P[i]; op=e[0]
        if op in ('ADD','COPY'):
            d,s,f=e[1],e[2],e[4]
            if d>=n or s>=n:
                for r in (d,s):
                    if r<n:
                        assert SM[f] & ceil[r]==SM[f], 'pinned gate above ceiling'
                        ceil[r]=SM[f]
                G[i]=SM[f]
            else:
                g=ceil[d]&ceil[s]; ceil[d]=g; ceil[s]=g; G[i]=g
        elif op=='SCALE' and e[1]<n:
            G[i]=ceil[e[1]]  # scale at current ceiling
        elif op=='SCALE':
            G[i]=SM[e[3]]
    # forward rebuild
    cur=[SM[x] for x in W['initial']]
    prog=[]
    for i,e in enumerate(P):
        op=e[0]
        if op=='MOVE':
            if e[1]>=n: prog.append(e)
            continue
        if op in ('INIT','CLEAR'): prog.append(e); continue
        regs=[e[1]] if op=='SCALE' else [e[1],e[2]]
        g=G[i]
        for r in regs:
            if r<n and cur[r]!=g:
                assert cur[r]&g==cur[r]
                prog.append(['MOVE',r,fid(cur[r]),fid(g),False]); cur[r]=g
        if op=='SCALE': prog.append(['SCALE',e[1],e[2],fid(g) if e[1]<n else e[3]])
        else: prog.append([op,e[1],e[2],e[3],fid(g)])
    for r in range(n):
        fm=SM[W['final'][r]]
        if cur[r]!=fm: prog.append(['MOVE',r,fid(cur[r]),W['final'][r],False]); cur[r]=fm
    W2=dict(W); W2['program']=prog; W2['frames']=frames
    return W2
