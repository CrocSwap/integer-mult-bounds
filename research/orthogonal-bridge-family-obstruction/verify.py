"""Exact checks for the prescribed orthogonal fresh-bridge family.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Binary, rank, quadratic and Laurent routines adapt PR7695 and its
credited CubeJerry PR6782 and Ali Romman PR7694 sources. The proof
and checker are author-checked, not an independent source review.
"""
from collections import Counter
from fractions import Fraction
from math import factorial
from pathlib import Path
import hashlib
import itertools
import json


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


def dual(xs):
    n = len(xs)
    require(len(basis(xs)) == n, 'invertible old image basis')
    return tuple(next(y for y in range(1, 1 << n)
                      if [(y & x).bit_count() % 2 for x in xs] == [int(i == j) for j in range(n)])
                 for i in range(n))


def frame(xs, b, with_products=False):
    N, ys = len(xs), dual(xs)
    require(N >= 1 and b >= 1, 'positive old and fresh dimensions')
    width, diagonal = N + b, identity(N + b)
    old = [outer(x, y, width) for x, y in zip(xs, ys)]
    kernel, diagonal_sums = [], {}
    for mask in range(1 << N):
        matrix = 0
        for i, value in enumerate(old):
            if mask >> i & 1:
                matrix ^= value
        if not matrix & ~diagonal:
            kernel.append(mask)
            diagonal_sums[mask] = matrix
    signatures = {}
    for i in range(N):
        signatures.setdefault(tuple(mask >> i & 1 for mask in kernel), []).append(i)
    groups = list(signatures.values())
    indicators = [sum(1 << i for i in group) for group in groups]
    require(len(kernel) == 1 << len(groups) and all(mask in kernel for mask in indicators),
            'Boolean partition is complete')
    active = [sum((diagonal_sums[mask] >> (j * width + j) & 1) << j for j in range(N))
              for mask in indicators]
    require(all(mask.bit_count() == len(group) for mask, group in zip(active, groups)),
            'physical target multiplicity')
    require(sum(active) == (1 << N) - 1
            and all(not a & b for a, b in itertools.combinations(active, 2)),
            'physical supports partition the old coordinates')
    hx = hy = 0
    for x, y in zip(xs, ys):
        hx ^= x
        hy ^= y
    z = tuple((1 << p) ^ ((1 << b) - 1 if N % 2 else 0) for p in range(b))
    require(len(basis(z)) == b, 'independent fresh covectors')
    pairs = list(zip(xs, ys)) + [(hx | (1 << (N + p)), hy | (z[p] << N)) for p in range(b)]
    require(all((x & y).bit_count() % 2 for x, y in pairs), 'all types idempotent')
    require(all((pairs[N + p][1] & pairs[N + q][0]).bit_count() % 2 == int(p == q)
                for p in range(b) for q in range(b)),
            'the bridges are mutually orthogonal')
    k = N - len(groups) + b
    require(len(basis(outer(x, y, width) & ~diagonal for x, y in pairs)) == k,
            'actual ambient pattern dimension')
    allowed = [outer(sum(((ys[i] >> j) & 1) << i for i in range(N)),
                     sum(((xs[i] >> j) & 1) << i for i in range(N)), width) & ~diagonal
               for j in range(N)]
    ones = (1 << N) - 1
    normalized = [(1 << i, 1 << i) for i in range(N)] + [
        (ones | (1 << (N + p)), ones | (z[p] << N)) for p in range(b)]
    bridges = [outer(*pair, width) for pair in normalized[N:]]
    Q = basis([matrix & ~diagonal for matrix in bridges] + allowed)
    require(len(Q) == k, 'endpoint quotient dimension')
    stars = [reduce_vector((left_project(normalized[i], bridges[p], width)
                           ^ left_project(normalized[N + p], outer(*normalized[i], width), width))
                          & ~diagonal, Q) for p in range(b) for i in range(N)]
    star_rank = len(basis(stars))
    require(star_rank == N * b - (b - 1 if N % 2 == 0 else 0), 'parity-dependent star rank')
    if N % 2 == 0:
        for p in range(1, b):
            total = 0
            for i in range(N):
                total ^= stars[i] ^ stars[p * N + i]
            require(total == 0, 'even bridge-pair star dependence')
    products = {(i, j): reduce_vector(left_project(a, outer(*b, width), width) & ~diagonal, Q)
                for i, a in enumerate(normalized) for j, b in enumerate(normalized)} if with_products else {}
    return {'N': N, 'b': b, 'xs': tuple(xs), 'ys': ys, 'groups': groups, 'active': active,
            'k': k, 'star_rank': star_rank, 'pairs': pairs, 'products': products,
            'coordinate_old_types': sum(not matrix & ~diagonal for matrix in old)}


