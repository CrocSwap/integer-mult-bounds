"""Own explicit legal-edge Hopcroft-Karp witness; from our r13 search."""
from collections import deque
import sys
from paired_cube.frames import basis,perp,contained
def carrier_matching(g,ordering='node'):
    """Exact legal edge list, then deterministic Hopcroft--Karp matching.

    Frame and chronological predicates are the retained compiler's predicates;
    the resulting explicit arcs are checked anew by compile_graph.
    """
    h=g['h'];v=g['v'];args=[None]+[None if a is None else [y+1 for y in a] for a in g['args']]
    roots=[dict(r,node=r['node']+1) for r in g['roots']];n=len(args)
    spans=[()]*n
    for i,u in enumerate(g['inputs']):spans[i+1]=(u,)
    for x in range(v+1,n):spans[x]=basis(spans[args[x][0]]+spans[args[x][1]])
    rann=[];rframe=[]
    for r in roots:
        if r['kind']=='center':U=spans[r['node']];A=perp(U,h)
        else:A=basis(g['inputs'][t] for t in r['targets']);U=perp(A,h)
        rann.append(A);rframe.append(U)
    active=set(range(1,v+1));todo=[r['node'] for r in roots]
    while todo:
        x=todo.pop()
        if x in active:continue
        active.add(x);todo.extend(args[x] or [])
    initial=spans
    if g['matching_frames'] in ('maximal','coordinate'):
        initial=[()]*n;ann=[None]*n;successors=[[] for _ in args];constraints=[[] for _ in args]
        for x in sorted(active):
            for y in args[x] or []:successors[y].append(x)
        for j,r in enumerate(roots):constraints[r['node']].extend(rann[j])
        for x in sorted(active,reverse=True):
            ann[x]=basis(constraints[x]+[z for y in successors[x] for z in ann[y]])
            initial[x]=perp(ann[x],h)
            if g['matching_frames']=='coordinate':
                cover=0
                for u in spans[x]:cover|=u
                initial[x]=perp(ann[x]+tuple(1<<j for j in range(h) if not cover>>j&1),h)
            assert contained(spans[x],initial[x])
    order=sorted(active,key=lambda x:(len(initial[x]),x));position={x:i for i,x in enumerate(order)}
    uses=[[] for _ in args];uf=[];ut=[];uc=[]
    for x in order:
        for j,y in enumerate(args[x] or []):uses[y].append(len(uc));uf.append(initial[x]);ut.append(x);uc.append(2*x+j)
    for j,r in enumerate(roots):uses[r['node']].append(len(uc));uf.append(rframe[j]);ut.append(n+j);uc.append((1<<31)|j)
    donors=[x for x in order if args[x]]
    if ordering=='reverse':donors.reverse()
    elif ordering=='narrow':donors.sort(key=lambda x:(len(initial[x]),x))
    elif ordering=='wide':donors.sort(key=lambda x:(-len(initial[x]),x))
    elif ordering=='node':donors.sort()
    elif ordering.startswith('random:'):
        import random
        rnd=random.Random(int(ordering.split(':',1)[1]));rnd.shuffle(donors)
    adjacency=[]
    for x in donors:
        row=[u for y in args[x] for u in uses[y] if (ut[u]>=n or position[ut[u]]>position[x]) and contained(initial[x],uf[u])]
        if ordering.startswith('late'):   # prefer the latest use in the chronology (root uses last), then the largest growth
            row.sort(key=lambda u:(-(position[ut[u]] if ut[u]<n else 10**9),-(len(uf[u])-len(initial[x])),uc[u]))
        elif ordering.startswith('latefirst'):
            row.sort(key=lambda u:(-(position[ut[u]] if ut[u]<n else -1),uc[u]))
        else:
            row.sort(key=lambda u:(len(uf[u])-len(initial[x]),uc[u]))
        if ordering.startswith('random:') and ordering.count(':')==2:rnd.shuffle(row)   # 'random:SEED:rows' also shuffles use order
        adjacency.append(row)
    if ordering=='struct':
        return dict(donors=donors,adjacency=adjacency,uc=uc,uf=uf,ut=ut,initial=initial,n=n,position=position),None
    L=len(donors);ml=[-1]*L;mr=[-1]*len(uc);dist=[0]*L;iterations=0
    def bfs():
        queue=deque();found=False
        for u in range(L):
            dist[u]=0 if ml[u]<0 else -1
            if ml[u]<0:queue.append(u)
        while queue:
            u=queue.popleft()
            for v2 in adjacency[u]:
                z=mr[v2]
                if z<0:found=True
                elif dist[z]<0:dist[z]=dist[u]+1;queue.append(z)
        return found
    def dfs(u):
        for v2 in adjacency[u]:
            z=mr[v2]
            if z<0 or dist[z]==dist[u]+1 and dfs(z):ml[u]=v2;mr[v2]=u;return True
        dist[u]=-1;return False
    sys.setrecursionlimit(max(10000,2*L))
    while bfs():
        iterations+=1
        for u in range(L):
            if ml[u]<0:dfs(u)
    arcs=[[donors[i],uc[v2]] for i,v2 in enumerate(ml) if v2>=0]
    stats=dict(donors=L,uses=len(uc),edges=sum(map(len,adjacency)),matched=len(arcs),augment_rounds=iterations)
    if ordering.startswith('frozen:'):
        import json as _j
        given=_j.loads(open(ordering.split(':',1)[1]).read());pos_of={uc[u]:u for u in range(len(uc))}
        growth=0;seen=0
        for x,code in given:
            u=pos_of.get(code)
            if u is None:continue
            seen+=1;growth+=len(uf[u])-len(initial[x])
        stats.update(frozen_arcs=len(given),frozen_seen=seen,frozen_growth=growth,hk_growth=int(sum(len(uf[v2])-len(initial[donors[i]]) for i,v2 in enumerate(ml) if v2>=0)))
        import os as _os
        if _os.environ.get('MATCH_FEATURES'):
            chosen={x:pos_of[c] for x,c in given if c in pos_of};hk={donors[i]:v2 for i,v2 in enumerate(ml) if v2>=0}
            rec=[]
            for i,x in enumerate(donors):
                cands=[dict(u=u,growth=len(uf[u])-len(initial[x]),udim=len(uf[u]),root=int(ut[u]>=n),gap=(position[ut[u]]-position[x]) if ut[u]<n else -1,frozen=int(chosen.get(x)==u),hk=int(hk.get(x)==u)) for u in adjacency[i]]
                if cands:rec.append(dict(x=x,ddim=len(initial[x]),pos=position[x],cands=cands))
            open(_os.environ['MATCH_FEATURES'],'w').write(_j.dumps(rec))
        return [list(a) for a in given],stats
    if ordering.startswith('mincost'):
        # Among matchings that saturate the Hopcroft-Karp matched donor set, pick the one minimizing the total frame
        # growth (dim use frame - dim donor frame), via scipy's sparse LAPJV. 'mincost:max' maximizes it instead.
        import numpy as np
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import min_weight_full_bipartite_matching
        parts=ordering.split(':');sign=-1 if len(parts)>1 and parts[1]=='max' else 1
        noise=None
        if len(parts)>2:
            import random as _r;noise=_r.Random(int(parts[2]))
        rows=[i for i,v2 in enumerate(ml) if v2>=0];rid={i:k for k,i in enumerate(rows)}
        data=[];ri=[];ci=[]
        for i in rows:
            x=donors[i]
            for u in adjacency[i]:
                growth=len(uf[u])-len(initial[x]);ri.append(rid[i]);ci.append(u);data.append(1+sign*growth+(0 if sign>0 else 30)+(noise.random()*float(parts[3]) if noise else 0.0))
        M=csr_matrix((np.array(data,dtype=float),(np.array(ri),np.array(ci))),shape=(len(rows),len(uc)))
        r_ind,c_ind=min_weight_full_bipartite_matching(M)
        arcs=[[donors[rows[r]],uc[c]] for r,c in zip(r_ind,c_ind)]
        stats.update(matched=len(arcs),total_growth=int(sum(len(uf[c])-len(initial[donors[rows[r]]]) for r,c in zip(r_ind,c_ind))),mincost=True)
        hk_growth=int(sum(len(uf[v2])-len(initial[donors[i]]) for i,v2 in enumerate(ml) if v2>=0));stats['hk_growth']=hk_growth
    return arcs,stats

