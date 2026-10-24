"""Verify one exact cut bound for a shared monotone cache network."""

from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
FLAG = [243, 249, 311, 132, 131, 489, 442, 405, 178]
SNAPSHOT = "3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c"
INTERFACE = "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3"
CORE = "fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exact_rank(matrix):
    pivots = {}
    for row in matrix:
        row = [Fraction(value) for value in row]
        for index, old in sorted(pivots.items()):
            scale = row[index]
            row = [a-scale*b for a, b in zip(row, old)]
        index = next((i for i, value in enumerate(row) if value), None)
        if index is not None:
            scale = row[index]
            pivots[index] = [value/scale for value in row]
    return len(pivots)


def binary_pivots(basis, coordinates):
    pivots = {}
    for vector in basis:
        vector = coordinates[vector]
        for index, old in sorted(pivots.items()):
            if vector >> index & 1:
                vector ^= old
        if vector:
            index = (vector & -vector).bit_length()-1
            pivots[index] = vector
    return set(pivots)


def main():
    coordinates = {0: 0}
    for index, vector in enumerate(FLAG):
        require(vector not in coordinates, "The flag vectors are dependent")
        coordinates.update({old ^ vector: bits | 1 << index
                            for old, bits in tuple(coordinates.items())})
    require(len(coordinates) == 512, "The flag is not a binary basis")
    interface_raw = (HERE.parent / "circuit-interface/INTERFACE.json").read_bytes()
    require(sha256(interface_raw).hexdigest() == INTERFACE, "The interface pin differs")
    data = json.loads(interface_raw)
    labels = data["ports"]
    R = [[Fraction(row.get(str(p), "0")) for p in range(112)] for row in data["R"]]
    shells = [[] for _ in range(9)]
    for p, label in enumerate(labels):
        dual = sum(((label & vector).bit_count() % 2) << i
                   for i, vector in enumerate(FLAG))
        require(dual != 0, "A nonzero port has zero dual coordinates")
        shells[dual.bit_length()-1].append(p)
    ranks = [exact_rank([[row[p] for p in shell] for row in R]) for shell in shells]
    require(ranks == [0, 1, 1, 2, 8, 6, 8, 8, 8], "The exact shell ranks differ")
    snapshot_raw = gzip.decompress((HERE.parent / "history-encoding/BACKWARD-SNAPSHOT-INTERVALS.json.gz").read_bytes())
    require(sha256(snapshot_raw).hexdigest() == SNAPSHOT, "The snapshot pin differs")
    source = json.loads(snapshot_raw)
    frame_pivots = [binary_pivots(basis, coordinates) for basis in source["frames"]]
    require(all(len(pivots) == len(basis) for pivots, basis in zip(frame_pivots, source["frames"])),
            "A frame basis is dependent")
    # Check the support separation for every possible permitted port at each frame.
    support_tests = 0
    for basis, pivots in zip(source["frames"], frame_pivots):
        for i in pivots:
            for p in shells[i]:
                support_tests += 1
                require(any((labels[p] & vector).bit_count() % 2 for vector in basis),
                        "A shell port can enter its cut without a native edge")
    core_raw = gzip.decompress((HERE.parent / "circuit-interface/CENTRE-FREE-PROGRAMS.json.gz").read_bytes())
    require(sha256(core_raw).hexdigest() == CORE, "The core pin differs")
    edges = set()
    for event in json.loads(core_raw)["backward"]:
        if event[0] != "climb":
            continue
        _, _, wire, before, after, cost = event
        old, new = frame_pivots[before], frame_pivots[after]
        require(old <= new, "A retained edge is not monotone in the flag cuts")
        require(len(new-old) == cost, "The cut charge differs from native rank")
        edges.add((before, after, cost))
    review = HERE / "SNAPSHOT-SUPPORT-REVIEW.json"
    dependency = json.loads(review.read_bytes())
    require(dependency["status"] == "PASS_EXACT_SNAPSHOT_SUPPORT_AND_SINGLE_CONE_EXCLUSION",
            "The exact support review is absent")
    require(dependency["inputs"]["snapshot_decompressed_sha256"] == SNAPSHOT,
            "The support review uses another snapshot source")
    result = {
        "status": "PASS_SHARED_MONOTONE_CACHE_DAG_LOWER_BOUND_42",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources": {"snapshot_decompressed_sha256": SNAPSHOT, "interface_sha256": INTERFACE,
                    "core_decompressed_sha256": CORE,
                    "support_review_sha256": sha256(review.read_bytes()).hexdigest()},
        "flag_basis": FLAG, "shells": shells, "exact_shell_ranks": ranks,
        "rank_sum": sum(ranks), "retained_edge_count": len(edges),
        "frame_shell_support_tests": support_tests,
        "scope": "Same-content monotone frame networks, arbitrary scalar sharing and all snapshot times. This bound does not prove64 or optimality.",
        "not_checked": ["A constructive merged cache network", "Internal native-child cuts", "A changed core", "Logical address re-gauging", "A complete supplier invoice"],
    }
    output = HERE / "SNAPSHOT-FLAG-CUT.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in result.items() if key != "shells"}, sort_keys=True))


if __name__ == "__main__":
    main()
