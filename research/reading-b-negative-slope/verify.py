#!/usr/bin/env python3
"""Corroborate the negative-slope Reading B proof.

PROOF.md is the argument for every rank and every real negative slope. This
script checks the exact witnesses used there, the concavity and contract
controls, and an exhaustive census of a finite box. The census is not the
proof. Failures raise; the checks do not use assert.
"""

from fractions import Fraction
from functools import lru_cache
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
R_MAX = 22
SLOPES = (
    Fraction(-5, 2),
    Fraction(-2),
    Fraction(-1),
    Fraction(-1, 2),
    Fraction(-1, 3),
)
SELECTED_KAPPA = "363005817/100000000000"
SELECTED_DECIMAL = "0.00363005817"


def require(condition, message):
    if not condition:
        raise SystemExit("FAIL: " + message)


@lru_cache(maxsize=None)
def partitions(rank):
    """Positive partitions of rank, each in nonincreasing order."""

    def extend(remain, cap):
        if remain == 0:
            yield ()
            return
        for piece in range(1, min(cap, remain) + 1):
            for tail in extend(remain - piece, piece):
                yield (piece,) + tail

    return tuple(tuple(sorted(parts, reverse=True)) for parts in extend(rank, rank))


def prefix(diffs):
    values = [Fraction(0)]
    for delta in diffs:
        values.append(values[-1] + delta)
    return values


def differences(values):
    return [values[j] - values[j - 1] for j in range(1, len(values))]


def is_tariff(values):
    diffs = differences(values)
    return values[0] == 0 and all(delta >= 0 for delta in diffs) and all(
        diffs[j] >= diffs[j + 1] for j in range(len(diffs) - 1)
    )


def shortest_credit(values, parts, slope):
    """c-free Reading B credit, freeing one shortest piece."""
    rank = sum(parts)
    short = min(parts)
    charged = list(parts)
    charged.remove(short)
    total = sum((values[piece] for piece in charged), Fraction(0))
    return values[short] + (1 - slope) * total - values[rank], short, charged


def gamma(values, rank, slope, small):
    return values[small] + (1 - slope) * values[rank - small] - values[rank]


def lam(values, rank, slope, small):
    return values[rank - small] + (1 - slope) * values[small] - values[rank]


