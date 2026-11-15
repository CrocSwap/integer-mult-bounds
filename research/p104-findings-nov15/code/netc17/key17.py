"""NETC17 gate part 2: are delivered contents unique per (frame)? distinct (content,F) pairs vs helpers, native vs compiled."""
import sys, collections, statistics as S
W5='inputs/'
sys.path.insert(0, W5+'REBUILDKIT')
from load import Word
from fractions import Fraction as Fr
P=2**61-1
def run(path,tag):
    w=Word(path); W=w.W; n=w.n; N=w.N; dim=w.dim
    Hs=set(r for r in range(n) if w.cls[r]=='h'); top=max(dim)
    rows=[({r:1} if r<n else {}) for r in range(N)]
    md=lambda q:(lambda q:q.numerator%P*pow(q.denominator%P,P-2,P)%P)(Fr(q))
    G=[]; touched=set()
    for t,e in enumerate(W['program']):
        op=e[0]; r=e[1]
        if op=='MOVE': continue
        if op in('INIT','CLEAR'): rows[r]={}; continue
        if op=='SCALE':
            q=md(e[2]); rows[r]={k:v*q%P for k,v in rows[r].items()}; continue
        s=e[2]; q=md(e[3]); F=e[4]
        if r in Hs: touched.add(r)
        if s in Hs:
            touched.add(s)
            if r not in Hs:
                c=frozenset((k,v) for k,v in rows[s].items() if k not in Hs)
                if c: G.append((s,c,F,dim[F],r,t))
        for k,v in rows[s].items():
            nv=(rows[r].get(k,0)+q*v)%P
            if nv: rows[r][k]=nv
            else: rows[r].pop(k,None)
    def norm(c):
        d=dict(c); k0=min(d); inv=pow(d[k0],P-2,P); return frozenset((k,v*inv%P) for k,v in d.items())
    nc=len(touched)
    cs=set(norm(g[1]) for g in G)
    cF=set((norm(g[1]),g[2]) for g in G)
    cd=set((norm(g[1]),g[3]) for g in G)
    ch=set((norm(g[1]),g[0]) for g in G)
    # (content, helper) distinct already ~ helpers use; and (content,F,receiver-set size)
    print(tag,'helpers',nc,'gives',len(G),'proj contents',len(cs),'(content,F)',len(cF),'(content,dim)',len(cd),'(content,helper)',len(ch),flush=True)
    byc=collections.Counter(norm(g[1]) for g in G)
    print(tag,'gives per content mean %.1f max %d; helpers per content mean %.2f'%(S.mean(byc.values()),max(byc.values()),len(ch)/len(cs)))
    # helpers per content-F
    print(tag,'helper-content ratio: (content,F)/helpers=%.2f contents/helpers=%.2f (content,dim)/helpers=%.2f'%(len(cF)/nc,len(cs)/nc,len(cd)/nc))
    # distinct receivers and receiver frames
    rf=set((g[4]) for g in G); print(tag,'distinct receivers',len(rf))
    # pre-frame: how many frames F used by gives
    print(tag,'distinct give frames',len(set(g[2] for g in G)))
run(W5+'MAINFUSE/w7546.json.gz','native')
run(W5+'NETC15/glob_p.json.gz','glob_p')
