#!/usr/bin/env python3
"""Reproduce the scoped grade-modulus audit; Python standard library only."""

import argparse
import hashlib
import json
from itertools import product
from math import gcd, lcm, prod
from pathlib import Path
import random
from types import ModuleType

import audit
import independent

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 74


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def check(condition, message):
    if not condition:
        raise RuntimeError(message)


def sources():
    pins = json.loads((HERE / "SOURCE.json").read_text())
    for name, expected in pins["files"].items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        check(actual == expected, f"source digest mismatch: {name}")
    path = ROOT / "research/graded-box-convolution/code/graded.py"
    # Preserve the predecessor's asserted obligations even under python -O.
    module = ModuleType("pinned_pr524")
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec", optimize=0), module.__dict__)
    return pins, module


def domains():
    exhaustive = [s for d in range(1, 7) for s in product((1, 2, 3), repeat=d)
                  if prod(s) <= 48]
    rng = random.Random(SEED)
    extended = set()
    # A fixed 74 accepted shapes; at most four active axes keeps N <= 81.
    while len(extended) < 74:
        d = rng.randrange(7, 13)
        shape = [1] * d
        for i in rng.sample(range(d), rng.randrange(2, 5)):
            shape[i] = rng.choice((2, 3))
        extended.add(tuple(shape))
    return exhaustive, sorted(extended)


