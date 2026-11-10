#!/usr/bin/env python3
"""Bounded checker for the depth-four repetition law of balanced chain words.

Letters 1..4 mean z_l += B_l z_{l-1} with z_0 = x and z_4 = y. N[i][j]
counts scattered subwords i(i+1)...j. A balanced word with m copies of each
letter is correct for target c precisely when every interval count except
N14 is 0 modulo m and N14 = c (mod m).

Theorem checked here (proof in README.md): for d | m and n = m/d, a balanced
word v with n copies of each letter makes v^d correct for target c exactly
when (d odd or n even), (3 does not divide d or 3 divides n), d divides c,
and v is correct modulo n for target c/d.

Standard library only. Read-only: prints a JSON receipt to stdout.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

DEPTH = 4
LETTERS = (1, 2, 3, 4)
INTERVALS = tuple((i, j) for i in LETTERS for j in LETTERS if i <= j)
TARGET = (1, 4)
MAX_D_SMALL = 12  # repetitions tested for blocks with n <= 2
MAX_D_N3 = 4  # repetitions tested for blocks with n = 3
MAX_N = 3
LEMMA_D = 240
LEMMA_N = 60


class CheckFailure(Exception):
    pass


def require(cond: bool, message: str) -> None:
    if not cond:
        raise CheckFailure(message)


def interval_counts(word: tuple[int, ...]) -> dict[tuple[int, int], int]:
    """Literal chronological counts N_ij; appending j adds N_{i,j-1} to N_ij."""
    n = {iv: 0 for iv in INTERVALS}
    for letter in word:
        for i in range(1, letter):
            n[(i, letter)] += n[(i, letter - 1)]
        n[(letter, letter)] += 1
    return n


def balanced_blocks(k: int) -> list[tuple[int, ...]]:
    """Every word with exactly k copies of each of the four letters."""
    out: list[tuple[int, ...]] = []
    rem = [k] * DEPTH
    buf: list[int] = []
    total = DEPTH * k

    def rec() -> None:
        if len(buf) == total:
            out.append(tuple(buf))
            return
        for idx in range(DEPTH):
            if rem[idx]:
                rem[idx] -= 1
                buf.append(idx + 1)
                rec()
                buf.pop()
                rem[idx] += 1

    rec()
    require(len(out) == math.factorial(total) // math.factorial(k) ** DEPTH,
            f"block count for k={k}")
    return out


def is_correct(counts: dict[tuple[int, int], int], m: int, c: int) -> bool:
    for iv in INTERVALS:
        want = c if iv == TARGET else 0
        if (counts[iv] - want) % m:
            return False
    return True


def compositions(i: int, j: int) -> list[list[tuple[int, int]]]:
    """Every split of the interval i..j into consecutive nonempty parts."""
    if i == j:
        return [[(i, i)]]
    out = []
    for cut in range(i, j + 1):
        head = (i, cut)
        if cut == j:
            out.append([head])
        else:
            for tail in compositions(cut + 1, j):
                out.append([head] + tail)
    return out


COMPOSITIONS = {iv: compositions(*iv) for iv in INTERVALS}


def repeated_counts(base: dict[tuple[int, int], int], d: int) -> dict[tuple[int, int], int]:
    """Composition formula: N_I(v^d) = sum_parts C(d, r) prod N_part(v)."""
    out = {}
    for iv, comps in COMPOSITIONS.items():
        total = 0
        for parts in comps:
            prod = 1
            for part in parts:
                prod *= base[part]
            total += math.comb(d, len(parts)) * prod
        out[iv] = total
    return out


def gates(d: int, n: int, c: int) -> bool:
    return (d % 2 == 1 or n % 2 == 0) and (d % 3 != 0 or n % 3 == 0) and c % d == 0


def predicted(base: dict[tuple[int, int], int], d: int, n: int, c: int) -> bool:
    return gates(d, n, c) and is_correct(base, n, (c // d) % n if n > 1 else 0)


def check_shift_lemma() -> int:
    """Under both gates, every non-leading term of the composition formula is 0 mod dn
    for blocks satisfying the pair conditions. Checked on the coefficient level."""
    cases = 0
    for d in range(1, LEMMA_D + 1):
        for n in range(1, LEMMA_N + 1):
            m = d * n
            pair_ok = d % 2 == 1 or n % 2 == 0
            triple_ok = d % 3 != 0 or n % 3 == 0
            c2, c3, c4 = math.comb(d, 2), math.comb(d, 3), math.comb(d, 4)
            # pair shift is C2 n^2; (d-1)n even <=> pair gate
            require(((c2 * n * n) % m == 0) == pair_ok, f"pair shift d={d} n={n}")
            if not pair_ok:
                continue
            # with a = n*alpha etc. the C2 * n * n * (anything) terms vanish
            require((c2 * n * n) % m == 0, "C2 n^2")
            require(((c3 * n ** 3) % d == 0) == triple_ok, f"triple gate d={d} n={n}")
            require(((c3 * n ** 3) % m == 0) == triple_ok, f"triple shift d={d} n={n}")
            if not triple_ok:
                continue
            require((c4 * n ** 4) % m == 0, f"quartic shift d={d} n={n}")
            cases += 1
    return cases


def least_period(word: tuple[int, ...]) -> int:
    length = len(word)
    for p in range(1, length + 1):
        if length % p == 0 and word[p:] + word[:p] == word:
            return p
    raise CheckFailure("unreachable")


def divisors(m: int) -> list[int]:
    return [d for d in range(1, m + 1) if m % d == 0]


def euler_phi(k: int) -> int:
    return sum(1 for j in range(1, k + 1) if math.gcd(j, k) == 1)


def main() -> int:
    blocks = {k: balanced_blocks(k) for k in range(1, MAX_N + 1)}
    base_counts = {k: [interval_counts(v) for v in blocks[k]] for k in blocks}

    # W4(n, c): literal counts of correct n-blocks.
    w4 = {}
    for k in blocks:
        for c in range(k):
            w4[(k, c)] = sum(1 for cnt in base_counts[k] if is_correct(cnt, k, c) or k == 1)
    require(w4[(1, 0)] == 24, "W4(1,0) convention")

    # A + B: literal counts of v^d versus the composition formula and the gate law.
    formula_checks = 0
    word_target_checks = 0
    fixed = {}
    for k in blocks:
        max_d = MAX_D_SMALL if k <= 2 else MAX_D_N3
        for d in range(1, max_d + 1):
            m = d * k
            fix_counts = [0] * m
            for v, base in zip(blocks[k], base_counts[k]):
                lit = interval_counts(v * d)
                require(lit == repeated_counts(base, d), f"composition formula v={v} d={d}")
                formula_checks += 1
                for c in range(m):
                    actual = is_correct(lit, m, c)
                    require(actual == predicted(base, d, k, c),
                            f"gate law v={v} d={d} c={c} actual={actual}")
                    word_target_checks += 1
                    fix_counts[c] += actual
            for c in range(m):
                want = w4[(k, c // d)] if gates(d, k, c) else 0
                require(fix_counts[c] == want, f"F_d count m={m} d={d} c={c}")
                fixed[(m, d, c)] = fix_counts[c]

    # C: full literal census at m = 1, 2, 3; least periods and Burnside.
    census = {}
    for m in range(1, MAX_N + 1):
        for c in range(m):
            correct_words = [v for v, cnt in zip(blocks[m], base_counts[m])
                             if m == 1 or is_correct(cnt, m, c)]
            periods: dict[int, int] = {}
            for w in correct_words:
                p = least_period(w)
                periods[p] = periods.get(p, 0) + 1
            orbits = sum(cnt // p for p, cnt in periods.items())
            require(all(cnt % p == 0 for p, cnt in periods.items()), "orbit sizes")
            burnside_sum = sum(euler_phi(d) * fixed[(m, d, c)] for d in divisors(m))
            require(burnside_sum % (4 * m) == 0 and burnside_sum // (4 * m) == orbits,
                    f"Burnside m={m} c={c}")
            # rotation closure: rotations of correct words are correct
            for w in correct_words:
                r = w[1:] + w[:1]
                require(m == 1 or is_correct(interval_counts(r), m, c), "rotation closure")
            if math.gcd(c, m) == 1 and m > 1:
                require(set(periods) <= {4 * m}, f"coprime primitivity m={m} c={c}")
                require(len(correct_words) % (4 * m) == 0, "4m | W4")
            census[f"{m},{c}"] = {"W4": len(correct_words),
                                  "least_periods": {str(p): periods[p] for p in sorted(periods)},
                                  "cyclic_classes": orbits}

    # Coprime-target primitivity on every tested repetition: F_d = 0 for d > 1.
    for (m, d, c), val in fixed.items():
        if d > 1 and math.gcd(c, m) == 1:
            require(val == 0, f"coprime fixed point m={m} d={d} c={c}")

    lemma_cases = check_shift_lemma()

    # D: false-claim controls. Each must disagree with the literal data.
    controls = {
        "no_pair_gate": lambda base, d, n, c: (d % 3 != 0 or n % 3 == 0) and c % d == 0
        and is_correct(base, n, (c // d) % n if n > 1 else 0),
        "no_triple_gate": lambda base, d, n, c: (d % 2 == 1 or n % 2 == 0) and c % d == 0
        and is_correct(base, n, (c // d) % n if n > 1 else 0),
        "depth_three_cubic_shift": lambda base, d, n, c: (d % 2 == 1 or n % 2 == 0)
        and (c - math.comb(d, 3) * n ** 3) % d == 0
        and is_correct(base, n, ((c - math.comb(d, 3) * n ** 3) // d) % n if n > 1 else 0),
        "quartic_target_shift": lambda base, d, n, c: (d % 2 == 1 or n % 2 == 0)
        and (d % 3 != 0 or n % 3 == 0) and (c - math.comb(d, 4)) % d == 0
        and is_correct(base, n, ((c - math.comb(d, 4)) // d) % n if n > 1 else 0),
        "target_not_divided": lambda base, d, n, c: gates(d, n, c)
        and is_correct(base, n, c % n if n > 1 else 0),
    }
    rejected = {}
    for name, claim in controls.items():
        hit = None
        for k in (1, 2):
            for d in range(1, MAX_D_SMALL + 1):
                m = d * k
                for v, base in zip(blocks[k], base_counts[k]):
                    lit = repeated_counts(base, d)
                    for c in range(m):
                        if claim(base, d, k, c) != is_correct(lit, m, c):
                            hit = {"block": "".join(map(str, v)), "d": d, "c": c}
                            break
                    if hit:
                        break
                if hit:
                    break
            if hit:
                break
        require(hit is not None, f"control {name} not rejected")
        rejected[name] = hit

    here = Path(__file__).resolve().parent
    files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(here.iterdir()) if p.is_file() and p.suffix in {".py", ".json", ".md"}}
    receipt = {
        "status": "PASS_CHAIN_DEPTH_FOUR_REPETITION_LAW",
        "W4_small": {f"{k},{c}": w4[(k, c)] for (k, c) in sorted(w4)},
        "census": census,
        "composition_formula_checks": formula_checks,
        "word_target_gate_checks": word_target_checks,
        "shift_lemma_cases": lemma_cases,
        "rejected_controls": rejected,
        "package_sha256": files,
    }
    json.dump(receipt, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CheckFailure as exc:
        print(f"FAIL_CHAIN_DEPTH_FOUR_REPETITION_LAW: {exc}", file=sys.stderr)
        sys.exit(1)
