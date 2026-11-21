from lm7 import *
import networkx as nx, collections
for kind in ('e7','p52'):
    ports=shard(kind); setlabels(ports); lab=NL.L; V=span(lab); dV=len(V)
    els=[0]
    for y in V: els+=[e^y for e in els]
    print(kind,'n',len(ports),'dimV',dV,'label multiset distinct?',len(set(lab))==len(lab))
    # hyperplanes of V: kernels of functionals w in F2^9 restricted to V (distinct restrictions)
    seen={}
    for w in range(1,512):
        h=frozenset(e for e in els if dot(e,w)==0)
        if len(h)==len(els)//2: seen[h]=w
    stats=collections.Counter()
    for h,w in seen.items():
        X=[i for i,l in enumerate(lab) if l in h]
        g=nx.Graph(); g.add_nodes_from(X)
        for i in X:
            for j in X:
                if i<j and NL.Qm[i,j]: g.add_edge(i,j)
        om=max((len(c) for c in nx.find_cliques(g)),default=0)
        v_in = 1 if (len(span(lab))>0 and all(True for _ in [0])) else 0
        stats[(len(X),om)]+=1
    print(' hyperplane (nports, omega) counts:',sorted(stats.items()))
