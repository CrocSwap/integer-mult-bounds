#!/usr/bin/env python3
"""Replay two exact predecessor collisions and the strict comparison controls.

Arham Tahir, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import unittest

from adapter import check_sources, load_benchmark
from comparison import POLICY, comparison_key

HERE = Path(__file__).resolve().parent


def trailer(elapsed=b"0.000", count=b"1", noun=b"test", status=b"OK", nl=b"\n"):
    return b"-" * 70 + nl + b"Ran " + count + b" " + noun + b" in " + elapsed + b"s" + nl + nl + status + nl


def collision_evidence():
    legacy = load_benchmark(strict=False)
    pairs = {
        "diagnostic_elapsed_shape": (
            b"AssertionError: rank invoice in 1.000s\n" + trailer(status=b"FAILED (failures=1)"),
            b"AssertionError: rank invoice in 2.000s\n" + trailer(status=b"FAILED (failures=1)")),
        "replacement_decoding": (
            b"diagnostic byte: \xff\n" + trailer(),
            b"diagnostic byte: \xfe\n" + trailer()),
    }
    records = {}
    for name, (left, right) in pairs.items():
        if left == right or legacy.normalize(left) != legacy.normalize(right):
            raise ValueError("predecessor collision not reproduced: " + name)
        if comparison_key(left) == comparison_key(right):
            raise ValueError("strict key erased diagnostic difference: " + name)
        records[name] = {
            "left_hex": left.hex(), "right_hex": right.hex(),
            "legacy_key_sha256": sha256(legacy.normalize(left)).hexdigest(),
            "strict_left_key_sha256": sha256(comparison_key(left)).hexdigest(),
            "strict_right_key_sha256": sha256(comparison_key(right)).hexdigest(),
            "same_exit_code_and_stdout_can_hide_change": True,
        }
    return records


def evidence():
    # Real unittest captures and injected benchmark controls accompany byte
    # fixtures. Timing and temporary paths do not enter this stable receipt.
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.discover(str(HERE), pattern="test_comparison.py")
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise ValueError("comparison control failure:\n" + stream.getvalue())
    return {
        "status": "PASS_UNITTEST_RECEIPT_COMPARISON",
        "policy": POLICY,
        "source_sha256": check_sources(),
        "collisions": collision_evidence(),
        "tests_passed": result.testsRun,
        "scope": "Exact captured-byte comparison and bounded benchmark integration controls; no full repository benchmark, mathematical replay or new kappa.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", action="store_true")
    args = parser.parse_args()
    result = evidence()
    encoded = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    target = HERE / "RESULT.json"
    if args.write_result:
        with target.open("x", encoding="utf-8", newline="\n") as output:
            output.write(encoded)
    elif json.loads(target.read_bytes()) != result:
        raise ValueError("complete result receipt differs")
    print(result["status"] + " collisions=2 tests=" + str(result["tests_passed"]))


if __name__ == "__main__":
    main()
