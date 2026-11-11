"""Check integer premises of the k-summary descent cost bound."""
import json
from pathlib import Path
import sys


def check(transport):
    assert transport["minimum_nonzero_weight"] == 48
    capacities = {int(rank): count for rank, count in transport["max_catalogue_lines_by_rank"].items()}
    assert capacities == {0: 0, 1: 1, 2: 2, 4: 12, 6: 30, 7: 62, 8: 111}
    assert all(capacities[r] <= r for r in (1, 2))
    assert all(capacities[r] <= 3 * r for r in (1, 2, 4))
    lower_multiples = {1: 48, 2: 24, 4: 4, 6: 2, 7: 1, 8: 1}
    mass = {}
    for k in range(1, 5):
        mass[k] = {r: (k - 1 + b) * r for r, b in lower_multiples.items()}
        assert all(v >= 7 * k for v in mass[k].values())
    assert (5 - 1 + lower_multiples[4]) * 4 < 7 * 5
    return dict(status="PASS_JOINT_MONOTONE_DESCENT_BOUND",
                checked_summary_counts=[1, 2, 3, 4], cover_capacities=capacities,
                minimum_nonzero_weight=48, lower_multiples=lower_multiples, mass_by_count=mass)


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Use assertions")
    print(json.dumps(check(json.loads(Path(sys.argv[1]).read_bytes())), sort_keys=True, indent=2))
