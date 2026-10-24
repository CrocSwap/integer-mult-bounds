#!/usr/bin/env python3
"""Aggregate idle histogram versus 144 copies of the per-call histogram.

The checker prices two named histograms. It does not search another histogram.
"""

import hashlib
import json
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_IDLE_AGGREGATION_GAP mass=237024 pooled_below=true no_new_kappa"
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"
INDEPENDENT = "research/community-frontier1094-audit/INDEPENDENT1094.json"
PRECISION = 256
MODULUS = 73
CALLS = 144
LIVE = 14336
GRID = 10 ** 15
ENDPOINT = Fraction(1688603446527, GRID)
POOLED = {51: 4647, 27: 1}
COPIED = {51: 4608, 14: 144}


def fail(message):
    raise SystemExit("FAIL_IDLE_AGGREGATION_GAP " + message)


def require(condition, message):
    if not condition:
        fail(message)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {row["path"]: row for row in sources["files"] if row["usage"] == "input"}
    require(set(pinned) == {ASSEMBLY, INDEPENDENT}, "input inventory changed")
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def downward(value):
    return Fraction((value.numerator << PRECISION) // value.denominator, 1 << PRECISION)


def upward(value):
    return -downward(-value)


def inverse_hyperbolic(slope, memory):
    if slope in memory:
        return memory[slope]
    total = Fraction(0)
    power = slope
    index = 0
    while True:
        total += power / (2 * index + 1)
        power *= slope * slope
        index += 1
        tail = power / ((2 * index + 1) * (1 - slope * slope))
        if tail < Fraction(1, 1 << (PRECISION + 8)):
            memory[slope] = (downward(total), upward(total + tail))
            return memory[slope]


def logarithm(rank, logs, slopes):
    if rank in logs:
        return logs[rank]
    low, high = logarithm(rank - 1, logs, slopes)
    left, right = inverse_hyperbolic(Fraction(1, 2 * rank - 1), slopes)
    logs[rank] = (downward(low + 2 * left), upward(high + 2 * right))
    return logs[rank]


def exponential(low, high):
    def series(value, upper):
        total = Fraction(1)
        term = Fraction(1)
        index = 0
        while True:
            index += 1
            term = term * value / index
            total += term
            if term * value < Fraction(1, 1 << (PRECISION + 8)):
                if upper:
                    return upward(total + 2 * term * value / (index + 1))
                return downward(total)

    return series(low, False), series(high, True)


def child_cost(rank, saving, logs, slopes):
    low_modulus, high_modulus = logs[MODULUS]
    low_rank, high_rank = logarithm(rank, logs, slopes)
    low_exp, high_exp = exponential(
        max(Fraction(0), saving * (low_modulus - high_rank)),
        saving * (high_modulus - low_rank),
    )
    return downward(Fraction(rank, MODULUS) * low_exp), upward(Fraction(rank, MODULUS) * high_exp)


def moment(local, idle, saving, logs, slopes):
    low = high = Fraction(0)
    counts = {rank: count * CALLS for rank, count in local.items()}
    for rank, count in idle.items():
        counts[rank] = counts.get(rank, 0) + count
    for rank, count in counts.items():
        left, right = child_cost(rank, saving, logs, slopes)
        low += count * left
        high += count * right
    return low / LIVE, high / LIVE


def invoice():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    assembly = json.loads((ROOT / ASSEMBLY).read_text(encoding="utf-8"))
    independent = json.loads((ROOT / INDEPENDENT).read_text(encoding="utf-8"))
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    counts = {int(rank): count for rank, count in assembly["complex_profile"].items()}
    require(counts == {int(rank): count for rank, count in independent["owner"]["profile"].items()}, "the invoices disagree")
    idle = {int(rank): count for rank, count in independent["owner"]["idle"].items()}
    calls, live = independent["price"]["calls"], independent["price"]["live"]
    require((calls, live) == (CALLS, LIVE), "the aggregation unit moved")
    local = {}
    for rank, count in counts.items():
        paid = count - idle.get(rank, 0)
        require(paid >= 0 and paid % CALLS == 0, "a local rank is not uniform")
        if paid:
            local[rank] = paid // CALLS
    require(all(count % CALLS != 0 for count in idle.values()), "an actual idle count divides evenly")
    return selected, local


def bracket(local, idle, logs, slopes):
    low, high = 0, GRID // 20
    require(moment(local, idle, Fraction(low, GRID), logs, slopes)[1] < 1, "the lower window is not below one")
    require(moment(local, idle, Fraction(high, GRID), logs, slopes)[0] > 1, "the upper window is not above one")
    while high - low > 1:
        mid = (low + high) // 2
        bounds = moment(local, idle, Fraction(mid, GRID), logs, slopes)
        if bounds[1] < 1:
            low = mid
        elif bounds[0] > 1:
            high = mid
        else:
            fail("a grid point did not separate")
    return Fraction(low, GRID), Fraction(high, GRID)


def evaluate():
    authenticate()
    selected, local = invoice()
    require(local == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "the paid profile moved")
    require(sum(rank * count for rank, count in POOLED.items()) == 237024, "the pooled mass moved")
    require(sum(rank * count for rank, count in COPIED.items()) == 237024, "the copied mass moved")
    pieces = [(39, {51: 33}), (1, {51: 32, 27: 1}), (104, {51: 32})]
    combined = {}
    require(sum(count for count, _ in pieces) == CALLS, "the decomposition lost a call")
    for count, histogram in pieces:
        for rank, copies in histogram.items():
            combined[rank] = combined.get(rank, 0) + count * copies
    require(combined == POOLED, "the decomposition missed the pooled histogram")
    logs = {1: (Fraction(0), Fraction(0))}
    slopes = {}
    logarithm(MODULUS, logs, slopes)
    pooled_low, pooled_high = moment(local, POOLED, ENDPOINT, logs, slopes)
    copied_low, _ = moment(local, COPIED, ENDPOINT, logs, slopes)
    require(pooled_high < 1 < copied_low, "the aggregation counterexample moved")
    lower, upper = bracket(local, POOLED, logs, slopes)
    require((lower, upper) == (Fraction(1690044548222, GRID), Fraction(1690044548223, GRID)), "the corrected bracket moved")
    saving = Fraction(selected["kappa"]) / (1 - Fraction(selected["kappa"]))
    require(saving < lower, "the selected saving is not below the corrected bracket")
    return {
        "calls": CALLS,
        "idle_mass": 237024,
        "pooled_below": True,
        "restricted_above": True,
        "corrected_lower": "1690044548222/1000000000000000",
        "corrected_upper": "1690044548223/1000000000000000",
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
