#!/usr/bin/env python3
"""Independent Q=7 even-subset R classification and champion replay.

Does not import model.py or verify.py. Prepared by Wentao Li with substantial
AI assistance. Apache-2.0.
"""
from __future__ import annotations

import json
from collections import Counter
from itertools import combinations, combinations_with_replacement, permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
CERT_PATH = HERE / "CERTIFICATE.json"
CHAMPION = (0, 1, 2, 6, 12, 24, 16, 0)
BASIS = (1, 2, 4, 8, 16)


def fail(message):
    raise SystemExit(f"FAIL_INDEPENDENT: {message}")


def even_R(slots):
    n = len(slots)
    best = [99] * 32
    for bits in range(1 << n):
        if bits.bit_count() % 2:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        size = bits.bit_count()
        if size < best[value]:
            best[value] = size
    if any(best[mask] >= 99 for mask in range(1, 32)):
        return None
    return sum(best[1:])


def even_image(slots):
    n = len(slots)
    image = set()
    for bits in range(1 << n):
        if bits.bit_count() % 2:
            continue
        value = 0
        for i in range(n):
            if bits >> i & 1:
                value ^= slots[i]
        image.add(value)
    return image


def tariff(q, r, x):
    return (28 * q + r) + (9 * q) + x + (q + r + x)


def distinct6_spectrum():
    hist = Counter()
    covering = 0
    for nonzero in combinations(range(1, 32), 6):
        total = even_R((0,) + nonzero)
        if total is None:
            continue
        covering += 1
        hist[total] += 1
    if sorted(hist) != [82, 88]:
        fail(f"spectrum {sorted(hist)}")
    if dict(hist) != {82: 97216, 88: 486080}:
        fail(f"histogram {dict(hist)}")
    if covering != 583296:
        fail(f"covering {covering}")
    return dict(hist)


def one_repeat_basis():
    hist = Counter()
    covering = 0
    # Extra 0
    for j in range(1, 6):
        rest = [i for i in range(1, 7) if i != j]
        for perm in permutations(BASIS):
            slots = [0] * 7
            slots[j] = 0
            for pos, val in zip(rest, perm):
                slots[pos] = val
            if any(slots[i] == slots[i + 1] for i in range(6)) or slots[6] == 0:
                continue
            total = even_R(tuple(slots))
            if total is None:
                continue
            covering += 1
            hist[total] += 1
    # Doubled basis vector
    for dbl_idx in range(5):
        others = [BASIS[i] for i in range(5) if i != dbl_idx]
        for p1, p2 in combinations(range(1, 7), 2):
            rest_pos = [i for i in range(1, 7) if i not in (p1, p2)]
            for perm in permutations(others):
                slots = [0] * 7
                slots[p1] = slots[p2] = BASIS[dbl_idx]
                for pos, val in zip(rest_pos, perm):
                    slots[pos] = val
                if any(slots[i] == slots[i + 1] for i in range(6)) or slots[6] == 0:
                    continue
                total = even_R(tuple(slots))
                if total is None:
                    continue
                covering += 1
                hist[total] += 1
    if sorted(hist) != [96]:
        fail(f"repeat spectrum {sorted(hist)}")
    if covering != 1680:
        fail(f"repeat covering {covering}")
    return covering, dict(hist)


def rank_obstruction():
    labels = (1, 2, 3, 4, 5)
    best = 0
    for multi in combinations_with_replacement((0,) + labels, 6):
        best = max(best, len(even_image((0,) + multi)))
    if best >= 32:
        fail(f"dependent set covered with image {best}")
    return best


def path_x(closed):
    total = 0
    for a, b in zip(closed, closed[1:]):
        delta = a ^ b
        if delta == 0:
            fail("zero edge")
        total += 2 * (delta.bit_count() - 1)
    return total


def replay_champion():
    """Direct F2 column simulation of the path-lowered champion."""
    slots = list(CHAMPION[:-1])
    if even_R(tuple(slots)) != 82:
        fail("champion R")
    if path_x(CHAMPION) != 6:
        fail("champion X")
    # Connector walk + even-subset reads + path-local shears on formal AB image.
    x = [1 << j for j in range(5)]
    z = 0
    y = [0] * 32
    reads = {}
    for mask in range(1, 32):
        found = None
        for size in range(2, len(slots) + 1, 2):
            for subset in combinations(range(len(slots)), size):
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
    for step, point in enumerate(CHAMPION):
        for mask, subset in reads.items():
            if step in subset:
                y[mask] ^= z
        if step + 1 >= len(CHAMPION):
            break
        delta = point ^ CHAMPION[step + 1]
        target = (delta & -delta).bit_length() - 1
        donors = [j for j in range(5) if j != target and delta >> j & 1]
        for j in donors:
            x[target] ^= x[j]
        z ^= x[target]
        for j in reversed(donors):
            x[target] ^= x[j]
    if x != [1 << j for j in range(5)] or z != 0:
        fail("sources/connector not restored")
    for mask in range(1, 32):
        expected = 0
        for j in range(5):
            if mask >> j & 1:
                expected ^= 1 << j
        # y holds connector snapshots; with B=id on masks, image should match mask bits.
        if y[mask] != expected:
            fail(f"output image mask {mask}: {y[mask]} != {expected}")
    return 82, 6


def main():
    hist = distinct6_spectrum()
    cov, rh = one_repeat_basis()
    img = rank_obstruction()
    r, x = replay_champion()
    if tariff(7, 82, 6) != 442:
        fail("tariff")
    if tariff(7, 78, 6) >= 436:
        fail("R=78 threshold")
    committed = json.loads(CERT_PATH.read_text(encoding="utf-8"))
    if committed["claim"]["min_R_among_X_eq_6"] != 82:
        fail("certificate claim")
    if committed["classification"]["distinct_six_nonzero"]["histogram"] != {
        str(k): v for k, v in hist.items()
    }:
        # hist keys are ints; certificate uses string keys
        cert_hist = committed["classification"]["distinct_six_nonzero"]["histogram"]
        if cert_hist != {str(k): v for k, v in hist.items()}:
            fail("cert distinct hist mismatch")
    print(
        "PASS_INDEPENDENT_SEVEN_QUERY_R_FLOOR "
        f"min_R=82 repeat_covering={cov} repeat_hist={rh} "
        f"dep_image={img} champion_R={r} champion_X={x} tariff=442 "
        "answers_7qxor_oq1"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
