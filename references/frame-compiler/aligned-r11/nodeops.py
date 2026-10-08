# PR74 reorder/relabel derived from Thomas DiFiore, head3f78d8967c009153f2df5c6a6577b6ab1d37e2ca.
# Original extracts retained at original/nodeops.py. Apache-2.0, inherited notices apply.
# Rank-preserving tie keys and dense verifier added by Chafik Boukhalfa with OpenAI Codex assistance.
from hashlib import sha256

def order_key(item,mode):
    (core,cover),nodes=item
    rank=cover.bit_count()-core.bit_count()
    masks={
        'pr74':(-core,cover),
        'core-plus-cover-plus':(core,cover),
        'core-plus-cover-minus':(core,-cover),
        'core-minus-cover-minus':(-core,-cover),
        'cover-plus-core-plus':(cover,core),
        'cover-plus-core-minus':(cover,-core),
        'cover-minus-core-plus':(-cover,core),
        'cover-minus-core-minus':(-cover,-core),
        'small-core-plus':(core.bit_count(),core,cover),
        'small-core-minus':(core.bit_count(),-core,cover),
        'large-core-plus':(-core.bit_count(),core,cover),
        'large-core-minus':(-core.bit_count(),-core,cover),
        'minnode-plus':(min(nodes),-core,cover),
        'minnode-minus':(-min(nodes),-core,cover),
        'maxnode-plus':(max(nodes),-core,cover),
        'maxnode-minus':(-max(nodes),-core,cover),
    }
    return (rank,)+masks[mode]+(min(nodes),)

def reorder(c,mode='pr74'):
    groups={}
    for x in sorted(c.active):
        if c.args[x]:groups.setdefault((c.core[x],c.union[x]),[]).append(x)
    # Every cross-envelope dependency strictly raises dimension. This permits
    # arbitrary ties at fixed rank while retaining original order inside a group.
    for x in sorted(c.active):
        for y in c.args[x] or ():
            assert y<x
            a,b=(c.core[y],c.union[y]),(c.core[x],c.union[x])
            assert not(b[0]&~a[0]) and not(a[1]&~b[1])
            if a!=b:assert a[1].bit_count()-a[0].bit_count()<b[1].bit_count()-b[0].bit_count()
    ordered=sorted(groups.items(),key=lambda item:order_key(item,mode))
    ids=list(range(len(c.inputs)+1))+[x for _,nodes in ordered for x in nodes]
    assert len(ids)==len(set(ids)) and set(ids)==c.active|{0}
    mapping={x:i for i,x in enumerate(ids)}
    args,core,cover,provenance=c.args,c.core,c.union,c.provenance
    for _,nodes in ordered:assert nodes==sorted(nodes)
    c.args=[tuple(mapping[y] for y in args[x]) if args[x] else None for x in ids]
    c.core=[core[x] for x in ids];c.union=[cover[x] for x in ids]
    c.provenance=[provenance[x] for x in ids]
    c.active={mapping[x] for x in c.active};c.outputs={k:mapping[v] for k,v in c.outputs.items()}
    c.support_in.cache_clear();c.verify()
    return c

def verify_dense(c):
    """Reconstruct all scalar supports in the global input basis, without provenance."""
    from itertools import combinations
    triples=list(combinations(range(c.h),3));assert list(c.inputs)==triples
    support=[0]*len(c.args);core=[0]*len(c.args);cover=[0]*len(c.args)
    digest=sha256();width=(len(triples)+7)//8
    for x in sorted(c.active):
        if c.args[x]:
            a,b=c.args[x];assert a<x and b<x and not(support[a]&support[b])
            support[x]=support[a]^support[b];core[x]=core[a]&core[b];cover[x]=cover[a]|cover[b]
        else:
            assert 1<=x<=len(triples);support[x]=1<<(x-1)
            core[x]=cover[x]=sum(1<<i for i in triples[x-1])
        assert core[x]==c.core[x] and cover[x]==c.union[x]
        digest.update(support[x].to_bytes(width,'little'))
    input_masks=[sum(1<<i for i in t) for t in triples]
    for (common,target),x in c.outputs.items():
        forbidden=sum(1<<i for i in target if i!=common)
        expected=sum(1<<i for i,mask in enumerate(input_masks) if mask>>common&1 and not(mask&forbidden))
        assert support[x]==expected
    return {'status':'PASS all global supports, exact envelopes, disjoint additions and target outputs','nodes':len(c.active),'outputs':len(c.outputs),'sha256':digest.hexdigest()}

# Coordinate action preserves the literal physical word under a global input relabel.
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
