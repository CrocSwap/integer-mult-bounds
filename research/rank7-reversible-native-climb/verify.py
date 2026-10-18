# SPDX-License-Identifier: Apache-2.0
"""Rebuild the reached native boundary and execute its reversible bit circuits."""

import argparse
import hashlib
import importlib
import itertools
import json
import tempfile
from fractions import Fraction as Q
from pathlib import Path

import binding

predecessor, caller = binding.sources()
circuits = importlib.import_module("circuits")

PACKAGE = Path(__file__).resolve().parent
require = circuits.require


def expected_pair(values, sign):
    a, b, c, d = values
    numerators = (
        a - sign * b + c + sign * d,
        sign * a + b - sign * c + d,
        a + sign * b + c - sign * d,
        -sign * a + b + sign * c + d,
    )
    require(all(v % 2 == 0 for v in numerators), "integral C endpoint")
    return tuple(v // 2 for v in numerators)


def pair_proof():
    reports = {}
    for sign in (-1, 1):
        expected = [
            [Q(v, 2) for v in row]
            for row in (
                (1, -sign, 1, sign),
                (sign, 1, -sign, 1),
                (1, sign, 1, -sign),
                (-sign, 1, sign, 1),
            )
        ]
        for control in (False, True):
            endpoint, trace = circuits.rational_lift(sign, control)
            require(endpoint == expected, "exact independent C formula")
            require(
                max(sum(map(abs, r)) for rows in trace for r in rows) == 2,
                "two-input-unit maximum at every lifting microstate",
            )
            require(
                max(q.denominator for rows in trace for r in rows for q in r) == 2,
                "one additional grid bit at most",
            )
        for width in (3, 8, 69, 133, 256):
            direct = circuits.tariff(circuits.lift(sign), width)
            control = circuits.tariff(circuits.lift(sign, True), width)
            require(
                direct == {"cx": 40 * width - 47, "ccx": 34 * width - 52},
                "literal direct C tariff",
            )
            require(
                control["cx"] - direct["cx"] == 12 * width - 8
                and control["ccx"] == direct["ccx"],
                "strict shift-elimination saving",
            )
        reports[str(sign)] = {
            "rows": [[str(q) for q in row] for row in expected],
            "max_microstate_l1": 2,
            "max_denominator": 2,
        }
    return reports


def truth_columns(cases, width):
    require(len(cases) <= circuits.MAX_TRUTH_COLUMNS, "bounded exhaustive truth domain")
    buffers = [bytearray((len(cases) + 7) // 8) for _ in range(4 * width)]
    for column, values in enumerate(cases):
        for bank, value in enumerate(values):
            for bit in range(width):
                buffers[bank * width + bit][column // 8] |= ((value >> bit) & 1) << (
                    column % 8
                )
    return [int.from_bytes(v, "little") for v in buffers] + [0] * (width - 1)


def exhaustive():
    reports = {}
    for width in range(3, 7):
        limit = 1 << (width - 1)
        cases = [
            v
            for v in itertools.product(range(-limit // 2, limit // 2), repeat=4)
            if (v[0] - v[2]) % 2 == (v[1] - v[3]) % 2 == 0
        ]
        original = truth_columns(cases, width)
        for sign in (-1, 1):
            expected = truth_columns([expected_pair(v, sign) for v in cases], width)
            for control in (False, True):
                gates = circuits.pair_gates(width, sign, control)
                observed = circuits.packed(gates, original, width)
                require(
                    observed == expected,
                    "exhaustive literal C endpoint and carry return",
                )
                require(
                    circuits.packed(list(reversed(gates)), observed, width) == original,
                    "literal inverse and clean return on the reachable image",
                )
        reports[str(width)] = len(cases)
    return reports


def raw_fixtures(precision):
    limit = 1 << (precision - 1)
    result = {"zero": [0] * 5120, "grid": [0] * 5120}
    result["grid"][4096] = 1
    result["dense"] = [
        int.from_bytes(hashlib.sha256(str(i).encode()).digest(), "little") % (2 * limit)
        - limit
        for i in range(5120)
    ]
    result["alternating"] = [limit - 1 if i % 3 else -limit for i in range(5120)]
    retained = json.loads((binding.PRIOR / "RESULT.json").read_text())
    witnesses = retained["providers"]["base"]["boundary"]["witnesses"]
    for side in ("low", "high"):
        raw = [0] * 5120
        for atom, value in witnesses[side]["assignment"]:
            raw[atom] = -limit if value < 0 else limit - 1
        result[side] = raw
    return result


def execute_fixtures(program, control, operators):
    reports = {}
    for precision in (3, 64, 128):
        width = precision + 5
        checked = {}
        for name, raw in raw_fixtures(precision).items():
            before, expected = binding.fixture(raw, operators)
            after = circuits.run(before, program, width)
            require(
                after == expected, "complete native boundary versus Gaussian operator"
            )
            require(
                circuits.run(
                    before, control, width, bits=precision == 64 and name == "dense"
                )
                == expected,
                "physical-shift control endpoint",
            )
            if precision == 64 and name == "dense":
                inverse = [
                    ((g[0], g[1], g[2], -g[3], g[4]) if g[0] == "add" else g)
                    for g in reversed(program)
                ]
                require(
                    circuits.run(after, inverse, width) == before,
                    "complete literal native inverse and clean return",
                )
            checked[name] = binding.digest(after)
            if name in ("low", "high"):
                try:
                    circuits.run(before, program, width - 1, bits=False)
                except ValueError as error:
                    require("signed" in str(error), "smaller-format rejection reason")
                else:
                    raise ValueError("undersized reached boundary accepted")
        reports[str(precision)] = checked
    return reports


def tariff_report(program, control):
    reports = {}
    for width in (8, 69, 133):
        direct = circuits.tariff(program, width)
        baseline = circuits.tariff(control, width)
        saving = {g: baseline[g] - direct[g] for g in ("cx", "ccx")}
        require(
            saving == {"cx": 256 * (12 * width - 8), "ccx": 0},
            "complete-boundary saving with both monomials and ADD charged",
        )
        reports[str(width)] = {
            "direct": direct,
            "physical_shift_control": baseline,
            "saving": saving,
            "data_bits": 2048 * width,
            "clean_carry_bits": width - 1,
            "scratch_fields": 0,
        }
    return reports


def run(work):
    pair = pair_proof()
    truth = exhaustive()
    bindings = binding.refresh(predecessor, work)
    columns = bindings["base"]["columns"]
    program, operators = binding.dispatch(predecessor, columns)
    control, other = binding.dispatch(predecessor, columns, True)
    require(operators == other, "same boundary in the constructed control")
    require(len(program) <= circuits.MAX_MACROS, "complete dispatch bound")
    fixtures = execute_fixtures(program, control, operators)
    tariffs = tariff_report(program, control)
    return {
        "status": "PASS_REVERSIBLE_A13_NATIVE_CLIMB_NO_NEW_KAPPA",
        "source_inputs": binding.authenticate(),
        "bindings": bindings,
        "grid_bits": 2,
        "signed_width": "P+5",
        "precision_domain": [3, 128],
        "pair_proof": pair,
        "exhaustive_columns_per_sign_and_implementation": truth,
        "dispatch_macros": len(program),
        "control_macros": len(control),
        "dispatch_sha256": binding.digest(program),
        "control_sha256": binding.digest(control),
        "pair_gates_69_sha256": binding.digest(circuits.pair_gates(69)),
        "complete_native_fixtures": fixtures,
        "complete_boundary_tariffs": tariffs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path)
    args = parser.parse_args()
    if args.work is not None:
        work = args.work.expanduser().resolve()
        require(
            not work.exists() and not work.is_relative_to(binding.ROOT),
            "fresh external work path",
        )
        work.mkdir(parents=True)
        result = run(work)
    else:
        with tempfile.TemporaryDirectory(
            prefix="reversible-native-climb-"
        ) as directory:
            result = run(Path(directory))
    expected = PACKAGE / "RESULT.json"
    if expected.exists():
        require(
            result == json.loads(expected.read_text()),
            "deterministic committed receipt",
        )
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
