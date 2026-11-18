"""Exact checks for an arbitrary orthogonal binary basis and one bridge.

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
Matrix and Laurent routines are adapted from PR7694 and its credited
CubeJerry PR6782 source. This is not an independent review.
"""

from collections import Counter
from fractions import Fraction
import hashlib
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


def orders(t, h):
    size = 2 * t + h
    for bridge_positions in itertools.combinations(range(size), h):
        positions = set(bridge_positions)
        for old in itertools.permutations(range(2 * t)):
            it = iter(old)
            yield tuple(2 * t if i in positions else next(it) for i in range(size))


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
def dual(xs):
    n = len(xs)
    require(len(basis(xs)) == n, 'invertible old image basis')
    return tuple(next(y for y in range(1, 1 << n)
                      if [(y & x).bit_count() % 2 for x in xs] == [int(i == j) for j in range(n)])
                 for i in range(n))


def inspect_basis(xs):
    N, ys = len(xs), dual(xs)
    require(N >= 2 and N % 2 == 0, 'positive even old dimension')
    n, diagonal = N + 1, identity(N + 1)
    old_matrices = [outer(x, y, n) for x, y in zip(xs, ys)]
    kernel, diagonal_sums = [], {}
    for c in range(1 << N):
        value = 0
        for i, p in enumerate(old_matrices):
            if c >> i & 1:
                value ^= p
        if not value & ~diagonal:
            kernel.append(c)
            diagonal_sums[c] = value
    require((1 << N) - 1 in kernel and all((a & b) in kernel for a in kernel for b in kernel),
            'unital Boolean diagonal intersection')
    signatures = {}
    for i in range(N):
        signatures.setdefault(tuple(c >> i & 1 for c in kernel), []).append(i)
    groups = list(signatures.values())
    indicators = [sum(1 << i for i in group) for group in groups]
    require(all(c in kernel for c in indicators) and len(kernel) == 1 << len(groups), 'partition gives the full kernel')
    active = [sum(((diagonal_sums[c] >> (j * n + j)) & 1) << j for j in range(N)) for c in indicators]
    require(all(mask.bit_count() == len(group) for mask, group in zip(active, groups)), 'target multiplicities')
    require(all(not (a & b) for a, b in itertools.combinations(active, 2))
            and sum(active) == (1 << N) - 1, 'active coordinate partition')
    k = N - len(groups) + 1
    require(len(basis(p & ~diagonal for p in old_matrices)) == k - 1, 'old pattern dimension')
    allowed = [outer(sum(((ys[i] >> j) & 1) << i for i in range(N)),
                     sum(((xs[i] >> j) & 1) << i for i in range(N)), n) & ~diagonal for j in range(N)]
    J = (1 << (n * n)) - 1
    Q = basis([J & ~diagonal] + allowed)
    ones = (1 << n) - 1
    normalized = [(1 << i, 1 << i) for i in range(N)] + [(ones, ones)]
    stars = [(left_project(normalized[i], J, n) ^ left_project(normalized[-1], outer(*normalized[i], n), n)) & ~diagonal
             for i in range(N)]
    require(len(Q) == k and len(basis((*Q, *stars))) == k + N, 'general star quotient')
    coordinate_count = sum(not (p & ~diagonal) for p in old_matrices)
    require(coordinate_count == sum(len(g) == 1 for g in groups), 'singleton blocks are coordinate projectors')
    products = {(i, j): reduce_vector(left_project(p, outer(*q, n), n) & ~diagonal, Q)
                for i, p in enumerate(normalized) for j, q in enumerate(normalized)}
    return {'N': N, 'xs': tuple(xs), 'ys': ys, 'groups': groups, 'active': active,
            'k': k, 'Q': Q, 'products': products, 'coordinate_count': coordinate_count}


def basis_census(N):
    counts, examples = Counter(), {}
    digest = hashlib.sha256()
    for xs in itertools.permutations(range(1, 1 << N), N):
        if len(basis(xs)) != N:
            continue
        row = inspect_basis(xs)
        key = str(tuple(sorted(map(len, row['groups']))))
        counts[key] += 1
        data = {name: row[name] for name in ('xs', 'ys', 'groups', 'active', 'k', 'coordinate_count')}
        examples.setdefault(key, data)
        digest.update((json.dumps(data, sort_keys=True) + '\n').encode())
    require(sum(counts.values()) == {2: 6, 4: 20160}[N], 'all invertible bases')
    return {'N': N, 'bases': sum(counts.values()), 'partition_counts': dict(sorted(counts.items())),
            'examples': examples, 'certificate_sha256': digest.hexdigest()}


