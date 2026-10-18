"""Full finite replay and semantic controls, active under python -O.

The census supports the written reduction, not a proof-assistant claim.
Mason Hale, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from itertools import combinations
import argparse
import json
from pathlib import Path
import random
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from census import census, interval_differences, mandatory, partitions
from program import star


def require(condition, message):
    if not condition:
        raise ValueError(message)


def formal(program):
    """Opaque h_j=B_j(x_j) and initial dirty-root symbols; separate A rows."""
    n, k = program["sources"], program["roots"]
    roots = [1 << i for i in range(k)]
    outputs = [0] * (1 << n)
    for kind, label, port in program["operations"]:
        require(type(port) is int and 0 <= port < k, "bad port")
        if kind == "X":
            require(type(label) is int and 0 <= label < k and label != port, "bad shear")
            roots[label] ^= roots[port]
        elif kind == "B":
            require(type(label) is int and 0 <= label < n, "bad source")
            roots[port] ^= 1 << (k + label)
        elif kind == "A":
            require(type(label) is int and 0 < label < 1 << n, "bad target")
            outputs[label] ^= roots[port]
        else:
            raise ValueError("unknown operation")
    require(roots == [1 << i for i in range(k)], "dirty roots do not restore")
    require(outputs == [m << k for m in range(1 << n)], "wrong output or uncancelled dirt")


def apply_matrix(matrix, vector):
    answer = []
    for mask in matrix:
        value = 0
        for i, x in enumerate(vector):
            if mask >> i & 1:
                value ^= x
        answer.append(value)
    return answer


def dense(program, widths, seed, reverse=False):
    """All input columns at once, concrete rectangular/singular binary maps."""
    n, k = program["sources"], program["roots"]
    sx, sz, sy = widths
    rng = random.Random(seed)
    b = [[rng.randrange(1 << sx) for _ in range(sz)] for _ in range(n)]
    a = [[rng.randrange(1 << sz) for _ in range(sy)] for _ in range((1 << n) - 1)]
    b[0] = [0] * sz
    a[0] = [0] * sy
    offset = 0

    def row(size):
        nonlocal offset
        result = [1 << i for i in range(offset, offset + size)]
        offset += size
        return result

    x = [row(sx) for _ in range(n)]
    z = [row(sz) for _ in range(k)]
    y = [row(sy) for _ in range((1 << n) - 1)]
    before_z, before_y = [r[:] for r in z], [r[:] for r in y]
    ops = program["operations"][::-1] if reverse else program["operations"]
    for kind, label, port in ops:
        if kind == "X":
            z[label] = [u ^ v for u, v in zip(z[label], z[port])]
        elif kind == "B":
            z[port] = [u ^ v for u, v in zip(z[port], apply_matrix(b[label], x[label]))]
        else:
            y[label - 1] = [u ^ v for u, v in zip(y[label - 1], apply_matrix(a[label - 1], z[port]))]
    expected = []
    for mask in range(1, 1 << n):
        total = [0] * sz
        for j in range(n):
            if mask >> j & 1:
                total = [u ^ v for u, v in zip(total, apply_matrix(b[j], x[j]))]
        expected.append([u ^ v for u, v in zip(before_y[mask - 1], apply_matrix(a[mask - 1], total))])
    require(z == before_z and y == expected, "dense dirty-basis replay failed")
    return offset


def controls(program):
    rejected = 0

    def reject(operations):
        nonlocal rejected
        try:
            formal({**program, "operations": operations})
        except ValueError:
            rejected += 1
        else:
            raise ValueError("mutation escaped")

    ops = program["operations"]
    for i in range(len(ops)):
        reject(ops[:i] + ops[i + 1:])
    for kind in ("A", "B", "X"):
        i = next(j for j, op in enumerate(ops) if op[0] == kind)
        bad = [x[:] for x in ops]
        if kind == "X":
            bad[i][1], bad[i][2] = bad[i][2], bad[i][1]
        else:
            bad[i][2] = (bad[i][2] + 1) % program["roots"]
        reject(bad)
    i = next(i for i, op in enumerate(ops) if op[0] == "A")
    bad = [x[:] for x in ops]
    bad[i][1] = 2 if bad[i][1] == 1 else 1
    reject(bad)
    reject([["X", 0, 0], *ops])
    formal({**program, "operations": [["X", 0, 1], ["X", 0, 1], *ops]})
    # Three B calls can restore in a multi-root excursion. The theorem must
    # not import the one-root even-incidence rule.
    z = [1, 2]
    for kind, p in (("B", 0), ("B", 1), ("X", 0), ("B", 1), ("X", 0)):
        z[p] ^= 4 if kind == "B" else z[1]
    require(z == [1, 2], "odd-incidence positive control failed")
    return rejected


def geometric_controls():
    checked = 0
    for full in range(1, 8):
        plane = [v for v in range(1, 8) if (v & full).bit_count() % 2]
        require(len(plane) == 4, "wrong affine plane")
        for size in (3, 4):
            for axes in combinations(plane, size):
                for r in range(1, 8):
                    response = [(r & v).bit_count() % 2 for v in axes]
                    require(sum(response) < 3 or all(response), "rainbow lemma false")
                    checked += 1
    for blocks in partitions(7):
        expected = sum(1 << m for m in range(128) if sum(bool(m & b) for b in blocks) >= 3)
        require(mandatory(blocks) == expected, "mandatory mask engine mismatch")
    # This necessary condition must admit the known six-source/three-root case.
    word = (0, 1, 0, 1, 4, 5, 2, 3, 2, 3, 4, 5)
    blocks = (15, 16, 32)
    require(mandatory(blocks) & ~interval_differences(word) == 0, "six-source control excluded")
    return checked


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native-result", type=Path)
    args = ap.parse_args()
    result = census()
    require(result["words"] == 135135 and result["partitions"] == 651,
            "enumeration cardinality mismatch")
    require(result["cases"] == 87972885, "case count mismatch")
    for entry in result["groups"].values():
        require(0 not in entry["missing_histogram"], "three-root candidate survives")
        require(sum(entry["missing_histogram"].values()) == 135135 * entry["partitions"],
                "incomplete group coverage")
    canonical = json.loads(json.dumps(result))
    require(canonical == json.loads((HERE / "CENSUS.json").read_text()), "census receipt mismatch")
    if args.native_result:
        require(canonical == json.loads(args.native_result.read_text()), "C++/Python census disagreement")
    program = json.loads((HERE / "WITNESS.json").read_text())
    require(program == star(7), "literal witness differs from credited star construction")
    formal(program)
    formal({**program, "operations": program["operations"][::-1]})
    formal(star(6))
    counts = Counter(op[0] for op in program["operations"])
    require(counts == {"B": 14, "A": 254, "X": 56}, "invoice mismatch")
    require(Counter(op[1] for op in program["operations"] if op[0] == "B") == dict.fromkeys(range(7), 2),
            "source multiplicity mismatch")
    require(Counter(op[1] for op in program["operations"] if op[0] == "A") == dict.fromkeys(range(1, 128), 2),
            "output multiplicity mismatch")
    require(Counter(op[2] for op in program["operations"] if op[0] == "X") == {1: 32, 2: 16, 3: 8},
            "directional transfer invoice mismatch")
    columns = sum(dense(program, shape, seed, reverse)
                  for shape in ((2, 3, 2), (3, 2, 1), (3, 4, 2))
                  for seed in (54, 55, 56) for reverse in (False, True))
    rejected = controls(program)
    geometry = geometric_controls()
    print(f"PASS_SEVEN_SOURCE_ROOT_MINIMUM words=135135 partitions=651 cases=87972885 "
          f"roots=4 B=14 A=254 X=56 dense_columns={columns} mutations={rejected} affine_checks={geometry}")


if __name__ == "__main__":
    main()
