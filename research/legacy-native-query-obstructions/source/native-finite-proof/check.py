"""Check a dual-number representation of the rational G2 times A1 group."""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent

def rmul(a, b):
    return ((a & 1)*(b & 1)) | ((((a & 1)*((b >> 1) & 1)) ^
                                (((a >> 1) & 1)*(b & 1))) << 1)

def xsum(items):
    out = 0
    for x in items:
        out ^= x
    return out

def eye(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))

def matmul(a, b, ring=False):
    return tuple(tuple(xsum(rmul(a[i][k], b[k][j]) for k in range(len(b))) if ring
                       else sum(a[i][k]*b[k][j] for k in range(len(b)))
                       for j in range(len(b[0]))) for i in range(len(a)))

def power(a, n, ring=False):
    out = eye(len(a))
    for _ in range(n):
        out = matmul(a, out, ring)
    return out

def block(a, t):
    return (tuple(a[0])+(0,), tuple(a[1])+(0,), (0, 0, t))

def rank(a):
    a = [list(map(Q, row)) for row in a]
    r = 0
    for j in range(len(a[0])):
        p = next((i for i in range(r, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[r], a[p] = a[p], a[r]
        pivot = a[r][j]
        a[r] = [x/pivot for x in a[r]]
        for i in range(len(a)):
            if i != r:
                t = a[i][j]
                a[i] = [x-t*y for x, y in zip(a[i], a[r])]
        r += 1
    return r

def difference(a):
    return tuple(tuple(x ^ int(i == j) for j, x in enumerate(row))
                 for i, row in enumerate(a))

def outer(a, b):
    return tuple(tuple(rmul(x, y) for y in b) for x in a)

def factor(d):
    pivot = next(((i, j) for i in range(3) for j in range(3) if d[i][j] & 1), None)
    if pivot:
        i, j = pivot
        u = tuple(d[r][j] for r in range(3))
        v = tuple(rmul(d[i][j], d[i][s]) for s in range(3))
    else:
        assert d == ((0, 0, 0), (0, 0, 0), (0, 0, 2))
        u, v = (0, 0, 2), (0, 0, 1)
    assert outer(u, v) == d
    return u, v

# Rational dihedral rotation and reflection.
a = ((Q(0), Q(-1)), (Q(1), Q(1)))
s = ((Q(0), Q(1)), (Q(1), Q(0)))
assert power(a, 3) == ((-1, 0), (0, -1))
assert power(a, 6) == eye(2)
assert matmul(matmul(s, a), s) == power(a, 5)
# A finite rational common Gram matrix is a separate exact check.
gram = ((Q(2), Q(1)), (Q(1), Q(2)))
for g in (a, s):
    gt = tuple(zip(*g))
    assert matmul(matmul(gt, gram), g) == gram

# Map a to (1+e) times its order-three binary reduction and s to its
# binary permutation matrix. The independent axis sign maps to 1+e.
ar = ((0, 3), (3, 3))
sr = ((0, 1), (1, 0))
assert power(ar, 3, True) == ((3, 0), (0, 3))
assert power(ar, 6, True) == eye(2)
assert matmul(matmul(sr, ar, True), sr, True) == power(ar, 5, True)

maps = {}
for k, reflected, axis in product(range(6), range(2), range(2)):
    g2 = matmul(power(a, k), s if reflected else eye(2))
    r2 = matmul(power(ar, k, True), sr if reflected else eye(2), True)
    g = block(g2, -1 if axis else 1)
    r = block(r2, 3 if axis else 1)
    assert g not in maps
    maps[g] = r
assert len(maps) == 24
homomorphism_checks = 0
for g, rg in maps.items():
    for h, rh in maps.items():
        gh = matmul(g, h)
        assert gh in maps and maps[gh] == matmul(rg, rh, True)
        homomorphism_checks += 1
z = tuple(tuple(-int(i == j) for j in range(3)) for i in range(3))
assert maps[z] == tuple(tuple(3*int(i == j) for j in range(3)) for i in range(3))
reflections = [g for g in maps if rank([[g[i][j]-int(i == j) for j in range(3)] for i in range(3)]) == 1]
assert len(reflections) == 7
projectors = [(tuple((u >> i) & 1 for i in range(4)), tuple((v >> i) & 1 for i in range(4)))
              for u in range(1, 16) for v in range(1, 16) if (u & v).bit_count() % 2]
assert len(projectors) == 120
factored = 0
for g in reflections:
    d = difference(maps[g])
    u, v = factor(d)
    assert matmul(g, g) == eye(3)
    for x, y in projectors:
        n = outer(x, y)
        assert matmul(n, n, True) == n
        left = tuple(rmul(i, j) for i in x for j in u)
        right = tuple(rmul(i, j) for i in y for j in v)
        expected = tuple(tuple(rmul(n[i//3][j//3], d[i % 3][j % 3])
                               for j in range(12)) for i in range(12))
        assert outer(left, right) == expected
        factored += 1

# Some reflections are genuinely nonmonomial in the rational coordinates.
nonmonomial = [g for g in reflections if any(sum(x != 0 for x in row) > 1 for row in g)]
assert nonmonomial
assert all(maps[g] != eye(3) for g in reflections)

result = dict(status='PASS_EXACT_G2_A1_DUAL_NUMBER_REPRESENTATION',
              rational_group_order=24, complete_products=homomorphism_checks,
              rational_rank_one_reflections=7,
              nonmonomial_reflections=len(nonmonomial),
              scalar_projectors=120, native_outer_factorizations=factored,
              central_minus_identity_image='(1+e) I3',
              proven_query_bound='3r for r productive roles',
              scope='Finite rational three-dimensional reflection groups only. No infinite-group obstruction or kappa gain.',
              script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
(HERE/'RESULT.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
