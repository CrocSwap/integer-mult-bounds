"""Exact Gaussian E8 COPY lower bound, using real-coordinate subspaces.

Written for chinmayarvind23 with substantial OpenAI Codex assistance.
No third-party imports or predecessor code execution.
"""
import itertools
import json
import math
import hashlib
import argparse
from pathlib import Path
from collections import Counter
from fractions import Fraction

PACKAGE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_sources():
    manifest = json.loads((PACKAGE / 'SOURCES.json').read_text(encoding='utf-8'))
    root = PACKAGE.parent.parent
    for source in manifest['sources']:
        path = (root / source['path']).resolve()
        require(path.is_relative_to(root.resolve()), 'source path escapes repository')
        require(hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256'],
                'source hash mismatch: ' + source['path'])
    return hashlib.sha256((PACKAGE / 'SOURCES.json').read_bytes()).hexdigest()


def primitive(row):
    g = math.gcd(*row)
    if not g:
        return tuple(row)
    if next(x for x in row if x) < 0:
        g = -g
    return tuple(x // g for x in row)


def reduce_row(row, basis):
    row = tuple(row)
    for b in basis:
        p = next(i for i, x in enumerate(b) if x)
        if row[p]:
            row = primitive(tuple(x * b[p] - y * row[p] for x, y in zip(row, b)))
    return row


def extend(basis, row):
    row = primitive(reduce_row(row, basis))
    if not any(row):
        return basis
    p = next(i for i, x in enumerate(row) if x)
    out = []
    for b in basis:
        if b[p]:
            b = primitive(tuple(x * row[p] - y * b[p] for x, y in zip(b, row)))
        out.append(b)
    out.append(row)
    return tuple(sorted(out, key=lambda b: next(i for i, x in enumerate(b) if x)))


def rotation(r):
    return tuple(z for k in range(0, 8, 2) for z in (-r[k + 1], r[k]))


def geometry():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for a, b in itertools.product((-2, 2), repeat=2):
            r = [0] * 8
            r[i], r[j] = a, b
            roots.append(tuple(r))
    roots += [r for r in itertools.product((-1, 1), repeat=8) if sum(x < 0 for x in r) % 2 == 0]
    lines = sorted({min(r, rotation(r), tuple(-x for x in r), tuple(-x for x in rotation(r))) for r in roots})
    require(len(set(roots)) == 240 and len(lines) == 60, 'incorrect root/line census')
    root_set = set(roots)
    require(all(rotation(r) in root_set for r in roots), 'J does not preserve roots')
    require(all(rotation(rotation(r)) == tuple(-x for x in r) for r in roots), 'J squared is not -I')
    for r in lines:
        basis = extend(extend((), r), rotation(r))
        require(len(basis) == 2, 'line is not two-dimensional over Q')
        require(sum(not any(reduce_row(s, basis)) for s in roots) == 4, 'Gaussian line has unexpected roots')
        require(sum(not any(reduce_row(s, basis)) for s in lines) == 1, 'duplicate Gaussian line')
    adj = []
    for i, r in enumerate(lines):
        adj.append(sum(1 << j for j, s in enumerate(lines) if i != j and
                       (sum(x*y for x, y in zip(r, s)) or sum(x*y for x, y in zip(r, rotation(s))))))
    return lines, adj


def clique_census(adj):
    maximum, cliques, nodes = 12, [], 0
    def visit(r, p, x):
        nonlocal maximum, cliques, nodes
        nodes += 1
        if r.bit_count() + p.bit_count() < maximum:
            return
        if not p and not x:
            n = r.bit_count()
            if n > maximum:
                maximum, cliques = n, []
            if n == maximum:
                cliques.append(r)
            return
        union = p | x
        candidates = []
        while union:
            bit = union & -union
            candidates.append(bit.bit_length()-1)
            union ^= bit
        pivot = max(candidates, key=lambda u: (p & adj[u]).bit_count())
        todo = p & ~adj[pivot]
        while todo:
            bit = todo & -todo
            v = bit.bit_length()-1
            visit(r | bit, p & adj[v], x & adj[v])
            p ^= bit
            x |= bit
            todo ^= bit
    visit(0, (1 << len(adj))-1, 0)
    return maximum, sorted(cliques), nodes


def flat_census(lines):
    n = len(lines)
    first = {}
    for i, r in enumerate(lines):
        b = extend(extend((), r), rotation(r))
        first[1 << i] = b
    levels = [{0: ()}, first]
    for rank in (2, 3):
        new = {}
        seen_bases = set()
        for mask, basis in levels[-1].items():
            for i, r in enumerate(lines):
                if mask >> i & 1:
                    continue
                b = extend(extend(basis, r), rotation(r))
                if b in seen_bases:
                    continue
                seen_bases.add(b)
                closure = sum(1 << j for j, s in enumerate(lines) if not any(reduce_row(s, b)))
                new[closure] = b
        levels.append(new)
        require(all(len(b)==2*rank for b in new.values()), 'incorrect flat dimension')
    full = ()
    for r in lines:
        full = extend(extend(full, r), rotation(r))
    levels.append({(1 << n)-1: full})
    return [(rank, mask, basis) for rank, lev in enumerate(levels) for mask, basis in sorted(lev.items())]


def perpendicular_vector(basis):
    pivots = [next(i for i, x in enumerate(b) if x) for b in basis]
    free = next(i for i in range(8) if i not in pivots)
    row = [Fraction(0) for _ in range(8)]
    row[free] = Fraction(1)
    for p, b in zip(pivots, basis):
        row[p] = -Fraction(b[free], b[p])
    denominator = math.lcm(*(x.denominator for x in row))
    return primitive(tuple(int(x * denominator) for x in row))


def inner(a, b):
    return (sum(x*y for x,y in zip(a,b)), sum(x*y for x,y in zip(a,rotation(b))))


def cmul(a,b):
    return (a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0])


