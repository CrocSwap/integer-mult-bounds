"""Bounded prime-field reference for the all-field graph-domain proof.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
Matrices act on column vectors. No predecessor code is imported.
"""
from collections import Counter
from itertools import permutations, product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def field(q):
    require(type(q) is int and q in (2, 3, 5), 'reference field must be 2, 3 or 5')


def matrix(value, q):
    field(q)
    require(type(value) in (tuple, list) and len(value) <= 4, 'reference matrix dimension exceeds four')
    n = len(value)
    require(all(type(row) in (tuple, list) and len(row) == n for row in value), 'matrix must be square')
    require(all(type(x) is int and 0 <= x < q for row in value for x in row), 'noncanonical field entry')
    return tuple(tuple(row) for row in value)


def identity(n):
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def multiply(a, b, q):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b))) % q
                       for j in range(len(b))) for i in range(len(a)))


def reduce_rows(rows, width, q):
    rows = [list(row) for row in rows]
    pivots = []
    for column in range(width):
        candidates = [i for i in range(len(pivots), len(rows)) if rows[i][column] % q]
        if not candidates:
            continue
        index = len(pivots)
        rows[index], rows[candidates[0]] = rows[candidates[0]], rows[index]
        scale = pow(rows[index][column] % q, -1, q)
        rows[index] = [x * scale % q for x in rows[index]]
        for i in range(len(rows)):
            if i != index:
                coefficient = rows[i][column] % q
                rows[i] = [(x - coefficient * y) % q for x, y in zip(rows[i], rows[index], strict=True)]
        pivots.append(column)
    return rows, pivots


def inverse(a, q):
    n = len(a)
    rows, pivots = reduce_rows([tuple(a[i]) + identity(n)[i] for i in range(n)], n, q)
    require(len(pivots) == n, 'singular graph or complement basis')
    return tuple(tuple(row[n:]) for row in rows)


