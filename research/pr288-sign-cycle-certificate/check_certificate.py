#!/usr/bin/env python3
"""Check the small PR #288 sign obstruction using exact arithmetic only.

This checker neither imports the certificate producer nor runs the upstream
checker. It normalizes all nonzero vectors in F9^3 to reconstruct PG(2,9),
then checks explicit paths and one negative cycle. No solver is used.

The mathematical interpretation is in math_review.md. In particular the
frame matrices are over Q, despite the graph coordinates being over F9.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from functools import lru_cache
from pathlib import Path
import sys


# Pin the exact reviewed transcription as well as binding certificate to data.
# This is the SHA-256 of the distributed instance.json, including whitespace.
EXPECTED_INSTANCE_SHA256 = (
    "06f62ef3c3b5448a67fd1b8ff1edf69012f6aa07c7dd60b1f3c83baa5343dabb"
)
DIMENSION = 5


class CertificateError(ValueError):
    """A malformed input or an unproved certificate claim."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CertificateError(message)


def _integer(value: object) -> bool:
    # JSON true/false must not silently count as the integers 1/0.
    return type(value) is int


def _fields(value: object, expected: set[str], context: str) -> None:
    _require(type(value) is dict, f"{context} must be an object")
    _require(set(value) == expected, f"{context} has missing or unknown fields")


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        _require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _parse_json(raw: bytes, context: str) -> object:
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise CertificateError(f"invalid {context}: {error}") from error


