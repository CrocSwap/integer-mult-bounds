#!/usr/bin/env python3
"""Exact finite audit of a written Gaussian endpoint-potential argument.

Standard library only. No predecessor arithmetic/checker is imported.
The finite checks are evidence, not a formal proof of the universal bound.
"""
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
from math import gcd
from pathlib import Path
import argparse
import json
import random

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LO = Q(333, 106) / Q(6932, 10000)
HI = Q(355, 113) / Q(693, 1000)
LOG_FACTOR = Q(101, 100)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil(value):
    return -(-value.numerator // value.denominator)


def constant_checks():
    """Rational Taylor enclosures; Machin's identity and atanh(1/3)."""
    def atan_interval(q):
        terms = 12
        partial = sum((-1) ** k * q ** (2 * k + 1) / (2 * k + 1)
                      for k in range(terms))
        return partial, partial + q ** (2 * terms + 1) / (2 * terms + 1)

    a, b = atan_interval(Q(1, 5)), atan_interval(Q(1, 239))
    pi_lo, pi_hi = 16 * a[0] - 4 * b[1], 16 * a[1] - 4 * b[0]
    log_lo = 2 * sum(Q(1, 3) ** (2 * k + 1) / (2 * k + 1) for k in range(12))
    log_hi = log_lo + 2 * Q(1, 3) ** 25 / (25 * (1 - Q(1, 9)))
    require(Q(333, 106) < pi_lo < pi_hi < Q(355, 113), "pi enclosure")
    require(Q(693, 1000) < log_lo < log_hi < Q(6932, 10000), "log(2) enclosure")
    require(Q(201, 100) ** 100 < 2 ** 101, "log2(2.01) enclosure")


def phase(s, t, j):
    """Exact nearest integer, ties upward, for positive or negative j."""
    x = Q(t * j, s)
    return x - (x + Q(1, 2)).__floor__()


def step(s, t, j, h):
    sigma, theta = Q(t, s), Q(t - s, s)
    b, end = phase(s, t, j), phase(s, t, j + h)
    y = b + theta * h
    w = y - end
    exponent = (sigma * h + b) ** 2 - end ** 2
    endpoint = (end ** 2 - b ** 2) / theta
    gap = sigma / theta * w * (2 * y - w)
    require(w.denominator == 1, "phase carry must be integral")
    require(exponent == sigma * h * h + endpoint + gap, "step identity")
    require(gap >= 0, "step remainder must be nonnegative")
    return exponent, endpoint, gap


def integer_path(s, t, j, moves):
    """Independent oracle: integer phase numerators, no Fraction step formula.

    All Gaussian exponents are multiplied by s^2; modulo arithmetic replaces
    nearest-integer evaluation. The endpoint bound is cross-multiplied.
    """
    def numerator(k):
        return ((2 * t * k + s) % (2 * s) - s) // 2

    start = numerator(j)
    total = 0
    energy = 0
    for h in moves:
        before, after = numerator(j), numerator(j + h)
        total += (t * h + before) ** 2 - after ** 2
        energy += h * h
        j += h
    end = numerator(j)
    slack = (t - s) * (total - t * s * energy) - s * (end * end - start * start)
    require(slack >= 0, "integer path inequality")
    return total, slack


def audit_path(s, t, j, moves):
    initial = j
    exponent = Q(0)
    gaps = Q(0)
    for h in moves:
        x, _, gap = step(s, t, j, h)
        exponent += x
        gaps += gap
        j += h
    energy = Q(t, s) * sum(h * h for h in moves)
    endpoint = (phase(s, t, j) ** 2 - phase(s, t, initial) ** 2) / Q(t - s, s)
    require(exponent == energy + endpoint + gaps, "path telescope")
    total, slack = integer_path(s, t, initial, moves)
    require(exponent * s * s == total, "independent exponent disagreement")
    require(gaps * s * s * (t - s) == slack, "independent slack disagreement")
    require(exponent >= energy - Q((s // 2) ** 2, s * (t - s)), "phase range bound")


def counts(p, alpha, s, t):
    require(type(p) is int and p > 0, "positive integral precision")
    require(type(alpha) is int and alpha >= 2, "integral alpha >= 2")
    require(type(s) is int and type(t) is int and 2 <= s < t and gcd(s, t) == 1,
            "coprime 2 <= s < t")
    a2, theta, sigma = alpha * alpha, Q(t - s, s), Q(t, s)
    decay = LO * a2 * sigma - LOG_FACTOR
    require(decay > 0, "positive decay")
    burn = HI * a2 * Q((s // 2) ** 2, s * (t - s))
    old_burn = HI * a2 * (1 / (4 * theta) + Q(1, 2))
    n = ceil((p + burn) / decay)
    inverse = ceil((p + 1 + burn) / decay)
    require(n * decay - burn >= p, "residual precision")
    require(inverse * decay - burn >= p + 1, "inverse-tail precision")
    same_decay_old = ceil((p + old_burn) / decay)
    require(n <= same_decay_old, "endpoint-only count must not increase")
    result = dict(p=p, alpha=alpha, s=s, t=t, burn=str(burn), decay=str(decay),
                  residual_count=n, inverse_count_if_norm_below_half=inverse,
                  old_endpoint_same_decay_count=same_decay_old)
    if a2 * theta >= 1 and theta < 1:
        original = min(ceil(Q(p, 1) / (a2 * theta)),
                       ceil(Q(p + 1, 4 * a2) + 1 / theta))
        # This check concerns the stated integer domain, not arbitrary reals.
        require(n <= original, "count exceeds predecessor in tested domain")
        result["original_corollary_count"] = original
    return result


def source_check(root):
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    for row in manifest["files"]:
        data = (root / row["path"]).read_bytes()
        require(sha256(data).hexdigest() == row["sha256"], "source drift: " + row["path"])
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        from hashlib import sha1
        require(sha1(blob).hexdigest() == row["git_blob"], "source blob drift")
    return len(manifest["files"])


def rejection_controls():
    # Mathematical controls bypass source hashes and test plausible wrong claims.
    # The first one shows that deleting the endpoint prefactor is unsound.
    x, endpoint, gap = step(4, 5, 2, 1)
    energy = Q(5, 4)
    require(x == Q(1, 2) and endpoint == Q(-3, 4) and gap == 0,
            "fixed no-prefactor witness changed")
    require(x < energy, "zero burn-in mutation was not refuted")
    # Endpoint direction and coefficient are independently falsifiable.
    require(x != energy - endpoint + gap, "reversed endpoint mutation")
    require(x != energy + Q(5, 4) * endpoint + gap, "sigma/theta endpoint mutation")
    require(phase(2, 3, 1) == Q(-1, 2), "half-up tie control")
    # Counting only the residual is insufficient for the inverse tail.
    e = Q(-1, 4)
    require(abs(e ** 2) == Q(1, 16) and abs(e ** 2 / (1 + e)) > Q(1, 16),
            "residual-versus-tail control")
    for args in ((0, 2, 5, 6), (100, 1, 5, 6), (100, 2, 4, 6),
                 (100, 2, 6, 5), (True, 2, 5, 6)):
        try:
            counts(*args)
        except ValueError:
            continue
        raise ValueError("invalid domain accepted")
    return 10


def certificate(root=ROOT):
    pins = source_check(root)
    constant_checks()
    require(Q(201, 100) ** 100 < 2 ** 101, "log2(2.01) bound")
    # With a = pi*alpha^2*sigma > 12 and exp(-a) < 1/4096,
    # sum_{h != 0} exp(-a*h^2) <= 2 exp(-a)/(1-exp(-3a)) < 2.01 exp(-a).
    require(Q(2, 1) / (1 - Q(1, 4096 ** 3)) < Q(201, 100), "Gaussian tail bound")
    pairs = [(s, t) for s in range(2, 33) for t in range(s + 1, 3 * s + 1)
             if gcd(s, t) == 1]
    steps = 0
    for s, t in pairs:
        betas = [phase(s, t, j) for j in range(s)]
        require(min(b * b for b in betas) == 0, "phase minimum")
        require(max(b * b for b in betas) == Q((s // 2) ** 2, s * s), "phase maximum")
        for j in range(s):
            for h in range(-4, 5):
                if h:
                    audit_path(s, t, j, (h,))
                    steps += 1
    paths = 0
    for s, t in ((2, 3), (3, 4), (4, 5), (5, 6), (7, 9), (5, 11)):
        for length in range(1, 5):
            for moves in product((-2, -1, 1, 2), repeat=length):
                for j in range(s):
                    audit_path(s, t, j, moves)
                    paths += 1
    rng = random.Random(62)
    for _ in range(620):
        s = rng.randrange(2, 100)
        t = rng.randrange(s + 1, 4 * s)
        while gcd(s, t) != 1:
            t += 1
        moves = tuple(rng.choice((-8, -3, -1, 1, 3, 8)) for _ in range(rng.randrange(1, 17)))
        audit_path(s, t, rng.randrange(-2 * s, 2 * s), moves)
        paths += 1
    count_cases = 0
    endpoint_savings = 0
    for p in (101, 128, 256, 1024):
        for alpha in range(2, 17):
            if alpha * alpha >= p:
                continue
            for s, t in pairs:
                theta = Q(t - s, s)
                if Q(1, alpha * alpha) <= theta <= Q(1, 4):
                    row = counts(p, alpha, s, t)
                    count_cases += 1
                    endpoint_savings += row["residual_count"] < row["old_endpoint_same_decay_count"]
    examples = [counts(*args) for args in ((101, 2, 4, 5), (128, 4, 15, 16),
                                         (1024, 8, 63, 64), (4096, 16, 255, 256))]
    return dict(status="SCOPED_EXACT_AUDIT_NO_NEW_KAPPA", assignment_seed=62,
                pinned_files=pins, coprime_pairs=len(pairs), exact_steps=steps,
                exact_paths=paths, count_cases=count_cases,
                strict_endpoint_only_count_savings=endpoint_savings,
                controls=rejection_controls(), examples=examples)


def check_receipt(result, expected):
    require(json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "receipt mismatch (including JSON value types)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", type=Path, help="write a new receipt; refuse existing output")
    args = parser.parse_args()
    result = certificate(args.root)
    if args.write:
        with args.write.open("x", encoding="utf-8", newline="\n") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    else:
        expected = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
        check_receipt(result, expected)
    print("PASS_GAUSSIAN_ENDPOINT_POTENTIAL", json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
