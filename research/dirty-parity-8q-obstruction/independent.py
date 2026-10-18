#!/usr/bin/env python3
"""Independent all-subset / parity-repair census at Q=8.

Does not import model.py or verify.py. Prepared by Wentao Li with substantial
AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
import os
from collections import Counter
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
CHAMPION = (0, 1, 2, 3, 4, 8, 16, 29)
INF = 99


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def gf2_rank(vals):
    basis = []
    for v in vals:
        x = v
        for b in basis:
            x = min(x, x ^ b)
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    return len(basis)


def scores(slots):
    """Bit-enumeration totals: all / even / zero-slot repair."""
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
    if any(best_all[m] >= 99 for m in range(1, 32)):
        return None
    return sum(best_all[1:]), sum(best_even[1:]), sum(best_repair[1:])


def dp_scores(slots):
    """Separate DP implementation (not the bit oracle)."""
    ba = [INF] * 32
    be = [INF] * 32
    boz = [INF] * 32
    bon = [INF] * 32
    ba[0] = 0
    be[0] = 0
    for v in slots:
        is_zero = v == 0
        na = ba[:]
        ne = be[:]
        noz = boz[:]
        non = bon[:]
        for m in range(32):
            if ba[m] < INF:
                nm = m ^ v
                c = ba[m] + 1
                if c < na[nm]:
                    na[nm] = c
            if be[m] < INF:
                nm = m ^ v
                c = be[m] + 1
                if is_zero:
                    if c < noz[nm]:
                        noz[nm] = c
                else:
                    if c < non[nm]:
                        non[nm] = c
            if boz[m] < INF:
                nm = m ^ v
                c = boz[m] + 1
                if c < ne[nm]:
                    ne[nm] = c
            if bon[m] < INF:
                nm = m ^ v
                c = bon[m] + 1
                if c < ne[nm]:
                    ne[nm] = c
        ba, be, boz, bon = na, ne, noz, non
    br = be[:]
    if any(s == 0 for s in slots):
        for m in range(32):
            if boz[m] < INF:
                br[m] = min(br[m], boz[m] - 1)
            if bon[m] < INF:
                br[m] = min(br[m], bon[m] + 1)

    def tot(best):
        if any(best[m] >= INF for m in range(1, 32)):
            return None
        return sum(best[1:])

    return tot(ba), tot(be), tot(br)


def tariff(q, r, x):
    return (28 * q + r) + (9 * q) + x + (q + r + x)


def _worker(combos):
    ha, he, hr = Counter(), Counter(), Counter()
    covering = match = 0
    for combo in combos:
        if gf2_rank(combo) < 5:
            continue
        slots = (0,) + combo
        got = dp_scores(slots)
        if got is None:
            continue
        a, e, r = got
        covering += 1
        ha[a] += 1
        he[e] += 1
        hr[r] += 1
        if r == e:
            match += 1
    return covering, match, ha, he, hr


def distinct7():
    combos = list(combinations(range(1, 32), 7))
    n = os.cpu_count() or 4
    chunk = (len(combos) + n - 1) // n
    chunks = [combos[i * chunk : (i + 1) * chunk] for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(_worker, chunks)
    covering = match = 0
    ha, he, hr = Counter(), Counter(), Counter()
    for c, m, a, e, r in parts:
        covering += c
        match += m
        ha.update(a)
        he.update(e)
        hr.update(r)
    if covering != 2430400:
        fail(f"covering {covering}")
    if match != covering:
        fail(f"repair!=even on {covering - match} sets")
    if dict(ha) != {61: 416640, 64: 1180480, 68: 833280}:
        fail(f"all hist {dict(ha)}")
    if dict(he) != {74: 416640, 80: 1180480, 84: 833280}:
        fail(f"even hist {dict(he)}")
    if dict(hr) != {74: 416640, 80: 1180480, 84: 833280}:
        fail(f"repair hist {dict(hr)}")
    return covering, min(ha), min(hr)


def _dup_worker(items):
    ha, hr = Counter(), Counter()
    covering = 0
    for six, dup in items:
        if gf2_rank(six) < 5:
            continue
        slots = tuple(sorted(((0,) + six) + (dup,)))
        got = dp_scores(slots)
        if got is None:
            continue
        a, _e, r = got
        covering += 1
        ha[a] += 1
        hr[r] += 1
    return covering, ha, hr


def one_dup():
    items = []
    for six in combinations(range(1, 32), 6):
        labels = (0,) + six
        for dup in labels:
            items.append((six, dup))
    n = os.cpu_count() or 4
    chunk = (len(items) + n - 1) // n
    chunks = [items[i * chunk : (i + 1) * chunk] for i in range(n)]
    with Pool(n) as pool:
        parts = pool.map(_dup_worker, chunks)
    covering = 0
    ha, hr = Counter(), Counter()
    for c, a, r in parts:
        covering += c
        ha.update(a)
        hr.update(r)
    if covering != 4083072:
        fail(f"one-dup covering {covering}")
    if dict(ha) != {66: 680512, 72: 3402560}:
        fail(f"one-dup all {dict(ha)}")
    if dict(hr) != {82: 680512, 88: 3402560}:
        fail(f"one-dup repair {dict(hr)}")
    return min(ha), min(hr)


def champion_checks():
    bit = scores(CHAMPION)
    dp = dp_scores(CHAMPION)
    if bit != dp:
        fail(f"champion DP/bit {bit} vs {dp}")
    if bit != (61, 74, 74):
        fail(f"champion totals {bit}")
    # Odd-dirt on a min all-subset schedule.
    reads = {}
    n = len(CHAMPION)
    for mask in range(1, 32):
        found = None
        for size in range(1, n + 1):
            for subset in combinations(range(n), size):
                value = 0
                for i in subset:
                    value ^= CHAMPION[i]
                if value == mask:
                    found = subset
                    break
            if found is not None:
                break
        if found is None:
            fail(f"uncovered {mask}")
        reads[mask] = found
    odds = [m for m, s in reads.items() if len(s) % 2 == 1]
    if not odds:
        fail("no odd dirt on champion")
    hyp = tariff(8, 61, 0)
    rep = tariff(8, 74, 0)
    if hyp != 426 or rep != 452:
        fail(f"tariff {hyp} {rep}")
    if not (hyp < 436 < rep or hyp < 436 <= rep):
        fail("tariff ordering")
    if not (hyp < 436 and rep > 436):
        fail("undercut flags")
    return len(odds)


def main():
    cert = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    claim = cert["claim"]
    odd_count = champion_checks()
    covering, all_min, repair_min = distinct7()
    dup_all, dup_repair = one_dup()
    if claim["all_subset_min_R_distinct7"] != all_min:
        fail("claim all min")
    if claim["parity_repair_min_R_distinct7"] != repair_min:
        fail("claim repair min")
    if claim["one_dup_all_subset_min_R"] != dup_all:
        fail("claim one-dup all")
    if claim["one_dup_parity_repair_min_R"] != dup_repair:
        fail("claim one-dup repair")
    if claim["undercuts_436_if_all_subset_free"] is not True:
        fail("free undercut flag")
    if claim["undercuts_436_after_parity_repair"] is not False:
        fail("repair undercut flag")
    if claim["answers_cr7q_oq2"] is not True:
        fail("oq2 flag")
    print(
        "PASS_INDEPENDENT_DIRTY_PARITY_8Q "
        f"covering={covering} all_min={all_min} repair_min={repair_min} "
        f"tariff_free={tariff(8, all_min, 0)} tariff_repair={tariff(8, repair_min, 0)} "
        f"one_dup_all={dup_all} one_dup_repair={dup_repair} "
        f"champion_odd_dirt={odd_count} answers_cr7q_oq2 no_new_kappa"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
