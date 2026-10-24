"""Check the shared snapshot cut certificate from its source data."""

from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import gzip
import json


HERE = Path(__file__).resolve().parent
LANES = HERE.parent
PINS = {
    "interface": "5c6c51fbffc07a683e922f17532fd90262ae9e23cc3560a696002073dd234ef3",
    "snapshot": "3dd1d7388c7d3bca104a21e642b5fcafe175d83a2f1dfce1a3ee3e86b864276c",
    "core": "fa60b4af013dd8b8db289845e3ed597720ff955751ad270c3d58236b64080877",
    "support_review": "d3a7dc571b2ac2e55945918b0bccd66d99d0d08b6b7af8326e53999578e61fe7",
}


def check(value, message):
    if not value:
        raise ValueError(message)


def read(path, key, compressed=False):
    raw = path.read_bytes()
    if compressed:
        raw = gzip.decompress(raw)
    check(sha256(raw).hexdigest() == PINS[key], "Source pin differs: " + key)
    return json.loads(raw)


def span(basis):
    values = {0}
    for vector in basis:
        values |= {value ^ vector for value in tuple(values)}
    return values


def gram_rank(columns):
    matrix = [[Fraction(sum(col[i] * col[j] for col in columns))
               for j in range(8)] for i in range(8)]
    # A Gram matrix is positive semidefinite. A zero diagonal has a zero row.
    rank = 0
    for pivot in range(8):
        value = matrix[pivot][pivot]
        if not value:
            check(all(not a for a in matrix[pivot]), "Invalid Gram pivot")
            continue
        check(value > 0, "A Gram pivot is negative")
        rank += 1
        column = [matrix[i][pivot] for i in range(8)]
        for i in range(8):
            for j in range(8):
                matrix[i][j] -= column[i] * column[j] / value
    return rank


def main():
    receipt_path = LANES / "cover-algebra/SNAPSHOT-FLAG-CUT.json"
    proof_path = LANES / "cover-algebra/SNAPSHOT-FLAG-CUT.md"
    candidate = json.loads(receipt_path.read_bytes())
    interface = read(LANES / "circuit-interface/INTERFACE.json", "interface")
    snapshots = read(HERE / "BACKWARD-SNAPSHOT-INTERVALS.json.gz", "snapshot", True)
    core = read(LANES / "circuit-interface/CENTRE-FREE-PROGRAMS.json.gz", "core", True)
    support = read(LANES / "cover-algebra/SNAPSHOT-SUPPORT-REVIEW.json", "support_review")
    check(support["status"] == "PASS_EXACT_SNAPSHOT_SUPPORT_AND_SINGLE_CONE_EXCLUSION",
          "The independent support premise did not pass")
    flag = candidate["flag_basis"]
    coordinate = {}
    for bits in range(512):
        value = 0
        for i, vector in enumerate(flag):
            if bits >> i & 1:
                value ^= vector
        check(value not in coordinate, "The flag is dependent")
        coordinate[value] = bits
    check(len(coordinate) == 512, "The flag is incomplete")
    labels = interface["ports"]
    R = [[Fraction(row.get(str(p), "0")) for p in range(112)]
         for row in interface["R"]]
    check(all(value.denominator == 1 for row in R for value in row),
          "The pinned query has a noninteger coefficient")
    R = [[int(value) for value in row] for row in R]
    columns = list(zip(*R))
    shells = [[] for _ in range(9)]
    low_shells = [[] for _ in range(9)]
    for p, label in enumerate(labels):
        dual = [((label & vector).bit_count() & 1) for vector in flag]
        nonzero = [i for i, bit in enumerate(dual) if bit]
        check(nonzero, "A port has zero dual coordinates")
        shells[max(nonzero)].append(p)
        low_shells[min(nonzero)].append(p)
    ranks = [gram_rank([columns[p] for p in shell]) for shell in shells]
    check(shells == candidate["shells"], "The shell partition differs")
    check(ranks == candidate["exact_shell_ranks"], "A shell rank differs")
    check(sum(ranks) == 42, "The lower bound differs")

    frame_spans = [span(basis) for basis in snapshots["frames"]]
    pivots = []
    separation_count = 0
    wrong_order_failures = 0
    for basis, values in zip(snapshots["frames"], frame_spans):
        check(len(values) == 1 << len(basis), "A frame basis is dependent")
        lead = {(coordinate[value] & -coordinate[value]).bit_length() - 1
                for value in values if value}
        check(len(lead) == len(basis), "The pivot count differs")
        pivots.append(lead)
        for i in lead:
            witness = next(value for value in values if value and
                           (coordinate[value] & -coordinate[value]).bit_length() - 1 == i)
            for p in shells[i]:
                separation_count += 1
                check((labels[p] & witness).bit_count() & 1,
                      "A shell coordinate is not excluded by its pivot witness")
            for p in low_shells[i]:
                wrong_order_failures += not any((labels[p] & value).bit_count() & 1
                                               for value in basis)
    check(wrong_order_failures > 0, "The reversed-shell control did not fail")
    edges = set()
    for event in core["backward"]:
        if event[0] != "climb":
            continue
        _, _, wire, before, after, rank = event
        check(frame_spans[before] <= frame_spans[after], "An edge is not monotone")
        check(pivots[before] <= pivots[after], "A pivot cut can be left")
        charge = len(pivots[after] - pivots[before])
        check(charge == rank, "The native edge charge differs")
        edges.add((before, after, rank))
    check(len(edges) == 2880, "The retained edge count differs")
    positive_edge = next(edge for edge in edges if edge[2])
    check(len(pivots[positive_edge[1]] - pivots[positive_edge[0]]) > positive_edge[2] - 1,
          "The undercharged-edge control did not fail")
    output = {
        "status": "PASS_INDEPENDENT_SHARED_SNAPSHOT_FLAG_BOUND_42",
        "checker_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "sources": PINS,
        "candidate_receipt_sha256": sha256(receipt_path.read_bytes()).hexdigest(),
        "candidate_proof_sha256": sha256(proof_path.read_bytes()).hexdigest(),
        "flag": flag,
        "shell_sizes": [len(shell) for shell in shells],
        "exact_gram_ranks": ranks,
        "native_rank_lower_bound": sum(ranks),
        "checked_frames": len(pivots),
        "checked_native_edges": len(edges),
        "separation_checks": separation_count,
        "controls": {"reversed_shell_failures": wrong_order_failures,
                     "one_unit_native_undercharge_rejected": True},
        "scope": "Same-content monotone frame DAGs with scalar sharing. No 64 bound or construction is proved.",
        "proof_checks": ["Pivot-set inclusion for arbitrary nested frames",
                         "Whole-array dimension in each cut inequality",
                         "No separate-tree assumption in the cut sum"],
        "not_checked": ["A positive cache circuit", "Native phase recipes for new edges",
                        "Changed address codes", "Global supplier cost"],
    }
    (HERE / "SNAPSHOT-FLAG-CUT-REVIEW.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(output, sort_keys=True))


if __name__ == "__main__":
    main()
