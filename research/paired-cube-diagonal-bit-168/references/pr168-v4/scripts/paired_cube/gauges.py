# Copyright 2026 icekylinx. Apache-2.0.
# Developed with GPT-6 Astra assistance; integrated with Codex assistance.
"""One exact chronological partial-gauge selection on a concrete binary word.

Uses the retained initial old-response cancellation and center-closure lemma.
The signed matrix is specified by the literal word, while union incidence is
only a conservative test of which target frames must contain each gauge.
"""
from pathlib import Path
from collections import Counter
import json,sys,math
from .frames import basis,perp,contained

def select(g,p,w):
    if g['args'][len(g['inputs'])] is not None:
        g=dict(g);g['args']=[None]+[None if a is None else [x+1 for x in a] for a in g['args']]
        g['roots']=[dict(r,node=r['node']+1) for r in g['roots']]
    h=p['h'];v=p['v'];args=g['args'];roots=g['roots'];n=len(args)
    order=w['order'];ann=w['annihilators'];arcs=dict(w['matching_arcs']);incoming=set(arcs.values())
    uses=[[] for _ in args]
    for x in order:
        if args[x]:
            for j,y in enumerate(args[x]):uses[y].append(2*x+j)
    for j,r in enumerate(roots):uses[r['node']].append((1<<31)|j)
    assign={};sources={};ops=[];opcoeff=[];R=0
    for x in order:
        if args[x]:
            aa,bb=args[x];dest,control=assign[2*x],assign[2*x+1]
            swapped=False
            if x in arcs:
                u=arcs[x];value=roots[u&0x7fffffff]['node'] if u>>31 else args[u//2][u&1]
                if value==aa:dest,control=control,dest;swapped=True
                else:assert value==bb
                assert u not in assign;assign[u]=control
            ops.append((dest,control,x))
            sign=g['signs'][x-1]
            opcoeff.append((sign,1) if swapped else (1,sign))
        else:dest=R;R+=1;sources[x]=dest
        free=[u for u in uses[x] if u not in incoming];assert free
        for j,u in enumerate(free):
            assert u not in assign
            if j==0:assign[u]=dest
            else:
                target=R;R+=1;assign[u]=target;ops.append((target,dest,x));opcoeff.append((1,1))
    assert R==p['R'],(R,p['R'])
    rootroles=[assign[(1<<31)|j] for j in range(len(roots))]
    prev=[-1]*R;pred=[];first=[None]*R
    for i,(a,b,x) in enumerate(ops):
        pred.append((prev[a],prev[b]));prev[a]=prev[b]=i
        if first[a] is None:first[a]=x
        if first[b] is None:first[b]=x
    stack=[prev[s] for r,s in zip(roots,rootroles) if r.get('kind','side')=='center' and prev[s]>=0]
    phase=set()
    while stack:
        i=stack.pop()
        if i in phase:continue
        phase.add(i);stack.extend(j for j in pred[i] if j>=0)
    touched=set(sources.values())
    for i in phase:touched.update(ops[i][:2])
    co=[0]*R
    for r,s in zip(roots,rootroles):co[s]|=sum(1<<t for t in r['targets'])
    for a,b,x in reversed(ops):co[b]|=co[a]
    inputs=g['inputs'];limit=[None]*v
    for r in roots:
        if r.get('kind','side')=='center':continue
        A=basis(inputs[t] for t in r['targets'])
        for t in r['targets']:
            if limit[t] is None:limit[t]=A
    for t in range(v):
        if limit[t] is None:limit[t]=(inputs[t],)
    selected=[];gauges=Counter();H=Counter({r:c for r,c in enumerate(p['remaining_internal_histogram'])})
    candidates=sorted((s for s in range(R) if s not in touched and first[s] is not None),key=lambda s:(len(ann[first[s]]),co[s].bit_count(),s))
    trial_a=g.get('gauge_trial_saving',0.00065)
    def excess(t):return t*math.expm1(trial_a*math.log(3*h/t)) if t else 0.
    rejected_cost=0
    for s in candidates:
        A=tuple(ann[first[s]]);targets=[];bits=co[s]
        while bits:
            low=bits&-bits;t=low.bit_length()-1;bits^=low;targets.append(t)
            A=basis(A+tuple(limit[t]))
            if len(A)==h:break
        if len(A)==h:continue
        r=h-len(ann[first[s]]);d=h-len(A)
        delta=3*(excess(r-d)-excess(r))+excess(3*d)
        delta+=3*math.fsum(excess(d)+excess(h-len(limit[t])-d)-excess(h-len(limit[t])) for t in targets)
        if delta>=-1e-12:
            rejected_cost+=1
            continue
        H[r]-=1;H[r-d]+=1;gauges[d]+=1
        assert H[r]>=0
        for t in targets:limit[t]=A
        selected.append(dict(role=s,annihilator=A,rank=d,targets=targets))
    Y=Counter();current=[()]*v
    for z in reversed(selected):
        U=perp(z['annihilator'],h)
        for t in z['targets']:
            assert contained(current[t],U)
            Y[len(U)-len(current[t])]+=1;current[t]=U
    for r in roots:
        if r.get('kind','side')=='center':continue
        U=perp(basis(inputs[t] for t in r['targets']),h)
        for t in r['targets']:
            assert contained(current[t],U)
            Y[len(U)-len(current[t])]+=1;current[t]=U
    for t in range(v):Y[h-1-len(current[t])]+=1
    m=3*h;W=2*v+R;C=Counter({r:3*c for r,c in H.items() if r})
    C.update({int(r):3*c for r,c in p['source_data_histogram'].items() if int(r)})
    C.update({r:3*c for r,c in Y.items() if r});C.update({3*r:c for r,c in gauges.items()})
    C[2]+=2*v;mass=sum(r*c for r,c in C.items());assert W*m-mass==2*v-3*p['loss']
    lo=0.;hi=.1
    for _ in range(75):
        a=(lo+hi)/2
        if math.fsum(c*r*math.exp(a*math.log(m/r)) for r,c in C.items())<W*m:lo=a
        else:hi=a
    p=dict(p,selected_roles=len(selected),selected_rank_histogram=dict(gauges),
        remaining_internal_histogram=[H[r] for r in range(h+1)],target_data_histogram=dict(Y),
        phase1_operations=len(phase),total_M_operations=len(ops),untouched_non_source_roles=R-len(touched),
        numerical_complex_root=lo,child_histogram=dict(C),rank_per_vertex=mass,
        gauge_cost_rejections=rejected_cost,gauge_trial_saving=trial_a,
        gauge_selection='Descending first-frame dimension, narrow incidence first; exact local numerical moment-gain filter; intersections with target upper frames; old-value reads in reverse order')
    return p,dict(selected=selected,phase1=sorted(phase),sources=sources,rootroles=rootroles,ops=ops,opcoeff=opcoeff)
