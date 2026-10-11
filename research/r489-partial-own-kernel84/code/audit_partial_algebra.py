"""Independent exact read-back of partial-own loads and selected kernel relations.
Imports no construction or kernel helper code. Prepared by OpenAI Codex.
"""
import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from fractions import Fraction as Q
from pathlib import Path

if not __debug__:
    raise RuntimeError('This exact algebra audit requires assertions enabled.')

p=argparse.ArgumentParser()
p.add_argument('--base',type=Path,required=True,help='Changed ungauged partial-own base word')
p.add_argument('--word',type=Path,required=True,help='Selected kernel word before frame retiming')
p.add_argument('--selection',type=Path,required=True)
p.add_argument('--original-base',type=Path,required=True,help='Pinned original ungauged PR433 full word')
p.add_argument('--original-selection',type=Path,required=True,help='Pinned PR484 gauge80-kernel42 selection')
p.add_argument('--retimed-word',type=Path,help='Optional frame-only successor; the entire derived prelude is checked unchanged')
p.add_argument('--out',type=Path,required=True);a=p.parse_args()
def read(p):
    raw=p.read_bytes();return json.loads(gzip.decompress(raw) if p.suffix=='.gz' else raw)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sp(f):
    s={0}
    for v in f:s|={x^v for x in tuple(s)}
    return s
def op(e,rows):
    t=e[1]
    if e[0]=='scale':
        q=Q(e[2],e[3]);assert q;rows[t]={j:q*x for j,x in rows[t].items()}
    else:
        assert e[0]=='add';s=e[2];q=Q(e[3],e[4]);assert s!=t
        for j,x in list(rows[s].items()):
            r=rows[t].get(j,Q(0))+q*x
            if r:rows[t][j]=r
            else:rows[t].pop(j,None)
def inverse(e):
    r=e[:]
    if r[0]=='add':r[3]=-r[3]
    else:r[2],r[3]=r[3],r[2]
    return r
def dual(e):
    r=inverse(e)
    if r[0]=='add':r[1],r[2]=r[2],r[1]
    return r
def ident(n):return [{r:Q(1)} for r in range(n)]
def matrix_rank(rows):
    d={}
    for row in rows:
        r={k:Q(v) for k,v in row.items() if v}
        while r:
            k=min(r)
            if k not in d:
                q=r[k];d[k]={j:v/q for j,v in r.items()};break
            q=r[k]
            for j,v in d[k].items():
                z=r.get(j,Q(0))-q*v
                if z:r[j]=z
                else:r.pop(j,None)
    return len(d)
def determinant(mat):
    m=[list(map(Q,row)) for row in mat];d=Q(1);n=len(m)
    for j in range(n):
        k=next(i for i in range(j,n) if m[i][j])
        if k!=j:m[k],m[j]=m[j],m[k];d=-d
        v=m[j][j];d*=v
        for i in range(j+1,n):
            q=m[i][j]/v
            m[i]=[x-q*y for x,y in zip(m[i],m[j])]
    return d
def dyadic(q):return q.denominator&(q.denominator-1)==0

base=read(a.base);word=read(a.word);sel=read(a.selection);n=240+base['report']['R'];assert n==800
baseline_path=a.original_base
old=read(baseline_path)
preserved=['B','center_frames','centers','cut','ports','precondition','root_lines','scatter']
assert all(base[k]==old[k] for k in preserved)
assert len(base['A'])==2680 and len(old['A'])==2736
root=base['root_lines'];gram=[[Q(sum(x*y for x,y in zip(r,s)),2) for s in root] for r in root]

# Replay all clean source coefficients through actual A and inspect the first
# load of every fixed own-block register; no constructor state is trusted.
rows=[{i:Q(1)} if i<120 else {} for i in range(n)];loads={}
for i,e in enumerate(base['A']):
    if e[0]=='add' and 240<=e[1]<352 and e[1] not in loads:
        assert not rows[e[1]] and Q(e[3],e[4])==1
        assert len(rows[e[2]])==2 and len(sp(e[-1]))==4
        loads[e[1]]=dict(event=i,source=e[2],frame=e[-1],clean_coefficients=dict(rows[e[2]]))
    op(e,rows)
assert len(loads)==112
own_targets={}
for e in base['B']:
    if e[0]=='add' and 240<=e[2]<352:
        assert 120<=e[1]<240 and Q(e[3],e[4])==Q(-1,2)
        h,t=e[2],e[1]-120;assert h not in own_targets;own_targets[h]=t
        t_support={j for j,x in enumerate(root[t]) if x}
        expected={s:gram[t][s] for s in range(120) if s!=t and gram[t][s] and {j for j,x in enumerate(root[s]) if x}==t_support}
        assert rows[h]==expected,('own transfer',h,t)
