#!/usr/bin/env python3
"""All small two-cut menus, checked against direct integer bills; no dependencies."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement, product
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from pricing import Menu, first_periodic_replication, frontier


def states():
    # Twelve is divisible by all allowed widths. One unit of price is twelve ticks.
    out = []
    for prices in product(range(4), repeat=4):
        rows = [(w, c) for w, c in enumerate(prices, 1) if c]
        if not rows:
            continue
        menu = Menu(rows)
        density = min(12*c//w for w, c in rows)
        # Amount-ordered direct billing with no use of any residue table.
        bills = [0]
        for n in range(1, 181):
            options = [bills[n-w] + 12*c for w, c in rows if w <= n and bills[n-w] is not None]
            bills.append(min(options, default=None))
        for q in range(1, 4):
            excess = [None if bills[q*a] is None else bills[q*a] - density*q*a for a in range(61)]
            out.append(((q, menu), density*q, excess))
    return out


def measured(excess):
    block = excess[24:36]
    if block != excess[36:48] or block != excess[48:60]:
        raise ValueError("direct tail blocks disagree")
    period = next(p for p in range(1, 13) if block == block[p:] + block[:p])
    onset = 1 + max((a for a in range(1, 36) if excess[a] != excess[a+period]), default=0)
    floor = next(a for a in range(1, 13) if excess[a] == 0)
    records = []
    for a in range(1, floor+1):
        loss = excess[a]
        if loss is not None and (not records or loss*records[-1] < excess[records[-1]]*a):
            records.append(a)
    return period, onset, floor, records


def census():
    rows = states()
    solo_starts = [measured(item[2])[1] for item in rows]
    digest, periods, onsets, sizes = sha256(), Counter(), Counter(), Counter()
    early = delayed = pairs = 0
    for i, j in combinations_with_replacement(range(len(rows)), 2):
        (cut1, rate1, losses1), (cut2, rate2, losses2) = rows[i], rows[j]
        losses = [None if x is None or y is None else x+y for x, y in zip(losses1, losses2, strict=True)]
        p, start, first, records = measured(losses)
        cuts = (cut1, cut2)
        period, floor, points = frontier(cuts)
        if period != p or first_periodic_replication(cuts) != start:
            raise ValueError(("period or onset", i, j))
        if floor != Fraction(rate1+rate2, 12) or points[-1][0] != first:
            raise ValueError(("cost floor", i, j))
        if [a for a, _, _ in points] != records:
            raise ValueError(("strict records", i, j))
        if any((fee-floor)*12*a != losses[a] for a, fee, _ in points):
            raise ValueError(("record prices", i, j))
        digest.update(bytes((p, start, first, len(records), *records)))
        periods[p] += 1
        onsets[start] += 1
        sizes[len(records)] += 1
        early += int(start < max(solo_starts[i], solo_starts[j]))
        delayed += int(first > p)
        pairs += 1
    return dict(menu_multiplicity_states=len(rows), unordered_pairs=pairs, scanned_positive_sizes=60*pairs,
                frontier_replications_sha256=digest.hexdigest(), period_histogram=dict(periods),
                onset_histogram=dict(onsets), frontier_size_histogram=dict(sizes),
                earlier_than_max_single_onset=early, first_floor_after_least_period=delayed)


if __name__ == "__main__":
    actual = json.loads(json.dumps(census()))
    expected = json.loads((PACKAGE / "CENSUS.json").read_text(encoding="utf-8"))
    if actual != expected:
        raise SystemExit("stored two-cut census differs")
    print(json.dumps({"status": "PASS_PRICED_WIDTH_CENSUS", "result": actual}, sort_keys=True))