def census(N):
    counts = Counter()
    digest = hashlib.sha256()
    bridge_counts = [b for b in range(1, 5) if N * b % 2 == 0]
    distinct = 0
    for xs in itertools.permutations(range(1, 1 << N), N):
        if len(basis(xs)) != N:
            continue
        distinct += 1
        for b in bridge_counts:
            row = frame(xs, b)
            counts[str((b, tuple(sorted(map(len, row['groups'])))))] += 1
            record = {name: row[name] for name in ['b', 'xs', 'ys', 'groups', 'active', 'k', 'star_rank']}
            digest.update((json.dumps(record, sort_keys=True) + '\n').encode())
    require(distinct == {1: 1, 2: 6, 3: 168, 4: 20160}[N], 'complete basis census')
    require(sum(counts.values()) == distinct * len(bridge_counts), 'all valid fresh dimensions')
    return {'N': N, 'bases': distinct, 'basis_bridge_checks': sum(counts.values()),
            'bridge_counts': bridge_counts, 'partitions': dict(sorted(counts.items())),
            'certificate_sha256': digest.hexdigest()}


def type_orders(N, hs):
    counts = [1] * N + list(hs)
    size = sum(counts)
    def walk(prefix):
        if len(prefix) == size:
            yield tuple(prefix)
            return
        for kind, count in enumerate(counts):
            if count:
                counts[kind] -= 1
                prefix.append(kind)
                yield from walk(prefix)
                prefix.pop()
                counts[kind] += 1
    yield from walk([])


def gap_count(N, hs):
    total = 0
    for assignment in itertools.product(range(N + 1), repeat=len(hs)):
        ways = 1
        for gap in range(N + 1):
            multiplicities = [h for h, chosen in zip(hs, assignment) if chosen == gap]
            interleavings = factorial(sum(multiplicities))
            for h in multiplicities:
                interleavings //= factorial(h)
            ways *= interleavings
        total += ways
    return factorial(N) * total


def allocate(order, groups, b):
    N = sum(map(len, groups))
    positions = {kind: [i for i, value in enumerate(order) if value == kind] for kind in range(N + b)}
    require(all(positions.values()), 'every type occurs')
    dependent = {positions[kind][-1] for kind in range(N, N + b)}
    for group in groups:
        dependent.update(positions[kind][-1] for kind in group[1:])
    free = [i for i in range(len(order)) if i not in dependent]
    r = len(free)
    exps = [[0] * r for _ in order]
    for j, pos in enumerate(free):
        exps[pos][j] = 1
    for group in groups:
        total = [sum(exps[pos][j] for pos in positions[group[0]]) for j in range(r)]
        for kind in group[1:]:
            pos = positions[kind][-1]
            exps[pos] = [total[j] - sum(exps[other][j] for other in positions[kind] if other != pos)
                         for j in range(r)]
    for kind in range(N, N + b):
        pos = positions[kind][-1]
        exps[pos] = [-sum(exps[other][j] for other in positions[kind][:-1]) for j in range(r)]
    require(len(dependent) == N - len(groups) + b, 'exact relation count')
    require(all(tuple(int(i == j) for i in range(r)) in map(tuple, exps) for j in range(r)),
            'paid exponents generate the full free group')
    return [tuple(row) for row in exps]


def chronology(order, N, b):
    for kind in range(N, N + b):
        positions = [i for i, value in enumerate(order) if value == kind]
        if any(value < N for value in order[positions[0]:positions[-1] + 1]):
            return False
    return True


def endpoint(row, order, exps, width):
    N, r = row['N'], len(exps[0])
    totals = [tuple(sum(value[j] for kind, value in zip(order, exps) if kind == i)
                    for j in range(r)) for i in range(N)]
    expected = {(0,) * r: sum(1 << (i * width + i) for i in range(N, width))}
    for group, active in zip(row['groups'], row['active']):
        require(all(totals[i] == totals[group[0]] for i in group), 'equal block totals')
        mask = sum(1 << (i * width + i) for i in range(N) if active >> i & 1)
        label = totals[group[0]]
        expected[label] = expected.get(label, 0) ^ mask
    return {key: value for key, value in expected.items() if value}


def domain(name, xs, hs):
    b = len(hs)
    row = frame(xs, b, True)
    N, width = row['N'], row['N'] + b
    counts = Counter()
    for order in type_orders(N, hs):
        exps = allocate(order, row['groups'], b)
        legal = chronology(order, N, b)
        require((not quadratic(order, exps, row['products'])) == legal, 'quadratic chronology')
        actual = laurent(order, exps, row['pairs'], width)
        expected = endpoint(row, order, exps, width)
        require((actual == expected) == legal, 'full ambient endpoint')
        if not legal:
            require(any(value & ~identity(width) for value in actual.values()),
                    'failed chronology gives a nondiagonal word')
        counts['orders'] += 1
        counts['passing'] += legal
    expected_count = factorial(N + sum(hs))
    for h in hs:
        expected_count //= factorial(h)
    require(counts['orders'] == expected_count, 'all multiset orders')
    require(counts['passing'] == gap_count(N, hs), 'independent gap count')
    order = next(type_orders(N, hs))
    exps = allocate(order, row['groups'], b)
    require(len(exps) - rational_rank(exps) == row['k'], 'actual saturated relation rank')
    return {'name': name, 'N': N, 'b': b, 'k': row['k'], 'groups': row['groups'], 'bridge_calls': hs,
            'full_laurent': True, 'counts': dict(counts)}


