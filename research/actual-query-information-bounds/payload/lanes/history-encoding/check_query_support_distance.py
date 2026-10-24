"""Check the source data for the exact query support bound."""

from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
INTERFACE_PIN = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
SNAPSHOT_PIN = "3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c"
SUPPORT_PIN = "d3a7dc571b2ac2e55945918b0bccd66d99d0d08b6b7af8326e53999578e61fe7"
NONZERO_PER_QUARTET = [0, 8, 4, 6, 5]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def quartet_data(columns):
    groups = defaultdict(list)
    for p, column in enumerate(columns):
        support = sum((value != 0) << i for i, value in enumerate(column))
        require(support.bit_count() == 4, "A root has the wrong support size")
        require(all(value in (-1, 0, 1) for value in column), "A root coefficient differs")
        groups[support].append(p)
    require(len(groups) == 14, "The quartet count differs")
    for support, ports in groups.items():
        indices = [i for i in range(8) if support >> i & 1]
        patterns = {tuple(columns[p][i] * columns[p][indices[0]] for i in indices)
                    for p in ports}
        require(len(ports) == len(patterns) == 8,
                "A quartet does not contain all sign patterns up to sign")
    return groups


def main():
    interface_raw = (HERE.parent / "circuit-interface/INTERFACE.json").read_bytes()
    snapshot_raw = gzip.decompress((HERE / "BACKWARD-SNAPSHOT-INTERVALS.json.gz").read_bytes())
    support_raw = (HERE.parent / "cover-algebra/SNAPSHOT-SUPPORT-REVIEW.json").read_bytes()
    require(sha256(interface_raw).hexdigest() == INTERFACE_PIN, "The interface pin differs")
    require(sha256(snapshot_raw).hexdigest() == SNAPSHOT_PIN, "The snapshot pin differs")
    require(sha256(support_raw).hexdigest() == SUPPORT_PIN, "The support review pin differs")
    source = json.loads(interface_raw)
    snapshots = json.loads(snapshot_raw)
    R = [[Fraction(row.get(str(p), "0")) for p in range(112)] for row in source["R"]]
    require(all(value.denominator == 1 for row in R for value in row), "A root coefficient is not integral")
    R = [[int(value) for value in row] for row in R]
    columns = list(zip(*R))
    groups = quartet_data(columns)
    lower_by_size = {}
    exact_support_bounds = {}
    for support in range(1, 256):
        bound = sum(NONZERO_PER_QUARTET[(support & block).bit_count()] for block in groups)
        size = support.bit_count()
        lower_by_size[size] = min(bound, lower_by_size.get(size, bound))
        exact_support_bounds[str(support)] = bound
    require(lower_by_size == {1: 56, 2: 76, 3: 78, 4: 53, 5: 73, 6: 75, 7: 77, 8: 70},
            "A coefficient support bound differs")
    attained = [sum(sum(a * b for a, b in zip(query, column)) != 0 for column in columns)
                for query in columns]
    require(set(attained) == {53}, "An old-root query does not attain 53")
    frame_histogram = defaultdict(Counter)
    for basis in snapshots["frames"]:
        allowed = sum(all((label & vector).bit_count() % 2 == 0 for vector in basis)
                      for label in source["ports"])
        frame_histogram[len(basis)][allowed] += 1
    require(all(count <= 20 for rank, values in frame_histogram.items()
                if rank >= 2 for count in values), "A high-rank frame permits more than 20 ports")
    broken = list(columns)
    first_group = next(iter(groups.values()))
    broken[first_group[1]] = broken[first_group[0]]
    try:
        quartet_data(broken)
    except ValueError:
        duplicate_rejected = True
    else:
        duplicate_rejected = False
    require(duplicate_rejected, "The duplicate-sign control passed")
    wrong_table = [0, 8, 4, 6, 6]
    query = columns[0]
    query_support = sum((value != 0) << i for i, value in enumerate(query))
    false_bound = sum(wrong_table[(query_support & block).bit_count()] for block in groups)
    require(false_bound > attained[0], "The excessive quartet bound control passed")
    result = {
        "status": "PASS_EXACT_QUERY_SUPPORT_MINIMUM_53",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources": {"interface_sha256": INTERFACE_PIN,
                    "snapshot_decompressed_sha256": SNAPSHOT_PIN,
                    "independent_support_review_sha256": SUPPORT_PIN},
        "quartets": {str(block): ports for block, ports in sorted(groups.items())},
        "nonzero_per_quartet_lower_bounds": NONZERO_PER_QUARTET,
        "lower_bounds_by_nonzero_coefficient_count": lower_by_size,
        "all_255_coefficient_support_bounds": exact_support_bounds,
        "minimum_source_port_support": 53,
        "attaining_old_root_directions": len(attained),
        "frame_allowed_port_histogram": {rank: dict(sorted(values.items()))
                                         for rank, values in sorted(frame_histogram.items())},
        "controls": {"duplicate_sign_pattern_rejected": duplicate_rejected,
                     "excessive_quartet_bound_rejected": True},
        "consequence": "A k-dimensional query space needs at least k+2 rank-at-least-two birth fields in one common span.",
        "not_claimed": ["A native rank lower bound of 64 for shared networks",
                        "A constructive cache network", "A full supplier improvement"],
    }
    (HERE / "QUERY-SUPPORT-DISTANCE.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ("quartets", "all_255_coefficient_support_bounds")}, sort_keys=True))


if __name__ == "__main__":
    main()
