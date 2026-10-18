#!/usr/bin/env python3
"""Independent all-subset / parity-repair census at Q=7.

Does not import model.py or verify.py. Prepared by Wentao Li with substantial
AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations, permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
CHAMPION = (0, 1, 2, 6, 12, 24, 16)
BASIS = (1, 2, 4, 8, 16)


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def scores(slots):
    n = len(slots)
    best_all = [99] * 32
    best_even = [99] * 32
    best_repair = [99] * 32
    zero_idxs = [i for i in range(n) if slots[i] == 0]
    for bits in range(1 << n):
        size = bits.bit_count()
        if size == 0:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        if size < best_all[value]:
            best_all[value] = size
        if size % 2 == 0:
            if size < best_even[value]:
                best_even[value] = size
            if size < best_repair[value]:
                best_repair[value] = size
        elif zero_idxs:
            includes_zero = any(bits >> i & 1 for i in zero_idxs)
            cost = size - 1 if includes_zero else size + 1
            if cost < best_repair[value]:
                best_repair[value] = cost
    if any(best_even[m] >= 99 for m in range(1, 32)):
        return None
    return sum(best_all[1:]), sum(best_even[1:]), sum(best_repair[1:])


def all_reads(slots):
    n = len(slots)
    reads = {}
    for mask in range(1, 32):
        found = None
        for size in range(1, n + 1):
            for subset in combinations(range(n), size):
                value = 0
                for i in subset:
                    value ^= slots[i]
                if value == mask:
                    found = subset
                    break
            if found is not None:
                break
        if found is None:
            fail(f"uncovered {mask}")
        reads[mask] = found
    return reads


def tariff(q, r, x):
    return (28 * q + r) + (9 * q) + x + (q + r + x)


def distinct6():
    ha, he, hr = Counter(), Counter(), Counter()
    covering = 0
    match = 0
    for nonzero in combinations(range(1, 32), 6):
        got = scores((0,) + nonzero)
        if got is None:
            continue
        a, e, r = got
        covering += 1
        ha[a] += 1
        he[e] += 1
        hr[r] += 1
        if r == e:
            match += 1
    if covering != 583296:
        fail(f"covering {covering}")
    if dict(ha) != {66: 97216, 72: 486080}:
        fail(f"all hist {dict(ha)}")
    if dict(he) != {82: 97216, 88: 486080}:
        fail(f"even hist {dict(he)}")
    if dict(hr) != {82: 97216, 88: 486080}:
        fail(f"repair hist {dict(hr)}")
    if match != covering:
        fail(f"repair/even mismatch count {match}")
    return covering


def one_repeat(kind):
    hist = Counter()
    covering = 0

    def take(slots):
        nonlocal covering
        if slots[-1] == 0 or any(slots[i] == slots[i + 1] for i in range(6)):
            return
        got = scores(tuple(slots))
        if got is None:
            return
        a, e, r = got
        total = a if kind == "all" else r
        covering += 1
        hist[total] += 1

    for j in range(1, 6):
        rest = [i for i in range(1, 7) if i != j]
        for perm in permutations(BASIS):
            slots = [0] * 7
            slots[j] = 0
            for pos, val in zip(rest, perm):
                slots[pos] = val
            take(slots)
    for dbl in range(5):
        others = [BASIS[i] for i in range(5) if i != dbl]
        for p1, p2 in combinations(range(1, 7), 2):
            rest = [i for i in range(1, 7) if i not in (p1, p2)]
            for perm in permutations(others):
                slots = [0] * 7
                slots[p1] = slots[p2] = BASIS[dbl]
                for pos, val in zip(rest, perm):
                    slots[pos] = val
                take(slots)
    return covering, dict(hist)


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    covering = distinct6()
    cov_all, hist_all = one_repeat("all")
    cov_rep, hist_rep = one_repeat("repair")
    if cov_all != 1680 or hist_all != {80: 1680}:
        fail(f"repeat all {cov_all} {hist_all}")
    if cov_rep != 1680 or hist_rep != {96: 1680}:
        fail(f"repeat repair {cov_rep} {hist_rep}")

    got = scores(CHAMPION)
    if got != (66, 82, 82):
        fail(f"champion scores {got}")
    odds = [m for m, subset in all_reads(CHAMPION).items() if len(subset) % 2]
    if not odds:
        fail("champion all-subset schedule has no odd dirt")
    if tariff(7, 66, 6) != 410 or tariff(7, 82, 6) != 442:
        fail("tariff")
    if not (
        cert["claim"]["all_subset_min_R"] == 66
        and cert["claim"]["parity_repair_min_R"] == 82
        and cert["claim"]["undercuts_436_after_parity_repair"] is False
    ):
        fail("certificate claim drift")

    print(
        "PASS_INDEPENDENT_CHEAPER_READOUT_7Q",
        f"covering={covering}",
        "all_min=66",
        "repair_min=82",
        "tariff_free=410",
        "tariff_repair=442",
        "answers_7qr_oq1",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
