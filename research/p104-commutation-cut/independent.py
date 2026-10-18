"""Separate interval graph: per-role traces, descendant closures and RREF frames.

No imports from graph.py. Jeremy Diviney with substantial OpenAI Codex
assistance, Apache-2.0. This is not independent human review.
"""
from bisect import bisect_left
from collections import defaultdict,deque

def require(ok, why):
    if not ok:raise ValueError(why)

def basis(vectors):
    pivots={}
    for original in vectors:
        v=original
        while v:
            p=v.bit_length()-1
            if p in pivots:v ^= pivots[p]
            else:pivots[p]=v;break
    for p in sorted(pivots):
        for q in sorted(pivots):
            if q>p and (pivots[q]>>p)&1:pivots[q]^=pivots[p]
    return tuple(pivots[p] for p in sorted(pivots))

def check(w):
    events=w['program'];n=len(events);touches=defaultdict(list)
    for j,e in enumerate(events):
        for r in e[1:3] if e[0] in ('add','copy') else e[1:2]:touches[r].append(j)
    next_events=[set() for _ in events]
    for trace in touches.values():
        for a,b in zip(trace,trace[1:]):next_events[a].add(b)
    descendants=[set() for _ in events]
    for a in range(n-1,-1,-1):
        for b in next_events[a]:descendants[a].add(b);descendants[a].update(descendants[b])
    # Build each role's frame intervals separately, with its own private births.
    nodes=[];role_nodes={};initial={};final={}
    for role in sorted(touches):
        current=basis(w['initial_frames'][role]) if role in w['initial_frames'] else None
        start=-1;trace=[]
        if current is not None:initial[role]=len(nodes)
        for at in touches[role]:
            e=events[at]
            if e[1]!=role:continue  # original READ orders events but does not split a wire
            op=e[0]
            if op=='zero':
                require(current is None,'private birth');current=basis(e[2]);start=at;continue
            require(current is not None,'live role')
            trace.append(len(nodes));nodes.append((role,start,at,current))
            if op=='erase':current=None;continue
            if op=='transport':
                require(current==basis(e[2]),'old frame');current=basis(e[3])
            start=at
        if current is not None:
            final[role]=len(nodes);trace.append(len(nodes));nodes.append((role,start,n,current))
            require(current==basis(w['final_frames'][role]),'final frame')
        role_nodes[role]=trace
    adjacency=[set() for _ in nodes];ends={};starts={}
    for i,(role,a,b,_) in enumerate(nodes):ends[role,b]=i;starts[role,a]=i
    removed=[];causal=0
    for at,e in enumerate(events):
        op=e[0];r=e[1]
        if op in ('zero','erase'):continue
        left,right=ends[r,at],starts[r,at]
        if op=='transport' and r=='C' and len(basis(e[2]))>len(basis(e[3])):
            removed.append((at,left,right,e[4]))
        else:adjacency[left].add(right);causal+=1
        if op in ('add','copy'):
            src=e[2];trace=role_nodes[src];ss=[nodes[j][1] for j in trace]
            k=bisect_left(ss,at)-1;source=trace[k]
            require(nodes[source][1]<at<=nodes[source][2],'source read interval')
            require(nodes[source][3]==nodes[left][3]==basis(e[-1]),'literal common frame')
            adjacency[source].add(right);causal+=1
    classes=defaultdict(list)
    for j,node in enumerate(nodes):classes[node[3]].append(j)
    def precedes(a,b):
        if a<0 or b==n:return True
        if a==n or b<0:return False
        return a==b or b in descendants[a]
    free_edges=0
    for same in classes.values():
        for i,u in enumerate(same):
            ru,au,bu,_=nodes[u]
            for v in same[i+1:]:
                rv,av,bv,_=nodes[v]
                if ru==rv or precedes(bu,av) or precedes(bv,au):continue
                adjacency[u].add(v);adjacency[v].add(u);free_edges+=2
    sources={v for k,v in initial.items() if k.startswith('X')}
    def reachable(extra=()):
        extra=dict(extra);seen=set(sources);queue=deque(sources)
        while queue:
            u=queue.popleft();out=adjacency[u]
            if u in extra:out=out|{extra[u]}
            for v in out-seen:seen.add(v);queue.append(v)
        return sorted(k for k,v in final.items() if k.startswith('Y') and v in seen),seen
    targets,seen=reachable();require(not targets,'independent cut separates all targets')
    reopen=[]
    for at,left,right,rank in removed:
        targets,_=reachable([(left,right)]);require(targets,'single descent restores real path');reopen.append(len(targets))
    return {'nodes':len(nodes),'frames':len(classes),'causal_edges':causal,'potential_common_frame_edges':free_edges,
            'cut_events':[v[0] for v in removed],'cut_ranks':[v[3] for v in removed],
            'reachable_nodes':len(seen),'single_edge_reopened_targets':reopen}
