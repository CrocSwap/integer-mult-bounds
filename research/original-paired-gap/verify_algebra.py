"""Check ordered identities for the reviewed monomial-square theorem.

The proof states the access and frame hypotheses. These checks use no
fourth-power relation for Q. New code is Apache-2.0, with Codex assistance.
"""

from fractions import Fraction as Q


def need(value, message):
    if not value:
        raise ValueError(message)


def reduce_word(word):
    result = []
    for token in word:
        if result and ((result[-1], token) in (('q', 'q-'), ('q-', 'q'), ('T', 'T'))):
            result.pop()
        else:
            result.append(token)
    return tuple(result)


def add(a, b, coefficient=1):
    result = dict(a)
    for word, value in b.items():
        value = result.get(word, 0) + coefficient * value
        if value:
            result[word] = value
        else:
            result.pop(word, None)
    return result


def product(a, b):
    result = {}
    for u, x in a.items():
        for v, y in b.items():
            result = add(result, {reduce_word(u + v): x * y})
    return result


def scale(value, coefficient):
    return {word: coefficient * x for word, x in value.items() if coefficient * x}


I, ZERO = {(): Q(1)}, {}


def token(name):
    return {(name,): Q(1)}


def eye(n):
    return [[dict(I if i == j else ZERO) for j in range(n)] for i in range(n)]


def mm(a, b):
    result = []
    for row in a:
        values = []
        for column in zip(*b):
            value = {}
            for x, y in zip(row, column):
                value = add(value, product(x, y))
            values.append(value)
        result.append(values)
    return result


def shear(n, target, source, coefficient):
    result = eye(n)
    result[target][source] = coefficient
    return result


def ordered_maps():
    r, k, t = map(token, ('R', 'K', 'T'))
    kr = product(k, r)
    g, h = product(r, add(I, t, -1)), product(add(I, t), k)
    raw_f = [[I, ZERO, ZERO], [add(I, kr, -1), I, scale(k, -1)],
             [scale(r, -2), ZERO, scale(I, -1)]]
    pre = shear(3, 2, 0, scale(product(r, t), -1))
    mode = shear(3, 2, 0, r)
    target = shear(3, 1, 2, product(t, k))
    forward = mm(target, mm(mode, mm(raw_f, pre)))
    expected_f = [[I, ZERO, ZERO], [add(I, product(h, g), -1), I, scale(h, -1)],
                  [scale(g, -1), ZERO, scale(I, -1)]]
    need(forward == expected_f, 'General ordered forward map')
    raw_b = [[I, scale(add(I, kr), -1), scale(k, -8)], [ZERO, I, ZERO],
             [ZERO, scale(r, -Q(1, 4)), scale(I, -1)]]
    pre_x = shear(3, 0, 2, scale(product(t, k), -8))
    pre_mode = shear(3, 2, 1, scale(r, -Q(1, 8)))
    post_mode = shear(3, 2, 1, scale(product(r, t), Q(1, 8)))
    backward = mm(post_mode, mm(raw_b, mm(pre_mode, pre_x)))
    expected_b = [[I, scale(I, -1), scale(h, -8)], [ZERO, I, ZERO],
                  [ZERO, scale(g, -Q(1, 8)), scale(I, -1)]]
    need(backward == expected_b, 'General ordered backward map')
    need(mm(post_mode, mm(raw_b, mm(pre_x, pre_mode))) != expected_b,
         'Wrong backward old-mode order control')
    inverse_f = [[I, ZERO, ZERO], [scale(I, -1), I, scale(h, -1)],
                 [scale(g, -1), ZERO, scale(I, -1)]]
    inverse_b = [[I, add(I, product(h, g), -1), scale(h, -8)], [ZERO, I, ZERO],
                 [ZERO, scale(g, -Q(1, 8)), scale(I, -1)]]
    for actual, inverse in ((forward, inverse_f), (backward, inverse_b)):
        need(mm(actual, inverse) == mm(inverse, actual) == eye(3), 'Both general inverse orders')
    need(product(g, h) == ZERO and product(h, g) != ZERO, 'Only the required feedback product is zero')
    for s in range(9):
        gs = product(token('Ninv_' + str(s)), product(token('R_' + str(s)), add(I, t, -1)))
        for j in range(9):
            hj = product(add(I, t), product(token('K_' + str(j)), token('N_' + str(j))))
            need(product(gs, hj) == ZERO, 'Every ordered stage pair annihilates')
    n1 = product(h, product(token('C1'), g))
    n2 = product(h, product(token('C2'), g))
    need(product(n1, n2) == product(n2, n1) == ZERO, 'Pairwise-zero residual products')
    need(product(add(I, n1), add(I, n2)) == add(add(I, n1), n2), 'Finite product consequence')
    need(product(add(I, add(n1, n2)), add(I, add(n1, n2), -1)) == I, 'Finite inverse consequence')
    other = token('T_other')
    need(product(add(I, t, -1), add(I, other)) != ZERO, 'Unrelated stage phases control')
    need(product(g, product(token('B'), h)) != ZERO, 'Unrestricted bridge control')
    return 81


