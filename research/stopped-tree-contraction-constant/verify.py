#!/usr/bin/env python3
"""Exact new-tree corroboration for the contraction toll bound; Apache-2.0."""

from fractions import Fraction as F
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json
import platform


def need(condition, message):
    if not condition:
        raise ValueError(message)


def coarse_constant(beta, delta, rho, stop, moment):
    need(beta > 0 and 0 < delta <= 1, "invalid exponents")
    need(0 < rho < 1 and stop >= 1, "invalid contraction or stop")
    need(0 <= moment <= 1, "critical moment exceeds one")
    return 1 / (delta * (1 - rho))


def rational_power(value, exponent):
    """Only the fixed integer/half-integer fixture exponents are accepted."""
    need(value > 0 and exponent.denominator in (1, 2), "power domain")
    if exponent.denominator == 1:
        return value ** exponent.numerator
    numerator, denominator = isqrt(value.numerator), isqrt(value.denominator)
    need(numerator**2 == value.numerator, "nonsquare numerator")
    need(denominator**2 == value.denominator, "nonsquare denominator")
    return F(numerator, denominator) ** exponent.numerator


def enumerate_tree(root, stop, beta, delta, rho, branches):
    """Explicit finite paths; volumes and normalized path weights are separate."""
    queue = [(root, F(1), F(1), F(0), 0)]
    toll, leaf_potential, max_path, leaf_probability = (F(0),) * 4
    visited = 0
    for _ in range(8191):
        if not queue:
            return toll, leaf_potential, max_path, leaf_probability, visited
        width, volume, probability, path_sum, depth = queue.pop()
        visited += 1
        need(depth <= 12, "tree depth bound")
        need(probability == volume * rational_power(width / root, beta),
             "path/volume normalization")
        if width <= stop:
            leaf_potential += volume * rational_power(width, beta)
            leaf_probability += probability
            max_path = max(max_path, path_sum)
            continue
        increment = rational_power(width, -delta)
        path_sum += increment
        toll += volume * rational_power(width, beta - delta)
        children = branches(width)
        conditional_mass = F(0)
        for child, factor in children:
            need(0 < child <= rho * width, "strict width contraction")
            weight = factor * rational_power(child / width, beta)
            conditional_mass += weight
            queue.append((child, volume * factor, probability * weight,
                          path_sum, depth + 1))
        need(conditional_mass <= 1, "node critical moment")
        if conditional_mass < 1:
            max_path = max(max_path, path_sum)
    raise ValueError("tree node bound exhausted")


def check_tree(root, stop, beta, delta, rho, branches):
    toll, leaves, longest, probability, visited = enumerate_tree(
        root, stop, beta, delta, rho, branches)
    exact_factor = 1 / (1 - rational_power(rho, delta))
    allowance = rational_power(root, beta) * rational_power(stop, -delta)
    need(toll <= allowance * exact_factor, "exact contraction toll bound")
    need(longest <= rational_power(stop, -delta) * exact_factor,
         "backward path bound")
    need(leaves <= rational_power(root, beta) and probability <= 1,
         "leaf potential bound")
    coarse = coarse_constant(beta, delta, rho, stop, F(1))
    need(exact_factor <= coarse, "concavity relaxation")
    return toll, leaves, visited


def floor_trees():
    cases, nodes = 0, 0
    for beta in (F(1), F(2)):
        base = (F(1), F(1)) if beta == 1 else (F(9, 2), F(9, 8))
        for thinning in (F(1), F(1, 2)):
            weights = tuple(thinning * weight for weight in base)
            for stop in (2, 3, 7, 16):
                tolls, leaves = [F(0)] * 97, [F(0)] * 97
                for width in range(1, 97):
                    if width <= stop:
                        leaves[width] = F(width) ** beta.numerator
                    else:
                        f = width // 3
                        tolls[width] = F(width) ** (beta.numerator - 1)
                        for rank, weight in zip((1, 2), weights):
                            tolls[width] += weight * tolls[rank * f]
                            leaves[width] += weight * leaves[rank * f]
                    def branches(current):
                        f = current // 3
                        return ((F(f), weights[0]), (F(2 * f), weights[1]))
                    actual = check_tree(F(width), F(stop), beta, F(1),
                                        F(2, 3), branches)
                    need(actual[:2] == (tolls[width], leaves[width]),
                         "literal tree disagrees with bottom-up recurrence")
                    cases += 1
                    nodes += actual[2]
    return cases, nodes


