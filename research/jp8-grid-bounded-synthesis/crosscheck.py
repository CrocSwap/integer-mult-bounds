#!/usr/bin/env python3
"""Independent finite-graph checker for the claim in this directory.

This module does not import the synthesis code.  It constructs the entire graph
and uses synchronous Bellman relaxation from BOTH signed goals.  Its potential
is checked at every vertex and edge: zero exactly at the goals, a unit-edge
Lipschitz lower bound, and a descending edge at every other vertex.  Thus the
potential gives both a lower bound for every path and a matching witness.

The CLI accepts CERTIFICATE.json with an ``entries`` list.  A record contains
positive reduced ``numerator``, ``denominator`` in {1,2,4,8,16}, an ``operations``
list, ``end_sign`` in {-1,1}, and ``preparation_steps``.  The operations are
double, halve, add, subtract, negate.  Optional --potentials writes the full
integer distance arrays, ordered by state -bound through +bound; their hashes
are always included in the report.  All arithmetic uses Python integers.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path


class CertificateError(ValueError):
    """A witness or potential fails an independently checked obligation."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CertificateError(message)


def _domain(numerator: int, denominator: int) -> tuple[int, int]:
    _require(type(numerator) is int and 1 <= numerator <= 127,
             "numerator is outside the claimed positive range")
    _require(type(denominator) is int and denominator in (1, 2, 4, 8, 16),
             "denominator is outside the claimed dyadic grid")
    _require(denominator == 1 or numerator % 2 == 1,
             "coefficient is not reduced")
    return numerator * denominator, denominator


