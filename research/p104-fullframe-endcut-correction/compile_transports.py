#!/usr/bin/env python3
"""Compile and exactly check the 208 added P104 target-frame transports."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
WITNESS = ROOT / "research/p104-native-channel/inputs/LOWRANK-WITNESS.json"
RECIPES = ROOT / "research/p104-native-channel/NATIVE-RECIPES.json.gz"
COMPILER = ROOT / "research/p104-native-channel/vendor/clifford_exact.py"
INTERPRETER = ROOT / "research/p104-native-channel/vendor/native_verify.py"
CHANNEL_COMPILER = ROOT / "research/p104-native-channel/compile.py"
SOURCE_MANIFEST = json.loads((PACKAGE / "SOURCES.json").read_text())

PINS = {
    WITNESS: "0f541bef7f19fdeffd67157684e9f03d785f42c89973632f508fc1a0452b580e",
    RECIPES: "a1c4d83d3d5fe1338e99b59272e8cf5d43244c33888597da340b2aa7fef5b3e8",
    COMPILER: "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962",
    INTERPRETER: "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38",
    CHANNEL_COMPILER: "9d2fc2d81962ddb0b4dd7d6482d9918a87a6b05759690317dea79939ca5656a3",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact_array_document(document: dict, array_key: str) -> str:
    items = sorted(document.items())
    lines = ["{"]
    for index, (key, value) in enumerate(items):
        comma = "," if index < len(items) - 1 else ""
        if key == array_key:
            lines.append(f"  {json.dumps(key)}: [")
            for row_index, row in enumerate(value):
                row_comma = "," if row_index < len(value) - 1 else ""
                lines.append("    " + json.dumps(
                    row, sort_keys=True, separators=(",", ":")
                ) + row_comma)
            lines.append("  ]" + comma)
        else:
            lines.append("  " + json.dumps(key) + ": " + json.dumps(
                value, sort_keys=True, separators=(",", ":")
            ) + comma)
    lines.append("}")
    return "\n".join(lines) + "\n"


def module_at(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def run() -> dict:
    for path, expected in PINS.items():
        require(path.is_file(), f"Missing pinned input: {path.relative_to(ROOT)}")
        require(sha256(path) == expected, f"Input hash mismatch: {path.relative_to(ROOT)}")

    compiler = module_at(COMPILER, "p104_endcut_clifford_exact")
    interpreter = module_at(INTERPRETER, "p104_endcut_native_verify")
    with gzip.open(RECIPES, "rt") as stream:
        native_data = json.load(stream)
    require(native_data["source_compiler_sha256"] == sha256(COMPILER),
            "Retained label isometry has a different compiler pin")
    require(native_data["source_native_checker_sha256"] == sha256(INTERPRETER),
            "Retained label isometry has a different native checker pin")

    iso = native_data["label_isometry"]
    dual = tuple(iso["compressed_dual_gram"])
    orthogonal = tuple(iso["orthonormal_basis_compressed"])

    def mv(matrix: tuple[int, ...], value: int) -> int:
        return sum(((row & value).bit_count() & 1) << i
                   for i, row in enumerate(matrix))

    def pairing(a: int, b: int) -> int:
        return (a & mv(dual, b)).bit_count() & 1

    def physical_label(value: int) -> int:
        return sum(pairing(value, basis) << i for i, basis in enumerate(orthogonal))

    def canonical(values: list[int]) -> tuple[int, ...]:
        pivots: dict[int, int] = {}
        for value in values:
            reduced = value
            while reduced:
                pivot = reduced.bit_length() - 1
                if pivot in pivots:
                    reduced ^= pivots[pivot]
                else:
                    pivots[pivot] = reduced
                    break
        for pivot in sorted(pivots):
            for other in pivots:
                if other > pivot and (pivots[other] >> pivot) & 1:
                    pivots[other] ^= pivots[pivot]
        return tuple(pivots[pivot] for pivot in sorted(pivots, reverse=True))

    witness = json.loads(WITNESS.read_text())
    full = tuple(1 << i for i in range(9))
    full_chart = compiler.canonical_frame(9, full)
    full_expected = interpreter.frame(full, 9)
    records = []

    for target in range(104):
        compressed = witness["final_frames"][f"Y{target}"]
        require(len(compressed) == 8, f"Target Y{target} frame is not dimension eight")
        physical = canonical([physical_label(value) for value in compressed])
        require(len(physical) == 8, f"Physical Y{target} frame rank changed")
        target_chart = compiler.canonical_frame(9, physical)
        target_expected = interpreter.frame(physical, 9)

        directions = (
            ("raise", target_chart, full_chart, physical, full),
            ("lower", full_chart, target_chart, full, physical),
        )
        for direction, old_chart, new_chart, old_frame, new_frame in directions:
            actual = old_chart.adjoint().then(new_chart)
            record, _compiled = compiler.lower_child(actual)
            require(record["rank"] == 1,
                    f"Y{target} {direction} transport is not an H1")
            expected = interpreter.adjoint(
                target_expected if direction == "raise" else full_expected
            ) + (full_expected if direction == "raise" else target_expected)
            interpreter.equal(
                interpreter.recipe(record), expected,
                f"Y{target} {direction} exact native transport",
            )
            records.append({
                "target": target,
                "direction": direction,
                "old_frame": list(old_frame),
                "new_frame": list(new_frame),
                "rank": record["rank"],
                "recipe": record,
            })

    require(len(records) == 208, "Expected two exact transports per target")
    document = {
        "format": "p104-fullframe-endcut-native-transports/v1",
        "base_commit": SOURCE_MANIFEST["base_commit"],
        "input_sha256": {str(path.relative_to(ROOT)): digest for path, digest in PINS.items()},
        "label_isometry_source": "retained and natively verified PR #1991 recipe package",
        "records": records,
    }
    output_path = PACKAGE / "TRANSPORTS.json"
    if output_path.exists() and output_path.stat().st_size:
        retained = json.loads(output_path.read_text())
        if retained != document:
            retained_header = {key: value for key, value in retained.items()
                               if key != "records"}
            generated_header = {key: value for key, value in document.items()
                                if key != "records"}
            require(retained_header == generated_header,
                    "Retained TRANSPORTS.json source/header pins changed")
            require(len(retained.get("records", [])) == len(records),
                    "Retained TRANSPORTS.json record count changed")
            for index, (candidate, generated) in enumerate(
                    zip(retained["records"], records)):
                for key in ("target", "direction", "old_frame", "new_frame", "rank"):
                    require(candidate.get(key) == generated[key],
                            f"Retained transport metadata changed at record {index}")
                old_frame = tuple(candidate["old_frame"])
                new_frame = tuple(candidate["new_frame"])
                expected = interpreter.adjoint(interpreter.frame(old_frame, 9))
                expected += interpreter.frame(new_frame, 9)
                interpreter.equal(
                    interpreter.recipe(candidate["recipe"]), expected,
                    f"Retained exact transport record {index}",
                )
    return {
        "status": "PASS_P104_FULLFRAME_ENDCUT_NATIVE_TRANSPORTS",
        "targets": 104,
        "exact_native_transports": len(records),
        "rank_histogram": {"1": len(records)},
        "all_signed_pauli_actions_and_global_phases_checked": True,
        "transport_sha256": hashlib.sha256(
            json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest(),
    }, document


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-transports", action="store_true")
    args = parser.parse_args()
    try:
        summary, document = run()
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"FAIL_P104_FULLFRAME_ENDCUT_NATIVE_TRANSPORTS: {error}", file=sys.stderr)
        return 1
    if args.emit_transports:
        sys.stdout.write(compact_array_document(document, "records"))
    else:
        print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
