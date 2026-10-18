#!/usr/bin/env python3
"""Exact checker for the balanced (5a,5b) ten-call four-SWAP residual.

Model (see research/coordinate-cnot-register-bound/README.md and the pinned
predecessors): R = F2[GL_2(F2)], paid calls I + ([g]+1) N with g in {a,b} the
two coordinate CNOTs, N = u v^T a binary rank-one idempotent (v^T u = 1),
free scalar GL_r(F2) mixing normalizable to identity by augmentation, complete
formal boundary T = diag([S],...,[S]) on r target registers.

This program derives the exact J^3 augmentation-layer equations

    prod_i (1 + eps_i) = 1 + sum eps_i + sum_{i<j} eps_i eps_j   (mod J^3 M_r)

(same-label pairs vanish since ([a]+1)^2 = ([b]+1)^2 = 0), checks them and the
full formal equality against control words, and runs a bounded seeded search
for a balanced (5 a-labels, 5 b-labels) ten-call word at r = 4 realizing
T = diag([S],[S],[S],[S]).  Exact bit arithmetic throughout; stdlib only.
No new kappa; the selected frontier is unchanged.
"""
import argparse
import itertools
import json
import pathlib
import random
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent

# ---------------------------------------------------------------- group GL2(F2)
def m2(row0, row1):
    """2x2 binary matrix as int: row p in bits 2p, 2p+1 (c0 low bit)."""
    return row0 | (row1 << 2)


def mm2(x, y):
    """Product of two encoded 2x2 binary matrices over F2."""
    return m2(_row_mult(x & 3, y), _row_mult((x >> 2) & 3, y))


def _row_mult(row, mat):
    out = 0
    for c in (0, 1):
        if (row >> c) & 1:
            out ^= (mat >> (2 * c)) & 3
    return out


def det2(x):
    a = x & 1
    b = (x >> 1) & 1
    c = (x >> 2) & 1
    d = (x >> 3) & 1
    return (a & d) ^ (b & c)


def build():
    global ELEMS, IDX, GPROD, RMUL, A, B, S, IDE, GP1, BP1, SP1, PAB, QBA
    global J1, J2, J3, ECHELON, RED, DIMS
    ELEMS = [x for x in range(16) if det2(x)]
    assert len(ELEMS) == 6
    IDX = {g: i for i, g in enumerate(ELEMS)}
    GPROD = [[0] * 6 for _ in range(6)]
    for i, g in enumerate(ELEMS):
        for j, h in enumerate(ELEMS):
            GPROD[i][j] = 1 << IDX[mm2(g, h)]
    RMUL = [[0] * 64 for _ in range(64)]
    for x in range(64):
        for y in range(64):
            v = 0
            for i in range(6):
                if (x >> i) & 1:
                    for j in range(6):
                        if (y >> j) & 1:
                            v ^= GPROD[i][j]
            RMUL[x][y] = v
    A = m2(3, 2)   # [[1,1],[0,1]]
    B = m2(1, 3)   # [[1,0],[1,1]]
    S = m2(2, 1)   # [[0,1],[1,0]]
    assert mm2(mm2(A, B), A) == S and mm2(mm2(B, A), B) == S
    IDE = m2(1, 2)
    assert mm2(IDE, IDE) == IDE
    GP1, BP1, SP1 = gplus(A), gplus(B), gplus(S)
    PAB, QBA = RMUL[GP1][BP1], RMUL[BP1][GP1]
    J1 = [gplus(g) for g in ELEMS if g != IDE]
    J2 = _span([RMUL[x][y] for x in J1 for y in J1])
    J3 = _span([RMUL[RMUL[x][y]][z] for x in J1 for y in J1 for z in J1])
    ECHELON = _echelon(J3)
    RED = [0] * 64
    for x in range(64):
        RED[x] = _reduce(x)
    DIMS = (len(J1), len(J2), len(J3))


def idx(g):
    return IDX[g]


def gen(i):
    return 1 << i


def gplus(g):
    return (1 << IDX[g]) ^ (1 << IDX[IDE])


def rmul(x, y):
    return RMUL[x][y]


def _span(vecs):
    """Reduced row-echelon basis of the F2 span of 6-bit vectors."""
    rows = [v for v in vecs if v]
    r = 0
    for col in range(5, -1, -1):
        sel = next((i for i in range(r, len(rows)) if (rows[i] >> col) & 1), None)
        if sel is None:
            continue
        rows[r], rows[sel] = rows[sel], rows[r]
        for i in range(len(rows)):
            if i != r and (rows[i] >> col) & 1:
                rows[i] ^= rows[r]
        r += 1
    return sorted(rows[:r], reverse=True)


