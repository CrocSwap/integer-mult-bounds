#!/usr/bin/env python3
"""Independent Fraction / reflection-orbit check; imports no primary code.

Reconstructs 240 signed roots, enumerates code by XOR closure, and computes
rational costs only at orbit representatives. Literal isometries transport
those costs to all 255 cases, checking every primary rank table and witness.
Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def check(ok, message):
    if not ok:
        raise ValueError(message)


def sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def normalize(root):
    return root if next(x for x in root if x) > 0 else tuple(-x for x in root)


def reconstruct():
    signed = set()
    for a, b in combinations(range(8), 2):
        for x, y in product((-2, 2), repeat=2):
            r = [0] * 8
            r[a], r[b] = x, y
            signed.add(tuple(r))
    for r in product((-1, 1), repeat=8):
        if sum(x < 0 for x in r) % 2 == 0:
            signed.add(r)
    check(len(signed) == 240, '240 signed roots')
    return sorted({normalize(r) for r in signed})


def closed_span(generators):
    out = {0}
    for g in generators:
        if g not in out:
            out |= {v ^ g for v in out}
    return out


def f2rank(words):
    # Low-column Gaussian elimination, independent of the primary high-bit basis.
    rows = list(words)
    rank = 0
    for bit in range(120):
        pivot = next((i for i in range(rank, len(rows)) if (rows[i] >> bit) & 1), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for i in range(rank + 1, len(rows)):
            if (rows[i] >> bit) & 1:
                rows[i] ^= rows[rank]
        rank += 1
    return rank


def qrank(rows):
    # Literal rational row echelon form; no modular rank assumption.
    rows = [[Q(x) for x in row] for row in rows]
    height = 0
    for col in range(8):
        pivot = next((i for i in range(height, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[height], rows[pivot] = rows[pivot], rows[height]
        divisor = rows[height][col]
        rows[height] = [x / divisor for x in rows[height]]
        for i in range(height + 1, len(rows)):
            divisor = rows[i][col]
            if divisor:
                rows[i] = [x - divisor * y for x, y in zip(rows[i], rows[height])]
        height += 1
    return height


def move(word, permutation):
    result = 0
    while word:
        bit = word & -word
        result |= 1 << permutation[bit.bit_length() - 1]
        word -= bit
    return result


def generators(roots):
    simple = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0)]
    simple += [tuple(-2 if j == i else 2 if j == i + 1 else 0 for j in range(8)) for i in range(6)]
    index = {r: i for i, r in enumerate(roots)}
    permutations = []
    for a in simple:
        check(sum(x * x for x in a) == 8, 'reflection norm')
        perm = []
        for r in roots:
            coefficient = Q(sum(x * y for x, y in zip(r, a)), 4)
            v = normalize(tuple(Q(x) - coefficient * y for x, y in zip(r, a)))
            check(all(x.denominator == 1 for x in v), 'integral reflected root')
            perm.append(index[v])
        check(sorted(perm) == list(range(120)), 'reflection permutation')
        permutations.append(perm)
    return permutations


def transport_orbit(start, permutations):
    transports = {start: list(range(120))}
    queue = [start]
    for old in queue:
        for perm in permutations:
            new = move(old, perm)
            if new not in transports:
                transports[new] = [perm[j] for j in transports[old]]
                queue.append(new)
    return transports


def check_summary(summary, words, costs):
    dim = f2rank(words)
    filtration = [f2rank(w for w in words if costs[w] <= d) for d in range(9)]
    minimum = sum(dim - filtration[d] for d in range(8))
    histogram = {str(k): v for k, v in sorted(Counter(costs[w] for w in words if w).items())}
    check(summary['dimension'] == dim, 'target/ambient dimension')
    check(summary['filtration'] == filtration, 'rank filtration')
    check(summary['rank_histogram'] == histogram, 'rational rank histogram')
    check(summary['cost'] == minimum, 'minimum basis invoice')


def check_witness(summary, words, costs):
    selected = [int(w) for w in summary['basis']]
    check(all(w in words and w for w in selected), 'witness membership')
    check(len(selected) == summary['dimension'] == f2rank(selected), 'witness independence')
    check(closed_span(selected) == set(words), 'witness spanning')
    check([costs[w] for w in selected] == summary['basis_ranks'], 'witness physical ranks')
    check(sum(costs[w] for w in selected) == summary['cost'], 'witness total charge')


def run(certificate):
    for source in json.loads((HERE / 'SOURCES.json').read_text())['retained_sources']:
        data = (HERE / source['local_path']).read_bytes()
        check(hashlib.sha256(data).hexdigest() == source['sha256'], 'source hash')
    roots = reconstruct()
    check([list(r) for r in roots] == certificate['root_order'], 'root order')
    rows = []
    for r in roots:
        bits = [int(1 + Q(sum(a * b for a, b in zip(r, s)), 4)) % 2 for s in roots]
        rows.append(sum(bit << i for i, bit in enumerate(bits)))
    full_code = closed_span(rows)
    check(Counter(w.bit_count() for w in full_code) == {0: 1, 56: 255, 64: 255, 120: 1}, 'complete code weights')
    punctures = {w for w in full_code if w.bit_count() == 56}
    permutations = generators(roots)
    for perm in permutations:
        check({move(w, perm) for w in full_code} == full_code, 'code equivariance')
    cases = {int(c['deleted']): c for c in certificate['cases']}
    check(len(cases) == len(certificate['cases']) == 255 and set(cases) == punctures, 'all first-rank-drop punctures')
    full = (1 << 120) - 1
    visited = set()
    stats = []
    representative_rank_calls = 0
    for orbit in certificate['orbit_classes']:
        start = int(orbit['representative'])
        check(start in punctures, 'representative membership')
        transports = transport_orbit(start, permutations)
        check(not visited & transports.keys(), 'disjoint orbits')
        visited |= transports.keys()
        check(len(transports) == orbit['size'], 'orbit size')
        check(sha([str(w) for w in sorted(transports)]) == orbit['members_sha256'], 'orbit membership digest')
        live = full ^ start
        available = {w & live for w in full_code}
        needed = closed_span(rows[t] & live for t in range(120) if live >> t & 1)
        costs = {w: qrank([root for t, root in enumerate(roots) if w >> t & 1]) for w in available}
        representative_rank_calls += len(costs)
        check_summary(orbit['available'], available, costs)
        check_summary(orbit['required'], needed, costs)
        best = min(orbit['available']['cost'], orbit['required']['cost'])
        check(orbit['optimal_star_cost'] == best and orbit['ratio'] == str(Q(best, 64)), 'orbit optimum')
        stats.append((len(transports), f2rank(needed), best))
        for deleted, transport in transports.items():
            case = cases[deleted]
            moved_costs = {move(w, transport): cost for w, cost in costs.items()}
            moved_needed = {move(w, transport) for w in needed}
            live = full ^ deleted
            check(moved_needed == closed_span(rows[t] & live for t in range(120) if live >> t & 1), 'transported target code')
            check(set(moved_costs) == {w & live for w in full_code}, 'transported ambient code')
            table = [[str(w), moved_costs[w]] for w in sorted(moved_costs)]
            check(case['rank_table_sha256'] == sha(table), 'all-case rational rank table')
            for key, words in [('available', set(moved_costs)), ('required', moved_needed)]:
                for field in ['dimension', 'filtration', 'cost', 'rank_histogram', 'basis_ranks']:
                    check(case[key][field] == orbit[key][field], 'case summary: ' + field)
                check_witness(case[key], words, moved_costs)
            check(case['optimal_star_cost'] == best and case['ratio'] == str(Q(best, 64)), 'case optimum')
    check(visited == punctures, 'orbit coverage')
    check(sorted(stats) == [(120, 7, 50), (135, 8, 57)], 'two-class result')
    # Separate all-rank-profile check of the inherited capacity relaxation.
    caps = certificate['standard_flat_capacities']
    check(caps == [0, 1, 3, 6, 12, 20, 36, 63, 120], 'inherited capacity table')
    from itertools import combinations_with_replacement
    lower = min(sum(profile) for profile in combinations_with_replacement(range(1, 9), 9)
                if all(caps[a] + caps[b] >= 28 for a, b in combinations(profile, 2)))
    check(lower == certificate['rank_retained_lower_bound'] == 44, 'retained rank-nine relaxation')
    print('PASS_E8_FIRST_RANK_DROP_INDEPENDENT cases=255 rational_tables=2 rational_ranks=' + str(representative_rank_calls)
          + ' costs=50,57 retained_lower=44 no_new_kappa')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--certificate', type=Path, default=HERE / 'CERTIFICATE.json')
    args = parser.parse_args()
    run(json.loads(args.certificate.read_text()))


if __name__ == '__main__':
    main()