def polynomial_add(a, b, q):
    return trim(tuple(((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % q
                      for i in range(max(len(a), len(b)))))


def trim(a):
    nonzero = [i for i, x in enumerate(a) if x]
    return tuple(a[:max(nonzero) + 1]) if nonzero else (0,)


def polynomial_product(a, b, q):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] = (result[i + j] + x * y) % q
    return trim(result)


def remainder(a, b, q):
    result = list(trim(a))
    for i in range(len(result) - len(b), -1, -1):
        coefficient = result[i + len(b) - 1] * pow(b[-1], -1, q) % q
        for j, value in enumerate(b):
            result[i + j] = (result[i + j] - coefficient * value) % q
    return trim(result[:len(b) - 1])


def quotient(a, b, q):
    require(remainder(a, b, q) == (0,), 'non-exact polynomial division')
    result, answer = list(a), [0] * (len(a) - len(b) + 1)
    for i in range(len(answer) - 1, -1, -1):
        answer[i] = result[i + len(b) - 1] * pow(b[-1], -1, q) % q
        for j, value in enumerate(b):
            result[i + j] = (result[i + j] - answer[i] * value) % q
    return trim(answer)


def characteristic(a, q):
    n, result = len(a), (0,)
    for perm in permutations(range(n)):
        sign = (-1) ** sum(perm[i] > perm[j] for i in range(n) for j in range(i + 1, n))
        term = (sign % q,)
        for i, j in enumerate(perm):
            term = polynomial_product(term, ((-a[i][j]) % q, 1) if i == j else ((-a[i][j]) % q,), q)
        result = polynomial_add(result, term, q)
    return result


def factors(polynomial, q):
    """Ascending-degree monic trial division; lower-degree factors removed first."""
    current, result = polynomial, []
    for degree in range(1, len(polynomial)):
        for lower in product(range(q), repeat=degree):
            candidate = lower + (1,)
            exponent = 0
            for _ in range(len(polynomial) - 1):
                if len(current) < len(candidate) or remainder(current, candidate, q) != (0,):
                    break
                current = quotient(current, candidate, q)
                exponent += 1
            if exponent:
                result.append((candidate, exponent))
    require(current == (1,), 'incomplete characteristic factorization')
    return result


def evaluate(polynomial, a, q):
    n = len(a)
    value = tuple((0,) * n for _ in range(n))
    for coefficient in reversed(polynomial):
        value = multiply(value, a, q)
        value = tuple(tuple((value[i][j] + (coefficient if i == j else 0)) % q
                            for j in range(n)) for i in range(n))
    return value


def profile(value, q):
    """Irreducible polynomial and primary block partition; includes p=t."""
    a = matrix(value, q)
    result = []
    for polynomial, exponent in factors(characteristic(a, q), q):
        degree = len(polynomial) - 1
        operator, power, previous, heights = evaluate(polynomial, a, q), identity(len(a)), 0, []
        for _ in range(exponent):
            power = multiply(power, operator, q)
            nullity = len(a) - len(reduce_rows(power, len(a), q)[1])
            require((nullity - previous) % degree == 0, 'nonintegral primary block height')
            heights.append((nullity - previous) // degree)
            previous = nullity
        require(heights == sorted(heights, reverse=True), 'primary heights not decreasing')
        parts = tuple(j for j in range(exponent, 0, -1)
                      for _ in range(heights[j - 1] - (heights[j] if j < exponent else 0)))
        require(sum(parts) == exponent, 'primary multiplicity mismatch')
        result.append((polynomial, parts))
    return tuple(result)


def gl_order(q, n):
    value = 1
    for i in range(n):
        value *= q ** n - q ** i
    return value


def centralizer(value, q):
    answer = 1
    for polynomial, parts in profile(value, q):
        degree, multiplicities = len(polynomial) - 1, Counter(parts)
        heights = [sum(part >= j for part in parts) for j in range(1, max(parts) + 1)]
        exponent = degree * (sum(h * h for h in heights) - sum(m * m for m in multiplicities.values()))
        answer *= q ** exponent
        for count in multiplicities.values():
            answer *= gl_order(q ** degree, count)
    return answer


def intertwiner_basis(source, target, q):
    """Solve S source = target S by elimination, independently of profiles."""
    source, target = matrix(source, q), matrix(target, q)
    require(len(source) == len(target), 'relative operator sizes differ')
    n, equations = len(source), []
    for i in range(n):
        for j in range(n):
            row = [0] * (n * n)
            for k in range(n):
                row[i * n + k] += source[k][j]
                row[k * n + j] -= target[i][k]
            equations.append(tuple(x % q for x in row))
    reduced, pivots = reduce_rows(equations, n * n, q)
    basis = []
    for free in range(n * n):
        if free not in pivots:
            vector = [int(i == free) for i in range(n * n)]
            for row, pivot in zip(reduced, pivots):
                vector[pivot] = -row[free] % q
            basis.append(tuple(vector))
    return tuple(basis)


def intertwiners(source, target, q):
    basis = intertwiner_basis(source, target, q)
    require(q ** len(basis) <= 4096, 'bounded intertwiner enumeration exceeds 4096')
    n, result = len(source), []
    for coefficients in product(range(q), repeat=len(basis)):
        flat = tuple(sum(c * v[i] for c, v in zip(coefficients, basis, strict=True)) % q
                     for i in range(n * n))
        candidate = tuple(flat[i * n:(i + 1) * n] for i in range(n))
        if len(reduce_rows(candidate, n, q)[1]) == n:
            result.append(candidate)
    return tuple(result)


def complete(left, fourth, target_left, target_fourth, q, unused=0,
             shear=None, complement=None):
    """Four ordered graph images, with explicit arbitrary ambient freedom.

    Frames are A, B, graph(left), graph(fourth); left must be invertible.
    The reference is bounded; PROOF.md gives the all-field construction.
    """
    left, fourth = matrix(left, q), matrix(fourth, q)
    target_left, target_fourth = matrix(target_left, q), matrix(target_fourth, q)
    n = len(left)
    require(all(len(a) == n for a in (fourth, target_left, target_fourth)), 'graph sizes differ')
    require(type(unused) is int and 0 <= unused and 2 * n + unused <= 9, 'ambient dimension exceeds nine')
    shear = tuple((0,) * unused for _ in range(2 * n)) if shear is None else shear
    complement = identity(unused) if complement is None else complement
    require(type(shear) in (tuple, list) and len(shear) == 2 * n and
            all(type(row) in (tuple, list) and len(row) == unused for row in shear), 'invalid shear shape')
    require(type(complement) in (tuple, list) and len(complement) == unused and
            all(type(row) in (tuple, list) and len(row) == unused for row in complement), 'invalid complement shape')
    require(all(type(x) is int and 0 <= x < q for rows in (shear, complement) for row in rows for x in row),
            'noncanonical ambient entry')
    inverse(complement, q)
    source = multiply(inverse(left, q), fourth, q)
    target = multiply(inverse(target_left, q), target_fourth, q)
    compatible = profile(source, q) == profile(target, q)
    witnesses = intertwiners(source, target, q)
    require(bool(witnesses) == compatible, 'profile and intertwiner compatibility disagree')
    active = centralizer(source, q) if compatible else 0
    require(len(witnesses) == active, 'centralizer and intertwiner count disagree')
    ambient = active * q ** (2 * n * unused) * gl_order(q, unused)
    if not compatible:
        return {'compatible': False, 'active_realizers': 0, 'ambient_realizers': 0, 'map': None}
    s = witnesses[0]
    lower = multiply(multiply(target_left, s, q), inverse(left, q), q)
    active_map = tuple(s[i] + (0,) * n for i in range(n)) + tuple((0,) * n + lower[i] for i in range(n))
    full = tuple(active_map[i] + tuple(shear[i]) for i in range(2 * n))
    full += tuple((0,) * (2 * n) + tuple(row) for row in complement)
    return {'compatible': True, 'active_realizers': active, 'ambient_realizers': ambient, 'map': full}
