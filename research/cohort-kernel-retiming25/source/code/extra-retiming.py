"""Source-bound rational frame retiming after the PR254 cohort transform.

The frozen plan changes no ADD or COPY instruction. All frame paths are
rebuilt, both annihilator ledgers checked, and every used cleared Gram
determinant freshly evaluated. Original source527 and PR254 notices apply;
new composition prepared with substantial OpenAI Codex assistance.
"""
from pathlib import Path
from array import array
from collections import Counter
from functools import lru_cache
import hashlib, importlib.util, json, sys

assert __debug__, 'assertions required'
HERE=Path(__file__).resolve().parent
OUT=Path(sys.argv[1]).resolve()
load=lambda p:json.loads(p.read_text())
save=lambda p,j:p.write_text(json.dumps(j,indent=2)+'\n')
sha=lambda b:hashlib.sha256(b).hexdigest()
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
M=module('retiming_integer_geometry', OUT/'upstream/loader/source_inputs/base_bit/research/paired-cube-diagonal-bit-168/references/pr168-v4/research/paired-cube-bit/check_paired_cube_bit.py')
P=module('retiming_prime_witnesses',OUT/'upstream/prime_witnesses.py')
X=OUT/'temporal/CURRENT249-EXPORT'; L=OUT/'lead'
plan=load(HERE.parent/'extra-retiming-selection.json')
raw=array('i');raw.frombytes((L/'COHORT249-RECORDS.bin').read_bytes())
assert sha(raw.tobytes())==plan['input_raw_sha256']
assert len(raw)//6==plan['source_record_count']
frames=load(X/'frames.json')['frames'];newframes=load(L/'COHORT249-FRAMES.json');frames.update(newframes)
B={int(f):r['B']for f,r in frames.items()};A={int(f):r['A']for f,r in frames.items()};D={f:len(b)for f,b in B.items()}
basis_sha=lambda b:sha(json.dumps(b,separators=(',',':')).encode())
changed={};edits=[];nextid=max(B)+1
for row in plan['entries']:
    record=row['record'];op,a,b,c,f,z=raw[6*record:6*record+6]
    assert op==1 and [a,b,c,z]==row['scalar'] and record not in changed
    assert D[f]==row['old_dimension'] and basis_sha(B[f])==row['old_basis_sha256']
    C=row['new_basis'];g=nextid;nextid+=1
    assert len(C)==row['new_dimension'] and M.rank(C,24)==len(C)
    annihilator=M.kernel(C,24)[0]
    assert len(annihilator)==24-len(C)
    B[g]=C;A[g]=annihilator;D[g]=len(C)
    newframes[str(g)]=dict(B=C,A=annihilator,dim=len(C))
    changed[record]=g
    edits.append(dict(record=record,old_frame=f,new_frame=g,old_dimension=D[f],new_dimension=D[g],basis_sha256=basis_sha(C)))
assert len(changed)==plan['selected_gate_count'] and len(changed)>0
@lru_cache(None)
def sub(a,b):
    return D[a]<=D[b] and all(M.dot(x,y)==0 for x in B[a]for y in A[b])
for row,edit in zip(plan['entries'],edits):
    old,new=edit['old_frame'],edit['new_frame']
    assert sub(old,new)if row['direction']=='maximal'else sub(new,old)
st=load(X/'249-states.json');initial={int(k):v for k,v in load(L/'COHORT249-INITIAL.json').items()};final={int(k):v for k,v in st['final'].items()}
n=st['n'];state=dict(initial);out=array('i');copied=None
def move(s,f):
    old=state[s]
    if old==f:return
    assert sub(old,f),('frame retreat',s,old,f)
    gap=D[f]-D[old];assert gap>=0
    out.extend((0,s,old,f,gap,0));state[s]=f
