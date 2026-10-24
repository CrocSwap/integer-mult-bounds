#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Two-central Laurent substitution on the selected #4470 p16 invoice.

Checks, all exact (Fractions and outward-rounded rational intervals):

  1. source binding: the selected complete invoice (joint-helper-lattice RESULT.json,
     the selected record's source certificate) and its one-central coverage identity;
  2. a small complete instance: formal Laurent identities for the substitution
     Q -> Qa*Qb and the conjugation contract, plus a literal Gaussian-rational
     operator replay on F2^3 with arbitrary (dirty) inputs;
  3. the credit-rank lemma on those instances (sigma: Qb -> -Qb);
  4. moments: the selected root, the optimistic relaxation, the conjugation-charged
     profile, the native allowance, the full-credit dominance obstruction and the
     partial-credit ceiling;
  5. mutation controls that must be rejected.

usage: verify.py [--write]
JoyboyBrian, with substantial assistance from Anthropic Claude. Apache-2.0.
"""
import hashlib
import json
import random
import sys
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'complex-local-word-ceiling'))
import ceiling as CE  # noqa: E402  (stdlib exact ln/exp enclosures, pinned in SOURCES.json)

SELECTED = ROOT / 'research' / 'joint-helper-lattice' / 'RESULT.json'
SELECTED_SHA = 'c7b2388f6511c19976b337d8c8ac374610af616866a249d75dace704eb5d9e21'
V, B, NATIVE, PAIRS, THIN = 112, 8, 18, 16, 15
SEL_LO, SEL_HI = Q(3020165977, 10 ** 12), Q(30201659771, 10 ** 13)


def require(ok, why):
    if not ok:
        raise SystemExit('FAIL: ' + why)


def rejected(fn, *args):
    """True when fn raises (a control the verifier must reject)."""
    try:
        fn(*args)
    except (SystemExit, AssertionError, ValueError):
        return True
    return False


# ---------------------------------------------------------------- 1. source binding
def load_selected():
    raw = SELECTED.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SELECTED_SHA, 'selected RESULT.json hash')
    d = json.loads(raw)
    T = {int(k): v for k, v in d['targets'].items()}
    P = {int(k): v for k, v in d['paid'].items()}
    return d, T, P


def coverage_identity(d, T, P):
    """One central credit per main target: target 1+8k against paid idle 8k, 145 = 1+8*18."""
    require(d['full_calls'] == NATIVE and d['pairs'] == PAIRS and d['query_shears'] == THIN, 'controller shape')
    H = {int(k): v for k, v in d['local_helpers'].items()}
    Pl = {int(k): v for k, v in d['local_paid'].items()}
    main = {r: n for r, n in T.items() if r > 9}
    require(sum(T.values()) == d['productive_fields'] == 10928, 'productive fields')
    require(sum(P.values()) == d['paid_calls'] == 64620, 'paid calls')
    require(main == {145: 2 * V, 73: 2 * V, **{1 + B * k: 4 * V for k in range(2, 9)}}, 'main targets')
    require(all(P[B * k] == main[1 + B * k] for k in range(2, 10)), 'idle 8k matches target 1+8k')
    require(145 == 1 + B * NATIVE, 'long target is 1 + 8 * natives')
    credits = sum(main.values())
    require(credits == 2 * V * PAIRS == 3584, 'one central credit per main target')
    require(P[1] == NATIVE * Pl[1] + V * THIN, 'thin queries are rank one')
    m1 = sum(r * n for r, n in T.items()) - sum(r * n for r, n in P.items())
    h1, p1 = sum(r * n for r, n in H.items()), sum(r * n for r, n in Pl.items())
    require(m1 == 752 == NATIVE * (h1 - p1 + V + 2 * V * B) - V, 'rank-one surplus identity')
    return dict(main_targets=credits, rank_one_surplus=m1, helper_mass=h1, native_paid_mass=p1,
                identity='surplus(C=0) = 18*(H1 - P1 + V + 2VB) - V = 752')


# ---------------------------------------------------------------- 2/3. small complete instance
class L:
    """Laurent polynomial in (Qa, Qb, D) with rational coefficients."""

    def __init__(self, t=None):
        self.t = {k: v for k, v in (t or {}).items() if v}

    @staticmethod
    def mono(a=0, b=0, d=0, c=1):
        return L({(a, b, d): Q(c)})

    def __add__(s, o):
        t = dict(s.t)
        for k, v in o.t.items():
            t[k] = t.get(k, 0) + v
        return L(t)

    def __neg__(s):
        return L({k: -v for k, v in s.t.items()})

    def __sub__(s, o):
        return s + (-o)

    def __mul__(s, o):
        t = {}
        for k1, v1 in s.t.items():
            for k2, v2 in o.t.items():
                k = tuple(x + y for x, y in zip(k1, k2))
                t[k] = t.get(k, 0) + v1 * v2
        return L(t)

    def __eq__(s, o):
        return s.t == o.t

    def sigma(s):
        return L({k: (-v if k[1] % 2 else v) for k, v in s.t.items()})


ONE, ZERO = L.mono(), L()


def mm(A, Bm):
    n = len(A)
    return [[sum((A[i][k] * Bm[k][j] for k in range(n)), ZERO) for j in range(n)] for i in range(n)]


def word(*Ms):
    out = Ms[0]
    for M in Ms[1:]:
        out = mm(out, M)
    return out


def Sy(c):  # (X, Y) -> (X, Y + c X)
    return [[ONE, ZERO], [c, ONE]]


def Sx(c):  # (X, Y) -> (X + c Y, Y)
    return [[ONE, c], [ZERO, ONE]]


def diag(a, b):
    return [[a, ZERO], [ZERO, b]]


def rank2(M):
    if all(x == ZERO for row in M for x in row):
        return 0
    return 2 if not (M[0][0] * M[1][1] - M[0][1] * M[1][0]) == ZERO else 1


def sig_pert(M):
    return [[x.sigma() - x for x in row] for row in M]


def odd_entries(T):
    return sum(1 for row in T for x in row if x != ZERO and any(k[1] % 2 for k in x.t))


def formal_instance():
    Qa, Qb, D = L.mono(1), L.mono(0, 1), L.mono(0, 0, 1)
    Qai, Qbi = L.mono(-1), L.mono(0, -1)
    Q2, Q2i = Qa * Qb, Qai * Qbi
    out = {}
    # one-central swap controller and its substitution
    W1 = word(Sy(Qai), Sx(-Qa), Sy(Qai))
    require(W1 == [[ZERO, -Qa], [Qai, ZERO]], 'one-central three-shear identity')
    W2 = word(Sy(Q2i), Sx(-Q2), Sy(Q2i))
    T2 = [[ZERO, -Q2], [Q2i, ZERO]]
    require(W2 == T2, 'two-central substituted identity')
    # native contact by conjugation, Delta = diag(1, Qb)
    Dl, Dli = diag(ONE, Qb), diag(ONE, Qbi)
    F1 = mm(diag(D, D), Sy(Qai))
    require(word(Dli, F1, Dl) == mm(diag(D, D), Sy(Q2i)), 'native conjugation F_s(QaQb) = Delta^-1 F_s(Qa) Delta')
    require(word(Dli, Sx(-Qa), Dl) == Sx(-Q2), 'back shear conjugation')
    G = word(Dli, W1, Dl)
    require(G == T2, 'gauge realization of the two-central swap')
    # credit-rank lemma on both realizations (sigma: Qb -> -Qb)
    credits = odd_entries(T2)
    require(credits == 2 and rank2(sig_pert(T2)) == 2, 'two odd credits')
    subst_terms = sum(rank2(sig_pert(F)) for F in (Sy(Q2i), Sx(-Q2), Sy(Q2i)))
    gauge_terms = sum(rank2(sig_pert(F)) for F in (Dli, Dl))
    require(credits <= subst_terms == 3 and credits <= gauge_terms == 2, 'credit-rank lemma instances')
    # gauge on a diagonal target gives no credit
    Td = diag(D * Qa, D * Qai)
    require(odd_entries(word(Dli, Td, Dl)) == 0, 'diagonal targets absorb a pure gauge')
    # a longer interleaved controller with D factors: 2*p shears, product is monomial
    W3 = word(mm(diag(D, D), Sy(Q2i)), Sx(-Q2), Sy(Q2i))
    out['interleaved_monomial'] = all((W3[i][j] == ZERO) == (i == j) for i in range(2) for j in range(2))
    require(out['interleaved_monomial'], 'interleaved word stays antidiagonal')
    require(odd_entries(W3) <= 3, 'lemma on interleaved word')
    out.update(credits=credits, substitution_qb_terms=subst_terms, gauge_qb_terms=gauge_terms)
    return out


# literal operators on F2^3: axes qa = 1, qb = 2, d = 4 (bit masks); Gaussian rationals as pairs
def gmul(x, y):
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def gadd(x, y):
    return (x[0] + y[0], x[1] + y[1])


HALF_P, HALF_M = (Q(1, 2), Q(1, 2)), (Q(1, 2), Q(-1, 2))  # (1+i)/2, (1-i)/2
N3 = 8


def conv(kernel, f):
    out = [(Q(0), Q(0))] * N3
    for s, c in kernel.items():
        for x in range(N3):
            out[x ^ s] = gadd(out[x ^ s], gmul(c, f[x]))
    return out


def kmul(k1, k2):
    out = {}
    for s1, c1 in k1.items():
        for s2, c2 in k2.items():
            out[s1 ^ s2] = gadd(out.get(s1 ^ s2, (Q(0), Q(0))), gmul(c1, c2))
    return {s: c for s, c in out.items() if c != (Q(0), Q(0))}


def Cq(q):
    return {0: HALF_P, q: HALF_M}


def Xq(q):
    return {q: (Q(1), Q(0))}


def fourier_rank(kernel):
    basis = []
    for s in kernel:
        for b in basis:
            s = min(s, s ^ b)
        if s:
            basis.append(s)
    return len(basis)


def literal_instance(inverse_translation=True):
    qa, qb, dd = 1, 2, 4
    require(kmul(Cq(qa), Cq(qa)) == Xq(qa), 'C_q^2 = X_q')
    inv = (lambda q: kmul(Xq(q), Cq(q))) if inverse_translation else Cq
    require(kmul(Cq(qa), inv(qa)) == {0: (Q(1), Q(0))}, 'C_q^-1 = X_q C_q')
    Q2 = kmul(Cq(qa), Cq(qb))
    Q2i = kmul(inv(qa), inv(qb))
    require(fourier_rank(Cq(qa)) == 1 and fourier_rank(Q2) == 2, 'central ranks one and two')
    D = Cq(dd)
    rng = random.Random(20261023)
    for _ in range(6):  # arbitrary dirty inputs (Gaussian integers)
        X = [(Q(rng.randint(-9, 9)), Q(rng.randint(-9, 9))) for _ in range(N3)]
        Y = [(Q(rng.randint(-9, 9)), Q(rng.randint(-9, 9))) for _ in range(N3)]
        # three-shear word with Q = Qa Qb: S_y(Q^-1) S_x(-Q) S_y(Q^-1), rightmost first
        x, y = X, [gadd(a, b) for a, b in zip(Y, conv(Q2i, X))]
        x = [gadd(a, (-b[0], -b[1])) for a, b in zip(x, conv(Q2, y))]
        y = [gadd(a, b) for a, b in zip(y, conv(Q2i, x))]
        require(x == [(-b[0], -b[1]) for b in conv(Q2, Y)] and y == conv(Q2i, X), 'two-central swap on dirty input')
        # conjugation contract for one native-shaped factor D S_y(Qa^-1 Qb^-1)
        lhs_x, lhs_y = conv(D, X), conv(D, [gadd(a, b) for a, b in zip(Y, conv(Q2i, X))])
        y1 = conv(Cq(qb), Y)                                       # Delta
        x2, y2 = conv(D, X), conv(D, [gadd(a, b) for a, b in zip(y1, conv(inv(qa), X))])  # F_s(Qa)
        y3 = conv(inv(qb), y2)                                     # Delta^-1
        require(x2 == lhs_x and y3 == lhs_y, 'conjugated native factor on dirty input')
    return dict(columns_replayed=6, field_dimension=3, central_ranks=[1, 2])


# ---------------------------------------------------------------- 4. moments
def power(r, C):
    """Enclosure of r^(1-C) for integer r >= 1, 0 <= C <= 1/20."""
    if r == 1:
        return Q(1), Q(1)
    lo, hi = CE.ln(r)
    e = CE.exp(C * lo, C * hi)
    return CE.down(Q(r) / e[1]), CE.up(Q(r) / e[0])


def moment(prof, C):
    lo = hi = Q(0)
    for r, n in prof.items():
        a, b = power(r, C)
        lo, hi = lo + n * a, hi + n * b
    return lo, hi


def surplus(T, P, C):
    t, p = moment(T, C), moment(P, C)
    return t[0] - p[1], t[1] - p[0]


def sign(T, P, C):
    lo, hi = surplus(T, P, C)
    require(lo > 0 or hi < 0, f'enclosure does not separate at C={C}')
    return 1 if lo > 0 else -1


def bump(prof, delta):
    out = dict(prof)
    for r, n in delta.items():
        out[r] = out.get(r, 0) + n
        require(out[r] >= 0, 'negative count')
    return {r: n for r, n in out.items() if n}


def credited(T):
    """Every main target gains the second central coordinate (rank + 1)."""
    out = {}
    for r, n in T.items():
        k = r + 1 if r > 9 else r
        out[k] = out.get(k, 0) + n
    return out


def root_bracket(T, P, lo, hi, grid):
    require(sign(T, P, lo) > 0 and sign(T, P, hi) < 0, 'root bracket ends')
    while hi - lo > grid:
        mid = Q(int((lo + hi) / 2 / grid)) * grid
        mid = lo + grid if mid <= lo else mid
        if sign(T, P, mid) > 0:
            lo = mid
        else:
            hi = mid
    return lo, hi


def charged(credits, qb_terms):
    """Credit-rank lemma: every second-coordinate credit needs a q_b-touching rank-one term."""
    require(credits <= qb_terms, f'{credits} credits but only {qb_terms} q_b-touching terms')
    return True


def dominates(targets, paid):
    """Sorted main targets dominate the same number of largest paid ranks, elementwise."""
    tl = sorted((r for r, n in targets.items() for _ in range(n)), reverse=True)
    pl = sorted((r for r, n in paid.items() for _ in range(n)), reverse=True)[:len(tl)]
    require(len(pl) == len(tl) and all(a >= b for a, b in zip(tl, pl)) and tl != pl, 'dominance')
    return True


def g(r, C):
    a, b = power(r + 1, C)
    if r == 0:
        return a, b
    c, d = power(r, C)
    return a - d, b - c


def partial_gain_upper(main, P, C):
    """Max over credited subsets S of sum_S g(R) - (cheapest charge for |S| q_b terms)."""
    tl = sorted((r for r, n in main.items() for _ in range(n)))            # small targets first
    pl = sorted((r for r, n in P.items() for _ in range(n)), reverse=True)  # large requests first
    best = cur = Q(0)
    cache = {}
    for R, r in zip(tl, pl):
        key = (R, r)
        if key not in cache:
            cache[key] = g(R, C)[1] - g(r, C)[0]
        cur += cache[key]
        best = max(best, cur)
    return best, sum(1 for R, r in zip(tl, pl) if R < r)


def moments(T, P):
    out = {}
    require(sign(T, P, SEL_LO) > 0 and sign(T, P, SEL_HI) < 0, 'selected root bracket')
    out['selected_root'] = [str(SEL_LO), str(SEL_HI)]
    main = {r: n for r, n in T.items() if r > 9}
    credits = sum(main.values())
    T2 = credited(T)
    # (i) optimistic relaxation: natives unchanged, thin queries rank 2
    P_opt = bump(P, {1: -V * THIN, 2: V * THIN})
    # the thin shears supply V*THIN q_b terms; the lemma charges the rest to the natives
    require(rejected(charged, credits, V * THIN), 'thin shears alone cannot pay every credit')
    lo, hi = root_bracket(T2, P_opt, Q(1, 100), Q(11, 1000), Q(1, 10 ** 9))
    out['optimistic_root'] = [str(lo), str(hi)]
    out['optimistic_ratio_vs_selected'] = float(lo / SEL_HI)
    out['native_qb_terms_needed'] = credits - V * THIN
    # (ii) conjugation-charged: two rank-one q_b requests per port per native stage
    P_conj = bump(P_opt, {1: 2 * V * NATIVE})
    charged(credits, V * THIN + 2 * V * NATIVE)
    m1 = sum(r * n for r, n in T2.items()) - sum(r * n for r, n in P_conj.items())
    require(m1 == 752 + credits - V * THIN - 2 * V * NATIVE == -1376, 'conjugation mass')
    require(sign(T2, P_conj, SEL_LO) < 0, 'conjugation profile loses at the selected root')
    out['conjugation_rank_one_surplus'] = m1
    # (iii) allowance: extra rank-one units on top of the optimistic profile at the selected root end
    def ok(e):
        return sign(T2, bump(P_opt, {1: e}), SEL_HI) > 0
    lo_e, hi_e = 0, 2 * V * NATIVE
    require(ok(lo_e) and not ok(hi_e), 'allowance bracket')
    while hi_e - lo_e > 1:
        mid = (lo_e + hi_e) // 2
        lo_e, hi_e = (mid, hi_e) if ok(mid) else (lo_e, mid)
    out['allowance_rank_one_units'] = lo_e
    out['allowance_per_native_call'] = str(Q(lo_e, NATIVE))
    out['native_terms_fit_allowance_as_rank_one'] = (credits - V * THIN) <= lo_e
    # (iv) full-credit dominance: any incremental realization is strictly below selected
    dominates(main, P)
    gain, cost = Q(0), Q(0)
    tl = sorted((r for r, n in main.items() for _ in range(n)), reverse=True)
    pl = sorted((r for r, n in P.items() for _ in range(n)), reverse=True)[:len(tl)]
    for C in (SEL_LO, Q(1, 1000), Q(1, 100)):
        acc = Q(0)
        cache = {}
        for R, r in zip(tl, pl):
            if (R, r) not in cache:
                cache[(R, r)] = g(R, C)[1] - g(r, C)[0]
            acc += cache[(R, r)]
        require(acc < 0, f'full-credit gain below cheapest charge at C={C}')
        if C == SEL_LO:
            gain = acc
    out['full_credit_net_upper_at_selected_root'] = float(gain)
    # (v) partial-credit ceiling: surplus_sel + best partial net gain
    def part_sign(C):
        best, _ = partial_gain_upper(main, P, C)
        lo_s, hi_s = surplus(T, P, C)
        if lo_s > 0:
            return 1
        require(hi_s + best < 0, f'partial ceiling does not separate at C={C}')
        return -1
    best_sel, pairs_gaining = partial_gain_upper(main, P, SEL_HI)
    require(best_sel > 0, 'partial credits can gain a little (positive control)')
    lo_c, hi_c = SEL_LO, Q(3040, 10 ** 6)
    require(part_sign(hi_c) < 0, 'partial ceiling end')
    grid = Q(1, 10 ** 9)
    while hi_c - lo_c > grid:
        mid = Q(int((lo_c + hi_c) / 2 / grid)) * grid
        mid = lo_c + grid if mid <= lo_c else mid
        try:
            s = part_sign(mid)
        except SystemExit:
            s = 1
        lo_c, hi_c = (mid, hi_c) if s > 0 else (lo_c, mid)
    out['partial_credit_ceiling'] = str(hi_c)
    out['partial_best_net_gain_at_selected_root'] = float(best_sel)
    out['partial_pairs_with_target_below_charge'] = pairs_gaining
    return out, T2, P_opt


# ---------------------------------------------------------------- 5. controls
def controls(d, T, P, T2, P_opt, allowance):
    main = {r: n for r, n in T.items() if r > 9}
    c = {}
    c['inverse_without_translation'] = rejected(literal_instance, False)
    c['uncharged_second_coordinate'] = rejected(charged, sum(main.values()), 0)
    # crediting only the smallest main targets is the partial-credit loophole: no dominance
    c['partial_credit_breaks_dominance'] = rejected(dominates, {17: 4 * V}, P)
    c['allowance_plus_one_fails'] = sign(T2, bump(P_opt, {1: allowance + 1}), SEL_HI) < 0
    c['allowance_holds'] = sign(T2, bump(P_opt, {1: allowance}), SEL_HI) > 0
    bad = dict(T)
    bad[145] -= 1
    bad[146] = 1
    c['mutated_main_target_rejected'] = rejected(coverage_identity, d, bad, P)
    D, Qb, Qbi = L.mono(0, 0, 1), L.mono(0, 1), L.mono(0, -1)
    native = mm(diag(D, D), Sy(L.mono(-1)))
    wrong = word(diag(Qbi, ONE), native, diag(Qb, ONE))  # gauge on X instead of Y
    c['wrong_gauge_orientation_rejected'] = wrong != mm(diag(D, D), Sy(L.mono(-1, -1)))
    require(all(c.values()), 'control failed: ' + json.dumps(c))
    return c


def main():
    d, T, P = load_selected()
    res = {'status': 'PASS_TWO_CENTRAL_LAURENT_COVERAGE', 'base_commit': 'cef4b52f2a59009865bf8eabde1be3f159063703',
           'selected_source_sha256': SELECTED_SHA}
    res['coverage_identity'] = coverage_identity(d, T, P)
    res['formal_instance'] = formal_instance()
    res['literal_instance'] = literal_instance()
    mres, T2, P_opt = moments(T, P)
    res['moments'] = mres
    res['controls'] = controls(d, T, P, T2, P_opt, mres['allowance_rank_one_units'])
    path = HERE / 'RESULT.json'
    text = json.dumps(res, indent=2, sort_keys=True) + '\n'
    if '--write' in sys.argv[1:]:
        path.write_text(text)
    else:
        require(path.exists() and path.read_text() == text, 'RESULT.json differs from the recomputed certificate')
    print(json.dumps(res['moments'], indent=2, sort_keys=True))
    print('PASS_TWO_CENTRAL_LAURENT_COVERAGE')


if __name__ == '__main__':
    main()
