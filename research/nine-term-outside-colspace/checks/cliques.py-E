from setup9 import *
import networkx as nx, itertools, collections
unit=sys.argv[1]
L,v,G,frames,nbar,h,basis,cls=load(unit)
og=nx.Graph(); og.add_nodes_from(range(v)); og.add_edges_from((t,s) for t in range(v) for s in range(t+1,v) if G[t][s]==0)
print('orth degree',collections.Counter(dict(og.degree()).values()))
allc=set()
for c in nx.find_cliques(og):
    for k in range(5,len(c)+1):
        for sub in itertools.combinations(sorted(c),k): allc.add(sub)
cnt=collections.Counter(len(c) for c in allc); print(sorted(cnt.items()))
pickle.dump(sorted(allc),open(f'cliques_{unit}.pkl','wb'))
