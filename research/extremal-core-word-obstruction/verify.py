"""Exact scalar-word checks for all extremal irreducible binary cores.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The Laurent matrix recurrence is adapted from CubeJerry's PR6782
independent_five_word.py. This adaptation is not an independent review.
See CREDITS.md for the exact source and proof dependencies.
"""

from collections import Counter
from fractions import Fraction
import itertools
import json
from pathlib import Path


def require(ok, message):
    if not ok:
        raise ValueError(message)


def basis(values):
    pivots = {}
    for value in values:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return tuple(pivots[i] for i in sorted(pivots, reverse=True))


def reduce_vector(value, pivots):
    for row in pivots:
        value = min(value, value ^ row)
    return value


def outer(x, y, width):
    return sum(y << (i * width) for i in range(width) if x >> i & 1)


def identity(width):
    return sum(1 << (i * width + i) for i in range(width))


def left_project(pair, matrix, width):
    x, y = pair
    row, mask = 0, (1 << width) - 1
    while y:
        bit = y & -y
        row ^= (matrix >> ((bit.bit_length() - 1) * width)) & mask
        y ^= bit
    return outer(x, row, width)


def model(t):
    n = 2 * t + 1
    ones = (1 << n) - 1
    pairs = [(1 << i, 1 << i) for i in range(2 * t)] + [(ones, ones)]
    edge_bits = [1 << ((2 * i) * n + 2 * i + 1) for i in range(t)]
    diagonal = identity(n)
    quotient = basis([outer(ones, ones, n) & ~diagonal] + edge_bits)
    products = {}
    for i, p in enumerate(pairs):
        for j, q in enumerate(pairs):
            product = left_project(p, outer(*q, n), n) & ~diagonal
            products[i, j] = reduce_vector(product, quotient)
    return n, pairs, quotient, products, diagonal | sum(edge_bits)


def orders(t, h):
    size = 2 * t + h
    for bridge_positions in itertools.combinations(range(size), h):
        positions = set(bridge_positions)
        for old in itertools.permutations(range(2 * t)):
            it = iter(old)
            yield tuple(2 * t if i in positions else next(it) for i in range(size))


