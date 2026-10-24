"""Explicit dyadic shell-feature elimination, not a physical decoder.

Krzysztof Wojt with substantial OpenAI Codex assistance. Apache-2.0.
The uncompressed integer-valued feature identity is Cinna Davis's PR2222.
"""

from itertools import combinations
from math import comb


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_gram(gram, a=0, b=4):
    d = len(gram)
    require(2 <= d <= 48, "dimension must be between 2 and 48")
    require(type(a) is int and type(b) is int and 0 <= a < b < d,
            "invalid pivot indices")
    require(all(len(row) == d for row in gram), "Gram must be square")
    require(all(type(value) is int for row in gram for value in row),
            "Gram entries must be integers")
    require(all(gram[i][j] == gram[j][i] for i in range(d) for j in range(d)),
            "Gram must be symmetric")
    require(all(gram[i][i] % 2 == 0 for i in range(d)), "Gram must be even")
    require((gram[a][a], gram[a][b], gram[b][b]) == (6, -1, 6),
            "required pivot block is [[6,-1],[-1,6]]")
    return d


def feature_keys(d):
    require(type(d) is int and 2 <= d <= 48, "invalid feature dimension")
    return ([('f', i) for i in range(d)] + [('l', i) for i in range(d)]
            + [('s', i, j) for i in range(d) for j in range(d) if i != j]
            + [('t', *triple) for triple in combinations(range(d), 3)])


def shell_relations(gram, a=0, b=4):
    """Rows R with R phi = x_i (x^T G x - 6)/2, in sparse form."""
    d = validate_gram(gram, a, b)
    features = feature_keys(d)
    positions = {key: j for j, key in enumerate(features)}
    rows = [dict() for _ in range(d)]

    def put(row, key, value):
        if value:
            rows[row][positions[key]] = value

    for i in range(d):
        put(i, ('f', i), 3 * (gram[i][i] // 2))
        put(i, ('l', i), gram[i][i] // 2 - 3)
        for j in range(d):
            if i != j:
                put(i, ('s', j, i), gram[j][j] // 2)
                put(i, ('s', i, j), gram[i][j])
        for j, k in combinations((j for j in range(d) if j != i), 2):
            put(i, ('t', *sorted((i, j, k))), gram[j][k])
    pivots = [positions[('s', a, b)], positions[('s', b, a)]]
    pivots += [positions[('t', *sorted((i, a, b)))]
               for i in range(d) if i not in (a, b)]
    return features, rows, pivots


def integer_vector(values, d, name):
    require(len(values) == d and all(type(v) is int for v in values),
            name + " must have exactly d integer coordinates")


def source_values(x, features):
    d = sum(key[0] == 'f' for key in features)
    integer_vector(x, d, "source")
    values = []
    for key in features:
        kind, *indices = key
        if kind == 'f':
            u = x[indices[0]]
            values.append((u**3 - u) // 3)
        elif kind == 'l':
            values.append(x[indices[0]])
        elif kind == 's':
            i, j = indices
            values.append(x[i] * x[i] * x[j])
        else:
            i, j, k = indices
            values.append(x[i] * x[j] * x[k])
    return values


def old_target(v, features):
    """Integral psi; phi dot psi = ((x dot v)^3 - 4 x dot v)/3."""
    d = sum(key[0] == 'f' for key in features)
    integer_vector(v, d, "dual target")
    values = []
    for key in features:
        kind, *indices = key
        if kind == 'f':
            values.append(v[indices[0]]**3)
        elif kind == 'l':
            u = v[indices[0]]
            values.append((u**3 - 4*u) // 3)
        elif kind == 's':
            i, j = indices
            values.append(v[i] * v[i] * v[j])
        else:
            i, j, k = indices
            values.append(2 * v[i] * v[j] * v[k])
    return values


def elimination_multipliers(gram, pivot_values, a=0, b=4):
    """mu=8 R_P^-T pivot_values, valid for arbitrary integral pivot targets."""
    d = validate_gram(gram, a, b)
    integer_vector(pivot_values, d, "pivot target")
    mu = [0]*d
    mu[a] = pivot_values[0] + 3*pivot_values[1]
    mu[b] = 3*pivot_values[0] + pivot_values[1]
    for position, i in enumerate((i for i in range(d) if i not in (a, b)), 2):
        mu[i] = gram[i][b]*mu[a] + gram[i][a]*mu[b] - 8*pivot_values[position]
    return mu


def compress_target(gram, v, a=0, b=4, prepared=None):
    """Integer numerators/512 and mu, with d eliminated positions zero.

    No shell is enumerated. Only source points must have norm six for the
    identity; v may be any integer vector. For the kernel set v=G*y.
    """
    d = validate_gram(gram, a, b)
    integer_vector(v, d, "dual target")
    features, rows, pivots = prepared or shell_relations(gram, a, b)
    old = old_target(v, features)
    mu = elimination_multipliers(gram, [old[j] for j in pivots], a, b)
    numerators = [8*value for value in old]
    for multiplier, row in zip(mu, rows):
        for j, coefficient in row.items():
            numerators[j] -= multiplier*coefficient
    require(all(numerators[j] == 0 for j in pivots), "pivot cancellation failed")
    return numerators, mu


def gram_times(gram, x):
    integer_vector(x, len(gram), "lattice target")
    return [sum(g*t for g, t in zip(row, x)) for row in gram]


def quadratic(gram, x):
    return sum(u*v for u, v in zip(x, gram_times(gram, x)))


def evaluation_budget(d):
    """Conservative integer-preprocessing counts, not native scalar tariffs."""
    require(type(d) is int and 2 <= d <= 48, "invalid budget dimension")
    n = comb(d+2, 3)
    return {
        'retained_features': n,
        'source_multiplications': d*(d-1) + 2*comb(d, 3) + 2,
        'source_subtractions': d,
        'source_exact_divisions_by_3': d,
        'target_multiplications_upper': d*d + 8*n + 7*d - 4,
        'target_additions_upper': d*d + 5*n + 3*d - 2,
        'target_exact_divisions_by_3': d,
        'target_common_denominator': 512,
    }
