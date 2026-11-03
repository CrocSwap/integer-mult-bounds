"""Cyclic summands by quotient-annihilator saturation. See PROOF.md."""

from linear import combine, eye, matrix_combination, mm, mv
from linear import nullspace, prime, solve, span, transpose, vector


class Algebra:
    def __init__(self, p, table, unit):
        prime(p)
        n = len(table)
        if not 1 <= n <= 8 or any(len(row) != n for row in table):
            raise ValueError("algebra dimension must be in 1..8")
        vector(unit, n, p)
        for row in table:
            for v in row:
                vector(v, n, p)
        self.p, self.n = p, n
        self.table = tuple(tuple(tuple(v) for v in row) for row in table)
        self.unit = tuple(unit)
        self.left = tuple(transpose(row) for row in table)
        if matrix_combination(unit, self.left, p) != eye(n):
            raise ValueError("incorrect algebra unit")
        for i in range(n):
            for j in range(n):
                if table[i][j] != table[j][i]:
                    raise ValueError("noncommutative algebra")
                if mm(self.left[i], self.left[j], p) != matrix_combination(
                        table[i][j], self.left, p):
                    raise ValueError("nonassociative algebra")

    def product(self, x, y):
        assert len(x) == len(y) == self.n
        return mv(matrix_combination(x, self.left, self.p), y, self.p)


class Module:
    def __init__(self, algebra, actions):
        a, p = algebra, algebra.p
        d = len(actions[0]) if actions else 0
        if len(actions) != a.n or not 1 <= d <= 8:
            raise ValueError("module dimension must be in 1..8")
        for matrix in actions:
            if len(matrix) != d:
                raise ValueError("nonsquare module action")
            for row in matrix:
                vector(row, d, p)
        if matrix_combination(a.unit, actions, p) != eye(d):
            raise ValueError("nonunital module")
        for i in range(a.n):
            for j in range(a.n):
                if mm(actions[i], actions[j], p) != matrix_combination(
                        a.table[i][j], actions, p):
                    raise ValueError("incorrect module action")
        self.algebra, self.d = a, d
        self.actions = tuple(tuple(tuple(row) for row in m) for m in actions)

    def act(self, c, v):
        return mv(matrix_combination(c, self.actions, self.algebra.p), v,
                  self.algebra.p)

    def orbit(self, v):
        return transpose([mv(m, v, self.algebra.p) for m in self.actions])


def quotient_annihilator(module, v):
    """Ann_A(M/Av), not Ann_A(v)."""
    a, d = module.algebra, module.d
    functionals = nullspace(transpose(module.orbit(v)), a.p, d)
    equations = []
    for f in functionals:
        for j in range(d):
            equations.append([sum(f[k] * m[k][j] for k in range(d)) % a.p
                              for m in module.actions])
    return nullspace(equations, a.p, a.n)


def saturated_ideal(algebra, ideal):
    a = algebra
    current = span(ideal, a.p, a.n)
    for _ in range(a.n - 1):
        following = span([a.product(x, y) for x in current for y in ideal],
                         a.p, a.n)
        if following == current:
            break
        current = following
    return current


def ideal_identity(algebra, ideal):
    a = algebra
    if not ideal:
        return [0] * a.n
    equations, rhs = [], []
    for v in ideal:
        products = [a.product(w, v) for w in ideal]
        equations.extend(transpose(products))
        rhs.extend(v)
    coefficients = solve(equations, rhs, a.p, len(ideal))
    if coefficients is None:
        raise ArithmeticError("saturated ideal has no identity")
    e = combine(coefficients, ideal, a.n, a.p)
    if a.product(e, e) != e or any(a.product(e, v) != v for v in ideal):
        raise ArithmeticError("invalid saturated identity")
    return e


def cyclic_part(module):
    """Return generator, maximal cyclic idempotent, and orbit-rank trace."""
    a, d = module.algebra, module.d
    e, v, trace = [0] * a.n, [0] * d, []
    for w in eye(d):
        complement = [(x - y) % a.p for x, y in zip(a.unit, e)]
        z = [(x + y) % a.p for x, y in zip(v, module.act(complement, w))]
        ideal = saturated_ideal(a, quotient_annihilator(module, z))
        following = ideal_identity(a, ideal)
        if a.product(e, following) != e:
            raise ArithmeticError("cyclic summand decreased")
        e, v = following, module.act(following, z)
        trace.append(len(span(transpose(module.orbit(v)), a.p, d)))
        if e == list(a.unit):
            break
    if not check_part(module, v, e):
        raise ArithmeticError("invalid cyclic summand certificate")
    return v, e, trace


def check_part(module, v, e):
    """Check generation of eM; maximality is supplied by the written proof."""
    a, d = module.algebra, module.d
    vector(v, d, a.p)
    vector(e, a.n, a.p)
    image = transpose(matrix_combination(e, module.actions, a.p))
    return (a.product(e, e) == e and module.act(e, v) == v
            and span(transpose(module.orbit(v)), a.p, d) == span(image, a.p, d))
