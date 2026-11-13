#!/usr/bin/env python3
"""Independent checker for research/cubic-odd-s-shift-floor.

Imports neither verify.py nor build.py, and uses different routes:

* identities are checked by evaluating both sides at six pairwise
  non-proportional points (a binary cubic form is fixed by four), with the
  left side summed child by child;
* programs run in a separate interpreter on six input pairs; every event is
  a linear source change or a cube of a linear form, so y_final - Y is a
  binary cubic form and the registers are linear forms, and agreement at
  these points is an identity;
* the integer-shift classification enumerates the LARGER gap y over the odd
  divisors of S*N(x) and solves the node quadratic for the odd node, instead
  of enumerating divisors d of N(x) (PROOF.md, Remark after Lemma 5);
  modular square roots use Cipolla's method;
* predecessor arities are recomputed (Pell by direct square test).

Prepared by ahrazzle with substantial AI assistance. Apache-2.0.
"""

from __future__ import annotations

import json
import math
import pathlib
import sys
from fractions import Fraction as Q

HERE = pathlib.Path(__file__).resolve().parent
TOP = HERE.parents[1]
POINTS = [(1, 0), (0, 1), (1, 1), (1, -1), (2, 1), (3, -2)]


def stop(why: str) -> None:
    print("INDEPENDENT FAIL:", why)
    sys.exit(1)


def lhs(r: int, A: Q, B: Q) -> Q:
    total = Q(0)
    for i in range(r):
        total += (A + i * B) ** 3
    return total - r * A ** 3


def rhs(rows, weights, A: Q, B: Q) -> Q:
    return sum(Q(w) * (u * A + v * B) ** 3 for (u, v), w in zip(rows, weights))


def two_power(n: int) -> bool:
    return n > 0 and n & (n - 1) == 0


def dyadic(x: Q) -> bool:
    return two_power(x.denominator)


def interpret(r: int, program, Y: Q, A: Q, B: Q):
    y, a, b = Y, A, B
    for _ in range(r):
        y = y + a * a * a
        a = a + b
    for name, val in program:
        k = Q(val)
        if name == "a+=b":
            a = a + k * b
        elif name == "b+=a":
            b = b + k * a
        elif name == "y+=a^3":
            y = y + k * a * a * a
        elif name == "y+=b^3":
            y = y + k * b * b * b
        else:
            stop("unknown event " + name)
    return y, a, b


def program_repairs(r: int, program) -> bool:
    for (A, B), Y in zip(POINTS, (Q(7), Q(-3, 5), Q(0), Q(11, 2), Q(-1), Q(4))):
        A, B = Q(A), Q(B)
        if interpret(r, program, Y, A, B) != (Y + r * A ** 3, A, B):
            return False
    return True


def in_alphabet(program, kind: str) -> bool:
    for name, val in program:
        k = Q(val)
        if k == 0 or not dyadic(k):
            return False
        if kind != "general" and (name not in ("a+=b", "y+=a^3")
                                  or (name == "a+=b" and k.denominator != 1)):
            return False
    return True


# ------------------------------------------------ independent enumeration

def small_primes(limit: int) -> list[int]:
    flags = [True] * (limit + 1)
    flags[0] = flags[1] = False
    for i in range(2, int(limit ** 0.5) + 1):
        if flags[i]:
            for j in range(i * i, limit + 1, i):
                flags[j] = False
    return [i for i, f in enumerate(flags) if f]