assert len(own_targets)==112
by_block=defaultdict(list)
for h in loads:
    sources=tuple(sorted(loads[h]['clean_coefficients']))
    block=tuple(j for j,x in enumerate(root[sources[0]]) if x)
    assert all(tuple(j for j,x in enumerate(root[s]) if x)==block for s in sources)
    parity=sum(root[sources[0]][j]<0 for j in block)%2
    assert all(sum(root[s][j]<0 for j in block)%2==parity for s in sources)
    by_block[block,parity].append(h)
det_hist=Counter();T_witness=[]
for (block,parity),hs in sorted(by_block.items()):
    assert len(hs)==4
    srcs=sorted({s for h in hs for s in loads[h]['clean_coefficients']});assert len(srcs)==4
    T=[[loads[h]['clean_coefficients'].get(s,Q(0)) for s in srcs] for h in hs]
    det=determinant(T);assert det and dyadic(det) and dyadic(1/det)
    det_hist[str(det)]+=1
    T_witness.append(dict(block=block,parity=parity,helpers=hs,sources=srcs,matrix=[[str(q)for q in r]for r in T],determinant=str(det)))
assert len(T_witness)==28

# Exact complete dirty-response columns of the modified base, including its
# target inverse basis. Recompute; no old response columns are transplanted.
responses=ident(n)
for e in base['A']+base['cut']+base['B']:op(e,responses)
dirty=[{} for _ in range(n)]
for r in range(120,240):dirty[r]={j:q for j,q in responses[r].items() if j>=240}
for e in base['precondition']:op(e,dirty)
columns=[{} for _ in range(560)]
for t in range(120,240):
    for h,q in dirty[t].items():columns[h-240][t-120]=q
first={}
for e in base['A']+base['B']:
    for r in (e[1:3] if e[0]=='add' else e[1:2]):
        if r>=240:first.setdefault(r-240,sp(e[-1]))
prefix=word['A'][:-len(base['A'])];assert word['A'][-len(base['A']):]==base['A']
assert all(word[k]==base[k] for k in preserved)
gauges={int(h):f for h,f in sel['gauge'].items()}
origsel=read(a.original_selection)
assert sel['gauge']==origsel['gauge'] and sel['kernel'][:len(origsel['kernel'])]==origsel['kernel']
assert len(gauges)==80
pivots={h for c in sel['kernel']for h in c['pivots']};donors={h for c in sel['kernel']for h in c['donors']}
assert not pivots&donors and not (pivots|donors)&set(gauges)
assert len(pivots)==sum(len(c['pivots'])for c in sel['kernel'])
expected_entrances={str(240+h):f for h,f in gauges.items()}
kernel_ops=Counter();gauge_ops=Counter();relation_witness=[]
for e in prefix:
    assert e[0]=='add'
    target,source=e[1:3]
    if target<240:
        assert 120<=target and source-240 in gauges
        gauge_ops[(target-120,source-240,Q(e[3],e[4]),tuple(e[-1]))]+=1
    else:kernel_ops[(target-240,source-240,Q(e[3],e[4]),tuple(e[-1]))]+=1
expected_gauges=Counter((t,h,-q,tuple(f)) for h,f in gauges.items() for t,q in columns[h].items())
assert gauge_ops==expected_gauges
for ci,cl in enumerate(sel['kernel']):
    E=sp(cl['E']);ds=cl['donors'];ps=cl['pivots']
    assert matrix_rank([columns[d]for d in ds])==len(ds)
    assert all(E<=first[h]for h in ds+ps)
    for p in ps:
        expected_entrances[str(240+p)]=cl['E'];relation={}
        for d in ds:
            matches=[(key,count)for key,count in kernel_ops.items()if key[0]==d and key[1]==p]
            assert len(matches)<=1
            if matches:
                (dd,pp,q,ef),count=matches[0];assert count==1 and sp(ef)==E and dyadic(q)
                relation[d]=-q;del kernel_ops[dd,pp,q,ef]
        all_t=set(columns[p])|{t for d in relation for t in columns[d]}
        assert all(columns[p].get(t,Q(0))==sum(q*columns[d].get(t,Q(0))for d,q in relation.items())for t in all_t)
        relation_witness.append(dict(class_index=ci,pivot=p,entrance=cl['E'],donor_coefficients={str(d):str(q)for d,q in relation.items()}))
assert not kernel_ops and word['start_extra']==expected_entrances

