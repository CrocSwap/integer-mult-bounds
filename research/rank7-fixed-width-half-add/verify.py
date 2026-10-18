# SPDX-License-Identifier: Apache-2.0
"""Emit, read back and audit bounded fixed-width caller circuits."""

import argparse
import json
import tempfile
from dataclasses import asdict
from pathlib import Path

import audit
from kernel import build, check, invoice, require
from sources import (
    PACKAGE,
    SOURCE_COMMIT,
    authenticate,
    canonical,
    digest,
    inventory,
    read,
)

WIDTHS = (4, 5, 6, 7, 8, 16, 32, 64, 128, 256)


def fixtures(width: int, shift: int, sign: int) -> tuple[tuple[int, int], ...]:
    low, high = -(1 << (width - 1)), (1 << (width - 1)) - 1
    unit = 1 << shift
    sources = {low, low + unit, -unit, 0, unit, high - high % unit}
    result = set()
    for source in sorted(sources):
        if not low <= source <= high:
            continue
        delta = sign * (source // unit)
        for target in (
            low,
            low + 1,
            -1,
            0,
            1,
            high - 1,
            high,
            low - delta,
            high - delta,
        ):
            if low <= target <= high and low <= target + delta <= high:
                result.add((source, target))
    require(len(result) <= 54, "bounded boundary fixtures")
    return tuple(sorted(result))


def emit(circuit, work: Path):
    document = asdict(circuit) | {"wires": circuit.wires}
    payload = canonical(document)
    path = (
        work
        / f"w{circuit.width}-k{circuit.shift}-s{circuit.sign}-{circuit.policy}.json"
    )
    require(path.write_bytes(payload) == len(payload), "complete circuit write")
    restored = read(path)
    require(canonical(restored) == payload, "serialized gate bytes")
    return audit.parse(restored), digest(restored)


def check_program(circuit, program) -> int:
    width, shift, sign = circuit.width, circuit.shift, circuit.sign
    cases = 0
    if width <= 7:
        limit = 1 << (width - 1)
        for source in range(-limit, limit, 1 << shift):
            for target in range(-limit, limit):
                if -limit <= target + sign * (source >> shift) < limit:
                    check(circuit, source, target)
                    audit.check(program, source, target)
                    cases += 1
    else:
        for source, target in fixtures(width, shift, sign):
            check(circuit, source, target)
            audit.check(program, source, target)
            cases += 1
    return cases


def compare(circuits: dict) -> None:
    baseline, rotated, wired = (
        invoice(circuits[p]) for p in ("scratch", "source", "wired")
    )
    width, shift = circuits["wired"].width, circuits["wired"].shift
    require(rotated["cx"] - wired["cx"] == 6 * shift * (width - 1), "paid shift saving")
    require(
        baseline["cx"] - wired["cx"] == 2 * width + 6 * shift * (width - 1),
        "complete scratch saving",
    )
    require(baseline["ccx"] == wired["ccx"] == rotated["ccx"], "unchanged CCX")
    require(
        baseline["clean_bits"] - wired["clean_bits"] == width, "scratch bank eliminated"
    )
    require(
        rotated["total_bits"] == wired["total_bits"],
        "no extra guard or workspace allocation",
    )


def verify(work: Path) -> dict:
    pins = authenticate()
    require(not work.exists(), "fresh output directory")
    work.mkdir()
    results = []
    for width in WIDTHS:
        for shift in (1, 2, 3):
            for sign in (-1, 1):
                circuits = {
                    policy: build(width, shift, sign, policy)
                    for policy in ("scratch", "source", "wired")
                }
                compare(circuits)
                for policy, circuit in circuits.items():
                    program, sha256 = emit(circuit, work)
                    cases = check_program(circuit, program)
                    results.append(
                        {
                            "width": width,
                            "shift": shift,
                            "sign": sign,
                            "policy": policy,
                            "invoice": invoice(circuit),
                            "program_sha256": sha256,
                            "signed_cases_both_interpreters": cases,
                        }
                    )
    providers = {
        name: inventory(read(PACKAGE / f"vendor/WORD-{name}.json.gz"))
        for name in ("base", "extra")
    }
    require(
        providers["base"] == providers["extra"], "same candidate scalar occurrences"
    )
    return {
        "status": "PASS_FIXED_WIDTH_DYADIC_ADD_LOCAL_CALLER",
        "source_commit": SOURCE_COMMIT,
        "source_pins": pins,
        "emitted_programs": len(results),
        "signed_cases_both_interpreters": sum(
            x["signed_cases_both_interpreters"] for x in results
        ),
        "programs": results,
        "candidate_word_inventory": providers,
        "scope": "direct CX/CCX gates; caller guards required; no adoption or kappa",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--work", type=Path, help="fresh external directory; preserves emitted gates"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare the committed deterministic receipt",
    )
    arguments = parser.parse_args()
    if arguments.work is None:
        with tempfile.TemporaryDirectory(prefix="half-add-") as directory:
            result = verify(Path(directory) / "programs")
    else:
        result = verify(arguments.work)
    if arguments.check:
        require(result == read(PACKAGE / "evidence/RESULT.json"), "reproduced receipt")
        print(result["status"])
    else:
        print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
