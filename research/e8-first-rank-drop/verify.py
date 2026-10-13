#!/usr/bin/env python3
"""First E8 star-decoder rank drop; exact, offline, Python 3.10+ stdlib.

Ross Richardson with substantial OpenAI Codex assistance. Apache-2.0.
No predecessor implementation is imported. See PROOF.md for mathematical scope.
"""
import argparse
from collections import Counter, deque
from fractions import Fraction
import hashlib
from itertools import combinations, product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BASE = '47481c89fd30a43f8f882eb4b391e89c29273fd0'
SEED = 40
PRIME = 65537  # Every root minor has absolute value <= sqrt(8)^8 = 4096.
FULL = (1 << 120) - 1


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def binary_basis(words):
    pivots = {}
    for word in words:
        while word:
            pivot = word.bit_length() - 1
            if pivot in pivots:
                word ^= pivots[pivot]
            else:
                pivots[pivot] = word
                break
    return list(pivots.values())


def binary_span(words):
    result = [0]
    for word in binary_basis(words):
        result += [word ^ old for old in result]
    return sorted(result)


def root_rank(rows):
    """Rank modulo a prime larger than every possible nonzero root minor."""
    pivots = {}
    for original in rows:
        row = [x % PRIME for x in original]
        for pivot, old in pivots.items():
            factor = row[pivot]
            if factor:
                row = [(x - factor * y) % PRIME for x, y in zip(row, old)]
        pivot = next((j for j, x in enumerate(row) if x), None)
        if pivot is not None:
            inv = pow(row[pivot], -1, PRIME)
            pivots[pivot] = [x * inv % PRIME for x in row]
            if len(pivots) == 8:
                return 8
    return len(pivots)


def roots_and_simple():
    roots = []
    for a, b in combinations(range(8), 2):
        for sign in (-1, 1):
            row = [0] * 8
            row[a], row[b] = 2, 2 * sign
            roots.append(tuple(row))
    roots += [(1,) + signs for signs in product((-1, 1), repeat=7)
              if sum(x < 0 for x in signs) % 2 == 0]
    roots.sort()
    require(len(set(roots)) == 120 and all(dot(r, r) == 8 for r in roots), 'root geometry')
    simple = [(1, -1, -1, -1, -1, -1, -1, 1), (2, 2, 0, 0, 0, 0, 0, 0)]
    for j in range(6):
        row = [0] * 8
        row[j], row[j + 1] = -2, 2
        simple.append(tuple(row))
    return roots, simple


