#!/usr/bin/env python3
"""Offline exact audit. Default operation is read-only and fails on mismatch.

Prepared for William Lawyer with substantial OpenAI Codex assistance.
Apache-2.0. Finite certificates do not prove the written all-length results.
"""

import argparse
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import sys

from exact import (balanced_fixture, balanced_row_formula, cyclic_solve,
                   first_exceedance, perturbation_bound, power_certificate,
                   sharp_inverse_bound, sharp_local_cap)
from oracles import (Gaussian as G, gaussian_norm2, identity, inverse, monomial_norm2, multiply,
                     polynomial_from_roots, polynomial_matrix, real_norm,
                     weighted_matrix)

ROOT = Path(__file__).resolve().parent


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def reject(function, label):
    try:
        function()
    except (ValueError, ZeroDivisionError):
        return
    raise AssertionError("invalid input was accepted: " + label)


def rational_digest(value):
    """Canonical binary fraction digest, avoiding giant decimal conversion.

    SHA256 of sign byte, then numerator and denominator, each encoded as
    8-byte big-endian byte length followed by unsigned big-endian magnitude.
    """
    value = F(value)
    payload = bytes([value < 0])
    for part in (abs(value.numerator), value.denominator):
        data = part.to_bytes(max(1, (part.bit_length() + 7) // 8), "big")
        payload += len(data).to_bytes(8, "big") + data
    return hashlib.sha256(payload).hexdigest()


def source_check(root):
    sources = json.loads((root / "SOURCES.json").read_text(encoding="utf-8"))
    for entry in sources["files"]:
        data = (root / entry["local_path"]).read_bytes()
        require(hashlib.sha256(data).hexdigest() == entry["sha256"],
                "source SHA256: " + entry["local_path"])
        blob = b"blob " + str(len(data)).encode("ascii") + b"\0" + data
        require(hashlib.sha1(blob).hexdigest() == entry["git_blob"],
                "source git blob: " + entry["local_path"])
    return len(sources["files"])


def power_oracle():
    cases, powers = 0, 0
    for n in range(1, 6):
        gauges = [[F(1)] * n, [F(2) ** (i - 2) for i in range(n)],
                  [F(i + 1, i + 2) for i in range(n)]]
        phase_cycle = [G(1), G(0, 1), G(F(5, 13), F(12, 13))]
        phases = [[G(1)] * n, [G(F(3, 5), F(4, 5))] * n,
                  [phase_cycle[i % 3] for i in range(n)]]
        for permutation in itertools.permutations(range(n)):
            # Derive period by repeated composition, without cycle traversal.
            position = list(permutation)
            period = 1
            while position != list(range(n)):
                position = [permutation[j] for j in position]
                period += 1
            for gauge, phase in itertools.product(gauges, phases):
                weights = [phase[i] * (gauge[i] / gauge[permutation[i]])
                           for i in range(n)]
                certificate = power_certificate(
                    permutation, [(w.re, w.im) for w in weights])
                matrix = weighted_matrix(permutation, weights)
                backward = inverse(matrix)
                require(multiply(matrix, backward) == identity(n, G(1)),
                        "dense inverse residual")
                observed = F(1)
                for step in (matrix, backward):
                    current = identity(n, G(1))
                    for _ in range(period):
                        observed = max(observed, monomial_norm2(current))
                        current = multiply(current, step)
                        powers += 1
                require(observed == certificate["K2"], "dense power supremum")
                cases += 1
    return {"matrices": cases, "signed_power_samples": powers}


def small_resolvents(domain):
    cases, columns = 0, 0
    regimes = {"eta_below_delta": 0, "eta_equals_delta": 0, "eta_above_delta": 0}
    for k, m, multiplier in itertools.product(domain["eta_exponents"],
                                               domain["half_lengths"],
                                               domain["delta_multipliers"]):
        eta = F(1, 2 ** k)
        delta = eta * F(multiplier)
        a, weights = balanced_fixture(eta, m, delta)
        n = len(weights)
        wmat = weighted_matrix([(i - 1) % n for i in range(n)], weights)
        matrix = polynomial_matrix(wmat, [a, F(-1)])
        dense = inverse(matrix)
        require(multiply(matrix, dense) == identity(n), "left inverse residual")
        require(multiply(dense, matrix) == identity(n), "right inverse residual")
        for j in range(n):
            column = cyclic_solve(a, weights, [F(i == j) for i in range(n)])
            require(column == [row[j] for row in dense], "affine vs dense inverse")
            columns += 1
        row_sums = cyclic_solve(a, weights, [F(1)] * n)
        require(all(x >= 0 for row in dense for x in row), "positive inverse")
        require(row_sums == [sum(row) for row in dense], "inverse row sums")
        require(row_sums[m - 1] == balanced_row_formula(a, weights[0], m),
                "geometric vs affine row")
        require(max(row_sums) == real_norm(dense), "exact inverse norm")
        if eta < delta:
            require(real_norm(dense) <= 1 / (delta - eta), "uniform regime bound")
            regimes["eta_below_delta"] += 1
        elif eta == delta:
            require(m / a < real_norm(dense) <= n / (a * (1 - a ** -n)),
                    "critical linear regime bounds")
            regimes["eta_equals_delta"] += 1
        else:
            lower = ((weights[0] / a) ** m - 1) / (weights[0] - a)
            require(lower < real_norm(dense), "exponential regime lower bound")
            regimes["eta_above_delta"] += 1
        cases += 1
    return {"dense_inverses": cases, "independent_basis_solves": columns,
            "regimes": regimes}


def primary_witness(domain):
    eta, m = F(domain["eta"]), domain["half_length"]
    a, weights = balanced_fixture(eta, m)
    b, n = weights[0], len(weights)
    permutation = [(i - 1) % n for i in range(n)]
    cert = power_certificate(permutation, [(w, 0) for w in weights])
    require(cert["K2"] == b ** (2 * m), "primary power amplification")
    require(all(abs(w - 1) <= eta for w in weights), "primary local deviation")
    x = cyclic_solve(a, weights, [F(1)] * n)
    require(all(a * x[i] - weights[i] * x[i - 1] == 1 for i in range(n)),
            "primary sparse equation residual")
    row = balanced_row_formula(a, b, m)
    lower = ((b / a) ** m - 1) / (b - a)
    require(x[m - 1] == row and max(x) == row, "primary exact largest row")
    require(row > lower > 25 / (a - 1), "violates degree-only estimate without K")
    require(row <= b ** m / (a - 1), "power-paid geometric bound")
    require(int(row) < row < int(row) + 1, "primary strict integer enclosure")
    power_of_two = 1
    while (b / a) ** power_of_two <= 26:
        power_of_two *= 2
    require(power_of_two == m, "primary selection stopping rule")
    return {"length": n, "eta": str(eta), "a": str(a), "b": str(b),
            "circle_gap": str(a - 1), "loose_unit_bound": str(25 / (a - 1)),
            "sharper_unit_bound": str(5 / (a - 1)),
            "power_bound_floor": int(b ** m), "lower_bound_floor": int(lower),
            "inverse_norm": str(row), "inverse_norm_floor": int(row),
            "K2_digest": rational_digest(cert["K2"]),
            "inverse_norm_digest": rational_digest(row)}


def family_witnesses(domain):
    results = []
    for k in domain["eta_exponents"]:
        eta = F(1, 2 ** k)
        b, a = 1 + eta, 1 + eta / 2
        q = b / a
        m = first_exceedance(q, 26)
        require(q ** (m - 1) <= 26 < q ** m, "least threshold certificate")
        lower = (q ** m - 1) / (b - a)
        require(lower > 25 / (a - 1), "family exceeds unit-bound estimate")
        results.append({"eta": str(eta), "first_half_length": m,
                        "length": 2 * m, "lower_bound_floor": int(lower),
                        "lower_bound_digest": rational_digest(lower),
                        "numerator_bits": lower.numerator.bit_length(),
                        "denominator_bits": lower.denominator.bit_length()})
    return results


def polynomial_guards(domain):
    roots = list(map(F, domain["roots"]))
    tested, accepted, rejected = 0, 0, 0
    minimum, maximum = domain["degree_range"]
    n = domain["dimension"]
    permutation = [(i - 1) % n for i in range(n)]
    unit = weighted_matrix(permutation, [F(1)] * n)
    for degree in range(minimum, maximum + 1):
        for root_tuple in itertools.product(roots, repeat=degree):
            coefficients = polynomial_from_roots(root_tuple)
            delta = F(1)
            for r in root_tuple:
                delta *= r - 1
            # Each geometric factor at this unit permutation has norm <=1/(r-1).
            bound = 1 / delta
            base_matrix = polynomial_matrix(unit, coefficients)
            require(real_norm(inverse(base_matrix)) <= bound, "unit base bound")
            for eta in map(F, domain["eta"]):
                tested += 1
                weights = [1 + eta, 1 - eta, 1 + eta / 2, 1 - eta / 2]
                require(n == len(weights), "guard domain dimension")
                matrix = polynomial_matrix(weighted_matrix(permutation, weights),
                                           coefficients)
                difference = [[matrix[i][j] - base_matrix[i][j]
                               for j in range(n)] for i in range(n)]
                error, paid = perturbation_bound(list(map(abs, coefficients)),
                                                 eta, bound)
                require(real_norm(difference) <= error, "polynomial error bound")
                if paid is None:
                    rejected += 1
                else:
                    accepted += 1
                    require(real_norm(inverse(matrix)) <= paid,
                            "admitted Neumann inverse bound")
    require(accepted and rejected, "guard covers both outcomes")
    return {"tested": tested, "admitted": accepted, "not_admitted": rejected}


def admission_controls():
    controls = []
    def check(label, condition):
        require(condition, "admission/failure control: " + label)
        controls.append(label)

    c = power_certificate([0, 1], [(2, 0), (F(1, 2), 0)])
    check("global_product_cannot_replace_each_cycle_product", c["K2"] is None)
    c = power_certificate([1, 0], [(F(1, 2), 0)] * 2)
    check("forward_contraction_does_not_control_negative_powers", c["K2"] is None)
    c = power_certificate([1, 2, 3, 0], [(2, 0), (2, 0), (F(1, 2), 0),
                                            (F(1, 2), 0)])
    check("max_edge_is_not_max_path", c["K2"] == 16 and c["K2"] > 4)
    check("unit_spectrum_does_not_imply_power_norm_one", c["K2"] > 1)
    wmat = weighted_matrix([1, 2, 3, 0], [F(2), F(2), F(1, 2), F(1, 2)])
    check("monomial_attains_the_wiener_transfer_factor",
          real_norm(inverse(polynomial_matrix(wmat, [F(0), F(0), F(1)]))) == 4)
    c = power_certificate([1, 0], [(1, 1), (F(1, 2), -F(1, 2))])
    check("K_need_not_be_rational", c["K2"] == 2)
    c = power_certificate([1, 0], [(F(3, 5), F(4, 5)), (0, 1)])
    check("unit_holonomy_need_not_equal_one", c["K2"] == 1)
    for label, permutation, weights in [
            ("zero_weight", [0], [(0, 0)]),
            ("duplicate_column", [0, 0], [(1, 0)] * 2),
            ("out_of_range_column", [2, 0], [(1, 0)] * 2),
            ("empty_matrix", [], [])]:
        reject(lambda p=permutation, w=weights: power_certificate(p, w), label)
        controls.append(label)
    eta = F(1, 16)
    error, paid = perturbation_bound([1 + eta, 1], eta, 1 / eta)
    check("strict_guard_rejects_singular_equality", error / eta == 1 and paid is None)
    reject(lambda: inverse([[F(0)]]), "equality singular witness")
    error, paid = perturbation_bound([F(33, 32), 1], eta, F(32))
    check("counterexample_outside_perturbation_guard", error == eta and paid is None)
    weights = [F(17, 16)] * 2 + [F(16, 17)] * 2
    x = cyclic_solve(F(33, 32), weights, [F(1)] * 4)
    swapped = [weights[0], weights[2], weights[1], weights[3]]
    check("balanced_weight_order_changes_norm",
          max(x) != max(cyclic_solve(F(33, 32), swapped, [F(1)] * 4)))
    wrong = cyclic_solve(F(33, 32), swapped, [F(1)] * 4)
    check("residual_detects_wrong_weight_order",
          any(F(33, 32) * wrong[i] - weights[i] * wrong[i - 1] != 1
              for i in range(4)))
    reject(lambda: cyclic_solve(1, [F(2), F(1, 2)], [F(1)] * 2),
           "singular unit closure")
    controls.append("singular_cycle_closure")
    # Two cycles may choose different diagonal gauges; no global gauge ratio.
    c = power_certificate([1, 0, 3, 2], [(2, 0), (F(1, 2), 0),
                                               (3, 0), (F(1, 3), 0)])
    check("independent_cycle_gauges", c["K2"] == 9)
    # A nonunit product can still be admitted by the separate perturbation guard.
    e, paid = perturbation_bound([2, 1], F(1, 4), 1)
    check("guard_does_not_require_unit_cycle_product",
          e == F(1, 4) and paid == F(4, 3)
          and inverse([[F(3, 4)]])[0][0] == paid)
    return controls


def local_caps(domain):
    cases, paths = 0, 0
    for length, eta_text in itertools.product(domain["lengths"], domain["eta"]):
        eta = F(eta_text)
        lower, upper = 1 - eta, 1 + eta
        cap, weights = sharp_local_cap(length, lower, upper)
        require(all(lower <= w <= upper for w in weights), "local-cap interval")
        product = F(1)
        for w in weights:
            product *= w
        require(product == 1, "local-cap cycle product")
        observed = F(1)
        for i in range(length):
            product = F(1)
            for r in range(length):
                observed = max(observed, product)
                product *= weights[(i + r) % length]
                paths += 1
        cert = power_certificate([(i + 1) % length for i in range(length)],
                                 [(w, 0) for w in weights])
        require(observed == cap and cert["K2"] == cap ** 2,
                "attained sharp local cap")
        cases += 1
    return {"attaining_cycles": cases, "independent_path_products": paths}


def sharp_inverses(domain):
    cases = 0
    for length, eta_text, multiple in itertools.product(
            domain["lengths"], domain["eta"], domain["delta_multipliers"]):
        eta = F(eta_text)
        a = 1 + eta * F(multiple)
        bound, weights = sharp_inverse_bound(a, length, 1 - eta, 1 + eta)
        require(all(abs(w - 1) <= eta for w in weights), "extremizer local tolerance")
        cert = power_certificate([(i + 1) % length for i in range(length)],
                                 [(w, 0) for w in weights])
        require(cert["K2"] is not None, "extremizer cycle balance")
        wmat = weighted_matrix([(i + 1) % length for i in range(length)], weights)
        dense = inverse(polynomial_matrix(wmat, [a, F(-1)]))
        require(real_norm(dense) == bound == sum(dense[0]),
                "sharp bound attained in dense row zero")
        cases += 1
    large = []
    eta, length = F(1, 16), 256
    for multiple in domain["delta_multipliers"]:
        delta = eta * F(multiple)
        a = 1 + delta
        bound, weights = sharp_inverse_bound(a, length, 1 - eta, 1 + eta)
        # Reverse coordinates to use the independent predecessor recurrence.
        reversed_weights = [weights[-i % length] for i in range(length)]
        x = cyclic_solve(a, reversed_weights, [F(1)] * length)
        require(all(a * x[i] - reversed_weights[i] * x[i - 1] == 1
                    for i in range(length)), "sharp 256-cycle residual")
        require(x[0] == max(x) == bound, "sharp 256-cycle row norm")
        require(int(bound) < bound < int(bound) + 1, "sharp strict integer enclosure")
        large.append({"delta": str(delta), "norm_floor": int(bound),
                      "norm_digest": rational_digest(bound),
                      "upper_endpoint_weights": weights.count(1 + eta),
                      "lower_endpoint_weights": weights.count(1 - eta),
                      "residual_weights": [str(w) for w in weights
                                           if w not in (1 - eta, 1 + eta)]})
    return {"attaining_dense_inverses": cases, "large_cycle_length": length,
            "large_cycle_eta": str(eta), "large_cycle_regimes": large}


def complex_phase_inverses(domain):
    cases, strict = 0, 0
    phase_cycle = [G(1), G(0, 1), G(F(5, 13), F(-12, 13))]
    for length, eta_text, multiple in itertools.product(
            domain["lengths"], domain["eta"], domain["delta_multipliers"]):
        eta = F(eta_text)
        a = 1 + eta * F(multiple)
        bound, amplitudes = sharp_inverse_bound(a, length, 1 - eta, 1 + eta)
        phases = [[G(1)] * length, [G(F(3, 5), F(4, 5))] * length,
                  [phase_cycle[i % 3] for i in range(length)]]
        for phase in phases:
            weights = [p * amp for p, amp in zip(phase, amplitudes)]
            wmat = weighted_matrix([(i + 1) % length for i in range(length)], weights)
            matrix = polynomial_matrix(wmat, [a, F(-1)])
            dense = inverse(matrix)
            require(multiply(matrix, dense) == identity(length, G(1)),
                    "complex inverse residual")
            observed2 = gaussian_norm2(dense)
            require(observed2 <= bound ** 2, "complex sharp envelope upper bound")
            h = G(1)
            for weight in weights:
                h *= weight
            require(h.re ** 2 + h.im ** 2 == 1, "complex unit cycle product")
            denominator = a ** length - h
            denominator2 = denominator.re ** 2 + denominator.im ** 2
            predicted2 = bound ** 2 * (a ** length - 1) ** 2 / denominator2
            require(observed2 == predicted2, "exact complex closure factor")
            strict += observed2 < bound ** 2
            cases += 1
    require(strict > 0, "nontrivial phase denominator covered")
    return {"dense_inverses": cases, "strict_phase_improvements": strict}


def run(root=ROOT):
    domain = json.loads((root / "DOMAIN.json").read_text(encoding="utf-8"))
    return {"schema": 1, "arithmetic": "Python Fraction; Gaussian pairs of Fraction",
            "domain_sha256": hashlib.sha256((root / "DOMAIN.json").read_bytes()).hexdigest(),
            "pinned_source_files": source_check(root),
            "power_oracle": power_oracle(),
            "resolvent_oracle": small_resolvents(domain["resolvent_oracle"]),
            "primary_witness": primary_witness(domain["primary_witness"]),
            "near_unit_family": family_witnesses(domain["near_unit_family"]),
            "polynomial_guard": polynomial_guards(domain["polynomial_guard"]),
            "sharp_local_cap": local_caps(domain["sharp_local_cap"]),
            "sharp_inverse": sharp_inverses(domain["sharp_inverse"]),
            "complex_phase_inverse": complex_phase_inverses(domain["complex_phase_inverse"]),
            "admission_and_failure_controls": admission_controls()}


def check_receipt(result, path):
    expected = json.loads(path.read_text(encoding="utf-8"))
    require(result == expected, "receipt mismatch")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-receipt", action="store_true",
                        help="explicitly regenerate EXPECTED.json; default checks it")
    args = parser.parse_args()
    result = run()
    path = ROOT / "EXPECTED.json"
    if args.write_receipt:
        path.write_bytes((json.dumps(result, indent=2) + "\n").encode("utf-8"))
    else:
        check_receipt(result, path)
    print("PASS: exact weighted-cycle power audit")
    print(json.dumps({k: result[k] for k in ("power_oracle", "resolvent_oracle",
                                            "polynomial_guard", "sharp_local_cap")}, sort_keys=True))
    print("admission/failure controls:", len(result["admission_and_failure_controls"]))
    print("sharp inverse witnesses:", result["sharp_inverse"]["attaining_dense_inverses"],
          "dense and", len(result["sharp_inverse"]["large_cycle_regimes"]), "large")
    print("complex phase inverses:", result["complex_phase_inverse"]["dense_inverses"])
    print("primary inverse norm floor:", result["primary_witness"]["inverse_norm_floor"])
    print("Finite replay; see PROOF.md for all-length reasoning and inherited assumptions.")


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, ValueError, OSError) as error:
        print("FAIL:", error, file=sys.stderr)
        sys.exit(1)
