#!/usr/bin/env python3
"""Exact complete-caller constant-field composition for the fused LOCAL.

Source #8027 + #8035 caller; validates the fused 630-row normalized map and
its transpose, all 36 single placements, and the F2 span of all placement
matrices. Any nonzero error on constant binary fields is an admitted supplier
counterexample, including the specified retained power-268 suffix. This does
not identify reachable top-level integer operands or prove physical adjoints.
"""
from pathlib import Path
from collections import Counter
import gzip,hashlib,json
import sys

ROOT=Path(__file__).resolve().parent
ORIG=ROOT/'pinned'/'strong-bit.json.gz'
CALLER=ROOT/'pinned'/'EFREE-CALLER.json.gz'
EDIT=ROOT/'pinned'/'ONE-RESIDUAL.json.gz'
def load(path,digest):
    raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==digest
    return json.loads(gzip.decompress(raw))
g=load(ORIG,'74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326')
c=load(CALLER,'757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b')
f=load(EDIT,'7fa5589301124788237a569c3c0bbc0783f70efd840b15238300b8a2d5ab1cd7')
assert all(g[k]==f[k] for k in g if k!='program')
assert g['public']==630 and len(g['program'])==39600 and len(f['program'])==39605

def forward(data):
    charts=dict(enumerate(data['start']));v={i:1<<i for i in charts};clears={}
    for op,d,*args in data['program']:
        if op=='INIT':assert d not in charts;charts[d]=args[0];v[d]=0
        elif op=='ADD':s,chart=args;assert charts[d]==chart==charts[s];v[d]^=v[s]
        elif op=='SWAP':s,=args;charts[d],charts[s]=charts[s],charts[d];v[d],v[s]=v[s],v[d]
        elif op=='MOVE':src,dst=args;assert charts[d]==src;charts[d]=dst
        elif op=='CLEAR':assert charts.pop(d)==args[0];clears[d]=(args[0],v.pop(d))
        else:raise ValueError(op)
    assert charts==dict(enumerate(data['final'])) and len(clears)==3433
    return [v[i] for i in range(630)],clears

def reverse(data):
    charts=dict(enumerate(data['final']));v={i:1<<i for i in charts}
    for op,d,*args in reversed(data['program']):
        if op=='CLEAR':assert d not in charts;charts[d]=args[0];v[d]=0
        elif op=='ADD':s,chart=args;assert charts[d]==chart==charts[s];v[s]^=v[d]
        elif op=='SWAP':s,=args;charts[d],charts[s]=charts[s],charts[d];v[d],v[s]=v[s],v[d]
        elif op=='MOVE':src,dst=args;assert charts[d]==dst;charts[d]=src
        elif op=='INIT':assert charts.pop(d)==args[0];v.pop(d)
        else:raise ValueError(op)
    assert charts==dict(enumerate(data['start']))
    return [v[i] for i in range(630)]

original,oldclears=forward(g);fused,newclears=forward(f)
assert original==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(630)]
assert [i for i,(x,y) in enumerate(zip(original,fused,strict=True)) if x!=y]==[130]
assert original[130]^fused[130]==1<<38
for name,data,rows in [('original',g,original),('fused',f,fused)]:
    columns=reverse(data)
    assert all(((rows[o]>>i)&1)==((columns[i]>>o)&1) for o in range(630) for i in range(630)),name
assert len(oldclears)==len(newclears)==3433
clear_diff=[i for i in oldclears if oldclears[i]!=newclears[i]]
assert len(clear_diff)==7 and all(v for _,v in newclears.values())
D={int(k):v['dim'] for k,v in g['frames'].items()}
def hist(d):return Counter(abs(D[r[3]]-D[r[2]]) for r in d['program'] if r[0]=='MOVE')
h0,h1=hist(g),hist(f)
assert h0-h1==Counter({4:2}) and h1-h0==Counter({8:1})