def witness_check(shape, count):
    w = audit.witness(shape, count)
    strides = [prod(shape[:i]) for i in range(len(shape))]
    index = lambda a: sum(x * s for x, s in zip(a, strides))
    ia, ib, ic = [index(w[k]) for k in ("a", "b", "c")]
    check(ia + ib == ic < prod(shape), "witness does not have a below-N sum")
    # Independent carry calculation from remainders, not digit transitions.
    carries = [((ia % s) + (ib % s)) // s for s in strides[1:]]
    check(sum(carries) == count, "witness carry count differs from index oracle")
    check(all(0 <= x < n for key in ("a", "b", "c")
              for x, n in zip(w[key], shape)), "witness digit outside box")
    return w


def census_checks():
    exhaustive, extended = domains()
    rows = []
    pairs = aliases = modulus_cases = witnesses = below_n_once = 0
    for shape in exhaustive + extended:
        predicted = sorted(audit.count_witnesses(shape))
        check(predicted == list(independent.attainable_counts(shape)),
              f"attainable count mismatch: {shape}")
        for count in predicted:
            witness_check(shape, count)
            witnesses += 1
        least = audit.least_modulus(shape)
        active = sum(n > 1 for n in shape)
        check(least >= max(1, active), "prefix-residue lower bound failed")
        check(audit.admissible(shape, len(shape)), "inherited T=D is unsafe")
        results = []
        for modulus in range(1, len(shape) + 2):
            got = independent.census(shape, modulus)
            sound = audit.admissible(shape, modulus)
            check(sound == (got["accepted_invalid_pairs"] == 0),
                  f"modulus admission mismatch: {shape}, T={modulus}")
            pairs += got["below_n_pairs"]
            aliases += got["accepted_invalid_pairs"]
            modulus_cases += 1
            results.append([modulus, got["accepted_invalid_pairs"]])
        below_n_once += prod(shape) * (prod(shape) + 1) // 2
        rows.append({"shape": list(shape), "counts": predicted,
                     "least_modulus": least, "aliases_by_modulus": results})
    return {
        "exhaustive_shapes": len(exhaustive), "seeded_extended_shapes": len(extended),
        "seed": SEED, "modulus_cases": modulus_cases,
        "below_n_pairs_once_per_shape": below_n_once,
        "below_n_pair_modulus_checks": pairs, "accepted_invalid_pairs": aliases,
        "constructed_count_witnesses": witnesses, "all_rows_sha256": digest(rows),
        "domain": "All D=1..6, radices in {1,2,3}, N<=48; plus 74 seeded shapes, D=7..12, 2..4 active axes of radix 2 or 3; T=1..D+1.",
        "stopping_rule": "Complete fixed domain, no early stop or timed search.",
    }, rows


def direct_convolution(f, g, shape):
    coords = list(product(*(range(n) for n in shape)))
    lookup = {a: i for i, a in enumerate(coords)}
    result = [0] * len(coords)
    for i, a in enumerate(coords):
        for j, b in enumerate(coords):
            target = tuple(x + y for x, y in zip(a, b))
            if target in lookup:
                result[lookup[target]] += f[i] * g[j]
    return result


def convolution_checks(predecessor):
    shapes = [(1,), (1, 1, 1), (3,), (2, 1, 2), (2, 1, 1, 2),
              (2, 1, 2, 1, 1, 2), (2, 2, 2), (3, 2, 3)]
    rng = random.Random(SEED)
    rows = []
    cases = source_cases = 0
    for shape in shapes:
        size = prod(shape)
        inherited = predecessor.layout(shape)
        adapted = audit.layout(shape, len(shape))
        for key in ("coordinates", "indices", "grades", "slots", "outputs"):
            check(inherited[key] == adapted[key], f"inherited layout mismatch: {key}")
        least = audit.least_modulus(shape)
        moduli = sorted(set((least, len(shape))))
        vectors = [([1] * size, [-1] * size), ([0] * size, [5] * size),
                   ([(-1) ** i * (2 ** (i % 7) + 1) for i in range(size)],
                    [(-1) ** (i + 1) * (2 ** (i % 5)) for i in range(size)])]
        vectors += [([rng.randrange(-127, 128) for _ in range(size)],
                     [rng.randrange(-63, 64) for _ in range(size)]) for _ in range(4)]
        for f, g in vectors:
            expected = direct_convolution(f, g, shape)
            # The pinned source's operand-width assertion rejects some zero
            # operand cases (e.g. [0] * [5] in shape (1,)); see README.
            # Keep these in our adapter/oracle checks, separate from source replay.
            if any(f) and any(g):
                check(predecessor.apply(f, g, shape) == expected, "pinned PR524 differs")
                source_cases += 1
            for modulus in moduli:
                check(audit.convolve(f, g, shape, modulus) == expected,
                      "signed integer product differs from direct oracle")
                cases += 1
        # Bilinear basis-pair coverage for each audited adapter layout.
        for i in range(size):
            for j in range(size):
                f, g = [0] * size, [0] * size
                f[i] = g[j] = 1
                expected = direct_convolution(f, g, shape)
                for modulus in moduli:
                    check(audit.convolve(f, g, shape, modulus) == expected,
                          "basis-pair integer product differs")
                    cases += 1
        rows.append({"shape": list(shape), "moduli": moduli,
                     "least_modulus_product_slots": audit.layout(shape, least)["product_slots"],
                     "inherited_product_slots": adapted["product_slots"]})
    return {"adapter_convolutions": cases, "adapter_integer_products": 4 * cases,
            "pinned_source_convolutions": source_cases, "layouts": rows}


def source_zero_input_observation(predecessor):
    """A failed source assertion, distinct from the modulus counterexamples."""
    try:
        predecessor.apply([0], [5], (1,))
    except AssertionError:
        pass
    else:
        raise RuntimeError("pinned source zero-input observation changed")
    check(audit.convolve([0], [5], (1,), 1) == [0], "adapter zero product failed")
    check(direct_convolution([0], [5], (1,)) == [0], "oracle zero product failed")
    return {"shape": [1], "f": [0], "g": [5], "correct_output": [0],
            "source_result": "AssertionError at operand bit-length bound",
            "classification": "Failed source assertion, not a counterexample to the convolution identity. Predecessor loaded with assertions enabled in all audit modes; source remains unchanged."}


def alias_control(name, shape, modulus, criterion):
    check(criterion, f"control's deliberately wrong criterion did not admit: {name}")
    report = independent.census(shape, modulus)
    bad = report["first_bad_alias"]
    check(bad is not None, f"control has no concrete alias: {name}")
    try:
        audit.convolve([1] * prod(shape), [1] * prod(shape), shape, modulus)
    except ValueError as exc:
        check(str(exc) == "inadmissible grade modulus", "wrong admission failure")
    else:
        raise RuntimeError(f"unsafe modulus accepted by adapter: {name}")
    coords = audit.layout(shape, modulus)["coordinates"]
    f, g = [0] * len(coords), [0] * len(coords)
    f[coords.index(tuple(bad["a"]))] = 1
    g[coords.index(tuple(bad["b"]))] = 1
    expected = direct_convolution(f, g, shape)
    wrong = audit.convolve(f, g, shape, modulus, admit=False)
    check(wrong != expected and not any(expected), "delta-input alias did not manifest")
    return {"name": name, "shape": list(shape), "modulus": modulus,
            "witness": bad, "wrong_output": wrong, "correct_output": expected}


def controls():
    results = [
        alias_control("active_axis_count_is_not_a_safe_modulus", (2, 1, 2), 2, True),
        alias_control("admissibility_is_not_monotone", (2, 1, 1, 2), 3,
                      audit.admissible((2, 1, 1, 2), 2)),
        alias_control("checking_only_maximum_count_is_insufficient", (2, 1, 2, 1, 1, 2), 2,
                      max(audit.count_witnesses((2, 1, 2, 1, 1, 2))) % 2 != 0),
        alias_control("coprimality_of_each_gap_is_insufficient", (2, 1, 1, 2, 1, 1, 2), 2,
                      gcd(3, 2) == 1),
        alias_control("distinct_prefix_residues_are_not_sufficient", (2, 1, 2, 1, 1, 2, 1, 2), 4,
                      len({x % 4 for x in (0, 2, 5, 7)}) == 4),
    ]
    for name, option in (("omitted_grade_wrap", "grade_wrap"),
                         ("omitted_index_padding", "index_padding"),
                         ("omitted_signed_cross_products", "signed_cross")):
        shape = (2, 3, 2)
        size = prod(shape)
        found = None
        for i, j in product(range(size), repeat=2):
            f, g = [0] * size, [0] * size
            f[i], g[j] = 1, -1
            expected = direct_convolution(f, g, shape)
            wrong = audit.convolve(f, g, shape, len(shape), **{option: False})
            if wrong != expected:
                found = {"name": name, "shape": list(shape), "basis_indices": [i, j],
                         "coefficients": [1, -1], "wrong_output": wrong,
                         "correct_output": expected}
                break
        check(found is not None, f"packing mutation escaped: {name}")
        results.append(found)
    return results


def run():
    pins, predecessor = sources()
    independent.self_check()
    census, rows = census_checks()
    examples = []
    for shape in ((1, 1), (1, 3, 1), (2, 1, 2), (2, 1, 1, 2),
                  (2, 1, 2, 1, 1, 2), (2, 2, 2, 2)):
        counts = sorted(audit.count_witnesses(shape))
        examples.append({"shape": list(shape), "counts": counts,
                         "admissible_through_D_plus_1": [t for t in range(1, len(shape) + 2)
                                                        if audit.admissible(shape, t)]})
    lcm_family = []
    for k in range(1, 13):
        gap = lcm(*range(1, k + 1))
        check(all(gap % t == 0 for t in range(1, k + 1)), "lcm family failed")
        # Symbolic two-active-axis shape, not an allocated huge coordinate table.
        lcm_family.append({"K": k, "active_axis_gap": gap, "dimension": gap + 1,
                           "excluded_moduli": list(range(1, k + 1))})
    result = {"status": "PASS_GRADED_MODULUS_AUDIT", "base_commit": pins["base_commit"],
              "source_pins_sha256": digest(pins), "census": census,
              "convolution": convolution_checks(predecessor), "controls": controls(),
              "source_zero_input_observation": source_zero_input_observation(predecessor),
              "examples": examples, "symbolic_lcm_family": lcm_family,
              "scope": "Exact unchanged-recurrence modulus criterion with a written all-shape proof and bounded independent replay. Original T=D remains correct. No kappa, tape-runtime, weighted Gaussian, selected-supplier, or formal theorem claim."}
    return result, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", type=Path, help="write a new receipt instead of comparing EXPECTED.json")
    parser.add_argument("--details", type=Path, help="write the complete per-shape census")
    args = parser.parse_args()
    result, rows = run()
    if args.write:
        with args.write.open("x") as handle:
            handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((HERE / "EXPECTED.json").read_text())
        check(result == expected, "deterministic receipt differs from EXPECTED.json")
    if args.details:
        with args.details.open("x") as handle:
            handle.write(json.dumps(rows, indent=2, sort_keys=True) + "\n")
    print(f"{result['status']}: {result['census']['exhaustive_shapes']} exhaustive + "
          f"{result['census']['seeded_extended_shapes']} seeded shapes; "
          f"{result['census']['modulus_cases']} modulus cases; "
          f"{len(result['controls'])} negative controls")


if __name__ == "__main__":
    main()
