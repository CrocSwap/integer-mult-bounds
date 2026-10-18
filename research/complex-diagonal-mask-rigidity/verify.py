"""Exact finite evidence for PROOF.md; stdlib only, active under -O.

Arham-Tahir64 with substantial OpenAI Codex assistance. Apache-2.0.
The quantified completion theorem is a written proof, not a finite search.
"""
import argparse
from fractions import Fraction as F
import hashlib
from itertools import combinations, product
import json
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUTS = {
    'research/p112-single-lift/reference-geometry.json',
    'research/complex-frame-pair-decoders/PROOF.md',
    'research/complex-decoder-field-extension-seed44/PROOF.md',
}


def need(condition, message):
    if not condition:
        raise ValueError(message)


def pins():
    source = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    rows = [r for r in source['files'] if r['usage'] == 'input']
    need({r['path'] for r in rows} == INPUTS, 'source inventory')
    for row in rows:
        need(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest()
             == row['sha256'], 'source drift: ' + row['path'])


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def geometry():
    half = [s for s in product((-1, 1), repeat=8)
            if s[0] == 1 and s.count(-1) % 2 == 0]
    sparse = []
    for a, b in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0]*8
            row[a], row[b] = 2, 2*sign
            sparse.append(tuple(row))
    frame = [r for r in sparse if any(r[2*j] == 2 and
             abs(r[2*j+1]) == 2 for j in range(4))]
    roots = sorted(set(half + sparse) - set(frame))
    need((len(half), len(sparse), len(frame), len(roots)) == (64, 56, 8, 112),
         'E8/P112 inventory')
    need(all(dot(r, r) == 8 for r in half+sparse), 'root norms')
    source = json.loads((ROOT / 'research/p112-single-lift/reference-geometry.json')
                       .read_text(encoding='utf-8'))
    need(set(map(tuple, source['roots'])) == set(roots), 'pinned P112 lines')
    need(set(map(tuple, source['frame'])) == set(frame), 'pinned frame')
    return roots, half, source


