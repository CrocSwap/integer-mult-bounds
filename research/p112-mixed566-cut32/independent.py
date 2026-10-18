"""Check the new covering inequalities by integer occupancy. Apache-2.0."""

import json
from itertools import product

from verify import (
    PACKAGE,
    authenticate,
    canonical,
    check_premise_receipt,
    read_json,
    require,
)


def main():
    check_premise_receipt(authenticate())
    result = read_json(PACKAGE / "RESULT.json")
    require(
        type(result["schema_version"]) is int and result["schema_version"] == 1,
        "result schema version",
    )
    require(
        result["cut"] == 32 and result["binary_rank_bounds"] == [5, 6, 6],
        "fixed theorem contract",
    )
    require(
        result["inherited_concentration_replayed"] is False
        and result["sharpness_claimed"] is False
        and result["new_caller_claimed"] is False,
        "claim boundaries",
    )
    maxima = []
    for full_union, axis in ((82, 29), (84, 31)):
        maximum = 0
        feasible = 0
        # Each of three concentrated pieces chooses one axis and at most its cap.
        # This checks all 8*13*21*21 integer occupancy relaxations per plane type.
        for sides in product((0, 1), repeat=3):
            for counts in product(range(13), range(21), range(21)):
                loads = [
                    sum(n for n, side in zip(counts, sides, strict=True) if side == a)
                    for a in (0, 1)
                ]
                occupancy = min(axis, loads[0]) + min(axis, loads[1])
                maximum = max(maximum, occupancy)
                feasible += occupancy >= full_union - 32
        require(feasible == 0, "concentrated cover satisfies the forbidden size")
        maxima.append(maximum)
    require(maxima == [49, 51], "independent maxima")
    require(
        [r["coverage_at_most"] for r in result["D6"]] == maxima,
        "receipt occupancy maxima",
    )
    require(
        canonical(result["E6"])
        == canonical({"required_incidence": 92, "allowed_incidence": 86}),
        "E6 gap",
    )
    print(
        json.dumps(
            {
                "status": "PASS_INDEPENDENT_OCCUPANCY",
                "occupancy_cases": 2 * 8 * 13 * 21 * 21,
                "maxima": maxima,
                "inherited_geometry_replayed": False,
            }
        )
    )


if __name__ == "__main__":
    main()
