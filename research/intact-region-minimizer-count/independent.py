"""Independent domain-propagation certificate for the exact equality cube.

No imports from the primary counter or any predecessor executable.
produced by Nick Petalas. Apache-2.0.
"""
import gzip
from hashlib import sha256
from io import BytesIO
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
INPUT = "research/global-intact-region-optimum/WITNESSES.json.gz"


def check(condition, message):
    if not condition:
        raise ValueError(message)


def load():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    expected = [r["sha256"] for r in manifest["files"] if r["path"] == INPUT]
    blob = (ROOT / INPUT).read_bytes()
    check(len(blob) <= 1_000_000, "compressed budget")
    check(expected == [sha256(blob).hexdigest()], "input authentication")
    with gzip.GzipFile(fileobj=BytesIO(blob)) as stream:
        raw = stream.read(1_000_001)
    check(len(raw) <= 1_000_000, "payload budget")
    return json.loads(raw)


def extract(trace):
    check(len(trace) <= 203, "trace budget")
    constraints = []
    for step in trace:
        scope = (step["node"], *step["separator"])
        check(len(scope) <= 4, "scope budget")
        rows = set()
        for state in step["states"]:
            a, b = state["candidates"]
            selected = state["choice"]
            if selected is None:
                continue
            choices = (0, 1) if a is not None and a == b else (selected,)
            for choice in choices:
                rows.add((choice, *state["bits"]))
        constraints.append((scope, rows))
    return constraints


def cube(constraints):
    variables = {node for scope, _ in constraints for node in scope}
    check(1 <= len(variables) <= 203, "variable budget")
    domains = {node: {0, 1} for node in variables}
    # Each strict change removes a bit. At most 2|variables| removals are possible.
    for iteration in range(2 * len(variables) + 1):
        changed = False
        for scope, rows in constraints:
            compatible = [r for r in rows if all(b in domains[n] for n, b in zip(scope, r))]
            for index, node in enumerate(scope):
                supported = {row[index] for row in compatible}
                new = domains[node] & supported
                check(bool(new), "nonempty domain")
                if new != domains[node]:
                    domains[node], changed = new, True
        if not changed:
            break
    else:
        raise ValueError("propagation budget exhausted")
    # This is the sufficiency certificate, beyond mere arc consistency.
    checked_rows = 0
    for scope, rows in constraints:
        permitted = {r for r in rows if all(b in domains[n] for n, b in zip(scope, r))}
        whole_box = set(product(*(sorted(domains[n]) for n in scope)))
        check(permitted == whole_box, "a residual coupling prevents a free cube")
        checked_rows += len(whole_box)
    return domains, iteration + 1, checked_rows


def controls():
    equality = [((0, 1), {(0, 0), (1, 1)})]
    try:
        cube(equality)
    except ValueError as error:
        check("residual coupling" in str(error), "specific coupling rejection")
    else:
        raise ValueError("coupled marginals falsely accepted as cube")
    independent = [((n,), {(0,), (1,)}) for n in range(3)]
    domains, _, _ = cube(independent)
    check(sum(len(d) == 2 for d in domains.values()) == 3, "independent cube")
    domains, _, _ = cube(equality + [((1,), {(1,)})])
    check(domains == {0: {1}, 1: {1}}, "propagated implication")
    return 3


def main():
    witness = load()
    receipt = json.loads((HERE / "RESULT.json").read_text(encoding="utf-8"))
    for name in ("forward", "backward"):
        domains, passes, rows = cube(extract(witness[name]["elimination"]))
        free = sorted(n for n, d in domains.items() if len(d) == 2)
        fixed = {str(n): next(iter(d)) for n, d in domains.items() if len(d) == 1}
        expected = receipt["orientations"][name]
        check(free == expected["free_regions"] and fixed == expected["fixed_bits"],
              "independent equality-class agreement")
        check(1 << len(free) == expected["count"], "independent exact count")
        print(f"INDEPENDENT {name} passes={passes} local_cube_rows={rows} fixed={len(fixed)} free={len(free)}")
    print(f"PASS_INDEPENDENT_INTACT_REGION_CUBE controls={controls()}")


if __name__ == "__main__":
    main()
