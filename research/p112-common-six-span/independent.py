"""Separate lattice/RREF/dual-functional census; shares authenticated libraries."""

import json
from itertools import combinations

from common import expected_result, read_json, reference_library, require


def dual_census(flats, annihilators, violations, representatives, supports):
    indices = {pair: i for i, pair in enumerate(annihilators)}
    records = []
    for first in representatives:
        maximum = max((first | second).bit_count() for second in flats)
        require(maximum <= 68, "reference union cap")
        entries = []
        for h, support in enumerate(supports):
            if support.bit_count() > maximum + 6:
                continue
            residual = support & ~first
            eligible = [
                (a, residual & violations[a])
                for a in range(1, 512)
                if (residual & violations[a]).bit_count() <= 6
            ]
            for (a, x), (b, y) in combinations(eligible, 2):
                if b < (a ^ b) and (x | y).bit_count() <= 6:
                    require(len(entries) < 2048, "reference completion capacity")
                    entries.append([h, indices[(a, b)], str(x | y)])
        records.append([maximum, sorted(entries)])
    return records


def direct_subsets_bound(records):
    maximum, checked = 0, 0
    for _, entries in records:
        directions = sorted({h for h, _, _ in entries})
        # Four compatible distinct directions would contain a compatible triple
        # and fourth completion. Enumerate actual record quadruples directly.
        require(len(entries) <= 18, "direct quadruple capacity")
        for chosen in combinations(entries, 4):
            if len({row[0] for row in chosen}) != 4:
                continue
            checked += 1
            union = (
                int(chosen[0][2])
                | int(chosen[1][2])
                | int(chosen[2][2])
                | int(chosen[3][2])
            )
            require(union.bit_count() > 6, "four-direction common cut")
        for chosen in combinations(entries, 3):
            if len({row[0] for row in chosen}) == 3:
                union = int(chosen[0][2]) | int(chosen[1][2]) | int(chosen[2][2])
                maximum = max(maximum, 3 if union.bit_count() <= 6 else 0)
        require(len(directions) <= 18, "reference direction capacity")
    require(maximum == 3, "reference sharp triple")
    return {"quadruples_checked": checked, "maximum_projective_directions": maximum}


def run():
    expected = expected_result()
    ref = reference_library()
    roots, points, labels = ref.lattice_data()
    annihilators, flats, violations = ref.rref_flats(labels)
    representatives = [int(x) for x in expected["representative_masks"]]
    ref.validate_quotient(
        roots, points, flats, representatives, expected["flat_orbit_sizes"]
    )
    directions, supports = ref.low_support_directions(points)
    records = dual_census(flats, annihilators, violations, representatives, supports)
    require(
        json.dumps(records) == json.dumps(expected["classes"]),
        "reference complete six-cut table",
    )
    require(
        len(directions) == 1200 and sum(len(e) for _, e in records) == 230,
        "reference domains",
    )
    # The retained checker verifies the actual six-cut triple and min common union.
    witness = ref.witness_check(
        read_json("vendor/pr3253-witness.json"),
        roots,
        points,
        labels,
        annihilators,
        flats,
    )
    summary = {
        "status": "PASS_P112_COMMON_SIX_REFERENCE",
        **direct_subsets_bound(records),
        **witness,
    }
    require(
        json.dumps(summary, sort_keys=True)
        == json.dumps(read_json("REFERENCE.json"), sort_keys=True),
        "reference summary differs",
    )
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
