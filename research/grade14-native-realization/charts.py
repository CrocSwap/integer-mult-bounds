"""Bind exact Clifford factors and lower them to complete column operations."""

from functools import cache
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ENGINE = HERE.parent / "shared-wire-split-composition" / "frozen"
sys.path.insert(0, str(ENGINE))
import native_verify as check_clifford


def require(test, label):
    if not test:
        raise ValueError(label)


def packed(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def encode(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def linear_records(matrix):
    width = len(matrix)
    rows = list(matrix)
    operations = []
    for j in range(width):
        pivot = next((k for k in range(j, width) if rows[k] >> j & 1), None)
        require(pivot is not None, "singular address change")
        if pivot != j:
            rows[j], rows[pivot] = rows[pivot], rows[j]
            operations.extend((("ROW", j, pivot), ("ROW", pivot, j), ("ROW", j, pivot)))
        for k in range(width):
            if k != j and rows[k] >> j & 1:
                rows[k] ^= rows[j]
                operations.append(("ROW", k, j))
    require(rows == [1 << j for j in range(width)], "address reduction")
    return list(reversed(operations))


def monomial_records(record):
    matrix = record["matrix_rows"]
    quadratic = record["quadratic_rows"]
    phase = record["linear_Z4"]
    records = [("S", i, c) for i, c in enumerate(phase) if c]
    records.extend(
        ("CZ", i, j)
        for i, row in enumerate(quadratic)
        for j in range(i + 1, len(matrix))
        if row >> j & 1
    )
    records.extend(linear_records(matrix))
    records.extend(("NOT", j) for j in range(len(matrix)) if record["offset"] >> j & 1)
    if record["phase"]:
        records.append(("I", record["phase"]))
    return records


def action(records, axes, width):
    """Use bit j of each axis for column j. Higher axes are spectators."""
    mask = (1 << width) - 1
    axes = list(axes)
    phase = 0
    for op, *args in records:
        j = args[0]
        if op == "ROW":
            axes[j] ^= axes[args[1]]
        elif op == "NOT":
            axes[j] ^= mask
        elif op == "S":
            phase += args[1] * axes[j].bit_count()
        elif op == "CZ":
            phase += 2 * (axes[j] & axes[args[1]]).bit_count()
        else:
            require(op == "I", "monomial opcode")
            phase += width * j
    return tuple(axes), phase % 4


def native_catalogue(graph, layout, stored=None):
    """Generate every native factor, or verify a stored set with a separate engine."""
    generate = stored is None
    if generate:
        import clifford_exact as producer

    frames = graph["frames"]
    require(frames == layout["frames"], "literal frame table")

    @cache
    def frame(i):
        return check_clifford.frame(tuple(frames[i]), 9)

    @cache
    def make_frame(i):
        return producer.canonical_frame(9, tuple(frames[i]))

    xports = layout["live"]
    hosted = layout["hosted"]
    shadow = dict(
        zip(hosted["Dports"], zip(hosted["X2"], hosted["Y2"], strict=True), strict=True)
    )
    mains = (
        set(xports) | {x + 112 for x in xports} | set(hosted["X2"]) | set(hosted["Y2"])
    )
    require(
        len(mains) == 400 and len(shadow) == 96, "disjoint primary and hosted owners"
    )
    start, end = graph["initial"], graph["final"]
    pairs = {(a, b) for _, a, b in graph["moves"]}
    pairs.update(
        (a, b)
        for i, (a, b) in enumerate(zip(start, end, strict=True))
        if i not in mains
    )
    existing = {} if generate else {(a, b): rec for a, b, rec in stored["pairs"]}
    if not generate:
        require(
            len(stored["pairs"]) == len(existing) and set(existing) == pairs,
            "exact edge coverage",
        )

    attached = []
    for a, b in sorted(pairs):
        rec = (
            producer.lower_child(make_frame(a).adjoint().then(make_frame(b)))[0]
            if generate
            else existing[a, b]
        )
        require(
            rec["rank"] == abs(len(frames[a]) - len(frames[b])) > 0, "paid child grade"
        )
        check_clifford.equal(
            check_clifford.recipe(rec),
            check_clifford.adjoint(frame(a)) + frame(b),
            "complete interface and absolute phase",
        )
        attached.append([a, b, rec])
    ports = []
    for i, (x, q) in enumerate(zip(xports, layout["ports"], strict=True)):
        y = x + 112
        require(frames[start[y]] == [], "identity at Y ingress")
        check_clifford.equal(frame(end[x]), check_clifford.fourier(9), "full X egress")
        if generate:
            left = producer.cgate(9, q, -1).then(make_frame(start[x]))
            right = (
                make_frame(end[y])
                .adjoint()
                .then(producer.cgate(9, q, -1))
                .then(producer.fourier(9))
            )
            records = [producer.lower_child(op)[0] for op in (left, right)]
            require(
                all(rec["rank"] == 0 for rec in records), "uncharged positive port job"
            )
            ingress, egress = [rec["left"] for rec in records]
        else:
            label, ingress, egress = stored["ports"][i]
            require(label == q, "port label")
        check_clifford.equal(
            check_clifford.monomial(ingress),
            (("C", q, -1),) + frame(start[x]),
            "physical ingress",
        )
        check_clifford.equal(
            check_clifford.monomial(egress),
            check_clifford.adjoint(frame(end[y]))
            + (("C", q, -1),)
            + check_clifford.fourier(9),
            "physical egress",
        )
        if i in shadow:
            u, v = shadow[i]
            require(
                all(tags[x] == tags[u] and tags[y] == tags[v] for tags in (start, end)),
                "second shear port",
            )
        ports.append([q, ingress, egress])
    answer = dict(pairs=attached, ports=ports)
    if not generate:
        require(answer == stored, "no surplus or reordered catalogue")
    return answer


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", type=Path)
    mode.add_argument("--check-build", action="store_true")
    args = parser.parse_args()
    source = HERE / "retained/data"
    data = native_catalogue(
        packed(source / "complex.json.gz"), packed(source / "layout.json.gz")
    )
    blob = encode(data)
    if args.check_build:
        require(
            blob == gzip.decompress((HERE / "complex-atlas.json.gz").read_bytes()),
            "regenerated full catalogue",
        )
    else:
        args.build.write_bytes(gzip.compress(blob, mtime=0))
    print("PASS_NATIVE_ATLAS_BUILD", sha256(blob).hexdigest())
