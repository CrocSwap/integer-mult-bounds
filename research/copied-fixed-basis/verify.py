#!/usr/bin/env python3
"""Exact copied-center/fixed-I+J witness at dimensions (25,23).

Composition by Dominik Scholz with substantial GPT-6 Astra/Codex assistance.
Copied scheduling/assembly: icekylinx PR36. Fixed profiles: PR32/35.
Controlled permutations: Zhihao Chen PR29. Moment helper: Rohan Arun PR31/33.
Complete attribution and immutable inputs are recorded in SOURCE.json.
"""
from collections import Counter
from difflib import unified_diff
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import comb, factorial
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
REFERENCES = ROOT/'references/copied-fixed'
sys.path[:0] = [str(REFERENCES), str(ROOT/'scripts')]
from two_stage_unequal import prescriptions
from moment import moment_search
from copied_centers_network import profile as complex_profile, finite_bridge, AC
from partial_swap_network import moment
from structured_bulk_assembly import assembly, js
from structured_bulk.exactness import mersenne_prime

BIT_SAVING = Q(19432631, 500000000000)
KAPPA = Q(242889, 6250000000)
PREVIOUS_KAPPA = Q(384569, 10**10)


def check_sources():
    manifest = json.loads((HERE/'SOURCE.json').read_text())
    for name, record in manifest['files'].items():
        assert sha256((ROOT/name).read_bytes()).hexdigest() == record['sha256'], name
    return manifest


def tree(edges, vertices):
    assert len(edges) == vertices-1
    seen = {0}
    while True:
        expanded = seen | {v for u, v in edges if u in seen} | {u for u, v in edges if v in seen}
        if expanded == seen:
            break
        seen = expanded
    assert len(seen) == vertices


