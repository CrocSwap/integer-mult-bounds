#!/usr/bin/env python3
"""Exact ternary overlapping-projector count, produced by Nick Petalas. Apache-2.0."""

from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
from pathlib import Path
import sys


Q = 3
MASKS = ((0, 1, 0, 1), (0, 0, 1, 1))
FILES = ("README.md", "SOURCES.json", "TASK.json", "VERIFY.json", "verify.py")
TYPES = ("equal", "same_image", "same_kernel", "orthogonal",
         "st_zero", "ts_zero", "generic", "degenerate")
EXPECTED = dict(zip(TYPES, (44, 88, 88, 294, 168, 168, 0, 32)))
TERMINAL = dict(zip(TYPES, (114, 78, 78, 44, 50, 50, 56, 54)))


def need(condition, message):
    if not condition:
        raise ValueError(message)


def dot(a, b):
    need(len(a) == len(b) <= 4, "bounded dot dimensions")
    return sum(x * y for x, y in zip(a, b)) % Q


def identity(n):
    need(1 <= n <= 4, "identity dimension")
    return tuple(tuple(int(i == j) for j in range(n)) for i in range(n))


def multiply(a, b):
    need(1 <= len(a) <= 4 and 1 <= len(b) <= 4, "matrix dimensions")
    need(all(len(r) == len(b) for r in a), "inner dimensions")
    return tuple(tuple(dot(r, c) for c in zip(*b)) for r in a)


def inverse(a):
    n = len(a)
    need(1 <= n <= 4 and all(len(r) == n for r in a), "square dimension")
    b = [list(r) + list(e) for r, e in zip(a, identity(n))]
    for k in range(n):
        pivot = next((i for i in range(k, n) if b[i][k]), None)
        if pivot is None:
            return None
        b[k], b[pivot] = b[pivot], b[k]
        scale = pow(b[k][k], -1, Q)
        b[k] = [z * scale % Q for z in b[k]]
        for i in range(n):
            if i != k:
                factor = b[i][k]
                b[i] = [(u - factor * v) % Q for u, v in zip(b[i], b[k])]
    return tuple(tuple(r[n:]) for r in b)


def splits(n):
    need(n in (3, 4), "split dimension")
    vectors = tuple(product(range(Q), repeat=n))
    return tuple((x, y) for x in vectors for y in vectors if dot(x, y) == 1)


def completion(x, y, reverse=False):
    need(len(x) == len(y) == 4 and dot(x, y) == 1, "split pair")
    pivot = next(i for i, value in enumerate(x) if value)
    indices = [j for j in range(4) if j != pivot]
    if reverse:
        indices.reverse()
    columns = [y]
    for j in indices:
        column = [0] * 4
        column[j] = 1
        column[pivot] = -x[j] * pow(x[pivot], -1, Q) % Q
        columns.append(tuple(column))
    w = tuple(zip(*columns))
    g = inverse(w)
    need(g is not None and g[0] == x, "completion first row")
    need(multiply(g, w) == identity(4), "completion inverse")
    return g, w


def conjugate_diagonal(g, w, mask):
    need(len(g) == len(w) == len(mask) == 4, "conjugation dimension")
    return multiply(g, tuple(tuple(mask[i] * z % Q for z in w[i])
                             for i in range(4)))


def schur(a):
    need(len(a) == 4 and a[0][0] != 0, "nonzero first pivot")
    scale = pow(a[0][0], -1, Q)
    s = tuple(tuple((a[i][j] - a[i][0] * a[0][j] * scale) % Q
                    for j in range(1, 4)) for i in range(1, 4))
    need(multiply(s, s) == s, "residual idempotency")
    # Every nonzero column and row must span the respective rank-one space.
    need(any(any(r) for r in s), "nonzero residual")
    rows = {normalize(r) for r in s if any(r)}
    need(len(rows) == 1, "rank-one residual")
    return s


def normalize(vector):
    need(1 <= len(vector) <= 4 and any(vector), "nonzero projective vector")
    scale = pow(next(z for z in vector if z), -1, Q)
    return tuple(z * scale % Q for z in vector)


def pair_type(s, t):
    need(len(s) == len(t) == 3, "terminal dimension")
    if s == t:
        return "equal"
    images = []
    kernels = []
    for a in (s, t):
        images.append(normalize(next(c for c in zip(*a) if any(c))))
        kernels.append(normalize(next(r for r in a if any(r))))
    if images[0] == images[1]:
        return "same_image"
    if kernels[0] == kernels[1]:
        return "same_kernel"
    st, ts = multiply(s, t), multiply(t, s)
    nz_st, nz_ts = any(any(r) for r in st), any(any(r) for r in ts)
    if not nz_st and not nz_ts:
        return "orthogonal"
    if not nz_st:
        return "st_zero"
    if not nz_ts:
        return "ts_zero"
    trace = sum(st[i][i] for i in range(3)) % Q
    return "degenerate" if trace == 1 else "generic"


def terminal_counts(s, t, pairs):
    need(len(pairs) == 234, "complete second split domain")
    count_s = count_t = joint = 0
    for a, b in pairs:
        ps = s is not None and dot(tuple(dot(a, c) for c in zip(*s)), b) != 0
        pt = t is not None and dot(tuple(dot(a, c) for c in zip(*t)), b) != 0
        count_s += ps
        count_t += pt
        joint += ps and pt
    return count_s, count_t, joint


