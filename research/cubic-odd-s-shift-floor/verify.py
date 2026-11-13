#!/usr/bin/env python3
"""Primary verifier for research/cubic-odd-s-shift-floor.

Standard library only; every check is exact rational or integer arithmetic.

1. Authenticates the pinned predecessor bytes and the statements used here.
2. Recomputes, from scratch, every integer-shift three-query repair at the
   99 arities 3 <= r <= 200 with S = r(r-1)/2 odd (Theorem A of PROOF.md).
   The search is finite because of Lemmas 2-5, and it is complete.
3. Checks every certificate in CERTIFICATES.json by exact coefficient
   comparison, weight-ring and contract checks.
4. Executes every literal repair program symbolically (all r retained
   children, then the appended events) and on dirty rational inputs.
5. Checks the arity bookkeeping against the predecessor classes.
6. Runs rejection controls that must fail.

Explicit checks raise SystemExit, so they stay active under python -O.
Prepared by ahrazzle with substantial AI assistance. Apache-2.0.
"""

from __future__ import annotations

import hashlib
import json
import math
import pathlib
import random
import sys
from fractions import Fraction

PKG = pathlib.Path(__file__).resolve().parent
ROOT = PKG.parents[1]
R_MAX = 200

PR6653_README = "research/cubic-three-query-arities/README.md"
PR6653_CERTS = "research/cubic-three-query-arities/CERTIFICATES.json"
PR6212_README = "research/dyadic-cubic-repair/README.md"
PR6212_PROOF = "research/dyadic-cubic-repair/PROOF.md"

# Open (unmerged) predecessors, recorded by exact head; not executable inputs.
PR7475_R24 = 24  # ee81d7e993025b62983ac3def76991af1a58eb01
PR7478_HEAD = "233d639b89bed930e4db22e509170dfb62bd1cd9"  # Pell family r^2-3n^2=1


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def require(cond: bool, msg: str) -> None:
    if not cond:
        fail(msg)


# ---------------------------------------------------------------- sources

