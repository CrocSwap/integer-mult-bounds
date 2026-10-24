"""Check the dual-number obstruction with small exact matrices.

Use no solver, constructor, or external package. Elements of the ring
are two bits: constant term first, then the coefficient of epsilon.
"""

from fractions import Fraction as Q
from itertools import permutations, product
import hashlib
import json
from pathlib import Path


def multiply(a, b):
    return ((a & 1) * (b & 1)) | ((((a >> 1) * (b & 1)) ^ ((a & 1) * (b >> 1))) << 1)


def mm(a, b):
    return [[sum_xor(multiply(a[i][k], b[k][j]) for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def sum_xor(values):
    out = 0
    for value in values:
        out ^= value
    return out


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def add(a, b):
    return [[x ^ y for x, y in zip(row, other)] for row, other in zip(a, b)]


def outer(a, b):
    return [[multiply(x, y) for y in b] for x in a]


def binary_rank(a):
    pivots = {}
    for row in a:
        x = sum(value << i for i, value in enumerate(row))
        while x:
            j = x.bit_length() - 1
            if j in pivots:
                x ^= pivots[j]
            else:
                pivots[j] = x
                break
    return len(pivots)


def rational_rank(a):
    a = [[Q(x) for x in row] for row in a]
    pivot = 0
    for col in range(len(a[0])):
        selected = next((j for j in range(pivot, len(a)) if a[j][col]), None)
        if selected is None:
            continue
        a[pivot], a[selected] = a[selected], a[pivot]
        divisor = a[pivot][col]
        a[pivot] = [x / divisor for x in a[pivot]]
        for j in range(len(a)):
            if j != pivot:
                q = a[j][col]
                a[j] = [x - q * y for x, y in zip(a[j], a[pivot])]
        pivot += 1
    return pivot


def monomials(n, weights):
    return [(p, w) for p in permutations(range(n)) for w in product(weights, repeat=n)]


def compose(g, h):
    p, a = g
    q, b = h
    return tuple(p[q[j]] for j in range(len(p))), tuple(a[q[j]] * b[j] for j in range(len(p)))


def image(g):
    p, weights = g
    a = [[0] * len(p) for _ in p]
    for j, i in enumerate(p):
        assert weights[j]
        a[i][j] = 1 if weights[j] > 0 else 3
    return a


def rational_matrix(g):
    p, weights = g
    return [[weights[j] if p[j] == i else Q(0) for j in range(len(p))] for i in range(len(p))]


def difference(g):
    a = rational_matrix(g)
    return [[x - int(i == j) for j, x in enumerate(row)] for i, row in enumerate(a)]


def primitive_factor(g):
    p, weights = g
    n = len(p)
    moved = [i for i in range(n) if p[i] != i]
    a, b = [0] * n, [0] * n
    if not moved:
        changed = [i for i, value in enumerate(weights) if value != 1]
        assert len(changed) == 1
        i = changed[0]
        a[i], b[i] = (2 if weights[i] < 0 else 0), 1
        negative = weights[i] < 0
    else:
        assert len(moved) == 2
        i, j = moved
        assert p[i] == j and p[j] == i and weights[i] * weights[j] == 1
        assert all(weights[k] == 1 for k in range(n) if k not in moved)
        a[i] = b[i] = 1
        a[j] = b[j] = 1 if weights[i] > 0 else 3
        negative = True
    assert outer(a, b) == add(image(g), eye(n))
    return a, b, negative


for a, b, c in product(range(4), repeat=3):
    assert multiply(a, b ^ c) == multiply(a, b) ^ multiply(a, c)
    assert multiply(multiply(a, b), c) == multiply(a, multiply(b, c))
assert multiply(2, 2) == 0 and multiply(3, 3) == 1

weights = tuple(map(Q, (1, -1, 2, -2))) + (Q(1, 2), Q(-1, 2))
counts = {}
primitive_pool = []
for n in (1, 2, 3):
    pool = monomials(n, weights)
    primitives = [g for g in pool if rational_rank(difference(g)) == 1]
    for g in primitives:
        primitive_factor(g)
    counts[n] = {'maps': len(pool), 'rank_one_maps': len(primitives)}
    if n == 3:
        primitive_pool = primitives

signed = monomials(3, (Q(1), Q(-1)))
weighted = monomials(2, weights)
homomorphism_pairs = 0
for pool in (signed, weighted):
    for g in pool:
        for h in pool:
            assert image(compose(g, h)) == mm(image(g), image(h))
            homomorphism_pairs += 1

vectors = [[(x >> i) & 1 for i in range(4)] for x in range(1, 16)]
outer_checks = 0
idempotents = 0
for a, b in product(vectors, repeat=2):
    idempotents += sum(x * y for x, y in zip(a, b)) % 2
    for g in primitive_pool:
        u, v, _ = primitive_factor(g)
        x = [multiply(c, t) for c in a for t in u]
        y = [multiply(c, t) for c in b for t in v]
        delta = add(image(g), eye(3))
        wanted = [[multiply(a[i // 3] * b[j // 3], delta[i % 3][j % 3])
                   for j in range(12)] for i in range(12)]
        assert outer(x, y) == wanted
        outer_checks += 1
assert idempotents == 120 and outer_checks == 7425

# Check the constant-term rank inequality on every binary pair of these sizes.
kernel_pairs = 0
for d, k in ((2, 1), (3, 1), (3, 2)):
    for bs in product((0, 1), repeat=d * k):
        b = [list(bs[i * k:(i + 1) * k]) for i in range(d)]
        for cs in product((0, 1), repeat=k * d):
            c = [list(cs[i * d:(i + 1) * d]) for i in range(k)]
            if mm(b, c) == [[0] * d for _ in range(d)]:
                assert binary_rank(b) + binary_rank(c) <= k
                kernel_pairs += 1

# Exhaust all R factorizations with d=2 and k=1.
epsilon_identity_two = [[2, 0], [0, 2]]
for bs, cs in product(product(range(4), repeat=2), repeat=2):
    assert mm([[bs[0]], [bs[1]]], [list(cs)]) != epsilon_identity_two
assert mm([[2, 0], [0, 2]], eye(2)) == epsilon_identity_two

# Replay the sharp coordinate word and its telescoping outer factors.
p = eye(12)
columns, rows, word = [], [], []
for role in range(4):
    for address in range(3):
        a = [int(i == role) for i in range(4)]
        b = list(a)
        g = tuple(range(3)), tuple(Q(-1 if i == address else 1) for i in range(3))
        u, v, negative = primitive_factor(g)
        assert negative
        x = [multiply(c, t) for c in a for t in u]
        y = [multiply(c, t) for c in b for t in v]
        columns.append(x)
        rows.append(mm([y], p)[0])
        p = mm(add(eye(12), outer(x, y)), p)
        word.append({'role': role, 'axis_flip': address})
b = [[column[i] for column in columns] for i in range(12)]
c = rows
epsilon_identity = [[2 * int(i == j) for j in range(12)] for i in range(12)]
assert add(p, eye(12)) == epsilon_identity == mm(b, c)
b0 = [[x & 1 for x in row] for row in b]
b1 = [[x >> 1 for x in row] for row in b]
c0 = [[x & 1 for x in row] for row in c]
c1 = [[x >> 1 for x in row] for row in c]
assert mm(b0, c0) == [[0] * 12 for _ in range(12)]
assert add(mm(b0, c1), mm(b1, c0)) == eye(12)
assert binary_rank(b0) + binary_rank(c0) == 12

# Check the native group-algebra endpoint of the same coordinate word.
identity_group = tuple(range(3)), (Q(1),) * 3
native = [[{identity_group} if i == j else set() for j in range(4)] for i in range(4)]
for query in word:
    role, axis = query['role'], query['axis_flip']
    g = tuple(range(3)), tuple(Q(-1 if i == axis else 1) for i in range(3))
    native[role] = [{compose(g, term) for term in entry} for entry in native[role]]
negative_identity = tuple(range(3)), (Q(-1),) * 3
assert native == [[{negative_identity} if i == j else set() for j in range(4)] for i in range(4)]

# Track a clean helper through noninvertible, ADDRESS-neutral copies and clears.
p = s = [[1, 0], [0, 1], [0, 0]]
bs, cs = [], []
events = [
    ('free', [[1, 0, 0], [0, 1, 0], [1, 0, 0]]),
    ('free', [[0, 0, 0], [0, 1, 0], [0, 0, 1]]),
    ('query', 2),
    ('free', [[0, 0, 1], [0, 1, 0], [0, 0, 1]]),
    ('free', [[1, 0, 0], [0, 1, 0], [0, 0, 0]]),
    ('query', 1),
]
for kind, data in events:
    if kind == 'free':
        p, s = mm(data, p), mm(data, s)
        bs = [mm(data, [[x] for x in column]) for column in bs]
        bs = [[row[0] for row in column] for column in bs]
    else:
        x = [2 * int(i == data) for i in range(3)]
        y = [int(i == data) for i in range(3)]
        bs.append(x)
        cs.append(mm([y], p)[0])
        p = mm(add(eye(3), outer(x, y)), p)
    correction = [[0] * 2 for _ in range(3)]
    for x, y in zip(bs, cs):
        correction = add(correction, outer(x, y))
    assert p == add(s, correction)
assert s[:2] == eye(2) and p[:2] == [[3, 0], [0, 3]]
assert p[2] == [0, 0] and len(bs) == 2

# An entrywise sign rule on a genuine shear is not a group homomorphism.
shear_image = [[1, 1], [0, 1]]
assert mm(shear_image, shear_image) == eye(2)
assert shear_image != eye(2)  # I+2E01 has the same entrywise sign image.

result = {
    'status': 'PASS_INDEPENDENT_NATIVE_DUAL_CHECK',
    'dependencies': 'Python standard library only',
    'weighted_monomial_classification': counts,
    'representation_pairs': homomorphism_pairs,
    'binary_rank_one_role_matrices': 225,
    'binary_rank_one_idempotents': idempotents,
    'controlled_outer_factor_checks': outer_checks,
    'constant_kernel_pairs_checked': kernel_pairs,
    'dual_factorizations_d2_k1_rejected': 256,
    'sharp_coordinate_word_calls': len(word),
    'sharp_coordinate_word_target_dimension': 12,
    'telescoping_factorization_pass': True,
    'sharp_coordinate_word_full_group_algebra_endpoint_pass': True,
    'noninvertible_copy_clear_and_clean_helper_control_pass': True,
    'clean_helper_control_productive_roles': 2,
    'clean_helper_control_negative_queries': 2,
    'nonmonomial_shear_extension_rejected': True,
    'scope': 'Finite controls for the written general proof. This is not an exhaustive search over arbitrary rational words or a proof about genuine nonmonomial shears.',
    'word': word,
}
here = Path(__file__).resolve().parent
result['checker_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(here / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps(result, indent=2))
