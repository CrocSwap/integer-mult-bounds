#!/usr/bin/env python3
"""Exact finite corroboration of the written arbitrary-register theorem.

No finite matrix test is used to infer the universal formal identity.
Only Python's standard library is needed; checks survive python -O.
"""
from itertools import combinations, permutations, product
import json

E = (0, 0)
X = (0, 1)
Y = (-1, 1)
ZERO = frozenset()
ONE = frozenset({E})


def require(value, message):
    if not value:
        raise ValueError(message)


def group_mul(a, b):
    return (a[0] + (-1 if a[1] else 1) * b[0], a[1] ^ b[1])


def convolution(a, b, multiply):
    out = set()
    for x in a:
        for y in b:
            z = multiply(x, y)
            if z in out:
                out.remove(z)
            else:
                out.add(z)
    return frozenset(out)


def matmul(a, b, multiply):
    n = len(a)
    return tuple(tuple(sum_cells(convolution(a[i][k], b[k][j], multiply)
                                 for k in range(n)) for j in range(n))
                 for i in range(n))


def sum_cells(cells):
    out = ZERO
    for cell in cells:
        out = out ^ cell
    return out


def identity(n, one=ONE):
    return tuple(tuple(one if i == j else ZERO for j in range(n)) for i in range(n))


def projectors(n):
    for u in range(1, 1 << n):
        for v in range(1, 1 << n):
            if (u & v).bit_count() % 2:
                yield tuple(tuple(((u >> i) & 1) * ((v >> j) & 1)
                                  for j in range(n)) for i in range(n))


def diagonal_projector(n, role):
    return tuple(tuple(int(i == role and j == role) for j in range(n)) for i in range(n))


def call(n, g, projector):
    return tuple(tuple((ONE if i == j else ZERO) ^
                       (frozenset({E, g}) if projector[i][j] else ZERO)
                       for j in range(n)) for i in range(n))


def reduced(word):
    stack = []
    for letter in word:
        if stack and stack[-1] == letter:
            stack.pop()
        else:
            stack.append(letter)
    return tuple(stack)


def letters(g):
    k, flip = g
    word = ('x', 'y') * k if k >= 0 else ('y', 'x') * -k
    return reduced(word + (('x',) if flip else ()))


def direct(targets, n):
    return [(X if label == 'x' else Y, diagonal_projector(n, role))
            for role, target in enumerate(targets) for label in letters(target)]


def endpoint(targets, n):
    return tuple(tuple(frozenset({targets[i] if i < len(targets) else E})
                       if i == j else ZERO for j in range(n)) for i in range(n))


def replay(word, n):
    out = identity(n)
    for g, projector in word:
        out = matmul(out, call(n, g, projector), group_mul)
    return out


def literal_replay(word, n):
    """Independent group arithmetic: cancellation of literal x/y words."""
    unit = frozenset({()})
    out = identity(n, unit)
    for g, projector in word:
        label = ('x',) if g == X else ('y',)
        factor = tuple(tuple((unit if i == j else ZERO) ^
                             (frozenset({(), label}) if projector[i][j] else ZERO)
                             for j in range(n)) for i in range(n))
        out = matmul(out, factor, lambda a, b: reduced(a + b))
    return out


def representation(matrix, swapped=False):
    """Map formal cells to 2-by-2 Laurent blocks, storing exponents exactly."""
    n = len(matrix)
    out = [[ZERO for _ in range(2 * n)] for _ in range(2 * n)]
    for i in range(n):
        for j in range(n):
            for k, flip in matrix[i][j]:
                power = k + flip if swapped else -k
                for a in range(2):
                    b = a ^ flip
                    out[2 * i + a][2 * j + b] ^= frozenset({power if a == 0 else -power})
    return tuple(tuple(row) for row in out)


def determinant(matrix):
    n = len(matrix)
    terms = []
    for p in permutations(range(n)):
        term = frozenset({0})
        for i, j in enumerate(p):
            term = convolution(term, matrix[i][j], lambda a, b: a + b)
        terms.append(term)
    return sum_cells(terms)


def minor_degree(matrix):
    """Maximum degree of every square minor, including the empty minor."""
    n = len(matrix)
    result = 0
    for size in range(1, n + 1):
        for rows in combinations(range(n), size):
            for cols in combinations(range(n), size):
                det = determinant(tuple(tuple(matrix[i][j] for j in cols) for i in rows))
                if det:
                    result = max(result, max(det))
    return result