def enumerate_first(pairs):
    distribution = Counter({kind: 0 for kind in TYPES})
    witnesses = {}
    totals = [0, 0, 0]
    first_counts = [0, 0, 0]
    first_pairs = splits(4)
    need(len(first_pairs) == 2160, "complete first split domain")
    for x, y in first_pairs:
        g, w = completion(x, y)
        matrices = tuple(conjugate_diagonal(g, w, mask) for mask in MASKS)
        residuals = tuple(schur(a) if a[0][0] else None for a in matrices)
        for i in range(2):
            first_counts[i] += residuals[i] is not None
        first_counts[2] += all(s is not None for s in residuals)
        counts = terminal_counts(*residuals, pairs)
        totals = [a + b for a, b in zip(totals, counts)]
        if all(s is not None for s in residuals):
            kind = pair_type(*residuals)
            distribution[kind] += 1
            witnesses.setdefault(kind, (x, y))
            need(counts == (114, 114, TERMINAL[kind]), "terminal class count")
            h, v = completion(x, y, reverse=True)
            alternate = tuple(schur(conjugate_diagonal(h, v, m)) for m in MASKS)
            need(pair_type(*alternate) == kind, "completion-basis invariance")
    need(dict(distribution) == EXPECTED, "original residual distribution")
    need(first_counts == [1368, 1368, 882], "first-pivot counts")
    need(totals == [155952, 155952, 50208], "two-stage split counts")
    return distribution, witnesses, totals, first_counts


def gl3():
    result = []
    for entries in product(range(Q), repeat=9):
        g = tuple(tuple(entries[3 * i:3 * i + 3]) for i in range(3))
        h = inverse(g)
        if h is not None:
            need(multiply(g, h) == identity(3), "GL3 inverse")
            result.append((g, h))
    need(len(result) == 11232, "complete GL3 cardinality")
    return result


def direct_guard(x, y, z, v, mask):
    a = sum(x[i] * mask[i] * y[i] for i in range(4)) % Q
    b = sum(x[i] * mask[i] * v[i] for i in range(4)) % Q
    c = sum(z[i] * mask[i] * y[i] for i in range(4)) % Q
    d = sum(z[i] * mask[i] * v[i] for i in range(4)) % Q
    return a != 0 and (a * d - b * c) % Q != 0


def literal_fibres(witnesses):
    headers = gl3()
    counts = {}
    for kind, (x, y) in sorted(witnesses.items()):
        g, w = completion(x, y)
        passed = 0
        for k, h in headers:
            # Actual second row of diag(1,K)G and column of W diag(1,K^-1).
            z = tuple(sum(k[0][j] * g[j + 1][i] for j in range(3)) % Q
                      for i in range(4))
            v = tuple(sum(w[i][j + 1] * h[j][0] for j in range(3)) % Q
                      for i in range(4))
            passed += all(direct_guard(x, y, z, v, m) for m in MASKS)
        need(passed == TERMINAL[kind] * 48, "literal complete-header fibre")
        counts[kind] = passed
    need(len(counts) == 7, "every occupied type has a literal fibre")
    return counts


def controls(distribution, totals):
    need(inverse(((1, 0), (0, 0))) is None, "singular inverse control")
    rejected = 0
    for x, y in (((0, 0, 0, 0), (1, 0, 0, 0)),
                 ((1, 0, 0, 0), (0, 1, 0, 0))):
        try:
            completion(x, y)
        except ValueError:
            rejected += 1
    need(rejected == 2, "invalid split controls")
    try:
        schur(tuple((0, 0, 0, 0) for _ in range(4)))
    except ValueError:
        rejected += 1
    need(rejected == 3, "zero first pivot rejected")
    need(distribution["equal"] and distribution["orthogonal"], "distinct commuting types")
    need(TERMINAL["equal"] != TERMINAL["orthogonal"], "commutator-only state loses counts")
    need(882 * 11232 != totals[2] * 48, "first/full guard control")
    need(totals[2] != totals[2] * 48, "completion multiplier control")
    need(2160 * 11232 == 24261120, "full header denominator")
    return 8


def main():
    need(len(sys.argv) == 1, "no command-line arguments are supported")
    pairs = splits(3)
    distribution, witnesses, totals, first_counts = enumerate_first(pairs)
    literal = literal_fibres(witnesses)
    n_controls = controls(distribution, totals)
    denominator = 2160 * 11232
    joint = Fraction(totals[2] * 48, denominator)
    marginal = Fraction(totals[0] * 48, denominator)
    gap = joint - marginal * marginal
    need(joint == Fraction(523, 5265), "joint fraction")
    need(marginal == Fraction(361, 1170), "marginal fraction")
    need(gap == Fraction(5659, 1368900) and gap > 0, "strict positive correlation")
    package = Path(__file__).resolve().parent
    receipt = {
        "status": "PASS_RANKTWO_OVERLAP_TERNARY", "field": 3,
        "first_splits": 2160, "second_splits": len(pairs),
        "first_pivot_counts": first_counts, "distribution": dict(distribution),
        "two_stage_counts": totals, "complete_header_count": denominator,
        "joint_headers": totals[2] * 48, "marginal_headers": totals[0] * 48,
        "joint_fraction": str(joint), "marginal_fraction": str(marginal),
        "positive_covariance": str(gap), "literal_fibre_counts": literal,
        "literal_headers_checked": 7 * 11232, "controls": n_controls,
        "file_sha256": {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
                        for name in FILES},
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