def threshold(values, rank, slope):
    return max(gamma(values, rank, slope, small) for small in range(1, rank // 2 + 1))


def tariffs_for(rank):
    identity = prefix([1] * rank)
    harmonic = prefix([Fraction(1, j) for j in range(1, rank + 1)])
    cap_one = [Fraction(min(n, 1)) for n in range(rank + 1)]
    cap_three = [Fraction(min(n, 3)) for n in range(rank + 1)]
    saturated = [Fraction(n, n + 1) for n in range(rank + 1)]
    quadratic = [Fraction(n * (2 * rank - n)) for n in range(rank + 1)]
    zero = [Fraction(0)] * (rank + 1)
    return {
        "identity": identity,
        "harmonic": harmonic,
        "cap1": cap_one,
        "cap3": cap_three,
        "saturated": saturated,
        "quadratic": quadratic,
        "zero": zero,
    }


def check_selected_record():
    record = json.loads((ROOT / "certificates/selected-result.json").read_text(encoding="utf-8"))
    require(record["kappa"] == SELECTED_KAPPA, "selected kappa moved")
    require(record["decimal"] == SELECTED_DECIMAL, "selected decimal moved")


def check_identity_transfer():
    values = prefix([1] * 6)
    slope = -1
    require(threshold(values, 6, slope) == 5, "identity short-free threshold moved")
    require(max(lam(values, 6, slope, small) for small in range(1, 4)) == 3,
            "identity long-free threshold moved")
    # (5,1) frees 1. At c=4 the long-free test is nonpositive and this split pays.
    credit, short, _charged = shortest_credit(values, (5, 1), slope)
    require(short == 1 and credit == 5, "identity (5,1) credit moved")
    require(credit - 4 == 1, "identity transfer witness no longer pays at c=4")
    require(all(lam(values, 6, slope, small) <= 3 for small in range(1, 4)),
            "long-free identity values escaped the threshold")
    # The charged piece 4 exceeds floor((R-1)/2).
    credit_long, short_piece, charged = shortest_credit(values, (4, 1, 1), slope)
    require(short_piece == 1 and 4 in charged and 4 > (6 - 1) // 2,
            "charged-length transfer witness moved")
    require(credit_long == 5, "identity (4,1,1) credit moved")


def check_absolute_and_sharp_witnesses():
    harmonic = prefix([Fraction(1, j) for j in range(1, 7)])
    balanced, _, _ = shortest_credit(harmonic, (2, 2, 2), -1)
    pair = gamma(harmonic, 6, -1, 2)
    require(balanced == Fraction(101, 20), "harmonic (2,2,2) credit moved")
    require(pair == Fraction(193, 60), "harmonic (4,2) credit moved")
    require(threshold(harmonic, 6, -1) == Fraction(193, 60), "harmonic threshold moved")
    require(balanced > pair and balanced / 2 < pair,
            "harmonic witness no longer separates absolute credit from the ratio")

    cap = [Fraction(min(n, 1)) for n in range(9)]
    credit, _, _ = shortest_credit(cap, (6, 1, 1), -1)
    require(threshold(cap, 8, -1) == 2 and credit == 4, "cap equality witness moved")


def check_failure_controls():
    # Nondecreasing and zero at the origin, but not concave.
    bumped = prefix([0, 1, 0, 0, 2])
    require(not is_tariff(bumped), "rank-5 control became concave")
    require(threshold(bumped, 5, -1) == 0, "rank-5 two-part threshold moved")
    credit, short, _ = shortest_credit(bumped, (2, 2, 1), -1)
    require(short == 1 and credit == 1, "rank-5 three-part control moved")

    table = [Fraction(value) for value in (0, 0, 1, 1, 1, 1, 2)]
    require(not is_tariff(table), "published nonconcave table became concave")
    require(threshold(table, 6, -1) == 1, "published table threshold moved")
    published, _, _ = shortest_credit(table, (2, 2, 2), -1)
    require(published == 3 and published - 2 * 1 == 1,
            "published table no longer separates the existence test at c=1")

    # For d>0 the free piece is the long one. The short-free threshold is a
    # different number, so this package's test is not the nonnegative contract.
    harmonic = prefix([Fraction(1, j) for j in range(1, 7)])
    slope = Fraction(1, 2)
    long_free = max(lam(harmonic, 6, slope, small) for small in range(1, 4))
    short_free = threshold(harmonic, 6, slope)
    require(long_free == Fraction(23, 60) and short_free == Fraction(3, 10),
            "positive-slope thresholds moved")
    fee = Fraction(1, 3)
    require(short_free < fee < long_free, "fee 1/3 no longer separates the two contracts")


def check_census():
    partition_rows = 0
    lemma_rows = 0
    for rank in range(2, R_MAX + 1):
        rows = partitions(rank)
        partition_rows += len(rows)
        for name, values in tariffs_for(rank).items():
            require(is_tariff(values), name + " left the tariff hypotheses at rank " + str(rank))
            for slope in SLOPES:
                gate = threshold(values, rank, slope)
                require(gate >= 0, name + " produced a negative threshold")
                best_pair = None
                for small in range(1, rank // 2 + 1):
                    short_gain = gamma(values, rank, slope, small)
                    long_gain = lam(values, rank, slope, small)
                    require(short_gain >= long_gain,
                            name + " reversed the short-free and long-free gains")
                    if best_pair is None or short_gain > best_pair:
                        best_pair = short_gain
                require(best_pair == gate, name + " threshold disagrees with its pairs")
                for length in range(0, rank):
                    for piece in range(1, rank - length):
                        gap = values[length] + values[piece] - values[length + piece]
                        require((1 - slope) * gap <= gate,
                                f"one-piece gap exceeded the threshold: {name} R={rank}")
                        lemma_rows += 1
                for parts in rows:
                    if len(parts) == 1:
                        continue
                    credit, short, charged = shortest_credit(values, parts, slope)
                    require(values[short] == min(values[piece] for piece in parts),
                            name + " shortest piece missed the minimum tariff")
                    extras = len(charged)
                    require(credit <= extras * gate,
                            f"per-piece bound failed: {name} R={rank} d={slope} parts={parts}")
                    if name == "identity":
                        require(credit == -slope * (rank - short),
                                "identity credit left the closed form")
                        require(gate == -slope * (rank - 1),
                                "identity threshold left the closed form")
                    # Equal tariff values may be freed interchangeably.
                    for index, piece in enumerate(charged):
                        if values[piece] != values[short]:
                            continue
                        swapped = charged.copy()
                        swapped[index] = short
                        swapped_total = sum((values[item] for item in swapped), Fraction(0))
                        swapped_credit = values[piece] + (1 - slope) * swapped_total - values[rank]
                        require(swapped_credit == credit,
                                name + " tie between free pieces changed the credit")
                for fee in (Fraction(-1), Fraction(0), gate / 2, gate, gate + 1):
                    pays = False
                    for parts in rows:
                        if len(parts) == 1:
                            continue
                        credit, _short, charged = shortest_credit(values, parts, slope)
                        if credit > len(charged) * fee:
                            pays = True
                            break
                    require(pays == (gate > fee),
                            f"existence sign drifted: {name} R={rank} d={slope} c={fee}")
    return partition_rows, lemma_rows


def main():
    check_selected_record()
    check_identity_transfer()
    check_absolute_and_sharp_witnesses()
    check_failure_controls()
    partition_rows, lemma_rows = check_census()
    print(
        "PASS_READING_B_NEGATIVE_SLOPE"
        f" partitions={partition_rows} lemma_gaps={lemma_rows}"
        f" R<={R_MAX} tariffs=7 slopes={len(SLOPES)}"
    )


if __name__ == "__main__":
    main()
