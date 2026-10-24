# GK: modified copy of PR #433's complex_audit.py (icekylinx with Codex; PR #425) by DreamingOfClouds with Claude Opus 5.5
# (Anthropic), via Claude Code.  Every change is marked "GK:"; with a word that has no start_extra / target_levels the
# behaviour and the written files are PR #433's.
# Modified from PR425 by icekylinx with Codex assistance.
"""Read-back audit, independent of the Hamming producer and its row state."""
import copy,gzip,hashlib,importlib.util,json,math,time
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

OUT=Path('split-centres');p=OUT/'FULL-WORD.json.gz'
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
for _r,_E in word.get('start_extra',{}).items():
    assert 2*v<=int(_r)<2*v+word['report']['R'],('an entrance (residual wrapper, spectators, bank footprint) is defined for helper registers only',_r)   # GK
    can['start'][int(_r)]=fid([tau(x) for x in _E])   # GK: helper entrances
can['final']=[1]*v+[fid(perp(q)) for q in old['ports']]+[1]*word['report']['R']
can['ports']=old['ports'];can['centers']=[mapping[r] for r in word['centers']]
can['center_frames']=[fid([tau(x) for x in f]) for f in word['center_frames']]
tlev={}   # GK: nonzero-frame compensation raises targets before the centre scatter
for _t,_E in word.get('target_levels',{}).items():tlev[mapping[v+int(_t)]-v]=fid([tau(x) for x in _E])
if tlev:can['target_levels']=tlev
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
        assert all(cur[r]==tlev.get(r-v,0) for r in range(v,2*v))   # GK: targets sit at their level
        for r_c,f in zip(can['centers'],can['center_frames']):
            # GK: a centre copy descends cf -> served levels (descending chain) -> lowest served level; at the defaults the
            # only served level is 0 and this is PR #433's single child of rank |cf|
            served={tlev.get(e[1]-v,0) for e in can['cut'] if e[2]==r_c}
            o=f
            for Lv in sorted(served,key=lambda x:-len(frames[x])):
                assert basis(frames[Lv]+frames[o])==tuple(frames[o]),('centre level outside the previous frame',r_c)
                if Lv!=o:
                    paid[len(frames[o])-len(frames[Lv])]+=1
                    if not(o==f and Lv==0):edges.add((o,Lv));edges.add((Lv,o))   # (cf,0),(0,cf) are added by the phase script
                    o=Lv
    for e in can[part]:
        rs=[e[1]]+([e[2]] if e[0]=='add' else [])
        for r in rs:climb(r,e[-1]);incidences+=1
for r,f in enumerate(can['final']):climb(r,f)
assert dict(paid)=={int(r):x for r,x in word['report']['local_profile'].items()}
# GK: entrances lower the helper climb by their rank; centre descents may stop above frame zero
if not word.get('start_extra') and not word.get('target_levels'):assert sum(r*x for r,x in paid.items())==9*can['R']+240*8+72
else:assert sum(r*x for r,x in paid.items())==sum(int(r)*x for r,x in word['report']['local_profile'].items())
can['local_profile']=dict(sorted(paid.items()));can['edges']=sorted(edges)
cp=OUT/'CANONICAL-WORD.json.gz';cp.write_bytes(gzip.compress(json.dumps(can,sort_keys=True,separators=(',',':')).encode(),mtime=0))

def engine(name):
    p=Path('work/pr361/code/engines')/(name+'.py');s=importlib.util.spec_from_file_location('hamming_'+name,p)
    m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
M,M2=engine('moment'),engine('base_two_moment');m,W=73,word['report'].get('live',12720)   # GK: unhosted stock of the word
HG={int(r):z for r,z in word['report']['global_profile'].items()}
root=M.certify(HG,m,W,True);b=Q(int(Q(root['lower'])*10**18),10**18);grid=Q(1,10**18)
assert M.moment(HG,m,W,b,True)[1]<1<M.moment(HG,m,W,b+grid,True)[0]
fallback=32*m*m*sum(HG.values())
def second(a):
    lo,hi=M2.moment(m,W,list(HG.items()),a)
    l2,h2=M2.moment(m,W,[(1,fallback)],a)
    return lo+l2/10**16,hi+h2/10**16
assert second(b)[1]<1<second(b+grid)[0]
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
        'prospective_complex_b':str(b),'prospective_b_float':float(b),
        'prospective_gain_percent':float(100*(b/Q(999388595603943,10**18)-1)),
        'two_rational_moment_engines':True,'next_b_grid_rejected':True,
        'remaining':['new general scalar-interface proof integration','exact phase and emitted local/global program','finite invoice and outer assembly'],
        'scope':'Substantial new scalar-network candidate. All parameter values remain prospective until the expanded scalar interface and complete phase-aware supplier are admitted.',
        'seconds':time.monotonic()-start}
(OUT/'SCALAR-FRAME-AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
print('PASS prospective b',float(b),'gain',report['prospective_gain_percent'],'percent; seconds',report['seconds'],flush=True)
