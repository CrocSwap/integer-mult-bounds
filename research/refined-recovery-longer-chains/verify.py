"""Exact checks for the longer-chain refined recovery theorem (stdlib only).

Prints PASS_REFINED_RECOVERY_LONGER_CHAINS on success.
"""
import hashlib
import itertools
import json
import pathlib
import random
import sys
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
FIXTURE = HERE.parent / "precision-state-frontier" / "FIXTURE.json"
FIXTURE_SHA = "2ca4d7550fcae5b757ec500f87aee1d2ef9f64b59e4abe2bda93319521304af8"
N, MODES = 112, 8
F = (13**8 + 14 * 13**4 + 1) // 16


def fail(msg):
    raise SystemExit("FAIL: " + msg)


def check(cond, msg):
    if not cond:
        fail(msg)


def rnd(fr):
    """Nearest integer, half ties away from zero."""
    n, d = fr.numerator, fr.denominator
    q = (2 * abs(n) + d) // (2 * d)
    return q if n >= 0 else -q


def quot(s):
    lo, hi = -((26 + s) // 4) - 2, (26 - s) // 4 + 2
    return [q for q in range(lo, hi + 1) if rnd(Fraction(s + 56 * q, 52)) == q]


def f2_rank(vecs):
    piv, r = {}, 0
    for v in vecs:
        while v:
            p = v.bit_length() - 1
            if p not in piv:
                piv[p] = v
                r += 1
                break
            v ^= piv[p]
    return r


def load():
    raw = FIXTURE.read_bytes()
    check(hashlib.sha256(raw).hexdigest() == FIXTURE_SHA, "fixture hash")
    cols = json.loads(raw)["mode_columns"]
    check(len(cols) == MODES and all(len(c) == N for c in cols), "fixture shape")
    return [tuple(cols[j][i] for j in range(MODES)) for i in range(N)]


def mt(rho, vec):
    """M^T vec for an integer vector (dict index->value)."""
    return tuple(sum(x * rho[i][m] for i, x in vec.items()) for m in range(MODES))


def source_facts(rho):
    for a in range(MODES):
        for b in range(MODES):
            check(sum(r[a] * r[b] for r in rho) == (56 if a == b else 0), "M^T M = 56 I")
    colbits = [sum((rho[i][j] & 1) << i for i in range(N)) for j in range(MODES)]
    code = [q for q in range(256) if not f2_xor(colbits, q)]
    check(len(code) == 16, "|C| = 16")
    weights = sorted(bin(c).count("1") for c in code)
    check(weights == [0] + [4] * 14 + [8], "Hamming weight enumerator")
    check(all(bin(a & b).count("1") % 2 == 0 for a in code for b in code), "C self-orthogonal")
    check(f2_rank(colbits) == 4, "rank M mod 2 = 4")
    check(sum(13 ** (8 - bin(c).count("1")) for c in code) == 16 * F, "F = W_C(13,1)/16")
    return colbits, code


def f2_xor(colbits, q):
    v = 0
    for j in range(MODES):
        if (q >> j) & 1:
            v ^= colbits[j]
    return v


def scalar_and_box(code):
    for s in range(-4000, 4001):
        q = quot(s)
        check(q and q == list(range(q[0], q[-1] + 1)) and len(q) <= 13, "Q(s) interval <= 13")
    for m in range(-60, 61):
        check(quot(56 * m) == list(range(-6 - 14 * m, 7 - 14 * m)), "Q(56m) translate")
    # Box lemma at maximal lengths: every start parity per coordinate, every coset.
    best = 0
    for starts in range(256):
        counts = [((7, 6) if (starts >> k) & 1 == 0 else (6, 7)) for k in range(MODES)]
        for c in range(256):
            tot = 0
            for h in code:
                p = c ^ h
                v = 1
                for k in range(MODES):
                    v *= counts[k][(p >> k) & 1]
                tot += v
            best = max(best, tot)
    check(best == F, "box coset maximum equals F")
    # Fourier coefficient bound behind the lemma: |sum (-1)^x over an interval| <= 1.
    check(all(abs(sum((-1) ** x for x in range(a, a + L))) <= 1 for a in range(-3, 3) for L in range(14)), "signed interval sum")


def two_e_witnesses(rho):
    """Integer w_i with M^T w_i = 2 e_i, so 2 Z^8 lies in M^T Z^112."""
    basis = json.loads((HERE / "FRAMES.json").read_text())["lattice_basis_rows"]
    check(len(basis) == MODES, "basis size")
    for i in range(MODES):
        a = [[Fraction(rho[b][r]) for b in basis] + [Fraction(2 if r == i else 0)] for r in range(MODES)]
        for c in range(MODES):
            p = next((r for r in range(c, MODES) if a[r][c] != 0), None)
            check(p is not None, "lattice basis rows independent")
            a[c], a[p] = a[p], a[c]
            a[c] = [x / a[c][c] for x in a[c]]
            for r in range(MODES):
                if r != c and a[r][c] != 0:
                    f = a[r][c]
                    a[r] = [x - f * y for x, y in zip(a[r], a[c])]
        coef = [a[r][MODES] for r in range(MODES)]
        check(all(x.denominator == 1 for x in coef), "2e_i in M^T Z^112")
        w = {b: int(x) for b, x in zip(basis, coef) if x}
        check(mt(rho, w) == tuple(2 if k == i else 0 for k in range(MODES)), "2e_i witness value")


def frames(rho, colbits, code):
    data = json.loads((HERE / "FRAMES.json").read_text())
    ecoords = tuple(data["E_coords"])
    t = data["stages"]
    check(ecoords == (0, 1, 2, 4) and t == 26, "frame header")
    blocks = [[{int(i): int(x) for i, x in col} for col in blk] for blk in data["V_blocks"]]
    check(len(blocks) == t - 1 and all(len(b) == 4 for b in blocks), "block shape")
    for blk in blocks:
        for col in blk:
            check(all(x != 0 for x in col.values()), "sparse nonzero")
            check(mt(rho, col) == (0,) * MODES, "M^T V = 0")
            check(not any(i in col for i in ecoords), "E V = 0")
    # E M mod 2 has rank 4 and kernel C.
    em = [sum((rho[e][j] & 1) << j for j in range(MODES)) for e in ecoords]
    check(f2_rank(em) == 4, "rank EM = 4")
    check(all(all(bin(r & c).count("1") % 2 == 0 for r in em) for c in code), "ker EM contains C")
    # Binary images of W_j M = M + V_j (E M), j = 1..t (V_1 = 0).
    images = []
    vlist = [None] + blocks
    for j in range(t):
        for col in range(MODES):
            v = colbits[col]
            if vlist[j] is not None:
                for r, e in enumerate(ecoords):
                    if rho[e][col] & 1:
                        v ^= sum(1 << i for i, x in vlist[j][r].items() if x & 1)
            images.append(v)
    blockrank = [f2_rank(images[MODES * j:MODES * (j + 1)]) for j in range(t)]
    check(blockrank == [4] * t, "each image has dimension 4")
    check(f2_rank(images) == 4 * t == 104, "direct sum of 26 binary images")
    return ecoords, blocks, images


def apply_w(vec, blk, ecoords, sign):
    """(I + sign * V E) vec for a list vector."""
    out = list(vec)
    if blk is None:
        return out
    for r, e in enumerate(ecoords):
        if vec[e]:
            for i, x in blk[r].items():
                out[i] += sign * x * vec[e]
    return out


def chain_replay(rho, ecoords, blocks, depth, seed):
    """Forward chain with U_j = I + (V_j - V_(j+1)) E, then check the inverse identity."""
    rng = random.Random(seed)
    vlist = [None] + blocks

    def kernel(z):
        m = [sum(z[i] * rho[i][k] for i in range(N)) for k in range(MODES)]
        q = [rnd(Fraction(x, 52)) for x in m]
        return [z[i] - sum(rho[i][k] * q[k] for k in range(MODES)) for i in range(N)], q

    for _ in range(3):
        x = [rng.randint(-10**6, 10**6) for _ in range(N)]
        z, q = kernel([2 * v for v in x])
        qs = [q]
        for j in range(1, depth):
            # U_j z = (I - V_(j+1) E)(I + V_j E) z
            u = apply_w(apply_w(z, vlist[j - 1], ecoords, 1), vlist[j], ecoords, -1)
            z, q = kernel(u)
            qs.append(q)
        y = z
        # 2x = sum_j W_j M q_j + W_t y with W_j = I + V_j E.
        acc = apply_w(y, vlist[depth - 1], ecoords, 1)
        for j in range(depth):
            mq = [sum(rho[i][k] * qs[j][k] for k in range(MODES)) for i in range(N)]
            acc = [a + b for a, b in zip(acc, apply_w(mq, vlist[j], ecoords, 1))]
        check(acc == [2 * v for v in x], "inverse chain identity")


def parity_i_zero_fiber(code, t):
    """Zero fiber when every binary image equals im M: sum_j u_j in C."""
    cnt = [7 ** (8 - w) * 6 ** w for w in range(9)]
    weight = [cnt[bin(u).count("1")] for u in range(256)]
    dist = {0: 1}
    for _ in range(t):
        new = {}
        for a, va in dist.items():
            for u in range(256):
                new[a ^ u] = new.get(a ^ u, 0) + va * weight[u]
        dist = new
    return sum(dist.get(c, 0) for c in code)


def main():
    rho = load()
    colbits, code = source_facts(rho)
    scalar_and_box(code)
    two_e_witnesses(rho)
    ecoords, blocks, images = frames(rho, colbits, code)
    for t in (1, 2, 3):
        a_t = (13 ** (8 * t) + 14 * 13 ** (4 * t) + 1) // 16
        check(parity_i_zero_fiber(code, t) == a_t, "parity-I zero fiber equals A_t")
    check(parity_i_zero_fiber(code, 2) > F**2, "overlapping images enlarge the zero fiber")
    chain_replay(rho, ecoords, blocks, 3, 11)
    chain_replay(rho, ecoords, blocks, 26, 12)
    # Negative controls.
    bad = json.loads((HERE / "FRAMES.json").read_text())
    col = bad["V_blocks"][0][0]
    col[0][1] += 1
    try_col = {int(i): int(x) for i, x in col}
    check(mt(rho, try_col) != (0,) * MODES, "control: perturbed V leaves M^T V = 0")
    dup = images[:MODES * 25] + images[MODES:2 * MODES]
    check(f2_rank(dup) < 104, "control: repeated frame keeps a direct sum")
    print("depth, packed bits ceil(log2 F^t):", [(t, (F**t - 1).bit_length()) for t in (1, 2, 3, 26)])
    print("PASS_REFINED_RECOVERY_LONGER_CHAINS")


if __name__ == "__main__":
    main()
