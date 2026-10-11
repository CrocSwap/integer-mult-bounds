import json, sys, math
from collections import Counter
from itertools import combinations
sys.path.insert(0,'/home/claude/cx/tree/scripts')
from paired_cube.graph import Graph
from paired_cube.modules import triple_module_from, pair_module_from, all_but_one_from
for P,tag,mods in [(11,'L11',('tmod_final.json','pmod46_ptc1_final.json','qmod_q1_snap1.json')),(10,'L10',('tmod_p10.json','pmod37_p10.json','qmod_p10.json'))]:
    T=triple_module_from('mods/'+mods[0],P); PM=pair_module_from('mods/'+mods[1],P-1); Q=all_but_one_from('mods/'+mods[2],P-2)
    local=json.load(open('tree/references/paired-cube/sources/local_L1.json')); local['G']={k:'s' for k in local['G']}; local['A']={k:'fd' for k in local['A']}
    b=Graph(P,local=local); b.local_channels(); L=len(b.a)
    b.module(T,[b.F[I] for I in b.cubes]); Tend=len(b.a)
    for i in range(P):
        others=[a for a in range(P) if a!=i]; pairs=list(combinations(others,2))
        for bit in range(2): b.module(PM,[b.A[tuple(sorted((i,*K))),i,bit] for K in pairs])
    Pend=len(b.a)
    for i,j in combinations(range(P),2):
        others=[a for a in range(P) if a not in (i,j)]
        for mode in range(2): b.module(Q,[b.G[tuple(sorted((i,j,k))),i,j,mode] for k in others])
    Qend=len(b.a); v=len(b.labels)
    g=json.load(open(tag+'/tree-mw/cache/graph.json'))
    ok=g['args'][:Qend]==b.a[:Qend]
    def comp(x):
        x=x-1  # flow ids are 1-based graph nodes
        if x<v: return 'source'
        if x<L: return 'local'
        if x<Tend: return 'triple'
        if x<Pend: return 'pair'
        if x<Qend: return 'abo'
        return 'merge/centre'
    w=json.load(open(tag+'/tree-mw/flow.witness.json'))
    nd=Counter(); nn=Counter()
    for node in w['nodes']:
        ids=node['outputs'] or node['inputs']
        c=Counter(comp(x) for x in ids).most_common(1)[0][0] if ids else 'none'
        nd[c]+=node['new_dirty']; nn[c]+=1
    print('p=%d v=%d graph-match=%s  nodes: local %d triple %d pair %d abo %d'%(P,v,ok,L-v,Tend-L,Pend-Tend,Qend-Pend))
    print('   registers born by component:',dict(sorted(nd.items(),key=lambda x:-x[1])),'total',sum(nd.values()))