def allocate_exponents(order, groups):
    N = sum(map(len, groups))
    locations = {kind: [i for i, value in enumerate(order) if value == kind] for kind in range(N + 1)}
    require(all(locations.values()), 'every old type and the bridge occur')
    dependent = {locations[N][-1]}
    for group in groups:
        dependent.update(locations[kind][-1] for kind in group[1:])
    free = [i for i in range(len(order)) if i not in dependent]
    r = len(free)
    exps = [[0] * r for _ in order]
    for column, pos in enumerate(free):
        exps[pos][column] = 1
    for group in groups:
        reference = [sum(exps[pos][j] for pos in locations[group[0]]) for j in range(r)]
        for kind in group[1:]:
            pos = locations[kind][-1]
            exps[pos] = [reference[j] - sum(exps[other][j] for other in locations[kind] if other != pos) for j in range(r)]
    pos = locations[N][-1]
    exps[pos] = [-sum(exps[other][j] for other in locations[N][:-1]) for j in range(r)]
    require(len(dependent) == N - len(groups) + 1, 'exact saturated relation count')
    return [tuple(row) for row in exps]


def ambient_frame(frame, a=1, b=1, fresh_width=1, unused=0):
    N = frame['N']
    require(a and b and a < 1 << fresh_width and b < 1 << fresh_width and (a & b).bit_count() % 2,
            'fresh pairing one')
    hx, hy = 0, 0
    for x, y in zip(frame['xs'], frame['ys']):
        hx ^= x
        hy ^= y
    pairs = list(zip(frame['xs'], frame['ys'])) + [(hx | (a << N), hy | (b << N))]
    require(all((x & y).bit_count() % 2 for x, y in pairs), 'all projectors are idempotent')
    width = N + fresh_width + unused
    require(len(basis(outer(x, y, width) & ~identity(width) for x, y in pairs)) == frame['k'],
            'actual ambient pattern dimension')
    require(len(basis(x for x, _ in pairs)) == N + 1, 'actual ambient image dimension')
    return pairs, width


def target_endpoint(frame, order, exps, width):
    N, r = frame['N'], len(exps[0])
    totals = [tuple(sum(row[j] for kind, row in zip(order, exps) if kind == i) for j in range(r)) for i in range(N)]
    expected = {(0,) * r: sum(1 << (i * width + i) for i in range(N, width))}
    for group, active in zip(frame['groups'], frame['active']):
        require(all(totals[i] == totals[group[0]] for i in group), 'equal labels within each kernel block')
        mask = sum(1 << (i * width + i) for i in range(N) if active >> i & 1)
        label = totals[group[0]]
        expected[label] = expected.get(label, 0) ^ mask
    return {key: value for key, value in expected.items() if value}


def frames():
    return {
        'coordinate4': inspect_basis((1, 2, 4, 8)),
        'quad4': inspect_basis(tuple(15 ^ (1 << i) for i in range(4))),
        'normal3_plus_normal3': inspect_basis((6, 5, 7, 48, 40, 56)),
        'edge2_plus_quad4': inspect_basis((1, 3) + tuple((15 ^ (1 << i)) << 2 for i in range(4))),
        'orthogonal6': inspect_basis(tuple(63 ^ (1 << i) for i in range(6))),
        'coordinate6': inspect_basis(tuple(1 << i for i in range(6))),
        'orthogonal8': inspect_basis(tuple(255 ^ (1 << i) for i in range(8))),
        'orthogonal10': inspect_basis(tuple(1023 ^ (1 << i) for i in range(10))),
    }


