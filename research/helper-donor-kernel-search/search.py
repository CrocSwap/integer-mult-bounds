#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact helper-donor cold-kernel search (the #1274/#1286/#1297 mechanism) for gauge44/k8 local words.

For every register p and every write gate `p += k*Y` with earlier reads of p:
  * delete a nonempty subset of those early reads;
  * cancel p inside the write by `Y -= p/k` at a cut (after a read of Y, or at the write) and restore it with an
    early-cleanup tail gate `Y += p/k` at every position adjacent to a tail gate touching Y or p;
  * compute the exact change D of the whole program map mod 2^31-19;
  * compare D with the unit injection vector of every donor hook `X += p; <gate j reading X>; X -= p`, normalized,
    so that one hook with a dyadic coefficient q in {+-1,+-2,+-1/2,+-4} restores the map exactly (single-donor
    relation sum q*col = -D);
  * price each surviving candidate with #1186's exact frame solver (harness.Pricer: exactness mod p, cone caps,
    optimal frames). A negative delta is a profile gain.

usage: SHARD=i NSH=n python -B search.py WORD.json.gz TOOLKIT_DIR all|p1,p2,...
TOOLKIT_DIR = research/exact-frame-toolkit from PR #1186 (head 9254a3cc). Output is nomination data only;
a gain still needs native replay and strict owner admission. Wronskode, with Claude (Anthropic) assistance."""
import sys, itertools, time
from fractions import Fraction as Q
sys.path.insert(0, sys.argv[2])
import harness as C
PR=C.PR
path=sys.argv[1]; pivots=sorted({e[1] for e in __import__('harness').load(path)['B']}) if sys.argv[3]=='all' else [int(x) for x in sys.argv[3].split(',')]
P=C.Pricer(path); w=P.base; B=w['B']
base_rows=C.seg_rows(dict(w,_npre=0))
def diff(ed):
    w1=C.compile_edits(w,ed); r1=C.seg_rows(dict(w1,_npre=len(ed.get('prepend',[]))))
    out={}
    for q in set(base_rows)|set(r1):
        a=base_rows.get(q,{q:1}); b=r1.get(q,{q:1})
        for k in set(a)|set(b):
            d=(b.get(k,0)-a.get(k,0))%PR
            if d: out[(q,k)]=d
    return out
def E0(): return dict(delete=[],insert=[],tail=[],prepend=[])
inv=lambda x: pow(x,PR-2,PR)
QS=[Q(1),Q(-1),Q(2),Q(-2),Q(1,2),Q(-1,2),Q(4),Q(-4)]
import os
SH=int(os.environ.get('SHARD','0'));NS=int(os.environ.get('NSH','1'))
for p in pivots[SH::NS]:
  for wi,we in enumerate(B):
    if not(we[0]=='add' and we[1]==p): continue
    Y=we[2]; k=Q(we[3],we[4])
    early=[(i,e[1],Q(e[3],e[4])) for i,e in enumerate(B) if e[0]=='add' and e[2]==p and i<wi]
    if not early: continue
    pw=[i for i,e in enumerate(B) if e[1]==p and i<wi]; lo=max(pw)+1 if pw else 0  # p constant on [lo, wi)
    yr=[i for i,e in enumerate(B) if i<wi and e[0]=='add' and e[2]==Y and i>=lo]
    t0=time.time()
    # unit injection vectors: insert ('add',X,p,1) at j and ('add',X,p,-1) at j+1 around a read of X (gate j: t' += d X), lo<=j<wi
    hooks=[]
    for j in range(lo,wi):
        e=B[j]
        if e[0]=='add' and e[2]!=p and e[1]!=p:
            X=e[2]
            ed=dict(E0(),insert=[(j,['add',X,p,1,1,[]]),(j+1,['add',X,p,-1,1,[]])])
            v=diff(ed)
            if v: hooks.append((j,X,v))
    print('pivot',p,'write',wi,'Y',Y,'early',[(i,t,str(c)) for i,t,c in early],'hooks',len(hooks),'%.0fs'%(time.time()-t0),flush=True)
    def key(v):
        # normalize vector to a hashable with first nonzero scaled to 1
        it=sorted(v.items()); s=inv(it[0][1]); return tuple((a,b*s%PR) for a,b in it), it[0][1]
    hk={}
    for j,X,v in hooks:
        kk,lead=key(v); hk.setdefault(kk,[]).append((j,X,lead))
    T=[w['cleanup'][i] for i,U in w['early_cleanup']]
    tpos=sorted({0,len(T)}|{j for j,g in enumerate(T) if Y in g[1:3] or p in g[1:3]}|{j+1 for j,g in enumerate(T) if Y in g[1:3] or p in g[1:3]})
    for cut in sorted(set([x+1 for x in yr]+[wi])):
     for tp in tpos:
      for dsub in itertools.chain.from_iterable(itertools.combinations(early,r) for r in range(1,len(early)+1)):
        ed=dict(E0(),delete=[i for i,_,_ in dsub],insert=[(cut,['add',Y,p,-(1/k).numerator,(1/k).denominator,[]])],tail=[(tp,['add',Y,p,(1/k).numerator,(1/k).denominator,[]])])
        D=diff(ed)
        if not D: cands=[[]]
        else:
            negD={a:(-b)%PR for a,b in D.items()}
            kk,lead=key(negD); cands=[]
            for (j,X,l) in hk.get(kk,[]):
                q=lead*inv(l)%PR
                for qq in QS:
                    if (qq.numerator*inv(qq.denominator%PR))%PR==q: cands.append([(j,X,qq)])
        for cc in cands:
            e2=dict(ed,insert=list(ed['insert']))
            for j,X,qq in cc: e2['insert']+= [(j,['add',X,p,qq.numerator,qq.denominator,[]]),(j+1,['add',X,p,-qq.numerator,qq.denominator,[]])]
            r=P.price(e2,timeout=90)
            print('  cand cut',cut,'tail',tp,'del',[i for i,_,_ in dsub],'donor',[(j,X,str(qq)) for j,X,qq in cc],r.get('status'),r.get('delta'),r.get('profile'),flush=True)
