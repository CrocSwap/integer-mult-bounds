#!/usr/bin/env python3
"""Check the new Boolean rounding step; the cited spectral premise is not replayed."""

import hashlib
import json
from fractions import Fraction
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def spectral_scalar_pair(k: int, d: int) -> bool:
    """Decide 6k/d <= (27+9 sqrt(2))/7 by integer arithmetic."""
    require(k >= 0 and d > 0, "invalid scalar pair")
    rational_part = 42 * k - 27 * d
    return rational_part <= 0 or rational_part**2 <= 162 * d**2


def scalar_certificate() -> dict:
    best = Fraction(0)
    maximizers = []
    admitted = 0
    for k in range(57):
        for d in range(2, 505, 2):
            if not spectral_scalar_pair(k, d):
                continue
            admitted += 1
            ratio = Fraction(6 * k, d)
            if ratio > best:
                best = ratio
                maximizers = [(k, d)]
            elif ratio == best:
                maximizers.append((k, d))
    require(best == Fraction(17, 3), "wrong arithmetic maximum")
    require(maximizers == [(17, 18), (34, 36), (51, 54)], "wrong witnesses")
    gap = 1109**2 - 162 * 87**2
    require(gap == 3703 and gap > 0, "invalid rational-gap proof")
    require(Fraction(17, 3) + Fraction(1, 87) == Fraction(494, 87), "gap")
    return {"pairs_checked": 57 * 252, "admitted_pairs": admitted,
            "maximum": str(best), "maximizers": maximizers, "gap": gap}


def groups_and_labels() -> tuple:
    group = tuple((a, b, c) for a in range(1, 8) for b in range(1, 8)
                  if b != a for c in range(1, 8) if c not in (a, b, a ^ b))
    require(len(group) == len(set(group)) == 168, "GL3 inventory")
    labels = tuple((i, j) for i in range(3) for j in range(3) if i != j)
    return group, labels


def natural_image(matrix: tuple, vector: int) -> int:
    return sum(((row & vector).bit_count() & 1) << i
               for i, row in enumerate(matrix))


def cnot_matrix(matrix: tuple, i: int, j: int) -> tuple:
    result = list(matrix)
    result[i] ^= result[j]
    return tuple(result)


def cnot_vector(vector: int, i: int, j: int) -> int:
    return vector ^ (((vector >> j) & 1) << i)


def cycle_matrix(matrix: tuple) -> tuple:
    return matrix[1], matrix[2], matrix[0]


def cycle_vector(vector: int) -> int:
    return ((vector >> 1) & 1) | (((vector >> 2) & 1) << 1) | ((vector & 1) << 2)


def crossing(subset: set, permutation: dict) -> int:
    return sum(permutation[x] not in subset for x in subset)


def orbit_lift_certificate() -> dict:
    group, labels = groups_and_labels()
    group_set = set(group)
    paid = tuple({g: cnot_matrix(g, i, j) for g in group} for i, j in labels)
    cycle = {g: cycle_matrix(g) for g in group}
    require(all(set(p.values()) == group_set for p in paid), "paid bijections")
    require(set(cycle.values()) == group_set, "cycle bijection")
    require(all(p[p[g]] == g and p[g] != g for p in paid for g in group),
            "regular matchings must be fixed-point-free involutions")
    require(all(cycle[cycle[cycle[g]]] == g and cycle[g] != g for g in group),
            "regular cycle must have order three and no fixed point")
    fibers = [sum(natural_image(g, 1) == x for g in group) for x in range(1, 8)]
    require(fibers == [24] * 7, "orbit fibers")
    for mask in range(128):
        subset = {x for x in range(1, 8) if (mask >> (x - 1)) & 1}
        lift = {g for g in group if natural_image(g, 1) in subset}
        boundary = 0
        for label_index, (i, j) in enumerate(labels):
            natural = sum(cnot_vector(x, i, j) not in subset for x in subset)
            lifted = crossing(lift, paid[label_index])
            require(lifted == 24 * natural, "paid crossing does not lift")
            boundary += lifted
        natural_k = sum(cycle_vector(x) not in subset for x in subset)
        k = crossing(lift, cycle)
        require(k == 24 * natural_k, "cycle crossing does not lift")
        internal_twice = sum(p[g] in lift for p in paid for g in lift)
        require(internal_twice % 2 == 0, "internal matching-edge parity")
        require(boundary == 6 * len(lift) - internal_twice, "degree identity")
        require(boundary % 2 == 0 and boundary <= 504, "boundary constraints")
        require(k <= 56, "order-three crossing cap")
    return {"group_order": len(group), "natural_subsets": 128,
            "regular_lifts": 128, "fiber_size": 24}


def enforce_scalar_bound(k: int, d: int, bound: Fraction) -> None:
    require(spectral_scalar_pair(k, d), "control must obey spectral premise")
    require(Fraction(6 * k, d) <= bound, "proposed bound is false")


def hypothesis_controls() -> list:
    controls = ((17, 18, Fraction(28, 5), "smaller ceiling"),
                (52, 55, Fraction(17, 3), "parity omitted"),
                (87, 92, Fraction(17, 3), "crossing cap omitted"))
    rejected = []
    for k, d, bound, name in controls:
        require(spectral_scalar_pair(k, d), "invalid negative-control premise")
        try:
            enforce_scalar_bound(k, d, bound)
        except ValueError as error:
            require(str(error) == "proposed bound is false", "wrong failure")
            rejected.append(name)
        else:
            raise ValueError("negative control accepted: " + name)
    require(len(rejected) == 3, "missing controls")
    return rejected


def main() -> None:
    report = {"status": "PASS_THREE_CYCLE_BOOLEAN_ROUNDING",
              "scope": "New rounding/lifting step only; PR5063 spectral premise is cited.",
              "scalar": scalar_certificate(), "lift": orbit_lift_certificate(),
              "rejected_controls": hypothesis_controls()}
    package = Path(__file__).resolve().parent
    files = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    report["source_sha256"] = {
        name: hashlib.sha256((package / name).read_bytes()).hexdigest() for name in files}
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
