#!/usr/bin/env python3
"""Exact bounded no-change census; no floating moment is used as evidence.

Apache-2.0. Substantial OpenAI Codex assistance. No full multiplier claim.
"""
from collections import Counter
from hashlib import sha256
from itertools import product
from pathlib import Path
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    pins = json.loads((HERE / 'SOURCES.json').read_text())
    for row in pins['files']:
        if row['usage'] == 'input':
            actual = (ROOT / row['path']).read_bytes()
            need(sha256(actual).hexdigest() == row['sha256'], 'Source bytes: ' + row['path'])


def load_model():
    spec = importlib.util.spec_from_file_location('commuting_warp_model', HERE / 'search.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def histogram(model, edges, changed):
    result = Counter()
    for a, b, kind in edges:
        fa, fb = model.frame(a, changed), model.frame(b, changed)
        need(model.valid(fa, fb, kind), 'Every actual proposed edge is legal')
        rank = model.dims[fb] - model.dims[fa]
        need(0 <= rank <= 9, 'Actual paid rank')
        if rank:
            result[rank] += 1
    return result


def scalar_matrix(gate):
    out = [[int(i == j) for j in range(3)] for i in range(3)]
    out[gate[1][1]][gate[2][1]] = gate[3]
    return out


def multiply(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(a)))
             for j in range(len(a))] for i in range(len(a))]


def controls(module):
    # A tiny exact matrix interpreter checks the commutation test, including
    # common-target and common-source ADDs and genuinely noncommuting cases.
    gates = [['add', ['L', a], ['L', b], 1, 1]
             for a in range(3) for b in range(3) if a != b]
    accepted = rejected = 0
    for g, h in product(gates, repeat=2):
        a, b = ['scalar', g, 0], ['scalar', h, 0]
        if len(set(module.roles(a)) & set(module.roles(b))) != 1:
            continue
        commute = multiply(scalar_matrix(g), scalar_matrix(h)) == multiply(scalar_matrix(h), scalar_matrix(g))
        need(module.commuting_pair(a, b) == commute, 'Independent scalar matrix commutation')
        accepted += int(commute)
        rejected += int(not commute)
    need(accepted == 12 and rejected == 12, 'Three-role scalar fixture coverage')

    # This is a changed-map control. The line-incidence condition cannot be
    # dropped merely because the two late subspaces have equal dimensions.
    model = module.Model.__new__(module.Model)
    model.spaces = [frozenset(s) for s in ({0}, {0, 1}, {0, 2}, {0, 1, 2, 3})]
    model.dims = [0, 1, 1, 2]
    model.lines = {47: (1, 1)}
    need(model.valid(1, 2, 48), 'Free changed map can move a line')
    need(not model.valid(1, 2, 47), 'Shared prelude line forbids conflicting late transport')
    need(not model.valid(2, 1, 47), 'An outside line cannot map into an equal-dimensional image')
    need(model.valid(2, 3, 47), 'Larger cap can contain the extra prescribed image')
    need(not model.valid(1, 2, 0), 'Ordinary transport still requires containment')

    # Independently count the finite Grassmannians through the largest actual
    # quotient, and compare every emitted space rather than trusting labels.
    interval = sys.modules['intervals']
    counts = []
    for q, expected in enumerate((1, 2, 5, 16, 67, 374)):
        spaces = {interval.closure(b) for b in interval.subspaces(q)}
        gaussian = 0
        for d in range(q + 1):
            numerator = denominator = 1
            for i in range(d):
                numerator *= 2 ** (q - i) - 1
                denominator *= 2 ** (d - i) - 1
            need(numerator % denominator == 0, 'Integral Gaussian binomial')
            gaussian += numerator // denominator
        need(len(spaces) == gaussian == expected, 'Complete RREF enumeration')
        counts.append(expected)
    return {'exact_scalar_matrix_pairs': accepted + rejected,
            'commuting_pairs': accepted, 'noncommuting_pairs_rejected': rejected,
            'wrong_shared_map_rejected': True,
            'ordinary_noncontainment_rejected': True,
            'subspace_counts_dimension_zero_through_five': counts}


