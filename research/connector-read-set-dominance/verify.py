"""Exact finite certificate for connector read-set dominance. Apache-2.0."""

from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from search import dominates, emit, explore, insert, problem, require, solution


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def digest(value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode()).hexdigest()


def authenticate():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in sources["files"]:
        if row["usage"] == "input":
            require(sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                    "predecessor input hash mismatch")
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json",
             "VERIFY.json", "search.py", "verify.py")
    return {name: sha256((PACKAGE / name).read_bytes()).hexdigest() for name in names}


def oracle_frontier(best):
    """Postprocess the complete graph; no incremental frontier is reused."""
    result = {}
    for state, cost in best.items():
        redundant = False
        for other, price in best.items():
            if other != state and other[:3] == state[:3] and price <= cost:
                if state[3] & ~other[3] == 0:
                    redundant = True
                    break
        if not redundant:
            result[state] = cost
    return result


def replay(instance, program, reverse=False):
    n = len(instance.colors)
    roots = [{("d", p)} for p in range(2)]
    outputs = {t: {("y", t)} for t in instance.targets}
    operations = list(reversed(program)) if reverse else program
    if reverse:
        for t in instance.targets:
            outputs[t].update(("A", t, "B", j, "x", j)
                              for j in range(n) if t >> j & 1)
    for kind, index in operations:
        if kind == "B":
            require(type(index) is int and 0 <= index < n, "invalid B source")
            roots[0].symmetric_difference_update({("B", index, "x", index)})
        elif kind == "C":
            require(type(index) is int and index in (0, 1), "invalid root shear")
            roots[index].symmetric_difference_update(roots[1-index])
        else:
            require(kind == "A" and index in outputs, "invalid target read")
            outputs[index].symmetric_difference_update(
                {("A", index) + term for term in roots[0]})
    expected = {t: {("y", t)} for t in instance.targets}
    if not reverse:
        for t in instance.targets:
            expected[t].update(("A", t, "B", j, "x", j)
                               for j in range(n) if t >> j & 1)
    require(roots == [{("d", 0)}, {("d", 1)}], "dirty roots not restored")
    require(outputs == expected, "opaque-map output identity failed")


def check_word(instance, program, minima, bill):
    require(tuple(j for kind, j in program if kind == "B") == instance.source,
            "source order changed")
    counts = Counter(t for kind, t in program if kind == "A")
    require(counts == Counter(minima), "read bill is not the individual minimum")
    require(sum(kind == "C" for kind, _ in program) == bill,
            "wrong transfer bill")
    cut, a, b = 0, 1, 2
    for kind, index in program:
        if kind == "C":
            if index == 0:
                a ^= b
            else:
                b ^= a
        elif kind == "B":
            color = instance.colors[index]
            require((a & color).bit_count() % 2 == 1 and
                    (b & color).bit_count() % 2 == 0, "illegal source frame")
            cut += 1
    require((cut, a, b) == (len(instance.source), 1, 2), "wrong final frame")
    replay(instance, program)
    replay(instance, program, reverse=True)


def controls(instance, program):
    tests = []
    bucket = {0b111: 2}
    tests.append(insert(bucket, 0b011, 3) == (False, 0))
    bucket = {0b111: 3}
    tests.append(insert(bucket, 0b011, 2) == (True, 0))
    tests.append(not dominates(0b011, 1, 0b111, 2))
    tests.append(not dominates(0b011, 1, 0b101, 2))
    bucket = {0b011: 3, 0b101: 2}
    tests.append(insert(bucket, 0b111, 2) == (True, 2) and bucket == {0b111: 2})
    changed = list(program)
    del changed[next(i for i, op in enumerate(changed) if op[0] == "A")]
    try:
        replay(instance, changed)
    except ValueError:
        tests.append(True)
    else:
        tests.append(False)
    for thunk in (lambda: explore(instance, 6, True, cap=1),
                  lambda: explore(instance, 25, True),
                  lambda: problem((0, 0), (0,), (1,)),
                  lambda: problem((0, 0), (1,), (0,))):
        try:
            thunk()
        except ValueError:
            tests.append(True)
        else:
            tests.append(False)
    require(all(tests), "a semantic or resource control failed")
    return len(tests)


def main():
    require(len(sys.argv) == 1, "no arguments are supported")
    hashes = authenticate()
    instance = problem((0, 0, 1, 1, 2, 2), (1, 2, 3), tuple(range(1, 8)))
    full = explore(instance, 6, False)
    pruned = explore(instance, 6, True)
    frontier = oracle_frontier(full["best"])
    require(frontier == pruned["active"], "incremental and complete frontiers differ")
    for state, cost in full["best"].items():
        require(any(other[:3] == state[:3] and bill <= cost and
                    state[3] & ~other[3] == 0
                    for other, bill in pruned["active"].items()),
                "unpruned state has no retained dominating state")
    original, reduced = solution(instance, full), solution(instance, pruned)
    require(original is not None and reduced is not None, "no accepting state at six")
    bill, terminal, paths, minima = reduced
    require(original[0] == bill == 6 and sum(minima.values()) == 15,
            "unexpected fixture objective")
    require(solution(instance, explore(instance, 5, True)) is None,
            "a minimum-read solution uses at most five transfers")
    program = emit(instance, pruned, terminal, paths)
    check_word(instance, program, minima, bill)
    count = controls(instance, program)
    require(sum(pruned["expanded"]) < sum(full["expanded"]), "no state reduction")
    full_rows = sorted((*state, cost) for state, cost in full["best"].items())
    retained_rows = sorted((*state, cost) for state, cost in pruned["active"].items())
    receipt = {"status": "PASS_CONNECTOR_READ_SET_DOMINANCE", "files": hashes,
               "source": instance.source, "colors": instance.colors,
               "minimum_reads": minima, "transfers": bill, "program": program,
               "complete_expansions_by_cost": full["expanded"],
               "pruned_expansions_by_cost": pruned["expanded"],
               "complete_states": len(full["best"]),
               "pruned_discovered_states": len(pruned["best"]),
               "retained_states": len(frontier), "dominated_offers": pruned["rejected"],
               "retired_labels": pruned["removed"], "controls": count,
               "complete_graph_sha256": digest(full_rows),
               "retained_frontier_sha256": digest(retained_rows)}
    print(json.dumps({"receipt": receipt, "receipt_sha256": digest(receipt)}, sort_keys=True))


if __name__ == "__main__":
    main()
