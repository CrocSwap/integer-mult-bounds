#!/usr/bin/env python3
"""Independent check of PR #4554 (Dugongue) native FFT multiplier: PROOF.md and FFT-ERROR.md, from vendored text only.

Nothing is imported from #4554's native_fft.py, root_seed.py or recover.py.
  A. The error chain, run as worst-case recurrences in exact rational arithmetic for N = 2^h (h <= 20) and
     beta = 2^b (b <= 8), at the stated S = 2^F: forward amplitudes A_(j+1) = (2+delta)A_j + eta stay below
     4^j(beta+eta/3) <= 2*4^j beta; errors E_(j+1) = 2E_j + delta*A_j + eta stay below the closed form
     delta*beta*N(N-1) + eta(N-1) <= 36N^3 beta/S (1); the pointwise error is <= 112N^5 beta^2/S (2) with product
     modulus <= 5N^4 beta^2 (3); inverse amplitudes stay <= 6*4^j N^4 beta^2; E'_h <= 212N^7 beta^2/S; the normalized
     error is <= 216N^6 beta^2/S (4) <= 2^28 N^8 (F+1)^2 beta^4/S (5). The twiddle recurrence
     a_(j+1) = (1+2d)a_j + 4d gives a_j <= 8jd when 2jd <= 1. The parameter step (5) < 2^(-10 ell - 6) <= 2^-26 and
     delta, eta < 1 are checked exactly at the largest n of every ell in 2..200, with the word budget
     2F + 6ceil(log2 N) + 2b + 8 <= 16(F+16)+20.
  B. A separately written fixed-grid FFT multiplier following the PROOF.md construction: own root of unity (pi by
     Machin, cos/sin by Taylor, floor to the 2^-F grid), twiddles by successive floor-rounded complex products,
     conjugated forward twiddles, two forward transforms, rounded pointwise products, unnormalized inverse, floor
     division by N, nearest-integer recovery and radix-beta carries. Products are exact against Python's
     multiplication (oracle only) on random, all-ones and small exhaustive operands; the observed coefficient error
     and intermediate magnitudes are compared with (4), 1/4 and the 6N^6 beta^2 amplitude bound, and every stored
     value with the global word width.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Fr
import hashlib
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
SPECS = {"PR4554-PROOF.md": "db7d6ceb495e4b111764bdea1905f66c7e6f0921bd8c1e3048054445ad448c41", "PR4554-FFT-ERROR.md": "ca426930df5c449ca8ce432360ba3ac80f12377bcd9a058ad16387d8ad87bef5"}  # #4554 head 4f46c6a9, blobs c7b4777b (PROOF), 53691b10 (FFT-ERROR)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def params(n):
    ell = (n + 2).bit_length()
    b = max(1, ell // 8)
    L = -(-n // b)
    N = 1
    while N < 2 * L:
        N *= 2
    F = 24 * ell + 64
    return ell, b, L, N, F


# ---------------------------------------------------------------- A: the error chain
def chain(h, b, F):
    N, beta, S = 1 << h, Fr(1 << b), Fr(1 << F)
    delta, eta = 32 * N / S, 4 / S
    A, E = beta, Fr(0)
    for j in range(h):
        need(A <= 4 ** j * (beta + eta / 3) <= 2 * 4 ** j * beta, "forward amplitude")
        A, E = (2 + delta) * A + eta, 2 * E + delta * A + eta
    need(A <= 2 * N * N * beta, "A_h <= 2N^2 beta")
    need(E <= delta * beta * N * (N - 1) + eta * (N - 1) <= 36 * N ** 3 * beta / S, "(1)")
    P = E * (2 * N * N * beta + N * beta) + eta
    need(P <= 112 * N ** 5 * beta ** 2 / S, "(2)")
    need((2 * N * N * beta) ** 2 + eta <= 5 * N ** 4 * beta ** 2, "(3)")
    A2, E2 = (2 * N * N * beta) ** 2 + eta, P
    for j in range(h):
        need(A2 <= 6 * 4 ** j * N ** 4 * beta ** 2, "inverse amplitude")
        A2, E2 = (2 + delta) * A2 + eta, 2 * E2 + delta * A2 + eta
    need(A2 <= 6 * N ** 6 * beta ** 2, "inverse data modulus")
    need(E2 <= 212 * N ** 7 * beta ** 2 / S, "E'_h")
    final = E2 / N + eta
    need(final <= 216 * N ** 6 * beta ** 2 / S <= 2 ** 28 * N ** 8 * (F + 1) ** 2 * beta ** 4 / S, "(4) and (5)")
    return final * S / (216 * N ** 6 * beta ** 2)


def check_chain():
    cases, worst = 0, Fr(0)
    for h in range(1, 21):
        for b in (1, 2, 4, 8):
            worst = max(worst, chain(h, b, 24 * max(2, h) + 64))
            cases += 1
    tw = 0
    S = Fr(1 << 20)
    d = 1 / S
    a = Fr(0)
    for j in range(1, 3001):  # 2jd <= 1 throughout
        a = (1 + 2 * d) * a + 4 * d
        need(a <= 8 * j * d, "twiddle recurrence")
        tw += 1
    params_checked = 0
    for ell in range(2, 201):
        n = (1 << ell) - 3  # largest n with this ell; N is nondecreasing in n
        e2, b, L, N, F = params(n)
        need(e2 == ell, "ell")
        S = 1 << F
        need(N < 4 * L <= 4 * n < (1 << (ell + 2)) and F + 1 <= 1 << (ell + 7), "parameter bounds")
        need(2 ** 28 * N ** 8 * (F + 1) ** 2 * 2 ** (4 * b) * 2 ** (10 * ell + 6) < S, "(5) < 2^(-10 ell - 6)")
        need(32 * N < S and 4 < S, "delta, eta < 1")
        logN = N.bit_length() - 1
        need(2 * 12 * N ** 6 * 2 ** (2 * b) * S * S < 1 << (2 * F + 6 * logN + 2 * b + 8), "raw product budget")
        need(2 * F + 6 * logN + 2 * b + 8 <= 16 * (F + 16) + 20, "root width dominates")
        params_checked += 1
    return cases, float(worst), tw, params_checked


# ---------------------------------------------------------------- B: an independent fixed-grid multiplier
def fixed_pi(bits):
    one = 1 << bits

    def arctan_inv(x):
        total, term, k, sign = 0, one // x, 1, 1
        x2 = x * x
        while term:
            total += sign * (term // k)
            term //= x2
            k += 2
            sign = -sign
        return total

    return 4 * (4 * arctan_inv(5) - arctan_inv(239))


def root(N, F):
    """exp(2 pi i/N) floored to the 2^-F grid, from a Taylor series at F+64 bits."""
    G = F + 64
    one = 1 << G
    x = 2 * fixed_pi(G) // N
    c, s, term, k = 0, 0, one, 0
    while term:
        if k % 4 == 0:
            c += term
        elif k % 4 == 1:
            s += term
        elif k % 4 == 2:
            c -= term
        else:
            s -= term
        k += 1
        term = term * x // (one * k)
    return c >> 64, s >> 64


class Word:
    def __init__(self, w):
        self.limit = 1 << w
        self.peak = 0

    def __call__(self, v):
        a = abs(v)
        need(a < self.limit, "stored magnitude below 2^w")
        self.peak = max(self.peak, a)
        return v


def cmul(a, b, S, W):
    re = W(W(a[0] * b[0]) - W(a[1] * b[1]))
    im = W(W(a[0] * b[1]) + W(a[1] * b[0]))
    return (W(re // S), W(im // S))


def fft(data, tw, N, S, W, forward):
    a = list(data)
    j = 0
    for i in range(1, N):  # bit reversal
        bit = N >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j |= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    m = 2
    while m <= N:
        step = N // m
        for start in range(0, N, m):
            for k in range(m // 2):
                w = tw[k * step]
                if forward:
                    w = (w[0], -w[1])
                t = cmul(w, a[start + k + m // 2], S, W)
                u = a[start + k]
                a[start + k] = (W(u[0] + t[0]), W(u[1] + t[1]))
                a[start + k + m // 2] = (W(u[0] - t[0]), W(u[1] - t[1]))
        m *= 2
    return a


def multiply(x, y, n, stats):
    ell, b, L, N, F = params(n)
    S, beta = 1 << F, 1 << b
    W = Word(16 * (F + 16) + 20)
    w1 = root(N, F)
    tw = [(S, 0)]
    for _ in range(N // 2 - 1):
        tw.append(cmul(tw[-1], w1, S, W))
    dx = [((x >> (b * i)) & (beta - 1)) * S for i in range(L)] + [0] * (N - L)
    dy = [((y >> (b * i)) & (beta - 1)) * S for i in range(L)] + [0] * (N - L)
    X = fft([(v, 0) for v in dx], tw, N, S, W, True)
    Y = fft([(v, 0) for v in dy], tw, N, S, W, True)
    Z = fft([cmul(p, q, S, W) for p, q in zip(X, Y)], tw, N, S, W, False)
    inv_peak = max(max(abs(p[0]), abs(p[1])) for p in Z)
    coeffs = [(p[0] // N, p[1] // N) for p in Z]
    # Oracle only: exact convolution coefficients by Kronecker substitution.
    slot = 2 * b + L.bit_length() + 2
    px = sum(((x >> (b * i)) & (beta - 1)) << (slot * i) for i in range(L))
    py = sum(((y >> (b * i)) & (beta - 1)) << (slot * i) for i in range(L))
    pz = px * py
    exact = [(pz >> (slot * k)) & ((1 << slot) - 1) for k in range(N)]
    err = max(max(abs(Fr(c[0], S) - e), abs(Fr(c[1], S))) for c, e in zip(coeffs, exact))
    need(err < Fr(1, 4), "recovery margin")
    bound = Fr(216 * N ** 6 * beta ** 2, S)
    need(err <= bound, "observed error within (4)")
    need(inv_peak <= 6 * N ** 6 * beta ** 2 * S, "inverse amplitude bound")
    digits = [(2 * c[0] + S) // (2 * S) for c in coeffs]  # nearest integer
    carry, out = 0, 0
    for k in range(2 * L + 1):
        s_ = (digits[k] if k < N else 0) + carry
        out |= (s_ % beta) << (b * k)
        carry = s_ // beta
        need(carry <= L * (beta - 1), "carry bound")
    need(carry == 0, "final carry zero")
    stats["worst_error_over_bound"] = max(stats["worst_error_over_bound"], float(err / bound))
    stats["peak_bits_over_width"] = max(stats["peak_bits_over_width"], W.peak.bit_length() / (16 * (F + 16) + 20))
    return out


def check_multiplier():
    rng = random.Random(45541)
    stats = {"products": 0, "worst_error_over_bound": 0.0, "peak_bits_over_width": 0.0, "max_n": 0}
    cases = [(n, x, y) for n in range(1, 5) for x in range(1 << n) for y in range(1 << n)]
    for n in (7, 16, 31, 64, 100, 257, 1000, 4096, 12000):
        cases.append((n, (1 << n) - 1, (1 << n) - 1))
        for _ in range(2):
            cases.append((n, rng.getrandbits(n), rng.getrandbits(n)))
    for n, x, y in cases:
        need(multiply(x, y, n, stats) == x * y, "exact product")
        stats["products"] += 1
        stats["max_n"] = max(stats["max_n"], n)
    return stats


def check_binding():
    bound = 0
    for name, sha in SPECS.items():
        raw = (HERE / name).read_bytes()
        need(hashlib.sha256(raw).hexdigest() == sha, f"vendored {name}")
        bound += 1
    text = (HERE / "PR4554-FFT-ERROR.md").read_text(encoding="utf-8")
    for s in ("E_(j+1) <= 2 E_j + delta A_j + eta,", "<= 36N^3 beta/S.", "<= 112N^5 beta^2/S.", "<= 212N^7 beta^2/S.",
              "216N^6 beta^2/S.", "= 2^(-10ell-6)", "2F + 6ceil(log2 N) + 2b + 8,"):
        need(s in text, f"FFT-ERROR.md states: {s}")
        bound += 1
    proof = (HERE / "PR4554-PROOF.md").read_text(encoding="utf-8")
    for s in ("a_(j+1) ≤ (1+2δ)a_j + 4δ,", "F = 24ell+64", "w = 16(F+16)+20"):
        need(s in proof, f"PROOF.md states: {s}")
        bound += 1
    return bound


def main():
    cases, worst, tw, pc = check_chain()
    report = {"status": "PASS_PR4554_NATIVE_FFT_CHECK", "chain_cases": cases, "chain_worst_final_over_216_bound": worst,
              "twiddle_steps": tw, "ell_values_checked": pc, "multiplier": check_multiplier(),
              "spec_statements_bound": check_binding(), "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
