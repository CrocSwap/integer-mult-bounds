"""Independent exact scalar/envelope/terminal audit from a raw DAG alone."""
from pathlib import Path
from itertools import combinations
import argparse
import hashlib
import json
import struct


def run(dag):
    raw=Path(dag).read_bytes();h,v,n,q=struct.unpack_from('<4I',raw);at=16
    def take(code,count):
        nonlocal at
        values=struct.unpack_from('<'+str(count)+code,raw,at);at+=struct.calcsize(code)*count
        return values
    flat=take('I',2*n);args=list(zip(flat[::2],flat[1::2]));core,cover=take('Q',n),take('Q',n)
    roots,kinds,active=take('I',q),take('I',q),take('B',n);assert at==len(raw)
    triples=list(combinations(range(h),3));assert len(triples)==v
    support={};degrees=[0]*n;classes={};centers=[]
    for x in range(1,n):
        if not active[x]:continue
        classes[core[x].bit_count()]=classes.get(core[x].bit_count(),0)+1
        if args[x][0]:
            a,b=args[x];assert a<x and b<x and not support[a]&support[b]
            support[x]=support[a]|support[b];degrees[a]+=1;degrees[b]+=1
            assert core[x]==core[a]&core[b] and cover[x]==cover[a]|cover[b]
            assert core[x].bit_count() in (1,2)
        else:
            assert 1<=x<=v and core[x]==cover[x]==sum(1<<i for i in triples[x-1])
            support[x]=1<<(x-1)
    scatter=[0]*v
    for j,node in enumerate(roots):
        point=(core[node]&-core[node]).bit_length()-1
        if kinds[j]:
            target=[i for i,t in enumerate(triples) if point in t]
            expected=sum(1<<i for i in target);centers.append(node)
            assert core[node].bit_count()==1 and cover[node]==(1<<h)-1 and degrees[node]==0
        else:
            absent=((1<<h)-1)^cover[node];assert absent.bit_count()==2
            excluded=[i for i in range(h) if absent>>i&1]
            target=[triples.index(tuple(sorted([point,*excluded])))]
            expected=sum(1<<i for i,t in enumerate(triples) if point in t and not(set(t)&set(excluded)))
        assert support[node]==expected
        for i in target:scatter[i]^=support[node]
    assert scatter==[1<<i for i in range(v)] and len(centers)==len(set(centers))==h
    return dict(h=h,dag_sha256=hashlib.sha256(raw).hexdigest(),original_core_classes=classes,
                source_triples=v,center_terminal_count=len(centers),no_center_middle_consumers=True,
                all_output_supports_exact=True,JLV_identity=True,all_additions_disjoint=True,
                audit_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--dag',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    result=run(a.dag);Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PASS exact scalar/original-envelope/retained-center audit',result['h'])
