#!/usr/bin/env python3
"""Independent data reconstruction of frozen chronology; no search or solver.

Reads JSON/gzip only, imports no source model, and evaluates no native circuit.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'outputs/joint-clifford-design-20261023'
WORD=SOURCE/'inputs/research/general-gaussian-contact-search/inputs/round3-word.json.gz'


def need(ok,why):
    if not ok:raise RuntimeError(why)


def canonical(rows):
    rows=list(rows);i=0
    for bit in range(17,-1,-1):
        pivot=next((j for j in range(i,len(rows)) if rows[j]>>bit&1),None)
        if pivot is None:continue
        rows[i],rows[pivot]=rows[pivot],rows[i]
        for j in range(len(rows)):
            if j!=i and rows[j]>>bit&1:rows[j]^=rows[i]
        i+=1
    return tuple(rows[:i])


def orthogonal(basis):
    rows=list(basis);pivots=[];i=0
    for bit in range(9):
        pivot=next((j for j in range(i,len(rows))if rows[j]>>bit&1),None)
        if pivot is None:continue
        rows[i],rows[pivot]=rows[pivot],rows[i]
        for j in range(len(rows)):
            if j!=i and rows[j]>>bit&1:rows[j]^=rows[i]
        pivots.append(bit);i+=1
    return [(1<<bit)|sum(((rows[j]>>bit)&1)<<pivot for j,pivot in enumerate(pivots))
            for bit in range(9)if bit not in pivots]


def mv(columns,x):
    out=0
    while x:
        bit=x&-x;out^=columns[bit.bit_length()-1];x^=bit
    return out


def inverse(columns):
    rows=[sum(((columns[j]>>i)&1)<<j for j in range(9))|(1<<(9+i))for i in range(9)]
    for i in range(9):
        pivot=next((j for j in range(i,9)if rows[j]>>i&1),None)
        need(pivot is not None,'invertible native binary warp')
        rows[i],rows[pivot]=rows[pivot],rows[i]
        for j in range(9):
            if j!=i and rows[j]>>i&1:rows[j]^=rows[i]
    return [sum(((rows[i]>>(9+j))&1)<<i for i in range(9))for j in range(9)]


def reconstruct():
    payload=json.loads(gzip.decompress(WORD.read_bytes()));c=payload['canonical']
    frames=c['frames'];nodes=[0,0];edges=[];fixed=set();current=[]
    def new(frame,freeze=False):
        i=len(nodes);nodes.append(frame)
        if freeze:fixed.add(i)
        return i
    for role,frame in enumerate(c['start']):current.append(new(frame,role<224))
    def contact(role,frame,dst=None):
        a=current[role];b=new(frame)if dst is None else dst
        edges.append((a,b,0,len(frames[frame])-len(frames[nodes[a]])))
        need(edges[-1][3]>=0,'nonnegative original paid contact')
        current[role]=b
    centres=Counter();warp_count=0
    for event in payload['programs']['forward']:
        kind=event[0]
        if kind=='scalar':
            op,frame=event[1:];refs=op[1:3]if op[0]in ('add','copy')else op[1:2]
            dst=new(frame,any(ref[0]!='L'for ref in refs))
            for typ,role in refs:
                if typ=='L':contact(role,frame,dst)
        elif kind=='warp':
            _,role,op,a,b=event;need(role[0]=='L','persistent warp owner');contact(role[1],a)
            src=current[role[1]];dst=new(b);edges.append((src,dst,op,None));current[role[1]]=dst;warp_count+=1
        elif kind=='adapter':fixed.add(current[event[2]])
        elif kind=='center':centres[event[4]]+=1
        else:need(kind in ('phase','climb'),'known chronological event')
    for role,frame in enumerate(c['final']):contact(role,frame,new(frame,role<224))
    need(len(nodes)-2==19197,'complete original node count')
    parent=list(range(len(nodes)))
    def find(x):
        while parent[x]!=x:
            parent[x]=parent[parent[x]];x=parent[x]
        return x
    zero=0
    for a,b,op,rank in edges:
        if op==0 and rank==0:
            need(nodes[a]==nodes[b],'baseline zero contact has same actual frame')
            parent[find(b)]=find(a);zero+=1
    roots=sorted({find(i)for i in range(2,len(nodes))});index={r:i for i,r in enumerate(roots)}
    group={i:index[find(i)]for i in range(2,len(nodes))}
    charts=[canonical([x|(x<<9)for x in frames[nodes[r]]]+[z<<9 for z in orthogonal(frames[nodes[r]])])for r in roots]
    frozen=sorted({group[i]for i in fixed});maps={w['op']:tuple(w['G_columns'])for w in c['warps']}
    maps.update({-op:tuple(inverse(cols))for op,cols in list(maps.items())})
    operators={}
    for op,cols in maps.items():
        inv=inverse(cols);it=[sum(((inv[j]>>i)&1)<<j for j in range(9))for i in range(9)]
        def image(v):
            x,z=v&511,v>>9;gx=mv(cols,x)
            return gx|((mv(it,x^z)^gx)<<9)
        operators[op]=tuple(image(1<<bit)for bit in range(18))
    contacts=[];dropped=0
    for a,b,op,rank in edges:
        ga,gb=group[a],group[b]
        if ga==gb and op==0:dropped+=1;continue
        contacts.append((ga,gb,op,1))
    for role in range(224,632):contacts.append((group[2+role],group[len(nodes)-632+role],0,-1))
    keys=sorted(operators);opindex={op:i for i,op in enumerate(keys)};freeze=set(frozen)
    lines=[f'{len(charts)} {len(contacts)} {len(keys)}']
    lines += [f'{int(i in freeze)} '+' '.join(map(str,chart))for i,chart in enumerate(charts)]
    lines += [' '.join(map(str,operators[op]))for op in keys]
    lines += [f'{a} {b} {opindex[op]if op else -1} {sign}'for a,b,op,sign in contacts]
    encoded='\n'.join(lines)+'\n'
    need(encoded.encode()==(SOURCE/'inputs/contracted-graph.txt').read_bytes(),'independent full source graph byte identity')
    need(all(group[a]==group[b]for a,b,op,rank in edges if op==0 and rank==0),'all baseline zero edges stay inside one assigned group')
    result={'status':'PASS_INDEPENDENT_SOURCE_GRAPH_RECONSTRUCTION_NO_SEARCH',
            'source_word_sha256':sha256(WORD.read_bytes()).hexdigest(),
            'graph_sha256':sha256(encoded.encode()).hexdigest(),'original_nodes':len(nodes)-2,
            'original_contact_rows':len(edges),'baseline_zero_paid_rows':zero,
            'dropped_internal_identity_rows':dropped,'contracted_groups':len(charts),
            'frozen_groups':len(frozen),'signed_incidences':len(contacts),'warp_rows':warp_count,
            'centres_fixed':dict(sorted(centres.items())),
            'original_to_group_sha256':sha256(json.dumps([group[i]for i in range(2,len(nodes))],separators=(',',':')).encode()).hexdigest(),
            'all_original_zero_paid_edges_preserved_under_group_assignments':True,
            'candidate_search_or_single_census_executed':False,'new_kappa':None}
    return result


if __name__=='__main__':
    result=reconstruct();path=HERE/('SOURCE-GRAPH-BINDING-OPTIMIZED.json'if sys.flags.optimize else 'SOURCE-GRAPH-BINDING.json')
    path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
