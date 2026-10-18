"""Independent binary endpoint-rank census; no predecessor code is imported."""

import argparse
import hashlib
import json
from collections import Counter
from itertools import pairwise
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
N = 9


def require(condition, message):
    if not condition:
        raise ValueError(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def read_json(path):
    require(path.stat().st_size <= 500_000, "input capacity")
    raw = path.read_bytes()
    return json.loads(raw, object_pairs_hook=unique_object)


def authenticate():
    manifest = read_json(PACKAGE / "SOURCES.json")
    for item in manifest["files"]:
        if item["usage"] == "input":
            raw = (ROOT / item["path"]).read_bytes()
            require(
                hashlib.sha256(raw).hexdigest() == item["sha256"], "live source SHA256"
            )
    pins = read_json(PACKAGE / "PREDECESSOR.json")
    for item in pins["files"]:
        raw = (PACKAGE / item["local"]).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == item["sha256"], "predecessor SHA256")
        header = b"blob " + str(len(raw)).encode() + b"\0"
        require(
            hashlib.sha1(header + raw).hexdigest() == item["git_blob"],
            "predecessor blob",
        )


def image(columns, vector):
    result = 0
    for bit, column in enumerate(columns):
        if (vector >> bit) & 1:
            result ^= column
    return result


def multiply(left, right):
    return tuple(image(left, column) for column in right)


def identity(n):
    return tuple(1 << i for i in range(n))


def span(vectors):
    """Set closure, deliberately not Gaussian elimination. At most 512 elements."""
    values = {0}
    for vector in vectors:
        values |= {value ^ vector for value in values}
    return values


def binary_rank(vectors):
    size = len(span(vectors))
    require(size & (size - 1) == 0, "binary span cardinality")
    return size.bit_length() - 1


def frame(vectors, n=N):
    """Closed-form canonical frame action on Pauli labels, with phases forgotten.

    For extended basis a_i and dual basis d_i, the frame is the product of
    commuting symplectic transvections along (a_i, a_i+d_i), i < dim(frame).
    This is derived from the retained P/D/C semantics in the README.
    """
    require(type(n) is int and 1 <= n <= N, "address dimension")
    require(len(vectors) <= n, "frame capacity")
    require(all(type(v) is int and 0 < v < 1 << n for v in vectors), "frame vector")
    require(binary_rank(vectors) == len(vectors), "independent frame vectors")
    if len(vectors) == n:
        return identity(n) + tuple((1 << i) | (1 << (n + i)) for i in range(n))
    extended = list(vectors)
    for vector in identity(n):
        if vector not in span(extended):
            extended.append(vector)
    require(len(extended) == n, "extended basis")
    # Invert the basis by exhaustive lookup, not the predecessor's row reduction.
    preimage = {image(extended, v): v for v in range(1 << n)}
    require(len(preimage) == 1 << n, "invertible basis")
    inverse = tuple(preimage[1 << i] for i in range(n))
    result = identity(2 * n)
    for i, a in enumerate(extended[: len(vectors)]):
        dual = sum(((column >> i) & 1) << j for j, column in enumerate(inverse))
        v = a | ((a ^ dual) << n)
        generators = []
        for j in range(2 * n):
            pairing = (v >> (j + n if j < n else j - n)) & 1
            generators.append((1 << j) ^ (v if pairing else 0))
        result = multiply(tuple(generators), result)
    require(multiply(result, result) == identity(2 * n), "binary frame involution")
    return result


def mixing_rank(matrix, n=N):
    return binary_rank(tuple(column & ((1 << n) - 1) for column in matrix[n:]))


def endpoint_runs(word):
    program = word["program"]
    require(type(program) is list and len(program) == 5398, "source event count")
    sequences = {group + str(i): [] for group in "XY" for i in range(104)}
    for index, event in enumerate(program):
        require(type(event) is list and 3 <= len(event) <= 5, "event schema")
        require(event[0] in {"transport", "sign", "add", "zero", "erase"}, "event tag")
        if event[0] == "sign":
            require(event[2] == "-1", "scalar sign only")
        operands = event[1:3] if event[0] == "add" else event[1:2]
        for role in operands:
            require(type(role) is str and len(role) <= 4, "role schema")
            if role in sequences:
                sequences[role].append(index)
    runs = []
    for role, sequence in sequences.items():
        for side, order in (("entry", sequence), ("exit", list(reversed(sequence)))):
            runs.append(analyze_run(word, role, side, order))
    return runs


def analyze_run(word, role, side, order):
    program = word["program"]
    transports = []
    barrier = None
    for index in order:
        event = program[index]
        if event[0] == "transport":
            transports.append(index)
        elif event[0] != "sign":
            barrier = index
            break
    require(barrier is not None and len(transports) in (1, 2), "bounded endpoint run")
    ids = sorted(transports)
    edges = [program[i] for i in ids]
    for left, right in pairwise(edges):
        require(left[3] == right[2], "run frame continuity")
    endpoint = program[transports[0]]
    boundary = word["initial_frames" if side == "entry" else "final_frames"][role]
    require(endpoint[2 if side == "entry" else 3] == boundary, "boundary frame")
    require(type(endpoint[4]) is int and endpoint[4] == 1, "endpoint H1")
    # The binary canonical frame is an involution, even though its
    # phased complex operator need not be. No phase claim is made.
    operator = multiply(frame(tuple(edges[-1][3])), frame(tuple(edges[0][2])))
    rank = mixing_rank(operator)
    paid = 0
    for edge in edges:
        require(type(edge[4]) is int and 1 <= edge[4] <= N, "child rank schema")
        require(
            mixing_rank(multiply(frame(tuple(edge[3])), frame(tuple(edge[2]))))
            == edge[4],
            "individual child rank",
        )
        paid += edge[4]
    require(rank == paid, "run lower bound attained")
    return {"role": role, "side": side, "events": ids, "barrier": barrier, "rank": rank}


def verify():
    authenticate()
    runs = endpoint_runs(read_json(PACKAGE / "inputs/PR2586-WORD.json"))
    histogram = Counter(run["rank"] for run in runs)
    used = [index for run in runs for index in run["events"]]
    require(len(used) == len(set(used)), "disjoint endpoint runs")
    require(
        histogram == {1: 288, 3: 16, 4: 28, 5: 39, 6: 30, 7: 15}, "complete rank census"
    )
    require(
        len(runs) == 416 and sum(run["rank"] for run in runs) == 928,
        "endpoint rank mass",
    )
    return {
        "schema_version": 1,
        "runs": runs,
        "rank_mass": 928,
        "histogram": {str(k): v for k, v in sorted(histogram.items())},
        "scope": "Binary lower bound only; no phase or physical correctness claim",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    result = verify()
    if args.out:
        with args.out.open("x", encoding="utf-8") as stream:
            json.dump(result, stream, sort_keys=True, indent=2)
            stream.write("\n")
    else:
        expected = read_json(PACKAGE / "RESULT.json")
        require(
            json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True),
            "typed receipt",
        )
    print(
        "PASS_P104_ENDPOINT_RANK runs=416 rank_mass=928 no_native_imports no_new_kappa"
    )


if __name__ == "__main__":
    main()