def main():
    counts = {"projectors": 0, "generator_minor_checks": 0, "mixed_words": 0,
              "formal_targets": 0, "omission_controls": 0, "other_controls": 0}
    for n, expected in ((1, 1), (2, 6), (3, 28), (4, 120)):
        ps = tuple(projectors(n))
        require(len(ps) == expected, "projector census")
        counts['projectors'] += len(ps)
        for p in ps:
            require(all(sum(p[i][k] * p[k][j] for k in range(n)) % 2 == p[i][j]
                        for i in range(n) for j in range(n)), "idempotence")
            for label in (X, Y):
                c = call(n, label, p)
                require(matmul(c, c, group_mul) == identity(n), "call involution")
                if n <= 2:
                    for swapped in (False, True):
                        actual = minor_degree(representation(c, swapped))
                        expected_degree = int((label == X) == swapped)
                        require(actual == expected_degree, "generator degree")
                        counts['generator_minor_checks'] += 1
    generators = tuple(product((X, Y), projectors(2)))
    for word in product(generators, repeat=2):
        formal = replay(word, 2)
        literal = tuple(tuple(frozenset(letters(g) for g in cell) for cell in row)
                        for row in formal)
        require(literal_replay(word, 2) == literal, "mixed-projector word")
        for swapped in (False, True):
            represented = matmul(representation(call(2, *word[0]), swapped),
                                 representation(call(2, *word[1]), swapped),
                                 lambda a, b: a + b)
            require(representation(formal, swapped) == represented,
                    "mixed-word representation")
            charged_label = X if swapped else Y
            require(minor_degree(represented) <= sum(g == charged_label for g, _ in word),
                    "mixed-word degree bound")
        counts["mixed_words"] += 1
    group_window = tuple(product(range(-2, 3), range(2)))
    for a, b in product(group_window, repeat=2):
        require(reduced(letters(a) + letters(b)) == letters(group_mul(a, b)),
                "independent group law")
        for swapped in (False, True):
            left = representation(((frozenset({group_mul(a, b)}),),), swapped)
            right = matmul(representation(((frozenset({a}),),), swapped),
                           representation(((frozenset({b}),),), swapped),
                           lambda x, y: x + y)
            require(left == right, "representation homomorphism")
    fixtures = [(list(ts), 2) for ts in product(group_window, repeat=2)]
    fixtures += [([(2, 0), (-2, 1), (1, 1)], 4),
                 ([(7, 0), (-5, 1), (0, 1), (-3, 0)], 7)]
    for targets, n in fixtures:
        word = direct(targets, n)
        goal = endpoint(targets, n)
        require(replay(word, n) == goal, "formal endpoint")
        literal_goal = tuple(tuple(frozenset(letters(g) for g in cell) for cell in row)
                             for row in goal)
        require(literal_replay(word, n) == literal_goal, "literal endpoint")
        require(sum(g == X for g, _ in word) == sum(abs(k + f) for k, f in targets),
                "x invoice")
        require(sum(g == Y for g, _ in word) == sum(abs(k) for k, _ in targets),
                "y invoice")
        if n == 2:
            for swapped in (False, True):
                require(minor_degree(representation(goal, swapped)) ==
                        sum(abs(k + (f if swapped else 0)) for k, f in targets),
                        "target degree")
        for i in range(len(word)):
            require(replay(word[:i] + word[i + 1:], n) != goal, "omission accepted")
            counts['omission_controls'] += 1
        counts['formal_targets'] += 1
    dirty_targets, n = [(1, 0), (-1, 1)], 4
    word = direct(dirty_targets, n)
    goal = endpoint(dirty_targets, n)
    require(replay(word + [(X, diagonal_projector(n, 3))], n) != goal,
            "dirty spectator mutation accepted")
    require(replay(list(reversed(word)), n) != goal, "reversed rotation accepted")
    require(replay([(Y, p) if g == X else (X, p) for g, p in word], n) != goal,
            "swapped labels accepted")
    counts['other_controls'] += 3
    # Finite cyclic specialization is deliberately NOT a lower-bound oracle.
    finite_alias = ((frozenset({E, (4, 0)}),),)
    require(finite_alias[0][0] != ZERO, "formal alias control")
    require(sum_cells(frozenset({(k % 4, f)}) for k, f in finite_alias[0][0]) == ZERO,
            "finite quotient control")
    counts['other_controls'] += 1
    print(json.dumps(counts, sort_keys=True))
    print('PASS_INFINITE_DIHEDRAL_REGISTER_BOUND finite_checks_only; universal_proof=README.md')


if __name__ == '__main__':
    main()
