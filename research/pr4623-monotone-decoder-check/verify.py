#!/usr/bin/env python3
"""Independent check of three parts of PR #4623 (dillona, head fd5d3be1).

(A) Monotone extension of the C=.006 (complex) / C=.007 (BIT) negative Jensen
    bounds to every larger saving C in [cutoff, 1], with my own certified
    exp/log interval arithmetic (no nth-root grid, no import from #4623).
(B) The copied-input X decoder: exact correction identity, forced matrices
    M=I+J, N=-J (rank p-1), and the cumulative all-concave-moment certificate.
(T) Sanity: the idle-free controller emitted from the source chronology is
    the stated triangular Q^-1 U / Q V matrix, with degree-(p-1) border,
    diagonal monomial limit and unit determinant prod D_s^2.

Standard library only.  Prepared by lm1909 with Claude Code (Claude Opus 5.5)
assistance.  Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
import ast
import hashlib
import json
import sys
from pathlib import Path

PREC = 120          # outward rounding grid 2^-PREC for interval endpoints


def need(ok, msg):
    if not ok:
        raise SystemExit("FAIL: " + msg)


# ---------------------------------------------------------------- intervals
def down(x):
    s = 1 << PREC
    return F((x.numerator * s) // x.denominator, s)


def up(x):
    s = 1 << PREC
    return F(-((-x.numerator * s) // x.denominator), s)


def atanh_bounds(z):
    """Enclosure of atanh(z) for rational 0 <= z <= 1/3."""
    need(0 <= z <= F(1, 3), "atanh argument range")
    if z == 0:
        return F(0), F(0)
    total, term, k = F(0), z, 0
    z2 = z * z
    while True:
        total += term / (2 * k + 1)
        k += 1
        term *= z2
        tail = term / ((2 * k + 1) * (1 - z2))      # remainder bound
        if tail < F(1, 1 << (PREC + 8)):
            return down(total), up(total + tail)


def ln_bounds(r):
    """Enclosure of ln r for an integer r >= 1 via r = 2^k m, m in [1,2)."""
    need(isinstance(r, int) and r >= 1, "ln of positive integer")
    if r == 1:
        return F(0), F(0)
    k = r.bit_length() - 1
    m = F(r, 1 << k)
    l2 = atanh_bounds(F(1, 3))                       # ln 2 = 2 atanh(1/3)
    lm = atanh_bounds((m - 1) / (m + 1))
    return down(2 * k * l2[0] + 2 * lm[0]), up(2 * k * l2[1] + 2 * lm[1])


def exp_bounds_point(x, lower):
    """One-sided bound of exp(x) for rational 0 <= x <= 64."""
    need(0 <= x <= 64, "exp argument range")
    s = 10                                           # exp(x) = exp(x/1024)^1024
    y = x / (1 << s)
    total, term, k = F(1), F(1), 0
    while True:
        k += 1
        term = term * y / k
        total += term
        # tail sum_{j>k} y^j/j! <= term*y/(k+1) / (1-y)  (y <= 1/16)
        tail = term * y / (k + 1) / (1 - y)
        if tail < F(1, 1 << (PREC + 16)):
            break
    val = down(total) if lower else up(total + tail)
    for _ in range(s):
        val = down(val * val) if lower else up(val * val)
    return val


def pow_bounds(r, t):
    """Certified enclosure of r^t for integer r >= 1 and rational t in [0,1]."""
    t = F(t)
    need(0 <= t <= 1, "t in [0,1]")
    if r == 1 or t == 0:
        return F(1), F(1)
    lo, hi = ln_bounds(r)
    return exp_bounds_point(t * lo, True), exp_bounds_point(t * hi, False)


def iadd(*xs):
    return sum(x[0] for x in xs), sum(x[1] for x in xs)


def imul(x, c):
    c = F(c)
    a, b = x[0] * c, x[1] * c
    return (min(a, b), max(a, b))


def moment(profile, t):
    return (F(0), F(0)) if not profile else iadd(*(imul(pow_bounds(r, t), n) for r, n in profile.items()))


# ---------------------------------------------------------------- inputs
def load_profiles(root):
    cx = json.loads((root / "research/joint-helper-lattice/RESULT.json").read_text())
    helpers = {int(r): n for r, n in cx["local_helpers"].items()}
    paid = {int(r): n for r, n in cx["local_paid"].items()}
    bi = json.loads((root / "research/query-thinned-controllers/BIT-CONTROLLER.json").read_text())["invoice"]
    k = bi["thick_calls"]
    tg = Counter({int(r): n for r, n in bi["targets"].items()})
    tg.subtract({int(r): n for r, n in bi["main"].items()})
    pd = Counter({int(r): n for r, n in bi["paid"].items()})
    pd.subtract({int(r): n for r, n in bi["whole_idle"].items()})
    pd[1] -= bi["thin_queries"]
    need(all(n >= 0 and n % k == 0 for n in list(tg.values()) + list(pd.values())), "BIT per-call division exact")
    bh = {r: n // k for r, n in tg.items() if n}
    bp = {r: n // k for r, n in pd.items() if n}
    return {"complex": dict(b=8, v=112, H=helpers, P=paid, cutoff=F(3, 500)),
            "BIT": dict(b=7, v=111, H=bh, P=bp, cutoff=F(7, 1000))}


def signed(prof):
    s = Counter(prof["H"])
    s.subtract(prof["P"])
    return {r: n for r, n in s.items() if n}


# ---------------------------------------------------------------- (A)
def J_terms(prof, p):
    """Signed (rank, coefficient) list of J_p(t) = sum c * rank^t.

    The main term has rational base 1+b+2b/p, kept separately."""
    b, v = prof["b"], prof["v"]
    terms = [(F(r), (p + 2) * n) for r, n in signed(prof).items()]
    terms.append((F(1), -v * (p - 1)))
    terms.append((F(1 + b) + F(2 * b, p), 2 * v * p))
    return terms


def separator_interval(prof):
    """Maximal open interval of sigma for which every summand of J_p(t)/sigma^t
    is nondecreasing in t for every p>=1: c*(r-sigma) >= 0 termwise."""
    b = prof["b"]
    s = signed(prof)
    neg_max = max([r for r, n in s.items() if n < 0] + [1])     # thin query rank 1 is negative
    pos_min = min([r for r, n in s.items() if n > 0] + [1 + b])  # inf_p (1+b+2b/p) = 1+b, not attained
    return F(neg_max), F(pos_min)


def check_monotone_lemma(prof, sigma):
    for p in list(range(1, 300)) + [10**3, 10**6]:
        for r, c in J_terms(prof, p):
            # d/dt [c (r/sigma)^t] = c ln(r/sigma) (r/sigma)^t has the sign of c*(r-sigma)
            if c * (r - sigma) < 0:
                return False, p, r, c
    return True, None, None, None


def tangent_AB(prof, t):
    b, v = prof["b"], prof["v"]
    h = iadd(moment(prof["H"], t), imul(moment(prof["P"], t), -1))
    u = pow_bounds(1 + b, t)
    A = iadd(h, (F(-v), F(-v)), imul(u, 2 * v))
    B = iadd(imul(h, 2), (F(v), F(v)), imul(u, F(4 * v * b) * t / (1 + b)))
    return h, A, B


def J_direct(prof, p, t):
    """Certified enclosure of the unlinearised J_p(t), main base (p(1+b)+2b)/p as a ratio of integer powers.
    Consistency evidence only; the all-p claim uses the tangent bound plus the monotone lemma."""
    b, v = prof["b"], prof["v"]
    h = iadd(moment(prof["H"], t), imul(moment(prof["P"], t), -1))
    num, den = pow_bounds(p * (1 + b) + 2 * b, t), pow_bounds(p, t)
    main = (num[0] / den[1], num[1] / den[0])
    return iadd(imul(h, p + 2), (F(-v * (p - 1)),) * 2, imul(main, 2 * v * p))


def threshold_bracket(prof, lo=F(1, 1000), hi=F(1, 50), steps=14):
    """Certified bracket for the saving C* at which A(1-C) changes sign
    (A = lim_p J_p/p).  A(t)/sigma^t is nondecreasing in t (same separator lemma, sigma<=1+b),
    so A changes sign at most once and sign bisection is sound."""
    for _ in range(steps):
        mid = (lo + hi) / 2
        A = tangent_AB(prof, 1 - mid)[1]
        if A[1] < 0:
            hi = mid
        elif A[0] > 0:
            lo = mid
        else:
            break
    return lo, hi


# ---------------------------------------------------------------- Laurent algebra for (T) and (B)
def padd(a, b, c=1):
    out = dict(a)
    for k, x in b.items():
        out[k] = out.get(k, 0) + c * x
        if out[k] == 0:
            del out[k]
    return out


def pmono(a, e, c=1):
    return {tuple(x + y for x, y in zip(k, e)): c * x for k, x in a.items()}


def pmul(a, b):
    out = {}
    for k1, x in a.items():
        for k2, y in b.items():
            k = tuple(i + j for i, j in zip(k1, k2))
            out[k] = out.get(k, 0) + x * y
            if out[k] == 0:
                del out[k]
    return out


def emit_idle_free(p, thin=True, flip_backward_sign=False):
    """My own replay of the source chronology (complex_controller_factor.controller,
    read by hand), with every whole IDLE deleted and, if thin, stages 2,4,..,2p-2
    replaced by the unscaled shear.  Variables: (q, D_0..D_2p).  Rows = outputs."""
    n, W = 2 * p, 2 * p + 2
    Z = (0,) * W
    one = lambda i: tuple(int(k == i) for k in range(W))
    M = [[{Z: 1} if i == j else {} for j in range(n)] for i in range(n)]
    thick = {0, 2 * p} | set(range(1, 2 * p, 2))

    def row_add(dst, src, mono, c):
        M[dst] = [padd(a, pmono(s, mono, c)) for a, s in zip(M[dst], M[src])]

    def row_scale(r, mono):
        M[r] = [pmono(a, mono) for a in M[r]]

    def stage(s, j, backward):
        X, Y = 2 * j, 2 * j + 1
        if backward:     # B_s = D_s S_x(-Q): X += -Q Y
            qe = tuple(x for x in one(0))
            row_add(X, Y, qe, 1 if flip_backward_sign else -1)
        else:            # F_s = D_s S_y(Q^-1): Y += Q^-1 X
            row_add(Y, X, tuple(-x for x in one(0)), 1)
        if s in thick or not thin:
            row_scale(X, one(1 + s))
            row_scale(Y, one(1 + s))

    def bridge(dst, src, c):
        row_add(2 * dst, 2 * src, Z, c)
        row_add(2 * src + 1, 2 * dst + 1, Z, -c)

    stage(0, 0, False)
    for j in range(p):
        stage(2 * j + 1, j, True)
        if j < p - 1:
            bridge(j, j + 1, 1)
        stage(2 * j + 2, j, False)
        if j < p - 1:
            bridge(j, j + 1, -1)
    for j in reversed(range(p - 1)):
        bridge(j + 1, j, 1)
    for j in range(p):
        M[2 * j], M[2 * j + 1] = M[2 * j + 1], [pmono(a, Z, -1) for a in M[2 * j]]
    return M


def closed_form(p):
    """The PR's stated Q^-1 U (X block) and Q V (Y block), built from the text."""
    W = 2 * p + 2
    if p == 1:
        groups = [[0, 1, 2]]
    else:
        groups = [[0, 1]] + [[2 * j + 1] for j in range(1, p - 1)] + [[2 * p - 1, 2 * p]]
    d = [{tuple([0] + [int(s in g) for s in range(2 * p + 1)]): 1} for g in groups]
    one = {(0,) * W: 1}
    qm = (-1,) + (0,) * (W - 1)
    qp = (1,) + (0,) * (W - 1)
    M = [[{} for _ in range(2 * p)] for _ in range(2 * p)]
    for i in range(p):
        for j in range(p):
            if i == j:
                u = d[i]
                vv = d[i]
            elif i < j:
                u = pmono(padd(one, d[j], -1), (0,) * W, (-1) ** (j - i - 1))
                vv = {}
            else:
                u = {}
                prod = one
                for k in range(j, i):
                    prod = pmul(prod, d[k])
                vv = pmono(pmul(prod, padd(one, d[i], -1)), (0,) * W, (-1) ** (i - j - 1))
            M[2 * i][2 * j] = pmono(u, qm)
            M[2 * i + 1][2 * j + 1] = pmono(vv, qp)
    return M, d


