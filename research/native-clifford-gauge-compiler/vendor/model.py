#!/usr/bin/env python3
"""Exact contact graph and Gaussian rank invoices; Apache-2.0.

Substantial OpenAI Codex assistance. Credit PR4672 contact cuts, PR4654
Clifford chart grammar, PR4610 native words and the retained PR4470 lineage.
"""
from collections import Counter
from pathlib import Path
import gzip,json
def need(x,s):
    if not x:raise ValueError(s)

def span(b):
    s={0}
    for x in b:s|={y^x for y in tuple(s)}
    return s

def mv(cols,x):
    y=0
    for i,a in enumerate(cols):
        if x>>i&1:y^=a
    return y

def inv(cols):
    values={mv(cols,x):x for x in range(512)}
    need(len(values)==512,'invertible G')
    return [values[1<<i] for i in range(9)]

def graph(payload,mode):
    c=payload['canonical'];frames=c['frames'];sp=list(map(span,frames))
    nodes=[0,0];edges=[];fixed={};rewards=[]
    def new(f,freeze=False):
        n=len(nodes);nodes.append(f)
        if freeze:fixed[n]=0
        return n
    cur=[new(f,r<224 or mode=='exits') for r,f in enumerate(c['start'])]
    entry=cur[:]
    def move(r,f,dst=None):
        a=cur[r];old=nodes[a]
        need(sp[old]<=sp[f],f'nested {r}:{old}->{f}')
        b=new(f) if dst is None else dst
        edges.append(('paid',a,b,len(frames[f])-len(frames[old]),tuple(frames[old])))
        cur[r]=b
    maps={x['op']:x['G_columns'] for x in c['warps']}
    maps.update({-op:inv(cols) for op,cols in list(maps.items())})
    for e in payload['programs']['forward']:
        if e[0]=='climb':
            _,_,r,a,b,width=e
            need(sp[a]<sp[b] and width==len(frames[b])-len(frames[a]),'original paid rank and nesting')
            continue
        if e[0]=='scalar':
            g,f=e[1:];refs=g[1:3] if g[0] in ('add','copy') else g[1:2]
            owned=any(r[0]!='L' for r in refs);contact=new(f,owned)
            for typ,r in refs:
                if typ=='L':move(r,f,contact)
        elif e[0]=='warp':
            _,role,op,a,b=e;need(role[0]=='L','persistent warp')
            r=role[1];move(r,a);src=cur[r];dst=new(b)
            edges.append(('warp',src,dst,tuple(frames[a]),tuple(mv(maps[op],v) for v in frames[a])))
            cur[r]=dst
        elif e[0]=='adapter':
            fixed[cur[e[2]]]=0
        elif e[0]=='center':
            _,_,a,b,width=e
            need(sp[a]<sp[b] or sp[b]<sp[a],'original owned-center nesting')
            need(width==abs(len(frames[b])-len(frames[a])),'original owned-center rank')
        else:need(e[0]=='phase','known chronological event')
    for r,f in enumerate(c['final']):
        dst=new(f,r<224 or mode=='entrances');move(r,f,dst)
        if r>=224:
            a,b=c['start'][r],f;need(sp[a]<=sp[b],'nested helper boundary')
            rewards.append((entry[r] if mode=='entrances' else dst,
                            len(frames[b])-len(frames[a]),tuple(frames[a])))
    return nodes,edges,fixed,rewards

def mask(space):
    return sum(1 << x for x in space)

def dimension(bits):
    n = bits.bit_count()
    need(n > 0 and n & (n-1) == 0, 'binary subspace size')
    return n.bit_length()-1

def fourier_rank(a, b):
    return dimension(a)+dimension(b)-2*dimension(a & b)

def load(path):
    raw = Path(path).read_bytes()
    return json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)

