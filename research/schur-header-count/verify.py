#!/usr/bin/env python3
"""Exact one-block header counts over F2; standard library, no external inputs.

Prepared for ssafwann with substantial OpenAI Codex assistance. Apache-2.0.
The six-map criterion is credited to PR4671, with Nick Petalas's Schur lineage.
Bit-packed matrix enumeration below is separate from the counting formulas.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import itertools
import json
import math


def require(condition, message):
    if not condition:
        raise ValueError(message)


def eye(n):
    return tuple(1 << i for i in range(n))


def add(a, b):
    require(len(a) == len(b), "addition shape")
    return tuple(x ^ y for x, y in zip(a, b))


def mul(a, b):
    out = []
    for row in a:
        value = 0
        while row:
            bit = row & -row
            value ^= b[bit.bit_length() - 1]
            row ^= bit
        out.append(value)
    return tuple(out)


def rank(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length()
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return len(basis)


def inverse(a):
    n = len(a)
    rows = [row | 1 << (n + i) for i, row in enumerate(a)]
    for col in range(n):
        pivot = next((j for j in range(col, n) if rows[j] >> col & 1), None)
        require(pivot is not None, "singular header")
        rows[col], rows[pivot] = rows[pivot], rows[col]
        for j in range(n):
            if j != col and rows[j] >> col & 1:
                rows[j] ^= rows[col]
    return tuple(row >> n for row in rows)


def from_columns(cols, n):
    return tuple(sum((v >> i & 1) << j for j, v in enumerate(cols)) for i in range(n))


def matrices(rows, cols):
    return itertools.product(range(1 << cols), repeat=rows)


def gl_headers(n):
    def extend(cols, span):
        if len(cols) == n:
            yield from_columns(cols, n)
        else:
            for v in range(1, 1 << n):
                if v not in span:
                    yield from extend(cols + [v], span | {x ^ v for x in span})
    yield from extend([], {0})


def inj(n, k):
    if not 0 <= k <= n:
        return 0
    return math.prod((1 << n) - (1 << j) for j in range(k))


def gaussian(n, k):
    if not 0 <= k <= n:
        return 0
    return inj(n, k) // inj(k, k)


@lru_cache(maxsize=None)
def unrestricted_factor(r, d, rho):
    require(r >= 0 and d >= 1 and 0 <= rho <= d, "factor dimensions")
    return sum(gaussian(d - rho, d - k) * inj(r, k) * (1 << (d * (r - k)))
               for k in range(rho, min(d, r) + 1))


@lru_cache(maxsize=None)
def full_factor(r, d, rho):
    require(r >= 0 and d >= 1 and 0 <= rho <= d, "factor dimensions")
    if r < d:
        return 0
    return inj(r, d) * (1 << (rho * (r - d))) * inj(r - d, d - rho)


@lru_cache(maxsize=None)
def rank_pair_classes(d):
    return Counter((rank(h), rank(add(eye(d), h))) for h in matrices(d, d))


def predict(profile, d):
    require(len(profile) == 4 and all(type(r) is int and r >= 0 for r in profile),
            "four nonnegative integer sector dimensions")
    n = sum(profile)
    require(type(d) is int and 1 <= d <= n, "pivot dimension")
    identity = sharp = 0
    for (rh, rw), multiplicity in rank_pair_classes(d).items():
        r00, r10, r01, r11 = profile
        outside = unrestricted_factor(r00, d, rw)
        identity += multiplicity * outside * unrestricted_factor(r10, d, rw) * \
            unrestricted_factor(r01, d, rw) * unrestricted_factor(r11, d, rh)
        sharp += multiplicity * outside * full_factor(r10, d, rw) * \
            full_factor(r01, d, rw) * full_factor(r11, d, rh)
    tail = inj(n - d, n - d)
    total = inj(n, n)
    split_total = inj(n, d) * (1 << (d * (n - d)))
    require(tail * split_total == total, "GL completion normalization")
    require(0 <= sharp <= identity <= split_total, "count containment")
    return {"profile": profile, "d": d, "identity_splits": identity, "sharp_splits": sharp,
            "split_total": split_total, "completion_multiplicity": tail,
            "identity_headers": identity * tail, "sharp_headers": sharp * tail,
            "total_headers": total, "sharp_density": str(Fraction(sharp * tail, total)),
            "sharp_given_identity": str(Fraction(sharp, identity)) if identity else None}


def masks(profile):
    offset = 0
    sectors = []
    for r in profile:
        sectors.append(((1 << r) - 1) << offset)
        offset += r
    return sectors, sectors[1] | sectors[3], sectors[2] | sectors[3]


def schur(a, d):
    low = (1 << d) - 1
    require(tuple(row & low for row in a[:d]) == eye(d), "identity pivot")
    r = tuple(row >> d for row in a[:d])
    c = tuple(row & low for row in a[d:])
    dd = tuple(row >> d for row in a[d:])
    return add(dd, mul(c, r))


def inspect_header(header, profile, d):
    """Literal conjugation and direct Schur multiplication; no count formula."""
    n = len(header)
    require(n == sum(profile), "header dimension")
    back = inverse(header)
    _, pmask, qmask = masks(profile)
    p = mul(back, tuple(row if pmask >> i & 1 else 0 for i, row in enumerate(header)))
    q = mul(back, tuple(row if qmask >> i & 1 else 0 for i, row in enumerate(header)))
    low = (1 << d) - 1
    if any(tuple(row & low for row in a[:d]) != eye(d) for a in (p, q)):
        return None
    s, z = schur(p, d), schur(q, d)
    return rank(add(mul(s, z), mul(z, s)))


def factor_census():
    checked = 0
    for d in (1, 2, 3):
        for r in range(4):
            all_counts, full_counts = Counter(), Counter()
            xs, ys = list(matrices(d, r)), list(matrices(r, d))
            for x in xs:
                for y in ys:
                    t = mul(x, y)
                    all_counts[t] += 1
                    if rank(x) == rank(y) == d:
                        full_counts[t] += 1
            for t in matrices(d, d):
                rho = rank(t)
                require(all_counts[t] == unrestricted_factor(r, d, rho), "unrestricted factor count")
                require(full_counts[t] == full_factor(r, d, rho), "full-rank factor count")
            checked += len(xs) * len(ys)
    return checked


def direct_small_headers():
    receipts = []
    domains = [(3, (0, 1, 1, 1), 1), (4, (1, 1, 1, 1), 1),
               (4, (0, 1, 1, 2), 1), (4, (1, 1, 1, 1), 2)]
    for n, profile, d in domains:
        identity = sharp = total = 0
        for header in gl_headers(n):
            rk = inspect_header(header, profile, d)
            total += 1
            identity += rk is not None
            sharp += rk == 2 * d
        predicted = predict(profile, d)
        require((total, identity, sharp) == (predicted["total_headers"],
                predicted["identity_headers"], predicted["sharp_headers"]), "literal full-header census")
        receipts.append({"n": n, "profile": profile, "d": d, "total": total,
                         "identity": identity, "sharp": sharp})
    return receipts


def scalar_pair_header(x, covector, n):
    cols = [x]
    span = {0}
    for v in range(1, 1 << n):
        if (v & covector).bit_count() % 2 == 0 and v not in span:
            cols.append(v)
            span |= {u ^ v for u in span}
    require(len(cols) == n, "kernel completion")
    return from_columns(cols, n)


def scalar_split_census(profile):
    n = sum(profile)
    sectors, pmask, qmask = masks(profile)
    all_pairs = admitted = sharp = 0
    marginals = [0] * 6
    positive_headers = []
    for x in range(1, 1 << n):
        for covector in range(1 << n):
            if (x & covector).bit_count() % 2 != 1:
                continue
            all_pairs += 1
            if any((x & covector & mask).bit_count() % 2 != 1 for mask in (pmask, qmask)):
                continue
            admitted += 1
            conditions = [value != 0 for s in sectors[1:] for value in (x & s, covector & s)]
            marginals = [count + condition for count, condition in zip(marginals, conditions)]
            header = scalar_pair_header(x, covector, n)
            rk = inspect_header(header, profile, 1)
            require(rk is not None, "split pair has identity pivots")
            require((rk == 2) == all(conditions), "scalar six-map equivalence")
            if rk == 2:
                sharp += 1
                positive_headers.append(header)
    pred = predict(profile, 1)
    require((all_pairs, admitted, sharp) == (pred["split_total"], pred["identity_splits"],
                                            pred["sharp_splits"]), "all scalar split pairs")
    return {"profile": profile, "all_pairs": all_pairs, "identity": admitted,
            "sharp": sharp, "six_marginal_counts": marginals,
            "marginal_product_given_identity": str(math.prod(Fraction(m, admitted) for m in marginals))}, positive_headers


def positive_header_completions(profile, seeds, tails):
    """Enumerate every completion of each directly accepted scalar split pair."""
    seen = set()
    n = sum(profile)
    for seed in seeds:
        for tail in tails:
            change = (1,) + tuple(row << 1 for row in tail)
            header = mul(seed, change)
            require(inspect_header(header, profile, 1) == 2, "positive completion direct Schur rank")
            key = sum(row << (n * i) for i, row in enumerate(header))
            require(key not in seen, "distinct complete headers")
            seen.add(key)
    require(len(seen) == predict(profile, 1)["sharp_headers"], "complete positive-header count")
    return len(seen)


def rejects(label, call):
    try:
        call()
    except ValueError:
        return label
    raise ValueError("control did not reject: " + label)


def main():
    factor_pairs = factor_census()
    small = direct_small_headers()
    profiles = [(1, 1, 1, 2), (0, 2, 2, 1)]
    tails = list(gl_headers(4))
    require(len(tails) == 20160, "complete GL4 tail domain")
    scalar, completed = [], []
    for profile in profiles:
        receipt, seeds = scalar_split_census(profile)
        scalar.append(receipt)
        completed.append(positive_header_completions(profile, seeds, tails))
    examples = [predict(profile, 1) for profile in profiles] + [predict((2, 2, 2, 2), 2)]
    require([r["sharp_headers"] for r in examples[:2]] == [60480, 181440], "scalar examples")
    require(examples[2]["sharp_splits"] == 2592 and examples[2]["identity_splits"] == 1932288,
            "d=2 example")
    controls = []
    controls.append(rejects("all-headers-versus-conditioned", lambda: require(
        examples[0]["sharp_density"] == examples[0]["sharp_given_identity"], "different denominators")))
    controls.append(rejects("independent-six-events", lambda: require(
        scalar[0]["marginal_product_given_identity"] == examples[0]["sharp_given_identity"],
        "six events are dependent")))
    controls.append(rejects("missing-completion-multiplicity", lambda: require(
        examples[0]["sharp_headers"] == examples[0]["sharp_splits"], "headers are not split pairs")))
    controls.append(rejects("fourth-sector-full-rank", lambda: require(
        full_factor(0, 1, 0) > 0, "inactive sector need not have full-rank maps")))
    fake = sum(unrestricted_factor(1, 1, rank(add(eye(1), h))) for h in matrices(1, 1))
    controls.append(rejects("omit-surjectivity", lambda: require(
        fake == predict((1, 1, 1, 1), 1)["sharp_splits"], "injectivity alone overcounts")))
    controls.append(rejects("negative-sector", lambda: predict((-1, 1, 1, 2), 1)))
    controls.append(rejects("zero-pivot-size", lambda: predict((1, 1, 1, 2), 0)))
    print(json.dumps({"raw_factor_pairs": factor_pairs, "literal_small_header_censuses": small,
                      "scalar_split_censuses": scalar, "distinct_positive_headers": completed,
                      "examples": examples, "rejection_controls": controls}, sort_keys=True))
    print("PASS_SCHUR_HEADER_COUNT")


if __name__ == "__main__":
    main()
