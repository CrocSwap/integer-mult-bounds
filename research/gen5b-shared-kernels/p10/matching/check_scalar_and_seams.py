"""Independent direct all-column F2 producer replay and changed seam checks.
Reads inert source records and matching candidate only. No upstream code execution.
"""
if not __debug__:
    raise RuntimeError('Assertions must remain enabled')
import json,hashlib,time,math,base64,gzip
from pathlib import Path
from collections import defaultdict,Counter
from fractions import Fraction
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import support
P=support.out('matching','placeholder').parent;support.materialize_word();start=time.time()
HEAD='e983fea0896b2a1d7355983674db7e9bb33a9e32'
NAMES={'word':'bitword/selected/bit/word_p10.json.gz','frames':'bitword/selected/bit/frames_p10.json.gz','graph':'bitword/selected/bit/graph_p10.json','kchron':'bitword/selected/bit/kchron_p10.json'}
input_pins={}
def verified(name):
    name=NAMES[name];raw=support.read_bytes(name)
    row=next(r for r in support.pins()['files']if r['path']==name)
    input_pins[name]=dict(git_blob=row['git_blob'],sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))
    return support.read(name)
base=verified('word');g=verified('graph');frames=verified('frames')['frames'];K=verified('kchron')
raw=(P/'word_weighted892.json').read_bytes()
assert hashlib.sha256(raw).hexdigest()=='25a0edc8c5f399fcf536b28c4e3575aa52177bb78b6078a631acb748954f0739','Candidate byte mismatch'
w=json.loads(raw)
assert set(w)==set(base) and [k for k in w if w[k]!=base[k]]==['pairs','reads']
assert w['reads']==dict(base['reads'],**{'9118':19977,'9119':19979})

def null(rows):
    A=[list(map(Fraction,r)) for r in rows];piv=[];at=0
    for col in range(20):
        found=next((i for i in range(at,len(A)) if A[i][col]),None)
        if found is None:continue
        A[at],A[found]=A[found],A[at];den=A[at][col];A[at]=[x/den for x in A[at]]
        for i in range(len(A)):
            if i!=at and A[i][col]:
                c=A[i][col];A[i]=[x-c*y for x,y in zip(A[i],A[at])]
        piv.append(col);at+=1
    return [[1 if i==j else -A[piv.index(i)][j] if i in piv else 0 for i in range(20)] for j in range(20) if j not in piv]
