"""Replay zero-response slicing and ten frozen exact-cost frame changes.

Prepared for chafreaky with Codex assistance, Apache-2.0.
The suffix-response deletion is adapted from rohanarun's PR542 slice.py.
The fixed two-sided frame recipe and exact interval checks are new here.
No optimizer or floating-point decisions are used in this replay.
"""
import argparse, copy, gzip, hashlib, importlib.util, json
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from pathlib import Path

if not __debug__: raise SystemExit('Assertions must remain enabled')
ap=argparse.ArgumentParser();ap.add_argument('package',type=Path);ap.add_argument('source',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args()
assert not a.out.exists();a.out.mkdir(parents=True)
read=lambda p:json.loads(p.read_bytes())
w=json.loads(gzip.decompress(a.source.read_bytes()));original=copy.deepcopy(w)
recipe=read(a.package/'data/FRAME-RECIPE.json');slicing=read(a.package/'data/SLICE-RECIPE.json')
V=w['v'];N=2*V+w['R'];assert (V,N)==(120,720)
resp=[0]*N
for j in range(V):resp[V+j]=1<<j
for f,d,ss in reversed(w['B']):
    for s in ss:resp[s]^=resp[d]
for j,ss in enumerate(w['scatter']):
    for s in ss:resp[w['ret'][s]]^=resp[V+j]
dead=[]
for i in reversed(range(len(w['A']))):
    f,d,ss=w['A'][i]
    if resp[d]==0:dead.append(i)
    for s in ss:resp[s]^=resp[d]
assert sorted(dead)==slicing['removed_indices'] and len(dead)==227
assert [w['A'][i] for i in sorted(dead)]==slicing['removed_gates']
w['A']=[g for i,g in enumerate(w['A']) if i not in set(dead)]
w['C']=[[1,d,list(ss)] for f,d,ss in reversed(w['A'])]
frames=list(map(frozenset,w['frames']));lines=w['lines']
@lru_cache(None)
def basis(F):
    B={}
    for i in sorted(F):
        row=list(map(Q,lines[i]))
        for j,u in sorted(B.items()):
            q=row[j];row=[x-q*y for x,y in zip(row,u)]
        j=next((j for j,x in enumerate(row) if x),None)
        if j is not None:
            q=row[j];B[j]=[x/q for x in row]
    return B
def in_span(B,row):
    row=list(map(Q,row))
    for j,u in sorted(B.items()):
        q=row[j];row=[x-q*y for x,y in zip(row,u)]
    return not any(row)
for F in frames:assert F==frozenset(i for i,row in enumerate(lines) if in_span(basis(F),row))
rank=lambda f:len(basis(frames[f]))
def replay():
    cur=w['start'].copy();z=[1<<i for i in range(N)];H=Counter()
    def climb(r,f):
        old=cur[r];assert frames[old]<=frames[f],(r,old,f)
        diff=rank(f)-rank(old)
        if diff:H[diff]+=1
        cur[r]=f
    for section in ('D','A','B','C'):
        if section=='B':
            assert all(cur[V+j]==0 for j in range(V))
            snap=[z[r] for r in w['ret']]
            for r in w['ret']:assert rank(cur[r])==8;H[8]+=1
            for j,ss in enumerate(w['scatter']):
                for s in ss:z[V+j]^=snap[s]
        for f,d,ss in w[section]:
            assert len(set([d]+ss))==len(ss)+1
            for r in [d]+ss:climb(r,f)
            for s in ss:z[d]^=z[s]
    for r,f in enumerate(w['final']):climb(r,f)
    assert z==[(1<<r)^((1<<(r-V)) if V<=r<2*V else 0) for r in range(N)]
    return H
H0=replay();assert dict(H0)=={int(k):v for k,v in recipe['before'].items()}
engine=a.package/'vendor/e8-r480-nine-stage/vendor/e8-r740-replica32/code/engines/moment.py'
spec=importlib.util.spec_from_file_location('price',engine);M=importlib.util.module_from_spec(spec);spec.loader.exec_module(M)
weights={r:M.moment({r:1},64,30720,Q(recipe['reference_rate']),True) for r in range(1,9)}
receipts=[]
for move in recipe['moves']:
    sec,i=move['section'],move['index'];assert sec in ('A','B')
    gate=w[sec][i];assert sorted(frames[gate[0]])==move['old']
    H=replay();gate[0]=frames.index(frozenset(move['new']));after=replay()
    delta={r:after[r]-H[r] for r in H.keys()|after.keys() if after[r]!=H[r]}
    assert delta=={int(k):v for k,v in move['delta'].items()}
    assert sum(r*n for r,n in delta.items())==0
    lo=hi=Q(0)
    for r,n in delta.items():
        x,y=weights[r];lo+=n*(x if n>=0 else y);hi+=n*(y if n>=0 else x)
    assert hi<0 and [str(lo),str(hi)]==move['cost_interval']
    receipts.append(dict(section=sec,index=i,delta=delta,cost_interval=[str(lo),str(hi)]))
assert len(receipts)==10
H1=replay();assert dict(H1)=={int(k):v for k,v in recipe['after'].items()}
for key in ('D','B','scatter','ret','start','final','lines','frames'):assert w[key]==original[key]
assert w['C']==[[1,d,list(ss)] for f,d,ss in reversed(w['A'])]
raw=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
assert hashlib.sha256(raw).hexdigest()==recipe['word_content_sha256']
blob=gzip.compress(raw,mtime=0);blob=blob[:9]+bytes([255])+blob[10:]
assert hashlib.sha256(blob).hexdigest()==recipe['word_sha256']
(a.out/'WORD.json.gz').write_bytes(blob)
result=dict(status='PASS_EXACT_SLICE_AND_TEN_FROZEN_FRAME_MOVES',removed_gates=len(dead),moves=receipts,all_dirty_columns=N,local_profile=dict(H1),word_sha256=hashlib.sha256(blob).hexdigest(),source_sha256=hashlib.sha256(a.source.read_bytes()).hexdigest())
(a.out/'BUILD.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],flush=True)
