"""Check that a word differs from the rebuilt PR531 selected (pre-coalescing) word only by monotone frame lifts.
Prepared by rohanarun with Claude Opus 5.5 (Anthropic). Apache-2.0.
usage: check_frame_lifts.py SELECTED_WORD NEW_WORD OUT.json
Conditions (the PR531 coalescing lemma, applied node-wise): identical scalar operations, cut, cleanup-free fields, centres,
centre frames, starts and target levels; every A/B operation frame G contains its constructor frame F; every register's frame
chain (start, A, centre/target barriers, B, final frame) is monotone. Then each operation is executed at a frame that contains the
frame its constructor proved legal and is contained in its successors, exactly as in a PR531 promotion."""
import sys,json,gzip,hashlib
from collections import Counter
S,N,O=sys.argv[1:4]
sel=json.load(gzip.open(S));new=json.load(gzip.open(N))
def basis(vs):
    b={}
    for x in vs:
        for p in sorted(b,reverse=True):
            if x>>p&1:x^=b[p]
        if x:
            p=x.bit_length()-1
            for q in b:
                if b[q]>>p&1:b[q]^=x
            b[p]=x
    return tuple(b[p] for p in sorted(b,reverse=True))
def le(F,G): return basis(list(F)+list(G))==basis(G)
for k in ('ports','cut','precondition','centers','center_frames','scatter','start_extra','target_levels'):
    assert sel.get(k)==new.get(k),k
lifted=Counter();same=0
for sec in ('A','B'):
    assert len(sel[sec])==len(new[sec])
    for a,b in zip(sel[sec],new[sec]):
        assert a[:-1]==b[:-1],('operation changed',sec)
        assert le(a[-1],b[-1]),('frame not a lift of the constructor frame',sec,a,b)
        if basis(a[-1])==basis(b[-1]): same+=1
        else: lifted[(sec,len(basis(a[-1])),len(basis(b[-1])))]+=1
V=len(new['ports']);R=new['report']['R'];n=2*V+R
FULL=basis([1<<i for i in range(9)])
hyper=lambda p: basis([x for x in range(1,512) if not (x&p).bit_count()%2])
cur=[(p,) for p in new['ports']]+[()]*(V+R)
for r,F in new.get('start_extra',{}).items(): cur[int(r)]=basis(F)
lev={int(t):basis(F) for t,F in new.get('target_levels',{}).items()}
paid=Counter()
def step(r,F):
    F=basis(F);assert le(cur[r],F),('chain not monotone',r)
    if len(F)>len(cur[r]): paid[len(F)-len(cur[r])]+=1
    cur[r]=F
for sec in ('A','B'):
    if sec=='B':
        for r,F in zip(new['centers'],new['center_frames']): assert cur[r]==basis(F),'centre barrier'
        for t in range(V): assert cur[V+t]==lev.get(t,()),'target barrier'
    for e in new[sec]:
        for r in (e[1:3] if e[0]=='add' else e[1:2]): step(r,e[-1])
for r in range(n): step(r,hyper(new['ports'][r-V]) if V<=r<2*V else FULL)
res=dict(status='PASS_MONOTONE_FRAME_LIFTS_OF_CONSTRUCTOR_WORD',selected_sha256=hashlib.sha256(gzip.decompress(open(S,'rb').read())).hexdigest(),
  new_sha256=hashlib.sha256(gzip.decompress(open(N,'rb').read())).hexdigest(),unchanged_frames=same,
  lifted={f'{s}:{a}->{b}':z for (s,a,b),z in sorted(lifted.items())},lifted_total=sum(lifted.values()),chain_paid_profile=dict(sorted(paid.items())))
open(O,'w').write(json.dumps(res,indent=1)+'\n');print(json.dumps({k:res[k] for k in ('status','unchanged_frames','lifted_total','chain_paid_profile')}))
