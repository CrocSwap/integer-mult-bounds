#!/usr/bin/env python3
"""Exact coframed span census using the global rational relation kernel.
The kernel is propagated through every literal scalar operation; no prime
or inferred modular zero is used. Source/destination spans exclude mover.
"""
from collections import Counter,defaultdict
from fractions import Fraction as F
from functools import lru_cache
from pathlib import Path
import argparse,gzip,hashlib,json,time
ROOT=Path(__file__).resolve().parent;HERE=ROOT
SOURCE=ROOT/'inputs/WORD.json.gz'
PIN='acee323696b18914bd863d55341f92112b48d3d1dc1443c276efb6c396fcc0a9'

def need(ok,label):
    if not ok:raise ValueError(label)

@lru_cache(None)
def rational(text):return F(text)

def add(dst,src,q):
    need(dst is not src,'separate row objects')
    for i,v in src.items():
        z=dst.get(i,0)+q*v
        if z:dst[i]=z
        else:dst.pop(i,None)

def span(vectors):
    values={0}
    for v in vectors:values|={x^v for x in values}
    return sum(1<<x for x in values)

def dimension(mask):return mask.bit_count().bit_length()-1

def scalar_add(kernel,a,b,q):
    need(a!=b,'distinct ADD operands')
    for relation in kernel:
        c=relation.get(a,0)
        if c:
            z=relation.get(b,0)-q*c
            if z:relation[b]=z
            else:relation.pop(b,None)

def clear(kernel,a):
    pivot=next((i for i,k in enumerate(kernel) if k.get(a)),None)
    if pivot is None:return
    source=kernel[pivot];value=source[a]
    for i,row in enumerate(kernel):
        if i!=pivot and row.get(a):add(row,source,-row[a]/value)
    kernel.pop(pivot)

def bank_relation(kernel,a,donors,deadline):
    if not any(row.get(a) for row in kernel):
        return dict(inside=False,method='global_independent')
    allowed=set(donors)|{a};basis={}
    for i,relation in enumerate(kernel):
        if i%8==0 and time.monotonic()>deadline:raise TimeoutError
        value={j:v for j,v in relation.items() if j not in allowed}
        full=relation.copy()
        while value:
            p=max(value)
            if p not in basis:
                q=1/value[p]
                basis[p]=({j:v*q for j,v in value.items()}, {j:v*q for j,v in full.items()})
                break
            old,rep=basis[p];q=-value[p]
            add(value,old,q);add(full,rep,q)
        if not value and full.get(a):
            q=-1/full[a]
            return dict(inside=True,method='exact_kernel_projection',
                        witness={str(j):str(v*q) for j,v in full.items() if j!=a},
                        global_kernel_dim=len(kernel),projected_rank=len(basis))
    return dict(inside=False,method='exact_kernel_projection',
                global_kernel_dim=len(kernel),projected_rank=len(basis))

def controls():
    kernel=[{2:F(1)}]
    scalar_add(kernel,2,0,F(1))
    need(bank_relation(kernel,2,{0},float('inf'))['witness']=={'0':'1'},'COPY relation')
    scalar_add(kernel,0,1,F(1))
    for row in kernel:
        if row.get(0):row[0]/=2
    hit=bank_relation(kernel,2,{0,1},float('inf'))
    need(hit['witness']=={'0':'1/2','1':'-1'},'contragredient ADD/SCALE')
    need(not bank_relation(kernel,2,{0},float('inf'))['inside'],'dirty coordinate cannot disappear')
    clear(kernel,2);need(not kernel,'CLEAR kernel elimination')
    singular=[{2:F(1)}];scalar_add(singular,2,0,F(1));scalar_add(singular,0,2,F(-1))
    need(bank_relation(singular,0,set(),float('inf'))['inside'],'singular public-prefix support')
    clear(singular,2)
    need(bank_relation(singular,0,set(),float('inf'))['inside'],'independent CLEAR rank-loss support')
    return dict(copy_relation=True,add_scale_relation=True,dirty_coordinate_rejected=True,clear_elimination=True,singular_public_prefix=True,independent_clear_rank_loss=True)

