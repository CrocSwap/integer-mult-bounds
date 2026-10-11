"""Complex shared-donor response kernel on PR433's split-centre canonical word (PR451 parent chain).
usage: ckernel.py PARENT_SPLIT_CENTRES_DIR SELECTION.json OUT_WORKDIR
Writes OUT_WORKDIR/split-centres/CANONICAL-WORD.json.gz (kernelized) and KERNEL.json.
Entry = (entrance vector e, pivot p, donor d, lambda): response(p) = lambda*response(d) exactly over Q, where
response(h) is the frame-0 compensation column of helper h on the 120 targets; e lies in the first frame of p and d.
Pivot starts at frame <e> and leaves the compensation; d += -lambda*p at <e> before A; d += lambda*p at FULL after cleanup.
Rohan Arun with Claude Opus 5.5 (Anthropic) assistance; adapted from the PR417 bit kernel lineage. Apache-2.0."""
import copy,gzip,hashlib,json,sys
from collections import Counter,defaultdict
from fractions import Fraction as Q
from pathlib import Path
src,selp,out=Path(sys.argv[1]),Path(sys.argv[2]),Path(sys.argv[3])
c=json.loads(gzip.decompress((src/'CANONICAL-WORD.json.gz').read_bytes()))
sel=json.loads(selp.read_text())
v,R,h=c['v'],c['R'],c['h'];n=2*v+R;F=[tuple(f) for f in c['frames']]
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
fi={f:i for i,f in enumerate(F)}
assert all(basis(f)==f for f in F)
def fid(vs):
    t=basis(vs)
    if t not in fi:fi[t]=len(F);F.append(t)
    return fi[t]
def contains(big,small):return basis(list(F[big])+list(F[small]))==F[big]
resp=defaultdict(dict)
for e in c['compensation']:
    assert e[0]=='add' and v<=e[1]<2*v and 2*v<=e[2]<n and e[5]==0
    resp[e[2]][e[1]]=resp[e[2]].get(e[1],Q(0))+Q(e[3],e[4])
first={}
for e in c['A']:
    for r in [e[1]]+([e[2]] if e[0]=='add' else []):
        if 2*v<=r<n and r not in first:first[r]=e[-1]
assert all(c['start'][r]==0 for r in range(v,n)) and all(c['final'][r]==1 for r in range(2*v,n))
piv={};don={};kin=[];kout=[];tot=0
for vec,p,d,num,den in sel['entries']:
    lam=Q(num,den);E=fid([vec])
    assert 2*v<=p<n and 2*v<=d<n and p!=d and p not in piv and p not in don and d not in piv
    assert don.setdefault(d,E)==E,'donor serves one entrance'
    assert set(resp[p])==set(resp[d]) and all(resp[p][t]==lam*resp[d][t] for t in resp[p]),('response relation',p)
    assert contains(first[p],E) and contains(first[d],E),('entrance outside first frame',p,d)
    piv[p]=E;tot+=len(F[E])
    kin.append(['add',d,p,(-lam).numerator,(-lam).denominator,E]);kout.append(['add',d,p,lam.numerator,lam.denominator,1])
w=copy.deepcopy(c)
for p,E in piv.items():w['start'][p]=E
w['compensation']=[e for e in c['compensation'] if e[2] not in piv]
w['A']=kin+c['A'];w['cleanup']=c['cleanup']+kout
# exact replay of the complete program on all 800 columns
def apply(e,rows):
    if e[0]=='scale':
        _,t,a,b,*_=e;q=Q(a,b);rows[t]={j:q*x for j,x in rows[t].items()}
    else:
        _,t,s,a,b,*_=e;q=Q(a,b);assert t!=s
        for j,x in list(rows[s].items()):
            z=rows[t].get(j,Q(0))+q*x
            if z:rows[t][j]=z
            else:rows[t].pop(j,None)
def replay(w):
    rows=[{r:Q(1)} for r in range(n)]
    for e in w['precondition']+w['compensation']+w['A']+w['cut']+w['B']+w['cleanup']:apply(e,rows)
    exp=[{r:Q(1)} for r in range(n)]
    for t in range(v):exp[v+t][t]=Q(1)
    return rows==exp
assert replay(w),'kernel program does not restore every column'
controls=[]
for name,mut in [('omitted exit correction',lambda x:x['cleanup'].pop()),
                 ('omitted entry correction',lambda x:x['A'].pop(0)),
                 ('wrong lambda sign',lambda x:x['A'][0].__setitem__(3,-x['A'][0][3])),
                 ('pivot kept out without donors',lambda x:(x['A'].__delitem__(0),x['cleanup'].pop(-len(kout))))]:
    x=copy.deepcopy(w);mut(x)
    if replay(x):raise AssertionError('mutation accepted '+name)
    controls.append(name)
# climbs, paid profile and nested edges exactly as the PR433 audit
cur=list(w['start']);paid=Counter();edges=set()
def climb(r,f):
    old=cur[r]
    if old!=f:
        assert contains(f,old);d_=len(F[f])-len(F[old]);assert d_>0
        edges.add((old,f));paid[d_]+=1;cur[r]=f
for part in ('A','B'):
    if part=='B':
        assert all(cur[r]==f for r,f in zip(w['centers'],w['center_frames'])) and all(cur[r]==0 for r in range(v,2*v))
        for f in w['center_frames']:paid[len(F[f])]+=1
    for e in w[part]:
        for r in [e[1]]+([e[2]] if e[0]=='add' else []):climb(r,e[-1])
for r,f in enumerate(w['final']):climb(r,f)
assert sum(r*x for r,x in paid.items())==9*R-tot+240*8+72
w['local_profile']={str(k):x for k,x in sorted(paid.items())};w['edges']=sorted(edges);w['frames']=[list(f) for f in F]
w['kernel']=dict(entries=sel['entries'],entrance_rank=tot,rule='pivot starts at <e>, leaves frame-0 compensation; donor += -lambda*pivot at <e> before A; donor += lambda*pivot at FULL after cleanup')
(out/'split-centres').mkdir(parents=True,exist_ok=True)
blob=json.dumps(w,sort_keys=True,separators=(',',':')).encode()
(out/'split-centres/CANONICAL-WORD.json.gz').write_bytes(gzip.compress(blob,mtime=0))
res=dict(status='PASS_COMPLEX_RESPONSE_KERNEL',pivots=len(piv),donors=len(don),entrance_rank=tot,local_profile=w['local_profile'],
         parent_local_profile=c['local_profile'],frames=len(F),edges=len(edges),mutations_rejected=controls,
         helper_widths=dict(Counter(h-len(F[w['start'][r]]) for r in range(2*v,n))),canonical_word_payload_sha256=hashlib.sha256(blob).hexdigest())
(out/'KERNEL.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res))
