"""Exact height-one construction and complete rank-graph ceiling. Apache-2.0."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys


ROOTS = ((-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0))
FILES = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
         "verify.py", "ceiling.py")
EXPECTED = {0: 1480, 1: 4368, 2: 9624, 3: 5760, 4: 2096, 6: 160}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def difference_rank(left: tuple, right: tuple) -> int:
    a, b, c, d = (x - y for x, y in zip(left, right))
    return 2 if a * d != b * c else int(any((a, b, c, d)))


def witness() -> tuple:
    even = tuple((a, b, -a - b, a) for a, b in ROOTS)
    odd = tuple((a, b, b, -a - b) for a, b in ROOTS)
    return even, odd


def validate_witness(parts: tuple) -> None:
    require(len(parts) == 2, "two parts required")
    for part in parts:
        require(len(part) == 6, "each part must contain six matrices")
        for matrix in part:
            require(len(matrix) == 4, "matrix must have four entries")
            require(all(type(x) is int and -1 <= x <= 1 for x in matrix),
                    "entries must be height-one integers")
        for a, b in combinations(part, 2):
            require(difference_rank(a, b) == 2, "within-part rank must be two")
    for a, b in product(*parts):
        require(difference_rank(a, b) == 1, "cross-part rank must be one")


def rank_graph(matrices: tuple) -> tuple:
    require(matrices == tuple(product((-1, 0, 1), repeat=4)),
            "complete lexicographic height-one inventory required")
    near, far = [0] * 81, [0] * 81
    for i, a in enumerate(matrices):
        for j, b in enumerate(matrices):
            rank = difference_rank(a, b)
            if rank == 1:
                near[i] |= 1 << j
            elif rank == 2:
                far[i] |= 1 << j
    return near, far


def triple_ceiling(near: list, far: list) -> tuple:
    histogram = Counter()
    digest = sha256()
    candidates = 0
    for a, b, c in combinations(range(81), 3):
        candidates += 1
        if (far[a] >> b & 1) and (far[a] >> c & 1) and (far[b] >> c & 1):
            common = near[a] & near[b] & near[c]
            count = common.bit_count()
            require(count <= 6, "rank-two triple has more than six contacts")
            histogram[count] += 1
            digest.update(f"{a},{b},{c}:{common:x}\n".encode("ascii"))
    require(dict(histogram) == EXPECTED, "complete triple histogram differs")
    require(candidates == 85320, "complete triple inventory differs")
    return dict(sorted(histogram.items())), digest.hexdigest(), candidates


def rejection_controls() -> list:
    even, odd = witness()
    cases = (
        ("missing_matrix", (even[:-1], odd)),
        ("duplicate_matrix", (even[:-1] + even[:1], odd)),
        ("wrong_height", (((2, 0, 1, -1),) + even[1:], odd)),
        ("boolean_entry", (((True, 0, 1, -1),) + even[1:], odd)),
        ("noninteger_entry", (((-1.0, 0, 1, -1),) + even[1:], odd)),
        ("wrong_shape", (((-1, 0, 1),) + even[1:], odd)),
        ("overlapping_parts", (even, even)),
        ("rank_one_inside", (((0, 0, 1, -1),) + even[1:], odd)),
    )
    passed = []
    for name, bad in cases:
        try:
            validate_witness(bad)
        except ValueError:
            passed.append(name)
        else:
            raise ValueError(f"control accepted: {name}")
    domain = tuple(product((-1, 0, 1), repeat=4))
    for name, bad in (("missing_vertex", domain[:-1]),
                      ("repeated_vertex", domain[:-1] + domain[:1])):
        try:
            rank_graph(bad)
        except ValueError:
            passed.append(name)
        else:
            raise ValueError(f"control accepted: {name}")
    return passed


def main() -> None:
    require(len(sys.argv) == 1, "this verifier accepts no arguments")
    matrices = tuple(product((-1, 0, 1), repeat=4))
    parts = witness()
    validate_witness(parts)
    near, far = rank_graph(matrices)
    histogram, digest, candidates = triple_ceiling(near, far)
    root = Path(__file__).resolve().parent
    result = {
        "status": "PASS_HEIGHT_ONE_SHEAR_BICLIQUES",
        "claim_type": "exact finite certificate",
        "balanced_optimum": 6,
        "matrices": len(matrices),
        "ordered_rank_pairs": len(matrices) ** 2,
        "candidate_triples": candidates,
        "rank_two_triples": sum(histogram.values()),
        "common_rank_one_histogram": histogram,
        "triple_trace_sha256": digest,
        "witness": parts,
        "rejection_controls": rejection_controls(),
        "sources_sha256": {name: sha256((root / name).read_bytes()).hexdigest()
                           for name in FILES},
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
