"""Exact finite-field tensor recognition. Ali Romman with OpenAI Codex. Apache-2.0."""
from itertools import product
from math import gcd, isqrt


class Field:
    """Use base-p digits and a monic polynomial, in constant-first order."""

    def __init__(self, p, modulus):
        if type(p) is not int or p < 2 or any(p % d == 0 for d in range(2, isqrt(p) + 1)):
            raise ValueError('p must be prime')
        if (not isinstance(modulus, (tuple, list)) or len(modulus) < 2
                or modulus[-1] != 1
                or any(type(c) is not int or not 0 <= c < p for c in modulus)):
            raise ValueError('modulus must be monic with canonical prime-field coefficients')
        self.p, self.e = p, len(modulus) - 1
        self.modulus = tuple(modulus)
        self.q = p ** self.e
        digits = [[(a // p ** i) % p for i in range(self.e)] for a in range(self.q)]
        self.add = [[sum(((x + y) % p) * p ** i for i, (x, y) in enumerate(zip(a, b)))
                     for b in digits] for a in digits]
        self.neg = [sum((-x % p) * p ** i for i, x in enumerate(a)) for a in digits]
        self.mul = []
        for a in digits:
            row = []
            for b in digits:
                c = [0] * (2 * self.e - 1)
                for i, x in enumerate(a):
                    for j, y in enumerate(b):
                        c[i + j] = (c[i + j] + x * y) % p
                for k in range(len(c) - 1, self.e - 1, -1):
                    for j in range(self.e):
                        c[k - self.e + j] = (c[k - self.e + j] - c[k] * modulus[j]) % p
                row.append(sum(c[i] * p ** i for i in range(self.e)))
            self.mul.append(row)
        self.inv = [0] + [self.power(a, self.q - 2) for a in range(1, self.q)]
        if any(self.mul[a][self.inv[a]] != 1 for a in range(1, self.q)):
            raise ValueError('modulus is reducible')

    def power(self, a, n):
        if n < 0:
            raise ValueError('negative exponent')
        r = 1
        while n:
            if n & 1:
                r = self.mul[r][a]
            a = self.mul[a][a]
            n //= 2
        return r

    def total(self, xs):
        r = 0
        for x in xs:
            r = self.add[r][x]
        return r


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def columns(xs, n):
    return [[v[i] for v in xs] for i in range(n)]


def column(a, j):
    return [r[j] for r in a]


def rref(a, width, f):
    rows = [r[:] for r in a]
    pivots = []
    k = 0
    for j in range(width):
        pivot = next((i for i in range(k, len(rows)) if rows[i][j]), None)
        if pivot is None:
            continue
        rows[k], rows[pivot] = rows[pivot], rows[k]
        rows[k] = [f.mul[f.inv[rows[k][j]]][x] for x in rows[k]]
        for i in range(len(rows)):
            if i != k and rows[i][j]:
                c = f.neg[rows[i][j]]
                rows[i] = [f.add[x][f.mul[c][y]] for x, y in zip(rows[i], rows[k])]
        pivots.append(j)
        k += 1
        if k == len(rows):
            break
    return rows, pivots


def rank(a, f):
    return len(rref(a, len(a[0]) if a else 0, f)[1])


def kernel(a, width, f):
    rows, pivots = rref(a, width, f)
    out = []
    for j in range(width):
        if j in pivots:
            continue
        v = [0] * width
        v[j] = 1
        for i, p in enumerate(pivots):
            v[p] = f.neg[rows[i][j]]
        out.append(v)
    return out


def inverse(a, f):
    n = len(a)
    rows, pivots = rref([r + e for r, e in zip(a, identity(n))], n, f)
    if len(pivots) != n:
        raise ValueError('singular matrix')
    return [r[n:] for r in rows]


def mv(a, v, f):
    return [f.total(f.mul[x][y] for x, y in zip(r, v)) for r in a]


def mm(a, b, f):
    return columns([mv(a, column(b, j), f) for j in range(len(b[0]))], len(a))


def determinant(a, f):
    rows = [r[:] for r in a]
    d = 1
    for j in range(len(rows)):
        k = next((i for i in range(j, len(rows)) if rows[i][j]), None)
        if k is None:
            return 0
        if k != j:
            rows[k], rows[j] = rows[j], rows[k]
            d = f.neg[d]
        c = rows[j][j]
        d = f.mul[d][c]
        for i in range(j + 1, len(rows)):
            z = f.neg[f.mul[rows[i][j]][f.inv[c]]]
            rows[i] = [f.add[x][f.mul[z][y]] for x, y in zip(rows[i], rows[j])]
    return d


def tensor_value(t, u, v, f):
    n = len(t)
    out = [0] * n
    for i, x in enumerate(u):
        if x:
            for j, y in enumerate(v):
                if y:
                    c = f.mul[x][y]
                    out = [f.add[z][f.mul[c][a]] for z, a in zip(out, t[i][j])]
    return out


def algebra_power(t, u, exponent, unit, f):
    r = unit[:]
    while exponent:
        if exponent & 1:
            r = tensor_value(t, r, u, f)
        u = tensor_value(t, u, u, f)
        exponent //= 2
    return r


def model(heights, f):
    bounds = [f.p ** h for h in heights]
    exponents = list(product(*(range(b) for b in bounds)))
    ix = {v: i for i, v in enumerate(exponents)}
    n = len(exponents)
    t = [[[0] * n for _ in range(n)] for _ in range(n)]
    for i, a in enumerate(exponents):
        for j, b in enumerate(exponents):
            c = tuple(x + y for x, y in zip(a, b))
            if all(x < bound for x, bound in zip(c, bounds)):
                t[i][j][ix[c]] = 1
    return t, exponents


def semilinear_kernel(t, unit, h, f):
    """Return ker(a -> a^(p^h)), with the coefficient twist removed."""
    n = len(t)
    c = columns([algebra_power(t, v, f.p ** h, unit, f) for v in identity(n)], n)
    untwist = f.p ** ((-h) % f.e)
    return [[f.power(x, untwist) for x in v] for v in kernel(c, n, f)]


def validate_tensor(t, f):
    if not isinstance(f, Field):
        raise ValueError('field contract required')
    if not isinstance(t, (list, tuple)) or not t:
        raise ValueError('positive square tensor required')
    n = len(t)
    if any(not isinstance(a, (list, tuple)) or len(a) != n for a in t):
        raise ValueError('input dimensions differ')
    for a in t:
        for b in a:
            if not isinstance(b, (list, tuple)) or len(b) != n:
                raise ValueError('output dimension differs')
            if any(type(x) is not int or not 0 <= x < f.q for x in b):
                raise ValueError('noncanonical field entry')


def check_certificate(t, cert, f):
    """Check the factor maps by all basis products, without nucleus tests."""
    n = len(t)
    mu, _ = model(cert['heights'], f)
    if len(mu) != n:
        return False
    u, v, w = (cert[k] for k in ('U', 'V', 'W'))
    if any(determinant(a, f) == 0 for a in (u, v, w)):
        return False
    for i in range(n):
        for j in range(n):
            if tensor_value(t, column(u, i), column(v, j), f) != mv(w, mu[i][j], f):
                return False
    return True


def recognize(t, f):
    """Return (certificate, None), or (None, mathematical rejection reason)."""
    validate_tensor(t, f)
    n = len(t)
    equations = []
    for i, j, k in product(range(n), repeat=3):
        row = [0] * (2 * n * n)
        for a in range(n):
            row[a * n + i] = f.add[row[a * n + i]][t[a][j][k]]
            index = n * n + k * n + a
            row[index] = f.add[row[index]][f.neg[t[i][j][a]]]
        equations.append(row)
    basis = kernel(equations, 2 * n * n, f)
    if len(basis) != n:
        return None, 'nucleus dimension'
    xb = [[b[i * n:(i + 1) * n] for i in range(n)] for b in basis]
    yb = [[b[n * n + i * n:n * n + (i + 1) * n] for i in range(n)] for b in basis]
    if rank([b[:n*n] for b in basis], f) != n or rank([b[n*n:] for b in basis], f) != n:
        return None, 'nucleus projection'
    if any(mm(a, b, f) != mm(b, a, f) for a in yb for b in yb):
        return None, 'noncommutative nucleus'
    right = [[t[i][j][k] for j in range(n)] for i in range(n) for k in range(n)]
    if rank(right, f) != n:
        return None, 'right kernel'
    flat = [sum(a, []) for a in yb]
    _, positions = rref(flat, n * n, f)
    coord_inverse = inverse([[a[j] for a in flat] for j in positions], f)

    def coordinates(a):
        v = sum(a, [])
        c = mv(coord_inverse, [v[j] for j in positions], f)
        if [f.total(f.mul[c[k]][flat[k][j]] for k in range(n)) for j in range(n*n)] != v:
            raise ArithmeticError('nucleus closure')
        return c

    table = [[coordinates(mm(a, b, f)) for b in yb] for a in yb]
    unit = coordinates(identity(n))
    exponent = 1
    while exponent < n:
        exponent *= f.q
    qmap = columns([algebra_power(table, v, exponent, unit, f) for v in identity(n)], n)
    radical = kernel(qmap, n, f)
    if len(radical) != n - 1:
        return None, 'residue field or number of components'

    def cyclic(module):
        actions = [[[f.total(f.mul[c[k]][module[k][i][j]] for k in range(n))
                     for j in range(n)] for i in range(n)] for c in radical]
        jm = [column(a, j) for a in actions for j in range(n)]
        if rank(jm, f) != n - 1:
            return None
        seed = next(v for v in identity(n) if rank(jm + [v], f) == n)
        return columns([mv(a, seed, f) for a in module], n), seed

    ux, wy = cyclic(xb), cyclic(yb)
    if ux is None or wy is None:
        return None, 'nonregular nucleus module'
    u, u0 = ux
    w, _ = wy
    phi = columns([tensor_value(t, u0, e, f) for e in identity(n)], n)
    v = mm(inverse(phi, f), w, f)
    span = [tensor_value(table, a, b, f) for a in radical for b in radical]
    current = rank(span, f)
    generators, heights = [], []
    h, power = 0, 1
    while power < n:
        h += 1
        power *= f.p
        for a in semilinear_kernel(table, unit, h, f):
            new_rank = rank(span + [a], f)
            if new_rank > current:
                span.append(a)
                generators.append(a)
                heights.append(h)
                current = new_rank
    if f.p ** sum(heights) != n:
        return None, 'height dimension'
    mu, exponents = model(heights, f)
    images = []
    for exps in exponents:
        value = unit[:]
        for g, e in zip(generators, exps):
            value = tensor_value(table, value, algebra_power(table, g, e, unit, f), f)
        images.append(value)
    c = columns(images, n)
    if determinant(c, f) == 0:
        raise ArithmeticError('height criterion did not produce a basis')
    cert = {'heights': heights, 'U': mm(u, c, f), 'V': mm(v, c, f), 'W': mm(w, c, f)}
    if not check_certificate(t, cert, f):
        raise ArithmeticError('transported product mismatch')
    index = gcd(f.q - 1, *(n * (f.p ** h - 1) // 2 for h in heights))
    detu, detv, detw = (determinant(cert[k], f) for k in ('U', 'V', 'W'))
    delta = f.mul[detw][f.inv[f.mul[detu][detv]]]
    cert['sl_orbit_count'] = index
    cert['sl_orbit_label'] = f.power(delta, (f.q - 1) // index)
    return cert, None


def bezout(a, b):
    x, y, u, v = 1, 0, 0, 1
    while b:
        quotient, remainder = divmod(a, b)
        a, b = b, remainder
        x, u = u, x - quotient * u
        y, v = v, y - quotient * v
    return a, x, y


def sl_transporter(first, second, f):
    """Return determinant-one maps F,G,H with second(Fu,Gv)=H first(u,v)."""
    a, why = recognize(first, f)
    if a is None:
        return None, 'first tensor: ' + why
    b, why = recognize(second, f)
    if b is None:
        return None, 'second tensor: ' + why
    if a['heights'] != b['heights'] or a['sl_orbit_label'] != b['sl_orbit_label']:
        return None, 'different special-linear orbits'
    n, m = len(first), f.q - 1
    du, dv, dw = [f.mul[determinant(a[k], f)][f.inv[determinant(b[k], f)]]
                  for k in ('U', 'V', 'W')]
    z = f.mul[f.mul[du][dv]][f.inv[dw]]
    primitive = next(c for c in range(1, f.q)
                     if len({f.power(c, i) for i in range(m)}) == m)
    logz = next(i for i in range(m) if f.power(primitive, i) == z)
    g, coefficients = m, []
    for h in a['heights']:
        g, x, y = bezout(g, n * (f.p ** h - 1) // 2)
        coefficients = [x * c for c in coefficients] + [y]
    if logz % g:
        raise ArithmeticError('orbit label disagrees with determinant image')
    scalars = [f.power(primitive, (c * (logz // g)) % m) for c in coefficients]
    _, exponents = model(a['heights'], f)
    diagonal = [1] * n
    for j, es in enumerate(exponents):
        for c, e in zip(scalars, es):
            diagonal[j] = f.mul[diagonal[j]][f.power(c, e)]
    inverse_n = pow(n, -1, m)
    unit_a = f.power(f.mul[du][f.inv[z]], inverse_n)
    unit_b = f.power(f.mul[dv][f.inv[z]], inverse_n)
    factors = [unit_a, unit_b, f.mul[unit_a][unit_b]]
    out = {}
    for key, target, scalar in zip(('U', 'V', 'W'), ('F', 'G', 'H'), factors):
        middle = [[f.mul[scalar][diagonal[i]] if i == j else 0 for j in range(n)] for i in range(n)]
        out[target] = mm(mm(b[key], middle, f), inverse(a[key], f), f)
        if determinant(out[target], f) != 1:
            raise ArithmeticError('determinant correction failed')
    for i in range(n):
        for j in range(n):
            if tensor_value(second, column(out['F'], i), column(out['G'], j), f) != mv(out['H'], first[i][j], f):
                raise ArithmeticError('special-linear product mismatch')
    return out, None
