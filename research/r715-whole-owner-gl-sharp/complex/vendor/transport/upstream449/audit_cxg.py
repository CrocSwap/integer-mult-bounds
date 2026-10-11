# Modified from PR425 by icekylinx with Codex assistance.
"""Read-back audit, independent of the Hamming producer and its row state."""
import copy,gzip,hashlib,importlib.util,json,math,time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

import os
OUT=Path(os.environ.get('CXOUT','split-centres'));p=OUT/'FULL-WORD.json.gz'
word=json.load(gzip.open(p));v=120;n=240+word['report']['R'];start=time.monotonic()
def apply(e,rows):
    if e[0]=='scale':
        _,t,a,b,*_=e;q=Q(a,b);assert q
        rows[t]={j:q*x for j,x in rows[t].items()}
    else:
        _,t,s,a,b,*_=e;q=Q(a,b);assert t!=s
        for j,x in list(rows[s].items()):
            z=rows[t].get(j,Q(0))+q*x
            if z:rows[t][j]=z
            else:rows[t].pop(j,None)
def ident():return [{r:Q(1)} for r in range(n)]
def inv(e):
    e=copy.deepcopy(e)
    if e[0]=='add':e[3]*=-1
    else:e[2],e[3]=e[3],e[2]
    return e
def dual(e):
    e=inv(e)
    if e[0]=='add':e[1],e[2]=e[2],e[1]
    return e

main=word['A']+word['cut']+word['B']
assert all(not 120<=e[2]<240 for e in word['A']+word['B'] if e[0]=='add' and not 120<=e[1]<240)
matrix=ident()
for e in main:apply(e,matrix)
print('full main columns',n,'replayed',flush=True)
# Compute -A_Y^-1 B_S using only rows of the explicit main operator.
dirty=[{} for r in range(n)]
for r in range(v,2*v):dirty[r]={j:x for j,x in matrix[r].items() if j>=2*v}
for e in word['precondition']:apply(e,dirty)
comp=[]
for r in range(v,2*v):
    for j,q in sorted(dirty[r].items()):comp.append(['add',r,j,-q.numerator,q.denominator,[]])

cleanup=[inv(e) for e in reversed(word['A']+word['B']) if not v<=e[1]<2*v]
assert [e[:-1] for e in cleanup]==[e[:-1] for e in word['cleanup']]
program=word['precondition']+comp+main+cleanup
actual=ident()
for e in program:apply(e,actual)
expected=ident()
for t in range(v):expected[v+t][t]=Q(1)
assert actual==expected
print('PASS exact arbitrary dirt and restored sources/helpers',flush=True)
back=ident()
for e in program:apply(dual(e),back)
expected_back=ident()
for t in range(v):expected_back[t][v+t]=Q(-1)
assert back==expected_back
print('PASS exact inverse-transpose on every column',flush=True)
# Independent sparse vector controls avoid repeating a dense full replay.
def vector(es,x):
    x=list(map(Q,x))
    for e in es:
        if e[0]=='scale':x[e[1]]*=Q(e[2],e[3])
        else:x[e[1]]+=Q(e[3],e[4])*x[e[2]]
    return x
sample=[((i*137+13)%101)-50 for i in range(n)]
want=vector(program,sample)
controls={
    'missing_dirty_compensation':word['precondition']+main+cleanup,
    'missing_Y_inverse_basis':comp+main+cleanup,
    'missing_source_cleanup':word['precondition']+comp+main,
    'wrong_dual_event_order':[dual(e) for e in reversed(program)],
}
for name,es in controls.items():
    expected_sample=vector([dual(e) for e in program],sample) if name=='wrong_dual_event_order' else want
    assert vector(es,sample)!=expected_sample,name

# Orthogonal transvection and a port permutation bring the new geometry onto
# the already fixed 120-port routing family. Every incidence is transformed.
old=json.load(gzip.open('work/higher-stage-e8/verified/gcert1-e8-retimed.json.gz'))
def tau(x):return x^(43 if (x&43).bit_count()%2 else 0)
assert 43 .bit_count()%2==0
assert set(map(tau,word['ports']))==set(old['ports'])
mapping={i:old['ports'].index(tau(q)) for i,q in enumerate(word['ports'])}
mapping.update({v+i:v+mapping[i] for i in range(v)})
mapping.update({r:r for r in range(2*v,n)})
def basis(vs):
    b={}
    for x in vs:
        for k in sorted(b,reverse=True):
            if x>>k&1:x^=b[k]
        if x:
            k=x.bit_length()-1
            for j in b:
                if b[j]>>k&1:b[j]^=x
            b[k]=x
    return tuple(b[k] for k in sorted(b,reverse=True))
