import numpy as np,sys,gzip,json,itertools
def odd_graph(ports):
    v=len(ports)
    return [[bin(ports[i]&ports[j]).count('1')%2 for j in range(v)] for i in range(v)]
def max_clique(adj):
    v=len(adj);nb=[set(j for j in range(v) if j!=i and adj[i][j]) for i in range(v)]
    best=[]
    def expand(R,P):
        nonlocal best
        if not P:
            if len(R)>len(best):best=R[:]
            return
        if len(R)+len(P)<=len(best):return
        for x in sorted(P,key=lambda z:-len(nb[z]&P)):
            expand(R+[x],P&nb[x]);P=P-{x}
            if len(R)+len(P)<=len(best):return
    expand([],set(range(v)));return best
if __name__=='__main__':
    for p in sys.argv[1:]:
        w=json.load(gzip.open(p));ports=w['ports']
        a=odd_graph(ports)
        assert all(a[i][i]==1 for i in range(len(ports)))
        c=max_clique(a)
        print(p.split('cards/')[-1][:50],'v',len(ports),'distinct',len(set(ports)),'odd density',np.mean(a),'omega',len(c),sorted(c))
