"""Rebuild frozen T37 owners independently, without importing any constructor.

T16's frozen literal edit tuple is parsed as data; T21/T37 edits are JSON.
No optimizer, search, or root exploratory module is executed.
"""
import argparse
import ast
import copy
import gzip
import hashlib
import json
from pathlib import Path

if not __debug__:
    raise RuntimeError('Assertions must remain enabled; do not use Python -O')
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
T21=ROOT/'research/complex-t21-owners'
T37=HERE.parent
fields=('owner_replica','child','port','offset')
def read(path):
    raw=path.read_bytes()
    return json.loads(gzip.decompress(raw)if path.suffix=='.gz'else raw)
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def identity(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    args.out=args.out.resolve()
    assert not args.out.exists() and not args.out.is_relative_to(ROOT),'New output outside checkout required'
    plan_path=ROOT/'research/gauge44-frames-x/data/PLAN.json'
    roles_path=ROOT/'research/gauge44-frames-x/data/OWNERS.json.gz'
    source_py=T21/'vendor/pr870/t16/build_owners.py'
    literals={}
    for node in ast.parse(source_py.read_text()).body:
        if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            name=node.targets[0].id
            if name in ('SOURCE_PLAN_SHA256','SOURCE_OWNERS_SHA256','EDITS'):
                literals[name]=ast.literal_eval(node.value)
    assert sha(plan_path)==literals['SOURCE_PLAN_SHA256']
    assert sha(roles_path)==literals['SOURCE_OWNERS_SHA256']
    plan,source=read(plan_path),read(roles_path)
    def move(role,dest):
        role.update(dict(zip(fields,dest))if isinstance(dest,tuple)else dest)
        r,child,port=(role[k]for k in fields[:3])
        role['copy']=112*r+port
        role['family']=896*r+112*(2*plan['pairs'][str(child)]+plan['sides'][str(child)])+port
    t16=[]
    for role in source:
        for group in range(2):
            z=dict(role)
            z['replica']+=8*group
            z['owner_replica']+=8*group
            z['copy']+=896*group
            z['family']+=7168*group
            z['time']=2*role['time']+group
            t16.append(z)
    t16.sort(key=lambda z:(z['time'],z['helper']))
    bykey={(z['time'],z['helper']):z for z in t16}
    assert len(literals['EDITS'])==11
    for time,helper,width,before,after in literals['EDITS']:
        z=bykey[time,helper]
        assert tuple(z[k]for k in fields)==before and z['width']==width
        move(z,after)
    t21=copy.deepcopy(t16)
    for z in read(T21/'data/T5-OWNERS.json.gz'):
        z['replica']+=16
        z['owner_replica']+=16
        z['copy']+=1792
        z['family']+=14336
        t21.append(z)
    merged=[]
    count16=0
    for stage,replica in plan['order']:
        for group in range(3):
            r=replica+8*group
            if r>=21:continue
            if r<16:
                merged.append((2*count16,0,stage,r))
                count16+=1
            else:merged.append((2*(count16+4)-1,1,stage,r))
    order21=[(s,r)for _,_,s,r in sorted(merged)]
    at={key:i for i,key in enumerate(order21)}
    for z in t21:z['time']=at[z['stage'],z['replica']]
    t21.sort(key=lambda z:(z['time'],z['helper']))
    bykey={(z['time'],z['helper']):z for z in t21}
    edits21=read(T21/'data/EDITS.json')
    assert len(edits21)==9
    for e in edits21:
        z=bykey[tuple(e['role'])]
        assert {k:z[k]for k in fields}==e['before']
        move(z,e['after'])
    for z in t16:
        z['replica']+=21
        z['owner_replica']+=21
        z['copy']+=2352
        z['family']+=18816
    order16=[(s,r+8*g+21)for s,r in plan['order']for g in range(2)]
    edit_spec=read(T37/'EDITS.json')
    assert edit_spec['delay']==0
    decorated=[(144*i,0,s,r)for i,(s,r)in enumerate(order21)]
    decorated.extend((189*i,1,s,r)for i,(s,r)in enumerate(order16))
    order=[(s,r)for _,_,s,r in sorted(decorated)]
    assert len(order)==333 and len(set(order))==333
    # Stable subgroup projections are a consequence of this exact order.
    assert [(s,r)for s,r in order if r<21]==order21
    assert [(s,r)for s,r in order if r>=21]==order16
    at={key:i for i,key in enumerate(order)}
    roles=t21+t16
    for z in roles:z['time']=at[z['stage'],z['replica']]
    roles.sort(key=lambda z:(z['time'],z['helper']))
    before=copy.deepcopy(roles)
    bykey={(z['stage'],z['replica'],z['helper']):z for z in roles}
    assert len(bykey)==167832 and len(edit_spec['edits'])==8
    assert len({tuple(e['role'])for e in edit_spec['edits']})==8
    for e in edit_spec['edits']:
        z=bykey[tuple(e['role'])]
        assert {k:z[k]for k in fields}==e['before']
        move(z,e['after'])
    assert sum(a!=b for a,b in zip(before,roles))==8
    assert roles==read(T37/'OWNERS.json.gz')
    assert [list(k)for k in order]==read(T37/'ORDER.json')
    inputs=[plan_path,roles_path,source_py,T21/'data/T5-OWNERS.json.gz',T21/'data/EDITS.json',T37/'EDITS.json',T37/'OWNERS.json.gz',T37/'ORDER.json']
    receipt=dict(status='PASS_INDEPENDENT_FROZEN_T37_RECONSTRUCTION_NO_SEARCH',
      roles=len(roles),calls=len(order),edits=8,inherited_t16_edits=11,inherited_t21_edits=9,
      source_plan_pin_verified=True,source_owner_pin_verified=True,
      owner_content_sha256=identity(roles),order_content_sha256=identity(order),
      inputs={str(p.resolve()):sha(p)for p in inputs},
      scope='Exact frozen finite construction only. The independent owner/chart audit provides geometry; full supplier/invoice and inherited all-size assumptions are separate. Supplier ancestry admission is checked separately by the driver.')
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(receipt['status'],len(roles),'roles;',len(order),'calls; eight exact edits')

if __name__=='__main__':main()
