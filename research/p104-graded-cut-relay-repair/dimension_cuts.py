"""Certify the sharp total upward grade and two-chart sink cuts of #8027."""
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

GZIP_SHA='74e93daf2b7acf794ffb51f92f03f51556f68126d41ee13a8969bddb4cbe6326'
RAW_SHA='b096d6df2a0c4688296b13ab0cfd50fec1c7dec732819c624ddd7a745a144b69'


def rank_by_top(rows):
    pivots={}
    for r in rows:
        while r:
            p=r.bit_length()-1
            if p not in pivots:
                pivots[p]=r
                break
            r^=pivots[p]
    return len(pivots)


def rank_by_column(rows,n):
    a=[r for r in rows if r];rank=0
    for i in range(n):
        p=next((p for p in range(rank,len(a)) if a[p]>>i & 1),None)
        if p is None:continue
        a[p],a[rank]=a[rank],a[p]
        for j in range(rank+1,len(a)):
            if a[j]>>i & 1:a[j]^=a[rank]
        rank+=1
    return rank


def operator(g):
    n=g['public'];vf={i:1<<i for i in range(n)};f=dict(enumerate(g['start']));dirty=0;retired=0;edges=[]
    for k,(op,d,*a) in enumerate(g['program']):
        if op=='MOVE':
            assert f[d]==a[0]
            f[d]=a[1];edges.append((k,a[0],a[1]))
        elif op=='ADD':
            s,c=a;assert f[s]==f[d]==c;vf[d]^=vf[s]
        elif op=='INIT':assert d not in f;f[d],vf[d]=a[0],0
        elif op=='CLEAR':assert d>=n and f.pop(d)==a[0];retired+=1;dirty+=bool(vf.pop(d))
        elif op=='SWAP':
            s,=a;vf[s],vf[d]=vf[d],vf[s];f[s],f[d]=f[d],f[s]
        else:raise ValueError(op)
    assert f==dict(enumerate(g['final'])) and retired==dirty==3433
    rows=[vf[i] for i in range(n)]
    assert rows==[(1<<i)^((1<<(i-111)) if 111<=i<222 else 0) for i in range(n)]
    return rows,edges


def cut(g, rows, edges, group, second=True):
    n=g['public'];free=sum(1<<i for i,c in enumerate(g['start']) if c in group)
    wanted=[r for i,r in enumerate(rows) if g['final'][i] in group];limited=[r & ~free for r in wanted]
    rank=rank_by_top(limited)
    if second:assert rank==rank_by_column(limited,n)
    arrivals=sum(u not in group and v in group for _,u,v in edges)
    return {'inside_inputs':free.bit_count(),'inside_outputs':len(wanted),'restricted_target_rank':rank,'inbound_contacts':arrivals,'slack':arrivals-rank}


def check(path):
    raw=Path(path).read_bytes();assert sha256(raw).hexdigest()==GZIP_SHA
    unzipped=gzip.decompress(raw);assert sha256(unzipped).hexdigest()==RAW_SHA;g=json.loads(unzipped)
    rows,edges=operator(g);dims={int(c):v['dim'] for c,v in g['frames'].items()}
    layers={j:cut(g,rows,edges,{c for c,d in dims.items() if d>=j}) for j in range(1,9)}
    required=[516,627,627,627,616,616,616,505];assert [c['restricted_target_rank'] for c in layers.values()]==required
    assert all(x['slack']==0 for x in layers.values())
    ups=[dims[t]-dims[s] for _,s,t in edges if dims[s]<dims[t]];downs=[dims[s]-dims[t] for _,s,t in edges if dims[s]>dims[t]]
    assert (len(ups),sum(ups),len(downs),sum(downs))==(2776,4750,27,63)
    hubs={h:cut(g,rows,edges,{1,h},False) for h,d in sorted(dims.items()) if d==7}
    assert len(hubs)==120 and all(c['slack']==0 for c in hubs.values())
    assert hubs[531]==cut(g,rows,edges,{1,531}) and hubs[531]['inside_inputs']==0 and hubs[531]['inbound_contacts']==506
    changed=[(k,531 if k==8075 else s,t) for k,s,t in edges];assert [(s,t) for k,s,t in edges if k==8075]==[(326,1)]
    damaged=cut(g,rows,changed,{1,531});assert damaged['slack']==-1
    clean=edges+[(40000,326,531)];positive=cut(g,rows,clean,{1,531});assert positive['slack']==1
    # Restoring the actual external 6->7 contact fixes the cut exactly for the altered topology.
    restored=cut(g,rows,changed+[(40000,326,531)],{1,531});assert restored==hubs[531]
    # Grade-preserving fusions traversing identical layers are outside the isolated-reduction exclusion.
    triple=(6,7,8);assert [int(triple[0]<j<=triple[2]) for j in range(1,9)]==[int(triple[0]<j<=triple[1])+int(triple[1]<j<=triple[2]) for j in range(1,9)]
    return {'source_pr':8027,'source_commit':'fb9b6a7b0d27da1cf98430893a3016bf811e2aa4','compressed_sha256':GZIP_SHA,'expanded_sha256':RAW_SHA,'upward_events':len(ups),'downward_events':len(downs),'upward_grade':sum(ups),'downward_grade':sum(downs),'dimension_thresholds':layers,'all_120_rank_seven_hub_cuts':dict(Counter((v['inbound_contacts'] for v in hubs.values()))),'native_hub_531':hubs[531],'rerouted_hub_531':damaged,'with_external_contact_restored':restored,'native_control_with_extra_contact':positive}

if __name__=='__main__':print(json.dumps(check(sys.argv[1]),sort_keys=True,indent=2))
