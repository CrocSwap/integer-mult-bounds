"""Check the nine-deadline relay floor with arbitrary new rational charts.

Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
PR7750 supplies the fixed-chart paths and the retained support/coset replay.
"""

import argparse
from collections import Counter
from functools import reduce
import hashlib
import importlib.util
from itertools import combinations
import json
from math import gcd
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
PRIME = 1000003


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer_rank(rows):
    """Eliminate with integer row operations and primitive row division."""
    matrix = [list(row) for row in rows]
    rank = 0
    for column in range(8):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        value = matrix[rank][column]
        for i in range(rank+1, len(matrix)):
            factor = matrix[i][column]
            if factor:
                row = [value*a-factor*b for a, b in zip(matrix[i], matrix[rank], strict=True)]
                divisor = reduce(gcd, row, 0)
                matrix[i] = [a // divisor for a in row] if divisor else row
        rank += 1
    return rank


def modular_rank(rows):
    matrix = [[a % PRIME for a in row] for row in rows]
    rank = 0
    for column in range(8):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][column]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inverse = pow(matrix[rank][column], -1, PRIME)
        matrix[rank] = [(a*inverse) % PRIME for a in matrix[rank]]
        for i in range(rank+1, len(matrix)):
            factor = matrix[i][column]
            if factor:
                matrix[i] = [(a-factor*b) % PRIME
                             for a, b in zip(matrix[i], matrix[rank], strict=True)]
        rank += 1
    return rank


def load_source():
    for pin in json.loads((PACKAGE / "SOURCE-PINS.json").read_text()):
        require(hashlib.sha256((PACKAGE / pin["path"]).read_bytes()).hexdigest()
                == pin["sha256"], "retained source hash")
    path = PACKAGE / "retained/pr7750/verify.py"
    spec = importlib.util.spec_from_file_location("fixed_relay", path)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    result = source.calculate()
    require(result == json.loads((path.parent / "RESULT.json").read_text()),
            "complete predecessor replay")
    direct_source, direct_result = source.load_source()
    geometry, word = direct_source.load_sources()
    return result, direct_result, geometry, word


def check_pair(rank):
    require(rank >= 6, "dimension-four intersection exceeds two")


def pair_certificate(geometry, word):
    fours = sorted(int(i) for i, frame in word["frames"].items() if frame["dim"] == 4)
    require(len(fours) == 70, "complete dimension-four inventory")
    complement = {i: [geometry.integer_row(row) for row in word["frames"][str(i)]["A"]]
                  for i in fours}
    require(all(len(rows) == integer_rank(rows) == 4 for rows in complement.values()),
            "rational complement dimensions")
    require(all(PRIME % d for d in range(2, 1001)), "modular prime")
    cases = []
    histogram = Counter()
    for a, b in combinations(fours, 2):
        joined = complement[a] + complement[b]
        rank = integer_rank(joined)
        require(rank == modular_rank(joined), "integer/modular pair rank")
        check_pair(rank)
        intersection = 8-rank
        histogram[intersection] += 1
        cases.append(dict(charts=[a, b], complement_rank=rank,
                          intersection_dimension=intersection, subspace_distance=8-2*intersection))
    require(histogram == {0: 1155, 2: 1260} and len(cases) == 2415, "complete pair census")
    return dict(pairs=cases, intersection_histogram={str(k): histogram[k] for k in sorted(histogram)},
                pairs_checked=len(cases), modular_prime=PRIME,
                minimum_distinct_subspace_distance=4)


def coordinate_complement(indices):
    return [tuple(int(i == j) for j in range(8)) for i in range(8) if i not in indices]


def controls():
    a = {0, 1, 2, 3}
    b = {0, 1, 2, 4}
    c = {0, 1, 2, 5}
    rejected = 0
    for left, right in ((a, a), (a, b), (a, c), (b, c)):
        rank = integer_rank(coordinate_complement(left)+coordinate_complement(right))
        require(rank == modular_rank(coordinate_complement(left)+coordinate_complement(right)),
                "control rank agreement")
        try:
            check_pair(rank)
        except ValueError:
            rejected += 1
        else:
            raise ValueError("false pair-floor control accepted")
    # A common three-space does permit the proposed rank-six tree in a
    # different source geometry. It fails the actual source's pair premise.
    hub = {0, 1, 2}
    require(all(hub < leaf for leaf in (a, b, c)), "common-hub positive control")
    require(len(hub)+sum(len(leaf)-len(hub) for leaf in (a, b, c)) == 6,
            "rank-six star positive control")
    require(4+2+2+4 == 2*6, "changed-geometry tour equality")
    require(4*4 == 2*8 and 8 > 6, "actual four-terminal tour floor")
    require(max(17*k+2*(6-k) for k in range(3)) == 42 < 48,
            "small-component support bound")
    return dict(pair_premise_rejections=rejected, rank_six_changed_geometry_star=True,
                changed_geometry_tour_equality=True, actual_tour_floor=8,
                low_stock_support_bound=42)


def calculate():
    relay_result, direct_result, geometry, word = load_source()
    pairs = pair_certificate(geometry, word)
    require(relay_result["chain_checks"]["maximum_supports"]["6"] == 35,
            "retained high-chain bound")
    require(direct_result["donor_caps"] == {"1": 1, "2": 2, "4": 17, "6": 30},
            "source support caps")
    require(all(row["minimum_distance"] > 42 for row in direct_result["cases"]),
            "all rational relay separation")
    return dict(pair_certificate=pairs, target_minimum_distances=[row["minimum_distance"]
                for row in direct_result["cases"]], support_bound_without_original_six=42,
                support_bound_with_original_six=35, maximum_component_support=42,
                controls=controls(), scope="Nine fixed BIT deadlines with arbitrary new rational relay charts and no new source information; other arrivals not claimed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = calculate()
    if args.write_result:
        (PACKAGE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        require(result == json.loads((PACKAGE / "RESULT.json").read_text()), "result mismatch")
    print("PASS_BIT_RATIONAL_RELAY_PRICE_FLOOR 2415 pairs; support<=42<48")


if __name__ == "__main__":
    main()