def authenticate_sources(mutate: str | None = None) -> dict[str, bytes]:
    """Return pinned input bytes after checking their SHA256 pins.

    `mutate` names one input whose in-memory bytes are altered, as a control.
    """
    pins = json.loads((PKG / "SOURCES.json").read_text(encoding="utf-8"))
    out: dict[str, bytes] = {}
    for row in pins["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        if row["path"] == mutate:
            data = data + b" "
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            raise ValueError(f"pinned input changed: {row['path']}")
        out[row["path"]] = data
    return out


# ---------------------------------------------------------------- algebra

def cube(u: Fraction, v: Fraction) -> tuple[Fraction, ...]:
    """Coefficients of (uA + vB)^3 on A^3, A^2B, AB^2, B^3."""
    return (u ** 3, 3 * u * u * v, 3 * u * v * v, v ** 3)


def defect(r: int) -> tuple[Fraction, ...]:
    """sum_{i<r} (A+iB)^3 - r A^3, from direct power sums."""
    s1 = sum(range(r))
    s2 = sum(i * i for i in range(r))
    s3 = sum(i ** 3 for i in range(r))
    return (Fraction(0), Fraction(3 * s1), Fraction(3 * s2), Fraction(s3))


def form_sum(terms) -> tuple[Fraction, ...]:
    acc = [Fraction(0)] * 4
    for u, v, q in terms:
        for k, c in enumerate(cube(Fraction(u), Fraction(v))):
            acc[k] += Fraction(q) * c
    return tuple(acc)


def is_dyadic(x: Fraction) -> bool:
    d = x.denominator
    return d & (d - 1) == 0


def dyadic_ratio(num: int, den: int) -> bool:
    """num/den is a nonzero element of Z[1/2]."""
    if num == 0 or den == 0:
        return False
    d = abs(den) // math.gcd(num, den)
    return d & (d - 1) == 0


def node_weights(r: int, c) -> list[Fraction]:
    """Weights on (A + c_j B)^3 by exact elimination of the first three
    coefficient equations (not by the closed formula)."""
    S1 = Fraction(sum(range(r)))
    S2 = Fraction(sum(i * i for i in range(r)))
    m = [[Fraction(1)] * 3, [Fraction(x) for x in c],
         [Fraction(x) ** 2 for x in c]]
    rhs = [Fraction(0), S1, S2]
    n = 3
    for col in range(n):
        piv = next((i for i in range(col, n) if m[i][col] != 0), None)
        require(piv is not None, "singular node system")
        m[col], m[piv] = m[piv], m[col]
        rhs[col], rhs[piv] = rhs[piv], rhs[col]
        for i in range(n):
            if i != col and m[i][col] != 0:
                f = m[i][col] / m[col][col]
                m[i] = [a - f * b for a, b in zip(m[i], m[col])]
                rhs[i] -= f * rhs[col]
    return [rhs[i] / m[i][i] for i in range(n)]


# ---------------------------------------------------------------- programs

EVENTS = ("a+=b", "b+=a", "y+=a^3", "y+=b^3")


def run_symbolic(r: int, events) -> tuple[tuple, tuple, tuple]:
    """Execute r retained children and the appended events on formal
    arbitrary sources.  Registers are linear forms in (A, B); the output
    change is a cubic form.  Returns (output change, a, b)."""
    a = (Fraction(1), Fraction(0))
    b = (Fraction(0), Fraction(1))
    dy = [Fraction(0)] * 4

    def add_cube(w: Fraction, f) -> None:
        for k, c in enumerate(cube(f[0], f[1])):
            dy[k] += w * c

    for _ in range(r):
        add_cube(Fraction(1), a)
        a = (a[0] + b[0], a[1] + b[1])
    for kind, val in events:
        x = Fraction(val)
        if kind == "a+=b":
            a = (a[0] + x * b[0], a[1] + x * b[1])
        elif kind == "b+=a":
            b = (b[0] + x * a[0], b[1] + x * a[1])
        elif kind == "y+=a^3":
            add_cube(x, a)
        elif kind == "y+=b^3":
            add_cube(x, b)
        else:
            fail(f"unknown event {kind}")
    return tuple(dy), a, b


def run_literal(r: int, events, y: Fraction, a: Fraction, b: Fraction):
    for _ in range(r):
        y += a ** 3
        a += b
    for kind, val in events:
        x = Fraction(val)
        if kind == "a+=b":
            a += x * b
        elif kind == "b+=a":
            b += x * a
        elif kind == "y+=a^3":
            y += x * a ** 3
        elif kind == "y+=b^3":
            y += x * b ** 3
    return y, a, b


def program_ok(r: int, events, rng: random.Random) -> bool:
    dy, a, b = run_symbolic(r, events)
    if dy != (Fraction(r), 0, 0, 0) or a != (1, 0) or b != (0, 1):
        return False
    for _ in range(3):
        Y, A, B = (Fraction(rng.randint(-10 ** 6, 10 ** 6), rng.randint(1, 999))
                   for _ in range(3))
        if run_literal(r, events, Y, A, B) != (Y + r * A ** 3, A, B):
            return False
    return True


def contract_ok(events, alphabet: str) -> bool:
    """integer-shift: only a += k*b (k in Z) and y += q*a^3 (q dyadic).
    general-frame: determinant-one shears with dyadic k and dyadic queries
    on either named source."""
    for kind, val in events:
        x = Fraction(val)
        if kind not in EVENTS or not is_dyadic(x) or x == 0:
            return False
        if alphabet == "integer-shift":
            if kind in ("b+=a", "y+=b^3"):
                return False
            if kind == "a+=b" and x.denominator != 1:
                return False
    return True


def query_count(events) -> int:
    return sum(1 for k, _ in events if k.startswith("y+="))


def shear_count(events) -> int:
    return sum(1 for k, _ in events if not k.startswith("y+="))


# ------------------------------------------------- complete classification

def primes_upto(n: int) -> list[int]:
    sieve = bytearray([1]) * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(n) + 1):
        if sieve[i]:
            sieve[i * i::i] = bytearray(len(range(i * i, n + 1, i)))
    return [i for i in range(n + 1) if sieve[i]]