def border_check(M, p):
    """Conjugate by E(eps)=diag(eps^w), w(X_j)=j, w(Y_j)=p-1-j.  Return degree set and B(0)."""
    w = [j if par == 0 else p - 1 - j for j in range(p) for par in (0, 1)]
    degs = set()
    limit = {}
    for i in range(2 * p):
        for j in range(2 * p):
            if M[i][j]:
                e = w[j] - w[i]
                if e < 0 or (i != j and e == 0):
                    return None, None
                degs.add(e)
                if e == 0:
                    limit[i] = M[i][j]
    return degs, limit


def det_monomial_check(M, p, d):
    """Block-triangular: det = prod of diagonal entries.  Verify each diagonal is a unit monomial
    and the product is prod over thick stages D_s^2 (q cancels)."""
    W = 2 * p + 2
    tot = [0] * W
    for i in range(2 * p):
        e = M[i][i]
        if len(e) != 1 or list(e.values())[0] != 1:
            return False
        tot = [a + b for a, b in zip(tot, list(e)[0])]
    thick = {0, 2 * p} | set(range(1, 2 * p, 2))
    want = [0] + [2 * int(s in thick) for s in range(2 * p + 1)]
    return tot == want


def source_emitter(root, p):
    """Literal source chronology: extract only the three pure functions of the pinned
    complex_controller_factor.py (no source imports executed), run with keep=0 (every
    whole IDLE deleted) and set the exponent of each thin stage 2,4,..,2p-2 to zero."""
    path = root / "research/kappa-rebuild/bit/complex_controller_factor.py"
    tree = ast.parse(path.read_text())
    body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in {"plus", "monomial_times", "controller"}]
    need(len(body) == 3, "three pure source functions")
    space = {"Q": F}
    exec(compile(ast.Module(body=body, type_ignores=[]), str(path), "exec"), space)
    coeff, events, idle = space["controller"](p, 0)
    need(not any(e[0] == "IDLE" for e in events), "no whole IDLE event retained")
    thick = {0, 2 * p} | set(range(1, 2 * p, 2))
    M = [[{} for _ in range(2 * p)] for _ in range(2 * p)]
    for term, mat in coeff.items():
        key = (term[0],) + tuple(x if s in thick else 0 for s, x in enumerate(term[1:]))
        for i, row in enumerate(mat):
            for j, val in enumerate(row):
                if val:
                    M[i][j] = padd(M[i][j], {key: val})
    return M, len(idle)


