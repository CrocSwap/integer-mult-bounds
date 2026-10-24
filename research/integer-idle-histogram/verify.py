#!/usr/bin/env python3
"""Integer idle histogram for the selected complex profile.

The checker reads the pinned profile. It does not search another rank cap.
"""

import hashlib
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_INTEGER_IDLE_HISTOGRAM ranks=51,14 below_one=true no_new_kappa"
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"
INDEPENDENT = "research/community-frontier1094-audit/INDEPENDENT1094.json"
PRECISION = 256
MODULUS = 73
STAGES = 9
CENTRE = 64
LOW = Fraction(1688603446526, 10 ** 15)
HIGH = Fraction(1688603446527, 10 ** 15)


def fail(message):
    raise SystemExit("FAIL_INTEGER_IDLE_HISTOGRAM " + message)


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
    require(
        set(pinned) == {ASSEMBLY, INDEPENDENT},
        "input inventory changed",
    )
    for path, row in pinned.items():
        require(sha256(ROOT / path) == row["sha256"], "input drift " + path)


def downward(value):
    return Fraction((value.numerator << PRECISION) // value.denominator, 1 << PRECISION)


def upward(value):
    return -downward(-value)


def inverse_hyperbolic(slope):
    total = Fraction(0)
    power = slope
    index = 0
    while True:
        total += power / (2 * index + 1)
        power *= slope * slope
        index += 1
        tail = power / ((2 * index + 1) * (1 - slope * slope))
        if tail < Fraction(1, 1 << (PRECISION + 8)):
            return downward(total), upward(total + tail)


def logarithm(rank, memory):
    if rank in memory:
        return memory[rank]
    low, high = logarithm(rank - 1, memory)
    left, right = inverse_hyperbolic(Fraction(1, 2 * rank - 1))
    memory[rank] = (downward(low + 2 * left), upward(high + 2 * right))
    return memory[rank]


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


def child_cost(rank, saving, logs):
    low_modulus, high_modulus = logs[MODULUS]
    low_rank, high_rank = logs[rank]
    low_exp, high_exp = exponential(
        max(Fraction(0), saving * (low_modulus - high_rank)),
        saving * (high_modulus - low_rank),
    )
    return downward(Fraction(rank, MODULUS) * low_exp), upward(Fraction(rank, MODULUS) * high_exp)


def rank_cap():
    cap = isqrt((MODULUS * MODULUS - 1) // 2)
    while 2 * (cap + 1) ** 2 < MODULUS * MODULUS:
        cap += 1
    while 2 * cap * cap >= MODULUS * MODULUS:
        cap -= 1
    return cap


def optimum(mass, cap, saving, logs):
    costs = [0] + [int(child_cost(rank, saving, logs)[0] * (1 << PRECISION)) for rank in range(1, cap + 1)]
    best = [None] * (mass + 1)
    choice = [0] * (mass + 1)
    best[0] = 0
    for total in range(1, mass + 1):
        value, pick = None, 0
        for rank in range(1, min(cap, total) + 1):
            candidate = best[total - rank] + costs[rank]
            if value is None or candidate < value:
                value, pick = candidate, rank
        best[total], choice[total] = value, pick
    histogram = {}
    remaining = mass
    while remaining:
        rank = choice[remaining]
        histogram[rank] = histogram.get(rank, 0) + 1
        remaining -= rank
    return histogram, best[mass]


def moment(local, histogram, saving, logs, width):
    low = high = Fraction(0)
    for source in (local, histogram):
        for rank, count in source.items():
            left, right = child_cost(rank, saving, logs)
            low += count * left
            high += count * right
    return low / width, high / width


def profile():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000", "certificate": "research/community-frontier1094-audit/ASSEMBLY.json"}
    require(selected["certificate"] == ASSEMBLY, "the selected certificate moved")
    require(Fraction(selected["kappa"]) == Fraction(836330098538459, 500000000000000000), "the selected kappa moved")
    assembly = json.loads((ROOT / ASSEMBLY).read_text(encoding="utf-8"))
    independent = json.loads((ROOT / INDEPENDENT).read_text(encoding="utf-8"))
    counts = {int(rank): count for rank, count in assembly["complex_profile"].items()}
    require(counts == {int(rank): count for rank, count in independent["owner"]["profile"].items()}, "the profiles disagree")
    idle = {int(rank): count for rank, count in independent["owner"]["idle"].items()}
    calls, live = independent["price"]["calls"], independent["price"]["live"]
    require(calls % STAGES == 0 and live == 896 * (calls // STAGES), "the live stock moved")
    require(sum(rank * count for rank, count in counts.items()) == 72 * live + CENTRE * calls, "the coverage identity moved")
    local = {}
    for rank, count in counts.items():
        paid = count - idle.get(rank, 0)
        require(paid >= 0 and paid % calls == 0, "a local rank is not uniform")
        if paid:
            local[rank] = paid // calls
    width = Fraction(896, 9)
    idle_mass = (MODULUS - 1) * width + CENTRE - sum(rank * Fraction(count) for rank, count in local.items())
    require(idle_mass.denominator == 1, "the idle mass is not an integer")
    return selected, local, int(idle_mass), width


def evaluate():
    authenticate()
    selected, local, idle_mass, width = profile()
    require(local == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "the paid profile moved")
    require(idle_mass == 1646, "the idle mass moved")
    cap = rank_cap()
    require(cap == 51, "the halving guard moved")
    require(HIGH - LOW == Fraction(1, 10 ** 15), "the bracket width moved")
    logs = {1: (Fraction(0), Fraction(0))}
    logarithm(MODULUS, logs)
    histograms = []
    for saving, side in ((LOW, "lower"), (HIGH, "upper")):
        histogram, _ = optimum(idle_mass, cap, saving, logs)
        low, high = moment(local, histogram, saving, logs, width)
        histograms.append((histogram, low, high))
        if side == "lower":
            require(high < 1, "the lower endpoint is not below one")
        else:
            require(low > 1, "the upper endpoint is not above one")
    require(histograms[0][0] == histograms[1][0] == {51: 32, 14: 1}, "the optimum histogram moved")
    saving = Fraction(selected["kappa"]) / (1 - Fraction(selected["kappa"]))
    require(saving < LOW, "the selected saving is not below the bracket")
    return {
        "idle_mass": idle_mass,
        "rank_51": 32,
        "rank_14": 1,
        "below_one": True,
        "above_one": True,
        "selected_below": True,
        "no_new_kappa": True,
    }


def main():
    observed = evaluate()
    expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
    require(observed == expected, "RESULT.json does not match the execution")
    print(MARKER)


if __name__ == "__main__":
    main()