def build(payload, functionals):
    """All paid edges, including old zero edges, and both helper endpoints."""
    nodes, edges, fixed, _ = graph(payload, 'free')
    frames = payload['canonical']['frames']
    old = [mask(span(b)) for b in frames]
    kernel = mask(x for x in range(512)
                  if all((l & x).bit_count() % 2 == 0 for l in functionals))
    new = [s & kernel for s in old]
    tables = []
    for kind, a, b, x, y in edges:
        left = (old[nodes[a]], new[nodes[a]])
        right = (old[nodes[b]], new[nodes[b]])
        if kind == 'warp':
            image = {0: 0}
            for u, v in zip(x, y):
                image.update({z ^ u: w ^ v for z, w in list(image.items())})
            left = tuple(mask(image[z] for z in image if s >> z & 1) for s in left)
        ranks = [fourier_rank(left[i], right[j]) for i,j in ((0,0),(1,0),(0,1),(1,1))]
        if kind == 'warp': need(ranks[0] == 0, 'original native warp is monomial')
        tables.append((kind, a, b, ranks))
    helpers = []
    for r in range(224, 632):
        a, b = 2+r, len(nodes)-632+r
        left = (old[nodes[a]], new[nodes[a]])
        right = (old[nodes[b]], new[nodes[b]])
        ranks = [fourier_rank(left[i], right[j]) for i,j in ((0,0),(1,0),(0,1),(1,1))]
        helpers.append((r, a, b, ranks))
    centers = Counter(e[4] for e in payload['programs']['forward'] if e[0] == 'center')
    source_paid = Counter(e[5] for e in payload['programs']['forward'] if e[0] == 'climb') + centers
    result = dict(nodes=nodes, fixed=sorted(fixed), edges=tables, helpers=helpers,
                  centers=dict(centers), old_spaces=old, new_spaces=new)
    p,h = invoice(result, [])
    need(p == source_paid, 'reconstructed baseline invoice')
    return result

def invoice(model, selected):
    chosen = set(selected)
    need(not chosen.intersection(model['fixed']), 'main, adapter and owned boundaries frozen')
    need(all(2 <= n < len(model['nodes']) for n in chosen), 'valid selected contact')
    paid = Counter(model['centers'])
    helper = Counter()
    def rank_at(a, b, ranks):
        return ranks[(a in chosen)+2*(b in chosen)]
    for _,a,b,ranks in model['edges']:
        r=rank_at(a,b,ranks)
        if r: paid[r] += 1
    for _,a,b,ranks in model['helpers']:
        r=rank_at(a,b,ranks)
        need(r > 0, 'strict productive helper')
        helper[r] += 1
    return paid, helper


def binary_rank(rows):
    pivots = {}
    for x in rows:
        while x:
            i = x.bit_length()-1
            if i not in pivots:
                pivots[i] = x
                break
            x ^= pivots[i]
    return len(pivots)

def phase_matrix(functionals):
    rows = [0]*9
    for functional in functionals:
        for i in range(9):
            if functional >> i & 1:
                rows[i] ^= functional
    return rows

def restrict_form(rows, basis):
    def value(x, y):
        return sum((x >> i & 1)*((rows[i] & y).bit_count() % 2)
                   for i in range(9)) % 2
    return [sum(value(x,y) << j for j,y in enumerate(basis)) for x in basis]

def build_phase(payload, functionals):
    """Binary gauges b_U=0 or Q|U, Q=sum lambda*lambda^T over F2.

    Subspaces and logical G maps stay fixed. All changed paid and warp
    Gaussian ranks are charged. Both helper boundaries can change.
    """
    nodes, edges, fixed, _ = graph(payload, 'free')
    frames = payload['canonical']['frames']
    q = phase_matrix(functionals)
    matrices = [restrict_form(q, b) for b in frames]
    active = [bool(binary_rank(s)) for s in matrices]
    tables = []
    for kind,a,b,x,y in edges:
        if kind == 'paid':
            extra = binary_rank(matrices[nodes[a]])
            ranks = [x, x+extra, x+extra, x]
        else:
            source, target = restrict_form(q,x), restrict_form(q,y)
            ranks = [0, binary_rank(source), binary_rank(target),
                     binary_rank([u^v for u,v in zip(source,target)])]
        need(max(ranks) <= 9, 'valid physical phase rank')
        tables.append((kind,a,b,ranks))
    helpers = []
    for r in range(224,632):
        a,b = 2+r,len(nodes)-632+r
        h = len(frames[nodes[b]])-len(frames[nodes[a]])
        extra = binary_rank(matrices[nodes[a]])
        helpers.append((r,a,b,[h,h+extra,h+extra,h]))
    centers = Counter(e[4] for e in payload['programs']['forward'] if e[0]=='center')
    expected = Counter(e[5] for e in payload['programs']['forward'] if e[0]=='climb')+centers
    # Discovery only compares these tokens for whether a node has an alternative.
    m = dict(nodes=nodes, fixed=sorted(fixed), edges=tables, helpers=helpers,
             centers=dict(centers), old_spaces=list(range(len(frames))),
             new_spaces=[i+len(frames) if active[i] else i for i in range(len(frames))])
    paid,_ = invoice(m, [])
    need(paid == expected, 'reconstructed paid-phase baseline')
    return m

