"""Check the helper-consuming module and the five-call border exactly.

Stage interpolation proves the stated bounded-degree identities. The
parameter e stays formal in Q[e,e^-1]; it is never rounded or sampled.
Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as Q
from itertools import product


def run(A):
    need, eye, mul, add, transpose = A.need, A.eye, A.mul, A.add, A.transpose
    def diagonal(values):
        return [[x if i == j else 0 for j in range(len(values))] for i, x in enumerate(values)]
    def equal(a, b):
        return all(x == y for row, other in zip(a, b) for x, y in zip(row, other))

    identity = eye(3)
    projectors = [[[1, 1, 1], [0, 1, 0], [0, -1, 0]], identity,
                  [[0, -1, -1], [1, 2, 1], [-1, -1, 0]]]
    columns = [[[1], [0], [0]], [[0], [1], [0]], [[-1], [1], [0]]]
    rows = [[[0, -1, 0]], [[1, 0, 0]], [[1, 1, 0]]]
    queries = [mul(u, v) for u, v in zip(columns, rows)]
    selectors = [diagonal([0, 0, 0]), diagonal([0, 0, 1]), diagonal([0, 0, 0])]
    basis = [[0, 1, -1], [-1, -1, 0], [1, 1, 1]]
    basis_inverse = A.inverse(basis)
    for i, p in enumerate(projectors):
        need(mul(p, p) == p and mul(p, queries[i]) == queries[i]
             and mul(queries[i], p) == queries[i], 'Helper module query and stage support')
        need(mul(p, selectors[i]) == selectors[i] and mul(selectors[i], p) == selectors[i]
             and mul(queries[i], selectors[i]) == diagonal([0, 0, 0])
             and mul(selectors[i], queries[i]) == diagonal([0, 0, 0]), 'Disjoint consumed Gaussian selector')
        need(all(mul(p, q) == mul(q, p) for q in projectors), 'Helper stage projectors commute')
    helper_checks = 0
    for a, b, c in product((1, 2), repeat=3):
        target = diagonal([a*b*c, a*b, b*c])
        for sign in (1, -1):
            word = eye(3)
            for i, stage in enumerate((a, b, c)):
                query = add(identity, add(queries[i], selectors[i]), sign-1)
                word = mul(mul(add(identity, projectors[i], stage-1), query), word)
            need(mul(mul(basis_inverse, word), basis) == [[sign*x for x in row] for row in target],
                 'Every coefficient of the multilinear helper endpoint')
            helper_checks += 1

    identity = eye(4)
    e, ei = A.Laurent({1: 1}), A.Laurent({-1: 1})
    u = [[[1], [0], [0], [0]], [[-ei], [1], [0], [0]],
         [[-e], [0], [1], [0]], [[-e], [0], [1], [-1]], [[1], [0], [0], [ei]]]
    v = [[[0, ei, 0, 0]], [[0, 1, -e*e, 0]], [[-ei, 0, -1, 0]],
         [[-ei, 0, 0, 0]], [[-1, 0, 0, e]]]
    matrices = [mul(x, y) for x, y in zip(u, v)]
    masks = [diagonal([1, 1, 0, 0]), diagonal([1, 0, 1, 0]), diagonal([1, 0, 0, 1])]
    wrapper, wrapper_inverse = diagonal([e, 1, e*e, e*e]), diagonal([ei, 1, ei*ei, ei*ei])
    for i, matrix in enumerate(matrices):
        need(equal(mul(v[i], u[i]), [[i % 2]]), 'Nilpotent full query or rank-one central reflection')
        at_one = [[sum(x.terms.values()) if isinstance(x, A.Laurent) else x for x in row] for row in matrix]
        need(equal(matrix, mul(mul(wrapper_inverse, at_one), wrapper)), 'One global scalar wrapper')
        if i % 2 == 0:
            p = masks[i//2]
            need(equal(mul(p, matrix), matrix) and equal(mul(matrix, p), matrix), 'Border query support')

    def word(sign, stages, correct=False, factors=matrices):
        out = eye(4)
        for i, matrix in enumerate(factors):
            out = mul(add(identity, matrix, sign-1), out)
            if i % 2 == 0:
                out = mul(add(identity, masks[i//2], stages[i//2]-1), out)
            if correct and i == 1:
                correction = eye(4)
                correction[1][2] = e*e*(sign-1)
                out = mul(correction, out)
        if correct:
            correction = eye(4)
            correction[0][3] = e*(sign-1)
            out = mul(correction, out)
        return out

    border_checks = 0
    for stages in product((1, 2, 3), repeat=3):
        a, b, c = stages
        target = diagonal([a*b*c, a, b, c])
        inverse = diagonal([Q(1, a*b*c), Q(1, a), Q(1, b), Q(1, c)])
        for sign in (1, -1):
            error = diagonal([0, 0, 0, 0])
            error[0][3], error[1][2] = -(1-sign)*c*e, (1-sign)*e*e
            out = word(sign, stages)
            signed = [[sign*x for x in row] for row in target]
            need(equal(out, add(signed, error)), 'All forward Laurent coefficients')
            reverse = add([[sign*x for x in row] for row in inverse], mul(mul(inverse, error), inverse), -1)
            need(equal(mul(out, reverse), identity) and equal(mul(reverse, out), identity), 'Both inverse endpoint identities')
            need(equal(mul(mul(error, inverse), error), diagonal([0, 0, 0, 0])), 'The two error paths do not compose')
            need(equal(word(sign, stages, True), signed), 'Two paid corrections restore the exact endpoint')
            border_checks += 1
    bad = list(matrices)
    bad[1] = mul(u[1], [[0, 1, 0, 0]])
    need(not equal(word(-1, (1, 2, 3), factors=bad), word(-1, (1, 2, 3))), 'Missing input correction rejected')
    need(not equal(word(-1, (1, 1, 1)), [[-x for x in row] for row in identity]), 'The border is not an exact caller')
    return {'helper_module': {'characters_and_stage_nodes': helper_checks, 'stage_degree_per_variable': 1,
                             'output_masks': ['ABC', 'AB', 'BC'], 'consumed_output': 'B*S Gaussian'},
            'reflection_border': {'characters_and_stage_nodes': border_checks,
                                  'stage_Laurent_exponents_in_inverse_checks': [-1, 0, 1],
                                  'formal_parameter_ring': 'Q[e,e^-1]', 'full_sites': [0, 2, 4],
                                  'paid_reflection_sites': [1, 3],
                                  'endpoint': 'S diag(ABC,A,B,C)+(1-S)(-e*C*E03+e^2*E12)',
                                  'exact_correction_extra_queries': 2, 'rejected_controls': 2},
            'scope': 'Exact module identities and inverse checks only. No physical caller, precision transfer or kappa gain.'}
