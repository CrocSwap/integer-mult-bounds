"""Independent exact audit of uniform canonical three-stage rank-budget identities.

Standard library only. No author implementation is imported. Canonical query
normal forms and the scalar predecessor retain their source credits in SOURCES.
The universal proof is written in REVIEW.md; finite tests only corroborate it.
The sharp all-n completion was supplied by the root research agent and is
independently reconstructed and checked here, including every stage coefficient.
OpenAI Codex assistance. Apache-2.0. Internal author-side review, not acceptance.
"""
from argparse import ArgumentParser
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
    need(len(a) == len(b) and len(a[0]) == len(b[0]), 'Matrix addition dimensions')
    return [[x+factor*y for x, y in zip(r, s)] for r, s in zip(a, b)]


def scale(a, c):
    return [[c*x for x in row] for row in a]


def mm(a, b):
    need(len(a[0]) == len(b), 'Matrix product dimensions')
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]


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


def cols(*matrices):
    return [sum(rows, []) for rows in zip(*matrices)]


def lift(a, q):
    return [[F(a[i//q][j//q]) * (i % q == j % q)
             for j in range(len(a[0])*q)] for i in range(len(a)*q)]


def comm(a, b):
    return add(mm(a, b), mm(b, a), -1)


def canonical(n):
    u, v, r, prefixes = [], [], [], []
    p = eye(n)
    for i in range(n+1):
        col = [[F(j == i) if i < n else F((-1)**(j+1))] for j in range(n)]
        row = [[F(0 if i == j else 1 if i > j else -1) for j in range(n)]]
        u.append(col)
        v.append(row)
        r.append(mm(col, row))
        p = mm(add(eye(n), r[-1], -2), p)
        prefixes.append(p)
    return u, v, r, prefixes


def prefix_formula(n, i):
    a = [[F((-1)**j if j <= i else 0)] for j in range(n)]
    jmat = [[F(((-1 if j <= i else 1) if j == k else 0)) for k in range(n)] for j in range(n)]
    return add(jmat, mm(a, [[F(1)]*n]), 2)


def ingredients(n, i, u, v):
    a = [[F((-1)**j if j <= i else 0)] for j in range(n)]
    h = [[F(j <= i) for j in range(n)]]
    hp = [[F(j < i) for j in range(n)]]
    ht = [[F(j > i) for j in range(n)]]
    return a, h, hp, ht, add(mm(u[i], h), mm(a, v[i]))


def poly_product(a, b):
    n = len(next(iter(a.values())))
    out = {}
    for ka, x in a.items():
        for kb, y in b.items():
            key = tuple(i+j for i, j in zip(ka, kb))
            out[key] = add(out.get(key, zero(n, n)), mm(x, y))
    return {k: m for k, m in out.items() if any(any(row) for row in m)}


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


def expected_endpoint(n, q, minus=False):
    keys = [(1, 1, 1), (1, 1, 0), (0, 1, 0), (0, 0, 1)]+[(0, 0, 0)]*(n-4)
    out = {}
    for row, key in enumerate(keys):
        m = out.setdefault(key, zero(n, n))
        m[row][row] = F(-1 if minus else 1)
    return {k: lift(m, q) for k, m in out.items()}


def sharp_basis(n):
    need(n >= 4 and n % 2 == 0, 'Sharp chart domain')
    h = zero(n, n)
    first = [[1, 1, 0, 0], [1, 2, 1, 0], [1, 2, 2, 0]]
    for j, column in enumerate(first):
        for i, x in enumerate(column):
            h[i][j] = F(x)
    for j in range(3, n):
        for i, x in enumerate((0, 1, 1, 1)):
            h[i][j] = F(x)
    for j in range(3, n-1):
        h[j+1][j] = F(1)
        h[j+1][n-1] = F(-(-1)**(j+1))
    return h


def encoded(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(k): encoded(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encoded(x) for x in value]
    return value


def run():
    audits, sharps = [], []
    total_odd_pairs = total_even = total_left = total_right = 0
    for n in range(4, 21, 2):
        u, v, r, b = canonical(n)
        need(b[-1] == scale(eye(n), -1), 'Complete shortest canonical product')
        need(prefix_formula(n, n) != b[-1], 'Terminal prefix is separate, not interior formula')
        for i in range(n):
            need(b[i] == prefix_formula(n, i), 'Every literal interior prefix formula')
        Es = {}
        evens = lefts = rights = pairs = 0
        for i in range(1, n):
            a, h, hp, ht, e = ingredients(n, i, u, v)
            need(mm(b[i], u[i]) == add(scale(u[i], -1), a, 2), 'Prefix transports own column')
            if i % 2 == 0:
                A, C = cols(u[i], a), hp+ht
                need(mm(v[i], b[i]) == scale(add(hp, ht), -1), 'Even prefix row')
                need(rank(A) == rank(C) == 2 and mm(C, A) == zero(2, 2), 'Even four-q lower-bound spaces')
                evens += 1
            else:
                need(add(mm(v[i], b[i]), v[i]) == scale(h, 2), 'Odd forced row')
                A, C = cols(u[i], a), h+v[i]
                need(mm(C, A) == eye(2), 'Odd rank-two retract factorization')
                need(rank(e) == 2 and mm(e, e) == e, 'Forced odd projector')
                need(mm(e, u[i]) == u[i] and mm(v[i], e) == v[i], 'Forced projector compatible')
                need(comm(e, b[i]) == zero(n, n), 'Forced projector commutes its prefix')
                need(mm(e, u[0]) == add(u[i], a), 'Left endpoint transported column')
                need(mm(v[0], e) == add(v[i], h, -1), 'Left endpoint transported row')
                need(mm(e, u[n]) == scale(a, -1), 'Right endpoint transported column')
                need(mm(v[n], e) == h, 'Right endpoint transported row')
                A0, C0 = cols(u[0], mm(e, u[0])), v[0]+mm(v[0], e)
                An, Cn = cols(u[n], mm(e, u[n])), v[n]+mm(v[n], e)
                need(mm(C0, A0) == mm(Cn, An) == zero(2, 2), 'Both endpoint closures are zero-paired')
                need(rank(A0) == rank(C0) == (2 if i >= 3 else 1), 'Exact left far-endpoint rank domain')
                need(rank(An) == rank(Cn) == (2 if i <= n-3 else 1), 'Exact right far-endpoint rank domain')
                need(max(rank(A0), rank(An)) == 2, 'Every odd site has a full far-endpoint closure')
                lefts += int(i >= 3)
                rights += int(i <= n-3)
                Es[i] = e
        for i, ei in Es.items():
            ai = ingredients(n, i, u, v)[0]
            hi = ingredients(n, i, u, v)[1]
            for j, ej in Es.items():
                if i >= j:
                    continue
                aj = ingredients(n, j, u, v)[0]
                tj = [[F(k >= j) for k in range(n)]]
                bj = add(u[j], aj)
                need(mm(ei, ej) == scale(mm(ai, tj), -1), 'First ordered odd product')
                need(mm(ej, ei) == mm(bj, hi), 'Second ordered odd product')
                need(rank(cols(ai, bj)) == rank(tj+hi) == rank(comm(ei, ej)) == 2,
                     'Odd pair commutator rank-two factors')
                need(ai[i][0]*bj[i+1][0]-bj[i][0]*ai[i+1][0] == -1, 'Column minor is a unit')
                need(tj[0][j]*hi[0][0]-tj[0][0]*hi[0][j] == 1, 'Row minor is a unit')
                pairs += 1
        h, hi = sharp_basis(n), inverse(sharp_basis(n))
        su, sv = [mm(h, x) for x in u], [mm(x, hi) for x in v]
        sr = [mm(x, y) for x, y in zip(su, sv)]
        expected_u = [[1, 1, 0, 0], [1, 2, 1, 0], [-1, 0, 0, 1]]
        expected_v = [[1, -1, 0, 0], [1, 0, -1, 0], [1, 0, 0, 1]]
        for k, site in enumerate((0, 1, n)):
            need(su[site] == [[F(x)] for x in expected_u[k]]+zero(n-4, 1), 'Sharp selected column preserved')
            need(sv[site] == [[F(x) for x in expected_v[k]]+[F(0)]*(n-4)], 'Sharp selected row preserved')
        masks = {0: 3, 1: 7, n: 9}
        p = {i: [[F(j == k and (mask >> j & 1)) for k in range(n)] for j in range(n)]
             for i, mask in masks.items()}
        qs = (1, 2) if n <= 8 else (1,)
        for q in qs:
            SR = [lift(x, q) for x in sr]
            P = {i: lift(x, q) for i, x in p.items()}
            B = eye(n*q)
            for i in range(n+1):
                need(rank(SR[i]) == q and mm(SR[i], SR[i]) == zero(n*q, n*q), 'Every completed query paid rank and square-zero')
                B = mm(add(eye(n*q), SR[i], -2), B)
                if i in P:
                    need(mm(P[i], P[i]) == P[i], 'Sharp stage is a projector')
                    need(mm(P[i], SR[i]) == mm(SR[i], P[i]) == SR[i], 'Sharp compatibility')
                    need(comm(P[i], B) == zero(n*q, n*q), 'Sharp literal prefix commutator')
                    for other in P:
                        need(comm(P[i], P[other]) == zero(n*q, n*q), 'Sharp pairwise stage commutation')
            need(B == scale(eye(n*q), -1), 'Every original main direction returns minus identity')
            need([rank(P[i]) for i in (0, 1, n)] == [2*q, 3*q, 2*q], 'Sharp seven-q rank budget')
            calls = {i: (k, P[i]) for k, i in enumerate((0, 1, n))}
            plus, minus = stage_word(SR, calls, False), stage_word(SR, calls, True)
            need(plus == expected_endpoint(n, q) and minus == expected_endpoint(n, q, True),
                 'All coefficients of complete independent three-variable stage identity')
            sharps.append({'n': n, 'q': q, 'main_directions': n*q, 'queries': n+1,
                           'query_rank': q, 'full_sites': [0, 1, n], 'stage_ranks': [2*q, 3*q, 2*q],
                           'endpoint': ['SABC', 'SAB', 'SB', 'SC']+['S']*(n-4),
                           'polynomial_matrix_coefficients_per_character': len(plus)*(n*q)**2})
        audits.append({'n': n, 'prefixes': n, 'even_interior_sites': evens,
                       'odd_pairs': pairs, 'full_left_closures': lefts, 'full_right_closures': rights})
        total_even += evens
        total_odd_pairs += pairs
        total_left += lefts
        total_right += rights
    # Executed scope/control checks. These do not replace any uniform argument.
    u2, v2, r2, b2 = canonical(2)
    need(b2[-1] == scale(eye(2), -1) and all(comm(eye(2), x) == zero(2, 2) for x in b2),
         'n=2 has three compatible commuting rank-two stages, total6<7')
    _, _, r4, _ = canonical(4)
    h4 = sharp_basis(4)
    sr4 = [mm(mm(h4, x), inverse(h4)) for x in r4]
    ps = {i: (k, [[F(a == b and (mask >> a & 1)) for b in range(4)] for a in range(4)])
          for k, (i, mask) in enumerate(((0, 3), (1, 7), (4, 9)))}
    bad = list(sr4)
    bad[2] = zero(4, 4)
    need(stage_word(bad, ps, True) != expected_endpoint(4, 1, True), 'Removing a paid thin query breaks endpoint')
    missing_original = expected_endpoint(6, 1)
    missing_original.pop((0, 0, 0))
    _, _, rr6, _ = canonical(6)
    hh6 = sharp_basis(6)
    sr6 = [mm(mm(hh6, x), inverse(hh6)) for x in rr6]
    pp6 = {i: (k, [[F(a == b and (mask >> a & 1)) for b in range(6)] for a in range(6)])
           for k, (i, mask) in enumerate(((0, 3), (1, 7), (6, 9)))}
    need(stage_word(sr6, pp6, False) != missing_original, 'Extra original S outputs may not be dropped')
    return encoded({'status': 'PASS_INDEPENDENT_UNIFORM_SEVEN_Q_AUDIT',
                    'field_scope': 'Written proof over every field of characteristic not2; exact audit over Q only.',
                    'uniform_proof_cases': ['even_interior_rank_at_least4q', 'two_odd_extras_sum_at_leastq',
                                            'sole_odd_far_endpoint_deficit'],
                    'finite_scalar_audits': audits, 'sharp_full_endpoint_audits': sharps,
                    'totals': {'even_sites': total_even, 'odd_pairs': total_odd_pairs,
                               'full_left_closures': total_left, 'full_right_closures': total_right},
                    'sharp_basis_n4': h4, 'sharp_basis_formula_domain': 'All even n>=4, proved in REVIEW.md',
                    'controls': ['terminal_prefix_not_interior_formula', 'n2_counterexample',
                                 'missing_paid_thin_query', 'missing_original_S_outputs'],
                    'scope': 'Independent written symbolic proof review with finite exact corroboration. No native query realization, complete invoice, precision theorem, kappa or external scientific acceptance.'})


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    raw = json.dumps(run(), sort_keys=True, indent=2)+'\n'
    destination = HERE/'INDEPENDENT.json'
    if args.write:
        destination.write_text(raw)
    else:
        need(destination.read_text() == raw, 'Frozen independent finite receipt')
    print('PASS_INDEPENDENT_UNIFORM_SEVEN_Q_AUDIT')
