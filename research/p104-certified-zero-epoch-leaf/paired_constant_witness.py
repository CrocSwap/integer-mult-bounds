#!/usr/bin/env python3
"""Two explicit retained-input kernel vectors for simultaneous paired faults.

For the all-constant data subclass, every completed native lower-factor job is
identity on its field. Recoding by invertible maps before or after the two
faults cannot make a singular full-state map invertible. This does not rule out
extra clean storage, new communication, changed target domains, or nonconstant
and redesigned schedules.
"""
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from constant_nested_witness import c,g,inner,n,q,suffix,cut

assert 4*suffix >= cut

# Native-local kernel vectors for one-export variants, independently replayed
# through the actual complete caller below. Each set contains actual top-level
# productive tags, not local 630-row indices.
a = [('root',1,92),('root',1,99)] + [('helper',4,i) for i in (231,428,433,434,435,448,449,473,516,582)]
b = [('root',20,63)] + [('helper',5,i) for i in (222,230,362,367,368,369)]
assert not set(a)&set(b)

def caller(changes, ones):
    root=[[0]*q for _ in range(c['roles'])]
    helper={k:[0]*(n-2*q) for k,e in enumerate(c['events']) if e[0]=='LOCAL'}
    for kind,x,y in ones:
        if kind=='root': root[x][y]^=1
        else: helper[x][y-2*q]^=1
    boundary={}
    for clock,(op,*args) in enumerate(c['events']):
        if op=='LOCAL':
            stage,x,y=args; inp=root[x]+root[y]+helper[clock]
            out,_=inner(inp,changes.get(clock,'native'))
            root[x]=out[:q];root[y]=out[q:2*q];helper[clock]=out[2*q:]
            if clock in changes:
                boundary[clock]={'input_ones':[i for i,v in enumerate(inp) if v],
                                 'output_ones':[i for i,v in enumerate(out) if v]}
        elif op in ('ADD','QUERY'):
            x,y=args;root[x]=[u^v for u,v in zip(root[x],root[y],strict=True)]
        elif op=='SWAP':
            x,y=args;root[x],root[y]=root[y],root[x]
        elif op=='IDLE_ONE': pass
        else: raise AssertionError(op)
    result={('root',r,i):v for r,row in enumerate(root) for i,v in enumerate(row)}
    result.update({('helper',k,i+2*q):v for k,row in helper.items() for i,v in enumerate(row)})
    return {k for k,v in result.items() if v},boundary

results={}
for name,ones in [('first',a),('second',b),('xor',a+b)]:
    before,_=caller({},ones); after,boundary=caller({4:'a',5:'b'},ones)
    assert before==set(ones) and after==set()
    results[name]={'input_tags':ones,'native_nonzero_outputs':len(before),
                   'changed_nonzero_outputs':len(after),'fault_boundaries':boundary}
assert len(a)==12 and len(b)==7
print(json.dumps({'changed_local_events':{'4':'a (remove clock 10039)',
                                         '5':'b (remove clock 10036)'},
                  'all_factors':'rank-127 suffix repeated 267; all first-factor ports retained',
                  'independent_kernel_vectors':2,'results':results},indent=2))
print('PASS_RETAINED_PAIRED_KERNELS')
