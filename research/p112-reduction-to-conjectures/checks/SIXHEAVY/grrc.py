# Generalized RRC analyzer: caps replaced by cover oracles. ORACLE[(kind,M)] = True(coverable)/False/None(unknown)
import itertools, json, os, sys
import networkx as nx
sys.path.insert(0,'../sc2_e6')
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}
N={1:1,2:3,3:6,4:12,5:20,6:36,7:63}
MINOFF={'root':57,'nonroot':78}
OF='../SIXHEAVY/oracle.json'
ORACLE=json.load(open(OF)) if os.path.exists(OF) else {}
need=set()
def q(kind,M):
    M=tuple(sorted(M,reverse=True))
    if sum(g[w] for w in M)<MINOFF[kind]: return False
    k=kind+':'+','.join(map(str,M))
    if k in ORACLE: return ORACLE[k]
    need.add(k); return None
def scen(ws,d,s):
    if s==7: return [('ClassI',ws,d,0)]
    L=[('beta1',ws,d,0),('alpha',ws,d,1)]
    for x in sorted(set(ws)):
        w=list(ws); w.remove(x); w.append(x+1); L.append(('bump%d'%x,sorted(w,reverse=True),d,0))
    if 7 in ws:
        w=list(ws); w.remove(7); L.append(('b3B',w,d-1,0))
    return L
def kill(ws,d,ex):
    ws=sorted(ws,reverse=True); a=len(ws)
    unk=False
    # IMM
    seen=set()
    for K in itertools.combinations(range(a),d-1):
        comp=tuple(ws[i] for i in range(a) if i not in K)+(1,)*ex
        if comp in seen: continue
        seen.add(comp); r=q('root',comp)
        if r is False: return 'IMM K0^c=%s'%(comp,)
    seen=set()
    for j in range(2,min(d,7)+1):
        for K in itertools.combinations(range(a),d-j):
            key=(j,tuple(ws[i] for i in K))
            if key in seen: continue
            seen.add(key)
            comp=[ws[i] for i in range(a) if i not in K]
            nodes=[]; 
            for M in itertools.combinations(range(len(comp)),j-1):
                rest=tuple(comp[i] for i in range(len(comp)) if i not in M)+(1,)*ex
                nr=q('nonroot',rest)
                if nr is False: nodes.append(set(M))
            if len(nodes)<=N[j]: continue
            G=nx.Graph(); G.add_nodes_from(range(len(nodes)))
            for x in range(len(nodes)):
                for y in range(x+1,len(nodes)):
                    rest=tuple(comp[i] for i in range(len(comp)) if i not in nodes[x]|nodes[y])+(1,)*ex
                    if q('root',rest) is False: G.add_edge(x,y)
            cl=nx.max_weight_clique(G,weight=None)[1]
            if cl>N[j]: return 'GRRC j=%d K0=%s comp=%s clique=%d>%d'%(j,key[1],tuple(comp),cl,N[j])
    return None
ROWS={}
import csv
L='../../data/ledger2_consolidated.csv'
TARGET=[169,303,312,315,316,332,333,400,401,402,409,411,417,418,420,424,425,426,427,430,435,464]
for r in csv.DictReader(open(L)):
    if int(r['row']) in TARGET: ROWS[int(r['row'])]=(int(r['d']),json.loads(r['weights']),int(r['slack']))
if __name__=='__main__':
    res={}
    for r,(d,ws,s) in sorted(ROWS.items()):
        out=[]
        for tag,w2,dd,ex in scen(ws,d,s):
            out.append((tag,kill(w2,dd,ex)))
        res[r]=out
        print(r,d,s,ws,'ALL KILLED' if all(k for _,k in out) else 'open: '+' '.join(t for t,k in out if not k),flush=True)
    print('NEED',len(need)); json.dump(sorted(need),open('need.json','w'))
    json.dump(res,open('grrc_res.json','w'),indent=0)
