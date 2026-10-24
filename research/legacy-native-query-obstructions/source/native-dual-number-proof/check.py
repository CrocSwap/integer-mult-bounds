"""Check the native monomial obstruction in a ring of characteristic two."""
from fractions import Fraction as Q
from itertools import permutations, product
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent

def ring_product(a, b):
    return ((a & 1)*(b & 1)) | ((((a & 1)*((b >> 1) & 1)) ^
                                (((a >> 1) & 1)*(b & 1))) << 1)

def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))

def ring_matrix_product(a, b):
    return tuple(tuple(xor_sum(ring_product(a[i][k], b[k][j])
                              for k in range(len(b)))
                       for j in range(len(b[0]))) for i in range(len(a)))

def xor_sum(values):
    value = 0
    for x in values:
        value ^= x
    return value

def rational_product(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(len(b)))
                       for j in range(len(b[0]))) for i in range(len(a)))

def rank(a):
    a = [list(r) for r in a]
    count = 0
    for j in range(len(a[0])):
        p = next((i for i in range(count, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[count], a[p] = a[p], a[count]
        pivot = a[count][j]
        a[count] = [x/pivot for x in a[count]]
        for i in range(len(a)):
            if i != count:
                value = a[i][j]
                a[i] = [x-value*y for x, y in zip(a[i], a[count])]
        count += 1
    return count

def binary_rank(a):
    a = [sum((x & 1) << j for j, x in enumerate(row)) for row in a]
    count = 0
    for j in range(max((x.bit_length() for x in a), default=0)):
        p = next((i for i in range(count, len(a)) if (a[i] >> j) & 1), None)
        if p is None:
            continue
        a[count], a[p] = a[p], a[count]
        for i in range(len(a)):
            if i != count and ((a[i] >> j) & 1):
                a[i] ^= a[count]
        count += 1
    return count

def representation(g):
    assert all(sum(x != 0 for x in row) == 1 for row in g)
    assert all(sum(g[i][j] != 0 for i in range(len(g))) == 1
               for j in range(len(g)))
    return tuple(tuple(0 if x == 0 else 1 if x > 0 else 3 for x in row) for row in g)

def difference(a):
    return tuple(tuple(x ^ int(i == j) for j, x in enumerate(row))
                 for i, row in enumerate(a))

def tensor(a, b):
    return tuple(tuple(ring_product(a[i//len(b)][j//len(b[0])],
                                   b[i % len(b)][j % len(b[0])])
                       for j in range(len(a[0])*len(b[0])))
                 for i in range(len(a)*len(b)))

def outer(u, v):
    return tuple(tuple(ring_product(x, y) for y in v) for x in u)

def factor_difference(g):
    d = difference(representation(g))
    changed = [i for i in range(3) if any(d[i])]
    if not changed:
        return (0, 0, 0), (0, 0, 0)
    if len(changed) == 1:
        i = changed[0]
        assert d[i][i] == 2
        u = tuple(2*int(j == i) for j in range(3))
        v = tuple(int(j == i) for j in range(3))
    else:
        assert len(changed) == 2
        i, j = changed
        u = tuple(1 if k == i else d[i][j] if k == j else 0 for k in range(3))
        v = u
    assert outer(u, v) == d
    return u, v

# The coefficient ring and its sign character are checked without integers
# being used as binary VALUE coefficients.
assert ring_product(2, 2) == 0
assert ring_product(3, 3) == 1
for a, b, c in product(range(4), repeat=3):
    assert ring_product(a, b) == ring_product(b, a)
    assert ring_product(ring_product(a, b), c) == ring_product(a, ring_product(b, c))
    assert ring_product(a, b ^ c) == ring_product(a, b) ^ ring_product(a, c)

# Entrywise signs do not extend to nonmonomial maps. A unipotent square
# is a concrete failure of that proposed extension.
unipotent = ((Q(1), Q(1), Q(0)), (Q(0), Q(1), Q(0)), (Q(0), Q(0), Q(1)))
unipotent_square = rational_product(unipotent, unipotent)
invalid_sign_map = lambda g: tuple(tuple(0 if x == 0 else 1 if x > 0 else 3 for x in row) for row in g)
assert invalid_sign_map(unipotent_square) != ring_matrix_product(invalid_sign_map(unipotent), invalid_sign_map(unipotent))

group = sorted({tuple(tuple(Q(s[i]*int(j == p[i])) for j in range(3))
                      for i in range(3))
                for p in permutations(range(3)) for s in product((1, -1), repeat=3)})
assert len(group) == 48
homomorphism_checks = 0
for a in group:
    for b in group:
        assert representation(rational_product(a, b)) == ring_matrix_product(representation(a), representation(b))
        homomorphism_checks += 1
reflections = [g for g in group if rank([[g[i][j]-int(i == j) for j in range(3)] for i in range(3)]) == 1]
assert len(reflections) == 9
scalar_pool = [(tuple((u >> i) & 1 for i in range(4)),
                tuple((v >> i) & 1 for i in range(4)))
               for u in range(1, 16) for v in range(1, 16)
               if (u & v).bit_count() % 2]
assert len(scalar_pool) == 120
query_factorizations = 0
for g in reflections:
    u, v = factor_difference(g)
    for a, b in scalar_pool:
        n = outer(a, b)
        assert ring_matrix_product(n, n) == n
        left = tuple(ring_product(x, y) for x in a for y in u)
        right = tuple(ring_product(x, y) for x in b for y in v)
        assert outer(left, right) == tensor(n, difference(representation(g)))
        query_factorizations += 1

# Arbitrary rational reciprocal weights and scales include positive queries.
weighted_checks = 0
for a in (Q(1, 2), Q(2), Q(-3, 2), Q(-5)):
    for i in range(3):
        scale = tuple(tuple(a if r == s == i else Q(r == s) for s in range(3)) for r in range(3))
        assert rank([[scale[r][s]-int(r == s) for s in range(3)] for r in range(3)]) == 1
        factor_difference(scale)
        weighted_checks += 1
        for j in range(3):
            if i == j:
                continue
            swap = tuple(tuple(a if (r, s) == (i, j) else 1/a if (r, s) == (j, i)
                               else Q(r == s and r not in (i, j)) for s in range(3)) for r in range(3))
            assert rank([[swap[r][s]-int(r == s) for s in range(3)] for r in range(3)]) == 1
            factor_difference(swap)
            weighted_checks += 1

# The twelve-query word is the equality case of the lower bound.
i12 = identity(12)
word = []
query_outers = []
for role in range(4):
    n = outer(tuple(int(i == role) for i in range(4)), tuple(int(i == role) for i in range(4)))
    for address in range(3):
        g = tuple(tuple(Q((-1 if i == address else 1)*int(i == j)) for j in range(3)) for i in range(3))
        d = tensor(n, difference(representation(g)))
        word.append(tuple(tuple(x ^ int(i == j) for j, x in enumerate(row)) for i, row in enumerate(d)))
        u = tuple(2*int(i == 3*role+address) for i in range(12))
        v = tuple(int(i == 3*role+address) for i in range(12))
        assert outer(u, v) == d
        query_outers.append((u, v))
p = i12
for h in word:
    p = ring_matrix_product(h, p)
assert p == tuple(tuple(3*int(i == j) for j in range(12)) for i in range(12))

# A literal telescoping factorization reaches equality in the binary ranks.
suffix = i12
lefts = [None]*12
for j in reversed(range(12)):
    u, v = query_outers[j]
    lefts[j] = tuple(xor_sum(ring_product(suffix[i][k], u[k])
                            for k in range(12)) for i in range(12))
    suffix = ring_matrix_product(suffix, word[j])
assert suffix == p
b = tuple(tuple(lefts[j][i] for j in range(12)) for i in range(12))
c = tuple(v for u, v in query_outers)
assert ring_matrix_product(b, c) == difference(p)
b0 = tuple(tuple(x & 1 for x in row) for row in b)
c0 = tuple(tuple(x & 1 for x in row) for row in c)
assert binary_rank(b0) == 0 and binary_rank(c0) == 12
assert ring_matrix_product(b0, c0) == tuple((0,)*12 for _ in range(12))

# Omitting any query changes the complete target.
for omitted in range(12):
    q = i12
    for j, h in enumerate(word):
        if j != omitted:
            q = ring_matrix_product(h, q)
    assert q != p

result = dict(status='PASS_EXACT_DUAL_NUMBER_REPRESENTATION',
              b3_maps=48, b3_group_products=homomorphism_checks,
              b3_rank_one_reflections=9, scalar_projectors=120,
              native_rank_one_factorizations=query_factorizations,
              rational_weighted_examples=weighted_checks,
              twelve_query_target=True, twelve_omission_controls=True,
              target_inner_rank=12, minimum_queries=12,
              minimum_negative_monomial_queries=12,
              nonmonomial_extension_negative_control=True,
              scope='Sharp finite native monomial-word obstruction. No integer-multiplication lower bound or kappa gain.',
              script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              proof_sha256=hashlib.sha256((HERE/'PROOF.md').read_bytes()).hexdigest())
(HERE/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