def _echelon(vecs):
    """(pivot, vector) rows in increasing pivot order; pivot = msb."""
    rows = []
    for v in _span(vecs):
        rows.append((v.bit_length() - 1, v))
    rows.sort()
    return rows


def _reduce(x):
    for piv, v in ECHELON:
        if (x >> piv) & 1:
            x ^= v
    return x


# ------------------------------------------------------------- M_r(F2) / M_r(R)
def rank_one_idempotents(r):
    out = []
    for u in range(1, 1 << r):
        for v in range(1, 1 << r):
            if bin(u & v).count("1") & 1:
                n = 0
                for p in range(r):
                    if (u >> p) & 1:
                        n |= v << (p * r)
                out.append(n)
    return sorted(set(out))


def idem(r, u, v):
    n = 0
    for p in range(r):
        if (u >> p) & 1:
            n |= v << (p * r)
    return n


def matmul(r, x, y):
    out = 0
    for p in range(r):
        xp = (x >> (p * r)) & ((1 << r) - 1)
        row = 0
        for k in range(r):
            if (xp >> k) & 1:
                row ^= (y >> (k * r)) & ((1 << r) - 1)
        out |= row << (p * r)
    return out


def ident_m(r):
    n = 0
    for p in range(r):
        n |= 1 << (p * r + p)
    return n


def gl_elements(r):
    out = []
    for x in range(1 << (r * r)):
        # invertible iff some power reaches identity (r is tiny)
        seen = {x}
        y = x
        for _ in range(r * r + 2):
            y = matmul(r, y, x)
            if y in seen:
                break
            seen.add(y)
        if ident_m(r) in seen:
            out.append(x)
    return out


def conjugate(r, u, n):
    inv = None
    for w in gl_elements_cache(r):
        if matmul(r, u, w) == ident_m(r):
            inv = w
            break
    assert inv is not None
    return matmul(r, matmul(r, u, n), inv)


_GL_CACHE = {}


def gl_elements_cache(r):
    if r not in _GL_CACHE:
        _GL_CACHE[r] = gl_elements(r)
    return _GL_CACHE[r]


# ------------------------------------------------------------------ M_r(R) ops
def mR_ident(r):
    t = [0] * (r * r)
    e = 1 << IDX[IDE]
    for p in range(r):
        t[p * r + p] = e
    return tuple(t)


def mR_mul(r, x, y):
    t = [0] * (r * r)
    for p in range(r):
        for q in range(r):
            v = 0
            for k in range(r):
                a, b = x[p * r + k], y[k * r + q]
                if a and b:
                    v ^= RMUL[a][b]
            t[p * r + q] = v
    return tuple(t)


def factor(r, g, n):
    t = [0] * (r * r)
    gp = gplus(g)
    for e in range(r * r):
        if (n >> e) & 1:
            t[e] = gp
    return tuple(t)


def mR_add(x, y):
    return tuple(a ^ b for a, b in zip(x, y))


def word_value(r, labels, mats):
    acc = mR_ident(r)
    for g, n in zip(labels, mats):
        fac = list(mR_ident(r))
        gp = gplus(g)
        for e in range(r * r):
            if (n >> e) & 1:
                fac[e] ^= gp
        acc = mR_mul(r, acc, tuple(fac))
    return acc


def target(r, k):
    t = [0] * (r * r)
    sp = 1 << IDX[S]
    ip = 1 << IDX[IDE]
    for p in range(r):
        t[p * r + p] = sp if p < k else ip
    return tuple(t)


def layer_lhs(r, labels, mats):
    """1 + sum eps_i + sum_{i<j} eps_i eps_j in M_r(R)."""
    acc = list(mR_ident(r))
    facs = []
    for g, n in zip(labels, mats):
        f = [0] * (r * r)
        gp = gplus(g)
        for e in range(r * r):
            if (n >> e) & 1:
                f[e] = gp
        facs.append(f)
        acc = [a ^ b for a, b in zip(acc, f)]
    for i in range(len(facs)):
        for j in range(i + 1, len(facs)):
            prod = mR_mul(r, tuple(facs[i]), tuple(facs[j]))
            acc = [a ^ b for a, b in zip(acc, prod)]
    return tuple(acc)


