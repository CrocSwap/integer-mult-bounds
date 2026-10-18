#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Two-call P112 batch floor under isometric cross-call label charts.

Exact integer / F2 / Gaussian-integer arithmetic, standard library only,
read-only. Predecessor checkers are never imported or executed; the one
predecessor data file used (p112-single-lift reference geometry) is
hash-pinned in SOURCES.json and only compared against an independent
construction.

Prepared by thakrarsagar with substantial AI assistance from Claude
(Anthropic, Claude Opus 5.5). Apache-2.0.
"""
import hashlib
import itertools
import json
import random
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SAMPLE_SEED = 20261015
SAMPLE_WORDS = 160
MAX_WORD_LENGTH = 16
DIRECT_RANK_WORDS = 24
CROSS_FORM_SAMPLES = 48


class CheckFailure(Exception):
    pass


def require(ok, message):
    if not ok:
        raise CheckFailure(message)


# ---------------------------------------------------------------- F2 helpers
def popparity(x):
    return bin(x).count("1") & 1


def f2_basis(rows):
    basis = {}
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in basis:
                v ^= basis[h]
            else:
                basis[h] = v
                break
    return list(basis.values())


def f2_rank(rows):
    return len(f2_basis(rows))


# ------------------------------------------------------ exact rational rank
def rational_rank(rows):
    m = [[Fraction(x) for x in r] for r in rows]
    rank, ncols = 0, (len(m[0]) if m else 0)
    for col in range(ncols):
        piv = next((r for r in range(rank, len(m)) if m[r][col] != 0), None)
        if piv is None:
            continue
        m[rank], m[piv] = m[piv], m[rank]
        for r in range(len(m)):
            if r != rank and m[r][col] != 0:
                f = m[r][col] / m[rank][col]
                m[r] = [a - f * b for a, b in zip(m[r], m[rank])]
        rank += 1
    return rank


# ---------------------------------------------------------- geometry (P112)
def build_geometry():
    """Norm-4 shell of {x in Z^8 : x mod 2 in RM(1,3)} (= sqrt(2) E8) in
    frame-adapted Hamming coordinates; coordinates indexed by F2^3."""
    planes = set()
    for a in range(1, 8):
        for c in (0, 1):
            planes.add(tuple(p for p in range(8) if popparity(a & p) == c))
    planes = sorted(planes)
    require(len(planes) == 14 and all(len(p) == 4 for p in planes), "affine planes")
    live = []
    for plane in planes:
        for signs in itertools.product((1, -1), repeat=3):
            row = [0] * 8
            row[plane[0]] = 1
            for p, s in zip(plane[1:], signs):
                row[p] = s
            live.append(tuple(row))
    frame = [tuple(2 if k == j else 0 for k in range(8)) for j in range(8)]
    require(len(live) == 112, "112 live lines")
    allv = live + frame
    for x in allv:
        require(sum(t * t for t in x) == 4, "norm four")
    roots = set()
    for x in allv:
        roots.add(x)
        roots.add(tuple(-t for t in x))
    require(len(roots) == 240, "240 roots")
    for x in allv:  # reflections permute the 240 roots
        for y in allv:
            d = sum(a * b for a, b in zip(x, y))
            require(d % 2 == 0, "even dots")
            require(tuple(b - (d // 2) * a for a, b in zip(x, y)) in roots, "reflection closure")
    for j in range(8):
        for k in range(8):
            s = sum(r[j] * r[k] for r in live)
            require(s == (56 if j == k else 0), "X^T X = 56 I")
    return live, frame


def line_key(x):
    first = next(t for t in x if t != 0)
    return tuple(t if first > 0 else -t for t in x)


def doubled_e8_lines():
    out = set()
    for i, j in itertools.combinations(range(8), 2):
        for si in (2, -2):
            for sj in (2, -2):
                v = [0] * 8
                v[i], v[j] = si, sj
                out.add(line_key(tuple(v)))
    for signs in itertools.product((1, -1), repeat=8):
        if signs.count(-1) % 2 == 0:
            out.add(line_key(signs))
    require(len(out) == 120, "doubled E8 lines")
    return out


def cross_check_reference(live):
    """Compare with the pinned predecessor data file (data only, no code)."""
    data = json.loads((ROOT / "research/p112-single-lift/reference-geometry.json").read_text())
    ref_x = [tuple(r) for r in data["X"]]
    ref_q = [tuple(r) for r in data["roots"]]
    ref_f = [tuple(r) for r in data["frame"]]
    require(len(ref_x) == 112 and len(ref_q) == 112 and len(ref_f) == 8, "reference shape")
    require({line_key(r) for r in ref_x} == {line_key(r) for r in live}, "same live lines")
    require({line_key(r) for r in ref_q + ref_f} == doubled_e8_lines(), "reference is doubled E8")
    n = 0
    for i in range(112):
        for j in range(112):
            dq = sum(a * b for a, b in zip(ref_q[i], ref_q[j]))
            dx = sum(a * b for a, b in zip(ref_x[i], ref_x[j]))
            require(dq == 2 * dx, "scaled Gram")
            n += 1
    return n


class Form:
    def __init__(self, gmask):
        self.g = gmask

    def gy(self, y):
        out = 0
        for k in range(9):
            if popparity(self.g[k] & y):
                out |= 1 << k
        return out

    def b(self, x, y):
        return popparity(x & self.gy(y))


def labels(live, frame):
    """B_ij = 1 + x_i.x_j/2 mod 2 on all 120 lines; coordinates of each
    label in a basis of nine live label rows; Gram form G."""
    allv = live + frame
    n = len(allv)
    rows = []
    for x in allv:
        r = 0
        for j, y in enumerate(allv):
            d = sum(a * b for a, b in zip(x, y))
            if (1 + d // 2) % 2:
                r |= 1 << j
        rows.append(r)
    for i in range(n):
        for j in range(n):
            require(((rows[i] >> j) & 1) == ((rows[j] >> i) & 1), "B symmetric")
    require(f2_rank(rows) == 9, "rank B = 9")
    basis_idx, reduced = [], {}
    for i in range(112):
        v, comb = rows[i], 0
        while v:
            h = v.bit_length() - 1
            if h in reduced:
                v ^= reduced[h][0]
                comb ^= reduced[h][1]
            else:
                break
        if v:
            reduced[v.bit_length() - 1] = (v, comb ^ (1 << len(basis_idx)))
            basis_idx.append(i)
    require(len(basis_idx) == 9, "live labels span V")
    coords = []
    for i in range(n):
        v, comb = rows[i], 0
        while v:
            h = v.bit_length() - 1
            require(h in reduced, "label outside span")
            v ^= reduced[h][0]
            comb ^= reduced[h][1]
        coords.append(comb)
    for i in range(n):
        acc = 0
        for k in range(9):
            if (coords[i] >> k) & 1:
                acc ^= rows[basis_idx[k]]
        require(acc == rows[i], "label coordinates")
    gmask = [sum(((rows[basis_idx[k]] >> basis_idx[l]) & 1) << l for l in range(9))
             for k in range(9)]
    require(f2_rank(gmask) == 9, "Gram nonsingular")
    form = Form(gmask)
    for i in range(n):
        for j in range(n):
            require(form.b(coords[i], coords[j]) == ((rows[i] >> j) & 1), "B = c^T G c")
    return coords, form


# ------------------------------------------------------------ charts
def apply(phi, x):
    out = 0
    for k in range(9):
        if (x >> k) & 1:
            out ^= phi[k]
    return out


def transvection(form, u):
    return [(1 << k) ^ (u if form.b(1 << k, u) else 0) for k in range(9)]


def compose(phi, psi):  # phi after psi
    return [apply(phi, psi[k]) for k in range(9)]


def is_isometry(form, phi):
    if f2_rank(phi) != 9:
        return False
    return all(form.b(phi[k], phi[l]) == form.b(1 << k, 1 << l)
               for k in range(9) for l in range(9))


IDENTITY = [1 << k for k in range(9)]


# --------------------------------------------------- finite support premises
def support_premises(live, coords, form):
    lab = coords[:112]
    hist, exceptional = {}, []
    for h in range(1, 512):
        rows = [live[i] for i in range(112) if popparity(h & lab[i])]
        r = rational_rank(rows)
        hist[r] = hist.get(r, 0) + 1
        if r < 8:
            require(r == 7, "deficient rank is seven")
            ker = [j for j in range(8) if all(x[j] == 0 for x in rows)]
            require(len(ker) == 1, "kernel is one coordinate line")
            exceptional.append(ker[0])
    require(hist == {8: 503, 7: 8}, "complement rank histogram")
    require(sorted(exceptional) == list(range(8)), "each frame line once")
    supports = [[i for i in range(112) if live[i][j] != 0] for j in range(8)]
    perp = []
    for j in range(8):
        require(len(supports[j]) == 56, "56 roots")
        span = [lab[i] for i in supports[j]]
        require(f2_rank(span) == 8, "exceptional span 8")
        vs = [v for v in range(1, 512) if all(form.b(v, x) == 0 for x in span)]
        require(len(vs) == 1, "unique perp vector")
        perp.append(vs[0])
    for i in range(8):  # common chart: all 64 ordered pairs rank 8 (direct)
        for j in range(8):
            mat = [sum(form.b(lab[s], lab[t]) << n for n, t in enumerate(supports[j]))
                   for s in supports[i]]
            require(f2_rank(mat) == 8, "common-chart pair rank 8")
            require(form.b(perp[i], perp[j]) == 1, "b(v_i, v_j) = 1")
    return hist, supports, perp


# --------------------------------------------------------- Gaussian integers
ZERO = (0, 0)


def gmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def gadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def gconj(a):
    return (a[0], -a[1])


def block_column(live, coef):
    """coef: 16 Gaussian ints (call 0 coords 0..7, call 1 coords 0..7);
    returns the 224-entry column of (I_2 tensor X) coef."""
    out = []
    for s in range(2):
        for x in live:
            acc = ZERO
            for k in range(8):
                if x[k]:
                    acc = gadd(acc, gmul((x[k], 0), coef[8 * s + k]))
            out.append(acc)
    return out


def exact_check(live, terms, target, hermitian=False, diagonal_only=False):
    """All-pairs 224x224 check of sum_j D_j T_j^T (ordinary transpose unless
    hermitian=True) against the blocks target[s][t] * X X^T."""
    cols = [(block_column(live, a), block_column(live, c)) for a, c in terms]
    n = 0
    for r in range(224):
        s, i = divmod(r, 112)
        for q in range(224):
            t, k = divmod(q, 112)
            if diagonal_only and s != t:
                continue
            acc = ZERO
            for d, e in cols:
                if d[r] != ZERO and e[q] != ZERO:
                    acc = gadd(acc, gmul(d[r], gconj(e[q]) if hermitian else e[q]))
            want = target[s][t] * sum(a * b for a, b in zip(live[i], live[k]))
            if acc != (want, 0):
                return False, n
            n += 1
    return True, n


# ------------------------------------------------------------ term pricing
def union_pairing(form, model):
    """Pairing on V (+) V (call-0 label in bits 0..8, call-1 in 9..17).
    ('chart', phi): b(x0 + phi x1, y0 + phi y1), i.e. call 1 re-charted by
    phi and call identity forgotten; ('beta0',): b(x0,y0) + b(x1,y1)."""
    def pair(x, y):
        x0, x1, y0, y1 = x & 511, x >> 9, y & 511, y >> 9
        if model[0] == "chart":
            phi = model[1]
            return form.b(x0 ^ apply(phi, x1), y0 ^ apply(phi, y1))
        if model[0] == "cross":  # general cross forms beta01, beta10 (Form objects)
            return form.b(x0, y0) ^ form.b(x1, y1) ^ model[1].b(x0, y1) ^ model[2].b(x1, y0)
        require(model[0] == "beta0", "model")
        return form.b(x0, y0) ^ form.b(x1, y1)
    return pair


def term_cost(live, coords, pair, a, c):
    sets = []
    for col in (block_column(live, a), block_column(live, c)):
        sets.append([coords[r % 112] << (9 * (r // 112)) for r in range(224) if col[r] != ZERO])
    require(sets[0] and sets[1], "inactive term priced")
    u, w = f2_basis(sets[0]), f2_basis(sets[1])
    return f2_rank([sum(pair(x, y) << n for n, y in enumerate(w)) for x in u])


def term_cost_direct(live, coords, form, phi, a, c):
    """Same price in the single-V chart model from the full union-support
    pairing matrix (no span reduction): independent cross-check."""
    labs = []
    for col in (block_column(live, a), block_column(live, c)):
        labs.append([coords[r] if r < 112 else apply(phi, coords[r - 112])
                     for r in range(224) if col[r] != ZERO])
    return f2_rank([sum(form.b(x, y) << n for n, y in enumerate(labs[1])) for x in labs[0]])


def unit(k, scale=(1, 0)):
    v = [ZERO] * 16
    v[k] = scale
    return v


def vec(entries):
    v = [ZERO] * 16
    for k, s in entries:
        v[k] = (s, 0)
    return v


def classify(a, c):
    sa = {k // 8 for k in range(16) if a[k] != ZERO}
    sc = {k // 8 for k in range(16) if c[k] != ZERO}
    if sa & sc:
        return "N"
    return "P01" if sa == {0} else "P10"


def real_block_rank(terms, kind):
    rows = [[0] * 8 for _ in range(8)]
    sa, sc = (0, 8) if kind == "P01" else (8, 0)
    for a, c in terms:
        if classify(a, c) != kind:
            continue
        for i in range(8):
            for j in range(8):
                p = gmul(a[sa + i], c[sc + j])
                require(p[1] == 0, "real fixture")
                rows[i][j] += p[0]
    return rational_rank(rows)


# ------------------------------------------------------------- decoders
def standard_decoder():
    return [(unit(k), unit(k)) for k in range(16)]


def one_cross_decoder(p, q):
    """I_16 = Q_N + [[0, e_p e_q^T], [0, 0]]: the 16 unit rows of Q_N plus
    one pure cross term (call-0 reader coord p, call-1 source coord q)."""
    terms = []
    for k in range(16):
        c = vec([(p, 1), (8 + q, -1)]) if k == p else unit(k)
        terms.append((unit(k), c))
    terms.append((unit(p), unit(8 + q)))
    return terms


def two_cross_decoder(p, q):
    """R01 = e_p e_q^T and R10 = e_q e_p^T; Q_N has rank 15."""
    terms = [(unit(k), unit(k)) for k in range(16) if k not in (p, 8 + q)]
    w = vec([(p, 1), (8 + q, -1)])
    terms.append((w, w))
    terms.append((unit(p), unit(8 + q)))
    terms.append((unit(8 + q), unit(p)))
    return terms


def schur_decoder():
    """R01 = R10 = I: Q_N = [[I,-I],[-I,I]] (rank 8) plus 16 pure cross terms."""
    terms = []
    for k in range(8):
        w = vec([(k, 1), (8 + k, -1)])
        terms.append((w, w))
    for k in range(8):
        terms.append((unit(k), unit(8 + k)))
        terms.append((unit(8 + k), unit(k)))
    return terms


def schur_generic_decoder():
    """Q_N = [I; -I] M M^{-1} [I, -I] with M the upper-triangular all-ones
    matrix (M^{-1} = I - superdiagonal), so the eight both-call terms have
    non-coordinate columns; plus 16 coordinate pure cross terms."""
    terms = []
    for k in range(8):
        a = vec([(i, 1) for i in range(k + 1)] + [(8 + i, -1) for i in range(k + 1)])
        col = [(k, 1)] + ([(k + 1, -1)] if k < 7 else [])
        c = vec(col + [(8 + i, -t) for i, t in col])
        terms.append((a, c))
    for k in range(8):
        terms.append((unit(k), unit(8 + k)))
        terms.append((unit(8 + k), unit(k)))
    return terms


def call_spans(live, coords, coef):
    col = block_column(live, coef)
    return [f2_basis([coords[r - 112 * s] for r in range(112 * s, 112 * s + 112)
                      if col[r] != ZERO]) for s in range(2)]


def form_rank(beta, u, w):
    return f2_rank([sum(beta.b(x, y) << n for n, y in enumerate(w)) for x in u])


def prop_d_bound(live, coords, terms, costs, b01, b10):
    """Proposition D: total >= 128 - sum_double min(8, rho01 + rho10) + sum_pure cost."""
    bound = 128
    for (a, c), cost in zip(terms, costs):
        kind = classify(a, c)
        if kind != "N":
            bound += cost
            continue
        ua, wc = call_spans(live, coords, a), call_spans(live, coords, c)
        if ua[0] and wc[0] and ua[1] and wc[1]:
            rho = form_rank(b01, ua[0], wc[1]) + form_rank(b10, ua[1], wc[0])
            require(cost >= max(8, 16 - rho), "double-term price bound")
            bound -= min(8, rho)
    return bound


def batch_cost(live, coords, pair, terms):
    return [term_cost(live, coords, pair, a, c) for a, c in terms]


def lower_bound_report(terms, costs, c_min):
    kinds = [classify(a, c) for a, c in terms]
    r01, r10 = real_block_rank(terms, "P01"), real_block_rank(terms, "P10")
    require(kinds.count("N") >= 16 - min(r01, r10), "Schur count")
    require(all(x >= 8 for x, k in zip(costs, kinds) if k == "N"), "non-pure >= 8")
    require(all(x >= c_min for x, k in zip(costs, kinds) if k != "N"), "pure cross >= c")
    bound = 8 * (16 - min(r01, r10)) + c_min * (r01 + r10)
    require(sum(costs) >= bound >= 128, "batch bound")
    return {"N": kinds.count("N"), "P01": kinds.count("P01"), "P10": kinds.count("P10"),
            "r01": r01, "r10": r10, "bound": bound, "cost": sum(costs),
            "term_costs": sorted(costs)}


# ---------------------------------------------------------------- main
def run():
    out = {}
    live, frame = build_geometry()
    out["reference_scaled_gram_entries"] = cross_check_reference(live)
    coords, form = labels(live, frame)
    hist, supports, perp = support_premises(live, coords, form)
    out["complement_rank_histogram"] = {str(k): v for k, v in sorted(hist.items())}

    w0s = [w for w in range(512) if all(form.b(v, v) == form.b(v, w) for v in range(512))]
    require(len(w0s) == 1, "characteristic vector")
    w0 = w0s[0]
    out["b_w0_w0"] = form.b(w0, w0)
    out["b_v_w0"] = [form.b(v, w0) for v in perp]
    isotropic = [u for u in range(1, 512) if form.b(u, u) == 0]
    out["isotropic_nonzero"] = len(isotropic)
    out["perp_span_dim"] = f2_rank(perp)

    def zero_pairs(phi):
        return {(i, j) for i in range(8) for j in range(8)
                if form.b(perp[i], apply(phi, perp[j])) == 0}

    def direct_pair_rank(phi, i, j):
        cols = [apply(phi, coords[t]) for t in supports[j]]
        return f2_rank([sum(form.b(coords[s], y) << n for n, y in enumerate(cols))
                        for s in supports[i]])

    single_hist = {}
    for u in isotropic:
        phi = transvection(form, u)
        require(is_isometry(form, phi), "isotropic transvection is an isometry")
        s = sum(form.b(v, u) for v in perp)
        z = len(zero_pairs(phi))
        require(z == s * s, "single transvection count s^2")
        single_hist[z] = single_hist.get(z, 0) + 1
    out["single_transvection_rank7_pair_histogram"] = {
        str(k): v for k, v in sorted(single_hist.items())}

    u = next(u for u in isotropic if form.b(perp[0], u) and form.b(perp[1], u))
    target_phi = transvection(form, u)
    require(is_isometry(form, target_phi), "targeted isometry")
    out["targeted_u"] = u
    out["targeted_pair_rank_0_1"] = direct_pair_rank(target_phi, 0, 1)
    require(out["targeted_pair_rank_0_1"] == 7, "targeted rank-7 pair")
    out["targeted_rank7_pairs"] = len(zero_pairs(target_phi))

    rng = random.Random(SAMPLE_SEED)
    sample = [IDENTITY]
    for _ in range(SAMPLE_WORDS):
        phi = IDENTITY
        for _ in range(rng.randint(1, MAX_WORD_LENGTH)):
            phi = compose(transvection(form, rng.choice(isotropic)), phi)
        sample.append(phi)
    sample.append(target_phi)
    shist, direct_checked = {}, 0
    for idx, phi in enumerate(sample):
        require(is_isometry(form, phi), "sampled chart is an isometry")
        require(apply(phi, w0) == w0, "isometry fixes w0")
        zp = zero_pairs(phi)
        shist[len(zp)] = shist.get(len(zp), 0) + 1
        if idx < DIRECT_RANK_WORDS or idx == len(sample) - 1:
            for i in range(8):
                for j in range(8):
                    r = direct_pair_rank(phi, i, j)
                    require(r == (7 if (i, j) in zp else 8), "pure cross rank formula")
                    direct_checked += 1
    out["sample_charts"] = len(sample)
    out["sample_rank7_pair_histogram"] = {str(k): v for k, v in sorted(shist.items())}
    out["direct_pure_cross_ranks_checked"] = direct_checked
    out["sample_digest"] = hashlib.sha256(json.dumps(sample).encode()).hexdigest()

    target = [[1, 0], [0, 1]]
    fixtures = {}
    std = standard_decoder()
    ok, entries = exact_check(live, std, target)
    require(ok and entries == 224 * 224, "standard decoder exact")
    for idx, phi in enumerate(sample):
        costs = batch_cost(live, coords, union_pairing(form, ("chart", phi)), std)
        require(sum(costs) == 128, "standard decoder costs 128 under every sampled chart")
        if idx < 4 or idx == len(sample) - 1:
            for (a, c), cost in zip(std, costs):
                require(term_cost_direct(live, coords, form, phi, a, c) == cost, "direct price")
    fixtures["standard_cost_all_sampled_charts"] = 128

    pair_t = union_pairing(form, ("chart", target_phi))
    one = one_cross_decoder(0, 1)
    ok, n = exact_check(live, one, target)
    require(ok, "one-cross decoder exact")
    entries += n
    costs = batch_cost(live, coords, pair_t, one)
    for (a, c), cost in zip(one, costs):
        require(term_cost_direct(live, coords, form, target_phi, a, c) == cost, "direct price")
    rep = lower_bound_report(one, costs, 7)
    require(rep["term_costs"] == [7] + [8] * 16 and rep["bound"] == rep["cost"] == 135,
            "one-cross fixture 135, bound tight")
    fixtures["one_cross_targeted_chart"] = rep
    costs_id = batch_cost(live, coords, union_pairing(form, ("chart", IDENTITY)), one)
    fixtures["one_cross_common_chart_cost"] = sum(costs_id)
    require(sum(costs_id) == 136, "one-cross common chart 136")

    two = two_cross_decoder(0, 1)
    ok, n = exact_check(live, two, target)
    require(ok, "two-cross decoder exact")
    entries += n
    rep = lower_bound_report(two, batch_cost(live, coords, pair_t, two), 7)
    require(rep["N"] == 15 and rep["bound"] == 134 and rep["cost"] == 135, "two-cross fixture")
    fixtures["two_cross_targeted_chart"] = rep

    sch = schur_decoder()
    ok, n = exact_check(live, sch, target)
    require(ok, "Schur-pattern decoder exact")
    entries += n
    fixtures["schur_targeted_chart"] = lower_bound_report(
        sch, batch_cost(live, coords, pair_t, sch), 7)
    costs_b0 = batch_cost(live, coords, union_pairing(form, ("beta0",)), sch)
    require(sorted(costs_b0) == [0] * 16 + [16] * 8, "beta0 Schur term costs")
    fixtures["schur_beta0_cost"] = sum(costs_b0)
    require(sum(costs_b0) == 128, "beta0 Schur = 128")
    fixtures["standard_beta0_cost"] = sum(
        batch_cost(live, coords, union_pairing(form, ("beta0",)), std))
    require(fixtures["standard_beta0_cost"] == 128, "beta0 standard = 128")
    out["fixtures"] = fixtures
    out["full_matrix_entries_checked"] = entries

    # Secondary V(+)V model: general cross forms. Same chart expressed as
    # cross forms beta01 = G phi, beta10 = phi^T G must give identical prices.
    def form_matrix(f):  # rows of M with b(x, y) = x^T M y
        return [f.gy(1 << l) for l in range(9)]

    def transpose(rows):
        return [sum(((rows[l] >> k) & 1) << l for l in range(9)) for k in range(9)]

    g_cols = form_matrix(form)  # column l of G as a mask over k
    g_rows = transpose(g_cols)
    g_phi = Form(transpose([form.gy(target_phi[l]) for l in range(9)]))
    phit_g = Form([sum(form.b(target_phi[k], 1 << l) << l for l in range(9)) for k in range(9)])
    for k in range(9):
        for l in range(9):
            require(g_phi.b(1 << k, 1 << l) == form.b(1 << k, target_phi[l]), "G phi")
            require(phit_g.b(1 << k, 1 << l) == form.b(target_phi[k], 1 << l), "phi^T G")
    require(g_rows == form.g, "Gram transpose")
    pair_x = union_pairing(form, ("cross", g_phi, phit_g))
    for terms in (one, two, sch):
        require(batch_cost(live, coords, pair_x, terms) == batch_cost(live, coords, pair_t, terms),
                "chart = cross-form model")
    hbases = [f2_basis([coords[i] for i in supports[k]]) for k in range(8)]

    def cross_min(beta):
        return min(f2_rank([sum(beta.b(x, y) << n for n, y in enumerate(hbases[j]))
                            for x in hbases[i]]) for i in range(8) for j in range(8))

    rng2 = random.Random(SAMPLE_SEED + 1)
    forms = [("zero", Form([0] * 9), Form([0] * 9)), ("target_chart", g_phi, phit_g)]
    for t in range(CROSS_FORM_SAMPLES):
        forms.append(("random", Form([rng2.getrandbits(9) for _ in range(9)]),
                      Form([rng2.getrandbits(9) for _ in range(9)])))
    gen = schur_generic_decoder()
    ok, n = exact_check(live, gen, target)
    require(ok, "generic Schur-pattern decoder exact")
    entries += n
    out["full_matrix_entries_checked"] = entries
    families = {"schur": sch, "one_cross": one, "two_cross": two, "schur_generic": gen}
    xmin, xsuff, dmin = {}, 0, None
    for name, b01, b10 in forms:
        pair = union_pairing(form, ("cross", b01, b10))
        c01, c10 = cross_min(b01), cross_min(b10)
        for fam, terms in families.items():
            costs = batch_cost(live, coords, pair, terms)
            cost = sum(costs)
            require(cost >= 128, "cross-form family below 128 (would be a model-sharpness hit)")
            xmin[fam] = min(xmin.get(fam, cost), cost)
            bound = prop_d_bound(live, coords, terms, costs, b01, b10)
            require(cost >= bound, "Proposition D bound")
            dmin = bound if dmin is None else min(dmin, bound)
        if c01 + c10 >= 8:
            xsuff += 1
    fixtures["schur_generic_targeted_chart"] = lower_bound_report(
        gen, batch_cost(live, coords, pair_t, gen), 7)
    fixtures["schur_generic_beta0_cost"] = sum(
        batch_cost(live, coords, union_pairing(form, ("beta0",)), gen))
    out["cross_form_search"] = {
        "domain": "4 exact decoder families x (beta=0, targeted chart, %d seeded random "
                  "cross-form pairs)" % CROSS_FORM_SAMPLES,
        "seed": SAMPLE_SEED + 1, "forms": len(forms), "min_cost_by_family": xmin,
        "forms_meeting_sufficient_condition": xsuff, "min_proposition_d_bound": dmin,
        "status": "finite search; no sub-128 decoder found; not an impossibility theorem"}
    require(dmin == 128, "Proposition D minimum over the finite search")

    controls = []

    def must_fail(name, fn):
        try:
            fn()
        except CheckFailure:
            controls.append(name)
            return
        raise CheckFailure("negative control did not fail: " + name)

    # Over F2 the anisotropic "transvection" x -> x + b(x,a)a is singular
    # (it sends a to 0), so it is not a chart at all; record that as a
    # positive fact.  The isometry controls use an invertible shear instead,
    # so that they exercise the pairing-preservation branch of is_isometry.
    aniso = next(v for v in range(1, 512) if form.b(v, v) == 1)
    require(f2_rank(transvection(form, aniso)) == 8, "anisotropic map is singular")
    bad_phi = next(phi for phi in ([(1 << m) ^ ((1 << l) if m == k else 0) for m in range(9)]
                                   for k in range(9) for l in range(9) if k != l)
                   if any(form.b(phi[r], phi[c]) != form.b(1 << r, 1 << c)
                          for r in range(9) for c in range(9)))
    require(f2_rank(bad_phi) == 9, "shear is invertible")
    must_fail("invertible non-isometric shear rejected by pairing check",
              lambda: require(is_isometry(form, bad_phi), "isometry"))
    must_fail("invertible non-isometric chart changes call-2 own pairing",
              lambda: require(all(form.b(apply(bad_phi, coords[i]), apply(bad_phi, coords[j]))
                                  == form.b(coords[i], coords[j])
                                  for i in range(112) for j in range(112)), "own pairing"))
    ones = [(vec([(k, 1), (8 + k, 1)]), vec([(k, 1), (8 + k, 1)])) for k in range(8)]
    require(exact_check(live, ones, [[1, 1], [1, 1]])[0], "all-ones decoder exact for own C")
    must_fail("all-ones endpoint mutation rejected against I_2",
              lambda: require(exact_check(live, ones, target)[0], "endpoint"))
    herm = [(unit(k, (0, 1)), unit(k, (0, 1))) for k in range(16)]
    require(exact_check(live, herm, target, hermitian=True)[0], "Hermitian control")
    must_fail("Hermitian-only decoder rejected under ordinary transpose",
              lambda: require(exact_check(live, herm, target)[0], "ordinary transpose"))
    good_i = [(unit(k, (0, 1)), unit(k, (0, -1))) for k in range(16)]
    require(exact_check(live, good_i, target)[0], "(i, -i) decoder exact")
    crosstalk = std + [(unit(0), unit(9))]
    require(exact_check(live, crosstalk, target, diagonal_only=True)[0], "crosstalk diag")
    must_fail("cross-call crosstalk rejected by all-pairs check",
              lambda: require(exact_check(live, crosstalk, target)[0], "crosstalk"))
    must_fail("corrupted rank claim (targeted pair claimed rank 8)",
              lambda: require(direct_pair_rank(target_phi, 0, 1) == 8, "rank claim"))
    must_fail("corrupted fixture cost (one-cross claimed 127)",
              lambda: require(sum(batch_cost(live, coords, pair_t, one)) == 127, "cost claim"))
    out["negative_controls"] = controls
    return out


EXPECTED_RECEIPT_SHA256 = "92d4555bb78cbcc7b0945391416ea1a5df4fafaabc356e735406c96844bbf2bd"


def main():
    out = run()
    text = json.dumps(out, sort_keys=True, indent=1)
    digest = hashlib.sha256(text.encode()).hexdigest()
    print(text)
    print("receipt_sha256", digest)
    if EXPECTED_RECEIPT_SHA256 is not None and digest != EXPECTED_RECEIPT_SHA256:
        raise SystemExit("FAIL: receipt digest mismatch")
    print("PASS_P112_BATCH_CHART_CHANGE")


if __name__ == "__main__":
    try:
        main()
    except CheckFailure as exc:
        raise SystemExit("FAIL: " + str(exc))