def sqrt_mod(n: int, p: int) -> int | None:
    """A square root of n modulo the odd prime p (Tonelli-Shanks)."""
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    m, c, t, root = s, pow(z, q, p), pow(n, q, p), pow(n, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1:
            t2 = t2 * t2 % p
            i += 1
        bb = pow(c, 1 << (m - i - 1), p)
        m, c, t, root = i, bb * bb % p, t * bb * bb % p, root * bb % p
    require(root * root % p == n, "modular square root")
    return root


def triple_ok(r: int, c) -> bool:
    """Distinct integer nodes satisfying the node equation with nonzero
    dyadic weights; weights from the closed formula of PROOF.md Lemma 1."""
    S, a = r * (r - 1) // 2, 2 * r - 1
    if len(set(c)) != 3:
        return False
    e1 = c[0] + c[1] + c[2]
    e2 = c[0] * c[1] + c[0] * c[2] + c[1] * c[2]
    if 3 * e2 != a * e1 - 3 * S:
        return False
    for j in range(3):
        k, l = (j + 1) % 3, (j + 2) % 3
        if not dyadic_ratio(S * (a - 3 * (c[k] + c[l])),
                            3 * (c[j] - c[k]) * (c[j] - c[l])):
            return False
    return True


def integer_shift_triples(r: int, primes: list[int]) -> list[tuple[int, int, int]]:
    """All integer node triples giving a three-query dyadic repair at r.

    Complete when S is odd (PROOF.md Lemmas 2-5): exactly one node c0 has
    the other parity; with x = c1-c0 the smaller gap, x is odd, |x| < 2S,
    and d = w0 + 3x divides N = 3x^2 - M, where w0 = 6c0 - (2r-1),
    M = 2r^2 - 2r - 1 and (w0+3x)(w0+x+4y) = N.
    """
    S, a = r * (r - 1) // 2, 2 * r - 1
    M = 4 * S - 1
    n = S                                  # x = 2i+1 for 0 <= i < S
    Ns = [3 * (2 * i + 1) ** 2 - M for i in range(n)]
    rem = [abs(v) for v in Ns]
    fac: list[dict[int, int]] = [dict() for _ in range(n)]
    for i in range(n):
        if rem[i] == 0:
            continue
        for p in (2, 3):
            e = 0
            while rem[i] % p == 0:
                rem[i] //= p
                e += 1
            if e:
                fac[i][p] = e
    top = math.isqrt(max(rem)) + 1
    for p in primes:
        if p > top:
            break
        if p < 5:
            continue
        t = sqrt_mod(M * pow(3, -1, p), p)
        if t is None:
            continue
        for root in {t, (-t) % p}:
            x0 = root if root % 2 else root + p   # odd x, x = root mod p
            for i in range((x0 - 1) // 2, n, p):
                if rem[i] == 0:
                    continue
                e = 0
                while rem[i] % p == 0:
                    rem[i] //= p
                    e += 1
                if e:
                    fac[i][p] = e
    found: set[tuple[int, int, int]] = set()
    for i in range(n):
        xa = 2 * i + 1
        N = Ns[i]
        if N == 0:
            # (w0+3x)(w0+x+4y) = 0.  Branch w0 = -3x gives q0 = -S/x.
            require(S % xa != 0, f"r={r}: unhandled infinite family")
            # Branch w0 = -x-4y: q0 integral forces y | S*x (y odd).
            m = S * xa
            divs = [dv for dv in range(1, math.isqrt(m) + 1) if m % dv == 0]
            divs = sorted(set(divs + [m // dv for dv in divs]))
            for x in (xa, -xa):
                for dv in divs:
                    for y in (dv, -dv):
                        w0 = -x - 4 * y
                        if (w0 + a) % 6 == 0:
                            c0 = (w0 + a) // 6
                            c = (c0, c0 + x, c0 + y)
                            if triple_ok(r, c):
                                found.add(tuple(sorted(c)))
            continue
        if rem[i] > 1:
            fac[i][rem[i]] = fac[i].get(rem[i], 0) + 1
        prod = 1
        for p, e in fac[i].items():
            prod *= p ** e
        require(prod == abs(N), "factorization")
        odd = [1]
        for p, e in fac[i].items():
            if p != 2:
                odd = [o * p ** k for o in odd for k in range(e + 1)]
        v2 = fac[i].get(2, 0)
        # w0 and x are odd, so d = w0+3x and N/d = w0+x+4y are both even.
        ds = [s * (1 << j) * o for j in range(1, v2) for o in odd for s in (1, -1)]
        for x in (xa, -xa):
            for d in ds:
                w0 = d - 3 * x
                if (w0 + a) % 6:
                    continue
                y4 = N // d - d + 2 * x
                if y4 % 4:
                    continue
                y = y4 // 4
                c0 = (w0 + a) // 6
                c = (c0, c0 + x, c0 + y)
                if y not in (0, x):
                    e1 = sum(c)
                    e2 = c[0] * c[1] + c[0] * c[2] + c[1] * c[2]
                    require(3 * e2 == a * e1 - 3 * S, "divisor parametrization")
                    if triple_ok(r, c):
                        found.add(tuple(sorted(c)))
    return sorted(found)


def two_query_integer_shift(r: int) -> bool:
    """Two distinct integer nodes need (c-c')^2 = M/3 and weight S/(c-c')
    dyadic (PROOF.md Lemma 1, two-node case)."""
    S, M = r * (r - 1) // 2, 2 * r * r - 2 * r - 1
    if M % 3:
        return False
    x = math.isqrt(M // 3)
    return x * x == M // 3 and dyadic_ratio(S, x)


# -------------------------------------------------------------- bookkeeping

def is_power_of_two(x: int) -> bool:
    return x >= 1 and x & (x - 1) == 0


def covered_6653(r: int) -> bool:
    """The prior classes tabulated in PR6653 (PR6212, PR6215, PR6246, PR6250)."""
    return (r % 3 == 2 or r in (3, 4) or r % 9 in (0, 1)
            or is_power_of_two(r) or is_power_of_two(r - 1))


def pell_arities(limit: int) -> set[int]:
    """PR7478: equal-weight repairs exist exactly at r^2 - 3n^2 = 1, r >= 7."""
    out, (r, n) = set(), (2, 1)
    while r <= limit:
        if r >= 7:
            out.add(r)
        r, n = 2 * r + 3 * n, r + 2 * n
    return out


# --------------------------------------------------------------------- main

def main() -> None:
    rng = random.Random(20261113)
    src = authenticate_sources()
    r6653 = src[PR6653_README].decode("utf-8")
    c6653 = json.loads(src[PR6653_CERTS].decode("utf-8"))
    r6212 = src[PR6212_README].decode("utf-8")
    p6212 = src[PR6212_PROOF].decode("utf-8")
    require("Every certificate uses only the PR6212 alphabet: integer shears" in r6653,
            "PR6653 alphabet anchor")
    require("`v_j = 6c_j - (2r-1)`" in r6653, "PR6653 open-question substitution anchor")
    require("two queries suffice **only for r=2**" in r6212, "PR6212 two-query anchor")
    require("## Four integer queries for every r" in p6212, "PR6212 four-query anchor")
    unc = [r for r in range(3, 161) if not covered_6653(r)]
    require(c6653["uncovered_arities"] == unc, "PR6653 uncovered list")
    p6653 = {c["r"]: c["directions"] for c in c6653["certificates"]}
    for control in (PR6653_CERTS, PR6212_README):
        try:
            authenticate_sources(mutate=control)
        except ValueError:
            continue
        fail(f"mutated pinned input accepted: {control}")
    print("PASS sources: 4 pinned inputs, 4 anchors, PR6653 uncovered list, 2 byte mutations rejected")

    data = json.loads((PKG / "CERTIFICATES.json").read_text(encoding="utf-8"))
    require(data["r_max"] == R_MAX, "r_max")

    # ---- Theorem A: complete integer-shift classification at odd S.
    primes = primes_upto(70000)
    odd_s = [r for r in range(3, R_MAX + 1) if (r * (r - 1) // 2) % 2]
    require(len(odd_s) == 99, "99 odd-S arities")
    table = {r: integer_shift_triples(r, primes) for r in odd_s}
    solvable = [r for r in odd_s if table[r]]
    impossible = [r for r in odd_s if not table[r]]
    rec = data["integer_shift_odd_s"]
    require(rec["arities"] == odd_s, "recorded odd-S arities")
    require({int(k): [tuple(t) for t in v] for k, v in rec["three_query_node_sets"].items()}
            == {r: table[r] for r in solvable}, "recorded complete node-set table")
    require(rec["three_query_impossible"] == impossible, "recorded impossible list")
    require(len(solvable) == 17 and len(impossible) == 82, "17 / 82 split")
    require(all(not two_query_integer_shift(r) for r in odd_s), "no two-query integer-shift repair")
    for r in (15, 22, 30, 31):
        require(r in impossible, f"r={r} impossible")
    for r in (6, 7, 42, 51, 114):
        require(tuple(sorted(p6653[r])) in table[r], f"PR6653 certificate at r={r} recovered")
    require(all(covered_6653(r) or r in p6653 for r in solvable),
            "every solvable odd-S arity lies in a predecessor class")
    nsets = sum(len(v) for v in table.values())
    print(f"PASS Theorem A: 99 odd-S arities, {nsets} node sets at 17 arities, 82 need four queries")

    # ---- certificates and programs
    seen = {"three-shift": [], "four-shift": [], "general": []}
    for cert in data["certificates"]:
        r, kind = cert["r"], cert["kind"]
        terms = [(row[0], row[1], Fraction(q)) for row, q in zip(cert["rows"], cert["weights"])]
        require(form_sum(terms) == defect(r), f"{kind} identity r={r}")
        require(all(q != 0 and is_dyadic(q) for _, _, q in terms), f"weights r={r}")
        require(all(math.gcd(u, v) == 1 for u, v, _ in terms), f"primitive rows r={r}")
        require(len({Fraction(v, u) if u else None for u, v, _ in terms}) == len(terms),
                f"distinct directions r={r}")
        ev = [tuple(e) for e in cert["program"]]
        alphabet = "general-frame" if kind == "general" else "integer-shift"
        require(contract_ok(ev, alphabet), f"contract r={r}")
        require(query_count(ev) == len(terms), f"query count r={r}")
        require(shear_count(ev) == cert["shears"], f"shear count r={r}")
        require(program_ok(r, ev, rng), f"program r={r}")
        if kind != "general":
            require(all(u == 1 for u, _, _ in terms), f"monic rows r={r}")
            c = [v for _, v, _ in terms]
            w = node_weights(r, c) if len(c) == 3 else None
            if w is not None:
                require(w == [q for _, _, q in terms], f"eliminated weights r={r}")
        if kind == "three-shift":
            require(tuple(sorted(v for _, v, _ in terms)) in table[r], f"node set r={r}")
            require(len(terms) == 3, "three queries")
            seen["three-shift"].append(r)
        elif kind == "four-shift":
            require(len(terms) == 4, "four queries")
            seen["four-shift"].append(r)
        else:
            require(len(terms) == 3, "three queries")
            seen["general"].append(r)
    require(seen["three-shift"] == solvable, "one three-query program per solvable arity")
    require(seen["four-shift"] == impossible, "one four-query program per impossible arity")
    new20 = seen["general"]
    require(len(new20) == 20 and len(set(new20)) == 20, "twenty general-frame arities")
    nonunit2 = [c["r"] for c in data["certificates"]
                if c["kind"] == "general" and sum(row[0] != 1 for row in c["rows"]) >= 2]
    print(f"PASS certificates: {len(solvable)} three-query and {len(impossible)} four-query "
          f"integer-shift programs, 20 general-frame programs (two non-monic rows at {nonunit2})")

    # ---- bookkeeping against predecessors
    pell = pell_arities(R_MAX)
    known = {r for r in range(3, R_MAX + 1)
             if covered_6653(r) or r in p6653 or r == PR7475_R24 or r in pell}
    require(not (set(new20) & known), "a general-frame arity was already covered")
    require(all(r % 4 in (0, 1) for r in new20), "general-frame arities have even S")
    after = known | set(new20)
    open_odd = [r for r in impossible if r not in after]
    open_even = [r for r in range(3, R_MAX + 1)
                 if (r * (r - 1) // 2) % 2 == 0 and r not in after]
    require(len(open_odd) == 38 and len([r for r in impossible if r in known]) == 44,
            "44 of the 82 have predecessor three-query repairs in G; 38 are open")
    require(data["open_after_package"]["odd_s"] == open_odd, "recorded open odd-S list")
    require(data["open_after_package"]["even_s"] == open_even, "recorded open even-S list")
    print(f"PASS bookkeeping: 20 new arities outside PR6653 classes/certificates, PR7475 and "
          f"PR7478; still open r<=200: {len(open_odd)} odd-S, even-S {open_even}")

    # ---- rejection controls (each must fail)
    controls = 0
    gen = next(c for c in data["certificates"] if c["kind"] == "general")
    r0 = gen["r"]
    bad = [(row[0], row[1], Fraction(q)) for row, q in zip(gen["rows"], gen["weights"])]
    bad[0] = (bad[0][0], bad[0][1], bad[0][2] + Fraction(1, 1024))
    require(form_sum(bad) != defect(r0), "control: perturbed weight accepted")
    controls += 1
    terms = [(row[0], row[1], Fraction(q)) for row, q in zip(gen["rows"], gen["weights"])]
    require(form_sum(terms) != defect(r0 + 1), "control: wrong arity accepted")
    controls += 1
    ev = [tuple(e) for e in gen["program"]]
    last = max(i for i, e in enumerate(ev) if not e[0].startswith("y+="))
    require(not program_ok(r0, ev[:last] + ev[last + 1:], rng), "control: missing restore accepted")
    controls += 1
    q1 = next(i for i, e in enumerate(ev) if e[0].startswith("y+=") and i > 0
              and not ev[i - 1][0].startswith("y+="))
    swapped = ev[:q1 - 1] + [ev[q1], ev[q1 - 1]] + ev[q1 + 1:]
    require(not program_ok(r0, swapped, rng), "control: query moved before its shear accepted")
    controls += 1
    drop = [e for i, e in enumerate(ev) if i != next(j for j, f in enumerate(ev) if f[0].startswith("y+="))]
    require(not program_ok(r0, drop, rng), "control: omitted query accepted")
    controls += 1
    require(not contract_ok(ev, "integer-shift") or all(row[0] == 1 for row in gen["rows"]),
            "control: general frame passed as integer shift")
    controls += 1
    three = next(c for c in data["certificates"] if c["kind"] == "three-shift" and c["r"] == 6)
    c = [v for _, v in three["rows"]]
    require(not triple_ok(6, (c[0], c[1], c[2] + 1)), "control: shifted node accepted")
    controls += 1
    # The search is complete only for odd S: at r=12 (S=66) PR6653's
    # same-parity certificate (-21,-5,11) has no odd-one-out node.
    require(triple_ok(12, tuple(p6653[12])), "PR6653 r=12 certificate")
    require(tuple(sorted(p6653[12])) not in integer_shift_triples(12, primes),
            "control: odd-S search reached a same-parity triple")
    controls += 1
    four = next(c for c in data["certificates"] if c["kind"] == "four-shift")
    rows = [list(x) for x in four["rows"]]
    rows[1][1] += 1
    w4 = [Fraction(q) for q in four["weights"]]
    require(form_sum([(u, v, q) for (u, v), q in zip(rows, w4)]) != defect(four["r"]),
            "control: moved four-query node accepted")
    controls += 1
    print(f"PASS controls: {controls} rejection controls failed as required")
    print("PASS_CUBIC_ODD_S_SHIFT_FLOOR")


if __name__ == "__main__":
    main()
