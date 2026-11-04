"""Independent exact finite audit of the four-block 7q proof ingredients.

No author verifier or algebra implementation is imported. The canonical
query normal form and source lineage retain their predecessor credits.
The explicit scalar sharp chart was supplied by the root research agent;
this independent implementation checks its complete multivariate endpoint.
OpenAI Codex assistance. Apache-2.0. This is internal author-side review,
not external acceptance, a native caller, or a kappa claim.
"""
from argparse import ArgumentParser
from copy import deepcopy
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import json
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def zero(m, n):
    return [[F(0) for _ in range(n)] for _ in range(m)]


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def add(a, b, factor=1):
    return [[x+factor*y for x, y in zip(r, s)] for r, s in zip(a, b)]


def mm(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


def transpose(a):
    return [list(row) for row in zip(*a)]


def inverse(a):
    n = len(a)
    m = [[F(x) for x in r]+eye(n)[i] for i, r in enumerate(a)]
    for j in range(n):
        k = next((i for i in range(j, n) if m[i][j]), None)
        need(k is not None, 'Invertible rational basis')
        m[j], m[k] = m[k], m[j]
        c = m[j][j]
        m[j] = [x/c for x in m[j]]
        for i in range(n):
            if i != j and m[i][j]:
                c = m[i][j]
                m[i] = [x-c*y for x, y in zip(m[i], m[j])]
    return [r[n:] for r in m]


def rank(a):
    a = [[F(x) for x in r] for r in a]
    k = 0
    for j in range(len(a[0])):
        p = next((i for i in range(k, len(a)) if a[i][j]), None)
        if p is None:
            continue
        a[k], a[p] = a[p], a[k]
        c = a[k][j]
        a[k] = [x/c for x in a[k]]
        for i in range(k+1, len(a)):
            if a[i][j]:
                c = a[i][j]
                a[i] = [x-c*y for x, y in zip(a[i], a[k])]
        k += 1
        if k == len(a):
            break
    return k


def lift(a, q):
    return [[F(a[i//q][j//q]) * (i % q == j % q)
             for j in range(len(a[0])*q)] for i in range(len(a)*q)]


def canonical():
    u, v, r, prefixes = [], [], [], []
    p = eye(4)
    for i in range(5):
        col = [[F(j == i) if i < 4 else F((-1)**(j+1))] for j in range(4)]
        row = [[F(0 if i == j else 1 if i > j else -1) for j in range(4)]]
        u.append(col)
        v.append(row)
        r.append(mm(col, row))
        p = mm(add(eye(4), r[-1], -2), p)
        prefixes.append(p)
    return u, v, r, prefixes


def poly_product(a, b):
    n = len(next(iter(a.values())))
    out = {}
    for ka, x in a.items():
        for kb, y in b.items():
            key = tuple(i+j for i, j in zip(ka, kb))
            out[key] = add(out.get(key, zero(n, n)), mm(x, y))
    return {k: m for k, m in out.items() if any(any(r) for r in m)}


def stage_word(queries, projectors, minus):
    n = len(queries[0])
    out = {(0, 0, 0): eye(n)}
    for site, r in enumerate(queries):
        t = add(eye(n), r, -2) if minus else eye(n)
        if site not in projectors:
            call = {(0, 0, 0): t}
        else:
            stage, p = projectors[site]
            exponent = tuple(int(j == stage) for j in range(3))
            call = {(0, 0, 0): mm(add(eye(n), p, -1), t), exponent: mm(p, t)}
        out = poly_product(call, out)
    return out


def expected_endpoint(q, minus=False):
    out = {}
    for row, key in enumerate([(1, 1, 1), (1, 1, 0), (0, 1, 0), (0, 0, 1)]):
        m = zero(4, 4)
        m[row][row] = F(-1 if minus else 1)
        out[key] = lift(m, q)
    return out


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(x) for x in value]
    return value


def run():
    u, v, r, prefixes = canonical()
    need(prefixes[-1] == add(zero(4, 4), eye(4), -1), 'Complete canonical five-query product')
    w, e2 = [[F(1)], [F(-1)], [F(0)], [F(0)]], u[2]
    need(mm(prefixes[2], e2) == add(e2, w, 2) and mm(prefixes[2], w) == add(zero(4, 1), w, -1),
         'Literal site-two closed-column identities')
    need(mm(v[2], prefixes[2]) == [[F(-1), F(-1), F(0), F(-1)]], 'Literal site-two closed-row identity')
    a = [list(row) for row in zip(e2, w)]
    a = [[x[0] for x in row] for row in a]
    c = [[F(1), F(1), F(0), F(0)], [F(0), F(0), F(0), F(1)]]
    need(rank(a) == rank(c) == 2 and mm(c, a) == zero(2, 2), 'Site-two rank-four lower-bound ingredients')
    h = [[F(x) for x in row] for row in [[1, 1, 0, -1], [1, 2, 1, 0], [0, 1, 1, 0], [0, 0, 1, 2]]]
    hi = inverse(h)
    sharp_u = [mm(h, x) for x in u]
    sharp_v = [mm(x, hi) for x in v]
    sharp_r = [mm(x, y) for x, y in zip(sharp_u, sharp_v)]
    supplied_u = [[[1], [1], [0], [0]], [[1], [2], [1], [0]], [[-1], [0], [0], [1]]]
    supplied_v = [[[1, -1, 0, 0]], [[1, 0, -1, 0]], [[1, 0, 0, 1]]]
    need([sharp_u[i] for i in (0, 1, 4)] == supplied_u and [sharp_v[i] for i in (0, 1, 4)] == supplied_v,
         'Exact supplied sharp chart, completed without altering its rows or columns')
    masks = {0: 3, 1: 7, 4: 9}
    projectors = {i: [[F(j == k and (mask >> j & 1)) for k in range(4)] for j in range(4)]
                  for i, mask in masks.items()}
    fixtures = []
    for q in (1, 2, 3):
        U, V, R = [lift(x, q) for x in u], [lift(x, q) for x in v], [lift(x, q) for x in r]
        need(rank(lift(a, q)) == rank(lift(c, q)) == 2*q and mm(lift(c, q), lift(a, q)) == zero(2*q, 2*q),
             'Coupled site-two lower-bound ingredients')
        for i in range(5):
            need(rank(R[i]) == q and mm(R[i], R[i]) == zero(4*q, 4*q), 'Every literal query rank and square-zero')
            for j in range(5):
                need(mm(V[i], U[j]) == add(zero(q, q), eye(q), 0 if i == j else 1 if i > j else -1),
                     'All canonical coupled Gram blocks')
        P = {i: lift(p, q) for i, p in projectors.items()}
        SR = [lift(x, q) for x in sharp_r]
        B = eye(4*q)
        for i in range(5):
            B = mm(add(eye(4*q), SR[i], -2), B)
            if i in P:
                need(mm(P[i], SR[i]) == mm(SR[i], P[i]) == SR[i], 'Every sharp projector compatible')
                need(mm(P[i], B) == mm(B, P[i]), 'Every sharp full-site prefix commutator')
        need(B == add(zero(4*q, 4*q), eye(4*q), -1), 'Sharp completed shortest product')
        for i in P:
            need(mm(P[i], P[i]) == P[i], 'Every sharp projector idempotent')
            for j in P:
                need(mm(P[i], P[j]) == mm(P[j], P[i]), 'Sharp projectors commute')
        t01, t04, t14 = [rank(mm(P[i], P[j])) for i, j in ((0, 1), (0, 4), (1, 4))]
        common = rank(mm(mm(P[0], P[1]), P[4]))
        union = rank([sum(rows, []) for rows in zip(P[0], P[1], P[4])])
        need([t01, t04, t14, common, union] == [2*q, q, q, q, 4*q], 'All sharp intersection inequalities attained')
        need(sum(rank(p) for p in P.values())-union == t01+t04+t14-common == 3*q,
             'Commuting inclusion-exclusion gives exact seven-q budget')
        calls = {i: (j, P[i]) for j, i in enumerate((0, 1, 4))}
        plus, minus = stage_word(SR, calls, False), stage_word(SR, calls, True)
        need(plus == expected_endpoint(q) and minus == expected_endpoint(q, True),
             'Every coefficient of the full independent three-stage Gaussian endpoint')
        fixtures.append({'q': q, 'stage_ranks': [2*q, 3*q, 2*q], 'rank_sum': 7*q,
                         'main_fields': 4*q, 'queries': 5, 'query_rank': q,
                         'independent_stage_variables': 3, 'polynomial_matrix_coefficients': len(plus)*(4*q)**2})
    # Missing a paid query cannot retain the sharp endpoint.
    bad = deepcopy(sharp_r)
    bad[2] = zero(4, 4)
    calls = {i: (j, projectors[i]) for j, i in enumerate((0, 1, 4))}
    need(stage_word(bad, calls, True) != expected_endpoint(1, True), 'Missing thin query is rejected')
    bad_calls = deepcopy(calls)
    bad_calls[1] = (1, projectors[0])
    need(stage_word(sharp_r, bad_calls, True) != expected_endpoint(1, True), 'Unfunded middle-stage field is rejected')
    missing_target = expected_endpoint(1)
    missing_target.pop((0, 0, 1))
    need(stage_word(sharp_r, calls, False) != missing_target, 'All-original output inventory is necessary')
    return encode({'status': 'PASS_INDEPENDENT_FOUR_BLOCK_SEVEN_Q_INGREDIENTS',
                   'sharp_basis': h, 'sharp_inverse': hi,
                   'sharp_completed_queries': sharp_r, 'sharp_stage_masks': masks,
                   'sharp_endpoint_masks': ['ABC', 'AB', 'B', 'C'],
                   'fixtures': fixtures,
                   'controls': ['missing_thin_query', 'unfunded_middle_stage_field', 'missing_original_target'],
                   'scope': 'Independent finite rational corroboration of written uniform proof ingredients and a sharp formal stage endpoint. No native realization, precision, complete invoice, kappa or external scientific acceptance.'})


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    result = run()
    raw = json.dumps(result, sort_keys=True, indent=2)+'\n'
    destination = HERE/'INDEPENDENT.json'
    if args.write:
        destination.write_text(raw)
    else:
        need(destination.read_text() == raw, 'Frozen independent finite receipt')
    print(result['status'])