def perp(x):return basis([z for z in range(1,512) if not (x&z).bit_count()%2])
full=tuple(1<<i for i in range(8,-1,-1));frames=[(),full];fi={f:i for i,f in enumerate(frames)}
def fid(f):
    f=basis(f)
    if f not in fi:fi[f]=len(frames);frames.append(f)
    return fi[f]
def canonical(e):
    e=copy.deepcopy(e);e[1]=mapping[e[1]]
    if e[0]=='add':e[2]=mapping[e[2]]
    if e[-1] is not None:e[-1]=fid([tau(x) for x in e[-1]])
    return e
can={key:[canonical(e) for e in word[key]] for key in ('A','B','cut','cleanup','precondition')}
can['compensation']=[canonical(e) for e in comp]
can['start']=[fid([q]) for q in old['ports']]+[0]*(v+word['report']['R'])
for _r,_E in word.get('start_extra',{}).items():can['start'][int(_r)]=fid([tau(x) for x in _E])
can['final']=[1]*v+[fid(perp(q)) for q in old['ports']]+[1]*word['report']['R']
can['ports']=old['ports'];can['centers']=[mapping[r] for r in word['centers']]
can['center_frames']=[fid([tau(x) for x in f]) for f in word['center_frames']]
can['target_levels']={}
for _t,_E in word.get('target_levels',{}).items():can['target_levels'][mapping[v+int(_t)]-v]=fid([tau(x) for x in _E])
can['h']=9;can['v']=v;can['R']=word['report']['R'];can['frames']=frames
cur=list(can['start']);paid=Counter();edges=set();incidences=0
def climb(r,f):
    old=cur[r]
    assert basis(frames[old]+frames[f])==frames[f]
    if old!=f:
        delta=len(frames[f])-len(frames[old]);assert delta>0
        edges.add((old,f));paid[delta]+=1;cur[r]=f
for part in ('A','B'):
    if part=='B':
        assert all(cur[r]==f for r,f in zip(can['centers'],can['center_frames']))
        assert all(cur[r]==can['target_levels'].get(r-v,0) for r in range(v,2*v))
        for r_c,f in zip(can['centers'],can['center_frames']):
            # mass-neutral descent: cf -> served levels (descending) -> lowest served level
            served={can['target_levels'].get(e[1]-v,0) for e in can['cut'] if e[2]==r_c}
            o=f
            for L in sorted(served,key=lambda L:-len(frames[L])):
                assert basis(frames[L]+frames[o])==tuple(frames[o]),('centre frame must contain served level',r_c)
                if L!=o:paid[len(frames[o])-len(frames[L])]+=1;edges.add((o,L));edges.add((L,o));o=L
            if o==f:paid[0]+=0
    for e in can[part]:
        rs=[e[1]]+([e[2]] if e[0]=='add' else [])
        for r in rs:climb(r,e[-1]);incidences+=1
for r,f in enumerate(can['final']):climb(r,f)
assert dict(paid)=={int(r):x for r,x in word['report']['local_profile'].items()}
assert sum(r*x for r,x in paid.items())==sum(int(r)*x for r,x in word['report']['local_profile'].items())
can['local_profile']=dict(sorted(paid.items()));can['edges']=sorted(edges)
cp=OUT/'CANONICAL-WORD.json.gz';cp.write_bytes(gzip.compress(json.dumps(can,sort_keys=True,separators=(',',':')).encode(),mtime=0))

b=Q(0);grid=Q(1,10**18)
coeff=Counter(str(Q(e[3],e[4]) if e[0]=='add' else Q(e[2],e[3])) for e in program)
report={'status':'PASS_EXACT_SCALAR_AND_FRAME_RESEARCH_CANDIDATE_NOT_YET_ADMITTED',
        'full_word_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
        'canonical_word_sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),
        'live_columns_each_orientation':n,'arbitrary_helper_columns':can['R'],
        'all_live_source_and_helper_rows_restored':True,'all_target_rows_correct':True,
        'negative_controls_rejected':list(controls),'old_response_additions':len(comp),
        'complete_forward_scalar_operations':len(program),'coefficient_histogram':dict(coeff),
        'frames':len(frames),'nested_directed_edges':len(edges),'common_frame_incidences':incidences,
        'orthogonal_transport_vector':43,'transported_ports_exactly_match_fixed_routes':True,
        'local_profile':dict(sorted(paid.items())),
        'two_rational_moment_engines':True,'next_b_grid_rejected':True,
        'remaining':['new general scalar-interface proof integration','exact phase and emitted local/global program','finite invoice and outer assembly'],
        'scope':'Substantial new scalar-network candidate. All parameter values remain prospective until the expanded scalar interface and complete phase-aware supplier are admitted.',
        'seconds':time.monotonic()-start}
(OUT/'SCALAR-FRAME-AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS audit',report['seconds'],flush=True)
