"""Exact normal operator of the width-13 two-variable-site raw adjoint."""
from collections import Counter
from fractions import Fraction
from functools import cache
from itertools import product
from math import prod


@cache
def subspaces(n, dimension):
    """All binary subspaces, as sorted tuples of members."""
    spaces = {frozenset((0,))}
    for _ in range(dimension):
        spaces = {
            space | {u ^ v for u in space}
            for space in spaces for v in range(1, 1 << n) if v not in space
        }
    return tuple(sorted(tuple(sorted(space)) for space in spaces))


@cache
def isomorphisms(d):
    """Linear bijections in quotient coordinates, given by value tables."""
    tables = [(0,)]
    for _ in range(d):
        tables = [table + tuple(t ^ v for t in table)
                  for table in tables for v in range(1, 1 << d) if v not in table]
    return tuple(tables)


def quotient(n, kernel):
    """Linear map to coordinates of the quotient by kernel."""
    # Least coset representatives form a vector space (binary row reduction).
    reps = [min(x ^ u for u in kernel) for x in range(1 << n)]
    labels = {value: j for j, value in enumerate(sorted(set(reps)))}
    return tuple(labels[value] for value in reps)


def pair_types(n):
    q = 1 << n
    return {
        '00': ((0, 0), 1),
        'xx': ((1, 1), q - 1),
        '0x': ((0, 1), q - 1),
        'xy': ((1, 2), (q - 1) * (q - 2) // 2),
    }


def support_counts(n, j):
    """For each row/column multiset type, count graphs supporting each matching."""
    types = pair_types(n)
    blocks = list(product(types, repeat=2))
    counts = {block: [0, 0, 0] for block in blocks}
    lookups = [quotient(n, space) for space in subspaces(n, j)]
    graphs = 0
    for left in lookups:
        for right in lookups:
            for mapping in isomorphisms(n - j):
                graphs += 1
                # Only labels 0,1,2 occur in the chosen GL orbit representatives.
                image = [mapping[right[k]] for k in range(3)]
                for row, column in blocks:
                    (i, h), _ = types[row]
                    (k, l), _ = types[column]
                    direct = left[i] == image[k] and left[h] == image[l]
                    cross = left[i] == image[l] and left[h] == image[k]
                    tally = counts[row, column]
                    tally[0] += direct
                    tally[1] += cross
                    tally[2] += direct and cross
    return graphs, counts


def gaussian_binomial(n, k):
    return prod((1 << (n - i)) - 1 for i in range(k)) // prod(
        (1 << (k - i)) - 1 for i in range(k))


def normal_blocks(n=4, width=13, only_shell=None):
    """Block entries (a,b,c) of [[a,c],[c,b]], (a,) for one-dimensional blocks.

    Each is in the orthonormal symmetric monomial basis with unnormalized
    group counting, for the dictionary normalized as vec(V)/sqrt(2**n).
    """
    if n < 2 or width <= 2:
        raise ValueError("need n >= 2 and at least one frozen site")
    if only_shell is not None and not 0 <= only_shell <= n:
        raise ValueError("shell outside supported range")
    q = 1 << n
    symplectic_order = (1 << n**2) * prod((1 << (2 * i)) - 1 for i in range(1, n + 1))
    lagrangians = prod((1 << i) + 1 for i in range(1, n + 1))
    types = pair_types(n)
    blocks = {}
    for row, column in product(types, repeat=2):
        size = 3 if row in ('0x', 'xy') and column in ('0x', 'xy') else 1
        blocks[row, column] = [Fraction(0)] * size
    shells = range(n + 1) if only_shell is None else (only_shell,)
    for j in shells:
        graphs, counts = support_counts(n, j)
        multiplicity = gaussian_binomial(n, j) << (j * (j + 1) // 2)
        factor = Fraction(q * (symplectic_order // lagrangians) * multiplicity,
                          (q**width) * (1 << ((width - 1) * j)) * graphs)
        for key, block in blocks.items():
            row, column = key
            norm = 1 if row in ('00', 'xx') and column in ('00', 'xx') else 2
            first, other, both = counts[key]
            block[0] += norm * factor * first
            if len(block) > 1:
                block[1] += norm * factor * other
                if both:
                    block[2] -= norm * factor * Fraction(both, (1 << j) - 1)
    return {key: tuple(block) for key, block in blocks.items()}


def eigenpolynomials(n, blocks):
    """Exact rational eigenvalues or quadratic factors and multiplicities."""
    types = pair_types(n)
    factors = Counter()
    for (row, column), block in blocks.items():
        multiplicity = types[row][1] * types[column][1]
        if len(block) == 1:
            factors[(1, -block[0])] += multiplicity
            continue
        a, b, c = block
        if a == b:
            factors[(1, -a - c)] += multiplicity
            factors[(1, -a + c)] += multiplicity
        elif not c:
            factors[(1, -a)] += multiplicity
            factors[(1, -b)] += multiplicity
        else:
            factors[(1, -a - b, a * b - c * c)] += multiplicity
    return factors


if __name__ == '__main__':
    blocks = normal_blocks()
    for key, block in blocks.items():
        print(*key, *(str(entry) for entry in block))
    print('Characteristic factors of the symmetric sector (descending coefficients; multiplicity)')
    for poly, count in eigenpolynomials(4, blocks).items():
        print(' '.join(str(coefficient) for coefficient in poly), count)
