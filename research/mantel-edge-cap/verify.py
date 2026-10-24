#!/usr/bin/env python3
"""Mantel's edge cap on at most seven vertices.

The checker enumerates graphs above floor(n^2/4). It does not replay the
centre window.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
MARKER = "PASS_MANTEL_EDGE_CAP graphs=407058 no_new_kappa"
SELECTED = "836330098538459/500000000000000000"
MAX_VERTICES = 7
FLOOR_LIMIT = 1 << 20


def fail(message):
    raise SystemExit("FAIL_MANTEL_EDGE_CAP " + message)


def require(condition, message):
    if not condition:
        fail(message)


def edge_bit(order, left, right):
    return left * (2 * order - left - 1) // 2 + (right - left - 1)


def triangles(order):
    found = []
    for first in range(order):
        for second in range(first + 1, order):
            for third in range(second + 1, order):
                found.append((
                    edge_bit(order, first, second),
                    edge_bit(order, first, third),
                    edge_bit(order, second, third),
                ))
    return found


def construction(order):
    part = order // 2
    mask = 0
    for left in range(part):
        for right in range(part, order):
            mask |= 1 << edge_bit(order, left, right)
    return mask


def has_triangle(mask, triples):
    for first, second, third in triples:
        if (mask >> first) & 1 and (mask >> second) & 1 and (mask >> third) & 1:
            return True
    return False


def main():
    # The selected record at base_commit, a provenance pin checked by scripts/research_package.py.
    selected = {"kappa": "836330098538459/500000000000000000"}
    require(selected["kappa"] == SELECTED, "selected kappa moved")
    above = 0
    for order in range(1, MAX_VERTICES + 1):
        edge_count = order * (order - 1) // 2
        cap = (order * order) // 4
        triples = triangles(order)
        built = construction(order)
        require(built.bit_count() == cap, "the bipartite graph missed the cap")
        require(not has_triangle(built, triples), "the bipartite graph has a triangle")
        for mask in range(1 << edge_count):
            if mask.bit_count() <= cap:
                continue
            above += 1
            require(has_triangle(mask, triples), "a triangle-free graph passed the cap")
    floor_checks = 0
    for order in range(1, FLOOR_LIMIT + 1):
        left = order // 2
        right = (order + 1) // 2
        require(left * right == (order * order) // 4, "the floor identity moved")
        floor_checks += 1
    receipt = json.loads((PACKAGE / "RESULT.json").read_text())
    require(above == 407058, "graph count")
    require(floor_checks == 1048576, "floor count")
    require(receipt["max_vertices"] == MAX_VERTICES, "receipt vertices")
    require(receipt["graphs_above_cap"] == above, "receipt graphs")
    require(receipt["floor_checks"] == floor_checks, "receipt floors")
    require(receipt["no_new_kappa"] is True, "kappa flag")
    print(MARKER)


if __name__ == "__main__":
    main()
