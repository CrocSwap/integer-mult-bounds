#!/usr/bin/env python3
"""Independent semialgebraic audit, without angles or the branch criterion.

Enumerate every root bounding {x in [0,4]: x(4-x)<=s,
x(3-x)^2<=t} using square-free polynomials and Sturm sequences.
The envelope module is imported only for the final comparison.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import runpy


def check(ok, message):
    if not ok:
        raise ValueError(message)


def trim(p):
    p = list(map(F, p))
    while p and p[-1] == 0:
        p.pop()
    return tuple(p)


def evaluate(p, x):
    value = F(0)
    for c in reversed(p):
        value = value * x + c
    return value


def multiply(p, q):
    if not p or not q:
        return ()
    out = [F(0)] * (len(p) + len(q) - 1)
    for i, a in enumerate(p):
        for j, b in enumerate(q):
            out[i + j] += a * b
    return trim(out)


def divide(p, q):
    check(bool(q), "polynomial division by zero")
    rem = list(p)
    out = [F(0)] * max(0, len(p) - len(q) + 1)
    while len(rem) >= len(q):
        offset, factor = len(rem) - len(q), rem[-1] / q[-1]
        out[offset] = factor
        for i, c in enumerate(q):
            rem[offset + i] -= factor * c
        rem = list(trim(rem))
    return trim(out), trim(rem)


def derivative(p):
    return trim([i * p[i] for i in range(1, len(p))])


def gcd(p, q):
    while q:
        p, q = q, divide(p, q)[1]
    return tuple(c / p[-1] for c in p) if p else ()


def sturm(p):
    seq = [p, derivative(p)]
    while seq[-1]:
        rem = divide(seq[-2], seq[-1])[1]
        if not rem:
            break
        seq.append(tuple(-c for c in rem))
    return tuple(q for q in seq if q)


def variations(seq, x):
    signs = [1 if evaluate(p, x) > 0 else -1
             for p in seq if evaluate(p, x) != 0]
    return sum(a != b for a, b in zip(signs, signs[1:]))


def count_roots(seq, lo, hi):
    return variations(seq, lo) - variations(seq, hi)


def isolate(p, bits=64):
    p = divide(p, gcd(p, derivative(p)))[0]
    original = p
    roots = []
    for edge in (F(0), F(4)):
        if evaluate(p, edge) == 0:
            roots.append((edge, edge))
            p = divide(p, (-edge, F(1)))[0]
    seq, pending = sturm(p), [(F(0), F(4))]
    tolerance = F(1, 2 ** bits)
    while pending:
        lo, hi = pending.pop()
        count = count_roots(seq, lo, hi)
        if count == 0:
            continue
        if (count == 1 and hi - lo <= tolerance
                and evaluate(original, lo) != 0 and evaluate(original, hi) != 0):
            roots.append((lo, hi))
            continue
        mid = (lo + hi) / 2
        for denominator in range(3, len(p) + 3):
            if evaluate(p, mid) != 0:
                break
            mid = lo + (hi - lo) / denominator
        check(evaluate(p, mid) != 0, "could not choose nonroot split")
        pending.extend(((lo, mid), (mid, hi)))
    return sorted(roots)


def sign_at_root(poly, whole, interval):
    lo, hi = interval
    if lo == hi:
        value = evaluate(poly, lo)
    else:
        common = gcd(poly, whole)
        if len(common) > 1 and count_roots(sturm(common), lo, hi):
            return 0
        value = evaluate(poly, (lo + hi) / 2)
    return (value > 0) - (value < 0)


@lru_cache(maxsize=512)
def oracle(s, t):
    square, cube = trim((-s, 4, -1)), trim((-t, 9, -6, 1))
    boundary = multiply(multiply(square, cube), (0, -4, 1))
    roots = isolate(boundary)
    feasible = [r for r in roots if sign_at_root(square, boundary, r) <= 0
                and sign_at_root(cube, boundary, r) <= 0]
    check(bool(feasible), "zero should always be feasible")
    return feasible[-1]


def endpoint_fixtures():
    rows = [(F(0), F(4), F(4)), (F(3), F(0), F(3))]
    for bits in (65, 100, 160):
        delta = F(1, 2 ** bits)
        rows.extend([(F(0), 4 - delta, F(0)), (F(0), delta, F(0)),
                     (delta, F(0), F(0)), (3 - delta, F(0), F(0)),
                     (3 + delta, F(0), F(3))])
        for q in (1 + delta, 2 - delta):
            rows.append((4 - q * q, 2 + (q * q - 3) * q, 2 + q))
    return rows


def endpoint_checks():
    for s, t, expected in endpoint_fixtures():
        lo, hi = oracle(s, t)
        check(lo <= expected <= hi, "endpoint-isolation counterexample")
        if expected == 0:
            check((lo, hi) == (0, 0), "isolated zero was enlarged")
        square, cube = trim((-s, 4, -1)), trim((-t, 9, -6, 1))
        boundary = multiply(multiply(square, cube), (0, -4, 1))
        for a, b in isolate(boundary):
            check(a == b or evaluate(boundary, a) * evaluate(boundary, b) != 0,
                  "interior bracket includes another boundary root")
    return len(endpoint_fixtures())


def run():
    squared_envelope = runpy.run_path(str(Path(__file__).with_name("envelope.py")))["squared_envelope"]
    payload, total = [], 0
    for i in range(17):
        for j in range(17):
            s, t = F(i, 4), F(j, 4)
            actual = oracle(s, t)
            branch, lo, hi = squared_envelope(s, t, 80)
            check(max(actual[0], lo) <= min(actual[1], hi),
                  f"independent polynomial mismatch at {s},{t}")
            payload.append([str(s), str(t), branch, *map(str, actual)])
            total += 1
    jumps = 0
    for j in range(33):
        q = 1 + F(j, 32)
        s, t = 4 - q * q, 2 + (q * q - 3) * q
        variants = [t]
        if t:
            variants.append(t - min(t / 2, F(1, 1000000)))
        if t < 4:
            variants.append(t + min((4 - t) / 2, F(1, 1000000)))
        for value in variants:
            actual = oracle(s, value)
            branch, lo, hi = squared_envelope(s, value, 80)
            check(max(actual[0], lo) <= min(actual[1], hi),
                  "independent rational jump mismatch")
            payload.append([str(s), str(value), branch, *map(str, actual)])
            jumps += 1
    controls = 0
    for s, t, false in [(F(1), F(2), F(1)), (F(3), F(0), F(0)),
                         (F(0), F(4), F(0)), (F(0), F(0), F(4))]:
        lo, hi = oracle(s, t)
        check(not lo <= false <= hi, "bad branch survived the independent oracle")
        controls += 1
    digest = hashlib.sha256(json.dumps(payload, separators=(",", ":")).encode()).hexdigest()
    return {"polynomial_budget_pairs": total, "rational_jump_and_sides": jumps,
            "adversarial_endpoint_and_common_root_cases": endpoint_checks(),
            "wrong_endpoint_controls": controls,
            "oracle_digest": digest}


if __name__ == "__main__":
    print("PASS_ASYMMETRIC_PHASE_STURM " + json.dumps(run(), sort_keys=True))