def pair_census(lines, cliques, flats):
    enriched = []
    for rank, mask, basis in flats:
        generators, b = [], ()
        for i,r in enumerate(lines):
            if mask >> i & 1 and any(reduce_row(r,b)):
                generators.append(i)
                b=extend(extend(b,r),rotation(r))
                if len(generators)==rank:
                    break
        if b != basis or len(b)!=2*rank:
            raise ValueError('flat generators inconsistent')
        hits = sum(1<<i for i,c in enumerate(cliques) if mask&c)
        normal = perpendicular_vector(basis) if rank==3 else None
        enriched.append((rank,mask,basis,generators,hits,normal))
    gram = [[inner(r,s) for s in lines] for r in lines]
    def pairing(a,b):
        if a[0]>b[0]:
            a,b=b,a
        ra,ma,ba,ga,ha,na=a
        rb,mb,bb,gb,hb,nb=b
        if not ra or rb==4:
            return ra
        if ra==1:
            return int(any(gram[ga[0]][j]!=(0,0) for j in gb))
        if ra==2 and rb==2:
            p,q=ga
            r,s=gb
            x,y,z,w=gram[p][r],gram[p][s],gram[q][r],gram[q][s]
            if cmul(x,w)!=cmul(y,z):
                return 2
            return int(any(v!=(0,0) for v in (x,y,z,w)))
        if ra==2 and rb==3:
            # q(F,H)=dim(F)-dim(F intersect H-perp). H-perp is the
            # Gaussian line generated by nb, so the intersection is 0 or 1.
            return 2 if any(reduce_row(nb,ba)) else 1
        if ra==3 and rb==3:
            # The one-dimensional H-perp lies in F iff their normals
            # are Hermitian-orthogonal. Then the rank drops from 3 to 2.
            return 3 if inner(na,nb)!=(0,0) else 2
        raise ValueError('unhandled rank pair')
    counts, maxima, witnesses, tight = Counter(), {}, {}, Counter()
    digest=hashlib.sha256()
    for i,a in enumerate(enriched):
        for j in range(i,len(enriched)):
            b=enriched[j]
            q=pairing(a,b)
            h=(a[4]&b[4]).bit_count()
            counts[q]+=1
            digest.update(f'{i},{j},{q},{h}\n'.encode())
            if q not in maxima or h>maxima[q]:
                maxima[q]=h
                witnesses[q]=[i,j]
            if h==192*q:
                tight[q]+=1
            require(h<=192*q, f'COPY inequality fails at flats {i},{j}: {h} > 192*{q}')
    result=dict(pair_count=sum(counts.values()),pair_rank_counts=dict(counts),maximum_hits=maxima,
                witnesses={q:[flats[i][1],flats[j][1]] for q,(i,j) in witnesses.items()},
                tight_counts=dict(tight),pair_digest=digest.hexdigest())
    return result,enriched,pairing


