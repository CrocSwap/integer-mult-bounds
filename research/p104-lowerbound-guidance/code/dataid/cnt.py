exec(open('explore.py').read().split("print(lab==L1")[0])
adj=[[G[i][j]==0 and i!=j for j in range(104)] for i in range(104)]
nodes=0;work=0
def ext(k,c):
    global nodes,work
    nodes+=1; work+=len(c)
    if k==0: return 1
    t=0
    for i,v in enumerate(c):
        t+=ext(k-1,[w for w in c[i+1:] if adj[v][w]])
    return t
print(ext(8,list(range(104))),nodes,work)
