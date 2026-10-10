"""Generalized exact replay of the restricted PR117 complex producer.

Copyright 2026 eumemic, Apache-2.0. AI-assisted (Claude). The DAG was found by an
automated search over producers of the retained paired-triple, pair-star and
center-disjoint interfaces. The checks below are adapted from
stopped_product/complex.py (copyright 2026 icekylinx, Apache-2.0, PR #104).

The derived restricted witness lists the ordinary
additions after the v triple inputs and the retained roots: the disjoint sums
D[t], the pair stars P(a,b,i) and the center-disjoint sums A_i. Every support,
core, cover, type and rank is recomputed here from the operands; nothing is
read from the witness except the operand pairs and the root indices.
"""
import gzip, json, struct, sys, array
from fractions import Fraction
from itertools import combinations
from pathlib import Path


def write_array(f, values):
    """Little-endian array writer, as partial_swap.binary.write_array."""
    if sys.byteorder != 'little' and values.itemsize > 1:
        values = array.array(values.typecode, values)
        values.byteswap()
    values.tofile(f)


def build(witness, prefix):
    w = json.loads(gzip.decompress(Path(witness).read_bytes()))
    h, v, d = w['h'], w['v'], w['central_disjoint']
    assert h >= 12 and h%2 == 0 and (d,w['center_denominator']) == (h,h-3)
    triples = list(combinations(range(h), 3))
    assert v == len(triples)
    args = [(0, 0)]; support = [0]; core = [0]; cover = [0]; types = [0]; ranks = [0]
    for j, t in enumerate(triples):
        mask = sum(1 << a for a in t)
        args.append((0, 0)); support.append(1 << j); core.append(mask); cover.append(mask)
        types.append(1); ranks.append(1)
    flat = w['args']
    assert len(flat) % 2 == 0
    for k in range(0, len(flat), 2):
        a, b, x = flat[k], flat[k+1], len(args)
        assert 0 < a < x and 0 < b < x, 'Operands must precede their sum'
        assert not support[a] & support[b], 'Ordinary additions must be cancellation-free'
        args.append((a, b)); support.append(support[a] | support[b])
        core.append(core[a] & core[b]); cover.append(cover[a] | cover[b])
        if core[x].bit_count() >= 2:
            types.append(1); ranks.append(support[x].bit_count())
        else:
            types.append(2); ranks.append(cover[x].bit_count())
    n = len(args)
    point_masks = [sum(1 << j for j, t in enumerate(triples) if a in t) for a in range(h)]
    full_support = (1 << v) - 1
    roots, kind = [], []
    assert len(w['D']) == v
    for t, node in zip(triples, w['D']):
        assert 0 < node < n
        assert support[node] == full_support & ~(point_masks[t[0]]|point_masks[t[1]]|point_masks[t[2]])
        target_mask = sum(1 << a for a in t)
        if types[node] == 2:
            assert not cover[node] & target_mask
        else:
            assert types[node] == 1
            assert not support[node] & (point_masks[t[0]]^point_masks[t[1]]^point_masks[t[2]])
        roots.append(node); kind.append(0)
    stars = [(a, b, i) for a, b in combinations(range(h), 2) for i in range(h) if i not in (a, b)]
    assert len(w['P']) == len(stars)
    pair_outputs = {}
    for (a, b, i), node in zip(stars, w['P']):
        assert 0 < node < n
        assert support[node] == point_masks[a] & point_masks[b] & ~point_masks[i]
        assert types[node] == 1
        assert not support[node] & (point_masks[a]^point_masks[b]^point_masks[i])
        pair_outputs[a, b, i] = node
        roots.append(node); kind.append(0)
    assert len(w['A']) == d
    for i, node in enumerate(w['A']):
        assert 0 < node < n
        assert support[node] == full_support & ~point_masks[i]
        assert types[node] == 2 and cover[node] == ((1 << h)-1) ^ (1 << i)
        assert ranks[node] == h-1
        roots.append(node); kind.append(1)
    # Every A_i avoids i, so sum A_i = (h-3)T. The decoder is T=sum A_i/(h-3)
    # and the scatter is T-(1/2)sum_{i in target} A_i.
    decoder = Fraction(1, h-3)
    assert decoder == Fraction(1, h-3)
    scatter_coefficients = [decoder, decoder-Fraction(1, 2)]
    for coefficient in scatter_coefficients:
        odd_denominator = coefficient.denominator
        while odd_denominator % 2 == 0:
            odd_denominator //= 2
        assert (h-3) % odd_denominator == 0 and abs(coefficient) <= 1
    for source in triples:
        assert sum(i not in source for i in range(h))*decoder == 1
    Dset = set(range(d))
    for triple in triples:
        k = len(Dset.intersection(triple))
        assert 2*(3-k)-2*(d-k) == 2*(3-d)
    patterns = {}
    for target in triples:
        chosen = len(Dset.intersection(target))
        if chosen not in patterns:
            patterns[chosen] = target
    for chosen, target in patterns.items():
        target_set = set(target)
        for source in triples:
            k = len(Dset.intersection(source))
            total_coefficient = Fraction(2*(3-k)-2*(d-k), 2*(3-d))
            scalar = Fraction(len((target_set-Dset).intersection(source)), 2)
            scalar -= Fraction(len((target_set & Dset)-set(source)), 2)
            scalar += Fraction(chosen-1, 2)*total_coefficient
            assert scalar == Fraction(len(target_set.intersection(source))-1, 2)
    for j, t in enumerate(triples):
        masks = [point_masks[a] for a in t]
        two = (masks[0]&masks[1]&~masks[2]) | (masks[0]&masks[2]&~masks[1]) | (masks[1]&masks[2]&~masks[0])
        actual = 0
        for a, b in combinations(t, 2):
            excluded = next(i for i in t if i not in (a, b))
            actual |= support[pair_outputs[a, b, excluded]]
        assert actual == two
        assert masks[0]&masks[1]&masks[2] == 1 << j
    assert [((k-1)+(k == 0)-(k == 2)) for k in range(4)] == [0, 0, 0, 2]

    def contained(x, y):
        tx, ty = types[x], types[y]
        if tx == 1 and ty == 1: return not(core[y]&~core[x] or cover[x]&~cover[y])
        if tx in (1, 2) and ty == 2: return not cover[x]&~cover[y]
        return False
    active = [0]*n; stack = list(roots)
    while stack:
        x = stack.pop()
        if not x or active[x]: continue
        active[x] = 1
        if args[x][0]: stack.extend(args[x])
    degree = [0]*n
    for x in range(1, n):
        if active[x]:
            if types[x] == 1:
                assert core[x].bit_count() >= 2 and ranks[x] == support[x].bit_count()
            else:
                assert types[x] == 2 and ranks[x] == cover[x].bit_count()
        if active[x] and args[x][0]:
            for y in args[x]:
                assert y < x and contained(y, x), 'Binary frame nesting failed'
                degree[y] += 1
    for x in roots: degree[x] += 1
    H = [0]*(h+1); c = 0; loss = 0
    for x in range(1, n):
        if not active[x]: continue
        r = ranks[x]
        if args[x][0]:
            c += 1; H[r] += degree[x]-1; H[h-r] += 1
            for y in args[x]:
                assert r >= ranks[y]
                H[r-ranks[y]] += 1
        else: H[1] += degree[x]
    for x, k in zip(roots, kind):
        r = ranks[x]
        if k: H[r] += 1; H[h] += 1; loss += r
        else: H[h-1-r] += 1; H[1] += 1
    q = len(roots); R = c+q
    result = dict(h=h, v=v, c=c, q=q, R=R, loss=loss, central_disjoint=d, histogram=H,
                  rank_sum=sum(r*m for r, m in enumerate(H)))
    assert loss == h*(h-1) and result['rank_sum'] == h*R+2*loss
    result['center_denominator'] = h-3
    result['scalar_validation'] = dict(ordinary_supports_exact=True, centers_exact=True,
        center_decoder='sum A_i / '+str(h-3), scatter_coefficients=list(map(str, scatter_coefficients)),
        rational_scalar_identity_exact=True, mixed_center_scatter_exact=True, binary_frames_nested=True,
        binary_frames_nondegenerate=True)
    with open(str(prefix)+'.bin', 'wb') as f:
        f.write(struct.pack('<4I', h, v, n, q))
        write_array(f, array.array('I', (a for pair in args for a in pair)))
        write_array(f, array.array('Q', core)); write_array(f, array.array('Q', cover))
        write_array(f, array.array('I', roots)); write_array(f, array.array('I', kind))
        write_array(f, array.array('B', active))
    with open(str(prefix)+'.labels', 'wb') as f:
        write_array(f, array.array('I', ranks)); write_array(f, array.array('B', types))
    Path(str(prefix)+'.json').write_text(json.dumps(result, indent=2)+'\n')
    return result