# F9 elements are integers a+3*b encoding the polynomial a+b*t.
# Multiplication uses polynomial convolution, then reduction by t^2+1.
# This intentionally differs from the upstream pair-arithmetic constructor.
def field_add(x: int, y: int) -> int:
    return (x % 3 + y % 3) % 3 + 3 * ((x // 3 + y // 3) % 3)


def field_multiply(x: int, y: int) -> int:
    left, right = (x % 3, x // 3), (y % 3, y // 3)
    coefficients = [0, 0, 0]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            coefficients[i + j] += a * b
    coefficients[0] -= coefficients[2]
    return coefficients[0] % 3 + 3 * (coefficients[1] % 3)


@lru_cache(maxsize=8)
def field_inverse(x: int) -> int:
    _require(_integer(x) and 1 <= x <= 8, "only nonzero F9 elements invert")
    inverses = [y for y in range(1, 9) if field_multiply(x, y) == 1]
    _require(len(inverses) == 1, "F9 inverse is not unique")
    return inverses[0]


def _normalize(vector: tuple[int, int, int]) -> tuple[int, int, int]:
    pivot = next((x for x in vector if x), None)
    _require(pivot is not None, "zero vector has no projective normalization")
    inverse = field_inverse(pivot)
    return tuple(field_multiply(x, inverse) for x in vector)


def _dot(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    total = 0
    for x, y in zip(left, right):
        total = field_add(total, field_multiply(x, y))
    return total


@lru_cache(maxsize=1)
def projective_graph() -> tuple[tuple[tuple[int, int, int], ...],
                                tuple[tuple[int, int], ...]]:
    """Return canonical representatives and point-to-line oriented edges.

    Points 0..90 and lines 91..181 use the same sorted normalized triples.
    Edge indices sort by point, then by incident line, as in the source.
    """
    representatives = tuple(sorted({
        _normalize(vector)
        for vector in itertools.product(range(9), repeat=3)
        if any(vector)
    }))
    _require(len(representatives) == 91, "wrong projective point count")
    edges = tuple(
        (point, 91 + line)
        for point, p in enumerate(representatives)
        for line, ell in enumerate(representatives)
        if _dot(p, ell) == 0
    )
    _require(len(edges) == 910, "wrong full incidence edge count")
    _require(len(set(edges)) == 910, "duplicate full incidence edges")
    degrees = [0] * 182
    for point, line in edges:
        degrees[point] += 1
        degrees[line] += 1
    _require(set(degrees) == {10}, "full incidence graph is not 10-regular")
    return representatives, edges


def _integer_set(values: object, count: int, bound: int, context: str) -> set[int]:
    _require(type(values) is list and len(values) == count,
             f"{context} must have exactly {count} entries")
    _require(all(_integer(x) and 0 <= x < bound for x in values),
             f"{context} contains an out-of-range or non-integer entry")
    _require(len(set(values)) == count, f"{context} contains duplicate entries")
    return set(values)


def _validate_instance(instance: object) -> tuple[set[int], set[int]]:
    _fields(instance, {"schema", "removed_edges", "constant_zero_edges",
                       "dropped_edges", "vertex_order"}, "instance")
    _require(instance["schema"] == "pr288-pg29-v1", "wrong instance schema")
    removed = _integer_set(instance["removed_edges"], 175, 910, "removed_edges")
    _require(instance["removed_edges"] == sorted(removed),
             "removed_edges must be sorted")
    constants = _integer_set(instance["constant_zero_edges"], 9, 910,
                             "constant_zero_edges")
    dropped = _integer_set(instance["dropped_edges"], 9, 910, "dropped_edges")
    _require(constants <= removed and dropped <= removed,
             "constant and dropped edges must belong to removed_edges")
    _require(not constants & dropped, "constant and dropped sets overlap")
    _integer_set(instance["vertex_order"], 182, 182, "vertex_order")
    sessions = removed - constants - dropped
    physical = set(range(910)) - removed
    _require(len(sessions) == 157 and len(physical) == 735,
             "wrong session or physical-edge count")
    return sessions, physical


def verify(instance_path: str | Path, certificate_path: str | Path) -> dict:
    """Verify files and return a summary; raise CertificateError on failure."""
    raw_instance = Path(instance_path).read_bytes()
    raw_certificate = Path(certificate_path).read_bytes()
    instance = _parse_json(raw_instance, "instance JSON")
    certificate = _parse_json(raw_certificate, "certificate JSON")
    sessions, physical = _validate_instance(instance)
    _fields(certificate, {"schema", "dimension", "instance_sha256",
                          "cycle_nodes", "incidences"}, "certificate")
    _require(certificate["schema"] == "pr288-negative-cycle-v1",
             "wrong certificate schema")
    _require(_integer(certificate["dimension"])
             and certificate["dimension"] == DIMENSION,
             "certificate dimension must be exactly 5")
    instance_digest = hashlib.sha256(raw_instance).hexdigest()
    _require(certificate["instance_sha256"] == instance_digest,
             "certificate instance hash does not match exact file bytes")
    _require(instance_digest == EXPECTED_INSTANCE_SHA256,
             "instance does not match the pinned PR #288 transcription")

    _, edges = projective_graph()
    edge_ids = {edge: index for index, edge in enumerate(edges)}
    cycle = certificate["cycle_nodes"]
    _require(type(cycle) is list and len(cycle) >= 4 and len(cycle) % 2 == 0,
             "cycle must have an even number of at least four nodes")
    for node in cycle:
        _require(type(node) is list and len(node) == 2,
                 "cycle node must be [kind, integer]")
        kind, identity = node
        _require(kind in ("session", "edge") and _integer(identity),
                 "cycle node has an invalid kind or identity")
        if kind == "session":
            _require(identity in sessions, f"session {identity} is not in R minus C and J")
        else:
            _require(identity in physical, f"edge {identity} is not physical")
    _require(len({tuple(node) for node in cycle}) == len(cycle),
             "cycle nodes must be unique")
    incidences = certificate["incidences"]
    _require(type(incidences) is list and len(incidences) == len(cycle),
             "cycle and incidence counts differ")

    sign_product = 1
    distinct_paths = set()
    used_edges = set()
    for index, incidence in enumerate(incidences):
        first, second = cycle[index], cycle[(index + 1) % len(cycle)]
        _require(first[0] != second[0], "cycle does not alternate session and edge nodes")
        session, edge = (first[1], second[1]) if first[0] == "session" else (second[1], first[1])
        _fields(incidence, {"path", "sign"}, f"incidence {index}")
        path = incidence["path"]
        _require(type(path) is list and len(path) == DIMENSION + 1,
                 f"incidence {index}: path must have exactly five edges")
        _require(all(_integer(v) and 0 <= v < 182 for v in path),
                 f"incidence {index}: invalid path vertex")
        _require((path[0], path[-1]) == edges[session],
                 f"incidence {index}: wrong point-to-line session endpoints")
        _require(len(set(path)) == len(path), f"incidence {index}: path is not simple")
        occurrences = []
        for x, y in zip(path, path[1:]):
            oriented = (min(x, y), max(x, y))
            _require(oriented in edge_ids,
                     f"incidence {index}: consecutive vertices are not incident")
            traversed = edge_ids[oriented]
            _require(traversed in physical,
                     f"incidence {index}: path uses removed edge {traversed}")
            used_edges.add(traversed)
            if traversed == edge:
                occurrences.append(1 if (x, y) == edges[edge] else -1)
        _require(len(occurrences) == 1,
                 f"incidence {index}: selected edge must occur exactly once")
        actual_sign = occurrences[0]
        claimed_sign = incidence["sign"]
        _require(_integer(claimed_sign) and claimed_sign in (-1, 1),
                 f"incidence {index}: sign must be the integer +1 or -1")
        _require(claimed_sign == actual_sign,
                 f"incidence {index}: sign does not match path traversal")
        sign_product *= actual_sign
        distinct_paths.add(tuple(path))

    _require(sign_product == -1,
             "balanced cycle: sign product is +1, so this proves no obstruction")
    return {
        "status": "verified",
        "claim": "negative cycle in necessary rank-one frame sign constraints",
        "frame_field": "Q (also valid over any field of characteristic not 2)",
        "dimension": DIMENSION,
        "instance_sha256": instance_digest,
        "full_graph_vertices": 182,
        "full_graph_edges": len(edges),
        "physical_edges": len(physical),
        "sessions": len(sessions),
        "cycle_nodes": len(cycle),
        "certified_incidences": len(incidences),
        "distinct_length_five_paths": len(distinct_paths),
        "physical_edges_in_paths": len(used_edges),
        "sign_product": sign_product,
    }


def main() -> int:
    directory = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", type=Path, default=directory / "instance.json")
    parser.add_argument("--certificate", type=Path, default=directory / "certificate.json")
    args = parser.parse_args()
    try:
        result = verify(args.instance, args.certificate)
    except (CertificateError, OSError) as error:
        print(f"REJECTED: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