def det_int(rows):
    A=[list(r) for r in rows];n=len(A)
    if not n:return 1
    sign=1;previous=1
    for k in range(n-1):
        j=next((j for j in range(k,n) if A[j][k]),None)
        if j is None:return 0
        if j!=k:A[k],A[j]=A[j],A[k];sign=-sign
        pivot=A[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                numerator=A[i][j]*pivot-A[i][k]*A[k][j]
                assert numerator%previous==0
                A[i][j]=numerator//previous
            A[i][k]=0
        previous=pivot
    return sign*A[-1][-1]
old=dict(base['pairs']);new=dict(w['pairs']);alias={r:d for d,r in w['pairs']}
roles=sorted(set(range(9120))-set(alias));ids={r:1920+i for i,r in enumerate(roles)};physical=lambda r:ids[alias.get(r,r)]
gauges={e['role']:e for e in w['gauges']};ph=sorted(w['phase1']);ps=set(ph);rest=[i for i in range(len(w['ops'])) if i not in ps];order=ph+rest
times={i:j for j,i in enumerate(order)};uses=defaultdict(list)
for i in order:
    for r in w['ops'][i][:2]:uses[r].append(i)

adj=[{} for _ in range(9120)]
for r,s in zip(g['roots'],w['rootroles']):
    for t in r['targets']:adj[s][t]=adj[s].get(t,0)+1
for i in reversed(order):
    a,b,_=w['ops'][i]
    for t,c in adj[a].items():adj[b][t]=adj[b].get(t,0)+c
at=defaultdict(list)
for z in reversed(w['gauges']):at[w['reads'].get(str(z['role']),len(ph))].append(z['role'])
delivery=defaultdict(list)
for e in K['entries']:delivery[e['deliver_after_root']].append(e)
events=[];read_spans={};gate_positions={}
def read(r):
    begin=len(events)
    for t,c in adj[r].items():
        if c&1:events.append((960+t,physical(r)))
    read_spans[r]=(begin,len(events))
def gate(i):
    gate_positions.setdefault(i,len(events))
    a,b,_=w['ops'][i];events.append((physical(a),physical(b)))
for r in range(9120):
    if r not in gauges:read(r)
for source,r in w['sources'].items():events.append((physical(r),int(source)))
for i in ph:gate(i)
for root,r in zip(g['roots'],w['rootroles']):
    if root['kind']=='center':
        for t in root['targets']:events.append((960+t,physical(r)))
for j,i in enumerate(rest):
    for r in at[len(ph)+j]:read(r)
    gate(i)
for r in at[len(order)]:read(r)
for j,(root,r) in enumerate(zip(g['roots'],w['rootroles'])):
    if root['kind']=='side':
        for t in root['targets']:events.append((960+t,physical(r)))
    for e in delivery[j]:
        events.append((e['carrier'],e['passive']))
        for t in e['receivers']:events.append((960+t,e['carrier']))
for e in K['entries']:events.append((e['carrier'],e['passive']))
for i in reversed(order):gate(i)
for source,r in w['sources'].items():events.append((physical(r),int(source)))
n=1920+len(roles)
assert n==10148 and all(a!=b and 0<=a<n and 0<=b<n for a,b in events)
want=[1<<i for i in range(n)]
for t in range(960):want[960+t]^=1<<t
def replay(seq):
    rows=[1<<i for i in range(n)]
    for a,b in seq:rows[a]^=rows[b]
    return rows
assert replay(events)==want
assert replay(reversed(events))==want
assert replay(events[1:])!=want
late_controls=[]
for r in (9118,9119):
    a,b=read_spans[r];i=uses[r][0];cut=gate_positions[i]
    assert b==cut and a<b
    damaged=events[:a]+events[b:cut+1]+events[a:b]+events[cut+1:]
    assert len(damaged)==len(events) and replay(damaged)!=want
    late_controls.append(r)

# Exact changed frame-pair obligations. Existing frames only: no new basis is admitted.
detcache={}
def determinant(f):
    if f in detcache:return detcache[f]
    obj=frames[str(f)]
    if 'a' in obj:
        A=obj['a'];den=11
    else:A=obj['b'];den=9
    gram=[[den*sum(x*y for x,y in zip(a,b))-sum(a)*sum(b) for b in A] for a in A]
    det=det_int(gram)
    assert det!=0
    detcache[f]=dict(dimension=obj['dim'],gram_representation='annihilator_Ginv' if 'a' in obj else 'basis_G',clearing_factor=den,determinant=det)
    return detcache[f]
rows=[]
for d,r in w['pairs']:
    if old.get(d)==r:continue
    end=w['op_frame'][uses[d][-1]];entry=gauges[r]['frame'];D=frames[str(end)];E=frames[str(entry)]
    B=D['b'] if 'b' in D else null(D['a'])
    A=E['a'] if 'a' in E else null(E['b'])
    assert all(sum(x*y for x,y in zip(a,b))==0 for a in A for b in B)
    assert times[uses[d][-1]]<w['reads'][str(r)]==times[uses[r][0]]
    rows.append(dict(donor=d,recipient=r,physical_stream=physical(d),donor_end_frame=end,recipient_gauge_frame=entry,
       donor_last_order=times[uses[d][-1]],read_order=w['reads'][str(r)],recipient_first_order=times[uses[r][0]],
       donor_dimension=D['dim'],recipient_dimension=E['dim'],donor_nondegeneracy=determinant(end),recipient_nondegeneracy=determinant(entry),
       exact_containment=True,projector_contract='G-nondegenerate D subset E implies P_D P_E=P_E P_D=P_D; transition E-D is a G-orthogonal projector of the displayed rank',transition_rank=E['dim']-D['dim']))
report=dict(status='PASS_INDEPENDENT_WEIGHTED892_BASE_F2_AND_CHANGED_SEAMS',candidate_word_sha256=hashlib.sha256((P/'word_weighted892.json').read_bytes()).hexdigest(),
 source_head=HEAD,source_pins=input_pins,checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),dependencies='Python standard library only',
 formal_columns=n,scalar_adds=len(events),forward_all_columns=True,reverse_all_columns=True,omitted_first_compensation_rejected=True,
 late_new_recipient_read_controls_rejected=late_controls,
 changed_pairs=len(rows),unique_checked_seam_frames=len(detcache),seams=rows,
 scope='Direct base producer F2 word and new alias seams only. Installed transcript stages, integer decoder/norm, banks, finite invoice and conditional assembly are separate obligations.')
(P/'scalar_and_seams892.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='seams'},sort_keys=True))
