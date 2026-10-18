# SPDX-License-Identifier: Apache-2.0
# Jeremy Diviney, with substantial OpenAI Codex assistance.
"""Solver-free clique census, exact counterexamples and failure controls."""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cliques


def require(ok, message):
    if not ok:
        raise ValueError(message)


def low_pivot_rank(values):
    basis = {}
    for row in values:
        while row:
            bit = row & -row
            if bit in basis:
                row ^= basis[bit]
            else:
                basis[bit] = row
                break
    return len(basis)


def separate_census(model):
    """Set-based adjacency and tuple recursion, independent of cliques.py."""
    roots, live = model['lines'], model['live']
    neighbors = {i: {j for j in live if j > i and sum(a*b for a, b in zip(roots[i], roots[j])) == 0} for i in live}
    found = set()

    def visit(chosen, allowed):
        for i in sorted(allowed):
            group = chosen + (i,)
            found.add(sum(1 << j for j in group))
            visit(group, allowed.intersection(neighbors[i]))

    visit((), set(live))
    return found


def reconstruct_root_set():
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            x = [0] * 8
            x[i], x[j] = 2, 2*sign
            roots.add(tuple(x))
    for tail in product((-1, 1), repeat=7):
        x = (1,) + tail
        if sum(v < 0 for v in x) % 2 == 0:
            roots.add(x)
    return roots


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-certificate', action='store_true', help='explicitly regenerate package-local expected evidence')
    args = ap.parse_args()
    raw = (HERE / 'GEOMETRY.json').read_bytes()
    pins = json.loads((HERE / 'PREDECESSORS.json').read_text())
    require(hashlib.sha256(raw).hexdigest() == pins['geometry_sha256'], 'pinned geometry bytes')
    model = json.loads(raw)
    roots, live, puncture = model['lines'], model['live'], model['punctured_frame']
    require({tuple(x) for x in roots} == reconstruct_root_set() and len(roots) == 120, 'independent E8 root-set reconstruction')
    require(all(sum(x*x for x in r) == 8 for r in roots), 'norm eight')
    require(len(puncture) == 8 and set(live) == set(range(120)) - set(puncture) and len(live) == 112, 'exact puncture')
    require(all(sum(a*b for a, b in zip(roots[i], roots[j])) == 0 for i, j in combinations(puncture, 2)), 'orthogonal punctured frame')
    gram, binary, supports = cliques.geometry(model)
    full = cliques.all_orthogonal_sets(live, gram)
    separate = separate_census(model)
    require(len(full) == len(set(full)) and set(full) == separate, 'two complete clique enumerations')
    historical = cliques.frame_subsets(full)
    omitted = set(full) - historical
    census = {str(k): v for k, v in sorted(Counter(q.bit_count() for q in full).items())}
    require(census == {'1': 112, '2': 3304, '3': 31024, '4': 94892, '5': 82656, '6': 39088, '7': 10592, '8': 1260}, 'complete clique size census')
    require(len(historical) == 227696 and len(omitted) == 35232, 'frame-subset gap')
    examples = json.loads((HERE / 'CANDIDATES.json').read_text())
    checked = []
    live_mask = sum(1 << i for i in live)
    factors_by_name = {}
    for example in examples:
        factors = cliques.decode_terms(example['terms'], supports, live_mask)
        factors_by_name[example['name']] = factors
        costs = [cliques.pairing_rank(binary, L, R) for L, R in factors]
        other = [low_pivot_rank([binary[i] & R for i in live if L >> i & 1]) for L, R in factors]
        require(costs == other == example['pairing_ranks'], 'separate literal pairing-rank invoices')
        require(len(factors) == 9 and sum(costs) == example['copy_bill'] == 63, 'nine terms at cost 63')
        require(not cliques.rank_violations(factors, historical), 'fixture passes every frame-contained demand')
        bad = cliques.rank_violations(factors, full)
        require(len(bad) == 6, 'six exact full-clique failures')
        for witness in bad:
            vertices = witness['roots']
            q = sum(1 << i for i in vertices)
            require(q in omitted, 'failure is outside every full frame')
            require(all(sum(a*b for a, b in zip(roots[i], roots[j])) == 0 for i, j in combinations(vertices, 2)), 'literal witness orthogonality')
            available = [k for k, (L, R) in enumerate(factors) if any(L >> i & 1 for i in vertices) and any(R >> i & 1 for i in vertices)]
            require(available == witness['available_terms'] and len(available) < len(vertices), 'separate rank obstruction')
        checked.append({'name': example['name'], 'terms': 9, 'copy_bill': sum(costs),
                        'frame_subset_violations': 0, 'full_clique_violations': bad,
                        'is_decoder': False})
    coordinate = [(supports[2*a], supports[2*a]) for a in puncture]
    cliques.require_rank_demands(coordinate, full)
    require(sum(cliques.pairing_rank(binary, L, R) for L, R in coordinate) == 64, 'positive control invoice')
    for i in live:
        for j in live:
            total = sum(gram[i][a] * gram[j][a] for a in puncture)
            require(total == 2 * gram[i][j], 'positive control exact factorization')
            if i == j: require(total == 4, 'required diagonal one')
            elif gram[i][j] == 0: require(total == 0, 'required off-diagonal zero')
    controls = []
    for name, factors in factors_by_name.items():
        cliques.require_rank_demands(factors, historical)
        try:
            cliques.require_rank_demands(factors, full)
        except ValueError:
            controls.append('reject_' + name)
        else:
            raise ValueError('incomplete rank guard accepted invalid decoder fixture')
    altered = deepcopy(examples[0]['terms'])
    altered[0][2] = format(int(altered[0][2], 16) | (1 << puncture[0]), 'x')
    try:
        cliques.decode_terms(altered, supports, live_mask)
    except ValueError:
        controls.append('reject_nonlive_cut_bit')
    else:
        raise ValueError('invalid support encoding accepted')
    try:
        require(historical == separate, 'complete orthogonal-set domain')
    except ValueError:
        controls.append('reject_maximum_frame_subsets_as_complete_domain')
    else:
        raise ValueError('weak domain passed complete clique comparison')
    try:
        cliques.require_rank_demands(coordinate[:-1], full)
    except ValueError:
        controls.append('reject_missing_coordinate_term')
    else:
        raise ValueError('rank-seven factor list accepted on rank-eight frame')
    certificate = {'status': 'PASS_P112_COMPLETE_ORTHOGONAL_CLIQUE_AUDIT',
                   'geometry_sha256': hashlib.sha256(raw).hexdigest(),
                   'all_nonempty_orthogonal_sets': len(full), 'by_size': census,
                   'full_frames': 1260, 'frame_contained_nonempty_sets': len(historical),
                   'outside_full_frames': len(omitted),
                   'outside_by_size': {str(k): v for k, v in sorted(Counter(q.bit_count() for q in omitted).items())},
                   'candidates': checked, 'positive_control': {'copy_bill': 64, 'exact_entries': 12544, 'rank_violations': 0},
                   'failure_controls': controls, 'new_kappa': None,
                   'scope': 'Finite census, explicit counterexamples and necessary-condition guard. Not a decoder, global COPY floor, native supplier, full multiplication theorem or Lean proof.'}
    path = HERE / 'CERTIFICATE.json'
    if args.write_certificate:
        path.write_text(json.dumps(certificate, indent=2) + '\n')
    else:
        require(json.loads(path.read_text()) == certificate, 'saved canonical certificate')
    print(certificate['status'], '262928 cliques; 35232 outside full frames; two invalid cost-63 fixtures; five failure controls')


if __name__ == '__main__':
    main()
