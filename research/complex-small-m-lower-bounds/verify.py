#!/usr/bin/env python3
"""Registered check for research/complex-small-m-lower-bounds. Standard library only.

  python3 -B verify.py --part main       PASS_COMPLEX_SMALL_M_LOWER_BOUNDS_MAIN
  python3 -B verify.py --part controls   PASS_COMPLEX_SMALL_M_LOWER_BOUNDS_CONTROLS
  python3 -B verify.py                   both

Words. Block size m, n = 2^m addresses, W arrays, s paid calls. A call is
dir(z) = a I + b X_z on one array (a = (1+i)/2, b = (1-i)/2, X_z the shift by z).
At f digit columns every letter acts on (C^n)^(x)f, the same in every column.

The hook at block m and width f = j + 2 lives in V (x) Lambda^(j+1) V (V = C^n):
N = span{e_x (x) e_T : x in T}. For a letter g, raise(g) = dim(N + gN) - dim N
= rank of g_W[S^c, S]. Free letters (shifts, address maps, phases) keep N (proved
in Lean). The kept-subspace bound then gives W * demand <= cap * s.

Parts of --part main:
  pins      sha256 of every data file (equal, byte for byte, to files of
            jacobalansussman/wht-power-saving-lean at commits 86e575e, ce3c261 and f08d308;
            SOURCES.json)
  block2    m = 2, f = 3: cap <= 4 in all 3 directions (exact Z[i] vectors), attained
            (rank mod p), demand >= 8 (rank mod p of the whole block): s >= 2W
  block3    m = 3, f = 5: cap <= 80 in all 7 directions (exact Z[i] vectors) and attained
            in all 7 (rank mod p); demand >= 224 (a 224 x 224 minor nonzero mod p, and the
            rank mod p of the whole 280 x 280 block); two calls in a row raise the hook by <= 144 (136 exact vectors);
            the character block M_0 has rank >= 28 (two formats, two routines): s >= 14W/5
  leandata  the eight 28 x 28 blocks of Dem3Data.lean (the data Lean's kernel checked):
            certificate x formula = identity mod 65537, re-done here; 8 x 28 = 224
  face3     Theorem C3's certificate: Lambda^3(C^8), N = the 24 face triples; shifts and
            diagonal phases keep N; cap 8 in all 7 directions; demand 24 in all 28 bases
            (exact ranks over Q(i)): s >= 3W
  block4    cap formula (16/2) C(14,7) = 27,456; 16 x 5,412 = 86,592; ratio 41/13; the
            format of the 5,412 x 5,412 demand certificate (its determinant is author
            evidence: author-evidence/check_m0.c, about an hour)
  depth     the inputs of section 7: two and three moves in independent directions raise the
            block-4 hook by a_2 >= 48,576 and a_3 >= 68,320 (the hook split over the untouched
            address bits into ranks of at most 280 x 280, mod p; one move gives the cap 27,456
            and block 3 gives 80 and 144 the same way); the exact block-5 and block-6 bounds
            834241/278850 and 1188222/399685 from that profile; the format of the two minor
            certificates for a_2 and a_3 (their determinants on all 16 characters are author
            evidence: author-evidence/check_mj.c, 42 minutes)
  width     with one zero scratch array, C^(x)3 costs zero calls at width f = 1, and the
            same program is wrong at f = 2; every entry of C^(x)3 is nonzero
  table     every saving, exclusion and open shape printed in README.md and PROOF.md

--part controls: corrupted certificates and false claims; each must be rejected.
No assert statements are used; every check is explicit and reported.
"""
import argparse
import hashlib
import itertools
import json
import math
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

PINS = {
    "data/Dem3Data.lean": "0982f9cf408a7d2f930b4e65d1e2b1bd6a22b3c0601c372886fa7d9bf4c0cc52",
    "data/cert_m2_M0.txt": "884bc29dbaf3714cb23426f56e28039e1dafb9b13f63a6b595b8dc15423f3cf0",
    "data/cert_m3_B2.json": "078eb2a6a481f5a176b2fce2331fb285dbe8e20b034c5bb4558abc2455a27cf6",
    "data/cert_m3_M0.json": "325f47b568ce2fee4d1b8848f19b0e27772340de5b4a04702d8799b3b1763748",
    "data/cert_m3_M0_c.txt": "82169f3e70bc11ebdabc9b573f82f50f92e0a8073c5e747deb64714a84c0e6bc",
    "data/cert_m3_dem.json": "99235c4fbfb37a2205a888b18292edbfa3be07970dd0550c47f79bbe66e802c3",
    "data/cert_m4_M0.txt": "72530af84ea9a702b9e48b1dd8d5e69e9b0552840096f38b5caac9667c4236e2",
    "data/neg_m3_29.txt": "1d89519b59d32f23ca4dd5355b45ed03a226bec430bc90aeafaac0d001bbfa36",
    "data/neg_m3_comp.txt": "4ebc926017f670b43345af6d984039b4b93327ddb387e6d95d8f861133f65a8c",
    "data/neg_m3_dup.txt": "f6fe0a5d3025396dcfe168214a33e4730e20c46187b5b68a5aeaf86cabbfa928",
    "author-evidence/check_m0.c": "8242342188fe73eb8ab0db9e48727d086ec78c38032bdfb76b38a3af40ceef6e",
    "data/cert_m4_g2_M0.txt": "1961d7482576245953e4b0368603ecf6295b02a8543334816e5c0139d64601c3",
    "data/cert_m4_g3_M0.txt": "b04afdc7cb060c96605aeff19ee8a1ceb0968785208f6e66a938ebec7c3125ca",
    "author-evidence/check_mj.c": "ca59130c3153da31eac93282126c797afd555d9a0934f60ecb38e304f46e82e0",
    "author-evidence/out_check_m4_g2.txt": "7c4291efee95581d491be507e3f024d8ad36095d58440efd37c2ce9a1e5ea3c1",
    "author-evidence/out_check_m4_g3.txt": "f82df0cd636ac90734699b2d4cf269354b59e4332687732a027f6bffe254f97a",
    "author-evidence/induction-across-block-sizes.md": "0c2f6f5a07f1deccfa2b838c6d29bc6d86567069569890c37c820b03f7d888ef",
}

RESULTS = []


def report(name, ok, msg):
    RESULTS.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}: {msg}", flush=True)
    return bool(ok)


def control(name, rejected, msg):
    """A control passes when the corrupted input or false claim is rejected."""
    RESULTS.append((name, bool(rejected)))
    print(f"[{'PASS' if rejected else 'FAIL'}] control {name}: "
          f"{'rejected as it must be' if rejected else 'NOT rejected'}: {msg}", flush=True)
    return bool(rejected)


# ---------------------------------------------------------------- arithmetic

def is_prime(q):
    if q < 2:
        return False
    if q % 2 == 0:
        return q == 2
    d = 3
    while d * d <= q:
        if q % d == 0:
            return False
        d += 2
    return True


