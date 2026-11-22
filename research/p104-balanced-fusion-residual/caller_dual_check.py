#!/usr/bin/env python3
"""Independent prefix/adjoint proof of the 36 diagonal witnesses.

The #8027 fused graph has the separately replayed local fault y19 += x38.
For constant binary address fields the paired caller's root-role operations
are linear. A forward prefix finds each actual x38 source form; an independent
reverse sensitivity pass finds each final y19 response. Their outer product is
that placement's complete error. No full local graph code or the other caller
checker is imported.
"""
from pathlib import Path
import gzip,hashlib,json,sys
HERE=Path(__file__).resolve().parent
blob=(HERE/'pinned'/'EFREE-CALLER.json.gz').read_bytes()
assert hashlib.sha256(blob).hexdigest()=='757b3523798f840bdb02028b23708c3416627a99ea09e7a3c4bcdc5cd0c7ce4b'
c=json.loads(gzip.decompress(blob));assert (c['roles'],c['ports'])==(38,111)

def propagate(events,expect=True):
    state=[1<<i for i in range(38)];prefix={}
    for clock,(op,*args) in enumerate(events):
        if op=='LOCAL':
            stage,x,y=args;prefix[clock]=(stage,x,y,state[x]);state[y]^=state[x]
        elif op in ('ADD','QUERY'):
            x,y=args;state[x]^=state[y]
        elif op=='SWAP':x,y=args;state[x],state[y]=state[y],state[x]
        elif op=='IDLE_ONE':pass
        else:raise ValueError(op)
    dual=[1<<i for i in range(38)];suffix={}
    for clock in reversed(range(len(events))):
        op,*args=events[clock]
        if op=='LOCAL':
            stage,x,y=args;suffix[clock]=dual[y];dual[x]^=dual[y]
        elif op in ('ADD','QUERY'):
            x,y=args;dual[y]^=dual[x]
        elif op=='SWAP':x,y=args;dual[x],dual[y]=dual[y],dual[x]
        elif op=='IDLE_ONE':pass
        else:raise ValueError(op)
    assert state==dual==[1<<i for i in range(38)]
    assert len(prefix)==len(suffix)==36
    seen=set();records=[]
    for clock,(stage,x,y,a) in prefix.items():
        b=suffix[clock];lane=0 if y==0 else 19
        assert (x,y)==(lane+1,lane)
        target=(1<<lane)|(1<<(lane+stage))
        assert a==b==target
        key=(lane,stage);assert key not in seen;seen.add(key)
        records.append({'event':clock,'stage':stage,'lane_base':lane,
                        'source_roles':[lane,lane+stage],
                        'affected_output_roles':[lane,lane+stage],
                        'unique_diagonal':lane+stage})
    assert seen=={(lane,stage) for lane in (0,19) for stage in range(1,19)}
    return records

rows=propagate(c['events'])
bad=[r[:] for r in c['events']];bad[0]=['ADD',0,2]
try:propagate(bad)
except AssertionError:pass
else:raise AssertionError('An edited caller was not rejected')
assert 4*127**267>=15**268
print(json.dumps({'caller_sha256':hashlib.sha256(blob).hexdigest(),
   'placement_count':len(rows),'placement_records':rows,
   'independent_unique_diagonal_count':36,'all_nonempty_subsets_rejected':True,
   'retained_factor_count':267,'retained_factor_rank':127,
   'minimum_first_factor_rank':4,'exact_retention_inequality':True,
   'mutated_caller_rejected':True,
   'scope':'constant binary field source contract; not physical address-field inverse or operand reachability'},indent=2))
print('PASS_INDEPENDENT_CALLER_PREFIX_TRANSPOSE_DIAGONAL',file=sys.stderr)
