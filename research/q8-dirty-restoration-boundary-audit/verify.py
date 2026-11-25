#!/usr/bin/env python3
"""Independent exact Q8 matrix check for the PR #3697 dirty-state boundary."""

from itertools import product


def require(condition, message):
    if not condition:
        raise ValueError(message)


# An element is (sign, axis), where axis 0,1,2,3 denotes 1,i,j,k.
ONE = (1, 0)
I = (1, 1)
J = (1, 2)
K = (1, 3)
ZI = (-1, 1)
ZJ = (-1, 2)
Z = (-1, 0)
Q8 = tuple((sign, axis) for sign in (1, -1) for axis in range(4))
ZERO = frozenset()
ONE_TERM = frozenset((ONE,))


def qmul(left, right):
    sign_left, axis_left = left
    sign_right, axis_right = right
    sign = sign_left * sign_right
    if axis_left == 0:
        return sign, axis_right
    if axis_right == 0:
        return sign, axis_left
    if axis_left == axis_right:
        return -sign, 0
    cyclic = {(1, 2): 3, (2, 3): 1, (3, 1): 2}
    if (axis_left, axis_right) in cyclic:
        return sign, cyclic[(axis_left, axis_right)]
    return -sign, cyclic[(axis_right, axis_left)]


def xor(left, right):
    return left.symmetric_difference(right)


def ring_mul(left, right):
    result = set()
    for a in left:
        for b in right:
            value = qmul(a, b)
            if value in result:
                result.remove(value)
            else:
                result.add(value)
    return frozenset(result)


def identity(roles):
    return tuple(
        tuple(ONE_TERM if row == col else ZERO for col in range(roles))
        for row in range(roles)
    )


def multiply(left, right):
    roles = len(left)
    require(roles == len(right), "matrix dimension mismatch")
    result = [[ZERO for _ in range(roles)] for _ in range(roles)]
    for row in range(roles):
        for middle in range(roles):
            for col in range(roles):
                result[row][col] = xor(
                    result[row][col],
                    ring_mul(left[row][middle], right[middle][col]),
                )
    return tuple(tuple(row) for row in result)


def apply_vector(matrix, vector):
    result = []
    for row in matrix:
        value = ZERO
        for coefficient, entry in zip(row, vector):
            value = xor(value, ring_mul(coefficient, entry))
        result.append(value)
    return tuple(result)


def paid_factor(label, u, v):
    """Return I + (1+[label]) u v^T over F2[Q8]."""
    roles = len(u)
    require(roles == len(v) and roles > 0, "invalid projector dimensions")
    require(sum(a * b for a, b in zip(v, u)) % 2 == 1,
            "paid projector is not idempotent")
    result = [list(row) for row in identity(roles)]
    one_plus_label = frozenset((ONE, label))
    for row in range(roles):
        for col in range(roles):
            if u[row] & v[col]:
                result[row][col] = xor(result[row][col], one_plus_label)
    return tuple(tuple(row) for row in result)


def replay(word, roles):
    state = identity(roles)
    for label, u, v in word:
        state = multiply(paid_factor(label, u, v), state)
    return state


def target_matrix(targets, roles):
    require(len(targets) <= roles, "more targets than roles")
    return tuple(
        tuple(
            (frozenset((targets[row],)) if row < len(targets) else ONE_TERM)
            if row == col else ZERO
            for col in range(roles)
        )
        for row in range(roles)
    )


def basis(roles, at):
    return tuple(int(index == at) for index in range(roles))


def witness(targets, spectators):
    roles = len(targets) + spectators
    word = []
    for role, target in enumerate(targets):
        label = I if target == ZI else J
        e = basis(roles, role)
        word.extend((label, e, e) for _ in range(3))
    return roles, tuple(word)


def diagonal(matrix):
    return tuple(matrix[index][index] for index in range(len(matrix)))


def main():
    require(len(set(Q8)) == 8, "Q8 element encoding is not injective")
    require(all(qmul(ONE, g) == g and qmul(g, ONE) == g for g in Q8),
            "Q8 identity law failed")
    require(all(qmul(a, b) in Q8 for a in Q8 for b in Q8),
            "Q8 closure failed")
    require(all(qmul(qmul(a, b), c) == qmul(a, qmul(b, c))
                for a, b, c in product(Q8, repeat=3)),
            "Q8 associativity failed")
    require(qmul(qmul(I, I), I) == ZI and qmul(qmul(J, J), J) == ZJ,
            "negative-generator powers failed")
    require(qmul(I, I) == Z and qmul(J, J) == Z,
            "Q8 square relation failed")

    target_types = ((ZI,), (ZJ,), (ZI, ZI), (ZI, ZJ), (ZJ, ZI), (ZJ, ZJ))
    positive_cases = 0
    for targets in target_types:
        for spectators in range(4):
            roles, word = witness(targets, spectators)
            got = replay(word, roles)
            want = target_matrix(targets, roles)
            require(len(word) == 3 * len(targets), "witness length changed")
            require(got == want, "valid witness failed full-matrix endpoint")
            positive_cases += 1

    # x=(1,1), y=(1,0) gives the legal idempotent N=x y^T.
    # Three legal i calls produce the right diagonal but a nonzero leak.
    u = (1, 1)
    v = (1, 0)
    require(sum(a * b for a, b in zip(v, u)) % 2 == 1,
            "negative-control projector is not idempotent")
    leak_word = tuple((I, u, v) for _ in range(3))
    leaked = replay(leak_word, 2)
    desired = target_matrix((ZI,), 2)
    require(diagonal(leaked) == diagonal(desired),
            "negative control no longer fools a diagonal-only check")
    require(leaked != desired, "full-matrix check missed dirty leakage")
    require(leaked[1][0] == frozenset((ONE, ZI)),
            "negative-control leak has the wrong exact support")
    require(leaked[0][1] == ZERO, "negative-control leak orientation changed")

    # With the core input equal to [1], each dirty basis input h changes.
    for h in Q8:
        initial = (ONE_TERM, frozenset((h,)))
        got = apply_vector(leaked, initial)
        want = apply_vector(desired, initial)
        require(got[0] == want[0], "negative control changed its target coordinate")
        require(got[1] != want[1],
                "negative control unexpectedly restores a dirty basis state")

    print(
        "PASS_Q8_DIRTY_RESTORATION_BOUNDARY "
        f"full_endpoint_cases={positive_cases} "
        "diagonal_only_negative_control=1 dirty_leak=[1]+[zi]"
    )


if __name__ == "__main__":
    main()
