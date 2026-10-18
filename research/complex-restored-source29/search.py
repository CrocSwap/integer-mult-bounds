"""Exact two-register word metric; Hanson Sun, with OpenAI Codex assistance.

Apache-2.0. The ten-operation alphabet follows Philipp/mightyOil's PR883.
This implementation uses normalized integer matrices, with no magnitude cap.
"""

from fractions import Fraction
import hashlib


SEED = 29
RADIUS = 6
IDENTITY = (1, 0, 0, 1, 0)
GATES = ("t+s", "t-s", "s+t", "s-t", "2t", "t/2", "2s", "s/2", "-t", "-s")
INVERSE = (1, 0, 3, 2, 5, 4, 7, 6, 8, 9)
ORDER = tuple((i + SEED) % len(GATES) for i in range(len(GATES)))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def normalize(a, b, c, d, exponent):
    """Represent [[a,b],[c,d]] / 2**exponent uniquely."""
    need(type(exponent) is int and exponent >= 0, "invalid denominator exponent")
    while exponent and not ((a | b | c | d) & 1):
        a, b, c, d, exponent = a // 2, b // 2, c // 2, d // 2, exponent - 1
    return a, b, c, d, exponent


def step(matrix, gate):
    a, b, c, d, k = matrix
    if gate == 0:
        a, b = a + c, b + d
    elif gate == 1:
        a, b = a - c, b - d
    elif gate == 2:
        c, d = c + a, d + b
    elif gate == 3:
        c, d = c - a, d - b
    elif gate == 4:
        a, b = 2 * a, 2 * b
    elif gate == 5:
        c, d, k = 2 * c, 2 * d, k + 1
    elif gate == 6:
        c, d = 2 * c, 2 * d
    elif gate == 7:
        a, b, k = 2 * a, 2 * b, k + 1
    elif gate == 8:
        a, b = -a, -b
    elif gate == 9:
        c, d = -c, -d
    else:
        raise ValueError("unknown gate")
    return normalize(a, b, c, d, k)


def multiply(x, y):
    a, b, c, d, k = x
    e, f, g, h, ell = y
    return normalize(a * e + b * g, a * f + b * h,
                     c * e + d * g, c * f + d * h, k + ell)


def inverse(matrix):
    a, b, c, d, k = matrix
    determinant = a * d - b * c
    magnitude = abs(determinant)
    need(magnitude > 0 and magnitude & (magnitude - 1) == 0,
         "determinant is not a signed power of two")
    sign = 1 if determinant > 0 else -1
    exponent = magnitude.bit_length() - 1 - k
    values = [sign * d, -sign * b, -sign * c, sign * a]
    if exponent < 0:
        values = [v * 2 ** (-exponent) for v in values]
        exponent = 0
    return normalize(*values, exponent)


def ball(radius=RADIUS, order=ORDER):
    """Complete BFS ball: deduplication is exact matrix equality only."""
    need(type(radius) is int and 0 <= radius <= RADIUS, "radius outside fixed experiment")
    need(sorted(order) == list(range(10)), "incomplete gate alphabet")
    words = {IDENTITY: ()}
    frontier = [IDENTITY]
    layers = [1]
    for _ in range(radius):
        following = []
        for matrix in frontier:
            for gate in order:
                nxt = step(matrix, gate)
                if nxt not in words:
                    words[nxt] = words[matrix] + (gate,)
                    following.append(nxt)
        frontier = following
        layers.append(len(frontier))
    return words, layers


def distance_digest(words):
    digest = hashlib.sha256()
    for matrix in sorted(words):
        row = (*matrix, len(words[matrix]))
        digest.update((",".join(map(str, row)) + "\n").encode("ascii"))
    return digest.hexdigest()


def shear(q):
    q = Fraction(q)
    denominator = q.denominator
    need(denominator & (denominator - 1) == 0, "nondyadic shear")
    return normalize(denominator, q.numerator, 0, denominator,
                     denominator.bit_length() - 1)


def execute(word):
    result = IDENTITY
    for gate in word:
        result = step(result, gate)
    return result


def metric(coefficients, words):
    inverses = [(inverse(matrix), word) for matrix, word in words.items()]
    result = []
    for q in coefficients:
        goal = shear(q)
        best = None
        for left_inverse, prefix in inverses:
            suffix = words.get(multiply(goal, left_inverse))
            if suffix is not None and (best is None or len(prefix) + len(suffix) < len(best)):
                best = prefix + suffix
        if best is not None:
            need(execute(best) == goal, "constructed word misses the complete shear")
        result.append({
            "coefficient": str(q),
            "two_register_minimum": len(best) if best is not None else None,
            "two_register_lower_bound": len(best) if best is not None else 2 * RADIUS + 1,
            "word": [GATES[g] for g in best] if best is not None else None,
        })
    return result
