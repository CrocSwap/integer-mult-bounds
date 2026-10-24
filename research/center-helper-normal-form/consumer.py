"""Exact conditional three-field controller over Z[q]/(q^4-1).

Apache-2.0; substantial OpenAI Codex assistance. No physical provider is assumed.
"""


def need(value, message):
    if not value:
        raise ValueError(message)


ZERO = (0, 0, 0, 0)
ONE = (1, 0, 0, 0)
Q = (0, 1, 0, 0)
P = (0, 0, 1, 0)


def plus(a, b):
    return tuple(x+y for x, y in zip(a, b))


def neg(a):
    return tuple(-x for x in a)


def times(a, b):
    out = [0]*4
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[(i+j) % 4] += x*y
    return tuple(out)


def multiply(a, b):
    return [[tuple(sum(times(a[i][k], b[k][j])[e] for k in range(3))
                   for e in range(4)) for j in range(3)] for i in range(3)]


def product(*matrices):
    out = [[ONE if i == j else ZERO for j in range(3)] for i in range(3)]
    for matrix in matrices:
        out = multiply(out, matrix)
    return out


def check():
    u = [[ONE, Q, ZERO], [ZERO, ONE, Q], [ZERO, ZERO, ONE]]
    dual = [[ONE, ZERO, ZERO], [neg(Q), ONE, ZERO], [P, neg(Q), ONE]]
    d = [[P, ZERO, ZERO], [ZERO, ONE, ZERO], [ZERO, ZERO, P]]
    correction = [[ONE, ZERO, ZERO], [ZERO, ONE, ZERO], [neg(P), ZERO, ONE]]
    left = [[ONE, ZERO, ZERO], [ZERO, neg(P), ZERO], [ONE, ZERO, P]]
    right = [[ZERO, ONE, ONE], [ONE, ZERO, ZERO], [ZERO, ZERO, P]]
    target = [[Q, ZERO, ZERO], [ZERO, Q, ZERO], [ZERO, ZERO, ONE]]
    need(product(left, u, correction, d, dual, d, right) == target,
         'Every coefficient of the exact two-call controller')
    # Check the raw inverse transpose, rather than a sign-only opposite shear.
    transpose_u = [list(row) for row in zip(*u)]
    identity = [[ONE if i == j else ZERO for j in range(3)] for i in range(3)]
    need(product(transpose_u, dual) == product(dual, transpose_u) == identity,
         'Actual raw inverse transpose with its quadratic long-root term')
    wrong = [row[:] for row in correction]
    wrong[2][0] = P
    need(product(left, u, wrong, d, dual, d, right) != target, 'Wrong long-root sign rejected')
    need(product(left, u, d, dual, d, right) != target, 'Unpaid omitted long-root correction rejected')
    wrong_dual = [row[:] for row in dual]
    wrong_dual[2][0] = ZERO
    need(product(left, u, correction, d, wrong_dual, d, right) != target,
         'Omitted raw-dual quadratic term rejected')
    need(product(left, u, correction, dual, right) != target, 'Omitted Pauli conjugation rejected')
    # A dense rational specialization is separate from the cyclic convolution.
    def dense(m, scalar):
        return [[sum(x*scalar**e for e, x in enumerate(p)) for p in row] for row in m]
    def mm(a, b):
        return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
    for scalar in (-1, 1):
        actual = [[int(i == j) for j in range(3)] for i in range(3)]
        for matrix in (left, u, correction, d, dual, d, right):
            actual = mm(actual, dense(matrix, scalar))
        need(actual == dense(target, scalar), 'Independent exact dense specialization')
    actual = [[int(i == j) for j in range(3)] for i in range(3)]
    for matrix in (left, u, correction, d, dual, d, right):
        actual = mm(actual, dense(matrix, 2))
    need(actual != dense(target, 2), 'The order-four premise cannot be dropped')
    return {'status': 'PASS_CONDITIONAL_TWO_CALL_THREE_FIELD_CONTROLLER',
            'oracle_calls': ['U(Q)^(-T)', 'U(Q)'], 'query_outputs': 2, 'restored_outputs': 1,
            'coefficient_ring': 'Z[q]/(q^4-1)', 'free_boundary_entries': ['0', '1', '-P', 'P'],
            'homogeneous_progress_required': True, 'native_provider_realized': False,
            'new_kappa': None, 'controls': 5}
