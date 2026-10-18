#!/usr/bin/env python3
"""Independent two-repeat partitioned dual census at Q=8.

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
INF = 99

EXPECTED_26_COVERING = 0
EXPECTED_35_COVERING = 0
EXPECTED_44_VALID = 0
EXPECTED_26_WALKS = 26970
EXPECTED_26_221 = 13485
EXPECTED_26_311 = 13485
EXPECTED_35_MULTISETS = 465
ENDPOINT = 436


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def even_table(slots):
    n = len(slots)
    even = [INF] * 32
    even[0] = 0
    for bits in range(1, 1 << n):
        size = bits.bit_count()
        if size % 2:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        if size < even[value]:
            even[value] = size
    return even


def dual_R(e0, e1):
    reach0 = [(a, e0[a]) for a in range(32) if e0[a] < INF]
    total = 0
    for m in range(1, 32):
        best = INF
        for a, c0 in reach0:
            c1 = e1[a ^ m]
            if c1 < INF:
                best = min(best, c0 + c1)
        if best >= INF:
            return None
        total += best
    return total


def path_X(slots):
    closed = slots + (0,)
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        if delta == 0:
            return None
        total += 2 * (delta.bit_count() - 1)
    return total


def find_restoring(multiset_nz):
    for perm in set(permutations(multiset_nz)):
        walk = (0,) + perm
        if path_X(walk) is not None:
            return walk
    return None


def gf2_span(vals):
    basis = []
    for v in vals:
        x = v
        for b in basis:
            x = min(x, x ^ b)
        if x:
            basis.append(x)
            basis.sort(reverse=True)
    span = {0}
    for b in basis:
        span |= {s ^ b for s in span}
    return frozenset(span), len(basis)


def slots_from_ms(ms):
    nz = []
    for lab, cnt in sorted(Counter(ms).items()):
        nz.extend([lab] * cnt)
    return (0,) + tuple(nz)


def census_26():
    walks = []
    for d, e in combinations(range(1, 32), 2):
        for o in range(1, 32):
            if o in (d, e):
                continue
            w = find_restoring((d, d, e, e, o))
            if w is None:
                fail("{2,2,1} should restore")
            walks.append(w)
    n221 = len(walks)
    for d in range(1, 32):
        others = [x for x in range(1, 32) if x != d]
        for o1, o2 in combinations(others, 2):
            w = find_restoring((d, d, d, o1, o2))
            if w is None:
                fail("{3,1,1} should restore")
            walks.append(w)
    if n221 != EXPECTED_26_221:
        fail(f"221 count {n221}")
    if len(walks) - n221 != EXPECTED_26_311:
        fail("311 count")
    if len(walks) != EXPECTED_26_WALKS:
        fail(f"walks {len(walks)}")
    covering = 0
    for walk in walks:
        span, rank = gf2_span(walk)
        if rank > 3 or len(span) > 8:
            fail("span bound")
        e1 = even_table(slots_from_ms(walk[1:]))
        for sigma in range(1, 32):
            if dual_R(even_table((0, sigma)), e1) is not None:
                covering += 1
    if covering != EXPECTED_26_COVERING:
        fail(f"26 covering {covering}")
    return covering, len(walks), n221


def census_35():
    tables3 = [even_table((0,) + nz) for nz in combinations(range(1, 32), 2)]
    tables5 = []
    for d, e in combinations(range(1, 32), 2):
        if find_restoring((d, d, e, e)) is None:
            fail("{2,2} should restore")
        tables5.append(even_table(slots_from_ms((d, d, e, e))))
    if len(tables5) != EXPECTED_35_MULTISETS:
        fail("35 multisets")
    covering = 0
    for e0 in tables3:
        for e1 in tables5:
            if dual_R(e0, e1) is not None:
                covering += 1
    if covering != EXPECTED_35_COVERING:
        fail(f"35 covering {covering}")
    return covering, len(tables5)


def census_44():
    valid = 0
    for d in range(1, 32):
        if find_restoring((d, d, d)) is not None:
            valid += 1
    if valid != EXPECTED_44_VALID:
        fail(f"44 valid {valid}")
    return valid


def main():
    pinned = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    c26, n26, n221 = census_26()
    c35, n35 = census_35()
    v44 = census_44()
    claim = pinned["claim"]
    if claim["two_repeat_26_covering"] != c26:
        fail("26 claim drift")
    if claim["two_repeat_35_covering"] != c35:
        fail("35 claim drift")
    if claim["two_repeat_44_valid_walks"] != v44:
        fail("44 claim drift")
    if claim["undercuts_436_after_complete_bill"] is not False:
        fail("undercut claim")
    if claim["endpoint_Q6_tariff"] != ENDPOINT:
        fail("endpoint")
    print(
        "PASS_INDEPENDENT_WALKS_TWOREPEAT_8Q",
        f"covering_26={c26}",
        f"covering_35={c35}",
        f"valid_26={n26}",
        f"shape_221={n221}",
        f"multisets_35={n35}",
        f"valid_44={v44}",
        "tariff_floor=None",
        "no_undercut_436",
        "no_new_kappa",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