# Restrict to the two root ports touched by the fused operator. Every whole
# helper owner remains an independent target in the complete source but is
# unchanged by either local map; it therefore contributes an identity block.
locals_=[k for k,row in enumerate(c['events']) if row[0]=='LOCAL']
assert len(locals_)==36 and c['roles']==38 and c['ports']==111

def execute(selected):
    s=[[1<<(2*r),1<<(2*r+1)] for r in range(38)]
    for clock,(op,*args) in enumerate(c['events']):
        if op=='LOCAL':
            stage,x,y=args
            s[y][0]^=s[x][0];s[y][1]^=s[x][1]
            if clock in selected:s[y][0]^=s[x][1]
        elif op in ('ADD','QUERY'):
            x,y=args;s[x][0]^=s[y][0];s[x][1]^=s[y][1]
        elif op=='SWAP':
            x,y=args;s[x],s[y]=s[y],s[x]
        elif op=='IDLE_ONE':pass
        else:raise ValueError(op)
    return [v for row in s for v in row]

baseline=execute(set());assert baseline==[1<<i for i in range(76)]
matrices=[];records=[]
for idx,clock in enumerate(locals_):
    rows=execute({clock});diff=[x^y for x,y in zip(rows,baseline,strict=True)]
    assert all(diff[2*r+1]==0 for r in range(38))
    assert all(diff[2*r]&sum(1<<(2*i) for i in range(38))==0 for r in range(38))
    flat=0
    for out in range(38):
        for inp in range(38):
            if diff[2*out]>>(2*inp+1)&1:flat|=1<<(38*out+inp)
    assert flat
    stage=c['events'][clock][1]
    base=0 if idx%2==0 else 19
    assert c['events'][clock][2:]==[base+1,base]
    # The unique diagonal (base+stage,base+stage) appears in no other
    # placement, yielding an explicit separating witness for every subset.
    endpoints=(base,base+stage)
    exact=sum(1<<(38*out+inp) for out in endpoints for inp in endpoints)
    assert flat==exact
    matrices.append(flat)
    outidx=next(i for i,x in enumerate(diff) if x);inpidx=(diff[outidx]&-diff[outidx]).bit_length()-1
    records.append({'index':idx,'event':clock,'stage':c['events'][clock][1],
        'local_roles':c['events'][clock][2:],
        'wrong_root_output_count':sum(bool(x) for x in diff),
        'witness':{'input':['root',inpidx//2,38 if inpidx%2 else 19],
                   'output':['root',outidx//2,38 if outidx%2 else 19]},
        'changed_matrix_bits':flat.bit_count(),
        'unique_diagonal_witness':{'input':['root',base+stage,38],
                                   'output':['root',base+stage,19]}})

# Echelonize 36 exact 38x38 placement matrices, retaining dependencies.
basis={};relations=[]
for i,original_column in enumerate(matrices):
    x=original_column;comb=1<<i
    while x:
        pivot=x.bit_length()-1
        if pivot not in basis:basis[pivot]=(x,comb);break
        a,b=basis[pivot];x^=a;comb^=b
    if not x:relations.append(comb)
assert len(basis)+len(relations)==36
# Multiple changes add without cross-products because each extra shear reads
# port 38 and writes only port 19; all unmodified caller operations are portwise.
# Check the implementation's superposition on the full 36-placement subset.
allrows=execute(set(locals_));xorflat=0
for x in matrices:xorflat^=x
expected=0
for out in range(38):
 for inp in range(38):
  if ((allrows[2*out]^baseline[2*out])>>(2*inp+1))&1:expected|=1<<(38*out+inp)
assert expected==xorflat

def all_root_rows(selected,transpose=False):
    """All 4,218 independent root input/output variables, no truncation."""
    values=[[1<<(111*r+p) for p in range(111)] for r in range(38)]
    events=list(enumerate(c['events']))
    if transpose:events.reverse()
    for clock,(op,*args) in events:
        if op=='LOCAL':
            stage,x,y=args
            if not transpose:
                for p in range(111):values[y][p]^=values[x][p]
                if clock in selected:values[y][19]^=values[x][38]
            else:
                if clock in selected:values[x][38]^=values[y][19]
                for p in range(111):values[x][p]^=values[y][p]
        elif op in ('ADD','QUERY'):
            x,y=args
            if transpose:x,y=y,x
            for p in range(111):values[x][p]^=values[y][p]
        elif op=='SWAP':
            x,y=args;values[x],values[y]=values[y],values[x]
        elif op=='IDLE_ONE':pass
        else:raise ValueError(op)
    return [r for row in values for r in row]

def expect_complete(selected,transpose=False):
    selected_matrices=0
    for i,clock in enumerate(locals_):
        if clock in selected:selected_matrices^=matrices[i]
    for role in range(38):
      for port in range(111):
        row=1<<(111*role+port)
        if port==(38 if transpose else 19):
          for other in range(38):
            out,inp=(other,role) if transpose else (role,other)
            if selected_matrices>>(38*out+inp)&1:
                row^=1<<(111*other+(19 if transpose else 38))
        yield row

for clock in locals_:
    selected={clock}
    assert all_root_rows(selected)==list(expect_complete(selected))
    assert all_root_rows(selected,transpose=True)==list(expect_complete(selected,transpose=True))
for selected in (set(),set(locals_),set(locals_[::2]),set(locals_[:7])):
    assert all_root_rows(selected)==list(expect_complete(selected))
    assert all_root_rows(selected,transpose=True)==list(expect_complete(selected,transpose=True))

kernel=[]
if len(relations)<=20:
 for subset in range(1,1<<len(relations)):
    m=0
    for i,r in enumerate(relations):
     if subset>>i&1:m^=r
    k=[i for i in range(36) if m>>i&1]
    assert execute({locals_[i] for i in k})==baseline
    kernel.append(k)

out={'source_sha256':hashlib.sha256(ORIG.read_bytes()).hexdigest(),
 'caller_sha256':hashlib.sha256(CALLER.read_bytes()).hexdigest(),
 'candidate_sha256':hashlib.sha256(EDIT.read_bytes()).hexdigest(),
 'local_operator_error_row':130,'local_operator_error_input':38,
 'local_forward_transpose_checks':2,'private_clear_count':3433,
 'changed_private_clear_owners':clear_diff,'all_candidate_clears_nonzero_on_arbitrary_inputs':True,
 'changed_private_clear_details':[
    {'owner':i,'chart':newclears[i][0],
     'original_input_support':[j for j in range(630) if oldclears[i][1]>>j&1],
     'candidate_input_support':[j for j in range(630) if newclears[i][1]>>j&1]}
    for i in clear_diff],
 'deleted_paid_ranks':{'4':2},'added_paid_ranks':{'8':1},
 'local_placements':records,'placement_matrix_rank':len(basis),'placement_kernel_dimension':len(relations),
 'full_root_input_variables':4218,'separate_helper_input_variables':14688,
 'single_placement_full_root_forward_and_reverse_replays':36,
 'full_root_subset_controls':4,
 'explicit_separating_coordinate':'at stage s and lane base b, input (root,b+s,38), output (root,b+s,19)',
 'enumerated_nonzero_cancelling_subsets':len(kernel) if len(relations)<=20 else None,
 'kernel_basis':[[i for i in range(36) if r>>i&1] for r in relations],
 'maximum_cancelled_placements':max(map(len,kernel),default=0) if len(relations)<=20 else None,
 'largest_cancelling_examples':sorted(kernel,key=lambda x:-len(x))[:10],
 'power268_retention':{'suffix_rank':127,'count':267,'minimum_first_factor_target_rank':4,
                     'all_first_factor_targets_retained':4*127**267>=15**268},
 'scope':'exact constant binary address-field subclass of the complete arbitrary-field supplier; original 36-call role schedule, 111 ports and all unchanged helper outputs; no physical top-level operand reachability claim'}
print(json.dumps(out,indent=2))
print('PASS_ALL_36_FUSION_COMPOSITIONS_AND_TRANSPOSE',file=sys.stderr)