for k in range(0,len(raw),6):
    op,a,b,c,f,z=raw[k:k+6]
    if op==0:continue
    if op==1:
        f=changed.get(k//6,f);move(a,f);move(b,f);out.extend((op,a,b,c,f,z))
    elif op==2:
        assert copied is None and b==n;move(a,c);state[b]=f;copied=(a,b,c);out.extend((op,a,b,c,f,z))
    else:
        assert op==3 and copied==(a,b,c)and state[a]==c and state[b]==f
        out.extend((op,a,b,c,f,z));del state[b];copied=None
assert copied is None
for s,f in sorted(final.items()):move(s,f)
assert state==final
def projection(word):
    r=array('i')
    for k in range(0,len(word),6):
        op,a,b,c,f,z=word[k:k+6]
        if op:r.extend((op,a,b,c,z))
    return r.tobytes()
assert projection(raw)==projection(out),'changed scalar or COPY instruction'
def census(word):
    H=Counter()
    for k in range(0,len(word),6):
        op,a,b,c,f,z=word[k:k+6]
        if op==0 and f:H[f]+=1
        elif op==2:H[z]+=1
    return H
oldH=census(raw);H=census(out);delta=H.copy();delta.subtract(oldH);delta={r:n for r,n in delta.items()if n}
assert delta=={int(r):n for r,n in plan['expected_local_histogram_delta'].items()}
assert sum(r*n for r,n in delta.items())==0
# Independent census from ADD needs and immutable COPY requirements, ignoring
# the just-emitted MOVEs. This includes both reflected annihilator dimensions.
needs={s:[]for s in initial};copies=Counter();active=None
used=set(initial.values())|set(final.values())
for k in range(0,len(out),6):
    op,a,b,c,f,z=out[k:k+6]
    if op==1:
        needs[a].append(f)
        if b!=n:needs[b].append(f)
        else:assert active is not None
        used.add(f)
    elif op==2:
        assert active is None;active=(a,b,c);needs[a].append(c);copies[z]+=1;used.update((c,f))
    elif op==3:assert active==(a,b,c);active=None
assert active is None and copies=={22:24}
independent=Counter(copies);pairs=set()
for s,old in initial.items():
    for f in needs[s]+[final[s]]:
        assert sub(old,f) and len(A[old])-len(A[f])==D[f]-D[old]
        if D[f]>D[old]:independent[D[f]-D[old]]+=1
        pairs.add((old,f));old=f
assert independent==H
# Fresh all-used exact integer prime coverage, including inherited bases.
witnesses={};maximum_bits=0
for f in sorted(used):
    C=B[f];key=basis_sha(C)
    if key in witnesses:continue
    assert len(A[f])==24-len(C) and M.rank(C,24)==len(C)
    assert all(M.dot(x,y)==0 for x in C for y in A[f])
    sums=list(map(sum,C))
    gram=[[9*M.dot(x,y)-sums[i]*sums[j]for j,y in enumerate(C)]for i,x in enumerate(C)]
    det=P.det(gram);powers,residual=P.factor_witness(det)
    witnesses[key]=dict(dimension=len(C),cleared_gram_determinant=det,small_prime_powers=powers,remaining_factor=residual)
    maximum_bits=max(maximum_bits,abs(det).bit_length())
controls=[]
for label,fn in [('zero determinant',lambda:P.factor_witness(0)),('wrong determinant identity',lambda:P.validate_factor(7,{str(p):0 for p in P.PRIMES},1)),('excessive residual',lambda:P.validate_factor(2**80,{str(p):0 for p in P.PRIMES},2**80))]:
    try:fn()
    except AssertionError:controls.append(label)
    else:raise AssertionError('vacuous negative control: '+label)
receipt=dict(status='PASS_EXACT_PR254_POST_RETIMING_BOTH_REFLECTED_LEDGERS_AND_PRIME_COVERAGE',selected_gate_count=len(edits),input_raw_sha256=sha(raw.tobytes()),output_raw_sha256=sha(out.tobytes()),unchanged_scalar_copy_projection_sha256=sha(projection(out)),all_endpoints_unchanged=True,copy_lifetimes_unchanged=True,both_reflected_ledgers=True,local_histogram_delta=delta,histogram=dict(H),paid_calls=sum(H.values()),rank_mass=sum(r*n for r,n in H.items()),exact_frame_pairs=len(pairs),all_used_prime_witnesses=len(witnesses),maximum_determinant_bits=maximum_bits,all_remaining_factors_below_2_power_80=True,prime_controls=controls,changed_gates=edits,selection_sha256=sha((HERE.parent/'extra-retiming-selection.json').read_bytes()))
# Preserve the original kernel receipt before updating the actually paid word.
parent=load(L/'COHORT249-REPLAY.json');save(L/'PARENT-COHORT249-REPLAY.json',parent)
parent['post_retiming']=receipt;parent['new_records']=len(out)//6;parent['histogram']={str(r):n for r,n in H.items()};parent['new_rank_mass']=receipt['rank_mass']
combined=Counter({int(r):n for r,n in parent['delta'].items()});combined.update(delta)
parent['delta']={str(r):n for r,n in combined.items()if n}
(L/'COHORT249-RECORDS.bin').write_bytes(out.tobytes());save(L/'COHORT249-FRAMES.json',newframes);save(L/'COHORT249-REPLAY.json',parent)
save(L/'EXTRA-RETIMING.json',receipt);save(L/'EXTRA-PRIME-WITNESSES.json',witnesses)
print('PASS post retiming',len(edits),'gates; local delta',delta,'mass',receipt['rank_mass'],flush=True)