def validate_clique(mask, adj):
    require(mask>0 and mask < (1<<len(adj)), 'invalid clique mask')
    for i in range(len(adj)):
        if mask>>i&1:
            require(not (mask & ~(adj[i] | (1<<i))), 'orthogonal pair in purported clique')


def validate_flat(mask, basis, lines):
    actual=sum(1<<i for i,r in enumerate(lines) if not any(reduce_row(r,basis)))
    require(mask==actual, 'flat is not the full root closure of its span')


def validate_fitting(rows, adj):
    require(len(rows)==len(adj), 'wrong decoder dimensions')
    for i,row in enumerate(rows):
        require(row>=0 and row < (1<<len(adj)), 'invalid decoder row')
        require(row>>i&1, 'decoder diagonal not one')
        require(not row&adj[i], 'decoder has forbidden nonorthogonal entry')


def method_ceiling(lines,adj,cliques,enriched,pairing):
    allmask=(1<<len(lines))-1
    lookup={f[1]:f for f in enriched}
    hypers=[allmask & ~(adj[i]|(1<<i)) for i in range(len(lines))]
    require(all(h.bit_count()==15 and lookup[h][0]==3 for h in hypers), 'root hyperplanes do not span rank three')
    orthpairs=[(i,j) for i in range(60) for j in range(i+1,60) if not adj[i]>>j&1]
    require(len(orthpairs)==450,'incorrect orthogonal-pair census')
    for i,j in orthpairs:
        a,b=lookup[hypers[i]],lookup[hypers[j]]
        require(pairing(a,b)==2,'hyperplane witness has wrong pairing rank')
        require((a[4]&b[4]).bit_count()==384,'hyperplane witness has wrong incidence')
    for c in cliques:
        require(all(bool(c&hypers[i]) == (not bool(c>>i&1)) for i in range(60)), 'maximal-clique hyperplane identity fails')
        require(sum(bool(c&hypers[i]) and bool(c&hypers[j]) for i,j in orthpairs)==270,'method ceiling incidence fails')
    return dict(orthogonal_pairs=450,hyperplane_pair_rank=2,hits_per_pair=384,
                witness_pairs_hit_per_maximum_clique=270,method_ceiling=40), orthpairs, hypers


