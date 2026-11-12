#!/usr/bin/env python3
"""Exact negative-slope partition optimizer and exhaustive corroboration.

Produced by Nick Petalas. Apache-2.0. See PROOF.md for the all-rank theorem.
No predecessor executable or selected scientific replay is used.
"""

import argparse
from fractions import Fraction as Q
import hashlib
from itertools import combinations_with_replacement
import json
from pathlib import Path
import platform


MAX_RANK = 4096
GRID_RANK = 10
HARMONIC_RANK = 20
SLOPES = (Q(-3), Q(-1), Q(-1, 3))
FEES = (Q(0), Q(1, 3), Q(1), Q(3), Q(7))


def require(ok, message):
    if not ok:
        raise ValueError(message)


def validate(phi, slope, fee):
    require(2 <= len(phi) <= MAX_RANK + 1, "tariff rank outside 1..4096")
    require(all(isinstance(x, (int, Q)) for x in phi), "tariff must be rational")
    require(isinstance(slope, (int, Q)) and slope < 0, "slope must be negative")
    require(isinstance(fee, (int, Q)) and fee >= 0, "fee must be nonnegative")
    require(phi[0] == 0, "tariff must vanish at zero")
    steps = tuple(phi[j] - phi[j - 1] for j in range(1, len(phi)))
    require(steps[-1] >= 0, "tariff must be nondecreasing")
    require(all(a >= b for a, b in zip(steps, steps[1:])), "tariff must be concave")


def balanced_score(phi, rank, pieces, free, slope):
    """The c-free objective at a fixed shortest piece; caller supplies legal bounds."""
    charged = pieces - 1
    quotient, remainder = divmod(rank - free, charged)
    assert 1 <= free <= quotient
    total = (charged - remainder) * phi[quotient] + remainder * phi[quotient + 1]
    return phi[free] + (1 - slope) * total - phi[rank]


def first_difference(phi, rank, pieces, free, slope):
    charged = pieces - 1
    last = (rank - free + charged - 1) // charged
    return phi[free + 1] - phi[free] - (1 - slope) * (phi[last] - phi[last - 1])


