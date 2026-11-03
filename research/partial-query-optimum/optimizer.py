"""Exact additive partial-query acquisition at binary codimension at most four."""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def integer(value: object, lower: int, upper: int) -> int:
    require(type(value) is int and lower <= value <= upper, "integer out of range")
    return value


def reducer(vectors: list[int] | tuple[int, ...]) -> dict[int, tuple[int, int]]:
    """Keep triangular rows and their expressions in the supplied vectors."""
    rows: dict[int, tuple[int, int]] = {}
    for index, vector in enumerate(vectors):
        residue, expression = reduce_vector(vector, rows)
        if residue:
            rows[residue.bit_length() - 1] = (residue, expression ^ (1 << index))
    return rows


def reduce_vector(vector: int, rows: dict[int, tuple[int, int]]) -> tuple[int, int]:
    expression = 0
    for pivot in sorted(rows, reverse=True):
        if vector & (1 << pivot):
            row, coordinates = rows[pivot]
            vector ^= row
            expression ^= coordinates
    return vector, expression


def canonical(vectors: list[int] | tuple[int, ...]) -> tuple[int, ...]:
    rows = reducer(vectors)
    pivots = sorted(rows)
    values = {pivot: rows[pivot][0] for pivot in pivots}
    for pivot in pivots:
        for later in pivots:
            if later > pivot and values[later] & (1 << pivot):
                values[later] ^= values[pivot]
    return tuple(values[pivot] for pivot in reversed(pivots))


def duals_and_remainders(basis: list[int], width: int) -> tuple[list[int], list[int]]:
    rows = reducer(basis)
    require(len(rows) == len(basis), "dependent basis")
    duals = [0] * len(basis)
    remainders = []
    for bit in range(width):
        residue, coordinates = reduce_vector(1 << bit, rows)
        remainders.append(residue)
        for index in range(len(basis)):
            if coordinates & (1 << index):
                duals[index] |= 1 << bit
    return duals, remainders


def dot(left: int, right: int) -> int:
    return (left & right).bit_count() & 1


def image(vector: int, forms: list[int]) -> int:
    return sum(dot(vector, form) << index for index, form in enumerate(forms))


def reconstruct(mask: int, basis: list[int]) -> int:
    result = 0
    for index, vector in enumerate(basis):
        if mask & (1 << index):
            result ^= vector
    return result


def parse_problem(problem: object) -> tuple[int, list[int], list[int], list[int], int]:
    require(type(problem) is dict, "problem must be an object")
    require(set(problem) == {"width", "vectors", "costs", "targets"}, "problem keys")
    width = integer(problem["width"], 1, 256)
    vectors, costs, targets = (problem[key] for key in ("vectors", "costs", "targets"))
    require(type(vectors) is list and len(vectors) <= 4096, "query count")
    require(type(costs) is list and len(costs) == len(vectors), "cost count")
    require(type(targets) is list and len(targets) <= 256, "target count")
    for vector in vectors + targets:
        integer(vector, 0, (1 << width) - 1)
    for cost in costs:
        integer(cost, 0, 10**12)
    query_rows, target_rows = reducer(vectors), reducer(targets)
    require(all(reduce_vector(target, query_rows)[0] == 0 for target in targets),
            "target outside query span")
    codimension = len(query_rows) - len(target_rows)
    require(codimension <= 4, "codimension exceeds four")
    return width, vectors, costs, targets, codimension


def subspaces_by_extension(dimension: int) -> list[int]:
    """Enumerate spans by strict rank extension, at most 67 spaces."""
    layers: list[set[tuple[int, ...]]] = [{()}]
    for rank in range(dimension):
        following = set()
        for basis in layers[rank]:
            rows = reducer(basis)
            for vector in range(1, 1 << dimension):
                if reduce_vector(vector, rows)[0]:
                    following.add(canonical(list(basis) + [vector]))
        layers.append(following)
    spaces = []
    for layer in layers:
        for basis in layer:
            spaces.append(sum(1 << reconstruct(mask, list(basis))
                              for mask in range(1 << len(basis))))
    return sorted(spaces)


def subspaces_by_rref(dimension: int) -> list[int]:
    """Separate complete enumerator for the certificate checker."""
    spaces = []
    for rank in range(dimension + 1):
        for pivots in combinations(range(dimension), rank):
            cells = [(row, column) for row, pivot in enumerate(pivots)
                     for column in range(pivot + 1, dimension) if column not in pivots]
            for assignment in range(1 << len(cells)):
                basis = [1 << pivot for pivot in pivots]
                for bit, (row, column) in enumerate(cells):
                    if assignment & (1 << bit):
                        basis[row] |= 1 << column
                spaces.append(sum(1 << reconstruct(mask, basis)
                                  for mask in range(1 << rank)))
    require(len(spaces) == len(set(spaces)), "duplicate RREF spaces")
    return sorted(spaces)


def quotient_forms(vectors: list[int], targets: list[int], width: int) -> list[int]:
    basis = list(canonical(targets))
    target_rank = len(basis)
    rows = reducer(basis)
    for vector in vectors:
        if reduce_vector(vector, rows)[0]:
            basis.append(vector)
            rows = reducer(basis)
    duals, _ = duals_and_remainders(basis, width)
    return duals[target_rank:]


