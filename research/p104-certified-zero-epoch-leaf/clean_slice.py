#!/usr/bin/env python3
"""A preexisting omitted-helper slice in the pinned 268-fold source.

At one explicitly specified target suffix, 34 root roles are retained and
four rank-eight root roles and all 36 x 408 helper jobs are fresh zero. Replay the complete 36-call caller
for arbitrary binary *constant* input values in those 3,774 roots, changing
both chart-510 readouts in the first call.  This is an unpriced local tape
specialization: the unchanged tensor interpreter synchronizes all suffixes and
continues to issue the complete paid job stream.
"""
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import constant_nested_witness as z

p=z.p;g=z.g;c=z.c;q=z.q;n=z.n;dims=z.dims
# Suffix: 186 copies of a concrete rank-eight helper label and 81 of a
# concrete rank-64 root label. All products use exact Python integers.
a,b=186,81
assert a+b==267
assert c['events'][4][0]=='LOCAL'
assert abs(dims[g['final'][266]]-dims[g['start'][266]])==8
assert 1+7*len(c['diagonal'][1]['stages'])==64
suffix=8**a*64**b; cut=15**268
assert 8*suffix<cut<=15*suffix
retained_roles=[r for r,x in enumerate(c['diagonal']) if (1+7*len(x['stages']))*suffix>=cut]
assert len(retained_roles)==34 and set([0,1,19,20]) <= set(retained_roles)
assert all(abs(dims[g['final'][h]]-dims[g['start'][h]])*suffix<cut for h in range(222,n))

# Simultaneously apply both independently pinned chart-510 readout lists.
starta,rega,donora,lista=z.readouts['a']
startb,regb,donorb,listb=z.readouts['b']
assert (starta,startb)==(10037,10034) and regb not in lista
both=(list(enumerate(p[:startb]))+[(None,['INIT',regb,1])]+
      [(None,['ADD',regb,j,1]) for j in listb]+
      [(None,['INIT',rega,1])]+[(None,['ADD',rega,j,1]) for j in lista]+
      list(enumerate(p[starta+3:],starta+3)))
z.tapes['both']=both
old=sum(row[0]=='MOVE' for _,row in z.tapes['native'])
new=sum(row[0]=='MOVE' for _,row in both)
assert old-new==2

def run(first_mode):
    roots=[[(1<<(r*q+i)) if r in retained_roles else 0 for i in range(q)] for r in range(c['roles'])]
    helpers={k:[0]*(n-2*q) for k,e in enumerate(c['events']) if e[0]=='LOCAL'}
    for clock,(op,*args) in enumerate(c['events']):
        if op=='LOCAL':
            stage,x,y=args; inp=roots[x]+roots[y]+helpers[clock]
            out,_=z.inner(inp,first_mode if clock==4 else 'native')
            roots[x]=out[:q]; roots[y]=out[q:2*q]; helpers[clock]=out[2*q:]
        elif op in ('ADD','QUERY'):
            x,y=args; roots[x]=[u^v for u,v in zip(roots[x],roots[y],strict=True)]
        elif op=='SWAP':
            x,y=args; roots[x],roots[y]=roots[y],roots[x]
        elif op=='IDLE_ONE': pass
        else: raise AssertionError(op)
    return [v for row in roots for v in row]+[v for row in helpers.values() for v in row]
base=run('native');changed=run('both')
assert len(base)==18906 and base==changed
assert base[:38*q]==[(1<<i) if (i//q) in retained_roles else 0 for i in range(38*q)]
assert not any(base[38*q:])
print(json.dumps({'power':268,'floor':15,'suffix_ranks':{'8':a,'64':b},
                  'suffix_example_tags':{'rank_8':['helper',4,266], 'rank_64':['root',1,0]},
                  'suffix_power_of_two':3*a+6*b,'cutoff_bits':cut.bit_length(),
                  'root_ports_retained':len(retained_roles)*q,'root_ports_omitted':(38-len(retained_roles))*q,
                  'helper_ports_already_omitted':36*(n-2*q),
                  'arbitrary_constant_root_dimensions':len(retained_roles)*q,'output_forms_checked':len(base),
                  'changed_event':4,'removed_local_rank_one_moves':[10036,10039],
                  'removed_local_moves':old-new,
                  'remaining_obligation':'actual changed synchronized tensor schedule, ownership/cleanup, and complete paid and productive invoice'},indent=2))
print('PASS_PREEXISTING_CLEAN_ROOT_SLICE_LOCAL_ONLY')
