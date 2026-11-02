"""Exact source patch, scalar identity and literal frame invoice.
Adapted from a separate OpenAI Codex review by Ross Richardson.
Assertions must remain active; the public driver starts this in an unoptimized
child interpreter with an isolated bytecode-cache namespace."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter,defaultdict
from functools import lru_cache
import gzip,hashlib,json,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SRC=ROOT/'research/rank7-coupled-586-588-carrier-fold/edits'
@lru_cache(None)
def span(xs):
    a={0}
    for x in xs:a|={v^x for v in tuple(a)}
    return frozenset(a)
def dim(s):
    d=len(s).bit_length()-1;assert len(s)==1<<d;return d
FULL=span(tuple(1<<i for i in range(9)))
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def scalar(g):return g[:5] if g[0]=='add' else g[:4]
def profile(w):
    removed=set(w['removed']);current={r:span((w['ports'][r],)) if r<112 else span(tuple(w['start_extra'].get(str(r),[]))) for r in range(704)}
    counts=Counter();positive=0
    def climb(r,E):
        nonlocal positive
        E=span(tuple(E));assert current[r]<=E,(r,current[r],E)
        d=dim(E)-dim(current[r]);current[r]=E
        if d:counts[d]+=1;positive+=1
    def gate(g):
        if g[0]=='warp':
            r=g[1];assert current[r]==span(tuple(g[3]));current[r]=span(tuple(g[4]))
        else:
            for r in g[1:3] if g[0]=='add' else g[1:2]:climb(r,g[-1])
    for g in w['A']:gate(g)
    for r,E in zip(w['centers'],w['center_frames']):climb(r,E)
    for t in range(112):climb(112+t,w.get('target_levels',{}).get(str(t),[]))
    at=defaultdict(list)
    for p,r,G,U,E in w['warps']:at[p].append((r,U,E))
    for i in range(len(w['B'])+1):
        for r,U,E in at[i]:
            assert current[r]==span(tuple(U)),('native entry',i,r)
            current[r]=span(tuple(E))
        if i<len(w['B']):gate(w['B'][i])
    for g in w['restore']:gate(g)
    for r in range(704):
        if r in removed:continue
        E=w['helper_final'].get(str(r),list(FULL))
        if 112<=r<224:E=[x for x in FULL if not (x&w['ports'][r-112]).bit_count()%2]
        climb(r,E)
    # Separately paid private center descents through every served target level.
    for r,E in zip(w['centers'],w['center_frames']):
        U=span(tuple(E))
        levels={span(tuple(w.get('target_levels',{}).get(str(g[1]-112),[]))) for g in w['cut'] if g[2]==r}
        for T in sorted(levels,key=len,reverse=True):
            assert T<=U
            d=dim(U)-dim(T)
            if d:counts[d]+=1;positive+=1
            U=T
    inventory=Counter()
    for r in range(224,704):
        if r in removed:continue
        start=span(tuple(w['start_extra'].get(str(r),[])))
        end=span(tuple(w['helper_final'].get(str(r),list(FULL))))
        width=dim(end)-dim(start)
        if width:inventory[width]+=1
    return dict(sorted(counts.items())),dict(sorted(inventory.items())),positive

# Independent suffix-prefix identity proof. The differing gates access pivot
# values before any write to those pivots, so only their two input columns can
# change. Propagate those six relevant input columns exactly through the prefix.
CASES={644:((640,496),(2,-2),(184,185,186,187),599),660:((656,520),(-1,-2),(216,217,218,219),647)}
def prefix_columns(w,stop,changed=False,initial=None):
    inputs=(644,640,496,660,656,520)
    v={r:{r:Q(1)} if r in inputs else {} for r in range(704)}
    def add(d,s,q):
        for k,x in v[s].items():
            v[d][k]=v[d].get(k,Q(0))+q*x
            if not v[d][k]:del v[d][k]
    if initial:
        for h,(rs,qs,_,_) in CASES.items():
            for r,q in zip(rs,qs):add(r,h,Q(q))
    at=defaultdict(list)
    for p,r,G,U,E in w['warps']:at[p].append(r)
    for i in range(stop+1):
        if changed:
            for h,(rs,qs,drops,release) in CASES.items():
                if i==release:
                    for r,q in zip(rs,qs):add(r,h,Q(q))
        if i==stop:break
        for r in at[i]:assert not v[r],('pivot response crossed native unexpectedly',i,r,v[r])
        if changed and any(i in c[2] for c in CASES.values()):continue
        g=w['B'][i]
        if g[0]=='add':add(g[1],g[2],Q(g[3],g[4]))
        else:v[g[1]]={k:q*Q(g[2],g[3]) for k,q in v[g[1]].items() if q*Q(g[2],g[3])}
    return v

rows=[];pins={}
for provider in (sys.argv[1],):
    oldpath=SRC/f'FINAL-WORD-{provider}.json.gz';newpath=HERE/f'STAGED644-660-{provider}.json.gz'
    old,new=read(oldpath),read(newpath)
    for p in (oldpath,newpath):pins[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    expected=[];positions={};drops=set().union(*(set(c[2]) for c in CASES.values()))
    for i in range(len(old['B'])+1):
        positions[i]=len(expected)
        for h,(rs,qs,_,release) in CASES.items():
            if i==release:
                expected.extend(['add',r,h,q,1] for r,q in zip(rs,qs))
        if i<len(old['B']) and i not in drops:expected.append(scalar(old['B'][i]))
    assert [scalar(g) for g in new['B']]==expected
    assert [scalar(g) if g[0]!='warp' else g for g in new['A']]==[scalar(g) if g[0]!='warp' else g for g in old['A']]
    assert [scalar(g) for g in new['restore']]==[scalar(g) for g in old['restore']]
    assert new['warps']==[[positions[p],r,G,U,E] for p,r,G,U,E in old['warps']]
    for k in ('removed','centers','center_frames','ports','precondition','compensation','initial_corrections','helper_final','cut','target_levels','prelude_events'):
        assert new[k]==old[k],('unlisted field change',provider,k)
    starts=dict(old['start_extra']);starts.update({'644':[429,30],'660':[429,30]});assert new['start_extra']==starts
    for h,(rs,qs,ds,stop) in CASES.items():
        for r in (h,*rs):
            assert str(r) not in old['helper_final'] and old['start_extra'][str(r)]==[30]
            assert all(r not in (g[1:3] if g[0]=='add' else g[1:2]) for g in old['A'])
            assert all(g[2]!=r for g in old['compensation'])
            assert all(g['source']!=r for g in old['initial_corrections'])
        assert all(old['B'][i][1]!=h for i in range(stop))
        assert all(old['B'][i][0]=='add' and old['B'][i][2]==h and 112<=old['B'][i][1]<224 for i in ds)
    assert prefix_columns(old,647,changed=True)==prefix_columns(old,647,initial=True)
    before,oldinv,_=profile(old);after,newinv,positive=profile(new)
    assert before=={int(k):v for k,v in old['report']['local_profile'].items()},(before,old['report']['local_profile'])
    assert after=={1:2439,2:726,3:224,4:102,5:20,8:8}
    assert oldinv=={4:26,5:2,6:18,7:50,8:99,9:213}
    assert newinv=={4:26,5:2,6:18,7:52,8:97,9:213}
    rows.append({'provider':provider,'source_patch_exact':True,'prefix_identity_Pnew_equals_PoldS':True,'local_profile':after,'inventory':newinv,'positive_climbs':positive})
out={'status':'PASS_ROOT_SOURCE_PATCH_PREFIX_AND_FRAME_INVOICE','results':rows,'hashes':pins,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
     'scope':'Independent literal source/row/profile/inventory check; full arbitrary-dirty forward/dual cleanup and phase verification are separately source-bound native evidence, not duplicated by this script. Owner chronology/outer still separate.'}
print(json.dumps(out,indent=2))