def cipolla(n: int, p: int):
    n %= p
    if n == 0:
        return 0
    if pow(n, (p - 1) // 2, p) != 1:
        return None
    t = 0
    while pow((t * t - n) % p, (p - 1) // 2, p) != p - 1:
        t += 1
    w = (t * t - n) % p

    def mul(x, y):
        return ((x[0] * y[0] + x[1] * y[1] * w) % p, (x[0] * y[1] + x[1] * y[0]) % p)

    acc, base, e = (1, 0), (t, 1), (p + 1) // 2
    while e:
        if e & 1:
            acc = mul(acc, base)
        base = mul(base, base)
        e >>= 1
    if acc[0] * acc[0] % p != n:
        stop("Cipolla root")
    return acc[0]


def factor_by_trial(n: int, primes) -> dict[int, int]:
    out: dict[int, int] = {}
    for p in primes:
        if p * p > n:
            break
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


SQUARE_MASKS = {m: {i * i % m for i in range(m)} for m in (64, 63, 65, 11)}


def exact_sqrt(n: int):
    if n < 0:
        return None
    for m, ok in SQUARE_MASKS.items():
        if n % m not in ok:
            return None
    s = math.isqrt(n)
    return s if s * s == n else None


def good_triple(r: int, nodes) -> bool:
    S, n = r * (r - 1) // 2, 2 * r - 1
    if len(set(nodes)) < 3:
        return False
    c0, c1, c2 = nodes
    if 3 * (c0 * c1 + c0 * c2 + c1 * c2) != n * (c0 + c1 + c2) - 3 * S:
        return False
    for j in range(3):
        k, l = nodes[(j + 1) % 3], nodes[(j + 2) % 3]
        w = Q(S * (n - 3 * (k + l)), 3 * (nodes[j] - k) * (nodes[j] - l))
        if w == 0 or not dyadic(w):
            return False
    return True


def classify(r: int, primes) -> list[tuple]:
    """Integer node triples at odd S.  x = smaller gap from the odd-parity
    node (|x| < 2S), y = larger gap; y | odd part of S*N(x), N = 3x^2 - M."""
    S, n = r * (r - 1) // 2, 2 * r - 1
    M = 2 * r * r - 2 * r - 1
    fS = factor_by_trial(S, primes)
    xs = list(range(1, 2 * S, 2))
    val = [abs(3 * x * x - M) for x in xs]
    fac = [dict() for _ in xs]
    lim = math.isqrt(max(val)) + 1
    for p in primes:
        if p > lim:
            break
        if p == 2 or (p == 3 and M % 3):
            continue
        if p == 3:
            hits = range(len(xs))
        else:
            root = cipolla(M * pow(3, p - 2, p), p)
            if root is None:
                continue
            hits = []
            for t in sorted({root, (p - root) % p}):
                first = t if t % 2 else t + p
                hits.extend(range((first - 1) // 2, len(xs), p))
        for i in hits:
            while val[i] and val[i] % p == 0:
                val[i] //= p
                fac[i][p] = fac[i].get(p, 0) + 1
    found = set()
    for i, xa in enumerate(xs):
        while val[i] and val[i] % 2 == 0:
            val[i] //= 2
        if val[i] > 1:
            fac[i][val[i]] = fac[i].get(val[i], 0) + 1
        N = 3 * xa * xa - M
        if N == 0:
            if S % xa == 0:
                stop(f"r={r}: unhandled family")
            f = dict(fS)
            for p, e in factor_by_trial(xa, primes).items():
                f[p] = f.get(p, 0) + e
        else:
            f = dict(fS)
            for p, e in fac[i].items():
                f[p] = f.get(p, 0) + e
        divisors = [1]
        for p, e in f.items():
            if p != 2:
                divisors = [d * p ** k for d in divisors for k in range(e + 1)]
        for x in (xa, -xa):
            for d in divisors:
                if d < xa:
                    continue
                for y in (d, -d):
                    if N == 0:
                        roots = [-x - 4 * y]
                    else:
                        s = exact_sqrt(4 * (x * x - x * y + y * y) - M)
                        if s is None:
                            continue
                        roots = [-2 * (x + y) + s, -2 * (x + y) - s]
                    for w0 in roots:
                        if (w0 + n) % 6 == 0:
                            c0 = (w0 + n) // 6
                            t = (c0, c0 + x, c0 + y)
                            if good_triple(r, t):
                                found.add(tuple(sorted(t)))
    return sorted(found)


def pell_like(limit: int) -> set[int]:
    out = set()
    for r in range(7, limit + 1):
        m = math.isqrt((r * r - 1) // 3)
        if r * r - 3 * m * m == 1:
            out.add(r)
    return out


def main() -> None:
    data = json.loads((HERE / "CERTIFICATES.json").read_text(encoding="utf-8"))
    prior = json.loads((TOP / "research/cubic-three-query-arities/CERTIFICATES.json")
                       .read_text(encoding="utf-8"))
    certs = data["certificates"]
    kinds: dict[str, list[int]] = {"three-shift": [], "four-shift": [], "general": []}
    for c in certs:
        r, rows = c["r"], [tuple(x) for x in c["rows"]]
        ws = [Q(w) for w in c["weights"]]
        for A, B in POINTS:
            if lhs(r, Q(A), Q(B)) != rhs(rows, ws, Q(A), Q(B)):
                stop(f"identity r={r} at {(A, B)}")
        if any(w == 0 or not dyadic(w) for w in ws):
            stop(f"weight ring r={r}")
        if any(math.gcd(u, v) != 1 for u, v in rows):
            stop(f"row not primitive r={r}")
        if len({(Q(v, u) if u else "inf") for u, v in rows}) != len(rows):
            stop(f"repeated direction r={r}")
        if not in_alphabet(c["program"], c["kind"]):
            stop(f"alphabet r={r}")
        if not program_repairs(r, c["program"]):
            stop(f"program r={r}")
        q = sum(1 for e in c["program"] if e[0].startswith("y"))
        if q != len(rows) or c["shears"] != len(c["program"]) - q:
            stop(f"event counts r={r}")
        if c["kind"] != "general" and any(u != 1 for u, _ in rows):
            stop(f"non-monic row in integer-shift certificate r={r}")
        kinds[c["kind"]].append(r)
    print(f"INDEPENDENT PASS {len(certs)} certificates: six-point identities and "
          "six-input program executions")

    primes = small_primes(70000)
    odd = [r for r in range(3, data["r_max"] + 1) if (r * (r - 1)) % 4 == 2]
    table = {r: classify(r, primes) for r in odd}
    sol = [r for r in odd if table[r]]
    rec = data["integer_shift_odd_s"]
    if {int(k): [tuple(t) for t in v] for k, v in rec["three_query_node_sets"].items()} != \
            {r: table[r] for r in sol}:
        stop("node-set table differs")
    if rec["three_query_impossible"] != [r for r in odd if r not in sol]:
        stop("impossible list differs")
    if kinds["three-shift"] != sol or kinds["four-shift"] != rec["three_query_impossible"]:
        stop("program coverage")
    print(f"INDEPENDENT PASS classification: {len(sol)} of {len(odd)} odd-S arities admit "
          f"three integer-shift queries; {sum(map(len, table.values()))} node sets")

    def pow2ish(r: int) -> bool:
        return two_power(r) or two_power(r - 1)

    classes = {r for r in range(3, data["r_max"] + 1)
               if r % 3 == 2 or r in (3, 4) or r % 9 in (0, 1) or pow2ish(r)}
    known = classes | {c["r"] for c in prior["certificates"]} | {24} | pell_like(data["r_max"])
    if set(kinds["general"]) & known or len(kinds["general"]) != 20:
        stop("general-frame novelty")
    if not set(sol) <= known:
        stop("a solvable integer-shift arity outside predecessor classes")
    after = known | set(kinds["general"])
    open_odd = [r for r in rec["three_query_impossible"] if r not in after]
    open_even = [r for r in range(3, data["r_max"] + 1)
                 if (r * (r - 1)) % 4 == 0 and r not in after]
    if data["open_after_package"] != {"odd_s": open_odd, "even_s": open_even}:
        stop("open lists")
    print("INDEPENDENT PASS bookkeeping: 20 new arities; open lists agree")

    # Mutations that must be rejected.
    g = next(c for c in certs if c["kind"] == "general" and c["r"] == 84)
    rows, ws = [tuple(x) for x in g["rows"]], [Q(w) for w in g["weights"]]
    if all(lhs(84, Q(A), Q(B)) == rhs(rows, ws[::-1], Q(A), Q(B)) for A, B in POINTS):
        stop("permuted weights accepted")
    prog = [list(e) for e in g["program"]]
    k = next(i for i, e in enumerate(prog) if e[0] in ("a+=b", "b+=a"))
    prog[k][1] = str(Q(prog[k][1]) + 1)
    if program_repairs(84, prog):
        stop("altered shear accepted")
    prog = [list(e) for e in g["program"]]
    j = next(i for i, e in enumerate(prog) if e[0] == "y+=b^3") if any(
        e[0] == "y+=b^3" for e in prog) else next(i for i, e in enumerate(prog) if e[0] == "y+=a^3")
    prog[j][0] = "y+=a^3" if prog[j][0] == "y+=b^3" else "y+=b^3"
    if program_repairs(84, prog):
        stop("query on the wrong source accepted")
    if in_alphabet([["b+=a", "1"]], "four-shift") or in_alphabet([["a+=b", "1/2"]], "three-shift"):
        stop("integer-shift alphabet too permissive")
    if good_triple(15, (0, 1, 2)) or classify(7, primes) != [(0, 1, 5)]:
        stop("triple test")
    print("INDEPENDENT PASS 5 mutation controls rejected")
    print("PASS_CUBIC_ODD_S_SHIFT_FLOOR_INDEPENDENT")


if __name__ == "__main__":
    main()
