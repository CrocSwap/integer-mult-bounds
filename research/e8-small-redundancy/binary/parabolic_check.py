"""Check the eight root-hyperplane types with exact arithmetic."""
import gzip
import json
from fractions import Fraction
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / 'inputs/bit-word.json.gz'
ROOTS = json.load(gzip.open(SOURCE, 'rt'))['lines']


def rank2(words):
    pivots = {}
    for word in words:
        while word:
            p = word.bit_length() - 1
            if p not in pivots:
                pivots[p] = word
                break
            word ^= pivots[p]
    return len(pivots)


def basis2(words):
    pivots = {}
    for word in words:
        while word:
            p = word.bit_length() - 1
            if p not in pivots:
                pivots[p] = word
                break
            word ^= pivots[p]
    return list(pivots.values())


def rankq(rows):
    pivots = {}
    for raw in rows:
        row = list(map(Fraction, raw))
        for p, basis in sorted(pivots.items()):
            if row[p]:
                f = row[p]
                row = [x - f*y for x,y in zip(row,basis)]
        if any(row):
            p = next(i for i,x in enumerate(row) if x)
            f = row[p]
            pivots[p] = [x/f for x in row]
            if len(pivots) == 8:
                return 8
    return len(pivots)


def rankmod(rows, prime=101):
    pivots = {}
    for raw in rows:
        row = [x % prime for x in raw]
        for p, basis in sorted(pivots.items()):
            if row[p]:
                f = row[p]
                row = [(x - f*y) % prime for x,y in zip(row,basis)]
        if any(row):
            p = next(i for i,x in enumerate(row) if x)
            f = pow(row[p], -1, prime)
            pivots[p] = [(x*f) % prime for x in row]
            if len(pivots) == 8:
                return 8
    return len(pivots)


def rank(rows):
    value = rankmod(rows)
    return 8 if value == 8 else rankq(rows)


all_roots = {tuple(q) for q in ROOTS} | {tuple(-x for x in q) for q in ROOTS}
assert len(ROOTS) == 120 and len(all_roots) == 240
assert all(sum(x*x for x in q) == 4 for q in all_roots)
for q in all_roots:
    for r in all_roots:
        dot = sum(x*y for x,y in zip(q,r))
        assert dot % 2 == 0
        assert tuple(x - (dot//2)*y for x,y in zip(q,r)) in all_roots
positive = set()
for q in ROOTS:
    if next(x for x in q if x) < 0:
        q = [-x for x in q]
    positive.add(tuple(q))
simple = sorted(q for q in positive if not any(tuple(x-y for x,y in zip(q,p)) in positive for p in positive))
assert len(simple) == 8 and rankq(simple) == 8
code_basis = basis2(sum((1 ^ (sum(x*y for x,y in zip(q,r))//2 & 1)) << j for j,r in enumerate(ROOTS)) for q in ROOTS)
assert len(code_basis) == 9
code = [0]
for word in code_basis:
    code += [x ^ word for x in code]
assert all(rank([ROOTS[j] for j in range(120) if word >> j & 1]) == 8 for word in code[1:])
result = {'simple_roots':simple,'gram':[[sum(x*y for x,y in zip(q,r))//2 for r in simple] for q in simple], 'code_basis':code_basis, 'code_weight_histogram':{},'hyperplanes':[]}
for word in code:
    w = word.bit_count()
    result['code_weight_histogram'][w] = result['code_weight_histogram'].get(w,0)+1
for delete in range(8):
    hb = simple[:delete] + simple[delete+1:]
    inside = [j for j,q in enumerate(ROOTS) if rank(hb+[q]) == 7]
    outside = [j for j in range(120) if j not in inside]
    good = []
    histogram = {}
    for index,word in enumerate(code):
        r = rank([ROOTS[j] for j in outside if word >> j & 1])
        histogram[r] = histogram.get(r,0)+1
        if r <= 7:
            good.append(index)
    item={'delete':delete,'inside':inside,'inside_count':len(inside),'outside_rank_histogram':histogram,'good_messages':good,'good_message_span':rank2(good)}
    result['hyperplanes'].append(item)
    print(delete,len(inside),histogram,'good span',rank2(good),flush=True)
Path(__file__).with_name('parabolic-results.json').write_text(json.dumps(result,indent=2)+'\n')

root_code = [sum((1 ^ (sum(x*y for x,y in zip(q,r))//2 & 1)) << j for j,r in enumerate(ROOTS)) for q in ROOTS]
message_of_word = {word:i for i,word in enumerate(code)}
for item in result['hyperplanes']:
    inside = item['inside']
    outside = [j for j in range(120) if j not in inside]
    h = set(inside)
    good_words = {code[i] for i in item['good_messages']}
    if len(inside) != 63:
        assert good_words == {0} | {root_code[q] for q in inside}
        for q in inside:
            support = [ROOTS[j] for j in outside if root_code[q] >> j & 1]
            assert rankq(support) == 7
            assert all(sum(x*y for x,y in zip(ROOTS[q],r)) == 0 for r in support)
        item['structure'] = 'zero and K_q for q in H; each outside support spans q-perp'
    else:
        normals = [q for q in outside if all(sum(x*y for x,y in zip(ROOTS[q],ROOTS[r])) == 0 for r in inside)]
        assert len(normals) == 1
        normal = normals[0]
        t = root_code[normal]
        assert [j for j in range(120) if t >> j & 1] == sorted(inside+[normal])
        assert good_words == {0,t} | {root_code[q] ^ extra for q in inside for extra in (0,t)}
        for q in inside:
            for extra in (0,t):
                support = [ROOTS[j] for j in outside if (root_code[q] ^ extra) >> j & 1]
                assert rankq(support) == 7
                assert all(sum(x*y for x,y in zip(ROOTS[q],r)) == 0 for r in support)
        neighbors = {q:{r for r in inside if r != q and sum(x*y for x,y in zip(ROOTS[q],ROOTS[r])) != 0} for q in inside}
        assert all(rankq([ROOTS[r] for r in neighbors[q]]) == 7 for q in inside)
        common = [len(neighbors[q] & neighbors[r]) for i,q in enumerate(inside) for r in inside[i+1:]]
        assert min(common) > 0
        item['structure'] = 'zero, t, K_q and K_q+t for q in H; other outside supports span q-perp'
        item['normal'] = normal
        item['neighbor_ranks'] = [7] * len(inside)
        item['common_neighbor_min'] = min(common)
        item['common_neighbor_max'] = max(common)
        print('E7 common nonorthogonal neighbors:',min(common),max(common),flush=True)
result['structural_checks_passed'] = True
Path(__file__).with_name('parabolic-results.json').write_text(json.dumps(result,indent=2)+'\n')