def layer_expansion_holds(r, labels, mats):
    lhs = layer_lhs(r, labels, mats)
    full = word_value(r, labels, mats)
    return all(RED[a ^ b] == 0 for a, b in zip(lhs, full))


def layer_value_ok(r, labels, mats, k):
    lhs = layer_lhs(r, labels, mats)
    tgt = target(r, k)
    return all(RED[a ^ b] == 0 for a, b in zip(lhs, tgt))


# ------------------------------------------------------- sign quotient (exact)
def _m2_vec(g, v):
    """Action of g in GL_2(F2) on column vector v (bit0 = x, bit1 = y)."""
    x = bin((g & 3) & v).count("1") & 1
    y = bin(((g >> 2) & 3) & v).count("1") & 1
    return x | (y << 1)


def perm_sign(g):
    """Sign of g: parity of its permutation of the 3 nonzero vectors of F2^2."""
    vecs = (1, 2, 3)
    perm = [vecs.index(_m2_vec(g, v)) for v in vecs]
    return sum(1 for i, j in itertools.combinations(range(3), 2)
               if perm[i] > perm[j]) & 1


def zcoef(x):
    """z-coefficient of the sign-quotient image rho(x) in F2[z]/(z^2)."""
    c = 0
    for i in range(6):
        if (x >> i) & 1:
            c ^= perm_sign(ELEMS[i])
    return c


def zcoef_mR(r, x):
    """Entrywise z-coefficient matrix of rho applied to x in M_r(R)."""
    out = 0
    for e in range(r * r):
        if zcoef(x[e]):
            out |= 1 << e
    return out


def diag_m(r, k):
    n = 0
    for p in range(k):
        n |= 1 << (p * r + p)
    return n


# ------------------------------------------------------------------- controls
def direct_control_words():
    """(r, labels, mats, k): known direct words realizing diag([S]^k, 1..)."""
    out = []
    one = idem(1, 1, 1)
    out.append((1, (A, B, A), (one, one, one), 1))
    e1, e2 = idem(2, 1, 1), idem(2, 2, 2)
    out.append((2, (A, B, A, B, A, B), (e1, e1, e1, e2, e2, e2), 2))
    e3 = idem(3, 4, 4)
    out.append((3, (A, B, A) * 3, (idem(3, 1, 1),) * 3 + (idem(3, 2, 2),) * 3 + (e3,) * 3, 3))
    f1, f2, f3, f4 = (idem(4, 1, 1), idem(4, 2, 2), idem(4, 4, 4), idem(4, 8, 8))
    out.append((4, (A, B, A) * 2 + (B, A, B) * 2,
                (f1,) * 3 + (f2,) * 3 + (f3,) * 3 + (f4,) * 3, 4))
    return out


def mutation_controls():
    """(r, labels, mats, k, name): each must FAIL full formal equality."""
    out = []
    r, labels, mats, k = direct_control_words()[3]
    out.append((r, labels[:-1], mats[:-1], k, "drop-last-call"))
    flipped = list(labels)
    flipped[0] = B
    out.append((r, tuple(flipped), mats, k, "flip-first-label"))
    out.append((r, labels, mats, k - 1, "drop-one-target"))
    bad = list(mats)
    bad[0] = bad[0] ^ 1
    out.append((r, labels, tuple(bad), k, "perturb-first-N"))
    return out