def physical_profile(axes, profiles):
    a, b = (row['h'] for row in axes)
    assert (a, b) == (25, 23)
    m, N = a*b, comb(a, 3)*comb(b, 3)
    B1, B2 = (N//row['v']*row['R'] for row in axes)
    W = 2*N+B1+B2
    loss = sum(N//row['v']*row['loss'] for row in axes)
    d = a+b-1
    children = Counter({a: B1, b: B2, m-2*a: B1, m-2*b: B2})
    children[1] += (d-(b-2))*2*N
    children[b-2] += 2*N
    children[m-2*d] += 2*N
    for axis, fixed in zip(axes, profiles):
        h, copies = axis['h'], N//axis['v']
        for width, count in enumerate(fixed['blocks']):
            children[width] += copies*count
        # Replace only each retained total's full-rank cleanup; keep its copy.
        assert fixed['blocks'][h] >= h
        children[h] -= h*copies
        children[1] += h*copies
        children[1] += 2*N
        children[h-2] += 2*N
    children[1] += N  # Paid endpoint correction on complete copied streams.
    children = dict(sorted((t, n) for t, n in children.items() if t and n))
    assert all(0 < t < m and n > 0 for t, n in children.items())
    rank = sum(t*n for t, n in children.items())
    assert rank == W*m-N+loss
    return dict(dimensions=[a, b], m=m, N=N, W=W, B1=B1, B2=B2,
                L=loss, total_rank=rank, deficit=N-loss, maxchild=max(children),
                child_multiplicities=children,
                data_profile=dict(singletons=26, blocks=[21, 481]))


def run():
    assert not sys.flags.optimize, 'Assertions must remain enabled'
    manifest = check_sources()
    primes = [mersenne_prime(e) for e in (61, 31, 19)]
    modulus = primes[0]*primes[1]*primes[2]
    axes, profiles, bounds = [], [], {}
    for h in (25, 23):
        producer = json.loads((HERE/f'producer-{h}.json').read_text())
        axis = producer['original']
        fixed = json.loads((HERE/f'profiles-{h}.json').read_text())
        assert axis['h'] == fixed['h'] == h and axis['v'] == comb(h, 3)
        assert axis['R'] == fixed['R'] and axis['loss'] == fixed['loss'] == h*(h-1)
        assert fixed['rank_sum'] == axis['rank_sum'] == h*axis['R']+2*axis['loss']
        assert fixed['rank_sum'] == sum(t*n for t, n in enumerate(fixed['blocks']))
        assert fixed['field_prime'] == primes[0] and fixed['crt_disagreements'] == 0
        Z = 3*h-7
        B0 = (4*h-2)*Z+27*(h+1)
        D, B = 3*(h+1)*(h-1)**2, 2*(h-1)*B0
        minors = {r: sum(comb(h, j)*factorial(j)*B**j*D**(r-j)
                         for j in range(r+1)) for r in (2, 3, 4)}
        assert minors[2] < primes[0] and max(minors[3], minors[4]) < modulus
        assert 3*(h+1)*(h-1) < min(primes)
        bounds[h] = dict(common_denominator=D, numerator_bound=B,
                         single_numerator_bound=B0, minor_bounds=minors)
        axes.append(axis)
        profiles.append(fixed)
    bit = physical_profile(axes, profiles)
    a, b = bit['dimensions']
    m, d = bit['m'], a+b-1
    permutations = prescriptions(a, b)
    assert all(sorted(p) == list(range(a)) for p in permutations)
    row_edges = [(permutations[i%b][i//b], a+i%b) for i in range(d)]
    col_edges = [(permutations[i%b][i//b], a+i%b) for i in range(m-d, m)]
    tree(row_edges, a+b)
    tree(col_edges, a+b)
    exact = moment_search(m, bit['W'], bit['child_multiplicities'])
    assert exact['saving'] == BIT_SAVING and exact['next_moment_upper'] >= 1
    complex_axis = json.loads((ROOT/'certificates/copied-centers-complex-input.json').read_text())
    phase = complex_profile([complex_axis, complex_axis])
    complex_moment = moment(phase['m'], phase['W'], phase['child_multiplicities'], AC, True)
    inherited = json.loads((ROOT/'certificates/copied-centers-input.json').read_text())
    assert complex_moment['strict_gap'] == Q(inherited['complex_moment_gap'])
    for name, value in inherited['complex'].items():
        assert js(phase[name]) == value, name
    bridge = finite_bridge(bit, phase, [complex_axis, complex_axis])
    assert js(bridge) == inherited['finite_bridge']
    assembled = assembly(BIT_SAVING, AC, bridge, KAPPA)
    assert len(assembled['strict_constraints']) == 47 and len(assembled['margins']) == 7
    assert KAPPA > PREVIOUS_KAPPA
    negatives = []
    for name, operation in [
            ('next_kappa_grid', lambda: assembly(BIT_SAVING, AC, bridge, KAPPA+Q(1, 10**12))),
            ('missing_tree_edge', lambda: tree(row_edges[:-1], a+b))]:
        try:
            operation()
        except AssertionError:
            negatives.append(name)
        else:
            raise AssertionError('Negative control accepted: '+name)
    assert bit['total_rank']+bit['L'] >= bit['W']*m
    negatives.append('omit_copied_schedule_loses_rank_deficit')
    without_data = Counter(bit['child_multiplicities'])
    without_data[21] -= 2*bit['N']
    without_data[1] += 42*bit['N']
    assert moment_search(m, bit['W'], without_data)['saving'] < BIT_SAVING
    negatives.append('omit_data_block_lowers_saving')
    paths = list(HERE.glob('*.py'))+[HERE/'rankone_profiles.cpp', HERE/'SOURCE.json',
             HERE/'README.md', ROOT/'notes/copied-fixed-basis.tex']
    return dict(status='Conditional exact finite witness; not formal verification',
                kappa=KAPPA, previous_kappa=PREVIOUS_KAPPA,
                relative_improvement=KAPPA/PREVIOUS_KAPPA-1,
                basis='Both axes I+J; original envelopes and oriented matching; PR36 base2 graph',
                bit=dict(counts=bit, **exact), complex=dict(counts=phase, **complex_moment),
                finite_bridge=bridge, assembly=assembled, exactness=dict(primes=primes,
                prime_product=modulus, bounds=bounds), basis_permutations=permutations,
                corner_trees=dict(rows=row_edges, columns=col_edges),
                negative_controls=negatives, adopted_sources=manifest,
                source_sha256={str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                               for p in sorted(paths)})


if __name__ == '__main__':
    result = run()
    (HERE/'certificate.json').write_text(json.dumps(js(result), indent=2, sort_keys=True)+'\n')
    old = (REFERENCES/'copied-centers-note.tex').read_text()
    new = (ROOT/'notes/copied-fixed-basis.tex').read_text()
    patch = ''.join(unified_diff(old.splitlines(keepends=True), new.splitlines(keepends=True),
                                fromfile='a/notes/copied-centers-note.tex',
                                tofile='b/notes/copied-centers-note.tex'))
    (ROOT/'patches/copied-fixed-basis.patch').write_text(patch)
    print('PASS conditional kappa', KAPPA, 'bit', BIT_SAVING)
    print('moment gap', float(result['bit']['strict_gap']),
          'assembly gap', float(result['assembly']['absorption_gap']))