def run():
    authenticate()
    module = load_model()
    model = module.Model(discovery_price=False)
    # Reconstruct every paid transition from the chronological source word.
    # This also checks that replacing the source late-warp splits by one
    # optimistic consolidated transition has not already improved its bill.
    actual = Counter(e[5] for e in model.payload['programs']['forward'] if e[0] == 'climb')
    need(histogram(model, model.edges, {}) == actual, 'Graph equals full actual source paid-climb census')
    actual.update(e[4] for e in model.payload['programs']['forward'] if e[0] == 'center')
    need(actual == {1: 2201, 2: 412, 3: 510, 4: 127, 5: 40, 8: 8}, 'Complete source bill includes all centers')
    all_pairs = [i for i, (a, b) in enumerate(zip(model.raw, model.raw[1:])) if module.commuting_pair(a, b)]
    need(len(all_pairs) == 9829, 'Complete adjacent commuting-pair inventory')
    pairs = list(model.candidates())
    need(len(pairs) == 98, 'Complete movable-warp pair inventory')
    rows = []
    feasible_total = frame_pairs = 0
    for i in pairs:
        variables = {i, i + 1}
        edges = [e for e in model.graph(i) if e[0] in variables or e[1] in variables]
        old_edges = [e for e in model.edges if e[0] in variables or e[1] in variables]
        before = histogram(model, old_edges, {})
        da, db = (model.domain(n, edges, variables) for n in (i, i + 1))
        feasible = 0
        for f, g in product(da, db):
            changed = {i: f, i + 1: g}
            if not all(model.valid(model.frame(a, changed), model.frame(b, changed), kind)
                       for a, b, kind in edges):
                continue
            after = histogram(model, edges, changed)
            need(before == after, 'Every feasible retimed swap preserves exact paid histogram')
            feasible += 1
        frame_pairs += len(da) * len(db)
        feasible_total += feasible
        rows.append({'event': i, 'domain_sizes': [len(da), len(db)],
                     'feasible_assignments': feasible,
                     'incident_paid_before': dict(sorted(before.items())),
                     'free_operators': sorted({k for _, _, k in edges if k})})
    need('skipped_large_interval' not in model.stats, 'Every actual domain fully enumerated')
    need(frame_pairs == 1077 and feasible_total == 74, 'Exact finite census totals')
    need(sum(r['feasible_assignments'] == 0 for r in rows) == 24, 'Infeasible swap count')
    result = {'status': 'PASS_EXACT_COMMUTING_WARP_NO_PAID_CHANGE',
              'source_payload_sha256': sha256(__import__('gzip').decompress(model.source_bytes)).hexdigest(),
              'adjacent_commuting_pairs': len(all_pairs), 'movable_warp_pairs': len(pairs),
              'fixed_warp_pairs_outside_scope': len(all_pairs) - len(pairs),
              'frame_assignments': frame_pairs, 'feasible_assignments': feasible_total,
              'infeasible_swaps': 24, 'identical_paid_histogram_assignments': feasible_total,
              'interval_stats': dict(sorted(model.stats.items())),
              'complete_source_paid': dict(sorted(actual.items())),
              'pairs': rows, 'controls': controls(module), 'new_kappa': False}
    return json.loads(json.dumps(result))


if __name__ == '__main__':
    result = run()
    if sys.argv[1:] == ['--write']:
        (HERE / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    else:
        need(not sys.argv[1:], 'No unrecognized verification arguments')
        need(result == json.loads((HERE / 'RESULT.json').read_text()), 'Deterministic exact receipt')
    print(json.dumps({k: v for k, v in result.items() if k != 'pairs'}, sort_keys=True))
