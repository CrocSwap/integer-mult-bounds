"""Check formal identities and the full-rank target boundary independently."""

from fractions import Fraction
from itertools import combinations

from catalogue import multiply

IDENTITY = (1, 0, 0, 0, 1, 0, 0, 0, 1)
ZERO = (0,) * 9


def unit(row, column):
    return tuple(int((i, j) == (row, column)) for i in range(3) for j in range(3))


def rank(rows):
    rows = [list(map(Fraction, row)) for row in rows]
    result = 0
    for column in range(len(rows[0])):
        pivot = next((i for i in range(result, len(rows)) if rows[i][column]), None)
        if pivot is None:
            continue
        rows[result], rows[pivot] = rows[pivot], rows[result]
        scale = rows[result][column]
        rows[result] = [x / scale for x in rows[result]]
        for i in range(result + 1, len(rows)):
            scale = rows[i][column]
            rows[i] = [x - scale * y for x, y in zip(rows[i], rows[result])]
        result += 1
        if result == len(rows):
            break
    return result


def matrix_rank(matrix):
    return rank([matrix[3 * row:3 * row + 3] for row in range(3)])


def formal_product(operations):
    terms = {ZERO: IDENTITY}
    for frame, projector in operations:
        updated = {}
        complement = tuple(x ^ y for x, y in zip(IDENTITY, projector))
        for address, coefficient in terms.items():
            for shift, scalar in ((ZERO, complement), (frame, projector)):
                exponent = tuple(x + y for x, y in zip(address, shift))
                matrix = multiply(coefficient, scalar)
                previous = updated.get(exponent, ZERO)
                updated[exponent] = tuple(x ^ y for x, y in zip(previous, matrix))
        terms = {address: matrix for address, matrix in updated.items() if any(matrix)}
    return terms


def scalar(code):
    return tuple((code >> i) & 1 for i in range(9))


def check_formal_controls():
    baseline = [(unit(i, i), unit(w, w)) for w in range(3) for i in range(3)]
    assert formal_product(baseline) == {IDENTITY: IDENTITY}
    # This rank-one address change is hidden by an invalid reduction modulo two.
    alias = [(tuple(3 * x for x in baseline[0][0]), baseline[0][1]), *baseline[1:]]
    assert formal_product(alias) != {IDENTITY: IDENTITY}
    assert formal_product([(tuple(x % 2 for x in frame), projector)
                           for frame, projector in alias]) == {IDENTITY: IDENTITY}

    e00, e11, e22, e10, e01 = (unit(i, j) for i, j in ((0, 0), (1, 1), (2, 2), (1, 0), (0, 1)))
    plus = lambda a, b: tuple(x + y for x, y in zip(a, b))
    minus = lambda a, b: tuple(x - y for x, y in zip(a, b))
    frames = [e22, e00, e11, plus(e00, e10), minus(e11, e10),
              plus(e00, e01), minus(e11, e01), tuple(-x for x in e22)]
    projectors = list(map(scalar, (3, 1, 1, 16, 16, 256, 256, 3)))
    assert all(matrix_rank(frame) == 1 for frame in frames)
    assert all(matrix_rank(projector) == 1 and multiply(projector, projector) == projector
               for projector in projectors)
    assert any(multiply(a, b) != multiply(b, a) for a, b in combinations(projectors, 2))
    assert rank(frames) == 5
    target = plus(e00, e11)
    assert matrix_rank(target) == 2
    assert formal_product(list(zip(frames, projectors))) == {target: IDENTITY}
    return {'nine_call_identity': True, 'modular_alias_rejected': True,
            'noncommuting_eight_call_identity': True, 'frame_span': 5, 'target_rank': 2}


# These are search-core controls, not admissible constructions. Code 17 is
# a rank-two scalar projector. A real accepted core example detects a checker
# that rejects every terminal; the mutation removes one target contribution.
CORE_WORDS = ((3, 3, 17, 17, 17, 256, 256, 256),
              (3, 3, 17, 17, 1, 256, 256, 256))