def monomial_square():
    q, qi = token('q'), token('q-')
    square, inverse_square = product(q, q), product(qi, qi)
    qq, qii = [[q, ZERO], [ZERO, q]], [[qi, ZERO], [ZERO, qi]]
    ss = [[square, ZERO], [ZERO, square]]
    a = [[ZERO, I], [inverse_square, ZERO]]
    ai = [[ZERO, square], [I, ZERO]]
    t = [[ZERO, q], [qi, ZERO]]
    need(mm(a, qq) == mm(qq, a) == t, 'General monomial-square T')
    need(mm(t, t) == eye(2), 'General paired involution')
    need(mm(a, ai) == mm(ai, a) == eye(2), 'General monomial access inverse')
    need(mm(ss, a) == ai, 'S A equals A inverse')
    need(mm(qii, mm(ss, a)) == mm(mm(ss, a), qii) == t, 'Both physical backward conversions')
    need(product(square, square) != I, 'No Q fourth-power relation was used')
    wrong = [[ZERO, I], [square, ZERO]]
    need(mm(mm(qq, wrong), mm(qq, wrong)) != eye(2), 'Using S instead of S inverse fails in general')
    distinct_views = [[I, ZERO], [ZERO, q]]
    need(mm(distinct_views, t) != mm(t, distinct_views), 'Distinct replica views need not commute with T')

    # Q=[[0,1],[i,0]] has unit monomial square iI and Q^4=-I.
    zero, one, imaginary = (0, 0), (1, 0), (0, 1)
    def cmul(x, y):
        return x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0]
    def cmm(left, right):
        result = []
        for row in left:
            values = []
            for column in zip(*right):
                terms = [cmul(x, y) for x, y in zip(row, column)]
                values.append((sum(x[0] for x in terms), sum(x[1] for x in terms)))
            result.append(values)
        return result
    actual_q = [[zero, one], [imaginary, zero]]
    actual_square = cmm(actual_q, actual_q)
    need(actual_square == [[imaginary, zero], [zero, imaginary]], 'Concrete legal monomial square')
    need(cmm(actual_square, actual_square) == [[(-1, 0), zero], [zero, (-1, 0)]],
         'Concrete Q fourth power is not identity')


def frame_counterexample():
    def multiply(left, right):
        return [[sum(x * y for x, y in zip(row, column)) for column in zip(*right)] for row in left]
    f = [[Q(1), Q(1)], [Q(1), Q(-1)]]
    fi = [[value / 2 for value in row] for row in f]
    r = [[Q(1), Q(0)], [Q(0), Q(-1)]]
    x = [[Q(0), Q(1)], [Q(1), Q(0)]]
    need(multiply(fi, multiply(r, f)) == x != r, 'Missing productive-frame intertwiner control')


def verify(r, k):
    pairs = ordered_maps()
    monomial_square()
    frame_counterexample()
    rnorm = max(sum(abs(value) for value in row.values()) for row in r)
    knorm = max(sum(abs(value) for value in row.values()) for row in k)
    need((rnorm, knorm) == (56, 1), 'Actual scalar operator row norms')
    bounds = {'forward_prefix': 1 + rnorm,
              'forward_suffix': max(1 + rnorm, 1 + knorm * (1 + rnorm)),
              'backward_prefix': max(1 + 8 * knorm, 1 + rnorm / 8),
              'backward_suffix': 1 + rnorm / 8}
    need(bounds == {'forward_prefix': 57, 'forward_suffix': 58,
                    'backward_prefix': 9, 'backward_suffix': 8}, 'Wrapper norm bounds')
    return {
        'status': 'PASS_GENERAL_MONOMIAL_SQUARE_IDENTITIES',
        'stage_pairs': pairs, 'both_ordered_local_maps_and_inverse_orders': 'PASS',
        'assumed_line_relation': 'Q inverse cancellation only; no Q^4 relation',
        'general_hypotheses': ['Admitted raw interface and helper contract', 'Legal Q^2 and Q^-2 monomial access',
                               'F Q = Q F', 'F_mode R = R F_data and F_data K = K F_mode',
                               'One transported global T for all stages'],
        'wrapper_infinity_norm_bounds': {name: str(value) for name, value in bounds.items()},
        'negative_controls': ['wrong backward old-mode order', 'S used in place of S inverse',
                              'Q fourth power need not be identity', 'missing productive-frame intertwiner',
                              'unrelated stage phases', 'distinct replica views', 'unrestricted intervening bridge'],
        'scope': 'Exact identities and counterexamples support the proof; no arbitrary-Q native core is constructed',
    }
