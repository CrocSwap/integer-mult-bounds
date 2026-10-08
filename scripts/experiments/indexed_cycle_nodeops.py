# Exact function extracts from Thomas DiFiore PR74,3f78d8967c009153f2df5c6a6577b6ab1d37e2ca. Apache-2.0; original source and notices retained.

def reorder(c):
    groups={}
    for x in sorted(c.active):
        if c.args[x]: groups.setdefault((c.core[x],c.union[x]),[]).append(x)
    def key(item):
        (core,cover),nodes=item
        return cover.bit_count()-core.bit_count(),-core,cover,min(nodes)
    ids=list(range(len(c.inputs)+1))+[x for _,nodes in sorted(groups.items(),key=key) for x in nodes]
    mapping={x:i for i,x in enumerate(ids)}
    args,core,cover,provenance=c.args,c.core,c.union,c.provenance
    c.args=[tuple(mapping[y] for y in args[x]) if args[x] else None for x in ids]
    c.core=[core[x] for x in ids];c.union=[cover[x] for x in ids]
    c.provenance=[provenance[x] for x in ids]
    c.active={mapping[x] for x in c.active};c.outputs={k:mapping[v] for k,v in c.outputs.items()}
    c.support_in.cache_clear()
    c.verify()
    return c


def relabel(word,permutation):
    from itertools import combinations
    h,v=word['h'],word['v'];assert sorted(permutation)==list(range(h))
    triples=list(combinations(range(h),3));assert len(triples)==v
    index={triple:i for i,triple in enumerate(triples)}
    def triple(t):return sorted(permutation[x] for x in t)
    mapping={i:index[tuple(triple(t))] for i,t in enumerate(triples)}
    def mask(bits):return sum(1<<permutation[i] for i in range(h) if bits>>i&1)
    word['frames']=[[mask(c),mask(u)] for c,u in word['frames']]
    word['sources']={str(mapping[int(i)]):slot for i,slot in word['sources'].items()}
    scatter=[]
    for a,b in word['scatter']:
        assert v<=a<2*v and b>=2*v
        scatter.append([v+mapping[a-v],b])
    word['scatter']=scatter
    word['outputs']=[[s,g,permutation[common],triple(t)] for s,g,common,t in word['outputs']]
    return word


