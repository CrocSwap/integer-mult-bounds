#!/usr/bin/env python3
"""Exact circuit traces by constrained quadratic Gauss sums.

No Clifford tableau, distinguished input column, floating point, or dense
operator matrix is used. See PROOF.md. Apache-2.0.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations


def require(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError(reason)


def bits(mask: int) -> list[int]:
    out = []
    while mask:
        low = mask & -mask
        out.append(low.bit_length() - 1)
        mask ^= low
    return out


def gaussian_mul(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    x, y = a
    z, w = b
    return x*z-y*w, x*w+y*z


def unit(power: int) -> tuple[int, int]:
    return ((1, 0), (0, 1), (-1, 0), (0, -1))[power % 4]


@dataclass
class Quadratic:
    """c + sum a_i x_i + 2 sum_(i<j) b_ij x_i x_j modulo four."""
    linear: list[int]
    pairs: set[tuple[int, int]]
    constant: int = 0

    @classmethod
    def zero(cls, n: int) -> Quadratic:
        require(type(n) is int and n >= 0, 'quadratic variable count')
        return cls([0]*n, set())

    def copy(self) -> Quadratic:
        return Quadratic(self.linear[:], self.pairs.copy(), self.constant)

    def toggle(self, i: int, j: int) -> None:
        require(0 <= i < len(self.linear) and 0 <= j < len(self.linear), 'quadratic index')
        if i == j:
            self.linear[i] = (self.linear[i]+2) % 4
            return
        pair = (min(i, j), max(i, j))
        if pair in self.pairs:
            self.pairs.remove(pair)
        else:
            self.pairs.add(pair)

    def add_affine(self, coefficient: int, form: tuple[int, int]) -> None:
        """Add coefficient times a Boolean affine parity, modulo four."""
        mask, constant = form
        require(mask >= 0 and mask >> len(self.linear) == 0 and constant in (0, 1), 'affine form domain')
        coefficient %= 4
        if coefficient == 0:
            return
        support = bits(mask)
        self.constant = (self.constant+coefficient*constant) % 4
        signed = coefficient*(1-2*constant)
        for i in support:
            self.linear[i] = (self.linear[i]+signed) % 4
        if coefficient % 2:
            for i, j in combinations(support, 2):
                self.toggle(i, j)

    def add_product(self, a: tuple[int, int], b: tuple[int, int]) -> None:
        """Add twice the product of two Boolean affine forms, modulo four."""
        x, c = a
        y, d = b
        require(x >= 0 and y >= 0 and (x | y) >> len(self.linear) == 0 and c in (0, 1) and d in (0, 1),
                'quadratic product domain')
        self.constant = (self.constant+2*c*d) % 4
        for i in bits((y if c else 0) ^ (x if d else 0)):
            self.linear[i] = (self.linear[i]+2) % 4
        for i in bits(x):
            for j in bits(y):
                self.toggle(i, j)

    def substitute(self, forms: list[tuple[int, int]], n: int) -> Quadratic:
        require(len(forms) == len(self.linear), 'complete substitution')
        out = Quadratic.zero(n)
        out.constant = self.constant
        for coefficient, form in zip(self.linear, forms, strict=True):
            out.add_affine(coefficient, form)
        for i, j in sorted(self.pairs):
            out.add_product(forms[i], forms[j])
        return out

    def value(self, x: int) -> int:
        require(type(x) is int and 0 <= x < 1 << len(self.linear), 'quadratic assignment')
        return (self.constant+sum(a for i, a in enumerate(self.linear) if x >> i & 1)
                +2*sum((x >> i & 1)*(x >> j & 1) for i, j in self.pairs)) % 4


def gauss_sum(poly: Quadratic) -> tuple[int, int]:
    """Return sum_x i^poly(x) exactly using one- and two-variable pivots."""
    q = poly.copy()
    active = set(range(len(q.linear)))
    factor = (1, 0)
    while active:
        odd = next((i for i in sorted(active) if q.linear[i] % 2), None)
        if odd is not None:
            a = q.linear[odd]
            neighbours = 0
            retained = set()
            for i, j in q.pairs:
                if odd == i:
                    neighbours ^= 1 << j
                elif odd == j:
                    neighbours ^= 1 << i
                else:
                    retained.add((i, j))
            q.pairs = retained
            q.linear[odd] = 0
            active.remove(odd)
            z = unit(a)
            factor = gaussian_mul(factor, (1+z[0], z[1]))
            q.add_affine(-a, (neighbours, 0))
            continue
        if q.pairs:
            i, j = min(q.pairs)
            require(i in active and j in active, 'elimination support invariant')
            u = v = 0
            retained = set()
            for a, b in q.pairs:
                if (a, b) == (i, j):
                    continue
                if i == a:
                    u ^= 1 << b
                elif i == b:
                    u ^= 1 << a
                elif j == a:
                    v ^= 1 << b
                elif j == b:
                    v ^= 1 << a
                else:
                    retained.add((a, b))
            require((u | v) & ((1 << i) | (1 << j)) == 0, 'two-pivot complement')
            ci, cj = q.linear[i]//2, q.linear[j]//2
            q.pairs = retained
            q.linear[i] = q.linear[j] = 0
            active.remove(i)
            active.remove(j)
            q.add_product((u, ci), (v, cj))
            factor = (2*factor[0], 2*factor[1])
            continue
        if any(q.linear[i] == 2 for i in active):
            return 0, 0
        require(all(q.linear[i] == 0 for i in active), 'isolated even phases')
        size = 1 << len(active)
        factor = factor[0]*size, factor[1]*size
        active.clear()
    require(not q.pairs and not any(q.linear), 'complete quadratic elimination')
    return gaussian_mul(factor, unit(q.constant))


def affine_solution(n: int, equations: list[tuple[int, int]]) -> tuple[list[tuple[int, int]], int] | None:
    """RREF parametrization of every solution, with each free assignment once."""
    rows = [[mask, rhs] for mask, rhs in equations]
    require(all(mask >= 0 and mask >> n == 0 and rhs in (0, 1) for mask, rhs in rows), 'linear equation domain')
    pivots = []
    k = 0
    for j in range(n):
        at = next((i for i in range(k, len(rows)) if rows[i][0] >> j & 1), None)
        if at is None:
            continue
        rows[k], rows[at] = rows[at], rows[k]
        for i in range(len(rows)):
            if i != k and rows[i][0] >> j & 1:
                rows[i][0] ^= rows[k][0]
                rows[i][1] ^= rows[k][1]
        pivots.append(j)
        k += 1
    if any(mask == 0 and rhs for mask, rhs in rows):
        return None
    free = [j for j in range(n) if j not in set(pivots)]
    positions = {j: i for i, j in enumerate(free)}
    forms = [(0, 0)]*n
    for j, i in positions.items():
        forms[j] = (1 << i, 0)
    for pivot, (mask, rhs) in zip(pivots, rows, strict=False):
        require(mask & sum(1 << j for j in pivots) == 1 << pivot, 'RREF pivot isolation')
        forms[pivot] = (sum(1 << positions[j] for j in free if mask >> j & 1), rhs)
    return forms, len(free)


def binary_inverse(rows: tuple[int, ...]) -> tuple[int, ...]:
    n = len(rows)
    require(n > 0 and all(type(row) is int and 0 <= row < 1 << n for row in rows), 'binary matrix domain')
    augmented = [row | (1 << (n+i)) for i, row in enumerate(rows)]
    for j in range(n):
        k = next((i for i in range(j, n) if augmented[i] >> j & 1), None)
        require(k is not None, 'singular address matrix')
        augmented[j], augmented[k] = augmented[k], augmented[j]
        for i in range(n):
            if i != j and augmented[i] >> j & 1:
                augmented[i] ^= augmented[j]
    require([row & ((1 << n)-1) for row in augmented] == [1 << i for i in range(n)], 'binary inverse endpoint')
    return tuple(row >> n for row in augmented)


def adjoint(circuit: tuple[tuple, ...]) -> tuple[tuple, ...]:
    out = []
    for gate in reversed(circuit):
        kind = gate[0]
        if kind == 'P':
            out.append(('P', binary_inverse(tuple(gate[1]))))
        elif kind == 'D':
            out.append(('D', tuple(gate[1]), tuple(-a % 4 for a in gate[2])))
        elif kind == 'C':
            out.append(('C', gate[1], -gate[2]))
        elif kind == 'phase':
            out.append(('phase', -gate[1] % 4))
        else:
            require(kind == 'X', 'adjoint gate vocabulary')
            out.append(gate)
    return tuple(out)


def circuit_trace(n: int, circuit: tuple[tuple, ...]) -> tuple[int, int, int]:
    """Trace numerator real/imaginary and power-of-two denominator.

    All accepted gates are unitary by their checked syntax and invertible
    address maps. The trace construction works at arbitrary n.
    """
    require(type(n) is int and n > 0, 'positive circuit dimension')
    addresses = [(1 << i, 0) for i in range(n)]
    q = Quadratic.zero(n)
    factor = (1, 0)
    denominator = 0
    for gate in circuit:
        kind = gate[0]
        if kind == 'P':
            require(len(gate) == 2 and len(gate[1]) == n, 'permutation arity')
            rows = tuple(gate[1])
            binary_inverse(rows)
            following = []
            for row in rows:
                mask = constant = 0
                for j in bits(row):
                    mask ^= addresses[j][0]
                    constant ^= addresses[j][1]
                following.append((mask, constant))
            addresses = following
        elif kind == 'X':
            require(len(gate) == 2 and type(gate[1]) is int and 0 <= gate[1] < 1 << n, 'translation domain')
            addresses = [(mask, constant ^ (gate[1] >> i & 1)) for i, (mask, constant) in enumerate(addresses)]
        elif kind == 'phase':
            require(len(gate) == 2 and type(gate[1]) is int and 0 <= gate[1] < 4, 'phase domain')
            q.constant = (q.constant+gate[1]) % 4
        elif kind == 'D':
            require(len(gate) == 3 and len(gate[1]) == len(gate[2]) == n, 'diagonal arity')
            rows, linear = gate[1:]
            require(all(type(row) is int and 0 <= row < 1 << n for row in rows), 'quadratic matrix domain')
            require(all(type(a) is int and 0 <= a < 4 for a in linear), 'quadratic linear phase domain')
            require(all((rows[i] >> j & 1) == (rows[j] >> i & 1) for i in range(n) for j in range(n)),
                    'symmetric source quadratic')
            require(all((linear[i] & 1) == (rows[i] >> i & 1) for i in range(n)), 'source diagonal parity')
            for coefficient, form in zip(linear, addresses, strict=True):
                q.add_affine(coefficient, form)
            for i in range(n):
                for j in range(i+1, n):
                    if rows[i] >> j & 1:
                        q.add_product(addresses[i], addresses[j])
        else:
            require(kind == 'C' and len(gate) == 3 and type(gate[1]) is int and 0 < gate[1] < 1 << n
                    and type(gate[2]) is int and gate[2] in (-1, 1), 'Gaussian gate domain')
            direction, sign = gate[1:]
            variable = 1 << len(q.linear)
            q.linear.append(-sign % 4)
            addresses = [(mask ^ (variable if direction >> i & 1 else 0), constant)
                         for i, (mask, constant) in enumerate(addresses)]
            factor = gaussian_mul(factor, (1, sign))
            denominator += 1
    constraints = [(mask ^ (1 << i), constant) for i, (mask, constant) in enumerate(addresses)]
    solved = affine_solution(len(q.linear), constraints)
    if solved is None:
        return 0, 0, 0
    forms, free = solved
    result = gaussian_mul(factor, gauss_sum(q.substitute(forms, free)))
    real, imag = result
    while denominator and real % 2 == 0 and imag % 2 == 0:
        real //= 2
        imag //= 2
        denominator -= 1
    return real, imag, denominator


def validate(n: int, circuit: tuple[tuple, ...]) -> None:
    """Validate original syntax before an adjoint can normalize any field."""
    require(type(n) is int and n > 0, 'positive circuit dimension')
    for gate in circuit:
        require(type(gate) in (tuple, list) and len(gate) > 0, 'gate record')
        kind = gate[0]
        if kind == 'P':
            require(len(gate) == 2 and len(gate[1]) == n, 'permutation arity')
            binary_inverse(tuple(gate[1]))
        elif kind == 'X':
            require(len(gate) == 2 and type(gate[1]) is int and 0 <= gate[1] < 1 << n, 'translation domain')
        elif kind == 'phase':
            require(len(gate) == 2 and type(gate[1]) is int and 0 <= gate[1] < 4, 'phase domain')
        elif kind == 'C':
            require(len(gate) == 3 and type(gate[1]) is int and 0 < gate[1] < 1 << n
                    and type(gate[2]) is int and gate[2] in (-1, 1), 'Gaussian gate domain')
        else:
            require(kind == 'D' and len(gate) == 3 and len(gate[1]) == len(gate[2]) == n, 'diagonal arity')
            rows, linear = gate[1:]
            require(all(type(row) is int and 0 <= row < 1 << n for row in rows), 'quadratic matrix domain')
            require(all(type(a) is int and 0 <= a < 4 for a in linear), 'quadratic linear phase domain')
            require(all((rows[i] >> j & 1) == (rows[j] >> i & 1) for i in range(n) for j in range(n)),
                    'symmetric source quadratic')
            require(all((linear[i] & 1) == (rows[i] >> i & 1) for i in range(n)), 'source diagonal parity')


def equal(n: int, actual: tuple[tuple, ...], expected: tuple[tuple, ...], label: str) -> tuple[int, int, int]:
    validate(n, expected)
    trace = circuit_trace(n, actual+adjoint(expected))
    require(trace == (1 << n, 0, 0), label+': exact unitary overlap trace '+str(trace))
    return trace
