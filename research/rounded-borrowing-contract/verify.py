#!/usr/bin/env python3
"""Check the exact finite domains specified in COVERAGE.md.

The uniform claims use the written proof. This finite checker is not a proof
assistant or a multiplication implementation. See NOTICE.md for attribution.
"""
import argparse
from fractions import Fraction
from hashlib import sha256
import importlib.util
from itertools import product
import json
from math import gcd
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from contracts import (exact_lift, inverse, nearest, offset_sum, prefix_degree,
                       replay, residue_response)


def need(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sources():
    manifest = json.loads((ROOT / "SOURCES.json").read_text())
    for item in manifest["files"]:
        data = (ROOT / item["path"]).read_bytes()
        need(sha256(data).hexdigest() == item["sha256"], "source digest mismatch")
        blob = b"blob " + str(len(data)).encode() + b"\0" + data
        import hashlib
        need(hashlib.sha1(blob).hexdigest() == item["git_blob"],
             "source Git blob mismatch")
    return manifest["base_commit"], len(manifest["files"])


def oracle(p, q, value):
    result = Fraction(p * value, q) + Fraction(1, 2)
    return result.numerator // result.denominator


def scalar_census():
    ratios = stable_tests = response_tests = average_tests = 0
    digest = sha256()
    for q in range(2, 25):
        for p in range(-2 * q, 2 * q + 1):
            if gcd(p, q) != 1:
                continue
            ratios += 1
            values = range(q)
            signatures = []
            for z in values:
                signatures.append(tuple(oracle(p, q, z + h) - oracle(p, q, z)
                                        for h in values))
            need(len(set(signatures)) == q, "residue classes not distinguished")
            for h in range(-2 * q, 2 * q + 1):
                differences = {oracle(p, q, z + h) - oracle(p, q, z)
                               for z in values}
                need((len(differences) == 1) == (h % q == 0),
                     "safe translation classification failed")
                stable_tests += 1
                for z in range(-2 * q, 2 * q + 1):
                    expected = oracle(p, q, z + h) - oracle(p, q, z)
                    observed = residue_response(p, q, p * z % q, h)
                    need(observed == expected, "saved residue response failed")
                    response_tests += 1
            for z in range(-q, q + 1):
                need(offset_sum(p, q, z) == p * z, "offset identity failed")
                average_tests += 1
            digest.update(canonical([p, q, signatures]))
    return {"denominators": [2, 24], "numerator_rule": "-2q<=p<=2q; gcd(p,q)=1",
            "ratios": ratios, "translation_tests": stable_tests,
            "residue_response_tests": response_tests,
            "offset_identity_tests": average_tests,
            "signature_sha256": digest.hexdigest()}


def matrix_census():
    cases = []
    # These matrices include singular maps, nonprime moduli, and shared residues.
    fixtures = [([[1, 0], [0, 1]], 2), ([[2, 0], [0, 2]], 4),
                ([[1, 1], [2, 2]], 4), ([[2, 3], [4, 0]], 6),
                ([[1, 2, 3], [0, 1, 1]], 4), ([[0, 0]], 5)]
    for matrix, q in fixtures:
        d = len(matrix[0])
        domain = list(product(range(q), repeat=d))

        def image(z):
            return tuple(sum(a * b for a, b in zip(row, z)) for row in matrix)

        def value(z):
            return tuple(oracle(1, q, coordinate) for coordinate in image(z))

        residues = {tuple(v % q for v in image(z)) for z in domain}
        signatures = set()
        stable_count = 0
        for h in domain:
            differences = set()
            for z in domain:
                shifted = tuple(a + b for a, b in zip(z, h))
                differences.add(tuple(a - b for a, b in zip(value(shifted), value(z))))
            safe = all(v % q == 0 for v in image(h))
            need((len(differences) == 1) == safe, "matrix safe lattice failed")
            stable_count += safe
        for z in domain:
            signature = []
            for h in domain:
                shifted = tuple(a + b for a, b in zip(z, h))
                signature.append(tuple(a - b for a, b in zip(value(shifted), value(z))))
            signatures.add(tuple(signature))
        need(len(signatures) == len(residues), "matrix response state count failed")
        need(len(residues) * stable_count == len(domain), "matrix quotient count failed")
        cases.append({"matrix": matrix, "q": q, "domain": len(domain),
                      "safe_residues": stable_count, "response_classes": len(signatures)})
    return cases


def joint_census():
    cases = []
    for ratios in [((1, 2), (1, 3)), ((2, 3), (4, 9)), ((4, 3), (8, 7))]:
        period = 1
        for _, q in ratios:
            period = period * q // gcd(period, q)
        signatures = {
            tuple(oracle(p, q, z + h) - oracle(p, q, z)
                  for p, q in ratios for h in range(period))
            for z in range(period)
        }
        need(len(signatures) == period, "joint residual state count failed")
        cases.append({"ratios": ratios, "classes_per_coordinate": len(signatures)})
    return cases


def borrowed_probe(borrow):
    # F is any normalized function on Z/qZ. Enumerate every such function.
    cases = []
    tree = (0, ((1, 2), 3))
    root_word = list(borrow.instructions(tree))
    child_calls = borrow.resources(tree[1])[1]
    word = root_word[1:1 + child_calls]
    need(child_calls == 10, "borrowed child boundary has changed")
    for q in range(2, 6):
        functions = additive_count = restored_count = boundaries = 0
        for tail in product(range(q), repeat=q - 1):
            f = (0,) + tail
            additive = all(f[(a + b) % q] == (f[a] + f[b]) % q
                           for a in range(q) for b in range(q))
            restored = True
            for x, y, z in product(range(q), repeat=3):
                # Execute the ten primitive calls with identity neighbors.
                state = [0, y, x, z, 0]
                for s, t, factor, sign in word:
                    increment = f[state[s]] if factor == 2 else state[s]
                    state[t] = (state[t] + sign * increment) % q
                restored &= state[3] == z
                boundaries += 1
            need(restored == additive, "borrowed boundary equivalence failed")
            functions += 1
            additive_count += additive
            restored_count += restored
        need(additive_count == q, "cyclic endomorphism count failed")
        cases.append({"group_order": q, "normalized_functions": functions,
                      "additive": additive_count, "restoring": restored_count,
                      "boundary_states": boundaries})
    return cases


def finite_accuracy():
    rows = []
    for width in range(0, 9):
        scale = 1 << width
        errors = []
        for slope in range(-2, 5):
            error = max(abs(Fraction(slope * n, scale) - Fraction(4 * n, 3 * scale))
                        for n in range(-scale, scale + 1))
            errors.append(error)
        need(min(errors) == Fraction(1, 3), "physical unit-range gap failed")
        rounded_error = max(abs(Fraction(oracle(4, 3, n), scale)
                                - Fraction(4 * n, 3 * scale))
                            for n in range(-scale, scale + 1))
        need(rounded_error == Fraction(1, 3 * scale), "rounded error scale failed")
        rows.append({"width": width, "source_points": 2 * scale + 1,
                     "best_additive_error": str(min(errors)),
                     "rounded_error": str(rounded_error)})
    return rows


def pinned_execution(borrow, dirty):
    width = 12
    unit = Fraction(1, 1 << width)
    beta = Fraction(1, 2)
    factors = []
    executions = 0
    for numerator, expected in ((1, 1), (-1, 0), (3, 2), (-3, -1)):
        need(dirty.rnd((Fraction(numerator, 2) * unit, Fraction(0)), width)
             == (expected * unit, Fraction(0)), "PR985 data tie convention failed")
    for bits in range(2, 9):
        p, q = 1 << bits, (1 << bits) - 1
        b = (Fraction(1, p), Fraction(0))
        for z in (-q - 1, -q, -1, 0, 1, q - 1, q, q + 1):
            for target in (-7, 0, 5):
                x = [(z * unit, Fraction(0))]
                y = [(target * unit, Fraction(0))]
                original_x, original_y = list(x), list(y)
                meter = dirty.lift(x, y, b, beta, width, 0)
                need(x == original_x, "PR985 diagonal source changed")
                need(y[0] == ((target + oracle(p, q, z)) * unit, Fraction(0)),
                     "PR985 diagonal differs from nearest rational map")
                dirty.lift(x, y, b, beta, width, 0, sign=-1)
                need(x == original_x and y == original_y, "PR985 inverse failed")
                executions += 2
        factors.append({"coefficient_bits": bits, "p": p, "q": q,
                        "residue_states_per_coordinate": q})
    tree = (0, ((1, 2), 3))
    word = list(borrow.instructions(tree))
    initial = [-2, -2, -2, 1, -2]
    arrays = [[(v * unit, Fraction(0))] for v in initial]
    counters = {"reads": 0, "writes": 0, "tape_moves": 0,
                "products": 0, "divisions": 0}

    def execute(records):
        nonlocal executions
        for s, t, factor, sign in records:
            meter = dirty.lift(arrays[s], arrays[t], (Fraction(1, 4), Fraction(0)),
                               beta, width, 0, sign=sign)
            for key in counters:
                counters[key] += getattr(meter, key)
            executions += 1

    execute(word)
    final = [int(row[0][0] / unit) for row in arrays]
    need(final == [-2, -10, -2, 2, -2], "rounded borrowed boundary fixture changed")
    need(final[2:] != initial[2:], "rounded helper failure was not observed")
    execute(inverse(word))
    need([row[0][0] / unit for row in arrays] == initial,
         "literal inverse did not restore the complete rounded state")
    return {"width": width, "diagonal_families": factors, "leaf_executions": executions,
            "borrowed_tree": tree, "borrowed_calls": len(word), "initial_units": initial,
            "final_units": final, "literal_inverse_units": initial,
            "borrowed_forward_and_inverse_meter": counters}


def lift_census(borrow):
    rows = []
    _, plans, _ = borrow.unit_plan(16)
    for n in (2, 3, 4, 5, 8, 16):
        for tree in dict.fromkeys((plans[n - 1], borrow.balanced_binary(n))):
            word = list(borrow.instructions(tree))
            degree = prefix_degree(word, 5)
            for length in (1, 3):
                initial = [[(r + 2) * (j + 1) - 5 for j in range(length)] for r in range(5)]
                state, denominator, count = exact_lift(word, initial, 4, 3, degree)
                expected = [[Fraction(value) for value in row] for row in initial]
                for j in range(length):
                    expected[1][j] += Fraction(4, 3) ** n * initial[0][j]
                need([[Fraction(v, denominator) for v in row] for row in state] == expected,
                     "finite exact lift or helper restoration failed")
                need(count["exact_divisions"] == len(word) * length,
                     "finite lift division bill failed")
                need(denominator % (3 ** n) == 0, "endpoint denominator was not paid")
                need(count["source_reads"] == count["target_reads"] == count["writes"]
                     == len(word) * length, "finite lift access bill failed")
                # The independent rational oracle checks every literal prefix.
                rational = [[Fraction(v) for v in row] for row in initial]
                integer = [[v * denominator for v in row] for row in initial]
                peak = max(abs(v) for row in integer for v in row)
                for s, t, factor, sign in word:
                    for j in range(length):
                        rational[t][j] += sign * Fraction(4, 3) * rational[s][j]
                        numerator = 4 * integer[s][j]
                        need(numerator % 3 == 0, "oracle found an inexact division")
                        integer[t][j] += sign * (numerator // 3)
                        need(Fraction(integer[t][j], denominator) == rational[t][j],
                             "exact lift prefix differs from rational oracle")
                        peak = max(peak, abs(numerator), abs(integer[t][j]))
                need(count["peak_signed_bits"] == peak.bit_length() + 1,
                     "finite lift peak width failed")
                magnitude = max(abs(v) for row in initial for v in row)
                prefix_bound = borrow.norm_bound(tree, 2)
                bit_bound = (4 * magnitude * prefix_bound * denominator).bit_length() + 1
                need(count["peak_signed_bits"] <= bit_bound,
                     "finite lift exceeds its stated signed width")
                round_trip, _, round_trip_count = exact_lift(
                    word + inverse(word), initial, 4, 3, degree)
                need(round_trip == [[v * denominator for v in row] for row in initial],
                     "integer inverse did not restore every extended array")
                need(round_trip_count["exact_divisions"] == 2 * len(word) * length,
                     "integer inverse work was not paid")
                for s, t, factor, sign in inverse(word):
                    for j in range(length):
                        rational[t][j] += sign * Fraction(4, 3) * rational[s][j]
                need(rational == initial, "finite lift literal inverse failed")
                rows.append({"factors": n, "tree": tree, "length": length,
                             "calls": len(word), "maximum_prefix_degree": degree,
                             "denominator": str(denominator), "signed_width_bound": bit_bound,
                             "round_trip_divisions": round_trip_count["exact_divisions"],
                             "invoice": count})
    return rows


def controls(borrow):
    labels = []
    need(nearest(1, 2) == 1 and nearest(-1, 2) == 0,
         "nearest tie convention failed")
    need(round(Fraction(1, 2)) != nearest(1, 2), "nearest-even control is ineffective")
    labels.append("nearest_even_is_not_the_data_rounder")
    need(int(Fraction(2, 3)) != nearest(2, 3), "truncation control is ineffective")
    labels.append("coefficient_truncation_is_not_data_rounding")
    need(residue_response(4, 3, 0, 1) != residue_response(4, 3, 1, 1),
         "discarded residue control is ineffective")
    labels.append("discarded_residue_changes_a_required_response")
    need(nearest(8, 3) != 2 * nearest(4, 3), "additive wrapper defect not detected")
    labels.append("nearest_source_increment_is_not_additive")
    need(nearest(4 * 3, 3) == 4 and nearest(4, 3) * 3 == 3,
         "constant first difference control is ineffective")
    labels.append("full_period_refutes_constant_first_differences")
    need(offset_sum(4, 3, 1) != nearest(4, 3), "averaging scaling control is ineffective")
    labels.append("offset_averaging_returns_the_scaled_integer_map")
    # Reaccess defeats the summary restriction, with no saved residue.
    for z in range(-12, 13):
        for h in range(-12, 13):
            current = z + h
            recovered = current - h
            need(nearest(4 * current, 3) - nearest(4 * recovered, 3)
                 == oracle(4, 3, z + h) - oracle(4, 3, z),
                 "zero-summary reaccess escape failed")
    labels.append("readable_current_and_shift_allow_zero_summary")
    word = list(borrow.instructions((0, ((1, 2), 3))))
    initial = [[1], [2], [3], [4], [5]]
    try:
        exact_lift(word, initial, 4, 3, 0)
    except ValueError as error:
        need(str(error) == "exact lift needs more denominator precision",
             "wrong failure for omitted precision extension")
    else:
        raise ValueError("omitted precision extension was accepted")
    labels.append("zero_precision_extension_rejects_inexact_division")
    # A coarser source grid and a finer target grid admit the exact ratio.
    for z in range(-20, 21):
        physical_source = Fraction(z)
        target_units = 4 * z
        need(Fraction(target_units, 3) == Fraction(4, 3) * physical_source,
             "different-grid escape failed")
    labels.append("different_input_and_output_grids_escape_integer_slope")
    return labels


def compute():
    base, pins = sources()
    borrow = load_module("pinned_borrow", ROOT / "vendor/pr1057/borrow.py")
    dirty = load_module("pinned_dirty", ROOT / "vendor/pr985/dirty_stride.py")
    selected = {}
    for label in ("base", "refresh"):
        context = json.loads((ROOT / "context" / (label + "-selected-result.json")).read_text())
        selected[label] = {"kappa": context["kappa"], "primary_pr": context["source_prs"][0]}
    return {"format": 1, "base_commit": base, "pinned_files": pins,
            "selected_context": selected,
            "scalar_census": scalar_census(), "matrix_census": matrix_census(),
            "joint_census": joint_census(), "borrowed_probe": borrowed_probe(borrow),
            "physical_accuracy": finite_accuracy(),
            "pinned_execution": pinned_execution(borrow, dirty),
            "finite_exact_lifts": lift_census(borrow), "controls": controls(borrow)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="write a fresh receipt to a path that does not exist")
    args = parser.parse_args()
    if args.output and args.output.exists():
        raise FileExistsError("receipt path already exists")
    result = compute()
    expected = json.loads((ROOT / "EXPECTED.json").read_text())
    need(canonical(result) == canonical(expected), "complete receipt differs from EXPECTED.json")
    if args.output:
        with args.output.open("x") as stream:
            json.dump(result, stream, indent=2, sort_keys=True)
            stream.write("\n")
    print("PASS_ROUNDED_BORROWING_CONTRACT "
          f"ratios={result['scalar_census']['ratios']} "
          f"responses={result['scalar_census']['residue_response_tests']} "
          f"rounded_leaves={result['pinned_execution']['leaf_executions']} "
          f"exact_lifts={len(result['finite_exact_lifts'])} "
          f"controls={len(result['controls'])}")


if __name__ == "__main__":
    main()