def decoder(roots):
    require(all(dot(a, b) % 4 == 0 for a in roots for b in roots), 'integral Gram')
    rows = [sum(((1 + dot(a, b) // 4) % 2) << j for j, b in enumerate(roots)) for a in roots]
    code = binary_span(rows)
    require(len(binary_basis(rows)) == 9, 'full reader dimension')
    require(Counter(w.bit_count() for w in code) == {0: 1, 56: 255, 64: 255, 120: 1}, 'code weight enumerator')
    return rows, code


def reflection_permutations(roots, simple, code):
    lookup = {r: i for i, r in enumerate(roots)}
    lookup.update({tuple(-x for x in r): i for i, r in enumerate(roots)})
    code_set = set(code)
    perms = []
    for alpha in simple:
        perm = [lookup[tuple(x - (dot(r, alpha) // 4) * a for x, a in zip(r, alpha))] for r in roots]
        require(len(set(perm)) == 120, 'reflection is a permutation')
        for w in code:
            require(permute(w, perm) in code_set, 'reflection preserves code')
        perms.append(perm)
    return perms


def permute(word, perm):
    return sum(1 << perm[j] for j in range(120) if word >> j & 1)


def puncture_orbits(punctures, perms):
    remaining = set(punctures)
    # Seed chooses which representative is visited first; every case is covered.
    ordering = sorted(punctures)
    ordering = ordering[SEED:] + ordering[:SEED]
    orbits = []
    for representative in ordering:
        if representative not in remaining:
            continue
        found = {representative}
        queue = deque([representative])
        while queue:
            word = queue.popleft()
            for perm in perms:
                image = permute(word, perm)
                require(image in punctures, 'orbit remains in minimum words')
                if image not in found:
                    found.add(image)
                    queue.append(image)
        remaining -= found
        orbits.append((representative, sorted(found)))
    require(not remaining, 'complete puncture orbit coverage')
    return orbits


def optimal_basis(code, costs):
    selected = []
    for word in sorted(code[1:], key=lambda w: (costs[w], w)):
        if len(binary_basis(selected + [word])) > len(selected):
            selected.append(word)
    dimension = len(binary_basis(code))
    require(len(selected) == dimension, 'basis spans required code')
    filtration = [len(binary_basis(w for w in code if costs[w] <= d)) for d in range(9)]
    lower = sum(d * (filtration[d] - filtration[d - 1]) for d in range(1, 9))
    require(sum(costs[w] for w in selected) == lower, 'basis matches filtration lower bound')
    return {'dimension': dimension, 'cost': lower,
            'rank_histogram': {str(k): v for k, v in sorted(Counter(costs[w] for w in code[1:]).items())},
            'filtration': filtration, 'basis': [str(w) for w in selected],
            'basis_ranks': [costs[w] for w in selected]}


def check_cover(available, required, words, costs, claimed_cost):
    require(all(w in available and w != 0 for w in words), 'admitted nonzero totals')
    require(len(binary_basis(words)) == len(words), 'independent totals')
    span = set(binary_span(words))
    require(set(required) <= span, 'live target rows not spanned')
    require(sum(costs[w] for w in words) == claimed_cost, 'incorrect complete star charge')


def analyze_puncture(deleted, roots, rows):
    require(deleted.bit_count() == 56, 'exactly 56 punctures')
    live = FULL ^ deleted
    available = binary_span(row & live for row in rows)
    required = binary_span(rows[t] & live for t in range(120) if live >> t & 1)
    require(len(available) == 256, 'available code has dimension eight')
    require(len(required) in (128, 256), 'required dimension seven or eight')
    costs = {w: root_rank([root for t, root in enumerate(roots) if w >> t & 1]) for w in available}
    ambient = optimal_basis(available, costs)
    target = optimal_basis(required, costs)
    # When the codimension is <= 1, these are ALL possible spans containing D.
    best = min(ambient['cost'], target['cost'])
    require(Fraction(best, 64) > Fraction(63, 111), 'rank-drop class improves benchmark')
    check_cover(set(available), required, [int(w) for w in ambient['basis']], costs, ambient['cost'])
    check_cover(set(available), required, [int(w) for w in target['basis']], costs, target['cost'])
    case = {'deleted': str(deleted), 'available': ambient, 'required': target,
            'optimal_star_cost': best, 'ratio': str(Fraction(best, 64)),
            'rank_table_sha256': digest([[str(w), costs[w]] for w in available])}
    return case, available, required, costs


def flat_capacities(roots, simple):
    aug = [[Fraction(x) for x in row] + [Fraction(i == j) for j in range(8)] for i, row in enumerate(simple)]
    for col in range(8):
        row = next(i for i in range(col, 8) if aug[i][col])
        aug[col], aug[row] = aug[row], aug[col]
        scale = aug[col][col]
        aug[col] = [x / scale for x in aug[col]]
        for i in range(8):
            if i != col:
                scale = aug[i][col]
                aug[i] = [x - scale * y for x, y in zip(aug[i], aug[col])]
    inv = [row[8:] for row in aug]
    supports = []
    for root in roots:
        coords = [sum(root[i] * inv[i][j] for i in range(8)) for j in range(8)]
        require(all(x.denominator == 1 for x in coords), 'integer simple coordinates')
        require(all(x >= 0 for x in coords) or all(x <= 0 for x in coords), 'positive root system')
        supports.append(sum(1 << j for j, x in enumerate(coords) if x))
    capacity = [0] * 9
    for subset in range(256):
        flat = [r for r, s in zip(roots, supports) if not s & ~subset]
        dimension = subset.bit_count()
        require(root_rank(flat) == dimension, 'standard flat dimension')
        capacity[dimension] = max(capacity[dimension], len(flat))
    require(capacity == [0, 1, 3, 6, 12, 20, 36, 63, 120], 'root capacity table')
    return capacity


def pins():
    source = json.loads((HERE / 'SOURCES.json').read_text())
    require(source['base_commit'] == BASE, 'source base')
    hashes = {}
    for entry in source['retained_sources']:
        data = (HERE / entry['local_path']).read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry['sha256'], 'source SHA256 mismatch')
        require(hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest() == entry['git_blob'], 'source Git blob mismatch')
        hashes[entry['local_path']] = entry['sha256']
    return hashes


def controls(roots, rows, cases):
    names = []
    def reject(name, fn, expected):
        try:
            fn()
        except ValueError as exc:
            require(expected in str(exc), 'wrong rejection: ' + name)
            names.append(name)
        else:
            raise ValueError('control accepted: ' + name)
    for dimension in (7, 8):
        case = next(c for c in cases if c['required']['dimension'] == dimension)
        _, available, required, costs = analyze_puncture(int(case['deleted']), roots, rows)
        witness = [int(w) for w in case['required']['basis']]
        reject('omitted target total at dimension ' + str(dimension),
               lambda: check_cover(set(available), required, witness[:-1], costs, sum(costs[w] for w in witness[:-1])), 'not spanned')
        reject('underpriced total at dimension ' + str(dimension),
               lambda: check_cover(set(available), required, witness, costs, case['required']['cost'] - 1), 'charge')
        cheap = [w for w in available if costs[w] < 8]
        reject('all cheap totals fail target coverage at dimension ' + str(dimension),
               lambda: check_cover(set(available), required, binary_basis(cheap), costs, sum(costs[w] for w in binary_basis(cheap))), 'not spanned')
    reject('wrong puncture cardinality', lambda: analyze_puncture(0, roots, rows), '56 punctures')
    # Positive control: outside-target totals are allowed, and can be optimal.
    case = next(c for c in cases if c['required']['dimension'] == 7)
    _, available, required, costs = analyze_puncture(int(case['deleted']), roots, rows)
    ambient = [int(w) for w in case['available']['basis']]
    require(any(w not in required for w in ambient), 'outside-target positive control')
    check_cover(set(available), required, ambient, costs, 50)
    return names


def build():
    source_hashes = pins()
    roots, simple = roots_and_simple()
    rows, code = decoder(roots)
    union_histogram = Counter((a | b).bit_count() for a, b in combinations(code[1:], 2))
    require(min(union_histogram) == 84, 'two-reader support union')
    punctures = [w for w in code if w.bit_count() == 56]
    perms = reflection_permutations(roots, simple, code)
    orbits = puncture_orbits(set(punctures), perms)
    cases = [analyze_puncture(p, roots, rows)[0] for p in punctures]
    lookup = {int(c['deleted']): c for c in cases}
    summary = []
    for representative, members in orbits:
        first = lookup[representative]
        signature = lambda c: {k: {f: c[k][f] for f in ('dimension', 'cost', 'rank_histogram', 'filtration', 'basis_ranks')}
                               for k in ('available', 'required')}
        require(all(signature(lookup[m]) == signature(first) for m in members), 'orbit invoice invariance')
        summary.append({'representative': str(representative), 'size': len(members), 'members_sha256': digest([str(m) for m in members]),
                        **signature(first), 'optimal_star_cost': first['optimal_star_cost'], 'ratio': first['ratio']})
    require(sorted((s['size'], s['required']['dimension'], s['optimal_star_cost']) for s in summary) == [(120, 7, 50), (135, 8, 57)], 'two orbit classes')
    capacities = flat_capacities(roots, simple)
    retained_cost, a, b = min((a + 8 * b, a, b) for a in range(1, 9) for b in range(a, 9)
                            if capacities[a] + capacities[b] >= 84 - 56)
    require(retained_cost == 44 and 111 * retained_cost > 63 * 64, 'rank-retained ratio bound')
    return {'schema': 1, 'base_commit': BASE, 'assignment_seed': SEED,
            'scope': '56-puncture real E8 fixed star decoder; no new kappa',
            'source_sha256': source_hashes, 'root_order': [list(r) for r in roots],
            'reader_weight_histogram': {str(k): v for k, v in sorted(Counter(w.bit_count() for w in code).items())},
            'pair_union_histogram': {str(k): v for k, v in sorted(union_histogram.items())},
            'standard_flat_capacities': capacities, 'rank_retained_lower_bound': retained_cost,
            'rank_retained_relaxed_pair': [a, b], 'orbit_classes': summary, 'cases': cases,
            'negative_controls': controls(roots, rows, cases),
            'positive_control': 'An eight-total ambient basis with outside-target totals attains cost 50.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', type=Path, help='write reconstructed certificate to a NEW path')
    args = parser.parse_args()
    if args.write:
        require(not args.write.exists(), 'output path already exists')
    report = build()
    if args.write:
        with args.write.open('x') as stream:
            stream.write(json.dumps(report, indent=2, sort_keys=True) + '\n')
    else:
        require(report == json.loads((HERE / 'CERTIFICATE.json').read_text()), 'certificate mismatch')
    print('PASS_E8_FIRST_RANK_DROP cases=255 orbits=120+135 target_dimensions=7,8 costs=50,57 retained_lower=44 controls=7 no_new_kappa')


if __name__ == '__main__':
    main()
