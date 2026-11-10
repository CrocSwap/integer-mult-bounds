"""Integral norm-six relation pivot and target numerators over 64.

Produced by Nick Petalas. Apache-2.0.
The kernel and integer-valued feature convention are credited in README.md.
"""

from dataclasses import dataclass
from itertools import combinations

COORDINATE_LIMIT = 1 << 20
DENOMINATOR = 64


def require(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Plan:
    gram: tuple
    roots: tuple
    parents: tuple


def make_plan(gram):
    """Validate the fixed-size integer boundary and choose direct unit edges."""
    require(len(gram) == 48, 'expected 48 Gram rows')
    require(all(len(row) == 48 for row in gram), 'expected 48 columns')
    require(all(type(a) is int and abs(a) <= 10 for row in gram for a in row),
            'Gram entries must be bounded integers')
    g = tuple(tuple(row) for row in gram)
    require(all(g[i][j] == g[j][i] for i in range(48) for j in range(48)),
            'Gram must be symmetric')
    require(all(g[i][i] > 0 and g[i][i] % 2 == 0 for i in range(48)),
            'Gram diagonal must be positive and even')
    roots = tuple(i for i in range(48) if g[i][i] == 8)
    require(bool(roots), 'missing diagonal-eight root')
    parents = []
    for i in range(48):
        candidates = tuple(r for r in roots if abs(g[i][r]) == 1)
        require(i in roots or bool(candidates), 'missing direct unit edge')
        parents.append(-1 if i in roots else candidates[0])
    return Plan(g, roots, tuple(parents))


def integer_vector(values):
    require(len(values) == 48, 'expected 48 coordinates')
    require(all(type(a) is int and abs(a) <= COORDINATE_LIMIT for a in values),
            'coordinates must be integers of magnitude at most 2^20')
    return tuple(values)


def keys():
    for kind in ('f', 'l'):
        for i in range(48):
            yield (kind, i)
    for i in range(48):
        for j in range(48):
            if i != j:
                yield ('s', i, j)
    for i, j, k in combinations(range(48), 3):
        yield ('t', i, j, k)


def pivot_keys(plan):
    return (tuple(('l', r) for r in plan.roots)
            + tuple(('s', i, p) for i, p in enumerate(plan.parents) if p >= 0))


def relation_column(plan, key):
    """Nonzero candidates of one credited shell-relation column."""
    g = plan.gram
    kind, i, *rest = key
    h = g[i][i] // 2
    if kind == 'f':
        return ((i, 3*h),)
    if kind == 'l':
        return ((i, h-3),)
    j = rest[0]
    if kind == 's':
        return ((i, g[i][j]), (j, h))
    k = rest[1]
    return ((i, g[j][k]), (j, g[i][k]), (k, g[i][j]))


def raw_pair(key, x, v):
    kind, i, *rest = key
    if kind == 'f':
        return ((x[i]**3-x[i])//3, v[i]**3)
    if kind == 'l':
        return (x[i], (v[i]**3-4*v[i])//3)
    j = rest[0]
    if kind == 's':
        return (x[i]**2*x[j], v[i]**2*v[j])
    k = rest[1]
    return (x[i]*x[j]*x[k], 2*v[i]*v[j]*v[k])


def multipliers(plan, v):
    """Solve R_P^T lambda = psi_P using the unit-edge block matrix."""
    lam = [0]*48
    for r in plan.roots:
        lam[r] = (v[r]**3-4*v[r])//3
    for i, p in enumerate(plan.parents):
        if p >= 0:
            h = plan.gram[i][i]//2
            lam[i] = plan.gram[i][p]*(v[i]**2*v[p]-h*lam[p])
    return tuple(lam)


def norm(plan, x):
    return sum(x[i]*plan.gram[i][j]*x[j] for i in range(48) for j in range(48))


def coefficient_records(plan, x, v):
    """Internal polynomial evaluator; its off-shell defect is in PROOF.md."""
    lam = multipliers(plan, v)
    pivots = frozenset(pivot_keys(plan))
    for key in keys():
        if key in pivots:
            continue
        phi, psi = raw_pair(key, x, v)
        correction = sum(a*lam[i] for i, a in relation_column(plan, key))
        yield key, phi, psi-correction


def records(plan, source, target):
    """Yield 19,600 (key, integral source, integral numerator) records.

    Their sum divided by 64 is the kernel for a norm-six source. The target
    need not lie on the shell. Inputs are snapshotted as bounded tuples.
    """
    x, y = integer_vector(source), integer_vector(target)
    require(norm(plan, x) == 6, 'source must have norm six')
    v = tuple(sum(plan.gram[i][j]*y[j] for j in range(48)) for i in range(48))
    yield from coefficient_records(plan, x, v)