def exponents(order, t, h):
    r, bridge = t + h - 1, 0
    result = []
    for kind in order:
        vector = [0] * r
        if kind < 2 * t:
            vector[kind // 2] = 1
        else:
            if bridge < h - 1:
                vector[t + bridge] = 1
            else:
                vector[t:] = [-1] * (h - 1)
            bridge += 1
        result.append(tuple(vector))
    require(bridge == h, 'bridge count')
    return result


def rational_rank(rows):
    pivots = {}
    for original in rows:
        row = [Fraction(x) for x in original]
        for col in sorted(pivots):
            coefficient = row[col]
            if coefficient:
                row = [x - coefficient * y for x, y in zip(row, pivots[col])]
        nonzero = next((i for i, x in enumerate(row) if x), None)
        if nonzero is not None:
            lead = row[nonzero]
            pivots[nonzero] = [x / lead for x in row]
    return len(pivots)


def consecutive(order, bridge):
    positions = [i for i, kind in enumerate(order) if kind == bridge]
    return bool(positions) and positions == list(range(positions[0], positions[-1] + 1))


def quadratic(order, exps, products):
    coefficients = {}
    supports = [[i for i, x in enumerate(row) if x % 2] for row in exps]
    for j in range(len(order)):
        for i in range(j):
            matrix = products[order[j], order[i]]
            if matrix:
                for a in supports[i]:
                    for b in supports[j]:
                        monomial = (min(a, b), max(a, b))
                        coefficients[monomial] = coefficients.get(monomial, 0) ^ matrix
    return {key: value for key, value in coefficients.items() if value}


def laurent(order, exps, pairs, width):
    """Multiply the full matrices with exact integer exponent tuples."""
    zero = (0,) * len(exps[0])
    out = {zero: identity(width)}
    for kind, exponent in zip(order, exps):
        new = {}
        for key, matrix in out.items():
            projected = left_project(pairs[kind], matrix, width)
            new[key] = new.get(key, 0) ^ matrix ^ projected
            shifted = tuple(x + y for x, y in zip(key, exponent))
            new[shifted] = new.get(shifted, 0) ^ projected
        out = {key: value for key, value in new.items() if value}
    return out


def expected_endpoint(t, r, width):
    result = {(0,) * r: sum(1 << (i * width + i) for i in range(2 * t, width))}
    for i in range(t):
        key = tuple(int(j == i) for j in range(r))
        result[key] = (1 << ((2 * i) * width + 2 * i)) | (1 << ((2 * i + 1) * width + 2 * i + 1))
    return result


def star_checks():
    result = []
    for t in range(1, 21):
        n, pairs, quotient, _, _ = model(t)
        diagonal = identity(n)
        bridge = outer(*pairs[-1], n)
        stars = [(left_project(pairs[i], bridge, n) ^ left_project(pairs[-1], outer(*pairs[i], n), n)) & ~diagonal
                 for i in range(2 * t)]
        require(len(basis((*quotient, *stars))) == t + 1 + 2 * t, 'independent old stars modulo quotient')
        fresh = (1 << (2 * t), 1 << (2 * t))
        fresh_star = (left_project(fresh, bridge, n) ^ left_project(pairs[-1], outer(*fresh, n), n)) & ~diagonal
        require(len(basis((*quotient, *stars, fresh_star))) == t + 1 + 2 * t,
                'the fresh star is dependent, not an extra independent constraint')
        result.append({'edge_pairs': t, 'width': n, 'quotient_rank': len(quotient), 'old_star_rank_mod_quotient': 2 * t})
    return result


def degree_two_census(t, h):
    _, _, _, products, _ = model(t)
    counts = Counter()
    for order in orders(t, h):
        exps = exponents(order, t, h)
        allowed = not quadratic(order, exps, products)
        block = consecutive(order, 2 * t)
        require(allowed == block, 'exact quadratic chronology criterion')
        counts['orders'] += 1
        counts['passing'] += allowed
    sample = next(orders(t, h))
    exps = exponents(sample, t, h)
    rank = rational_rank(exps)
    require(rank == t + h - 1 and len(exps) - rank == t + 1, 'saturated model relation rank')
    units = {tuple(int(i == j) for j in range(rank)) for i in range(rank)}
    require(units <= set(exps), 'the listed exponents generate the whole stated free group')
    return {'edge_pairs': t, 'bridges': h, 'relation_rank': t + 1, 'counts': dict(counts)}


def full_word_census(t):
    n, pairs, _, _, allowed_entries = model(t)
    counts = Counter()
    expected = expected_endpoint(t, t + 1, n)
    for order in orders(t, 2):
        actual = laurent(order, exponents(order, t, 2), pairs, n)
        block = consecutive(order, 2 * t)
        require((actual == expected) == block, 'full Laurent chronology agrees with the exact endpoint')
        if not block:
            require(any(matrix & ~allowed_entries for matrix in actual.values()), 'forbidden endpoint entry')
        counts['orders'] += 1
        counts['diagonal_endpoints'] += block
    return {'edge_pairs': t, 'width': n, 'counts': dict(counts)}


def ambient_checks():
    rows = []
    for t in (1, 2, 3, 4, 6):
        for h in (2, 3):
            width = 2 * t + 5
            old = [(x, y) for i in range(t) for x, y in
                   [(1 << (2 * i), 3 << (2 * i)), (3 << (2 * i), 1 << (2 * i + 1))]]
            hx = sum(1 << (2 * i + 1) for i in range(t))
            hy = sum(1 << (2 * i) for i in range(t))
            link = (hx | (3 << (2 * t)), hy | (5 << (2 * t)))
            pairs = old + [link]
            order = tuple(range(t)) + (2 * t,) * h + tuple(range(t, 2 * t))
            exps = exponents(order, t, h)
            actual = laurent(order, exps, pairs, width)
            kept = [(kind, exponent) for kind, exponent in zip(order, exps) if kind != 2 * t]
            deleted = laurent([p[0] for p in kept], [p[1] for p in kept], pairs, width)
            require(actual == deleted == expected_endpoint(t, t + h - 1, width), 'full ambient deletion, including spectator columns')
            omit = order.index(2 * t)
            wrong = laurent(order[:omit] + order[omit + 1:], exps[:omit] + exps[omit + 1:], pairs, width)
            dirty_column = 2 * t + 2
            changed = {key: wrong.get(key, 0) ^ actual.get(key, 0) for key in wrong.keys() | actual.keys()}
            require(any(any(matrix >> (i * width + dirty_column) & 1 for i in range(width))
                        for matrix in changed.values()), 'omitted bridge changes a dirty spectator column')
            rows.append({'edge_pairs': t, 'width': width, 'bridges': h,
                         'fresh_image': 3, 'fresh_covector': 5, 'dirty_column_checked': dirty_column,
                         'endpoint_terms': len(actual), 'omitted_bridge_error_terms': sum(bool(v) for v in changed.values())})
    return rows


def controls():
    t = 3
    n, pairs, _, products, allowed = model(t)
    order = (6, 6, 0, 1, 2, 3, 4, 5)
    good = exponents(order, t, 2)
    wrong = list(good)
    wrong[1] = wrong[0]
    require(not quadratic(order, wrong, products), 'wrong bridge sign has the same degree-two quotient')
    endpoint = laurent(order, wrong, pairs, n)
    require(any(matrix & ~allowed for matrix in endpoint.values()), 'full endpoint rejects a noncancelling bridge')
    require(rational_rank(wrong) == 4 and len(wrong) - rational_rank(wrong) == 4, 'wrong-sign relation rank is still k')
    # One extra relation permits a cancelling coordinate excursion inside the bridge calls.
    order = (6, 0, 0, 6, 0, 1, 2, 3, 4, 5)
    unit = lambda i: tuple(int(j == i) for j in range(5))
    neg = lambda row: tuple(-x for x in row)
    exps = [unit(3), unit(4), neg(unit(4)), neg(unit(3))] + [unit(i // 2) for i in range(6)]
    require(laurent(order, exps, pairs, n) == expected_endpoint(3, 5, n), 'extra-relation word is exactly diagonal')
    require(not consecutive(order, 6) and len(exps) - rational_rank(exps) == 5, 'one extra relation defeats literal chronology')
    # An ambient exponent basis can give a false parity kernel.
    paid_coordinates = [(1, 0), (0, 1)]
    ambient_coordinates = [(2, 0), (0, 2)]
    parity_rank = lambda rows: len(basis(sum((v % 2) << i for i, v in enumerate(row)) for row in rows))
    require(rational_rank(paid_coordinates) == rational_rank(ambient_coordinates) == 2,
            'the exponent groups have the same rational rank')
    require(parity_rank(paid_coordinates) == 2 and parity_rank(ambient_coordinates) == 0,
            'the associated-graded kernel must use the paid-generated group')
    return {'wrong_sign_same_linear_kernel': {'k': 4, 'relation_rank': 4, 'full_endpoint_rejected': True},
            'extra_relation_chronology_counterexample': {'order': order, 'exponents': exps, 'k': 4, 'relation_rank': 5},
            'paid_generated_parity_control': {'rational_rank': 2, 'paid_parity_rank': 2, 'ambient_parity_rank': 0}}


def compute():
    return {'status': 'PASS_EXTREMAL_CORE_WORD_OBSTRUCTION',
            'scope': 'Noncoordinate binary scalar words with irreducible image 2k-1, pattern dimension k>=2, at most k saturated exponent relations and a full diagonal monomial endpoint.',
            'star_quotient_checks': star_checks(),
            'degree_two_censuses': [degree_two_census(t, h) for t, hs in ((1, range(1, 5)), (2, range(1, 5)), (3, range(1, 4))) for h in hs],
            'full_laurent_censuses': [full_word_census(t) for t in (1, 2, 3)],
            'ambient_deletion_checks': ambient_checks(), 'boundary_controls': controls(),
            'limitations': ['Uses the pinned all-width extremal classification and the stated associated-graded argument.',
                            'Coordinate calls, reducible/subextremal images and larger relation budgets are outside the theorem.',
                            'No native supplier, complete multiplier invoice or new kappa.']}


if __name__ == '__main__':
    actual = json.loads(json.dumps(compute()))
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(actual == expected, 'committed exact receipt')
    print(actual['status'])
    print(json.dumps({'quadratic_orders': sum(r['counts']['orders'] for r in actual['degree_two_censuses']),
                      'full_laurent_orders': sum(r['counts']['orders'] for r in actual['full_laurent_censuses']),
                      'ambient_deletions': len(actual['ambient_deletion_checks'])}, sort_keys=True))
