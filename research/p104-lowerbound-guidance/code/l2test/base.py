import numpy as np, json, networkx as nx
WD='<research-tree>/cards/WILD/'
G=np.load(WD+'REBASET1/G104.npy').astype(int); L=json.load(open(WD+'REBASET1/lines104.json'))
dot=lambda a,b: bin(a&b).count('1')&1
Q=np.array([[dot(a,b) for b in L] for a in L])   # 1 = odd pair (incl diagonal)
F0=[0,6,16,22,29,36,45,95]; Ah=G[:,F0]            # 2G = Ah Ah^T on Q96 (R96 S5); check for 104 below
def sections(n):
    out={}
    for u in range(1,512):
        X=[p for p in range(n) if not dot(u,L[p])]
        out[u]=X
    return out
def rankQ(M):
    return np.linalg.matrix_rank(M.astype(float))
def f2rank(rows):
    b=[]
    for v in rows:
        for x in b: v=min(v,v^x)
        if v: b.append(v)
    return len(b)
def omega(X,Y=None):
    # max clique in odd graph on X (rows) ∩ Y(cols): vertices in X∩Y, edges odd pairs
    Y=X if Y is None else Y
    V=sorted(set(X)&set(Y)); g=nx.Graph(); g.add_nodes_from(V)
    for i,a in enumerate(V):
        for b in V[i+1:]:
            if Q[a,b]: g.add_edge(a,b)
    if not V: return 0,[]
    c=max(nx.find_cliques(g),key=len); return len(c),c