def square_trees():
    cases, nodes = 0, 0
    rho = F(4, 9)
    for beta in (F(1, 2), F(1)):
        weights = (F(1), F(3, 4)) if beta == F(1, 2) else (F(2), F(9, 8))
        for root_side in range(1, 13):
            for stop_side in range(1, 5):
                def branches(width):
                    return ((width / 4, weights[0]), (width * rho, weights[1]))
                actual = check_tree(F(root_side**2), F(stop_side**2),
                                    beta, F(1, 2), rho, branches)
                cases += 1
                nodes += actual[2]
    return cases, nodes


def application_constants():
    # These are cited source parameters, not a fresh certificate of its moment.
    b = F(".001730979115670792472760579929302792893760378764")
    a2 = F(".001733394791695384296")
    q, eta = b - F(1, 10**28), F(1, 10**32)
    beta, delta, rho = 1 - b, a2 - b, F(48, 73)
    bound = coarse_constant(beta, delta, rho, F(73), F(1))
    need(F(1208771) < bound < F(1209000), "new rational coefficient")
    need(1 - a2 > F(199, 200), "node exponent floor")
    need(74**199 >= 72**200, "remainder absorption")
    need(0 < q < b < a2 < 1 and eta * b < b - q, "outer exponent order")
    return {"beta": str(beta), "delta": str(delta), "rho": str(rho),
            "coarse_coefficient": str(bound), "integer_upper_bound": 1209000,
            "critical_moment": "cited PR4965 premise, not replayed"}


def rejected_controls():
    invalid = ((F(0), F(1), F(1, 2), F(1), F(1)),
               (F(1), F(0), F(1, 2), F(1), F(1)),
               (F(1), F(-1), F(1, 2), F(1), F(1)),
               (F(1), F(2), F(1, 2), F(1), F(1)),
               (F(1), F(1), F(0), F(1), F(1)),
               (F(1), F(1), F(1), F(1), F(1)),
               (F(1), F(1), F(1, 2), F(0), F(1)),
               (F(1), F(1), F(1, 2), F(1), F(2)))
    for values in invalid:
        try:
            coarse_constant(*values)
        except ValueError:
            continue
        raise ValueError("invalid theorem premise accepted")
    # At equal node/critical exponents each full binary level costs 2^depth.
    depth = 12
    critical_toll = sum(F(2**level) * F(2 ** (depth - level))
                        for level in range(depth))
    need(critical_toll == depth * 2**depth, "zero exponent-gap control")
    # Doubling each child's volume violates the critical moment condition.
    bad_toll = sum(F(4**level) for level in range(8))
    need(bad_toll > 2 * 2**8, "supercritical-mass control")
    need(F(5) > 1 / (1 - F(1, 2)), "noncontracting unary chain control")
    return len(invalid) + 3


def package_hashes():
    root = Path(__file__).resolve().parent
    names = ("PROOF.md", "README.md", "SOURCES.json", "TASK.json",
             "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        with (root / name).open("rb") as handle:
            payload = handle.read(131073)
        need(len(payload) <= 131072, "package file capacity")
        hashes[name] = sha256(payload).hexdigest()
    return hashes


def main():
    floor_cases, floor_nodes = floor_trees()
    square_cases, square_nodes = square_trees()
    receipt = {"status": "PASS_STOPPED_TREE_CONTRACTION_CONSTANT",
               "claim_type": "scoped written proof with exact corroboration",
               "floor_tree_cases": floor_cases, "floor_tree_nodes": floor_nodes,
               "square_tree_cases": square_cases, "square_tree_nodes": square_nodes,
               "controls": rejected_controls(), "application": application_constants(),
               "python": platform.python_version(), "files": package_hashes()}
    print(json.dumps(receipt, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