def run(seconds,source=SOURCE,output=None):
    started=time.monotonic();deadline=started+seconds;tested=controls()
    raw=source.read_bytes();need(hashlib.sha256(raw).hexdigest()==PIN,'literal source pin')
    w=json.loads(gzip.decompress(raw));n=w['public'];classes=[span(f) for f in w['frames']]
    charts=w['initial']+[None]*w['owned_fields'];banks=defaultdict(set)
    for i,f in enumerate(charts):
        if f is not None:banks[classes[f]].add(i)
    kernel=[];maximum=0;records=[];hits=[];counts=Counter();last=-1;complete=False
    try:
        for event,e in enumerate(w['program']):
            last=event
            if event%128==0 and time.monotonic()>deadline:raise TimeoutError
            op,a=e[:2]
            if op=='INIT':
                need(charts[a] is None and all(not k.get(a) for k in kernel),'fresh owned INIT')
                charts[a]=e[2];banks[classes[e[2]]].add(a);kernel.append({a:F(1)})
                maximum=max(maximum,len(kernel))
            elif op=='CLEAR':
                need(charts[a]==e[2],'CLEAR chart');clear(kernel,a)
                banks[classes[e[2]]].remove(a);charts[a]=None
            elif op in ('ADD','COPY'):
                b=e[2];need(charts[a]==charts[b]==e[-1],'cocharted scalar contact')
                if op=='COPY':need(bank_relation(kernel,a,set(),deadline)['inside'],'COPY into exact zero')
                scalar_add(kernel,a,b,rational(e[3]))
            elif op=='SCALE':
                need(charts[a]==e[-1],'SCALE chart');q=rational(e[2]);need(q!=0,'invertible source scalar')
                for relation in kernel:
                    if relation.get(a):relation[a]/=q
            elif op=='MOVE':
                need(charts[a]==e[2],'MOVE chart');old,new=classes[e[2]],classes[e[3]]
                source=bank_relation(kernel,a,banks[old]-{a},deadline)
                record=dict(event=event,owner=a,owned=bool(e[4]),rank=abs(dimension(old)-dimension(new)),source_fields=len(banks[old])-1,destination_fields=len(banks[new]),source=source)
                kind='owned' if e[4] else 'public';counts[kind+'_source_'+str(source['inside'])]+=1
                if source['inside']:
                    destination=bank_relation(kernel,a,banks[new]-{a},deadline)
                    record['destination']=destination;counts[kind+'_destination_'+str(destination['inside'])]+=1
                    if destination['inside']:hits.append(record)
                records.append(record)
                banks[old].remove(a);banks[new].add(a);charts[a]=e[3]
            else:raise ValueError(op)
        complete=True;need(charts==w['final']+[None]*w['owned_fields'],'all endpoint/lifetime charts')
    except TimeoutError:pass
    result=dict(status='COMPLETE_EXACT_GLOBAL_KERNEL_RELOCATION_CENSUS' if complete else 'TIME_LIMIT_PARTIAL_KERNEL_CENSUS',source_sha256=PIN,instructions=len(w['program']),last_event=last,checked_moves=len(records),total_MOVEs=sum(e[0]=='MOVE' for e in w['program']),maximum_relation_dimension=maximum,final_relation_dimension=len(kernel),counts=dict(counts),two_sided_hits=hits,ideal_removed_paid_profile=dict(Counter(h['rank'] for h in hits)),records=records,controls=tested,seconds=time.monotonic()-started,
                coframe_model='Equal GF2 subspaces, including one duplicate source-space ID pair with ordinary rank0 normalization granted.',scope='Exact global row-relation kernel overQ. Each MOVE separately; source excludes mover; all public inputs arbitrary. A hit requires physical slot/ownership/lifetime and full invoice review. No emitted source or summed-gain admission.')
    if output is not None:output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('records','two_sided_hits')},indent=2))
    for h in hits:print('HIT',h['event'],h['owner'],h['rank'])
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=60)
    p.add_argument('--source',type=Path,default=SOURCE)
    p.add_argument('--output',type=Path)
    args=p.parse_args();run(args.seconds,args.source,args.output)
