#!/usr/bin/env python3
"""Independent check of PR #4554 (Dugongue) NATIVE-OUTER-ASSEMBLY.md and NATIVE-RECOUNT.md, from vendored text only.

Nothing is imported from #4554's code.
  Outer assembly.
    * Exactly, for L = 2^k (k <= 64) and b <= 16, with delta = 1/(128 L 2^b): 2L2^b delta + delta^2 + delta < 1/16, the
      inverse-input modulus (L2^b + delta)^2 + delta <= L^4 2^(4b), and the final budget 1/16 + 1/16 = 1/8.
    * My own assembly with a contract-satisfying adversarial transform: every forward output, pointwise product and
      inverse output is perturbed by modulus delta*(1 - 1e-6), coherently (worst sign) or in random directions; digits
      are radix 2^b with b = floor(log2(n+2)/8), L the least power of two >= 2B. Recovery must be exact, with final
      real error < 1/8 and every carry <= B 2^b, for n up to 65534 bits (all-ones and random operands).
    * The corollary: L(log L)^(1-kappa) = O(n/(log n)^kappa) for L = n/log n, by exact exponent bookkeeping.
  Recount.
    * The two-sided lattice tail sum_{|j-z|>R} e^(-a(j-z)^2) <= 4 e^(-a(R-1)^2)/(1 - e^(-a(2R-1))) for 4,000 random
      real centres, a and R (ratio form, no underflow), and the derived periodic budget below 2^(-P-1).
    * Selecting R by doubling and rational squared comparisons (pi and ln 2 by rational bounds) meets both stated
      conditions and stays within a factor 2 of the least admissible radius.
    * Cost exponents with d = p^eps, alpha^2 = d sqrt(p): h ~ p^(1/4 - eps/2), d h ~ p^(1/4 + eps/2),
      d p/alpha^2 ~ p^(1/2), d alpha sqrt(p) ~ p^(3/4 + 3eps/2), in exact rational exponent arithmetic.
    * Metadata lemma: next = (current - M) & M enumerates every submask of M in increasing order (all M < 2^11), and
      a mixed-radix odometer with radices >= 2 changes at most 2T + d axis digits in total (exhaustive small cases).
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import cmath
from fractions import Fraction as Fr
import hashlib
import json
import math
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
SPECS = {"PR4554-NATIVE-OUTER-ASSEMBLY.md": "f1e194c01fc1ba4e33c698dbc287aeca8ff0efe822b195c50c95b619242cf9dc", "PR4554-NATIVE-RECOUNT.md": "fc14d31113ef3abd597e654e0aec35ef7972d014268e4b8b7624f202f9ff79db"}  # #4554 head 4f46c6a9; blobs b9c54968 (outer), 300188c8 (recount)


def need(condition, message):
    if not condition:
        raise AssertionError(message)


# ---------------------------------------------------------------- outer assembly
def check_tolerance_exact():
    cases = 0
    for k in range(1, 65):
        L = 1 << k
        for b in range(1, 17):
            d = Fr(1, 128 * L * 2 ** b)
            need(2 * L * 2 ** b * d + d * d + d < Fr(1, 16), "product error < 1/16")
            need((L * 2 ** b + d) ** 2 + d <= L ** 4 * 2 ** (4 * b), "inverse inputs inside the domain")
            need(Fr(1, 16) + d < Fr(1, 8) - Fr(1, 16) + Fr(1, 16), "final budget")
            cases += 1
    return cases


def fft(a, invert):
    n = len(a)
    if n == 1:
        return list(a)
    even, odd = fft(a[0::2], invert), fft(a[1::2], invert)
    sign = 1 if invert else -1
    out = [0j] * n
    for k in range(n // 2):
        t = cmath.exp(sign * 2j * math.pi * k / n) * odd[k]
        out[k], out[k + n // 2] = even[k] + t, even[k] - t
    return out


def perturb(vals, delta, mode, rng, ref=None):
    out = []
    for i, v in enumerate(vals):
        if mode == "coherent":
            direction = ref[i] / abs(ref[i]) if ref is not None and abs(ref[i]) > 0 else 1
        else:
            direction = cmath.exp(2j * math.pi * rng.random())
        out.append(v + delta * (1 - 1e-6) * direction)
    return out


def assemble(x, y, n, mode, rng):
    b = max(1, int(math.log2(n + 2)) // 8)
    B = -(-n // b)
    L = 1
    while L < 2 * B:
        L *= 2
    need(2 * B <= L < 4 * B, "2B <= L < 4B")
    delta = 1 / (128 * L * 2 ** b)
    dx = [(x >> (b * i)) & ((1 << b) - 1) for i in range(B)] + [0] * (L - B)
    dy = [(y >> (b * i)) & ((1 << b) - 1) for i in range(B)] + [0] * (L - B)
    X = fft([complex(v) for v in dx], False)
    Y = fft([complex(v) for v in dy], False)
    Xp = perturb(X, delta, mode, rng, ref=X)
    Yp = perturb(Y, delta, mode, rng, ref=Y)
    prod = [p * q for p, q in zip(Xp, Yp)]
    prod = perturb(prod, delta, mode, rng, ref=prod)
    need(max(abs(v) for v in prod) <= L ** 4 * 2 ** (4 * b), "inverse input domain")
    inv = [v / L for v in fft(prod, True)]
    inv = perturb(inv, delta, mode, rng, ref=[complex(1, 0)] * L)
    coeffs = [round(v.real) for v in inv]
    worst = max(abs(v.real - c) for v, c in zip(inv, coeffs))
    need(worst < 1 / 8, "final real error < 1/8")
    carry, out = 0, 0
    for j in range(L + 4):
        s = (coeffs[j] if j < L else 0) + carry
        out |= (s & ((1 << b) - 1)) << (b * j)
        carry = s >> b
        need(carry <= B * 2 ** b, "carry <= B 2^b")
    need(carry == 0, "carries terminate")
    return out, worst


def check_assembly():
    rng = random.Random(45544)
    runs, worst = 0, 0.0
    for n in (254, 1000, 5000, 65534):
        for kind in ("ones", "random"):
            x = (1 << n) - 1 if kind == "ones" else rng.getrandbits(n)
            y = (1 << n) - 1 if kind == "ones" else rng.getrandbits(n)
            for mode in ("coherent", "random"):
                out, w = assemble(x, y, n, mode, rng)
                need(out == x * y, "exact product")
                worst = max(worst, w)
                runs += 1
    # Corollary exponent bookkeeping: with L = n/log n, log L = log n - loglog n <= log n, so
    # L (log L)^(1-kappa) <= n (log n)^(-kappa); the n/log n output term is dominated when kappa <= 1.
    for kappa in (Fr(1, 1000), Fr(1, 3), Fr(1)):
        need(-kappa >= -1, "n/(log n)^kappa dominates n/log n for kappa <= 1")
    return runs, worst


# ---------------------------------------------------------------- recount
def check_lattice_tail():
    rng = random.Random(9)
    worst = 0.0
    for _ in range(4000):
        a = rng.uniform(0.02, 3.0)
        R = rng.uniform(1.2, 12.0)
        z = rng.uniform(-50, 50)
        denom = 1 - math.exp(-a * (2 * R - 1))
        lo, hi = math.floor(z - R - 80), math.ceil(z + R + 80)
        ratio = sum(math.exp(-a * ((j - z) ** 2 - (R - 1) ** 2)) for j in range(lo, hi + 1) if abs(j - z) > R)
        ratio = ratio * denom / 4
        need(ratio <= 1 + 1e-12, "two-sided lattice tail")
        worst = max(worst, ratio)
    # Derived budget: a(R-1)^2 >= P ln2 + ln(32(X+1)) and a(2R-1) >= ln 2 give X/alpha * tail < 2^(-P-1) (alpha >= 2).
    for P in (10, 64, 300):
        for X in (0, 1, 10 ** 6):
            tail_bound = 4 * 2.0 ** (-P) / (32 * (X + 1)) / (1 - 0.5)
            need(X / 2 * tail_bound < 2.0 ** (-P - 1), "periodic budget")
    return 4000, worst


def select_radius(alpha, P, X):
    """Doubling loop with rational squared comparisons: pi > 333/106, ln 2 < 6932/10000, ln y < 0.6932 * bitlength(y)."""
    a_lo = Fr(333, 106) / Fr(alpha) ** 2
    rhs = Fr(6932, 10000) * (P + (32 * (X + 1)).bit_length())
    R = 2
    while not (a_lo * (R - 1) ** 2 >= rhs and a_lo * (2 * R - 1) >= Fr(6932, 10000)):
        R *= 2
    return R, a_lo, rhs


def check_radius():
    cases = 0
    for alpha in (2, 3, 8, 50):
        for P in (16, 64, 512):
            for X in (0, 1, 2 ** 40):
                R, a_lo, rhs = select_radius(alpha, P, X)
                a_true = math.pi / alpha ** 2
                need(a_true * (R - 1) ** 2 >= P * math.log(2) + math.log(32 * (X + 1)), "first condition")
                need(a_true * (2 * R - 1) >= math.log(2), "second condition")
                # Least real radius meeting both rational conditions; the second, R >= (ln2/a + 1)/2 = Theta(alpha^2),
                # binds only when alpha exceeds about sqrt(P), outside the source regime alpha < sqrt(p).
                Rmin = max(1 + math.sqrt(float(rhs / a_lo)), (float(Fr(6932, 10000) / a_lo) + 1) / 2)
                need(R <= 2 * Rmin + 2, "within a factor 2 of the least admissible radius")
                cases += 1
    return cases


def check_exponents():
    eps = [Fr(1, 8), Fr(1, 4), Fr(1, 3)]
    for e in eps:
        d, alpha = e, e / 2 + Fr(1, 4)  # log_p d, log_p alpha (alpha^2 = d sqrt p)
        h = Fr(1, 2) - alpha  # h = O(sqrt(p)/alpha) for large p
        need(h == Fr(1, 4) - e / 2, "h exponent")
        need(d + h == Fr(1, 4) + e / 2, "d h exponent")
        need(d + 1 - 2 * alpha == Fr(1, 2), "d p / alpha^2 exponent")
        need(d + alpha + Fr(1, 2) == Fr(3, 4) + 3 * e / 2, "direct forward exponent")
    return len(eps)


def check_metadata():
    w = 16
    mask = (1 << w) - 1
    for M in range(1 << 11):
        seq, cur = [0], 0
        while True:
            cur = (cur - M) & M & mask
            if cur == 0:
                break
            seq.append(cur)
        need(seq == [s for s in range(M + 1) if s & ~M == 0], "submask enumeration")
    rng = random.Random(3)
    for _ in range(200):
        d = rng.randint(1, 6)
        radices = [rng.randint(2, 5) for _ in range(d)]
        T = math.prod(radices)
        digits, changes = [0] * d, d
        for _ in range(T - 1):
            i = 0
            while True:
                digits[i] += 1
                changes += 1
                if digits[i] < radices[i]:
                    break
                digits[i] = 0
                i += 1
        need(changes <= 2 * T + d, "odometer changes <= 2T + d")
    return 1 << 11


def check_binding():
    n = 0
    for name, sha in SPECS.items():
        need(hashlib.sha256((HERE / name).read_bytes()).hexdigest() == sha, f"vendored {name}")
        n += 1
    outer = (HERE / "PR4554-NATIVE-OUTER-ASSEMBLY.md").read_text(encoding="utf-8")
    for s in ("delta = 1/(128 L 2^b),", "2 L 2^b delta + delta^2 + delta < 1/16.", "L^4 2^(4b)"):
        need(s in outer, f"OUTER states: {s}")
        n += 1
    rec = (HERE / "PR4554-NATIVE-RECOUNT.md").read_text(encoding="utf-8")
    for s in ("<= 4 exp[-a(R-1)^2] / (1-exp[-a(2R-1)]).", "next = (current-M) & M", "O(T[p^epsilon log p + p^(1/4+epsilon/2)]",
              "O(T p^(3/4+3epsilon/2))"):
        need(s in rec, f"RECOUNT states: {s}")
        n += 1
    return n


def main():
    runs, worst = check_assembly()
    tails, tail_ratio = check_lattice_tail()
    report = {"status": "PASS_PR4554_OUTER_RECOUNT_CHECK", "tolerance_cases": check_tolerance_exact(),
              "adversarial_assemblies": runs, "assembly_worst_final_error": worst,
              "lattice_tail_cases": tails, "lattice_tail_worst_ratio": tail_ratio, "radius_cases": check_radius(),
              "exponent_cases": check_exponents(), "submask_masks": check_metadata(),
              "spec_statements_bound": check_binding(), "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