def nullspace(rows, width):
    rows=list(rows);pivots=[];k=0
    for j in range(width):
        found=next((i for i in range(k,len(rows)) if rows[i]>>j&1),None)
        if found is None:continue
        rows[k],rows[found]=rows[found],rows[k]
        for i in range(len(rows)):
            if i!=k and rows[i]>>j&1:rows[i]^=rows[k]
        pivots.append(j);k+=1
    return [(1<<j)|sum(((rows[i]>>j)&1)<<v for i,v in enumerate(pivots))
            for j in range(width) if j not in pivots]

def lagrangian(basis, width):
    return [x|(x<<width) for x in basis]+[x<<width for x in nullspace(basis,width)]

def transvection(basis, axis, width):
    low=(1<<width)-1
    def pairing(x):
        return (((x&low)&(axis>>width)).bit_count()+
                ((x>>width)&(axis&low)).bit_count())%2
    return [x^(axis if pairing(x) else 0) for x in basis]

def lagrangian_distance(a,b,width):
    return binary_rank(a+b)-width

def build_pauli(payload, coordinates):
    """Gauge C_U or C_U S_P for one common Hermitian Pauli quarter turn.

    The chosen axis is (X mask, Z mask); this can change both the chart
    subspace and its symmetric form. All changed physical edges are paid.
    """
    x,z=coordinates;axis=x|(z<<9)
    need(0<=x<512 and 0<=z<512 and axis,'nonzero nine-bit Pauli axis')
    nodes,edges,fixed,_=graph(payload,'free');c=payload['canonical'];frames=c['frames']
    old=[lagrangian(b,9) for b in frames]
    new=[transvection(b,axis,9) for b in old]
    active=[bool(lagrangian_distance(a,b,9)) for a,b in zip(old,new)]
    maps={w['op']:w['G_columns'] for w in c['warps']}
    maps.update({-op:inv(g) for op,g in list(maps.items())})
    warp_ops=iter(e[2] for e in payload['programs']['forward'] if e[0]=='warp')
    cache={};tables=[]
    for kind,a,b,r,image in edges:
        fa,fb=nodes[a],nodes[b]
        if kind=='paid':
            if (fa,fb) not in cache:
                need(lagrangian_distance(old[fa],old[fb],9)==r,'old chart rank')
                changed=lagrangian_distance(new[fa],old[fb],9)
                cache[fa,fb]=[r,changed,changed,r]
            ranks=cache[fa,fb]
        else:
            g=maps[next(warp_ops)];gi=inv(g)
            git=[sum(((gi[j]>>i)&1)<<j for j in range(9)) for i in range(9)]
            need(span(mv(g,v) for v in frames[fa])==span(frames[fb]),'native chart image')
            gx=mv(g,x);mapped_axis=gx|((mv(git,x^z)^gx)<<9)
            mapped=transvection(old[fb],mapped_axis,9)
            ranks=[0,lagrangian_distance(mapped,old[fb],9),
                   lagrangian_distance(old[fb],new[fb],9),
                   lagrangian_distance(mapped,new[fb],9)]
        need(0<=min(ranks)<=max(ranks)<=9,'physical Pauli-gauge ranks')
        tables.append((kind,a,b,ranks))
    helpers=[]
    for role in range(224,632):
        a,b=2+role,len(nodes)-632+role;fa,fb=nodes[a],nodes[b]
        h=lagrangian_distance(old[fa],old[fb],9)
        changed=lagrangian_distance(new[fa],old[fb],9)
        helpers.append((role,a,b,[h,changed,changed,h]))
    centers=Counter(e[4] for e in payload['programs']['forward'] if e[0]=='center')
    expected=Counter(e[5] for e in payload['programs']['forward'] if e[0]=='climb')+centers
    model=dict(nodes=nodes,fixed=sorted(fixed),edges=tables,helpers=helpers,centers=dict(centers),
               old_spaces=list(range(len(frames))),
               new_spaces=[i+len(frames) if active[i] else i for i in range(len(frames))])
    paid,_=invoice(model,[]);need(paid==expected,'Pauli-gauge baseline invoice')
    return model