# Gaussian-rational arithmetic for exact complex minors, without floats.
def z(x):
    return (F(x[0]), F(x[1])) if isinstance(x, tuple) else (F(x), F(0))


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def sub(a, b):
    return a[0]-b[0], a[1]-b[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def div(a, b):
    norm = b[0]*b[0]+b[1]*b[1]
    return ((a[0]*b[0]+a[1]*b[1])/norm,
            (a[1]*b[0]-a[0]*b[1])/norm)


def rank(matrix):
    a = [[z(x) for x in row] for row in matrix]
    if not a:
        return 0
    pivot = 0
    for col in range(len(a[0])):
        index = next((i for i in range(pivot, len(a)) if a[i][col] != z(0)), None)
        if index is None:
            continue
        a[pivot], a[index] = a[index], a[pivot]
        for i in range(pivot+1, len(a)):
            if a[i][col] == z(0):
                continue
            c = div(a[i][col], a[pivot][col])
            for j in range(col, len(a[0])):
                a[i][j] = sub(a[i][j], mul(c, a[pivot][j]))
        pivot += 1
        if pivot == len(a):
            break
    return pivot


def rank2(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length()-1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def basis(roots, forbidden):
    selected = []
    for i, row in enumerate(roots):
        if i not in forbidden and rank([roots[j] for j in selected]+[row]) > len(selected):
            selected.append(i)
        if len(selected) == 8:
            return selected
    raise ValueError('unchanged rows do not span eight dimensions')


def minor_fixture(roots, changes):
    support = set(changes)
    indices = basis(roots, support)+sorted(support)
    matrix = [[dot(roots[i], roots[j])//2 for j in indices] for i in indices]
    for a, i in enumerate(indices):
        if i in changes:
            matrix[a][a] = add(z(matrix[a][a]), z(changes[i]))
    got = rank(matrix)
    need(got == 8+len(support), 'exact changed-diagonal minor')
    # Upper bound is explicit: eight coordinate columns factor the Gram
    # matrix, and each correction is one additional rank-one matrix.
    return {'support': sorted(support), 'basis': indices[:8], 'rank': got,
            'diagonal_values': [[i, list(z(changes[i]))] for i in sorted(support)]}


def rejects(action, message):
    try:
        action()
    except ValueError:
        return message
    raise ValueError('control unexpectedly accepted: '+message)


def run():
    pins()
    roots, half, source = geometry()
    need(rank(roots) == 8 and rank(half) == 8, 'root ranks')
    zero_lines = [list(r) for r in half if sum(r) == 0]
    need(len(zero_lines) == 35, 'sharp half-root zero count')
    bounds = [F(0)]+[F(comb(k, k//2)*2**(8-k), 4) for k in range(2, 8)]+[F(35)]
    need(max(bounds) == 35 and max(bounds[:-1]) == 32, 'all active-coordinate bounds')
    x = [[dot(r, f)//4 for f in source['frame']] for r in roots]
    indexed = {tuple(r): row for r, row in zip(source['roots'], source['X'])}
    need(all(indexed[r] == row for r, row in zip(roots, x)), 'pinned coordinates')
    need(all(dot(x[i], x[j]) == dot(roots[i], roots[j])//2
             for i in range(112) for j in range(112)), 'all 12544 Gram entries')
    pairing = [sum(((dot(r, s)//4+1) % 2) << j for j, s in enumerate(roots)) for r in roots]
    need(rank2(pairing) == 9, 'binary pairing rank')
    costs = []
    for k in range(8):
        support = sum((row[k] != 0) << i for i, row in enumerate(x))
        costs.append(rank2([pairing[i] & support for i in range(112) if support >> i & 1]))
    need(costs == [8]*8, 'predecessor sharp coordinate cost 64')
    need(all(row >> i & 1 for i, row in enumerate(pairing)), 'singleton correction cost one')

    fixtures = [minor_fixture(roots, {i: (1, 0)}) for i in range(112)]
    fixtures += [minor_fixture(roots, {i: (0, 1)}) for i in range(112)]
    for s in range(13):
        fixtures.append(minor_fixture(roots, {i: ((-1)**i, i % 2) for i in range(s)}))
    punctures = []
    for p in range(13):
        live = [r for r in roots if r not in set(half[:p])]
        record = minor_fixture(live, {i: (1, 1) for i in range(12-p)})
        punctures.append({'deleted_half_roots': p, 'q': 20-p, 'fixture': record})

    controls = []
    controls.append(rejects(lambda: need(len(zero_lines) <= 34, 'false 34 bound'), 'false half-root bound 34'))
    controls.append(rejects(lambda: need(fixtures[0]['rank'] <= 8, 'rank-nine correction'), 'one changed diagonal at q=8'))
    controls.append(rejects(lambda: need(fixtures[226]['rank'] <= 9, 'rank-ten correction'), 'two changed diagonals at q=9'))
    controls.append(rejects(lambda: need(rank2([1, 2]) == 1, 'binary rank'), 'false pairing rank'))
    frame = list(map(tuple, source['frame']))
    controls.append(rejects(lambda: basis(frame, {0}), 'insufficient unchanged span'))
    frame_gram = [[dot(a, b)//2 for b in frame] for a in frame]
    frame_gram[0][0] += 1
    need(rank(frame_gram) == 8, 'outside-domain counterexample')
    controls.append(rejects(lambda: need(rank(frame_gram) == 9, 'false unqualified rigidity'), 'dropping redundancy hypothesis'))
    left, right = z((0, 1)), z((0, -1))
    need(mul(left, right) == z(1), 'ordinary-transpose phase fixture')
    controls.append(rejects(lambda: need(mul(left, (right[0], -right[1])) == z(1), 'conjugate transpose'), 'Hermitian substitution'))
    controls.append(rejects(lambda: need(dot(x[0], x[1])+1 == dot(roots[0], roots[1])//2,
                                         'off-diagonal drift'), 'altered off-diagonal entry'))
    need(len(controls) == 8, 'control coverage')
    singleton_minors = [{'port': i, 'basis': fixtures[i]['basis'],
                         'real_rank': fixtures[i]['rank'], 'imaginary_rank': fixtures[112+i]['rank']}
                        for i in range(112)]
    return {'status': 'PASS_COMPLEX_DIAGONAL_MASK_RIGIDITY', 'half_root_lines': 64,
            'sharp_zero_lines': zero_lines, 'antichain_bounds_k1_to_k8': list(map(str, bounds)),
            'p112_lines': 112, 'gram_entries': 12544, 'coordinate_costs': costs,
            'singleton_complex_minors': 224, 'singleton_minors': singleton_minors,
            'singleton_diagonal_values': [[1, 0], [0, 1]], 'one_correction_example_cost': 65,
            'support_count_fixtures': fixtures[224:], 'puncture_fixtures': punctures,
            'controls': controls, 'no_new_kappa': True}


def encoded(value):
    return json.dumps(value, indent=2, sort_keys=True, default=str)+'\n'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write', type=Path, help='write fresh receipt; never overwrite')
    args = ap.parse_args()
    receipt = json.loads(encoded(run()))
    if args.write:
        with args.write.open('x', encoding='utf-8', newline='\n') as output:
            output.write(encoded(receipt))
    else:
        need(receipt == json.loads((HERE/'RESULTS.json').read_text(encoding='utf-8')), 'receipt mismatch')
    print('PASS_COMPLEX_DIAGONAL_MASK_RIGIDITY half_roots=64 sharp_zeros=35 '
          'complex_singleton_minors=224 q=8..20 punctures=13 controls=8 no_new_kappa')


if __name__ == '__main__':
    main()
