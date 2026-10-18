"""Literal truth-table decoding/fiber audit; imports no new producer code."""
from fractions import Fraction
from pathlib import Path
import hashlib
import importlib.util
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def require(ok,message):
    if not ok:
        raise ValueError(message)


def rational_rank(rows):
    a=[[Fraction(x) for x in row] for row in rows]
    if not a:
        return 0
    rank=0
    for col in range(len(a[0])):
        found=next((j for j in range(rank,len(a)) if a[j][col]),None)
        if found is None:
            continue
        a[rank],a[found]=a[found],a[rank]
        leading=a[rank][col]
        a[rank]=[x/leading for x in a[rank]]
        for j in range(rank+1,len(a)):
            factor=a[j][col]
            a[j]=[x-factor*y for x,y in zip(a[j],a[rank])]
        rank+=1
    return rank


def binary_rank(rows):
    rows=list(rows);rank=0
    for bit in range(max(rows,default=0).bit_length()):
        found=next((j for j in range(rank,len(rows)) if rows[j] >> bit & 1),None)
        if found is None:
            continue
        rows[rank],rows[found]=rows[found],rows[rank]
        for j in range(rank+1,len(rows)):
            if rows[j] >> bit & 1:
                rows[j]^=rows[rank]
        rank+=1
    return rank


def run(path=None):
    for r in json.loads((HERE/'SOURCES.json').read_text())['files']:
        if r['usage']=='input':
            raw=(ROOT/r['path']).read_bytes()
            require(hashlib.sha256(raw).hexdigest()==r['sha256'],'independent source SHA')
            require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==r['git_blob'],'independent source blob')
    spec=importlib.util.spec_from_file_location('r036_independent_geometry',ROOT/'research/eisenstein-clique-copy-bound/geometry.py')
    geometry=importlib.util.module_from_spec(spec);spec.loader.exec_module(geometry)
    reps,images,adjacent,_,_=geometry.geometry()
    require(rational_rank(reps)==8,'full real span')
    prices={};cases=0;receivers=0;fibers=0;cost_sets={};transcript=hashlib.sha256()
    trees=json.loads((Path(path) if path else HERE/'SMALL-TREES.json').read_text())
    for name,tree in sorted(trees.items()):
        owners=[t for t,b in enumerate(tree['demands']) for _ in range(b)]
        n=len(owners)
        require(n<=16,'declared exhaustive truth-table size')
        nodes={tuple(node['history']):node for node in tree['nodes']}
        require(len(nodes)==len(tree['nodes']) and () in nodes,'literal public tree')
        leaf_inputs={};leaf_rows={};seen={t:{} for t,b in enumerate(tree['demands']) if b}
        own={t:sum(1 << j for j,u in enumerate(owners) if u==t) for t in seen}
        side={t:sum(1 << j for j,u in enumerate(owners) if u!=t and not (adjacent[t] >> u & 1)) for t in seen}
        costs=set()
        for x in range(1 << n):
            history=();cost=0;equations=[]
            while not nodes[history].get('terminal',False):
                node=nodes[history]
                rows=node['rows'];sources=tuple(node['sources'])
                require(0<=node['constant']<1 << len(rows),'constant width')
                require(all(type(row) is int and 0<=row<1 << n for row in rows),'linear payload masks')
                actual={owners[j] for row in rows for j in range(n) if row >> j & 1}
                require(actual<=set(sources),'literal source declarations')
                if sources not in prices:
                    rank=rational_rank([r for t in sources for r in (reps[t],images[t])])
                    require(rank%2==0,'even physical pairing dimension')
                    prices[sources]=rank//2
                cost+=len(rows)*prices[sources]
                answer=sum((bin(row&x).count('1')%2) << k for k,row in enumerate(rows))^node['constant']
                equations.extend((row,((answer^node['constant']) >> k)&1) for k,row in enumerate(rows))
                history+=(answer,)
                require(history in nodes,'missing paid-answer edge')
            leaf_inputs.setdefault(history,[]).append(x)
            leaf_rows[history]=equations
            require(cost>=n,'independent pathwise floor')
            costs.add(cost)
            for t in seen:
                key=(history,x&side[t]);value=x&own[t]
                require(key not in seen[t] or seen[t][key]==value,'receiver-conflict witness')
                seen[t][key]=value
                receivers+=1
            transcript.update((name+':'+str(x)+':'+str(history)+':'+str(cost)+'\n').encode())
            cases+=1
        for history,inputs in leaf_inputs.items():
            equations=leaf_rows[history]
            rank=binary_rank([row for row,_ in equations])
            require(all(all(bin(row&x).count('1')%2==rhs for row,rhs in equations) for x in inputs),'literal affine equations')
            require(len(inputs)==1 << (n-rank),'exact whole leaf fiber cardinality')
            require(len(inputs)==1 << binary_rank([x^inputs[0] for x in inputs]),'affine closure')
            fibers+=1
        cost_sets[name]=sorted(costs)
    return dict(status='PASS_INDEPENDENT_ADAPTIVE_AFFINE',literal_inputs=cases,
                receiver_conflict_checks=receivers,exact_leaf_fibers=fibers,
                actual_rational_support_prices=len(prices),cost_sets=cost_sets,
                transcript_sha256=transcript.hexdigest())


if __name__=='__main__':
    require(len(sys.argv)==1,'unknown arguments')
    print(json.dumps(run(),sort_keys=True))