def controls(lines,adj,cliques,flats,enriched,pairing,orthpairs,hypers):
    passed=[]
    def rejects(name, function):
        try:
            function()
        except ValueError:
            passed.append(name)
        else:
            raise ValueError('negative control accepted: '+name)
    i,j=orthpairs[0]
    rejects('orthogonal_pair_called_clique',lambda:validate_clique((1<<i)|(1<<j),adj))
    f=next(f for f in flats if f[0]==2 and f[1].bit_count()==6)
    rejects('one_root_missing_from_closed_flat',lambda:validate_flat(f[1]^(f[1]&-f[1]),f[2],lines))
    lookup={f[1]:f for f in enriched}
    a,b=lookup[hypers[i]],lookup[hypers[j]]
    h=(a[4]&b[4]).bit_count()
    rejects('unsupported_copy_bound_191',lambda:require(h<=191*pairing(a,b),'too-strong lower bound'))
    rejects('hyperplane_pair_rank_undercharged',lambda:require(h<=192,'rank-one undercharge'))
    rejects('source_rank_used_instead_of_pairing_rank',lambda:require(pairing(a,b)==a[0],'source rank is not pairing rank'))
    identity=[1<<i for i in range(60)]
    validate_fitting(identity,adj)
    bad=identity.copy();bad[0]=0
    rejects('missing_decoder_diagonal',lambda:validate_fitting(bad,adj))
    k=(adj[0]&-adj[0]).bit_length()-1
    bad=identity.copy();bad[0]|=1<<k
    rejects('forbidden_decoder_entry',lambda:validate_fitting(bad,adj))
    bad=identity.copy();bad[i]|=1<<j
    validate_fitting(bad,adj)  # Asymmetric orthogonal entries really are allowed.
    rank1a=lookup[1<<i];rank1b=lookup[1<<j]
    require(pairing(rank1a,rank1b)==0 and not rank1a[4]&rank1b[4], 'zero-charge positive control fails')
    require(len(cliques)==640 and sum(c.bit_count() for c in cliques)==7680,'clique coverage failure')
    rejects('one_clique_omitted_from_claimed_coverage',lambda:require(sum(c.bit_count() for c in cliques[:-1])==7680,'incomplete clique certificate'))
    return dict(negative=passed,positive=['asymmetric_orthogonal_entry','zero_charge_rectangle','identity_decoder'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write a freshly computed receipt to a NEW path instead of comparing RESULTS.json')
    args=parser.parse_args()
    sources_hash=check_sources()
    lines, adj = geometry()
    maximum, cliques, nodes = clique_census(adj)
    require(maximum==12 and len(cliques)==640,'maximum clique census changed')
    require(all(a.bit_count()==44 for a in adj),'nonorthogonality degree changed')
    for clique in cliques:
        validate_clique(clique,adj)
    flats = flat_census(lines)
    stats = Counter()
    for rank, mask, basis in flats:
        validate_flat(mask,basis,lines)
        hits = sum(bool(mask & c) for c in cliques)
        stats[(rank,mask.bit_count(),hits)]+=1
    require(len(flats)==2272,'flat census changed')
    pair_result,enriched,pairing=pair_census(lines,cliques,flats)
    ceiling,orthpairs,hypers=method_ceiling(lines,adj,cliques,enriched,pairing)
    control_result=controls(lines,adj,cliques,flats,enriched,pairing,orthpairs,hypers)
    data=dict(schema=1,source_manifest_sha256=sources_hash,roots=240,gaussian_lines=60,
              ambient_gaussian_rank=4,maximum_clique_size=maximum,maximum_clique_count=len(cliques),
              flat_count=len(flats),flat_census=[dict(rank=k[0],size=k[1],hits=k[2],count=v) for k,v in sorted(stats.items())],
              pairs=pair_result,ceiling=ceiling,controls=control_result,
              gaussian_copy_lower_bound=40,gaussian_row_upper_bound=60,rational_copy_lower_bound=80)
    text=json.dumps(data,indent=2,sort_keys=True)+'\n'
    if args.write:
        with args.write.open('x',encoding='utf-8',newline='\n') as output:
            output.write(text)
    else:
        require(json.loads(text)==json.loads((PACKAGE/'RESULTS.json').read_text(encoding='utf-8')),'computed receipt differs from RESULTS.json')
    print('PASS_GAUSSIAN_E8_COPY_BOUND lower=40 upper=60 flats=2272 pairs=2582128 controls=8')


if __name__ == '__main__':
    main()
