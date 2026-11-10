"""Literal binary algebras, independent of the order formulas.

Produced by Nick Petalas. Apache-2.0.
"""

from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field_mul(a, b, degree, modulus):
    value = 0
    for _ in range(degree):
        if b & 1:
            value ^= a
        a <<= 1
        if a >> degree:
            a ^= modulus
        b >>= 1
    return value


def apply(columns, value):
    result = 0
    for i, column in enumerate(columns):
        if value >> i & 1:
            result ^= column
    return result


def rank(columns):
    pivots = {}
    for value in columns:
        for _ in range(len(columns)):
            if value == 0:
                break
            pivot = value.bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = value
                break
            value ^= pivots[pivot]
        else:
            raise ValueError("rank iteration bound")
    return len(pivots)


class Ring:
    def __init__(self, degree, modulus, heights):
        require(1 <= degree <= 6 and len(heights) <= 3, "oracle field domain")
        require(all(1 <= h <= 3 for h in heights), "oracle height domain")
        self.degree = degree
        self.modulus = modulus
        self.bounds = tuple(2**h for h in heights)
        self.monomials = tuple(product(*(range(b) for b in self.bounds)))
        self.dimension = degree*len(self.monomials)
        require(self.dimension <= 16, "oracle dimension")
        self.size = 1 << self.dimension
        self.table = self.basis_products()

    def basis_products(self):
        indices = {a: i for i, a in enumerate(self.monomials)}
        table = []
        for i in range(self.dimension):
            row = []
            for j in range(self.dimension):
                a, b = self.monomials[i//self.degree], self.monomials[j//self.degree]
                exponent = tuple(x+y for x, y in zip(a, b, strict=True))
                if any(x >= bound for x, bound in zip(exponent, self.bounds, strict=True)):
                    row.append(0)
                else:
                    scalar = field_mul(1 << (i % self.degree), 1 << (j % self.degree),
                                       self.degree, self.modulus)
                    row.append(scalar << (self.degree*indices[exponent]))
            table.append(tuple(row))
        return tuple(table)

    def mul(self, a, b):
        result = 0
        for i in range(self.dimension):
            if a >> i & 1:
                result ^= apply(self.table[i], b)
        return result

    def power(self, a, exponent):
        require(0 <= exponent <= 64, "oracle power")
        result = 1
        for bit in range(exponent.bit_length()):
            if exponent >> bit & 1:
                result = self.mul(result, a)
            a = self.mul(a, a)
        return result


class Pair:
    def __init__(self, left, right):
        self.left, self.right = left, right
        self.dimension = left.dimension + right.dimension
        require(self.dimension <= 16, "pair dimension")

    def mul(self, a, b):
        cut = self.left.dimension
        mask = (1 << cut)-1
        return (self.left.mul(a & mask, b & mask)
                | (self.right.mul(a >> cut, b >> cut) << cut))


def validate_map(ring, columns, fixed_scalars=()):
    n = ring.dimension
    require(len(columns) == n and all(0 <= c < 1 << n for c in columns), "map shape")
    require(rank(columns) == n, "singular map")
    for scalar in fixed_scalars:
        require(apply(columns, scalar) == scalar, "base field moved")
    for i, j in product(range(n), repeat=2):
        require(apply(columns, ring.mul(1 << i, 1 << j))
                == ring.mul(columns[i], columns[j]), "multiplication changed")
    return n*n


def polynomial(ring, coefficients, value):
    result = 0
    for c in reversed(coefficients):
        result = ring.mul(result, value) ^ c
    return result


def coefficient_charts(ring, base, generator, degree):
    charts = {}
    for coefficients in product(base, repeat=degree):
        value = polynomial(ring, coefficients, generator)
        require(value not in charts, "dependent coefficient chart")
        charts[value] = coefficients
    require(set(charts) == set(range(1 << ring.degree)), "incomplete coefficient chart")
    return charts


def substitution(ring, coefficient_images, variables):
    monomials = []
    for exponents in ring.monomials:
        value = 1
        for y, exponent in zip(variables, exponents, strict=True):
            value = ring.mul(value, ring.power(y, exponent))
        monomials.append(value)
    return tuple(ring.mul(coefficient_images[1 << c], y)
                 for y in monomials for c in range(ring.degree))


def enumerate_local(ring, base, generator, relation, residue_degree):
    charts = coefficient_charts(ring, base, generator, residue_degree)
    roots = tuple(x for x in range(ring.size) if polynomial(ring, relation, x) == 0)
    variables = (() if not ring.bounds else
                 tuple(y for y in range(ring.size) if ring.power(y, ring.bounds[0]) == 0))
    choices = ((),) if not ring.bounds else tuple((y,) for y in variables)
    accepted, checks, candidates = [], 0, 0
    for root, values in product(roots, choices):
        coefficients = {c: polynomial(ring, chart, root) for c, chart in charts.items()}
        columns = substitution(ring, coefficients, values)
        candidates += 1
        if rank(columns) == ring.dimension:
            checks += validate_map(ring, columns, base)
            accepted.append(columns)
    require(len(set(accepted)) == len(accepted), "duplicate substitution maps")
    return tuple(accepted), {"roots": len(roots), "candidates": candidates,
                             "automorphisms": len(accepted), "basis_products": checks}


def enumerate_pair(left, right, left_maps, right_maps, exchange):
    ring = Pair(left, right)
    require(not exchange or left.table == right.table, "incompatible exchange")
    accepted, checks = set(), 0
    for a, b, swap in product(left_maps, right_maps, range(2 if exchange else 1)):
        columns = tuple(a) + tuple(c << left.dimension for c in b)
        if swap:
            columns = tuple(c << left.dimension for c in b) + tuple(a)
        require(columns not in accepted, "duplicate product map")
        checks += validate_map(ring, columns)
        accepted.add(columns)
    return ring, {"automorphisms": len(accepted), "basis_products": checks}


def mixed_histogram(ring, heights, samples_per_row=3):
    require(1 <= samples_per_row <= 3, "sample limit")
    tangent = tuple(ring.monomials.index(tuple(int(i == j) for i in range(len(heights))))
                    for j in range(len(heights)))
    histograms, samples = [], []
    for h in heights:
        powers = tuple(ring.power(1 << i, 2**h) for i in range(ring.dimension))
        histogram, representatives = {}, {}
        for value in range(ring.size):
            if apply(powers, value) == 0:
                row = sum(((value >> i) & 1) << j for j, i in enumerate(tangent))
                histogram[row] = histogram.get(row, 0)+1
                representatives.setdefault(row, [])
                if len(representatives[row]) < samples_per_row:
                    representatives[row].append(value)
        for value in range(0, ring.size, 1 if ring.size <= 256 else 257):
            require(apply(powers, value) == ring.power(value, 2**h), "Frobenius oracle mismatch")
        histograms.append(histogram)
        samples.append(representatives)
    count, checks, witnesses = 0, 0, 0
    for rows in product(*(tuple(h) for h in histograms)):
        if rank(rows) != len(heights):
            continue
        weight = 1
        for histogram, row in zip(histograms, rows, strict=True):
            weight *= histogram[row]
        count += weight
        for values in product(*(s[row] for s, row in zip(samples, rows, strict=True))):
            columns = substitution(ring, {1: 1}, values)
            checks += validate_map(ring, columns)
            witnesses += 1
    return {"automorphisms_factorized": count, "histograms": histograms,
            "direct_witnesses": witnesses, "basis_products": checks,
            "elements_per_generator": ring.size}


def odd_mul(a, b):
    return tuple(sum(a[i]*b[k-i] for i in range(k+1)) % 3 for k in range(3))


def odd_count():
    count, candidates = 0, 0
    for y in product(range(3), repeat=3):
        square = odd_mul(y, y)
        if odd_mul(square, y) != (0, 0, 0):
            continue
        candidates += 1
        columns = ((1, 0, 0), y, square)
        # The explicit 3-by-3 determinant expansion with first column (1,0,0).
        determinant = (columns[1][1]*columns[2][2] - columns[1][2]*columns[2][1]) % 3
        count += determinant != 0
    return {"elements": 27, "candidates": candidates, "automorphisms": count}