# -------------------------------------------------------------------- search
def search(r, q, n_a, k, samples, seed, budget_note=""):
    idems = rank_one_idempotents(r)
    idem_set = set(idems)
    ident = ident_m(r)
    rng = random.Random(seed)
    stat = {"r": r, "q": q, "n_a": n_a, "k": k, "samples": samples, "seed": seed,
            "valid": 0, "labelings": 0, "layer_hits": 0, "full_hits": 0,
            "full_witness": None, "layer_only_witness": None}
    for _ in range(samples):
        ns = [rng.choice(idems) for _ in range(q - 1)]
        last = ident
        for n in ns:
            last ^= n
        if last not in idem_set:
            continue
        ns.append(last)
        stat["valid"] += 1
        pairs = [[matmul(r, ns[i], ns[j]) for j in range(q)] for i in range(q)]
        total = ident
        for apos in itertools.combinations(range(q), n_a):
            stat["labelings"] += 1
            labels = [B] * q
            asum = 0
            for i in apos:
                labels[i] = A
                asum ^= ns[i]
            bsum = total ^ asum
            xsum = 0
            ysum = 0
            a_set = set(apos)
            for i in range(q):
                for j in range(i + 1, q):
                    if i in a_set and j not in a_set:
                        xsum ^= pairs[i][j]
                    elif i not in a_set and j in a_set:
                        ysum ^= pairs[i][j]
            # layer equation: 1 + ([a]+1)A_sum + ([b]+1)B_sum + P X + Q Y = T
            ok = True
            for e in range(r * r):
                v = (1 << IDX[IDE]) if (e % r == e // r) else 0
                if (asum >> e) & 1:
                    v ^= GP1
                if (bsum >> e) & 1:
                    v ^= BP1
                if (xsum >> e) & 1:
                    v ^= PAB
                if (ysum >> e) & 1:
                    v ^= QBA
                if RED[v ^ target(r, k)[e]]:
                    ok = False
                    break
            if not ok:
                continue
            stat["layer_hits"] += 1
            labels_t = tuple(labels)
            mats_t = tuple(ns)
            full = word_value(r, labels_t, mats_t) == target(r, k)
            if full:
                stat["full_hits"] += 1
                if stat["full_witness"] is None:
                    stat["full_witness"] = (labels_t, mats_t)
            elif stat["layer_only_witness"] is None:
                stat["layer_only_witness"] = (labels_t, mats_t)
    return stat


# ---------------------------------------------------------------------- main
def run_controls():
    lines = []
    for r, labels, mats, k in direct_control_words():
        assert word_value(r, labels, mats) == target(r, k), "direct word fails"
        assert layer_value_ok(r, labels, mats, k), "direct word fails layer"
    lines.append("direct_words=4")
    for r, labels, mats, k, name in mutation_controls():
        assert word_value(r, labels, mats) != target(r, k), "mutation passes: " + name
    lines.append("mutation_controls=4")
    r1 = search(1, 3, 1, 1, samples=4000, seed=11)
    assert r1["full_witness"] is not None, "r=1 control search found nothing"
    r2 = search(2, 6, 3, 2, samples=40000, seed=12)
    assert r2["full_witness"] is not None, "r=2 control search found nothing"
    assert r2["layer_hits"] > 0 and r2["layer_only_witness"] is not None, \
        "no strict-relaxation witness at r=2"
    lines.append("search_controls=r1:%d/%d r2:%d/%d/%d" %
                 (r1["full_hits"], r1["valid"], r2["full_hits"], r2["layer_hits"], r2["valid"]))
    # Obstruction check: the augmentation powers of F2[GL_2(F2)] stabilize at
    # J^2 = J^3, so R/J^3 is the sign quotient F2[z]/(z^2) and the J^2-layer
    # equation carries no information beyond sum N_i = I_r.
    assert DIMS[1] == DIMS[2] and _span(J2) == _span(J3), "expected J^2 = J^3"
    rng = random.Random(20261015)
    idems = rank_one_idempotents(4)
    equiv = 0
    for _ in range(200):
        q = rng.randrange(2, 8)
        labels = tuple((A, B)[rng.randrange(2)] for _ in range(q))
        mats = tuple(rng.choice(idems) for _ in range(q))
        total = 0
        for n in mats:
            total ^= n
        if layer_value_ok(4, labels, mats, 4) == (total == ident_m(4)):
            equiv += 1
    assert equiv == 200, "layer check must be equivalent to sum N_i = I_r"
    lines.append("j2_eq_j3=1 layer_iff_sum=200/200")
    # Restored-role sign quotient (review follow-up on
    # https://github.com/CrocSwap/integer-mult-bounds/pull/1755): at r = 5 with
    # endpoint diag([S],[S],[S],[S],1) the fifth role is restored with the
    # identity boundary, so its target augmentation is zero and the quotient
    # forces sum N_i = diag(I_4, 0), NOT I_5.  Conditioning on I_5 would
    # exclude every solution to that endpoint.  Exact checks below: the
    # permutation sign agrees with the J^2 = J^3 reduction, the endpoint's
    # z-coefficient matrix is diag(I_4,0) with a zero fifth diagonal entry, a
    # 12-call disjoint witness realizes the endpoint with sum N_i =
    # diag(I_4,0) != I_5, forcing the total to I_5 breaks the endpoint layer
    # equation, and the r = 5 layer equation stays equivalent to
    # sum N_i = diag(I_4,0) on 200/200 random instances.
    assert all(perm_sign(g) == (0 if RED[gplus(g)] == 0 else 1) for g in ELEMS), \
        "sign quotient must match the J^2 = J^3 reduction"
    zt = zcoef_mR(5, target(5, 4))
    assert zt == diag_m(5, 4) and not (zt >> 24) & 1, \
        "fifth role's target augmentation must be zero"
    labels5 = (A, B, A) * 2 + (B, A, B) * 2
    mats5 = (idem(5, 1, 1),) * 3 + (idem(5, 2, 2),) * 3 + \
            (idem(5, 4, 4),) * 3 + (idem(5, 8, 8),) * 3
    assert word_value(5, labels5, mats5) == target(5, 4), \
        "restored-role control word must realize diag([S],[S],[S],[S],1)"
    total5 = 0
    for n in mats5:
        total5 ^= n
    assert total5 == zt and total5 != ident_m(5), \
        "I_5 conditioning must overconstrain the restored-role endpoint"
    assert layer_value_ok(5, labels5, mats5, 4), "witness must pass the layer check"
    forced5 = total5 ^ idem(5, 16, 16)
    assert forced5 == ident_m(5)
    assert not layer_value_ok(5, labels5 + (A,), mats5 + (idem(5, 16, 16),), 4), \
        "an I_5 total must fail the endpoint layer equation"
    rng = random.Random(20261016)
    idems5 = rank_one_idempotents(5)
    equiv5 = 0
    for _ in range(200):
        q = rng.randrange(2, 8)
        labels = tuple((A, B)[rng.randrange(2)] for _ in range(q))
        mats = tuple(rng.choice(idems5) for _ in range(q))
        total = 0
        for n in mats:
            total ^= n
        if layer_value_ok(5, labels, mats, 4) == (total == zt):
            equiv5 += 1
    assert equiv5 == 200, \
        "r=5 layer check must be equivalent to sum N_i = diag(I_4,0)"
    lines.append("r5_restored_role=1 fifth_role_zcoef=0 i5_overconstrains=1 "
                 "layer_iff_sum_diagI4zero=200/200")
    return lines, r1, r2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--full", action="store_true", help="run the recorded full search budget")
    ap.add_argument("--samples", type=int, default=0)
    ap.add_argument("--emit", action="store_true", help="print receipt without comparing EXPECTED.json")
    args = ap.parse_args()
    build()
    t0 = time.time()
    lines, r1, r2 = run_controls()
    samples = args.samples or (6000000 if args.full else 2000000)
    mode = "full" if args.full else "default"
    main_stat = search(4, 10, 5, 4, samples=samples, seed=20261014)
    elapsed = time.time() - t0
    receipt = {
        "mode": mode,
        "dims_J1_J2_J3": list(DIMS),
        "samples": samples,
        "valid": main_stat["valid"],
        "labelings": main_stat["labelings"],
        "layer_hits": main_stat["layer_hits"],
        "full_hits": main_stat["full_hits"],
        "r1_control_full_hits": r1["full_hits"],
        "r2_control_full_hits": r2["full_hits"],
        "r2_control_layer_hits": r2["layer_hits"],
    }
    expected_path = HERE / "EXPECTED.json"
    if args.emit:
        print(json.dumps(receipt, indent=1, sort_keys=True))
    elif expected_path.exists():
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
        want = expected[mode]
        for key, value in want.items():
            assert receipt[key] == value, "receipt mismatch %s: got %r want %r" % (
                key, receipt[key], value)
    print("controls: " + " ".join(lines))
    print("augmentation dims (J1,J2,J3)=%s with J2=J3; R/J3 is the sign quotient" % (DIMS,))
    print("main search r=4 q=10 (5a,5b) k=4 samples=%d valid=%d labelings=%d "
          "layer_hits=%d full_hits=%d" % (samples, main_stat["valid"],
                                          main_stat["labelings"], main_stat["layer_hits"],
                                          main_stat["full_hits"]))
    if main_stat["full_witness"] is not None:
        labels, mats = main_stat["full_witness"]
        print("CANDIDATE_FOUND labels=" + "".join("a" if g == A else "b" for g in labels))
        print("CANDIDATE_MATS=" + json.dumps(list(mats)))
        print("PASS_FOUR_SWAP_BALANCED_J3_LAYER candidate_found no_new_kappa")
    else:
        print("PASS_FOUR_SWAP_BALANCED_J3_LAYER balanced_5a5b_unrealized_in_search "
              "layer_hits=%d no_new_kappa" % main_stat["layer_hits"])
    print("elapsed_seconds=%.1f" % elapsed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
