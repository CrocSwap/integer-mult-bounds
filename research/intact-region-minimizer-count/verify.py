"""Enumerate all minimizers of the cited intact-region elimination certificate.

produced by Nick Petalas. Apache-2.0.
"""
import argparse
import gzip
from hashlib import sha256
from io import BytesIO
from itertools import product
import json
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = "research/global-intact-region-optimum/WITNESSES.json.gz"
MAX_VARIABLES = 203
MAX_SEPARATOR = 3


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_witness():
    pins = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    row = next(row for row in pins["files"] if row["path"] == SOURCE)
    data = (ROOT / SOURCE).read_bytes()
    require(len(data) <= 1_000_000, "compressed input budget")
    require(sha256(data).hexdigest() == row["sha256"], "witness source hash")
    with gzip.GzipFile(fileobj=BytesIO(data)) as stream:
        raw = stream.read(1_000_001)
    require(len(raw) <= 1_000_000, "expanded input budget")
    witness = json.loads(raw)
    require(set(witness) == {"forward", "backward"}, "two orientations")
    return witness, sha256(data).hexdigest()


def relations(trace):
    """Keep both choices exactly when their certified histograms coincide."""
    require(1 <= len(trace) <= MAX_VARIABLES, "variable budget")
    nodes = [step["node"] for step in trace]
    require(all(type(node) is int for node in nodes), "integer region IDs")
    require(len(set(nodes)) == len(nodes), "distinct elimination nodes")
    position = {node: index for index, node in enumerate(nodes)}
    factors = []
    for index, step in enumerate(trace):
        node, separator = step["node"], tuple(step["separator"])
        require(len(separator) <= MAX_SEPARATOR, "separator budget")
        require(len(set(separator)) == len(separator), "distinct separator IDs")
        require(all(n in position and position[n] > index for n in separator),
                "separator follows eliminated variable")
        states = step["states"]
        expected = set(product((0, 1), repeat=len(separator)))
        require(len(states) == len(expected), "complete state table")
        require({tuple(s["bits"]) for s in states} == expected, "state coverage")
        table = {}
        for state in states:
            left, right = state["candidates"]
            choice, certificate = state["choice"], state["certificate"]
            if choice is None:
                require(left is None and right is None, "infeasible state")
                allowed = ()
            elif left is not None and left == right:
                require(choice in (0, 1) and certificate == "equal", "equal branch")
                allowed = (0, 1)
            else:
                require(type(choice) is int and choice in (0, 1), "chosen bit")
                require((left, right)[choice] is not None, "feasible chosen bit")
                require(certificate != "equal", "strict comparison is not a tie")
                allowed = (choice,)
            for bit in (0, 1):
                table[(bit,) + tuple(state["bits"])] = int(bit in allowed)
        factors.append(((node,) + separator, table))
    return nodes, factors


def count_assignments(nodes, factors, fixed=None):
    """Exact sum-product elimination on Boolean relations, without recursion."""
    require(len(nodes) <= MAX_VARIABLES, "count variable budget")
    factors = [(scope, dict(table)) for scope, table in factors]
    for node, bit in (fixed or {}).items():
        require(node in nodes and bit in (0, 1), "fixed-bit domain")
        factors.append(((node,), {(0,): int(bit == 0), (1,): int(bit == 1)}))
    for node in nodes:
        bucket = [factor for factor in factors if node in factor[0]]
        factors = [factor for factor in factors if node not in factor[0]]
        require(bool(bucket), "each counted variable has a factor")
        separator = tuple(sorted(set().union(*(set(s) for s, _ in bucket)) - {node}))
        require(len(separator) <= MAX_SEPARATOR, "count separator budget")
        table = {}
        for bits in product((0, 1), repeat=len(separator)):
            assignment, total = dict(zip(separator, bits)), 0
            for bit in (0, 1):
                assignment[node] = bit
                total += prod(t[tuple(assignment[n] for n in s)] for s, t in bucket)
            table[bits] = total
        factors.append((separator, table))
    require(all(not scope for scope, _ in factors), "all variables eliminated")
    return prod(table[()] for _, table in factors)