def fixed_length(phi, rank, pieces, slope):
    """Return the first maximizing free rank, c-free score and comparison count."""
    assert 2 <= pieces <= rank < len(phi)
    low, high = 1, rank // pieces
    comparisons = 0
    for _ in range((rank // pieces).bit_length()):
        if low == high:
            break
        middle = (low + high) // 2
        if first_difference(phi, rank, pieces, middle, slope) > 0:
            low = middle + 1
        else:
            high = middle
        comparisons += 1
    require(low == high, "binary search exhausted its explicit bound")
    assert low == 1 or first_difference(phi, rank, pieces, low - 1, slope) > 0
    assert low == rank // pieces or first_difference(phi, rank, pieces, low, slope) <= 0
    return low, balanced_score(phi, rank, pieces, low, slope), comparisons


def optimize(phi, slope, fee):
    """Maximize credit, breaking global ties by the least piece count."""
    validate(phi, slope, fee)
    rank = len(phi) - 1
    best_value, best_pieces, best_free = Q(0), 1, rank
    comparisons = 0
    for pieces in range(2, rank + 1):
        free, before_fee, used = fixed_length(phi, rank, pieces, slope)
        value = before_fee - (pieces - 1) * fee
        comparisons += used
        if value > best_value:
            best_value, best_pieces, best_free = value, pieces, free
    if best_pieces == 1:
        return best_value, (rank,), comparisons
    q, r = divmod(rank - best_free, best_pieces - 1)
    parts = (best_free,) + (q,) * (best_pieces - 1 - r) + (q + 1,) * r
    assert sum(parts) == rank and min(parts) == best_free
    return best_value, parts, comparisons


def all_partitions(rank):
    """Independent bounded dynamic enumeration, without the normal-form theorem."""
    require(1 <= rank <= HARMONIC_RANK, "partition census rank outside 1..20")
    rows = [[] for _ in range(rank + 1)]
    rows[0] = [()]
    for part in range(1, rank + 1):
        for total in range(part, rank + 1):
            # The source row is strictly earlier, so it cannot grow during this loop.
            rows[total].extend(p + (part,) for p in rows[total - part])
    return rows[rank]


def literal_credit(phi, parts, slope, fee):
    """Enumerate every choice of the uncharged part using the fee contract."""
    values = []
    for free_index, free in enumerate(parts):
        value = phi[free] - phi[sum(parts)]
        for index, part in enumerate(parts):
            if index != free_index:
                value += phi[part] - (fee + slope * phi[part])
        values.append(value)
    return max(values)


def brute_fixed(phi, rows, slope):
    best = {}
    for parts in rows:
        pieces = len(parts)
        candidate = (literal_credit(phi, parts, slope, Q(0)), -min(parts))
        if pieces not in best or candidate > best[pieces]:
            best[pieces] = candidate
    return best


def compare_case(phi, rows, slope, counts):
    rank = len(phi) - 1
    exact = brute_fixed(phi, rows, slope)
    counts["partitions_scored"] += len(rows)
    counts["free_choices_scored"] += sum(map(len, rows))
    for pieces in range(2, rank + 1):
        free, score, used = fixed_length(phi, rank, pieces, slope)
        require((score, -free) == exact[pieces], "fixed-length optimizer disagrees")
        bound = (rank // pieces - 1).bit_length()
        require(used <= bound, "binary comparison bound exceeded")
        counts["fixed_length_comparisons"] += 1
        for s in range(1, rank // pieces):
            actual = balanced_score(phi, rank, pieces, s + 1, slope)
            actual -= balanced_score(phi, rank, pieces, s, slope)
            require(actual == first_difference(phi, rank, pieces, s, slope), "difference formula")
            counts["difference_identities"] += 1
    for fee in FEES:
        expected = max((v[0] - (k - 1) * fee, -k) for k, v in exact.items())
        value, parts, _ = optimize(phi, slope, fee)
        require((value, -len(parts)) == expected, "global optimizer disagrees")
        require(literal_credit(phi, parts, slope, fee) == value, "witness does not attain")
        counts["global_comparisons"] += 1
    counts["tariff_slope_cases"] += 1


def exhaustive_grid(counts):
    for rank in range(1, GRID_RANK + 1):
        rows = all_partitions(rank)
        for increasing in combinations_with_replacement(range(4), rank):
            phi = [Q(0)]
            for step in reversed(increasing):
                phi.append(phi[-1] + step)
            for slope in SLOPES:
                compare_case(phi, rows, slope, counts)
            counts["integer_tariffs"] += 1


def harmonic_grid(counts):
    phi = [Q(0)]
    for rank in range(1, HARMONIC_RANK + 1):
        phi.append(phi[-1] + Q(1, rank))
        rows = all_partitions(rank)
        for slope in (*SLOPES, Q(-1, 20)):
            compare_case(phi, rows, slope, counts)


def witnesses():
    phi = [Q(0)]
    for rank in range(1, 13):
        phi.append(phi[-1] + Q(1, rank))
    expected = ((2, 4, Q(122407, 27720)), (3, 2, Q(41747, 5544)))
    for pieces, free, score in expected:
        actual_free, actual_score, _ = fixed_length(phi, 12, pieces, Q(-1))
        require((actual_free, actual_score) == (free, score), "interior-free witness")
    value, parts, _ = optimize(phi, Q(-1), Q(0))
    require(parts == (1,) * 12, "zero-fee singleton optimum")
    require(value == 23 - phi[12], "zero-fee value")
    # This is neither the balanced nor the extreme three-part partition.
    winner = literal_credit(phi, (2, 5, 5), Q(-1), Q(0))
    require(winner > literal_credit(phi, (4, 4, 4), Q(-1), Q(0)), "balanced control")
    require(winner > literal_credit(phi, (1, 1, 10), Q(-1), Q(0)), "extreme control")
    return 6


def failure_controls():
    cases = (
        ((0, 1, 3), -1, 0),
        ((0, 2, 1), -1, 0),
        ((1, 2, 3), -1, 0),
        ((0, 1, 2), 0, 0),
        ((0, 1, 2), 1, 0),
        ((0, 1, 2), -1, -1),
        ((0, 1.0, 2), -1, 0),
        ((0,), -1, 0),
        ((0,) * (MAX_RANK + 2), -1, 0),
    )
    for phi, slope, fee in cases:
        rejected = False
        try:
            optimize(phi, slope, fee)
        except ValueError:
            rejected = True
        require(rejected, "invalid contract accepted")
    # Without concavity even balancing the charged pieces can lower the credit.
    bad = tuple(map(Q, (0, 0, 1, 1, 4, 4, 4)))
    require(literal_credit(bad, (1, 1, 4), Q(-1), Q(0)) == 4, "nonconcave witness")
    require(literal_credit(bad, (1, 2, 3), Q(-1), Q(0)) == 0, "nonconcave balance")
    # Choosing a balanced whole partition is a genuinely failing candidate.
    linear = tuple(map(Q, range(7)))
    require(literal_credit(linear, (2, 2, 2), Q(-1), Q(0)) == 4, "linear balanced")
    require(literal_credit(linear, (1, 2, 3), Q(-1), Q(0)) == 5, "linear unbalanced")
    return len(cases) + 4


def write_receipt(path, counts):
    package = Path(__file__).resolve().parent
    destination = Path(path).resolve()
    require(not destination.is_relative_to(package), "receipt must be outside the package")
    files = sorted(p for p in package.iterdir() if p.is_file())
    receipt = {
        "schema": "negative-slope-partition-verification/v1",
        "status": "passed",
        "python": platform.python_version(),
        "counts": counts,
        "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
    }
    written = destination.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    require(written > 0, "empty receipt")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", help="optional hash-bound JSON output outside the package")
    args = parser.parse_args()
    counts = dict.fromkeys(("integer_tariffs", "tariff_slope_cases", "partitions_scored",
                           "free_choices_scored", "fixed_length_comparisons",
                           "difference_identities", "global_comparisons"), 0)
    exhaustive_grid(counts)
    harmonic_grid(counts)
    counts["witness_checks"] = witnesses()
    counts["failure_controls"] = failure_controls()
    counts["errors"] = 0
    if args.receipt:
        write_receipt(args.receipt, counts)
    print("PASS_NEGATIVE_SLOPE_PARTITION_OPTIMIZER " + json.dumps(counts, sort_keys=True))


if __name__ == "__main__":
    main()