def word_domain(name, frame, h, full):
    N, counts = frame['N'], Counter()
    pairs, width = ambient_frame(frame)
    for order in orders(N // 2, h):
        exps = allocate_exponents(order, frame['groups'])
        block = consecutive(order, N)
        require((not quadratic(order, exps, frame['products'])) == block, 'general-basis quadratic chronology')
        if full:
            actual = laurent(order, exps, pairs, width)
            expected = target_endpoint(frame, order, exps, width)
            require((actual == expected) == block, 'full original-coordinate endpoint')
            if not block:
                require(any(matrix & ~identity(width) for matrix in actual.values()), 'nonconsecutive word is not diagonal')
        counts['orders'] += 1
        counts['passing'] += block
    order = next(orders(N // 2, h))
    exps = allocate_exponents(order, frame['groups'])
    require(len(exps) - rational_rank(exps) == frame['k'], 'actual exponent relation rank')
    return {'name': name, 'N': N, 'k': frame['k'], 'partition': frame['groups'], 'bridges': h,
            'full_laurent': full, 'counts': dict(counts)}


def ambient_checks(all_frames):
    result = []
    for name, frame in all_frames.items():
        N = frame['N']
        pairs, width = ambient_frame(frame, 3, 5, 3, 2)
        old = (0, 0) + tuple(range(1, N))
        order = old[:N // 2] + (N, N, N) + old[N // 2:]
        exps = allocate_exponents(order, frame['groups'])
        require(len(exps) - rational_rank(exps) == frame['k'], 'repeated-type word keeps the exact relation budget')
        actual = laurent(order, exps, pairs, width)
        kept = [(kind, row) for kind, row in zip(order, exps) if kind != N]
        deleted = laurent([x[0] for x in kept], [x[1] for x in kept], pairs, width)
        require(actual == deleted == target_endpoint(frame, order, exps, width), 'full ambient target multiplicities and deletion')
        omit = order.index(N)
        wrong = laurent(order[:omit] + order[omit + 1:], exps[:omit] + exps[omit + 1:], pairs, width)
        delta = [wrong.get(key, 0) ^ actual.get(key, 0) for key in wrong.keys() | actual.keys()]
        require(any(any(matrix >> (i * width + N + 2) & 1 for i in range(width)) for matrix in delta),
                'one omitted bridge changes a dirty spectator column')
        result.append({'name': name, 'N': N, 'width': width, 'k': frame['k'], 'old_calls': len(old),
                       'coordinate_old_types': frame['coordinate_count'], 'physical_block_supports': frame['active'],
                       'endpoint_terms': len(actual), 'dirty_column_checked': N + 2})
    return result


def boundary_controls(all_frames):
    frame = all_frames['quad4']
    N, n = 4, 5
    order = (4, 0, 1, 2, 3, 4)
    exps = allocate_exponents(order, frame['groups'])
    diagonal, J = identity(n), (1 << (n * n)) - 1
    coarse = basis([J & ~diagonal] + [1 << (i * n + j) for i in range(N) for j in range(N) if i != j])
    ones = (1 << n) - 1
    normalized = [(1 << i, 1 << i) for i in range(N)] + [(ones, ones)]
    products = {(i, j): reduce_vector(left_project(p, outer(*q, n), n) & ~diagonal, coarse)
                for i, p in enumerate(normalized) for j, q in enumerate(normalized)}
    require(not quadratic(order, exps, products), 'coarse endpoint quotient loses the obstruction')
    require(quadratic(order, exps, frame['products']), 'actual conjugated diagonal quotient rejects')
    pairs, width = ambient_frame(frame)
    require(any(matrix & ~identity(width) for matrix in laurent(order, exps, pairs, width).values()),
            'coarse false positive fails the full endpoint')
    # A binary diagonal perturbation of J_N is never idempotent when N is even.
    checked = 0
    for N in (2, 4, 6):
        for mask in range(1 << N):
            JN = (1 << (N * N)) - 1
            M = JN ^ sum(1 << (i * N + i) for i in range(N) if mask >> i & 1)
            squared_diagonal = [sum(((M >> (i * N + j)) & 1) * ((M >> (j * N + i)) & 1)
                                    for j in range(N)) % 2 for i in range(N)]
            require(squared_diagonal != [(M >> (i * N + i)) & 1 for i in range(N)], 'idempotence obstruction')
            checked += 1
    require((15 & 15).bit_count() % 2 == 0, 'odd old dimension gives a nonidempotent all-one bridge')
    rejected = False
    try:
        inspect_basis((1, 2, 4))
    except ValueError as e:
        rejected = str(e) == 'positive even old dimension'
    require(rejected, 'odd-dimension guard')
    return {'single_quad_coarse_quotient_false_positive': {'order': order, 'k': 4, 'full_endpoint_rejected': True},
            'even_diagonal_perturbations_rejected': checked, 'odd_old_dimension_rejected': True,
            'coordinate_basis_four_pattern_dimension': all_frames['coordinate4']['k']}


def compute():
    all_frames = frames()
    domains = []
    for name, hs in [('coordinate4', range(1, 4)), ('quad4', range(1, 5)),
                     ('normal3_plus_normal3', range(1, 4)), ('edge2_plus_quad4', (2,)), ('orthogonal6', (2,))]:
        for h in hs:
            full = h == 2 and name in {'coordinate4', 'quad4', 'normal3_plus_normal3'}
            domains.append(word_domain(name, all_frames[name], h, full))
    return {'status': 'PASS_ORTHOGONAL_BASIS_BRIDGE_OBSTRUCTION',
            'scope': 'Every old type in an arbitrary even orthogonal binary basis, including coordinate types, plus one fresh pairing-one bridge; actual pattern relation budget and diagonal monomial endpoint.',
            'basis_censuses': [basis_census(N) for N in (2, 4)],
            'word_domains': domains, 'ambient_checks': ambient_checks(all_frames),
            'boundary_controls': boundary_controls(all_frames),
            'limitations': ['The alphabet is specified; extra projector types and larger relation budgets are not covered.',
                            'All-width and all-length conclusions rest on the written proof.',
                            'No native implementation, complete multiplier invoice or new kappa.']}


if __name__ == '__main__':
    actual = json.loads(json.dumps(compute()))
    expected = json.loads(Path(__file__).with_name('RESULT.json').read_text())
    require(actual == expected, 'committed exact receipt')
    print(actual['status'])
    print(json.dumps({'binary_bases': sum(r['bases'] for r in actual['basis_censuses']),
                      'quadratic_orders': sum(r['counts']['orders'] for r in actual['word_domains']),
                      'full_laurent_orders': sum(r['counts']['orders'] for r in actual['word_domains'] if r['full_laurent']),
                      'ambient_fixtures': len(actual['ambient_checks'])}, sort_keys=True))
