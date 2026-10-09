#!/usr/bin/env python3
"""Open generator of replacement-frames.json (discovery only; prove.py checks its output).

Copyright 2026 Joel Pulikkan (GamingPuzzled). Apache-2.0. Prepared with Anthropic Claude assistance.
Alternating passes over the operations of this package's bit word: each operation's common frame moves to the lower
bound (span of both roles' previous frames and the node's value span) or the upper bound (intersection of both
roles' next frames) when lower <= upper, the frame is nondegenerate, its Gram determinant has a residual below
2^80 after 2, 3 and 5, and the local child cost sum t log(m/t) drops.  Physical frame descent as in PR130/PR131;
upper-bound moves may leave the original frame, as in PR165.
Usage: python3 -B research/paired-cube-bit-rl-module/generate.py /new/path/plan.json
"""
import os,sys,json,math,time,tempfile
from collections import defaultdict
from pathlib import Path
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
import word
from prime_witnesses import det
_empty=tempfile.mkdtemp();Path(_empty,'replacement-frames.json').write_text(json.dumps(dict(p=12,frames=[])))
_out=word.HERE/'out'
word.HERE=Path(_empty);os.symlink(_out,Path(_empty,'out'))   # start from the unreplaced frames of out/
Candidate=word.Candidate
T0=time.time();log=lambda *a:print('[%5.0fs]'%(time.time()-T0),*a,flush=True)

def float_saving(row):
    C={int(k):n for k,n in row['child_histogram'].items()};W=row['W_per_vertex'];m=row['m']
    g=lambda a:math.fsum(n*r*math.exp(a*math.log(m/r)) for r,n in C.items())-W*m
    lo,hi=0.,1e-2
    for _ in range(70):
        mid=(lo+hi)/2;lo,hi=(mid,hi) if g(mid)<0 else (lo,mid)
    return lo

def generate(passes=6):
    c=Candidate([]);C=c.C;C.decoder();C.geometry();M=c.module;h=c.h;m=3*h;w=c.w
    ops=c.ops;orig=list(c.opframe);frames=list(c.opframe)
    role_ops=defaultdict(list)
    for i,(a,b,_) in enumerate(ops):role_ops[a].append(i);role_ops[b].append(i)
    idx={(s,i):k for s,l in role_ops.items() for k,i in enumerate(l)}
    start={b:w['source_frame'][s] for s,b in c.source.items()}
    start.update({b:z['frame'] for b,z in c.gauge.items()})
    after=defaultdict(list)
    for j,s in enumerate(w['rootroles']):after[s].append(w['root_frame'][j])
    full=w['full_frame']
    def prevF(s,i):
        k=idx[(s,i)];return frames[role_ops[s][k-1]] if k else start.get(s)
    def nextF(s,i):
        k=idx[(s,i)];l=role_ops[s]
        return frames[l[k+1]] if k+1<len(l) else (after[s][0] if after[s] else full)
    dim=lambda f:0 if f is None else C.dimf[f]
    phi=lambda t:t*math.log(m/t) if t>0 else 0.0
    def cost(i,F):
        a,b,_=ops[i];d=dim(F)
        return sum(phi(d-dim(prevF(s,i)))+phi(dim(nextF(s,i))-d) for s in (a,b))
    vals={}
    def valrows(x):
        if x not in vals:
            bits=C.sup[x];r=[]
            while bits:
                low=bits&-bits;r.append(C.chi[low.bit_length()-1]);bits-=low
            vals[x]=r
        return vals[x]
    lo_c,up_c,ok_c={},{},{}
    def lower(pa,pb,x):
        k=(pa,pb,x)
        if k not in lo_c:
            rows=(list(C.B[pa]) if pa is not None else [])+(list(C.B[pb]) if pb is not None else [])+valrows(x)
            B,_=M.reduce_rows(rows,h);lo_c[k]=c.register(B) if B else None
        return lo_c[k]
    def upper(na,nb):
        k=(min(na,nb),max(na,nb))
        if k not in up_c:
            B,_=M.kernel(list(C.A[na])+list(C.A[nb]),h);up_c[k]=c.register(B) if B else None
        return up_c[k]
    def valid(F):
        if F not in ok_c:
            ok=C.nondeg(F)
            if ok:
                B=C.B[F];s=list(map(sum,B))
                d=det([[9*sum(p*q for p,q in zip(x,y))-s[i]*s[j] for j,y in enumerate(B)] for i,x in enumerate(B)])
                if d==0:ok=False
                else:
                    r=abs(d)
                    for p in (2,3,5):
                        while r%p==0:r//=p
                    ok=r<2**80
            ok_c[F]=ok
        return ok_c[F]
    for p in range(passes):
        changes=0;gain=0.0
        for i in (range(len(ops)) if p%2==0 else reversed(range(len(ops)))):
            a,b,x=ops[i]
            L=lower(prevF(a,i),prevF(b,i),x);U=upper(nextF(a,i),nextF(b,i))
            if L is None or U is None or not C.sub(L,U):continue
            cur=frames[i];best=cur;bc=cost(i,cur)
            for F in (L,U):
                if F!=cur and valid(F):
                    cc=cost(i,F)
                    if cc<bc-1e-12:best,bc=F,cc
            if best!=cur:gain+=cost(i,cur)-bc;frames[i]=best;changes+=1
        log('pass',p,'changes',changes,'gain %.2f'%gain)
        if not changes:break
    out=[[i,[list(r) for r in C.B[frames[i]]]] for i in range(len(ops)) if not (C.sub(frames[i],orig[i]) and C.sub(orig[i],frames[i]))]
    return dict(p=12,discovery_only=True,frames=out,enlarged_beyond_original=sum(not C.sub(frames[i],orig[i]) for i,_ in out))

if __name__=='__main__':
    plan=generate(int(sys.argv[2]) if len(sys.argv)>2 else 6)
    Path(sys.argv[1]).write_text(json.dumps(plan,separators=(',',':')))
    log('wrote',len(plan['frames']),'frames,',plan['enlarged_beyond_original'],'outside the original')