# Independent full scalar word on every original source, target, and helper
# dirt column, for both the word and same-order inverse-transpose reflection.
main=word['A']+word['cut']+word['B'];m=ident(n)
for e in main:op(e,m)
dirty=[{} for _ in range(n)]
for t in range(120,240):dirty[t]={j:q for j,q in m[t].items()if j>=240}
for e in word['precondition']:op(e,dirty)
enter=set(map(int,word['start_extra']));assert all(not enter&set(dirty[t])for t in range(120,240))
comp=[['add',t,h,-q.numerator,q.denominator,[]] for t in range(120,240)for h,q in sorted(dirty[t].items())]
cleanup=[inverse(e)for e in reversed(word['A']+word['B'])if not 120<=e[1]<240]
assert [e[:-1]for e in cleanup]==[e[:-1]for e in word['cleanup']]
program=word['precondition']+comp+main+cleanup
for back in (False,True):
    m=ident(n);want=ident(n)
    for e in program:op(dual(e)if back else e,m)
    for t in range(120):want[t if back else t+120][t+120 if back else t]=Q(-1 if back else 1)
    assert m==want
for e in program:
    q=Q(e[3],e[4])if e[0]=='add'else Q(e[2],e[3]);assert dyadic(q)
    if e[0]=='scale':assert dyadic(1/q)

extra=relation_witness[42:]
retiming=None
if a.retimed_word:
    retimed=read(a.retimed_word)
    assert set(retimed)==set(word)
    changed={}
    for k in word:
        if k in ('A','B'):
            assert [e[:-1]for e in retimed[k]]==[e[:-1]for e in word[k]],('retimed scalar payload/order',k)
            changed[k]=sum(e!=f for e,f in zip(word[k],retimed[k]))
        elif k=='report':
            assert set(word[k])==set(retimed[k])
            for field in word[k]:
                if field not in ('local_profile','global_profile'):assert word[k][field]==retimed[k][field],('retimed report',field)
        else:assert word[k]==retimed[k],('retimed fixed boundary',k)
    assert retimed['A'][:len(prefix)]==word['A'][:len(prefix)],'entire gauge and kernel prelude must remain unchanged'
    retiming=dict(word_sha256=sha(a.retimed_word),full_prelude_events=len(prefix),
                  full_prelude_including_frames_unchanged=True,changed_frame_events=changed,
                  scalar_payloads_and_order_identical=True,all_boundaries_and_cleanup_identical=True,
                  scope='Frame chronology/accounting is checked separately on native emitted streams.')
report=dict(status='PASS_INDEPENDENT_PARTIAL_OWN_BASES_KERNEL_RELATIONS_AND_ALL_DIRT',
            inputs={str(p):sha(p)for p in [a.base,a.word,a.selection,baseline_path,a.original_selection]+([a.retimed_word]if a.retimed_word else [])},
            preserved_base_fields=preserved,baseline_A_events=len(old['A']),partial_A_events=len(base['A']),
            own_loads=112,own_loads_rank=2,own_tetrad_basis_count=28,own_basis_determinants=dict(det_hist),
            own_clean_Gram_rows_reconstructed=112,original_gauges=80,original_kernel_pivots=42,
            additional_kernel_pivots=len(extra),new_classes=[dict(entrance=cl['E'],donors=len(cl['donors']),pivots=len(cl['pivots']))for cl in sel['kernel'][len(origsel['kernel']):]],
            all_kernel_donor_sets_exactly_independent=True,all_kernel_relations_checked=len(relation_witness),
            prefix_scalar_events=len(prefix),gauge_compensation_events=sum(gauge_ops.values()),
            kernel_events=len(prefix)-sum(gauge_ops.values()),entering_helpers=len(enter),entrance_rank=sum(len(f)for f in word['start_extra'].values()),
            scalar_columns_each_orientation=800,scalar_records=len(program),frame_zero_compensation=len(comp),all_entering_dirty_compensation_zero=True,
            all_coefficients_dyadic=True,all_scale_inverses_dyadic=True,retiming=retiming,
            scope='Exact rational algebra and raw scalar word only; does not assert Gaussian/wrapper/physical hosting/invoice/all-size admission.')
a.out.mkdir(exist_ok=False)
(a.out/'ALGEBRA.json').write_text(json.dumps(report,indent=2)+'\n')
(a.out/'OWN-BASES.json').write_text(json.dumps(T_witness,indent=2)+'\n')
(a.out/'KERNEL-RELATIONS.json').write_text(json.dumps(relation_witness,indent=2)+'\n')
print(json.dumps(report,indent=2))
