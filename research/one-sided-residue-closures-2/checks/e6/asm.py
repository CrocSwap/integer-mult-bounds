import itertools, networkx as nx
g={1:1,2:2,3:4,4:8,5:12,6:20,7:36,8:64}
N={2:3,3:6,4:12,5:20,6:36}
Np={2:36,3:20,4:12,5:6,6:3}   # max pos roots of rank 8-j parabolic of E8 (j=2: E6=36 ... )
ROWS={168:(7,[7,7,6,6,6,6,6,5,5,5,4],7),169:(7,[7,7,6,6,6,6,6,6,4,4,4,1],7),
324:(8,[7,7,7,7,6,6,6,5,5,5,5,4],6),325:(8,[7,7,7,7,6,6,6,6,5,5,4,4],6),328:(8,[7,7,7,7,6,6,6,6,5,5,5,3],6),
332:(8,[7,7,7,7,6,6,6,6,6,4,4,3,1],6),333:(8,[7,7,7,7,6,6,6,6,6,4,4,4],6),
424:(8,[7,7,7,6,6,6,6,6,5,5,5,4,1],7),426:(8,[7,7,7,6,6,6,6,6,6,4,4,4,1,1],7),427:(8,[7,7,7,6,6,6,6,6,6,4,4,4,2],7),
448:(8,[7,7,7,7,6,6,6,6,5,4,4,4,1,1],7),449:(8,[7,7,7,7,6,6,6,6,5,4,4,4,2],7),457:(8,[7,7,7,7,6,6,6,6,5,5,5,4],7),464:(8,[7,7,7,7,6,6,6,6,6,4,4,4,1],7)}
def scen(ws,d,s):
    if s==7: return [('ClassI',ws,d,0)]
    L=[('beta1',ws,d,0),('alpha',ws,d,1)]
    for x in sorted(set(ws)):       # beta2/beta3-i: one piece of weight x becomes x+1
        w=list(ws); w.remove(x); w.append(x+1); L.append(('bump%d'%x,sorted(w,reverse=True),d,0))
    if 7 in ws:                     # beta3-B
        w=list(ws); w.remove(7); L.append(('b3B',w,d-1,0))
    return L
def kills(ws,d,ex):
    """return list of lemma tags that kill this scenario"""
    ws=sorted(ws,reverse=True); out=[]
    gv=[g[w] for w in ws]
    # IMM: some (d-1)-subset K with cap(rest)+ex<=56 ; best K = d-1 largest
    if sum(gv[d-1:])+ex<=56: out.append('IMM')
    for j in range(2,d+1):
        for K0 in set(itertools.combinations(range(len(ws)),d-j)):
            pass
        break
    # RRC & count over all K0 (as index subsets, dedupe by multiset)
    seen=set()
    for j in range(2,min(d,6)+1):
        for K in itertools.combinations(range(len(ws)),d-j):
            key=(j,tuple(sorted(gv[i] for i in K)))
            if key in seen: continue
            seen.add(key)
            comp=[gv[i] for i in range(len(ws)) if i not in K]; cap=sum(comp)+ex
            if cap<120-Np[j]: out.append('COUNT j=%d K0=%s cap=%d<%d'%(j,key[1],cap,120-Np[j])); 
            nodes=[M for M in itertools.combinations(range(len(comp)),j-1) if cap-sum(comp[i] for i in M)<=77]
            if len(nodes)>N[j]:
                G=nx.Graph(); G.add_nodes_from(range(len(nodes)))
                S=[set(M) for M in nodes]
                for a in range(len(nodes)):
                    for b in range(a+1,len(nodes)):
                        if cap-sum(comp[i] for i in S[a]|S[b])<=56: G.add_edge(a,b)
                w=nx.max_weight_clique(G,weight=None)[1]
                if w>N[j]: out.append('RRC j=%d K0=%s clique=%d>%d'%(j,key[1],w,N[j]))
            if out: return out   # first kill suffices
    # DimCover candidate (j=2, K0=top d-2)
    comp=sorted(ws[d-2:]) [::-1] if False else ws[d-2:]
    cg=sorted([g[w] for w in comp],reverse=True)
    return out
res={}
for r,(d,ws,s) in ROWS.items():
    print('ROW',r,'d',d,'s',s)
    for tag,w2,dd,ex in scen(ws,d,s):
        k=kills(w2,dd,ex)
        if k: print('  ',tag,'KILLED by',k[0])
        else:
            comp=tuple(sorted(w2[dd-2:]+[1]*ex,reverse=True)); cap=sum(g[w] for w in comp)
            print('  ',tag,'-> needs DimCover comp',comp,'cap',cap, 'len', len(w2), w2)