def candidate(vectors: list[int], costs: list[int], targets: list[int],
              eligible: list[int], width: int) -> dict:
    selected = []
    rows: dict[int, tuple[int, int]] = {}
    for index in sorted(eligible, key=lambda index: (costs[index], index)):
        residue, _ = reduce_vector(vectors[index], rows)
        if residue:
            selected.append(index)
            rows[residue.bit_length() - 1] = (residue, 0)
    basis = [vectors[index] for index in selected]
    duals, remainders = duals_and_remainders(basis, width)
    result = {"selected": selected, "duals": duals, "missing_target": None,
              "separator": None}
    for index, target in enumerate(targets):
        residue, _ = reduce_vector(target, reducer(basis))
        if residue:
            bit = residue.bit_length() - 1
            result["missing_target"] = index
            result["separator"] = sum(1 << position for position in range(width)
                                      if remainders[position] & (1 << bit))
            break
    return result


def solve(problem: dict) -> dict:
    width, vectors, costs, targets, codimension = parse_problem(problem)
    forms = quotient_forms(vectors, targets, width)
    images = [image(vector, forms) for vector in vectors]
    entries = []
    for space in subspaces_by_extension(codimension):
        eligible = [index for index, value in enumerate(images) if space & (1 << value)]
        entry = candidate(vectors, costs, targets, eligible, width)
        entries.append({"space": space, **entry})
    winners = [(sum(costs[index] for index in entry["selected"]), entry["space"])
               for entry in entries if entry["missing_target"] is None]
    require(bool(winners), "full quotient must be feasible")
    cost, winner = min(winners)
    return {"schema": "partial-query-optimum/v1", "quotient_forms": forms,
            "entries": entries, "cost": cost, "winner": winner}


def check_entry(entry: object, space: int, vectors: list[int], costs: list[int],
                targets: list[int], forms: list[int], width: int) -> int | None:
    require(type(entry) is dict and set(entry) ==
            {"space", "selected", "duals", "missing_target", "separator"}, "entry keys")
    require(integer(entry["space"], 1, (1 << (1 << len(forms))) - 1) == space,
            "wrong or missing quotient space")
    selected, duals = entry["selected"], entry["duals"]
    require(type(selected) is list and len(selected) <= width, "selected count")
    for index in selected:
        integer(index, 0, len(vectors) - 1)
    require(len(set(selected)) == len(selected), "duplicate selection")
    require(type(duals) is list and len(duals) == len(selected), "dual count")
    for form in duals:
        integer(form, 0, (1 << width) - 1)
    eligible = [index for index, vector in enumerate(vectors)
                if space & (1 << image(vector, forms))]
    eligible_set = set(eligible)
    require(all(index in eligible_set for index in selected), "ineligible selection")
    basis = [vectors[index] for index in selected]
    for row, form in enumerate(duals):
        require(all(dot(form, vector) == (row == column)
                    for column, vector in enumerate(basis)), "bad independence dual")
    for index in eligible:
        coordinates = image(vectors[index], duals)
        require(reconstruct(coordinates, basis) == vectors[index], "basis misses eligible query")
        require(all(not coordinates & (1 << position) or costs[index] >= costs[chosen]
                    for position, chosen in enumerate(selected)), "improving basis exchange")
    if entry["missing_target"] is not None:
        missing = integer(entry["missing_target"], 0, len(targets) - 1)
        separator = integer(entry["separator"], 1, (1 << width) - 1)
        require(dot(separator, targets[missing]) == 1 and
                all(dot(separator, vectors[index]) == 0 for index in eligible),
                "invalid infeasibility separator")
        return None
    require(entry["separator"] is None, "unexpected separator")
    require(all(reconstruct(image(target, duals), basis) == target for target in targets),
            "target not acquired")
    return sum(costs[index] for index in selected)


def check(problem: dict, certificate: object) -> int:
    width, vectors, costs, targets, codimension = parse_problem(problem)
    require(type(certificate) is dict and set(certificate) ==
            {"schema", "quotient_forms", "entries", "cost", "winner"}, "certificate keys")
    require(certificate["schema"] == "partial-query-optimum/v1", "certificate schema")
    forms = certificate["quotient_forms"]
    require(type(forms) is list and len(forms) == codimension, "quotient dimension")
    for form in forms:
        integer(form, 0, (1 << width) - 1)
    require(all(image(target, forms) == 0 for target in targets), "quotient moves target")
    require(len(reducer([image(vector, forms) for vector in vectors])) == codimension,
            "quotient not surjective")
    spaces = subspaces_by_rref(codimension)
    entries = certificate["entries"]
    require(type(entries) is list and len(entries) == len(spaces), "incomplete superspace list")
    attainable = []
    for space, entry in zip(spaces, entries, strict=True):
        cost = check_entry(entry, space, vectors, costs, targets, forms, width)
        if cost is not None:
            attainable.append((cost, space))
    require(bool(attainable), "no feasible candidate")
    cost = integer(certificate["cost"], 0, width * 10**12)
    winner = integer(certificate["winner"], 1, (1 << (1 << codimension)) - 1)
    require((cost, winner) == min(attainable), "nonoptimal reported winner")
    return cost


def read_json(path: Path) -> object:
    require(path.stat().st_size <= 8_000_000, "JSON file exceeds eight MB")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("problem", type=Path)
    parser.add_argument("--check", type=Path)
    arguments = parser.parse_args()
    problem = read_json(arguments.problem)
    certificate = read_json(arguments.check) if arguments.check else solve(problem)
    cost = check(problem, certificate)
    print(json.dumps({"status": "PASS_PARTIAL_QUERY_CERTIFICATE", "cost": cost}
                     if arguments.check else certificate, sort_keys=True))


if __name__ == "__main__":
    main()