def larger_checks():
    fixtures = [('coordinate1', (1,)), ('edge2', (1, 3)), ('normal3', (6, 5, 7)),
                ('quad4', (14, 13, 11, 7)), ('edge_triple5', (1, 3, 24, 20, 28)),
                ('two_triples6', (6, 5, 7, 48, 40, 56)),
                ('coordinate7', tuple(1 << i for i in range(7))),
                ('orthogonal8', tuple(255 ^ (1 << i) for i in range(8))),
                ('coordinate9', tuple(1 << i for i in range(9))),
                ('orthogonal10', tuple(1023 ^ (1 << i) for i in range(10)))]
    results = []
    fixtures = [(name, xs, 2) for name, xs in fixtures] + [
        ('edge2_three_bridges', (1, 3), 3), ('quad4_one_bridge', (14, 13, 11, 7), 1),
        ('coordinate1_four_bridges', (1,), 4), ('normal3_four_bridges', (6, 5, 7), 4),
        ('edge2_six_bridges', (1, 3), 6)]
    for name, xs, b in fixtures:
        row = frame(xs, b, True)
        N, width = row['N'], row['N'] + b + 2
        old = (0, 0) + tuple(range(1, N))
        middle = tuple(range(N, N + b)) * 2 + (N,)
        order = old[:len(old)//2] + middle + old[len(old)//2:]
        exps = allocate(order, row['groups'], b)
        require(len(exps) - rational_rank(exps) == row['k'], 'repeated calls retain exact relation rank')
        require(chronology(order, N, b), 'interleaving contains no old call')
        require(not quadratic(order, exps, row['products']), 'interleaving quadratic endpoint')
        actual = laurent(order, exps, row['pairs'], width)
        kept = [(kind, exponent) for kind, exponent in zip(order, exps) if kind < N]
        deleted = laurent([kind for kind, _ in kept], [exponent for _, exponent in kept], row['pairs'], width)
        require(actual == deleted == endpoint(row, order, exps, width),
                'full ambient deletion and target multiplicities')
        omitted = order.index(N)
        wrong = laurent(order[:omitted] + order[omitted + 1:], exps[:omitted] + exps[omitted + 1:], row['pairs'], width)
        delta = [wrong.get(key, 0) ^ actual.get(key, 0) for key in wrong.keys() | actual.keys()]
        changed = [j for j in range(N, N + b) if any(any(value >> (i * width + j) & 1 for i in range(width)) for value in delta)]
        require(changed, 'an omitted bridge changes an arbitrary fresh input')
        require(any(value < N for value in order) and (b == 1 or middle != tuple(sorted(middle))), 'literal bridge interleaving')
        results.append({'name': name, 'N': N, 'b': b, 'width': width, 'k': row['k'],
                        'old_calls': len(old), 'bridge_calls': [3] + [2] * (b - 1),
                        'coordinate_old_types': row['coordinate_old_types'],
                        'target_blocks': row['active'], 'omitted_bridge_changes_columns': changed})
    return results


def controls():
    row = frame((1, 3), 2, True)
    order = (2, 3, 0, 1, 2, 3)
    exps = allocate(order, row['groups'], 2)
    require(quadratic(order, exps, row['products']), 'independent bridge variables reject an old interposition')
    merged = [tuple([x[0] + x[1]] + list(x[2:])) for x in exps]
    require(len(exps) - rational_rank(exps) == row['k'], 'valid relation budget')
    require(len(merged) - rational_rank(merged) == row['k'] + 1, 'merged variables add a relation')
    require(not quadratic(order, merged, row['products']), 'merged variables hide the quadratic rejection')
    wrong = laurent(order, merged, row['pairs'], 4)
    require(any(value & ~identity(4) for value in wrong.values()), 'the false positive fails the full endpoint')
    doubled = [tuple(2 * value for value in exponent) for exponent in exps]
    require(not quadratic(order, doubled, row['products']), 'a larger ambient exponent group hides degree two')
    require(any(value & ~identity(4) for value in laurent(order, doubled, row['pairs'], 4).values()),
            'doubling exponents does not repair the full endpoint')
    collected = (0, 1, 2, 2, 3, 3)
    warped = allocate(collected, row['groups'], 2)
    warped[3] = warped[2]
    require(len(warped) - rational_rank(warped) == row['k'], 'parity-preserving warp retains relation rank')
    require(not quadratic(collected, warped, row['products']), 'a nonzero even bridge total passes degree two')
    require(any(value & ~identity(4) for value in laurent(collected, warped, row['pairs'], 4).values()),
            'the full endpoint rejects a nonzero even bridge total')
    normal = frame((6, 5, 7), 2)
    extra = (28, 28)
    require(extra not in normal['pairs'] and (extra[0] & extra[1]).bit_count() % 2,
            'the sixth projector is an additional idempotent')
    pattern = outer(*extra, 5) & ~identity(5)
    bridge_sum = outer(*normal['pairs'][3], 5) ^ outer(*normal['pairs'][4], 5)
    require(pattern == bridge_sum & ~identity(5), 'the sixth pattern couples the two bridge totals')
    require(all((extra[0] & y).bit_count() % 2 == 0 and (extra[1] & x).bit_count() % 2 == 0
                for x, y in normal['pairs'][3:]), 'the sixth projector is orthogonal to both bridges')
    wrong_parity = 0
    for N in range(1, 11):
        z = (1, 2) if N % 2 else (2, 1)
        ones = (1 << N) - 1
        for p in range(2):
            x, y = ones | (1 << (N + p)), ones | (z[p] << N)
            require((x & y).bit_count() % 2 == 0, 'wrong fresh pairing must fail idempotence')
            wrong_parity += 1
    singular = []
    for N in (1, 3, 5, 7):
        for b in (1, 3, 5):
            z = tuple(((1 << b) - 1) ^ (1 << p) for p in range(b))
            require(len(basis(z)) == b - 1, 'odd/odd fresh rank defect')
            kernel = ((1 << b) - 1) << N
            ones = (1 << N) - 1
            pairs = [(1 << i, 1 << i) for i in range(N)] + [
                (ones | (1 << (N + p)), ones | (z[p] << N)) for p in range(b)]
            require(all((y & kernel).bit_count() % 2 == 0 for _, y in pairs), 'actual common-kernel vector')
            rejected = False
            try:
                frame(tuple(1 << i for i in range(N)), b)
            except ValueError as error:
                rejected = str(error) == 'independent fresh covectors'
            require(rejected, 'singular pairing is outside the theorem')
            singular.append({'N': N, 'b': b, 'common_kernel_vector': kernel})
    return {'merged_bridge_variable_false_positive': {'order': order, 'valid_relation_rank': row['k'],
             'mutant_relation_rank': row['k'] + 1, 'mutant_full_endpoint_rejected': True},
             'extra_sixth_projector': {'pair': extra, 'off_pattern': 'off(B1)+off(B2)',
                                      'outside_named_alphabet': True},
             'larger_ambient_group_false_positive': {'all_exponents_doubled': True, 'full_endpoint_rejected': True},
             'even_nonzero_bridge_total_control': {'order': collected, 'relation_rank': row['k'],
                                                   'full_endpoint_rejected': True},
             'singular_fresh_pairing_controls': singular,
             'wrong_parity_links_rejected': wrong_parity}


def compute():
    bases = [census(N) for N in range(1, 5)]
    fixtures = [('coordinate1', (1,)), ('edge2', (1, 3)), ('normal3', (6, 5, 7)),
                ('coordinate3', (1, 2, 4)), ('quad4', (14, 13, 11, 7)),
                ('two_edges', (1, 3, 4, 12))]
    domains = []
    for name, xs in fixtures:
        result = domain(name, xs, (2, 2))
        domains.append(result)
    for name, xs in [('edge2_three_calls', (1, 3)), ('normal3_three_calls', (6, 5, 7))]:
        result = domain(name, xs, (3, 2))
        domains.append(result)
    for name, xs, hs in [('edge2_one_bridge', (1, 3), (3,)),
                         ('quad4_one_bridge', (14, 13, 11, 7), (3,)),
                         ('edge2_three_bridges', (1, 3), (2, 2, 2)),
                         ('coordinate1_four_bridges', (1,), (2, 2, 2, 2))]:
        result = domain(name, xs, hs)
        domains.append(result)
    return {'status': 'PASS_ORTHOGONAL_BRIDGE_FAMILY_OBSTRUCTION', 'bases': bases, 'domains': domains, 'larger_checks': larger_checks(), 'controls': controls()}

if __name__ == '__main__':
    actual = json.loads(json.dumps(compute()))
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(actual == expected, 'committed exact receipt')
    print(actual['status'])
    print('20335 bases; 81002 basis/bridge checks; 55250 full Laurent words; 10148 passing orders')
    print('15 larger fixtures; all bridge totals vanish in the stated class.')
