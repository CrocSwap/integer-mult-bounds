"""Check seven shared-hub calls and the two exceptional proof cases.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from hashlib import sha1, sha256
from itertools import permutations, product
import json
from math import factorial, gcd
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
PAIRS = ((6, 5), (5, 6), (7, 7), (12, 20), (20, 12), (28, 28))
SUPPORTS = tuple((tuple(i for i in range(5) if u >> i & 1),
                  tuple(i for i in range(5) if v >> i & 1)) for u, v in PAIRS)
ORDERS = tuple(permutations(range(7)))
# S, T and X; X and S-X are the two calls of the repeated type.
CASES = (
    ('S', (2, 0), (0, 1), (1, 0)),
    ('T', (1, 0), (0, 2), (0, 1)),
    ('X', (1, 0), (0, 1), (2, 0)),
    ('S+T', (1, 0), (1, 2), (0, 1)),
    ('S+X', (1, 0), (0, 1), (1, 2)),
    ('T+X', (1, 0), (0, 1), (0, 1)),
    ('S+T+X', (1, 0), (0, 1), (1, 1)),
    ('rank-one-1', (1, 0), (1, 0), (2, 0)),
    ('rank-one-2', (2, 0), (1, 0), (1, 0)),
    ('rank-one-3', (1, 0), (2, 0), (2, 0)),
    ('rank-one-4', (4, 0), (2, 0), (1, 0)),
    ('rank-one-5', (2, 0), (4, 0), (1, 0)),
    ('rank-one-6', (1, 0), (-1, 0), (2, 0)),
)


def require(value, message):
    if not value:
        raise ArithmeticError(message)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def parity(a):
    return (a[0] & 1) | ((a[1] & 1) << 1)


def quadratic(a, b):
    return ((a & b & 1) | ((((a & 1) * (b >> 1)) ^
            ((a >> 1) * (b & 1))) << 1) | ((a & b & 2) << 1))


def types_for(repeated):
    side = 0 if repeated < 3 else 3
    other = tuple(i for i in range(side, side + 3) if i != repeated)
    opposite = tuple(i for i in range(6) if i // 3 != repeated // 3)
    return (repeated, repeated, *other, *opposite)


def separated(order):
    first, last = sorted((order.index(0), order.index(1)))
    return any(call >= 4 for call in order[first + 1:last])


def two_blocks(order):
    return set(order[:4]) == set(range(4)) or set(order[:3]) == {4, 5, 6}


def cross_coefficients(order, labels, first_mixed=False):
    positions = [order.index(i) for i in range(7)]
    rows = []
    for calls in ((0, 1), (2,), (3,)):
        for b in (4, 5, 6):
            value = 0
            for a in calls:
                if positions[b] < positions[a]:
                    value ^= labels[a] if first_mixed else quadratic(labels[a], labels[b])
            rows.append(value)
    return rows


def check_leading_cases():
    records = []
    for f1, f2 in ((1, 1), (1, 2), (0, 1), (1, 0)):
        labels = (f1, f2, f1 ^ f2, f1 ^ f2, 1, 1, 1)
        passing = separated_pass = 0
        for order in ORDERS:
            values = cross_coefficients(order, labels, True)
            if len(set(values)) != 1:
                continue
            passing += 1
            separated_pass += separated(order)
            if not f1 or not f2:
                zero = 0 if f1 == 0 else 1
                core = tuple(i for i in order if i != zero)
                require(set(core[:3]) == (set(range(4)) - {zero}) or
                        set(core[:3]) == {4, 5, 6}, 'visible core has two blocks')
            else:
                require(not separated(order), 'leading forms admit a separator')
        records.append({'leading_forms': [f1, f2], 'passing_orders': passing,
                        'separated_passing_orders': separated_pass})
    # Every ordered pair of vectors has one of the four stated relation types.
    for f1, f2 in product(range(8), repeat=2):
        if not (f1 or f2):
            continue
        for alpha, beta, epsilon in product(range(2), repeat=3):
            if (f1 * alpha) ^ (f2 * beta) != (f1 ^ f2) * epsilon:
                continue
            if f1 and f2:
                require(alpha == beta, 'all coefficient relations')
                if f1 != f2:
                    require(alpha == epsilon, 'independent coefficient relations')
            else:
                require((alpha if f1 else beta) == epsilon, 'visible coefficient relation')
    return {'canonical_cases': records, 'coefficient_pairs': 63,
            'indicator_cases': 504, 'order_cases': 4 * len(ORDERS)}


def integer_matrix(pair):
    u, v = pair
    return sum(((u >> i & 1) * (v >> j & 1)) << (5 * i + j)
               for i in range(5) for j in range(5))


def matrix_product(a, b):
    return sum((sum(((a >> (5 * i + k)) & (b >> (5 * k + j)) & 1)
                    for k in range(5)) % 2) << (5 * i + j)
               for i in range(5) for j in range(5))


def off(a):
    return a & ~sum(1 << (6 * i) for i in range(5))


def span_basis(values):
    basis = {}
    for value in values:
        while value:
            pivot = value.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = value
                break
            value ^= basis[pivot]
    return basis


def remainder(value, basis):
    for pivot in sorted(basis, reverse=True):
        if value >> pivot & 1:
            value ^= basis[pivot]
    return value


def check_pool():
    matrices = list(map(integer_matrix, PAIRS))
    for i, matrix in enumerate(matrices):
        require(matrix_product(matrix, matrix) == matrix, 'idempotent')
        for j in range(6):
            if i != j and i // 3 == j // 3:
                require(matrix_product(matrix, matrices[j]) == 0, 'orthogonal triple')
    basis = span_basis(map(off, matrices))
    require(len(basis) == 4, 'pattern rank')
    commutators = [remainder(off(matrix_product(a, b) ^ matrix_product(b, a)), basis)
                   for a in matrices[:3] for b in matrices[3:]]
    zeros = []
    for mask in range(1, 512):
        value = 0
        for i, matrix in enumerate(commutators):
            if mask >> i & 1:
                value ^= matrix
        if value == 0:
            zeros.append(mask)
    require(zeros == [511], 'rank-eight commutator quotient')
    reflection = lambda a: sum((a >> i & 1) << (4 - i) for i in range(5))
    require(tuple((reflection(u), reflection(v)) for u, v in PAIRS[:3]) == PAIRS[3:],
            'reflection exchanges the triples')
    return {'off_pattern_rank': 4, 'commutator_rank': 8, 'subset_checks': 511}


def full_product(order, types, vectors):
    radix = 2 * sum(abs(a) for a, _ in vectors) + 1
    labels = [a + radix * b for a, b in vectors]
    offset = sum(-a for a in labels if a < 0)
    one = 1 << offset
    rows = [[one if i == j else 0 for j in range(5)] for i in range(5)]
    for call in order:
        image, covector = SUPPORTS[types[call]]
        exponent = labels[call]
        for column in range(5):
            donor = 0
            for row in covector:
                donor ^= rows[row][column]
            shifted = donor << exponent if exponent >= 0 else donor >> -exponent
            require(exponent >= 0 or (shifted << -exponent) == donor, 'Laurent shift')
            delta = donor ^ shifted
            for row in image:
                rows[row][column] ^= delta
    return rows, radix, offset


def sparse_product(order, types, vectors):
    one = {(0, 0)}
    rows = [[one.copy() if i == j else set() for j in range(5)] for i in range(5)]
    for call in order:
        u, v = PAIRS[types[call]]
        factor = [[({(0, 0)} if i == j else set()) ^
                   ({(0, 0), vectors[call]} if (u >> i & v >> j & 1) else set())
                   for j in range(5)] for i in range(5)]
        result = [[set() for _ in range(5)] for _ in range(5)]
        for i, j, k in product(range(5), repeat=3):
            for a in factor[i][k]:
                for b in rows[k][j]:
                    value = add(a, b)
                    if value in result[i][j]:
                        result[i][j].remove(value)
                    else:
                        result[i][j].add(value)
        rows = result
    return rows


def check_full_words():
    records = []
    sparse_checks = 0
    for repeated in range(6):
        types = types_for(repeated)
        for name, s, t, x in CASES:
            vectors = (x, add(s, tuple(-v for v in x)), s, s, t, t, t)
            require(all(v != (0, 0) for v in vectors), 'nonzero labels')
            minors = [abs(a[0] * b[1] - a[1] * b[0]) for a in vectors for b in vectors]
            paid_rank = 2 if any(minors) else 1
            if paid_rank == 2:
                require(gcd(*minors) == 1, 'paid-generated Z2 and saturated kernel')
            else:
                require(all(b == 0 for _, b in vectors) and gcd(*(abs(a) for a, _ in vectors)) == 1,
                        'paid-generated Z and saturated kernel')
            targets = (s, s, add(s, t), t, t) if repeated < 3 else (t, t, add(s, t), s, s)
            passed = 0
            digest = sha256()
            for index, order in enumerate(ORDERS):
                rows, radix, offset = full_product(order, types, vectors)
                diagonal = all(rows[i][j] == 0 for i in range(5) for j in range(5) if i != j)
                require(diagonal == two_blocks(order), 'full seven-call endpoint')
                if diagonal:
                    require([rows[i][i] for i in range(5)] ==
                            [1 << (offset + a + radix * b) for a, b in targets],
                            'exact hub and private targets')
                    passed += 1
                digest.update(json.dumps(rows, separators=(',', ':')).encode() + b'\n')
                if index in (0, 39, 101, 777, 2048, 5039):
                    sparse = sparse_product(order, types, vectors)
                    encoded = [[sum(1 << (offset + a + radix * b) for a, b in entry)
                                for entry in row] for row in sparse]
                    require(rows == encoded, 'independent bivariate multiplication')
                    sparse_checks += 1
            require(passed == 2 * factorial(4) * factorial(3), 'block count')
            records.append({'repeated_type': repeated, 'fixture': name, 'paid_rank': paid_rank, 'relations': 7 - paid_rank, 'orders': len(ORDERS),
                            'diagonal': passed, 'full_matrix_sha256': digest.hexdigest()})
    return {'cases': records, 'sparse_products': sparse_checks,
            'words': len(records) * len(ORDERS), 'diagonal': sum(r['diagonal'] for r in records)}


def pmul(a, b):
    result = set()
    for x in a:
        for y in b:
            value = x + y
            if value in result:
                result.remove(value)
            else:
                result.add(value)
    return result


def pmat(a, b):
    result = [[set() for _ in range(3)] for _ in range(3)]
    for i, j, k in product(range(3), repeat=3):
        result[i][j] ^= pmul(a[i][k], b[k][j])
    return result


def factor_sum(coefficients):
    return [
        [({0} if i == j else set()) ^
         xor_all(coefficient if (u >> i & v >> j & 1) else set()
                 for coefficient, (u, v) in zip(coefficients, PAIRS[:3]))
         for j in range(3)] for i in range(3)]


def xor_all(values):
    result = set()
    for value in values:
        result ^= value
    return result


def check_exact_cut():
    one = {0}
    a, b, c, d, t = ({1 << (4 * i)} for i in range(5))
    scale = [[one if i == j and i < 2 else t if i == j else set()
              for j in range(3)] for i in range(3)]

    def word(repeated, coefficients):
        extra = [set(), set(), set()]
        extra[repeated] = d
        return pmat(factor_sum(extra), pmat(scale, factor_sum(coefficients)))

    initial = word(0, (a, b, c))
    require(initial[0][1] == initial[0][2] == b ^ c, 'A0 initial private row')
    w = word(0, (a, b, b))
    require(w[1][0] ^ w[2][0] == pmul(one ^ t, a ^ b), 'A0 cut elimination')
    require(word(0, (a, a, a))[1][2] == pmul(pmul(d, t), one ^ a), 'A0 final factor')
    swapped = word(1, (b, a, b))
    require(all(swapped[i][j] == w[1 - i if i < 2 else 2][1 - j if j < 2 else 2]
                for i in range(3) for j in range(3)), 'A1 private permutation')
    general = word(2, (a, b, c))
    require(general[0][2] ^ general[1][2] == a ^ b, 'A2 private difference')
    w = word(2, (a, a, c))
    require(w[0][1] ^ w[0][2] == pmul(pmul(d, one ^ a), one ^ t), 'A2 final factor')
    # Every nonempty proper B prefix misses at least one coefficient.
    prefix_masks = []
    for mask in range(1, 7):
        patterns = [(v >> 3) & 3 for i, (_, v) in enumerate(PAIRS[3:]) if mask >> i & 1]
        rank = len(span_basis(patterns))
        require(rank == mask.bit_count(), 'proper prefix cut is injective')
        prefix_masks.append({'mask': mask, 'rank': rank})
    return {'symbolic_identities': 6, 'proper_prefix_masks': prefix_masks}


def controls():
    _, s, t, x = CASES[2]
    vectors = (x, add(s, tuple(-v for v in x)), s, s, t, t, t)
    order = (1, 2, 3, 4, 0, 5, 6)
    values = cross_coefficients(order, tuple(map(parity, vectors)))
    require(len(set(values)) == 1 and separated(order), 'even repeated label evades degree two')
    rows, _, _ = full_product(order, types_for(0), vectors)
    require(any(rows[i][j] for i in range(5) for j in range(5) if i != j), 'exact cut detects separator')
    labels = list(vectors)
    labels[2] = add(labels[2], (2, 0))
    require(tuple(map(parity, labels)) == tuple(map(parity, vectors)), 'even mutation parity')
    rows, _, _ = full_product(tuple(range(7)), types_for(0), labels)
    require(any(rows[i][j] for i in range(5) for j in range(5) if i != j), 'even total mutation')
    rows, radix, offset = full_product(tuple(range(7)), types_for(0), vectors)
    require(rows[2][2] != 1 << (offset + s[0] + radix * s[1]), 'missing hub contribution')
    return ['even repeated separator', 'even type-total mutation', 'missing hub target']


def source_replay():
    pins = json.loads((ROOT / 'SOURCE-PINS.json').read_text())['sources']
    for pin in pins:
        data = (ROOT / pin['retained']).read_bytes()
        require(sha256(data).hexdigest() == pin['sha256'], 'retained SHA256')
        require(sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
                == pin['git_blob'], 'retained Git blob')
    command = [sys.executable, '-W', 'error', *(['-O'] if sys.flags.optimize else []),
               '-B', str(ROOT / 'retained/single-pass/verify.py')]
    result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
    require('PASS_SHARED_HUB_SINGLE_PASS cases=527040 diagonal=792' in result.stdout,
            'unchanged source replay')
    return len(pins)


def collect():
    require(len(ORDERS) == factorial(7) and len(set(ORDERS)) == factorial(7), 'order coverage')
    return {'source_files': source_replay(), 'pool': check_pool(), 'leading_cases': check_leading_cases(),
            'exact_cut': check_exact_cut(), 'full_words': check_full_words(), 'controls': controls()}


def main():
    actual = collect()
    require(actual == json.loads((ROOT / 'RESULT.json').read_text()), 'saved certificate')
    print('PASS_SHARED_HUB_SEVEN_CALL')
    print('4 complete leading-form cases; 20160 order checks; 511 commutator subsets')
    print('393120 full Laurent words; 22464 diagonal endpoints; 468 independent sparse products')
    print('All three repeated projector types and both triples; exact exceptional cuts and controls')


if __name__ == '__main__':
    main()