def _graph(numerator: int, denominator: int) -> tuple[int, list[tuple[int, ...]]]:
    """Construct all successor indices, independently of a path search."""
    bound, source = _domain(numerator, denominator)
    successors = []
    for state in range(-bound, bound + 1):
        neighbors = {state + source, state - source, 2 * state, -state}
        if state % 2 == 0:
            neighbors.add(state // 2)
        successors.append(tuple(sorted(v + bound for v in neighbors
                                       if -bound <= v <= bound)))
    return bound, successors


def bellman_potential(numerator: int, denominator: int) -> dict:
    """Compute reverse distances by full synchronous relaxation, not BFS."""
    bound, graph = _graph(numerator, denominator)
    vertex_count = len(graph)
    infinity = vertex_count + 1
    distances = [infinity] * vertex_count
    distances[bound - numerator] = distances[bound + numerator] = 0
    rounds = 0
    while True:
        updated = [min(old, 1 + min(distances[j] for j in neighbors))
                   for old, neighbors in zip(distances, graph)]
        if updated == distances:
            break
        distances = updated
        rounds += 1
        _require(rounds <= vertex_count - 1, "relaxation did not converge")
    _require(max(distances) < infinity, "an enumerated state is unreachable")
    validate_potential(numerator, denominator, distances)
    encoded = json.dumps(distances, separators=(",", ":")).encode("ascii")
    return {
        "numerator": numerator,
        "denominator": denominator,
        "bound": bound,
        "vertices": vertex_count,
        "directed_edges": sum(map(len, graph)),
        "relaxation_rounds": rounds,
        "maximum_distance": max(distances),
        "preparation_steps": distances[bound + denominator],
        "potential_sha256": hashlib.sha256(encoded).hexdigest(),
        "distances": distances,
    }


def validate_potential(numerator: int, denominator: int, distances: list[int]) -> None:
    """Check complete Bellman obligations without recomputing the solution.

    Every step can lower the integer potential by at most one; a goal has
    potential zero.  Hence no path is shorter than the start potential.  Every
    non-goal has a successor with potential one smaller, giving attainment and
    proving that no vertex/edge omitted by a partial search is being ignored.
    """
    bound, graph = _graph(numerator, denominator)
    _require(len(distances) == len(graph), "potential does not cover every vertex")
    _require(all(type(value) is int and value >= 0 for value in distances),
             "potential must have nonnegative integer values")
    goals = {bound - numerator, bound + numerator}
    for vertex, neighbors in enumerate(graph):
        value = distances[vertex]
        _require((value == 0) == (vertex in goals),
                 f"incorrect zero set at state {vertex - bound}")
        for successor in neighbors:
            _require(value <= distances[successor] + 1,
                     f"edge lower-bound violation at state {vertex - bound}")
        if vertex not in goals:
            _require(any(value == distances[j] + 1 for j in neighbors),
                     f"no descending witness at state {vertex - bound}")


def replay_operations(numerator: int, denominator: int, operations: list[str],
                      end_sign: int) -> list[int]:
    """Replay submitted primitive names with a separate explicit interpreter."""
    bound, state = _domain(numerator, denominator)
    _require(type(end_sign) is int and end_sign in (-1, 1), "invalid end sign")
    _require(isinstance(operations, list), "operations must be a list")
    states = [state]
    for position, operation in enumerate(operations):
        if operation == "double":
            state *= 2
        elif operation == "halve":
            _require(state % 2 == 0, f"off-grid halving at operation {position}")
            state //= 2
        elif operation == "add":
            state += denominator
        elif operation == "subtract":
            state -= denominator
        elif operation == "negate":
            state = -state
        else:
            raise CertificateError(f"unknown operation {operation!r}")
        _require(-bound <= state <= bound,
                 f"magnitude bound exceeded at operation {position}")
        states.append(state)
    _require(state == end_sign * numerator, "witness does not reach its stated goal")
    return states


def _descending_witness(numerator: int, denominator: int,
                        distances: list[int]) -> list[int]:
    bound, graph = _graph(numerator, denominator)
    position = bound + denominator
    path = [denominator]
    while distances[position]:
        position = next(j for j in graph[position]
                        if distances[j] + 1 == distances[position])
        path.append(position - bound)
    _require(abs(path[-1]) == numerator, "independent witness missed both goals")
    return path


def verify_entry(entry: dict, *, include_distances: bool = False) -> dict:
    """Verify one submitted path and its exact shortest preparation length."""
    numerator = entry["numerator"]
    denominator = entry["denominator"]
    _domain(numerator, denominator)
    steps = entry["preparation_steps"]
    _require(type(steps) is int and steps >= 0, "invalid preparation step count")
    states = replay_operations(numerator, denominator, entry["operations"],
                               entry["end_sign"])
    _require(len(states) - 1 == steps, "forged preparation step count")
    result = bellman_potential(numerator, denominator)
    _require(result["preparation_steps"] == steps,
             f"submitted length {steps} is not the exact optimum "
             f"{result['preparation_steps']}")
    if "distance_potential" in entry:
        validate_potential(numerator, denominator, entry["distance_potential"])
        _require(entry["distance_potential"] == result["distances"],
                 "submitted potential differs from independent solution")
    result["submitted_states"] = states
    result["independent_states"] = _descending_witness(
        numerator, denominator, result["distances"])
    # An arbitrary incoming scratch value still has to be cleared for a unit
    # addition, even though that branch does not copy or prepare the source.
    result["macro_cost"] = 2 if numerator == denominator == 1 else steps + 3
    result["verified"] = True
    if not include_distances:
        del result["distances"]
    return result


def negative_controls() -> dict:
    """Ensure four distinct false claims are rejected by the checker."""
    valid = {"numerator": 3, "denominator": 2,
             "operations": ["halve", "add"],
             "end_sign": 1, "preparation_steps": 2}
    verify_entry(valid)
    controls = {}

    def rejection(name, operation):
        try:
            operation()
        except CertificateError as error:
            controls[name] = {"rejected": True, "reason": str(error)}
        else:
            raise CertificateError(f"negative control accepted: {name}")

    forged_optimum = copy.deepcopy(valid)
    forged_optimum["operations"] += ["negate", "negate"]
    forged_optimum["preparation_steps"] += 2
    rejection("valid_but_nonoptimal_path", lambda: verify_entry(forged_optimum))
    potential = bellman_potential(3, 2)["distances"]
    potential[6 + 2] -= 1
    rejection("forged_distance_potential", lambda: validate_potential(3, 2, potential))
    wrong_path = dict(valid, end_sign=-1)
    rejection("wrong_signed_endpoint", lambda: verify_entry(wrong_path))
    off_grid = dict(valid, operations=["halve", "halve"], preparation_steps=2)
    rejection("odd_state_halving", lambda: verify_entry(off_grid))
    return controls


def positive_controls() -> dict:
    """Check elementary exact distances and all primitive interpreter branches."""
    known_distances = [(1, 1, 0), (1, 2, 1), (1, 4, 2), (1, 8, 3),
                       (1, 16, 4), (3, 1, 2), (3, 2, 2), (7, 4, 4)]
    for numerator, denominator, steps in known_distances:
        actual = bellman_potential(numerator, denominator)["preparation_steps"]
        _require(actual == steps, "known elementary distance changed")
    # These two paths deliberately cover all five primitive names, independently
    # of whatever shortest witnesses happen to be supplied in a certificate.
    _require(replay_operations(3, 1, ["double", "negate", "subtract"], -1)
             == [1, 2, -2, -3], "primitive replay control failed")
    _require(replay_operations(3, 2, ["halve", "add"], 1) == [2, 1, 3],
             "fractional replay control failed")
    return {"known_distances": len(known_distances), "primitive_names_covered": 5}


def source_coefficients(path: Path) -> set[tuple[int, int]]:
    """Independently extract the claimed absolute JP8 scalar-add coefficient set."""
    data = path.read_bytes()
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    programs = json.loads(data)
    _require(set(programs) == {"forward", "backward"}, "unexpected program schema")
    selected = set()
    for program in programs.values():
        for row in program:
            if row[0] == "scalar" and row[1][0] == "add":
                coefficient = abs(Fraction(row[1][3], row[1][4]))
                n, d = coefficient.numerator, coefficient.denominator
                if 1 <= n <= 127 and d in (1, 2, 4, 8, 16):
                    selected.add((n, d))
    return selected


def run(entries: list[dict], *, include_distances: bool = False,
        source: Path | None = None) -> dict:
    _require(isinstance(entries, list) and entries, "certificate entries are empty")
    keys = [(e["numerator"], e["denominator"]) for e in entries]
    _require(len(keys) == len(set(keys)), "duplicate coefficient entry")
    if source is not None:
        expected = source_coefficients(source)
        # The direct unit addition is allowed to have no scratch-graph record.
        _require(set(keys) - {(1, 1)} == expected - {(1, 1)},
                 "certificate does not cover the selected source coefficients")
    verified = [verify_entry(e, include_distances=include_distances) for e in entries]
    return {
        "status": "PASS",
        "method": "full synchronous reverse Bellman relaxation and all-edge potential proof",
        "checked_coefficients": len(verified),
        "checked_vertices": sum(e["vertices"] for e in verified),
        "checked_directed_edges": sum(e["directed_edges"] for e in verified),
        "source_coverage_checked": source is not None,
        "negative_controls": negative_controls(),
        "positive_controls": positive_controls(),
        "entries": verified,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", nargs="?", type=Path)
    parser.add_argument("--source", type=Path,
                        help="pinned JP8 LOCAL-PROGRAMS.json.gz for independent coverage")
    parser.add_argument("--potentials", type=Path,
                        help="write full potential arrays as a reproducible certificate")
    parser.add_argument("--output", type=Path, help="write compact JSON report")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(json.dumps({"status": "PASS", "negative_controls": negative_controls(),
                          "positive_controls": positive_controls()},
                         indent=2, sort_keys=True))
        return
    if args.certificate is None:
        parser.error("certificate is required unless --self-test is used")
    certificate = json.loads(args.certificate.read_text())
    report = run(certificate["entries"], include_distances=bool(args.potentials),
                 source=args.source)
    if args.potentials:
        args.potentials.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        for entry in report["entries"]:
            del entry["distances"]
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
