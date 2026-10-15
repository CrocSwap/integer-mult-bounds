"""Literal checks of the affine normalization, native census and batch bounds.

The unrestricted r[(C2)^6]=14 value is reported by Gavrylkiv (JIS 2017,
Table 3). The native enumerators independently rebuild its finite lower bound.
Tairitsu-Aya, substantial OpenAI Codex assistance. Apache-2.0.
"""
import math
import random


def require(ok, message):
    if not ok:
        raise ValueError(message)


def differences(points):
    return {a ^ b for a in points for b in points}


def normalize(points):
    """Translate one point to zero, then choose an ordered linear basis."""
    require(points and len(set(points)) == len(points), "distinct nonempty input set")
    shifted = [p ^ points[0] for p in points]
    coordinates = {0: 0}
    basis = []
    for point in shifted:
        if point not in coordinates:
            index = len(basis)
            basis.append(point)
            coordinates.update({v ^ point: mask | (1 << index) for v, mask in list(coordinates.items())})
    require(len(basis) == 6 and len(coordinates) == 64, "full affine span is necessary")
    result = sorted(coordinates[p] for p in shifted)
    require({0, 1, 2, 4, 8, 16, 32} <= set(result), "normalized affine basis")
    for value, mask in coordinates.items():
        reconstructed = 0
        for j, v in enumerate(basis):
            if mask & (1 << j):
                reconstructed ^= v
        require(reconstructed == value, "normalization invertibility")
    require(len(differences(result)) == len(differences(points)), "coverage invariant under affine normalization")
    return result


def affine_controls(incumbent, near):
    rng = random.Random(202610142108)
    cases = 0
    for points in (incumbent, near):
        for _ in range(128):
            images = [1 << j for j in range(6)]
            for _ in range(30):
                i, j = rng.sample(range(6), 2)
                images[i] ^= images[j]
            offset = rng.randrange(64)
            transformed = []
            for point in points:
                value = offset
                for j in range(6):
                    if point & (1 << j):
                        value ^= images[j]
                transformed.append(value)
            rng.shuffle(transformed)
            normalized = normalize(transformed)
            require(len(differences(normalized)) == len(differences(points)), "independent affine-image control")
            cases += 1
    try:
        normalize(list(range(13)))
    except ValueError as error:
        require("full affine span" in str(error), "proper-subspace control failed for wrong reason")
    else:
        raise ValueError("proper-subspace input was treated as full affine span")
    return cases


def audit(first, second, incumbent, old_controls):
    keys = ("status", "normalized_sets", "maximum_coverage", "histogram")
    require(all(first[key] == second[key] for key in keys), "independent unrestricted censuses disagree")
    require(first["status"] == "EXHAUSTED", "complete unrestricted basis census required")
    require(first["normalized_sets"] == math.comb(57, 6) == 36288252, "all affine-basis-normalized 13-sets")
    histogram = first["histogram"]
    require(sum(histogram.values()) == first["normalized_sets"] and all(v > 0 for v in histogram.values()),
            "complete coverage histogram")
    require(max(map(int, histogram)) == first["maximum_coverage"] == 63, "unrestricted 13-point maximum")
    witnesses = []
    for native in (first, second):
        points = native["maximum_witness"]
        require(len(points) == len(set(points)) == 13 and all(type(p) is int and 0 <= p < 64 for p in points),
                "thirteen distinct binary points")
        require({0, 1, 2, 4, 8, 16, 32} <= set(points), "native normalized domain")
        require(len(differences(points)) == 63, "literal maximum-witness coverage")
        witnesses.append(sorted(points))
    require(len(incumbent) == len(set(incumbent)) == 14 and len(differences(incumbent)) == 64,
            "retained attaining fourteen-point basis")
    transformed = affine_controls(incumbent, witnesses[0])
    # Source calls k<=11 have at most C(k,2) nonzero differences. The complete
    # census gives at least one missing mask for k=12,13. Each missing output
    # needs >=4 instead of >=2 readouts; larger k already costs >=14+126.
    query_bounds = []
    for calls in range(1, 15):
        missing = max(0, 63 - math.comb(calls, 2))
        if calls <= 13:
            missing = max(missing, 1)
        reads = 126 + 2 * missing
        query_bounds.append({"source_calls": calls, "missing_masks_at_least": missing,
                             "readouts_at_least": reads, "queries_at_least": calls + reads})
    require(min(row["queries_at_least"] for row in query_bounds) == 140, "global batch query floor")
    adds = []
    for width in (12, 14):
        covered = old_controls[6, width]["max_coverage"]
        adds.append({"source_adds": width, "total_adds_at_least": width + 126 + 2 * (64 - covered)})
    adds.extend([{"source_adds": 16, "total_adds_at_least": 142},
                 {"source_adds": "even >=18", "total_adds_at_least": 144}])
    require(min(row["total_adds_at_least"] for row in adds) == 142, "global batch add floor")
    return {
        "domain": "all 13-element subsets of F2^6 up to existence of an affine-basis normalization",
        "normalization": {"fixed_points": [0, 1, 2, 4, 8, 16, 32], "available_points": 57,
                          "chosen_points": 6, "normalized_sets": first["normalized_sets"]},
        "coverage_histogram": histogram,
        "maximum_coverage": 63,
        "maximum_witnesses": witnesses,
        "attaining_14_points": incumbent,
        "affine_image_controls": transformed,
        "proper_subspace_control_rejected": True,
        "query_lower_bounds": query_bounds,
        "add_lower_bounds": adds,
        "minimum_paired_universal_source_calls_any_add_budget": 14,
        "global_batch_optimum": {"queries": 140, "adds": 142},
        "literature": {"author": "Volodymyr Gavrylkiv", "title": "Bases in Dihedral and Boolean Groups",
                       "year": 2017, "location": "Table 3", "reported_value": "r[(C2)^6]=14",
                       "url": "https://cs.uwaterloo.ca/journals/JIS/VOL20/Gavrylkiv/gav4.pdf"},
    }