# ---------------------------------------------------------------- (B) decoder
def mat_rank(A):
    A = [[F(x) for x in row] for row in A]
    r = 0
    for c in range(len(A[0]) if A else 0):
        piv = next((i for i in range(r, len(A)) if A[i][c]), None)
        if piv is None:
            continue
        A[r], A[piv] = A[piv], A[r]
        for i in range(len(A)):
            if i != r and A[i][c]:
                f = A[i][c] / A[r][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        r += 1
    return r


def decoder_identity(p, use_raw=True):
    """z = (I+J) X' - Q^-1 J x equals Q^-1 D x, using the EMITTED X block (thin, idle-free)."""
    M = emit_idle_free(p)
    _, d = closed_form(p)
    W = 2 * p + 2
    qm = (-1,) + (0,) * (W - 1)
    for i in range(p):
        for j in range(p):
            z = dict(M[2 * i][2 * j])
            if i + 1 < p:
                z = padd(z, M[2 * (i + 1)][2 * j])
                if j == i + 1 and use_raw:
                    z = padd(z, {qm: 1}, -1)
            want = pmono(d[i], qm) if i == j else {}
            if z != want:
                return False
    return True


def forced_decoder(p):
    """Solve M(I-S)=I, N=-MS exactly; return (M==I+J, N==-J, rank N)."""
    S = [[F((-1) ** (j - i - 1)) if j > i else F(0) for j in range(p)] for i in range(p)]
    ImS = [[F(i == j) - S[i][j] for j in range(p)] for i in range(p)]
    # inverse of unit upper triangular ImS by back substitution
    inv = [[F(0)] * p for _ in range(p)]
    for c in range(p):
        for i in reversed(range(p)):
            s = F(i == c) - sum(ImS[i][k] * inv[k][c] for k in range(i + 1, p))
            inv[i][c] = s / ImS[i][i]
    IJ = [[F(i == j or j == i + 1) for j in range(p)] for i in range(p)]
    N = [[-sum(inv[i][k] * S[k][j] for k in range(p)) for j in range(p)] for i in range(p)]
    negJ = [[F(-1) if j == i + 1 else F(0) for j in range(p)] for i in range(p)]
    return inv == IJ, N == negJ, mat_rank(N)


def decoder_profiles(prof, p):
    b, v = prof["b"], prof["v"]
    T = Counter({r: (p + 2) * n for r, n in prof["H"].items()})
    P = Counter({r: (p + 2) * n for r, n in prof["P"].items()})
    P[1] += v * (p - 1)               # paid thin queries
    P[1] += v * (p - 1)               # fresh X-correction Q jobs (forced rank p-1 per port)
    T[1 + 2 * b] += 4 * v
    T[1 + b] += 2 * v * (p - 2)
    return T, P


def cumulative(T, P):
    ranks = sorted(set(T) | set(P))
    out, acc = {}, 0
    for r in range(1, max(ranks) + 1):
        acc += r * (P.get(r, 0) - T.get(r, 0))
        out[r] = acc
    return out


# ---------------------------------------------------------------- main
def run(root):
    profs = load_profiles(root)
    res = {"A": {}, "B": {}, "T": {}}
    expect = {"complex": ({1: -2237, 2: -388, 3: -494, 4: -119, 5: -36, 7: 7, 8: 39, 9: 326}, F(5), F(7)),
              "BIT": ({1: -1323, 2: -1342, 3: -79, 4: -44, 5: -102, 6: -11, 7: -19, 8: 439}, F(7), F(8))}
    for name, prof in profs.items():
        s = signed(prof)
        lo, hi = separator_interval(prof)
        need(s == expect[name][0], name + " signed local profile pinned")
        need((lo, hi) == expect[name][1:], name + " separator interval")
        sigma = (lo + hi) / 2                     # 6 complex, 15/2 BIT; any sigma in (lo,hi] works
        ok, *bad = check_monotone_lemma(prof, sigma)
        need(ok, f"{name}: monotone lemma fails at p={bad[0]} rank={bad[1]} coeff={bad[2]}")
        need(lo < hi, name + " nonempty separator interval")
        t0 = 1 - prof["cutoff"]
        h, A, B = tangent_AB(prof, t0)
        need(A[1] < 0 and B[1] < 0, name + ": tangent bounds negative at cutoff")
        # every p: J_p(t0) <= p*A + B_J < 0, and J_p(t)/sigma^t nondecreasing => J_p(t)<0 for t<=t0.
        # spot evaluation of the unlinearised J_p on [0,t0] as a consistency check (not needed for proof)
        for p in (1, 2, 3, 16, 64, 1000):
            for tt in (F(0), F(1, 2), F(9, 10), t0):
                jd = J_direct(prof, p, tt)
                need(jd[1] < 0, f"{name}: direct J_{p}({tt}) negative")
                if tt == t0:
                    bound = iadd(imul(A, p), B)
                    need(jd[1] <= bound[1] + F(1, 10**20), f"{name}: tangent dominates J_{p}")
        c_lo, c_hi = threshold_bracket(prof)
        # Sharpened all-p exclusion: certify A<0 and B_J<0 at a rounded-up saving, and A>0 just below
        # (so J_p(t) > 0 for all large p there: the Jensen/tangent method cannot reach below it).
        sharp_ex, sharp_open = {"complex": (F(5687, 10**6), F(5685, 10**6)),
                                "BIT": (F(6512, 10**6), F(6510, 10**6))}[name]
        _, A2, B2 = tangent_AB(prof, 1 - sharp_ex)
        need(A2[1] < 0 and B2[1] < 0, name + ": sharpened exclusion certified")
        A3 = tangent_AB(prof, 1 - sharp_open)[1]
        need(A3[0] > 0, name + ": asymptotic slope positive just below sharpened cutoff")
        res["A"][name] = {"separator_interval_open_lo_closed_hi": [str(lo), str(hi)], "sigma_used": str(sigma),
                          "cutoff": str(prof["cutoff"]), "A_upper": float(A[1]), "B_J_upper": float(B[1]),
                          "A_width": float(A[1] - A[0]),
                          "asymptotic_A_sign_change_bracket": [float(c_lo), float(c_hi)],
                          "sharpened_excluded_saving": str(sharp_ex), "sharpened_A_upper": float(A2[1]),
                          "sharpened_B_J_upper": float(B2[1]),
                          "A_positive_at_saving": str(sharp_open), "A_lower_there": float(A3[0])}
        # (B) decoder all-moment certificate
        cums = {}
        for p in (2, 3):
            T, P = decoder_profiles(prof, p)
            cums[p] = cumulative(T, P)
        base, slope = cums[2], {r: cums[3][r] - cums[2][r] for r in cums[2]}
        for p in (4, 5, 16, 64, 1000):
            T, P = decoder_profiles(prof, p)
            c = cumulative(T, P)
            need(all(c[r] == base[r] + slope[r] * (p - 2) for r in c), name + " affine cumulative")
        need(all(base[r] > 0 and slope[r] > 0 for r in base), name + " all cumulative base/slope positive")
        R = max(base)
        need(base[R] + slope[R] * (16 - 2) == (64 * 16 - 96 if name == "complex" else 63 * 16 - 96),
             name + " total rank deficit 64p-96 / 63p-96")
        # direct certified evaluation at a few t, p
        for p in (2, 16):
            T, P = decoder_profiles(prof, p)
            for tt in (F(1, 100), F(1, 2), F(1)):
                diff = iadd(moment(P, tt), imul(moment(T, tt), -1))
                need(diff[0] > 0, f"{name}: decoder paid exceeds target at p={p},t={tt}")
        res["B"][name] = {"cumulative_base_p2": base, "cumulative_slope": slope}
    # (T) controller sanity, p=1..7
    for p in range(1, 8):
        E = emit_idle_free(p)
        C, d = closed_form(p)
        need(E == C, f"emitted idle-free controller equals closed form at p={p}")
        S, n_idle = source_emitter(root, p)
        need(S == E, f"literal source emitter (idles deleted, thin D=1) equals my replay at p={p}")
        degs, limit = border_check(E, p)
        need(degs is not None and max(degs) == p - 1 and degs == set(range(p)), f"border degree exactly p-1 at p={p}")
        need(len(limit) == 2 * p, f"diagonal limit full at p={p}")
        need(det_monomial_check(E, p, d), f"determinant prod D_s^2 at p={p}")
        # A(1) = I
        need(all(sum(E[i][j].values()) == (i == j) for i in range(2 * p) for j in range(2 * p)), f"A(1)=I at p={p}")
        if p >= 2:
            ok = decoder_identity(p)
            need(ok, f"decoder identity at p={p}")
            fm, fn, rk = forced_decoder(p)
            need(fm and fn and rk == p - 1, f"forced decoder M=I+J, N=-J, rank p-1 at p={p}")
        res["T"][p] = "ok"
    return res


def controls(root):
    rejected = []
    # 1. wrong backward sign in the emitter must disagree with the closed form
    rejected.append(("flipped_backward_sign", emit_idle_free(3, flip_backward_sign=True) != closed_form(3)[0]))
    # 2. thick (unthinned) stages: thin stage D's leak in -> not the stated formula
    rejected.append(("no_thinning", emit_idle_free(3, thin=False) != closed_form(3)[0]))
    # 3. reversed weights give negative border degrees
    E = emit_idle_free(3)
    w = [-(j if par == 0 else 2 - j) for j in range(3) for par in (0, 1)]
    rejected.append(("reversed_weights", any(E[i][j] and w[j] - w[i] < 0 for i in range(6) for j in range(6))))
    # 4. a paid rank-9 complex job breaks the separator lemma (negative term above any sigma<=7)
    profs = load_profiles(root)
    pr = dict(profs["complex"]); pr["P"] = dict(pr["P"]); pr["P"][9] = 400          # net rank-9 term 326-400 < 0, above sigma
    rejected.append(("paid_rank9_breaks_separator", check_monotone_lemma(pr, F(6))[0] is False))
    # 5. certification below the true threshold must fail (non-vacuous checker): complex C=.005, BIT C=.006
    for name, c in (("complex", F(1, 200)), ("BIT", F(3, 500))):
        A = tangent_AB(profs[name], 1 - c)[1]
        rejected.append((f"{name}_C={c}_not_certified", A[0] > 0))
    # 6. forgetting the fresh decoder queries leaves some cumulative threshold negative
    T, P = decoder_profiles(profs["complex"], 16)
    P[1] -= 112 * 15
    rejected.append(("decoder_without_fresh_queries", min(cumulative(T, P).values()) < 0))
    # 7. dropping the copied raw-input term -Q^-1 J x breaks the exact decoder identity
    rejected.append(("decoder_without_raw_input_term", not decoder_identity(3, use_raw=False)))
    for name, ok in rejected:
        need(ok, "control not rejected: " + name)
    return [n for n, _ in rejected]


def check_inputs(root, here, override=None):
    pins = json.loads((here / "SOURCES.json").read_text())
    for row in pins["files"]:
        if row["usage"] != "input":
            continue
        data = (root / row["path"]).read_bytes() if override is None or row["path"] not in override else override[row["path"]]
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            return False
    return True


if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else here.parents[1]
    need(check_inputs(root, here), "live input bytes match SOURCES.json pins")
    tampered = (root / "research/joint-helper-lattice/RESULT.json").read_bytes().replace(b"326", b"327", 1)
    need(not check_inputs(root, here, {"research/joint-helper-lattice/RESULT.json": tampered}),
         "control: tampered input bytes rejected")
    out = run(root)
    out["controls_rejected"] = ["tampered_input_sha256"] + controls(root)
    out["status"] = "PASS_PR4623_MONOTONE_DECODER_CONTROLLER_CHECK"
    print(json.dumps(out, indent=1, default=str))