def sqrt_minus_one(p):
    for g in range(2, 10000):
        c = pow(g, (p - 1) // 4, p)
        if c * c % p == p - 1:
            return c
    return None


def popc(x):
    return bin(x).count("1")


# Gaussian integers as pairs (re, im)
ZERO, ONE = (0, 0), (1, 0)


def gmul(x, y):
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def gadd(x, y):
    return (x[0] + y[0], x[1] + y[1])


def gneg(x):
    return (-x[0], -x[1])


def gdet(A):
    """Exact determinant over Z[i] by expansion along the first row."""
    if len(A) == 1:
        return A[0][0]
    tot = ZERO
    for j, e in enumerate(A[0]):
        if e == ZERO:
            continue
        minor = [row[:j] + row[j + 1:] for row in A[1:]]
        t = gmul(e, gdet(minor))
        tot = gadd(tot, t if j % 2 == 0 else gneg(t))
    return tot


def det_modp(A, p):
    A = [[x % p for x in r] for r in A]
    N = len(A)
    det = 1
    for c in range(N):
        pr = next((r for r in range(c, N) if A[r][c]), None)
        if pr is None:
            return 0
        if pr != c:
            A[c], A[pr] = A[pr], A[c]
            det = -det
        det = det * A[c][c] % p
        iv = pow(A[c][c], p - 2, p)
        rc = A[c]
        for r in range(c + 1, N):
            if A[r][c]:
                f = A[r][c] * iv % p
                A[r] = [(x - f * y) % p for x, y in zip(A[r], rc)]
    return det % p


def rank_modp(A, p):
    A = [[x % p for x in r] for r in A]
    R = len(A)
    C = len(A[0]) if R else 0
    rk = 0
    for c in range(C):
        pr = next((r for r in range(rk, R) if A[r][c]), None)
        if pr is None:
            continue
        A[rk], A[pr] = A[pr], A[rk]
        iv = pow(A[rk][c], p - 2, p)
        top = A[rk]
        for r in range(rk + 1, R):
            if A[r][c]:
                f = A[r][c] * iv % p
                A[r] = [(x - f * y) % p for x, y in zip(A[r], top)]
        rk += 1
    return rk


def rank_exact_gauss(rows):
    """Exact rank over Q(i) of a matrix with Z[i] entries: realify, Fraction elimination."""
    R = []
    for r in rows:
        R.append([Fraction(e[0]) for e in r] + [Fraction(-e[1]) for e in r])
        R.append([Fraction(e[1]) for e in r] + [Fraction(e[0]) for e in r])
    rk = 0
    ncol = len(R[0]) if R else 0
    for c in range(ncol):
        piv = next((r for r in range(rk, len(R)) if R[r][c] != 0), None)
        if piv is None:
            continue
        R[rk], R[piv] = R[piv], R[rk]
        for r in range(len(R)):
            if r != rk and R[r][c] != 0:
                f = R[r][c] / R[rk][c]
                R[r] = [x - f * y for x, y in zip(R[r], R[rk])]
        rk += 1
    return rk // 2, rk % 2 == 0


# ------------------------------------------------------------- the hook family

class Hook:
    """The hook N = span{e_x (x) e_T : x in T} inside V (x) Lambda^k V, V = C^n, n = 2^m."""

    def __init__(self, m, k):
        self.m, self.k, self.n = m, k, 1 << m
        self.subs = list(itertools.combinations(range(self.n), k))
        self.S = [(x, T) for x in range(self.n) for T in self.subs if x in T]
        self.Sc = [(y, U) for y in range(self.n) for U in self.subs if y not in U]

    # exact Z[i] matrices of 2 dir(z) and of shifts
    def two_dir(self, z):
        n = self.n
        M = [[ZERO] * n for _ in range(n)]
        for x in range(n):
            M[x][x] = gadd(M[x][x], (1, 1))
            M[x ^ z][x] = gadd(M[x ^ z][x], (1, -1))
        return M

    def matmul(self, A, B):
        n = self.n
        out = [[ZERO] * n for _ in range(n)]
        for r in range(n):
            for c in range(n):
                acc = ZERO
                for t in range(n):
                    if A[r][t] != ZERO and B[t][c] != ZERO:
                        acc = gadd(acc, gmul(A[r][t], B[t][c]))
                out[r][c] = acc
        return out

    def wedge_col(self, g, T):
        """(Lambda^k g) e_T = sum_U det g[U, T] e_U, exact."""
        col = {}
        for U in self.subs:
            d = gdet([[g[u][t] for t in T] for u in U])
            if d != ZERO:
                col[U] = d
        return col

    def apply_W(self, g, vec, cache):
        out = {}
        for (x, T), c in vec.items():
            if c == ZERO:
                continue
            if T not in cache:
                cache[T] = self.wedge_col(g, T)
            col = cache[T]
            for y in range(self.n):
                if g[y][x] == ZERO:
                    continue
                gy = gmul(g[y][x], c)
                for U, d in col.items():
                    key = (y, U)
                    out[key] = gadd(out.get(key, ZERO), gmul(gy, d))
        return {kk: v for kk, v in out.items() if v != ZERO}

    @staticmethod
    def wedge_sign_sorted(seq):
        if len(set(seq)) < len(seq):
            return 0, None
        inv = sum(1 for i in range(len(seq)) for j in range(i + 1, len(seq)) if seq[i] > seq[j])
        return (-1 if inv % 2 else 1), tuple(sorted(seq))

    def cap_vectors(self, z):
        """Exact vectors u in N with (2 dir z)_W u in N, pairwise disjoint supports.
        Their number t gives raise(dir z) <= |S| - t."""
        g = self.two_dir(z)
        vecs = []
        for a in range(self.n):
            b = a ^ z
            if a > b:
                continue
            for w in itertools.combinations(range(self.n), self.k - 1):
                u = {}
                for x, sg in ((a, 1), (b, -1)):
                    s, srt = self.wedge_sign_sorted((x,) + w)
                    if s:
                        u[(x, srt)] = (sg * s, 0)
                if u:
                    vecs.append(u)
        cache = {}
        bad = sum(1 for u in vecs if any(y not in U for (y, U) in self.apply_W(g, u, cache)))
        keys = [key for u in vecs for key in u]
        disjoint = len(keys) == len(set(keys)) and all(x in T for (x, T) in keys)
        return len(vecs), bad, disjoint

    def raise_modp(self, g_modp, p):
        """rank mod p of g_W[S^c, S] (a lower bound for raise(g) over Q(i))."""
        n = self.n
        wc = {}
        for T in self.subs:
            col = {}
            for U in self.subs:
                d = det_modp([[g_modp[u][t] for t in T] for u in U], p)
                if d:
                    col[U] = d
            wc[T] = col
        A = [[g_modp[y][x] * wc[T].get(U, 0) % p for (x, T) in self.S] for (y, U) in self.Sc]
        return rank_modp(A, p)


def dir_modp(n, z, p, I):
    h = pow(2, p - 2, p)
    M = [[0] * n for _ in range(n)]
    for x in range(n):
        M[x][x] = (M[x][x] + (1 + I) * h) % p
        M[x ^ z][x] = (M[x ^ z][x] + (1 - I) * h) % p
    return M


def mm_modp(A, B, p):
    n = len(A)
    return [[sum(A[r][t] * B[t][c] for t in range(n)) % p for c in range(n)] for r in range(n)]


def kernel_modp(m, p, I):
    n = 1 << m
    K = None
    for j in range(m):
        D = dir_modp(n, 1 << j, p, I)
        K = D if K is None else mm_modp(K, D, p)
    return K


# ------------------------------------------------------------------- the parts

def part_pins():
    ok = True
    for rel, want in sorted(PINS.items()):
        path = os.path.join(HERE, rel)
        try:
            got = hashlib.sha256(open(path, "rb").read()).hexdigest()
        except OSError as exc:
            got = f"unreadable ({exc})"
        ok &= report(f"pin {rel}", got == want, got[:16] + "...")
    return ok


P1 = 1000000009        # a prime = 1 mod 4 for the rank checks


def part_block2():
    H = Hook(2, 2)                  # j = 1, f = j + 2 = 3, k = j + 1 = 2
    ok = report("block2 hook size", len(H.S) == 12 and len(H.Sc) == 12, f"|S| = {len(H.S)}, |S^c| = {len(H.Sc)}")
    I = sqrt_minus_one(P1)
    caps = {}
    for z in range(1, 4):
        t, bad, disjoint = H.cap_vectors(z)
        attained = H.raise_modp(dir_modp(4, z, P1, I), P1)
        caps[z] = (len(H.S) - t, attained)
        ok &= report(f"block2 cap dir {z}", bad == 0 and disjoint and len(H.S) - t == 4 and attained == 4,
                     f"{t} exact vectors kept (images outside N: {bad}, disjoint: {disjoint}) -> raise <= {len(H.S) - t}; rank mod p = {attained}")
    dem = H.raise_modp(kernel_modp(2, P1, I), P1)
    ok &= report("block2 demand", dem >= 8, f"rank mod {P1} of K_W[S^c,S] = {dem} -> demand >= {dem}")
    ok &= report("block2 bound", Fraction(dem, 4) == 2, f"demand/cap = {dem}/4 = {Fraction(dem, 4)} calls per array: s >= 2W")
    return ok


def part_block3(full_attained=True):
    H = Hook(3, 4)                  # j = 3, f = 5, k = 4
    ok = report("block3 hook size", len(H.S) == 280 and len(H.Sc) == 280, f"|S| = {len(H.S)}")
    I = sqrt_minus_one(P1)
    for z in range(1, 8):
        t, bad, disjoint = H.cap_vectors(z)
        msg = f"{t} exact vectors (outside N: {bad}, disjoint: {disjoint}) -> raise <= {280 - t}"
        good = bad == 0 and disjoint and t == 200
        if full_attained or z == 1:
            att = H.raise_modp(dir_modp(8, z, P1, I), P1)
            msg += f"; rank mod p = {att} (attained)"
            good = good and att == 80
        ok &= report(f"block3 cap dir {z}", good, msg)
    # demand certificate
    C = json.load(open(os.path.join(DATA, "cert_m3_dem.json")))
    dem, msg = check_dem3_cert(C, H)
    ok &= report("block3 demand certificate", dem == 224, msg)
    full = H.raise_modp(kernel_modp(3, P1, I), P1)
    ok &= report("block3 demand, whole block", full >= 224, f"rank mod {P1} of the whole 280 x 280 block K_W[S^c,S] = {full}")
    # two calls in a row
    C2 = json.load(open(os.path.join(DATA, "cert_m3_B2.json")))
    f2, msg = check_b2_cert(C2, H)
    ok &= report("block3 two calls in a row", f2 == 144, msg)
    # character block M_0, two formats
    C3 = json.load(open(os.path.join(DATA, "cert_m3_M0.json")))
    r0, msg = check_m0_json(C3)
    ok &= report("block3 M_0 block (json format)", r0 == 28, msg)
    r0c, msg = check_m0_text(open(os.path.join(DATA, "cert_m3_M0_c.txt")).read())
    ok &= report("block3 M_0 block (text format, second routine)", r0c == 28, msg)
    r2, msg = check_m0_text(open(os.path.join(DATA, "cert_m2_M0.txt")).read())
    ok &= report("block2 M_0 block (text format)", r2 == 2, msg + "; 4 characters x 2 = 8")
    ok &= report("block3 bound", Fraction(224, 80) == Fraction(14, 5) and 8 * 28 == 224,
                 "demand/cap = 224/80 = 14/5 calls per array: 5 s >= 14 W; 8 characters x 28 = 224")
    return ok


def check_dem3_cert(C, H):
    p, I = C.get("p"), C.get("I")
    rows = [(r[0], tuple(r[1])) for r in C.get("rows", [])]
    cols = [(c[0], tuple(c[1])) for c in C.get("cols", [])]
    k = 4
    okfmt = (isinstance(p, int) and is_prime(p) and isinstance(I, int) and (I * I + 1) % p == 0
             and len(rows) == len(cols) == len(set(rows)) == len(set(cols))
             and all(len(U) == k and list(U) == sorted(set(U)) and y not in U and 0 <= y < 8 for y, U in rows)
             and all(len(T) == k and list(T) == sorted(set(T)) and x in T and 0 <= x < 8 for x, T in cols))
    if not okfmt:
        return 0, "format rejected (prime, square root of -1, distinct rows in S^c and columns in S)"
    K = kernel_modp(3, p, I)
    dets = {}

    def lam(U, T):
        if (U, T) not in dets:
            dets[(U, T)] = det_modp([[K[u][t] for t in T] for u in U], p)
        return dets[(U, T)]
    M = [[K[y][x] * lam(U, T) % p for (x, T) in cols] for (y, U) in rows]
    d = det_modp(M, p)
    return (len(rows) if d else 0), f"minor of K_W[S^c,S] of size {len(rows)}, det mod {p} = {d}"


def check_b2_cert(C2, H):
    basis = [(b[0], tuple(b[1])) for b in C2.get("basis_S", [])]
    okb = len(basis) == len(set(basis)) == len(H.S) and all(x in T for x, T in basis)
    if not okb:
        return None, "basis rejected"
    g2 = H.matmul(H.two_dir(1), H.two_dir(2))
    vecs = [{basis[int(key)]: (c[0], c[1]) for key, c in v.items()} for v in C2.get("vectors", [])]
    cache = {}
    bad = sum(1 for v in vecs if any(y not in U for (y, U) in H.apply_W(g2, v, cache)))
    pB = 1000000007 + 2
    while not (is_prime(pB) and pB % 4 == 1):
        pB += 1
    IB = sqrt_minus_one(pB)
    bidx = {b: i for i, b in enumerate(basis)}
    Vm = [[0] * len(H.S) for _ in vecs]
    for r, v in enumerate(vecs):
        for key, c in v.items():
            Vm[r][bidx[key]] = (c[0] + c[1] * IB) % pB
    rk = rank_modp(Vm, pB)
    if bad or rk != len(vecs):
        return None, f"{len(vecs)} vectors, images outside N {bad}, rank {rk}: rejected"
    return len(H.S) - rk, (f"{len(vecs)} exact vectors v in N with (dir 1 dir 2)_W v in N, independent "
                           f"(rank mod {pB} = {rk}) -> raise <= {len(H.S) - rk}")


def check_m0_json(C3):
    p3, I3 = C3.get("p"), C3.get("I")
    r3 = [tuple(U) for U in C3.get("rows", [])]
    c3 = [tuple(T) for T in C3.get("cols", [])]
    k = 4
    okf = (is_prime(p3) and (I3 * I3 + 1) % p3 == 0 and len(r3) == len(c3) == len(set(r3)) == len(set(c3))
           and all(0 not in U and len(U) == k and list(U) == sorted(set(U)) for U in r3)
           and all(0 in T and len(T) == k and list(T) == sorted(set(T)) for T in c3))
    if not okf:
        return 0, "format rejected"
    K3 = kernel_modp(3, p3, I3)

    def M0(U, T):
        return sum(K3[0][s] * det_modp([[K3[u][t ^ s] for t in T] for u in U], p3) for s in range(8)) % p3
    d = det_modp([[M0(U, T) for T in c3] for U in r3], p3)
    return (len(r3) if d else 0), f"minor of size {len(r3)}, det mod {p3} = {d}"


def check_m0_text(text):
    """Port of check_m0.c: M_alpha[U][T] = sum_s (-1)^(alpha.s) Q[0][s] det(Q[u_a][t_b xor s]),
    Q[u][v] = (-i)^popcount(u xor v); rows: k-subsets of {1..n-1}; columns: k-subsets containing 0."""
    tok = text.split()
    try:
        hdr = dict(zip(tok[0:12:2], tok[1:12:2]))
        m, k, alpha = int(hdr["m"]), int(hdr["k"]), int(hdr["alpha"])
        p, I, size = int(hdr["p"]), int(hdr["I"]), int(hdr["size"])
        pairs = [(int(tok[12 + 2 * i]), int(tok[13 + 2 * i])) for i in range(size)]
    except (KeyError, ValueError, IndexError):
        return 0, "header or body rejected"
    n = 1 << m
    prime = 2 < p < (1 << 31) and is_prime(p)
    okI = I * I % p == p - 1
    seenR, seenC, okS = set(), set(), True
    for R, C in pairs:
        if R >> n or C >> n or popc(R) != k or popc(C) != k or (R & 1) or not (C & 1) or R in seenR or C in seenC:
            okS = False
        seenR.add(R)
        seenC.add(C)
    if not (prime and okI and okS):
        return 0, f"format rejected (p prime: {prime}, I^2 = -1: {okI}, rows/cols well formed and distinct: {okS})"
    mi = [1, p - I, p - 1, I]
    A = []
    for R, _ in pairs:
        u = [x for x in range(n) if R >> x & 1]
        row = []
        for _, Cm in pairs:
            t = [x for x in range(n) if Cm >> x & 1]
            acc = 0
            for s in range(n):
                B = [[mi[popc(ua ^ tb ^ s) & 3] for tb in t] for ua in u]
                term = mi[popc(s) & 3] * det_modp(B, p) % p
                if popc(alpha & s) & 1:
                    term = (p - term) % p
                acc = (acc + term) % p
            row.append(acc)
        A.append(row)
    d = det_modp(A, p)
    return (size if d else 0), f"m = {m}, {size} x {size} minor of M_{alpha}, det mod {p} = {d}"


# ---------------------------------------------------------- Lean data (Dem3Data)

def load_dem3data(path):
    text = open(path, encoding="utf-8").read()
    out = {}
    for name in ("rowsD", "colsD", "invD"):
        key = "def " + name + " : List (List (List ℕ)) := "
        i = text.find(key)
        if i < 0:
            return None
        j = text.find("\n", i)
        out[name] = json.loads(text[i + len(key):j])
    return out


PWZ = [1, -256, -256, 65536, -256, 65536, 65536, -16777216]     # (-256)^popcount(z), as in Dem3Defs.lean


def chiZ(s, u):
    return [1, -1, -1, 1, -1, 1, 1, -1][s & u]


def det4(mx):
    """The Laplace expansion on rows 0, 1 written in Dem3Defs.lean."""
    m = mx
    return ((m[0][0] * m[1][1] - m[0][1] * m[1][0]) * (m[2][2] * m[3][3] - m[2][3] * m[3][2])
            - (m[0][0] * m[1][2] - m[0][2] * m[1][0]) * (m[2][1] * m[3][3] - m[2][3] * m[3][1])
            + (m[0][0] * m[1][3] - m[0][3] * m[1][0]) * (m[2][1] * m[3][2] - m[2][2] * m[3][1])
            + (m[0][1] * m[1][2] - m[0][2] * m[1][1]) * (m[2][0] * m[3][3] - m[2][3] * m[3][0])
            - (m[0][1] * m[1][3] - m[0][3] * m[1][1]) * (m[2][0] * m[3][2] - m[2][2] * m[3][0])
            + (m[0][2] * m[1][3] - m[0][3] * m[1][2]) * (m[2][0] * m[3][1] - m[2][1] * m[3][0]))


def genZ(s, us, ts):
    tz = [0] + list(ts)
    return sum(chiZ(s, u) * PWZ[u] * det4([[PWZ[us[b] ^ u ^ tz[a]] for a in range(4)] for b in range(4)])
               for u in range(8))


def block_check(D, s, bad_entry=False):
    rows, cols, inv = D["rowsD"][s], D["colsD"][s], D["invD"][s]
    if not (len(rows) == len(cols) == len(inv) == 28 and all(len(r) == 28 for r in inv)):
        return False, "shape rejected"
    okset = (len(set(map(tuple, rows))) == 28 and len(set(map(tuple, cols))) == 28
             and all(len(u) == 4 and list(u) == sorted(set(u)) and all(1 <= x <= 7 for x in u) for u in rows)
             and all(len(t) == 3 and list(t) == sorted(set(t)) and all(1 <= x <= 7 for x in t) for t in cols))
    if not okset:
        return False, "row or column representatives rejected"
    G = [[genZ(s, rows[k], cols[j]) for j in range(28)] for k in range(28)]
    B = [r[:] for r in inv]
    if bad_entry:
        B[0][0] = B[0][0] + 1
    for i in range(28):
        for j in range(28):
            v = sum(B[i][k] * G[k][j] for k in range(28)) - (1 if i == j else 0)
            if v % 65537 != 0:
                return False, f"entry ({i},{j}) of certificate x formula - identity is {v % 65537} mod 65537"
    return True, "certificate x formula = identity mod 65537 on all 784 entries"


def part_leandata():
    D = load_dem3data(os.path.join(DATA, "Dem3Data.lean"))
    if D is None:
        return report("leandata parse", False, "Dem3Data.lean not parsed")
    ok = report("leandata parse", all(len(D[k]) == 8 for k in D), "rowsD, colsD, invD: 8 blocks each")
    tot = 0
    for s in range(8):
        good, msg = block_check(D, s)
        ok &= report(f"leandata block {s}", good, msg)
        tot += 28 if good else 0
    ok &= report("leandata total", tot == 224, f"8 blocks of rank 28 mod 65537: {tot}")
    return ok


# ------------------------------------------------------------------- face3 (C3)

def face3_setup():
    n, m = 8, 3
    triples = list(itertools.combinations(range(n), 3))
    face = lambda T: any(len({(x >> j) & 1 for x in T}) == 1 for j in range(m))
    F = [T for T in triples if face(T)]
    NF = [T for T in triples if not face(T)]
    return F, NF


def det3g(A, S, T):
    return gdet([[A[s][t] for t in T] for s in S])


def leak3(A, F, NF):
    r, even = rank_exact_gauss([[det3g(A, S, T) for T in F] for S in NF])
    return r if even else None


def part_face3():
    n = 8
    H = Hook(3, 1)      # for two_dir / matmul only
    F, NF = face3_setup()
    ok = report("face3 face triples", len(F) == 24 and len(NF) == 32, f"{len(F)} face triples of {len(F) + len(NF)}")

    def shift(a):
        M = [[ZERO] * n for _ in range(n)]
        for x in range(n):
            M[x ^ a][x] = ONE
        return M
    leaks = [leak3(shift(a), F, NF) for a in range(n)]
    ok &= report("face3 shifts keep N", all(v == 0 for v in leaks), f"leaks {leaks}")
    ipow = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    diag_ok = True
    for z, c, q in [(1, 0, 0), (3, 1, 0), (7, 2, 0), (5, 3, 1)]:
        D = [[ZERO] * n for _ in range(n)]
        for x in range(n):
            e = (popc(z & x) + c + 2 * q * ((x & 1) * ((x >> 1) & 1))) % 4   # i^(z.x + c) times a CZ-type sign
            D[x][x] = ipow[e]
        diag_ok &= leak3(D, F, NF) == 0
    ok &= report("face3 diagonal phases keep N", diag_ok, "four phase patterns, leak 0")
    caps = {w: leak3(H.two_dir(w), F, NF) for w in range(1, n)}
    ok &= report("face3 cap", all(v == 8 for v in caps.values()), f"caps per direction {caps}")
    vecs = list(range(1, n))
    bases = [b for b in itertools.combinations(vecs, 3) if b[2] not in {0, b[0], b[1], b[0] ^ b[1]}]
    dems = {}
    for b in bases:
        K = H.matmul(H.matmul(H.two_dir(b[0]), H.two_dir(b[1])), H.two_dir(b[2]))
        dems[b] = leak3(K, F, NF)
    hist = {v: list(dems.values()).count(v) for v in set(dems.values())}
    ok &= report("face3 demand", len(bases) == 28 and hist == {24: 28}, f"{len(bases)} bases, demand histogram {hist}")
    ok &= report("face3 bound", Fraction(24, 8) == 3, "demand/cap = 24/8 = 3 calls per array: s >= 3W (with the kept-subspace bound and the transfer of PROOF.md)")
    return ok


# ------------------------------------------------------------------------ block 4

def part_block4():
    cap = (16 // 2) * math.comb(14, 7)
    ok = report("block4 cap formula", cap == 27456, f"(2^4/2) C(2^4 - 2, 7) = {cap} (hook_cap, proved in Lean for every block)")
    ok &= report("block4 demand split", 16 * 5412 == 86592, "16 character blocks x 5,412 = 86,592 (split argued by hand)")
    ok &= report("block4 ratio", Fraction(86592, 27456) == Fraction(41, 13), f"86,592/27,456 = {Fraction(86592, 27456)}")
    text = open(os.path.join(DATA, "cert_m4_M0.txt")).read()
    good, msg = m4_format(text)
    ok &= report("block4 certificate format", good, msg)
    return ok


def m4_format(text):
    tok = text.split()
    try:
        hdr = dict(zip(tok[0:12:2], tok[1:12:2]))
        m, k, alpha = int(hdr["m"]), int(hdr["k"]), int(hdr["alpha"])
        p, I, size = int(hdr["p"]), int(hdr["I"]), int(hdr["size"])
        pairs = [(int(tok[12 + 2 * i]), int(tok[13 + 2 * i])) for i in range(size)]
    except (KeyError, ValueError, IndexError):
        return False, "header or body rejected"
    n = 1 << m
    rows = [r for r, _ in pairs]
    cols = [c for _, c in pairs]
    good = (m == 4 and k == 8 and alpha == 0 and size == 5412 and is_prime(p) and I * I % p == p - 1
            and len(set(rows)) == size and len(set(cols)) == size
            and all(r >> n == 0 and popc(r) == k and not (r & 1) for r in rows)
            and all(c >> n == 0 and popc(c) == k and (c & 1) for c in cols)
            and len(tok) == 12 + 2 * size)
    return good, (f"m = {m}, k = {k}, p = {p} (prime: {is_prime(p)}), I^2 = -1: {I * I % p == p - 1}, "
                  f"{size} distinct rows (8-subsets without 0) and columns (8-subsets with 0); "
                  "its determinant 1797789153 mod p is author evidence (check_m0.c), not re-run here")


# ------------------------------------------------------------------ depth (block 4)
# The inputs a_2 = f(dir e1 dir e2) and a_3 = f(dir e1 dir e2 dir e3) of PROOF.md section 7. A product g of
# moves on the low j bits acts as G (x) I on V = C^(2^j) (x) C^(2^(4-j)): V = (+)_c W_c over the 2^(4-j) values c
# of the untouched bits, W_c = C^d (d = 2^j), and g = G on every W_c. So Lambda^k V = (+) over (k_c) of
# (x)_c Lambda^(k_c) W_c, and the hook splits the same way: N = (+) over (c0, (k_c)) of
# N1(W_c0, k_c0) (x) (x)_(c != c0) Lambda^(k_c) W_c, with N1(W, s) = span{e_x (x) e_S : x in S} in W (x) Lambda^s W.
# g keeps every summand and is invertible on the full factors, so
#   f(g) = sum over (k_c) with sum k_c = k, and over c0, of phi_d(k_c0) * prod_(c != c0) C(d, k_c),
# phi_d(s) = rank of G (x) Lambda^s G from N1(W, s) to its complement (at most 280 x 280 here). G is
# ((1+i)/2)^j times Q_j[u][v] = (-i)^popcount(u xor v), entries in Z[i]; a rank mod p (p = 1 mod 4, i -> sqrt(-1))
# is at most the rank over Q(i), so every value below is a lower bound. (The split is the route of an AI
# reviewer of my repository, skeptic-checks/fcheck.py there.)

DEPTH_CERTS = {2: ("cert_m4_g2_M0.txt", 3, 3036, 48576), 3: ("cert_m4_g3_M0.txt", 7, 4270, 68320)}


def local_rank(G, s, p):
    d = len(G)
    subs = list(itertools.combinations(range(d), s))
    minor = {(S, T): (det_modp([[G[x][y] for y in T] for x in S], p) if s else 1) for S in subs for T in subs}
    rows = [(y, S) for S in subs for y in range(d) if y not in S]
    cols = [(x, T) for T in subs for x in T]
    if not rows or not cols:
        return 0
    return rank_modp([[G[y][x] * minor[(S, T)] % p for (x, T) in cols] for (y, S) in rows], p)


def q_moves(j, p, I):
    mi = [1, p - I, p - 1, I]                       # (-i)^0..3 mod p
    d = 1 << j
    return [[mi[popc(u ^ v) & 3] for v in range(d)] for u in range(d)]


def split_demand(m, k, j, phi):
    d, nb = 1 << j, 1 << (m - j)
    tot = 0
    for comp in itertools.product(range(d + 1), repeat=nb):
        if sum(comp) != k:
            continue
        for c0 in range(nb):
            prod = 1
            for c in range(nb):
                if c != c0:
                    prod *= math.comb(d, comp[c])
            tot += phi[comp[c0]] * prod
    return tot


def demand_of_moves(m, k, j, p, G=None):
    I = sqrt_minus_one(p)
    G = q_moves(j, p, I) if G is None else G
    phi = {s: local_rank(G, s, p) for s in range((1 << j) + 1)}
    return split_demand(m, k, j, phi)


def n_counts(k, r):
    """Projection counts of PROOF.md section 7 (the closed form of the induction note, its Lemma 2), block k."""
    return {r: (2 ** (k - r) - 1) + (4 ** k - 2 ** (k + r)),
            r - 1: 2 * (2 ** k - 2 ** (k - r)) + (2 ** r - 1) * 2 ** (r - 1) * 2 ** (k - r),
            r - 2: (2 ** r - 1) * (2 ** (r - 1) - 1) * 2 ** (k - r)}


def projected_bounds(profile, upto):
    prof, out = dict(profile), {}
    for k in range(5, upto + 1):
        prof = {r: sum(c * prof.get(s, 0) for s, c in n_counts(k, r).items() if s >= 0) for r in range(1, k + 1)}
        out[k] = Fraction(prof[k], prof[1])
    return out


def depth_format(text, lab, size):
    tok = text.split()
    try:
        hdr = dict(zip(tok[0:14:2], tok[1:14:2]))
        m, k, lb, alpha = int(hdr["m"]), int(hdr["k"]), int(hdr["lab"]), int(hdr["alpha"])
        p, I, sz = int(hdr["p"]), int(hdr["I"]), int(hdr["size"])
        pairs = [(int(tok[14 + 2 * i]), int(tok[15 + 2 * i])) for i in range(sz)]
    except (KeyError, ValueError, IndexError):
        return False, "header or body rejected"
    n = 1 << m
    rows = [r for r, _ in pairs]
    cols = [c for _, c in pairs]
    good = (m == 4 and k == 8 and lb == lab and alpha == 0 and sz == size and is_prime(p) and I * I % p == p - 1
            and len(set(rows)) == sz and len(set(cols)) == sz
            and all(r >> n == 0 and popc(r) == k and not (r & 1) for r in rows)
            and all(c >> n == 0 and popc(c) == k and (c & 1) for c in cols)
            and len(tok) == 14 + 2 * sz)
    return good, (f"lab = {lb} (wanted {lab}), p = {p} (prime: {is_prime(p)}), size {sz}: {len(set(rows))} distinct "
                  f"rows and {len(set(cols))} distinct columns; its determinants on all 16 characters are author "
                  "evidence (check_mj.c), not re-run here")


def part_depth():
    ok = True
    got = {j: demand_of_moves(4, 8, j, P1) for j in (1, 2, 3)}
    ok &= report("block4 one move", got[1] == 27456, f"split ranks mod p give {got[1]} = the cap 27,456")
    for j in (2, 3):
        name, lab, size, want = DEPTH_CERTS[j]
        ok &= report(f"block4 {j} moves in independent directions", got[j] >= want,
                     f"split ranks mod p give a_{j} >= {got[j]} (section 7 uses {want:,})")
    b3 = (demand_of_moves(3, 4, 1, P1), demand_of_moves(3, 4, 2, P1))
    ok &= report("same split at block 3", b3 == (80, 144), f"one move {b3[0]}, two moves {b3[1]} (part block3: 80 and 144)")
    T = projected_bounds({0: 0, 1: 27456, 2: got[2], 3: got[3], 4: 86592}, 6)
    ok &= report("block 5 and 6 bounds from this profile", T[5] == BOUNDS[5] and T[6] == BOUNDS[6],
                 f"T_5 = {T[5]}, T_6 = {T[6]} (each grows with a_2, a_3, a_4; the denominator uses only the exact a_1)")
    for j in (2, 3):
        name, lab, size, want = DEPTH_CERTS[j]
        good, msg = depth_format(open(os.path.join(DATA, name)).read(), lab, size)
        ok &= report(f"block4 {j}-move certificate format ({size} x 16 = {16 * size:,})",
                     good and 16 * size == want, msg)
    return ok


# ------------------------------------------------------------------------- width

A_ = (Fraction(1, 2), Fraction(1, 2))       # (1+i)/2
B_ = (Fraction(1, 2), Fraction(-1, 2))      # (1-i)/2


def qmul(x, y):
    return (x[0] * y[0] - x[1] * y[1], x[0] * y[1] + x[1] * y[0])


def qadd(x, y):
    return (x[0] + y[0], x[1] + y[1])


QZ = (Fraction(0), Fraction(0))


def shift_f(vec, v, f):
    """X_v in every one of f digit columns of 3 bits each."""
    mask = 0
    for c in range(f):
        mask |= v << (3 * c)
    return [vec[x ^ mask] for x in range(len(vec))]


def call_f(vec, v, f):
    """C_v^(x)f: in each column apply a I + b X_v."""
    out = vec
    for c in range(f):
        sh = [out[x ^ (v << (3 * c))] for x in range(len(out))]
        out = [qadd(qmul(A_, out[x]), qmul(B_, sh[x])) for x in range(len(out))]
    return out


def kernel_f(vec, f):
    for j in range(3):
        vec = call_f(vec, 1 << j, f)
    return vec


def zero_call_program(vec, f):
    """One array r and one zero scratch s; per direction: copy, shift (free), mix, clear. No call."""
    r = list(vec)
    for j in range(3):
        s = list(r)                                  # copy (mixing)
        s = shift_f(s, 1 << j, f)                    # free shift in every column
        r = [qadd(qmul(A_, r[x]), qmul(B_, s[x])) for x in range(len(r))]   # mix a r + b s
    return r


def width_diff(f):
    N = 1 << (3 * f)
    diff = 0
    for x0 in range(N):
        e = [QZ] * N
        e[x0] = (Fraction(1), Fraction(0))
        diff += sum(1 for u, w in zip(zero_call_program(e, f), kernel_f(e, f)) if u != w)
    return diff


def part_width():
    d1 = width_diff(1)
    ok = report("width f = 1", d1 == 0, f"the zero-call program equals C^(x)3 at width 1 ({d1} entries differ)")
    d2 = width_diff(2)
    ok &= report("width f = 2", d2 > 0, f"the same program is wrong at width 2 ({d2} of 4096 entries differ)")
    e = [QZ] * 8
    nz = True
    for x0 in range(8):
        e = [QZ] * 8
        e[x0] = (Fraction(1), Fraction(0))
        nz &= all(v != QZ for v in kernel_f(e, 1))
    ok &= report("support", nz, "every entry of C^(x)3 is nonzero, while one call sends a basis vector to at most 2 addresses: without scratch, one array needs 3 calls (the argument of PROOF.md section 4)")
    return ok


# ------------------------------------------------------------------------- table

def saving(m, W, s):
    return math.log(m * W / s) / math.log(m)


def fig(x):
    """The 7.47e-4 style: three significant digits."""
    a = f"{x:.2e}"
    mant, ex = a.split("e")
    return mant + "e" + str(int(ex))


BOUNDS = {   # calls per array, exact, as published
    2: Fraction(2), 3: Fraction(14, 5), 4: Fraction(41, 13),
    5: Fraction(834241, 278850), 6: Fraction(1188222, 399685),
}


def excluded(m, W, s, game="engine"):
    """True if a W-in-s unit at block m is excluded by the bounds this note quotes."""
    if s >= m * W:
        return True   # not a saving at all
    lower = [BOUNDS[m] * W] if game == "engine" else []
    if W == 1:
        lower.append(Fraction(m))            # one array needs m calls
    else:
        lower.append(Fraction(max(W + m, 2 * W)))
    return any(s < b for b in lower)


PRINTED = [   # (m, W, s, figure as printed)
    (3, 4, 11, "7.92e-2"), (3, 5, 14, "6.28e-2"), (3, 6, 17, "5.20e-2"), (3, 7, 20, "4.44e-2"),
    (3, 8, 23, "3.87e-2"), (3, 3, 8, "1.07e-1"), (3, 2, 5, "1.66e-1"), (3, 3, 6, "3.69e-1"),
    (4, 2, 7, "9.63e-2"), (4, 3, 10, "1.32e-1"), (4, 4, 13, "1.50e-1"), (4, 5, 16, "1.61e-1"),
    (4, 6, 19, "1.69e-1"), (4, 3, 11, "6.28e-2"), (4, 4, 15, "4.66e-2"),
    (5, 2, 7, "2.22e-1"), (5, 3, 9, "3.17e-1"),
    (6, 2, 8, "2.26e-1"), (6, 3, 9, "3.87e-1"),
]

CAPS_PRINTED = {3: "6.28e-2", 4: "1.71e-1", 5: "3.19e-1", 6: "3.92e-1"}


def smallest_open(m, Ws, game="engine"):
    out = []
    for W in Ws:
        s = next((s for s in range(1, m * W) if not excluded(m, W, s, game)), None)
        if s is not None:
            out.append((W, s))
    return out


def part_table():
    ok = True
    for m, W, s, want in PRINTED:
        got = fig(saving(m, W, s))
        ok &= report(f"saving {W} in {s} at block {m}", got == want, f"ln({m}*{W}/{s})/ln {m} = {saving(m, W, s):.6f} -> {got}")
    for m, want in CAPS_PRINTED.items():
        got = fig(1 - math.log(float(BOUNDS[m])) / math.log(m))
        ok &= report(f"largest saving left open at block {m}", got == want, f"1 - ln({float(BOUNDS[m]):.5f})/ln {m} -> {got}")
    # exclusions quoted in the text
    ok &= report("block 3 excluded", all(excluded(3, W, s) for W, s in [(2, 5), (3, 7), (3, 8), (4, 11), (5, 13), (6, 16)])
                 and all(excluded(3, W, s) for W in range(1, 5) for s in range(1, 3 * W)),
                 "2 in 5, 3 in 7, 3 in 8, 4 in 11, 5 in 13, 6 in 16 and every unit with 4 or fewer arrays")
    ok &= report("Harvey's shape", 14 * 4 == 56 and 5 * 11 == 55 and 56 > 55 and excluded(3, 4, 11),
                 "4 arrays at block 3: 14 x 4 = 56 > 55 = 5 x 11, so at least 12 calls = 4 x 3 (plain)")
    ok &= report("5 in 14 exactly tight", 14 * 80 == 5 * 224 == 1120 and not excluded(3, 5, 14),
                 "14 x 80 = 5 x 224 = 1,120; not excluded")
    ok &= report("block 4 excluded", all(excluded(4, W, s) for W, s in [(2, 6), (3, 9), (4, 12)]),
                 "2 in 6, 3 in 9, 4 in 12")
    want = {3: [(5, 14), (6, 17), (7, 20), (8, 23)], 4: [(2, 7), (3, 10), (4, 13), (5, 16), (6, 19)],
            5: [(2, 7), (3, 9)], 6: [(2, 8), (3, 9)]}
    got = {3: smallest_open(3, range(5, 9)), 4: smallest_open(4, range(2, 7)),
           5: smallest_open(5, range(2, 4)), 6: smallest_open(6, range(2, 4))}
    ok &= report("smallest shapes not excluded (engine game)", got == want, str(got))
    got_ef = smallest_open(3, range(2, 4), game="everything-free")
    ok &= report("block 3, games with bounded free steps (max(W + 3, 2W) only)", got_ef == [(2, 5), (3, 6)], str(got_ef))
    ok &= report("block 5 and 6: 3 in 9", (not excluded(5, 3, 9)) and (not excluded(6, 3, 9))
                 and 3 * BOUNDS[5] < 9 and 3 * BOUNDS[6] < 9,
                 f"3 x {float(BOUNDS[5]):.5f} = {float(3 * BOUNDS[5]):.4f} < 9, 3 x {float(BOUNDS[6]):.5f} = {float(3 * BOUNDS[6]):.4f} < 9, W + m <= 9")
    ok &= report("block 4 near miss", 5 * 27456 == 137280 and 2 * 68320 == 136640 and 137280 - 136640 == 640,
                 "5 x 27,456 = 137,280 against 2 x 68,320 = 136,640: room 640")
    return ok


# ---------------------------------------------------------------------- controls

def part_controls():
    ok = True
    H3 = Hook(3, 4)
    C = json.load(open(os.path.join(DATA, "cert_m3_dem.json")))
    bad = json.loads(json.dumps(C))
    bad["rows"][1] = bad["rows"][0]
    dem, msg = check_dem3_cert(bad, H3)
    ok &= control("demand certificate with a repeated row", dem != 224, msg)
    bad = json.loads(json.dumps(C))
    bad["p"] = C["p"] + 2 if not is_prime(C["p"] + 2) else C["p"] + 4
    dem, msg = check_dem3_cert(bad, H3)
    ok &= control("demand certificate with a composite modulus", dem != 224, msg)
    bad = json.loads(json.dumps(C))
    used_r = {(r[0], tuple(r[1])) for r in bad["rows"]}
    used_c = {(c[0], tuple(c[1])) for c in bad["cols"]}
    extra_r = next(r for r in H3.Sc if r not in used_r)
    extra_c = next(c for c in H3.S if c not in used_c)
    bad["rows"].append([extra_r[0], list(extra_r[1])])
    bad["cols"].append([extra_c[0], list(extra_c[1])])
    dem, msg = check_dem3_cert(bad, H3)
    ok &= control("claim 'demand >= 225' by a minor with one row and column added", dem == 0, msg)
    bad = json.loads(json.dumps(C))
    y, U = bad["rows"][0]
    bad["rows"][0] = [U[0], U]
    dem, msg = check_dem3_cert(bad, H3)
    ok &= control("demand certificate with a row inside the hook", dem == 0, msg)
    C2 = json.load(open(os.path.join(DATA, "cert_m3_B2.json")))
    bad2 = json.loads(json.dumps(C2))
    basis = [(b[0], tuple(b[1])) for b in C2["basis_S"]]
    g2 = H3.matmul(H3.two_dir(1), H3.two_dir(2))
    leaving = next(i for i, b in enumerate(basis)
                   if any(y not in U for (y, U) in H3.apply_W(g2, {b: ONE}, {})))
    v0 = bad2["vectors"][0]
    old = v0.get(str(leaving), [0, 0])
    v0[str(leaving)] = [old[0] + 1, old[1]]
    f2, msg = check_b2_cert(bad2, H3)
    ok &= control("two-call certificate with one entry changed (a basis vector not kept by dir 1 dir 2 added)",
                  f2 is None, msg)
    bad2 = json.loads(json.dumps(C2))
    bad2["vectors"][1] = bad2["vectors"][0]
    f2, msg = check_b2_cert(bad2, H3)
    ok &= control("two-call certificate with a repeated vector", f2 is None, msg)
    I = sqrt_minus_one(P1)
    att = H3.raise_modp(dir_modp(8, 1, P1, I), P1)
    ok &= control("claim 'cap <= 79 at block 3'", att > 79, f"rank mod p of (dir 1)_W[S^c,S] = {att}")
    for name in ("neg_m3_29.txt", "neg_m3_comp.txt", "neg_m3_dup.txt"):
        r, msg = check_m0_text(open(os.path.join(DATA, name)).read())
        ok &= control(f"M_0 certificate {name}", r == 0, msg)
    D = load_dem3data(os.path.join(DATA, "Dem3Data.lean"))
    good, msg = block_check(D, 0, bad_entry=True)
    ok &= control("Lean data with one inverse entry + 1 (as NegControl.lean)", not good, msg)
    F, NF = face3_setup()
    H = Hook(3, 1)
    cap1 = leak3(H.two_dir(1), F, NF)
    ok &= control("claim 'face cap <= 7'", cap1 is not None and cap1 > 7, f"raise of dir 1 on the face span = {cap1}")
    cnot = [[ZERO] * 8 for _ in range(8)]
    for x in range(8):
        y = x ^ (((x >> 1) & 1) << 0)      # flip bit 0 when bit 1 is set
        cnot[y][x] = ONE
    lk = leak3(cnot, F, NF)
    ok &= control("claim 'every address map keeps the face span'", lk is not None and lk > 0, f"a CNOT address map raises it by {lk}")
    d2 = width_diff(2)
    ok &= control("claim 'the zero-call program is right at every width'", d2 > 0, f"{d2} entries differ at width 2")
    ok &= control("claim '4 in 11 at block 3 is allowed'", excluded(3, 4, 11), "5 x 11 = 55 < 56 = 14 x 4")
    ok &= control("claim '5 in 14 at block 3 is excluded'", not excluded(3, 5, 14), "5 x 14 = 70 = 14 x 5: on the bound, not below it")
    ok &= control("claim '2 in 7 at block 4 is excluded'", not excluded(4, 2, 7), "13 x 7 = 91 >= 82 = 41 x 2")
    text = open(os.path.join(DATA, "cert_m4_g2_M0.txt")).read()
    lines = text.split("\n")
    dup = "\n".join(lines[:2] + [lines[1]] + lines[3:])
    good, msg = depth_format(dup, 3, 3036)
    ok &= control("two-move certificate with a repeated row and column pair", not good, msg)
    good, msg = depth_format(text.replace("lab 3", "lab 1", 1), 3, 3036)
    ok &= control("two-move certificate relabelled as a one-move certificate", not good, msg)
    X = [[0, 1], [1, 0]]                   # dir(e1)^2 = X_e1 up to a scalar: a free shift
    same = demand_of_moves(4, 8, 1, P1, G=X)
    ok &= control("claim 'two moves in the same direction raise the hook by 48,576'", same < 48576,
                  f"(dir e1)^2 is the shift X_e1 (times a scalar); the split gives {same}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--part", choices=["main", "controls", "all"], default="all")
    args = ap.parse_args()
    t0 = time.time()
    ok = True
    if args.part in ("main", "all"):
        for name, fn in [("pins", part_pins), ("block2", part_block2), ("block3", part_block3),
                         ("leandata", part_leandata), ("face3", part_face3), ("block4", part_block4),
                         ("depth", part_depth), ("width", part_width), ("table", part_table)]:
            t = time.time()
            print(f"--- {name}", flush=True)
            ok &= fn()
            print(f"--- {name}: {time.time() - t:.1f} s", flush=True)
        if args.part == "main":
            print(f"{'PASS' if ok else 'FAIL'}_COMPLEX_SMALL_M_LOWER_BOUNDS_MAIN ({time.time() - t0:.1f} s)")
    if args.part in ("controls", "all"):
        t = time.time()
        print("--- controls", flush=True)
        okc = part_controls()
        print(f"--- controls: {time.time() - t:.1f} s", flush=True)
        if args.part == "controls":
            print(f"{'PASS' if okc else 'FAIL'}_COMPLEX_SMALL_M_LOWER_BOUNDS_CONTROLS ({time.time() - t0:.1f} s)")
        ok &= okc
    if args.part == "all":
        print(f"{'PASS' if ok else 'FAIL'}_COMPLEX_SMALL_M_LOWER_BOUNDS_ALL ({time.time() - t0:.1f} s)")
    fails = [n for n, good in RESULTS if not good]
    if fails:
        print("failed: " + "; ".join(fails))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