def summarize(trace):
    nodes, factors = relations(trace)
    total = count_assignments(nodes, factors)
    require(total > 0, "nonempty minimizing set")
    free, fixed, marginals = [], {}, {}
    for node in sorted(nodes):
        zero = count_assignments(nodes, factors, {node: 0})
        one = count_assignments(nodes, factors, {node: 1})
        require(zero + one == total, "marginal partition")
        marginals[str(node)] = [zero, one]
        if zero and one:
            free.append(node)
        else:
            fixed[str(node)] = int(one > 0)
    # A subset of the Boolean cube with its full cardinality is the whole cube.
    require(total == 1 << len(free), "minimizers form the complete free cube")
    require(all(marginals[str(n)] == [total // 2, total // 2] for n in free),
            "uniform free-bit marginals")
    return {"count": total, "free_regions": free, "fixed_bits": fixed,
            "marginals": marginals, "variables": len(nodes),
            "local_allowed_rows": sum(sum(t.values()) for _, t in factors)}


def controls():
    # Coupling x=y has two solutions, but both marginals vary: it is not a cube.
    equality = [((0, 1), {(a, b): int(a == b) for a, b in product((0, 1), repeat=2)})]
    require(count_assignments([0, 1], equality) == 2, "coupled-pair count")
    for bit in (0, 1):
        require(count_assignments([0, 1], equality, {0: bit}) == 1,
                "coupled-pair marginal")
    coupled_trace = [
        {"node": 0, "separator": [1], "states": [
            {"bits": [0], "candidates": [[0, 1], None], "choice": 0, "certificate": "forced"},
            {"bits": [1], "candidates": [None, [0, 1]], "choice": 1, "certificate": "forced"}]},
        {"node": 1, "separator": [], "states": [
            {"bits": [], "candidates": [[0, 1], [0, 1]], "choice": 0, "certificate": "equal"}]}]
    try:
        summarize(coupled_trace)
    except ValueError as error:
        require("complete free cube" in str(error), "specific noncube rejection")
    else:
        raise ValueError("coupled marginals falsely accepted as cube")
    disconnected = [((n,), {(0,): 1, (1,): 1}) for n in range(3)]
    require(count_assignments([0, 1, 2], disconnected) == 8, "independent product")
    impossible = equality + [((0,), {(0,): 1, (1,): 0}),
                             ((1,), {(0,): 0, (1,): 1})]
    require(count_assignments([0, 1], impossible) == 0, "inconsistent relations")
    # The tie for x exists only at y=1, while the later step forces y=0.
    conditional = [
        {"node": 0, "separator": [1], "states": [
            {"bits": [0], "candidates": [[0, 1], None], "choice": 0, "certificate": "forced"},
            {"bits": [1], "candidates": [[0, 1], [0, 1]], "choice": 0, "certificate": "equal"}]},
        {"node": 1, "separator": [], "states": [
            {"bits": [], "candidates": [[0, 1], None], "choice": 0, "certificate": "forced"}]}]
    require(summarize(conditional)["count"] == 1, "unreachable tie is not freedom")
    malformed = conditional + [conditional[0]]
    try:
        relations(malformed)
    except ValueError:
        pass
    else:
        raise ValueError("duplicate-variable rejection")
    return ["coupled pair", "coupled marginals", "noncube", "independent product",
            "inconsistency", "unreachable tie", "duplicate variable"]


def result():
    witness, digest = read_witness()
    output = {"schema_version": 1, "claim_type": "scoped equality-class proof",
              "source_sha256": digest, "orientations": {}, "controls": controls()}
    for name in ("forward", "backward"):
        output["orientations"][name] = summarize(witness[name]["elimination"])
    require(output["orientations"]["forward"] == output["orientations"]["backward"],
            "same equality cube in both orientations")
    output["artifact_sha256"] = {
        name: sha256((HERE / name).read_bytes()).hexdigest()
        for name in ("verify.py", "independent.py", "README.md")}
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate RESULT.json")
    args = parser.parse_args()
    computed = result()
    path = HERE / "RESULT.json"
    if args.write:
        path.write_text(json.dumps(computed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        require(json.loads(path.read_text(encoding="utf-8")) == computed, "generated receipt")
    values = computed["orientations"]["forward"]
    print("PASS_INTACT_REGION_MINIMIZER_COUNT orientations=2 "
          f"fixed={len(values['fixed_bits'])} free={len(values['free_regions'])} "
          f"count={values['count']} controls={len(computed['controls'])}")


if __name__ == "__main__":
    main()
