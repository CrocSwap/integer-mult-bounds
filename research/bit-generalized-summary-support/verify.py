"""Reconstruct generalized code support and projected catalogue bounds."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SOURCE = "research/paired-query-only-bit/retained/inputs/BIT-NATIVE-WORD.json.gz"
sys.path.insert(0, str(HERE))
import bounds
import catalogue
import weights


def projection(values):
    """Return the rank and number of columns whose deletion lowers it."""
    pivots = {}
    dependencies = 0
    count = 0
    for count, value in enumerate(values, 1):
        support = 1 << (count - 1)
        while value:
            index = value.bit_length() - 1
            if index not in pivots:
                pivots[index] = value, support
                break
            pivot, provenance = pivots[index]
            value ^= pivot
            support ^= provenance
        else:
            dependencies |= support
    return len(pivots), count - dependencies.bit_count()


def verify(path):
    weight = weights.audit(path)
    assert (weight["d1"], weight["d2"], weight["distinct_columns"], weight["zero_columns"]) == (48, 75, 111, 0)
    capacities, masks = catalogue.scan(path)
    assert capacities == {0: 0, **bounds.CAPACITY}
    assert len(masks) == 180
    assert 1 + 62 * bounds.TARGET / 7 < Fraction(5, 3)
    distances = {1: 48}
    for t in range(2, 10):
        avg = bounds.ceil(Fraction((2**t - 1) * 75, 3 * 2**(t-2)))
        distances[t] = max(avg, 111 - (2**(9-t) - 1))

    profiles = {}
    for k in range(6, 10):
        tested, survivors = set(), []
        for row in bounds.profiles(k):
            assert len(tested) < bounds.CAP and row not in tested
            assert row == tuple(sorted(row, reverse=True))
            tested.add(row)
            if len(row) < k:
                continue
            for t in range(1, k + 1):
                tail = row[k-t:]
                available = sum(capacities[r] for r in tail)
                if available < max(distances[t], bounds.incidence_lower(len(tail), t)):
                    break
            else:
                survivors.append(row)
        profiles[k] = dict(tested=len(tested), survivors=survivors)

    assert not profiles[6]["survivors"] and not profiles[7]["survivors"]
    assert set(profiles[8]["survivors"]) == {(6,) * 9}
    assert set(profiles[9]["survivors"]) == {(6,) * 10, (6,) * 10 + (1,), (7,) + (6,) * 9}

    rows = weights.read_rows(path)
    columns = [sum(((row >> i) & 1) << j for j, row in enumerate(rows)) for i in range(111)]

    def uncovered(mask):
        return projection(col for i, col in enumerate(columns) if not (mask >> i) & 1)

    assert uncovered(0) == (9, 0) and uncovered(rows[0])[0] < 9
    singleton = rows[0] & -rows[0]
    assert uncovered(rows[0] ^ singleton) == (9, 1)
    projections = Counter(uncovered(a | b) for a, b in combinations(masks, 2))
    assert projections == {(9, 0): 16110}
    assert max(mask.bit_count() for mask in masks) == 30 < weight["d1"] - 1
    return dict(status="PASS_GENERALIZED_BIT_SUMMARY_SUPPORT", profiles=profiles,
                required_support_by_dimension=distances, weights=weight,
                rank_six_pair_complement_ranks={"9": projections[(9, 0)]},
                rank_six_pair_deletion_rank_drops={"0": projections[(9, 0)]},
                remaining_profiles=[],
                dependencies={SOURCE: weights.PIN})


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Use assertions")
    result = verify(HERE.parents[1] / SOURCE)
    assert json.dumps(result, sort_keys=True, indent=2) + "\n" == (HERE / "RECEIPT.json").read_text()
    print(result["status"])
