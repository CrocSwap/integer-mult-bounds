# Copyright 2026 icekylinx. Apache-2.0.
# Prepared with OpenAI GPT-6 Astra and Codex assistance; see NOTICE.
"""Rational-center extension of the aligned general-residual complex motif.
The fixed rational phase adapter permits every d except 3.

Builds a concrete scalar addition DAG, its nondegenerate binary frames, and
the unmixed carrier histogram. No historical audit suite is invoked.
"""
import sys, json, struct, array, os
from itertools import combinations
from pathlib import Path
from .cube import CubeTriple as PairedTriple
from .interval import interval_sums

def build(h, base=2, central_disjoint=0, output_prefix='complex_general', output_dir=None):
    assert h == central_disjoint == 24, "Only the selected h=d=24 construction is supported"
    d=central_disjoint
    assert 0<=d<=h
    # Odd h uses the full coordinate frame for B_i centers.
    if d:
        divisor=abs(3-d)
        assert divisor, "The disjoint-center divisor 3-d must be nonzero."
    triples=list(combinations(range(h),3)); v=len(triples)
    args=[(0,0)]; support=[0]; core=[0]; cover=[0]; types=[0]; ranks=[0]
    lookup={}; inputs={}
    for j,t in enumerate(triples):
        mask=sum(1<<a for a in t); x=len(args); inputs[t]=x
        args.append((0,0));support.append(1<<j);core.append(mask);cover.append(mask)
        types.append(1);ranks.append(1);lookup[1<<j]=x
    def add(a,b,center=None):
        if not a:return b
        if not b:return a
        assert not support[a]&support[b], "Every selected addition must be disjoint"
        s=support[a]|support[b]
        if center is None and s in lookup:return lookup[s]
        x=len(args);args.append((a,b));support.append(s)
        core.append(core[a]&core[b]);cover.append(cover[a]|cover[b])
        if center is not None:
            types.append(3 if h % 2 == 0 else 2);ranks.append(h-1 if h % 2 == 0 else h);core[x]=1<<center
            if h % 2:cover[x]=(1<<h)-1
        elif core[x].bit_count()>=2:
            types.append(1);ranks.append(s.bit_count());lookup[s]=x
        else:
            types.append(2);ranks.append(cover[x].bit_count());lookup[s]=x
        return x
    def total(xs,center=None):
        xs=[x for x in xs if x]
        while len(xs)>1:
            xs=[add(xs[i],xs[i+1],center) if i+1<len(xs) else xs[i] for i in range(0,len(xs),2)]
        return xs[0] if xs else 0
    paired=PairedTriple(h,base)
    allresults=paired.triple(list(range(h)),paired.variables)
    selected=list(paired.outputs.values())
    selected += [allresults[(i,)] for i in range(d)] if d else [allresults[()]]
    active=set();stack=list(selected)
    while stack:
        x=stack.pop()
        if not x or x in active:continue
        active.add(x)
        if paired.args[x]:stack.extend(paired.args[x])
    mapping={0:0}|{j+1:inputs[t] for j,t in enumerate(triples)}
    for x in sorted(active):
        if paired.args[x]:
            a,b=paired.args[x];mapping[x]=add(mapping[a],mapping[b])
    roots=[mapping[paired.outputs[t]] for t in triples];kind=[0]*v
    center_disjoint_roots=[mapping[allresults[(i,)]] for i in range(d)]
    fulltotal=mapping[allresults[()]] if not d else None
    del paired, mapping, active, allresults
    pairtotals={}
    for a,b in combinations(range(h),2):
        others=[i for i in range(h) if i not in (a,b)]
        others.sort(key=lambda i:((i^1) in (a,b),i))
        star_total,star_out=interval_sums(add,[inputs[tuple(sorted((a,b,i)))] for i in others])
        for x in star_out:
            roots.append(x);kind.append(0)
        pairtotals[a,b]=star_total
    for a in range(d,h):
        root=total([pairtotals[tuple(sorted((a,b)))] for b in range(h) if b!=a],center=a)
        roots.append(root);kind.append(1)
    if d:
        roots.extend(center_disjoint_roots);kind.extend([1]*d)
    else:
        roots.append(fulltotal);kind.append(1)
    active=[0]*len(args);stack=list(roots)
    while stack:
        x=stack.pop()
        if not x or active[x]:continue
        active[x]=1
        if args[x][0]:stack.extend(args[x])
    degree=[0]*len(args)
    for x in range(1,len(args)):
        if active[x] and args[x][0]:
            for y in args[x]:degree[y]+=1
    for x in roots:degree[x]+=1
    H=[0]*(h+1);c=0;loss=0
    for x in range(1,len(args)):
        if not active[x]:continue
        r=ranks[x]
        if args[x][0]:
            c+=1;H[r]+=degree[x]-1;H[h-r]+=1
            for y in args[x]:H[r-ranks[y]]+=1
        else:H[1]+=degree[x]
    for x,k in zip(roots,kind):
        r=ranks[x]
        if k:H[r]+=1;H[h]+=1;loss+=r
        else:H[h-1-r]+=1;H[1]+=1
    q=len(roots);R=c+q
    result=dict(h=h,v=v,c=c,q=q,R=R,loss=loss,histogram=H,rank_sum=sum(r*n for r,n in enumerate(H)),central_disjoint=d)
    prefix=Path(output_dir)/f'{output_prefix}_{h}'
    with open(str(prefix)+'.bin','wb') as f:
        f.write(struct.pack('<4I',h,v,len(args),q))
        array.array('I',(a for pair in args for a in pair)).tofile(f)
        array.array('Q',core).tofile(f);array.array('Q',cover).tofile(f)
        array.array('I',roots).tofile(f);array.array('I',kind).tofile(f)
        array.array('B',active).tofile(f)
    with open(str(prefix)+'.labels','wb') as f:
        array.array('I',ranks).tofile(f);array.array('B',types).tofile(f)
    Path(str(prefix)+'.json').write_text(json.dumps(result,indent=2)+'\n')

    return result
