import sys,csv,ast,itertools,json,time
sys.path.insert(0,'../AUDIT-SC')
from rrc_audit import G,N,submultisets,scen
from collections import Counter
import networkx as nx
def best(gv,d,extra,tl=60):
    """max over (K0,j>=2) of maxclique-N_j ; also IMM margin"""
    gv=tuple(sorted(gv,reverse=True)); cnt=Counter(gv)
    res=(-99,None)
    imm=sum(gv[d-1:])+extra-56   # <=0 kills
    for j in range(2,d+1):
        for K0 in submultisets(cnt,d-j):
            rest=cnt.copy(); rest.subtract(Counter(K0)); comp=sorted(rest.elements(),reverse=True)
            cap=sum(comp)+extra; m=len(comp)
            nodes=[M for M in itertools.combinations(range(m),j-1) if cap-sum(comp[i] for i in M)<=77]
            # dedupe by multiset type is not valid for cliques; use all
            if len(nodes)<=N[j]:
                if len(nodes)-N[j]>res[0]: res=(len(nodes)-N[j],(K0,j,'nodes'))
                continue
            if len(nodes)>2500: 
                continue
            Gr=nx.Graph(); Gr.add_nodes_from(range(len(nodes)))
            S=[set(M) for M in nodes]
            for a in range(len(nodes)):
                for b in range(a+1,len(nodes)):
                    if cap-sum(comp[i] for i in S[a]|S[b])<=56: Gr.add_edge(a,b)
            c,w=nx.max_weight_clique(Gr,weight=None)
            if w-N[j]>res[0]: res=(w-N[j],(K0,j,len(nodes),w))
    return imm,res
if __name__=='__main__':
    rows=[r for r in csv.DictReader(open('ledger_v2.csv')) if r['audit_status']=='OPEN']
    out={}
    for r in rows:
        ws=sorted(ast.literal_eval(r['weights']),reverse=True); d=int(r['d']); s=int(r['slack'])
        sc=scen(ws,d,s)
        if sc is None: print(r['row'],'NA'); continue
        worst=None
        for tag,gv,dd,ex in sc:
            t=time.time(); b=best(gv,dd,ex)
            if worst is None or b[1][0]<worst[2][0]: worst=(tag,b[0],b[1])
        print(r['row'],d,s,ws,'margin',worst[2][0],worst[0],'imm',worst[1],worst[2][1],flush=True)
