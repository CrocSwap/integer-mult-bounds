#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Check the new adapter, not the predecessor's universal decoder theorem."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import replace
from fractions import Fraction as Q
from itertools import product
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
import replay as adapter
from replay import IntegerDot, MAX_CACHE_ROWS, SOURCE_HASHES, load_source


def need(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def equal_call(candidate, original, a, b) -> None:
    expected = original(a, b)
    actual = candidate(a, b)
    need(actual == expected and type(actual) is type(expected), "dot mismatch")


def arithmetic_controls(original) -> dict:
    candidate = IntegerDot(original)
    values = (-1, 0, Q(1, 2), Q(2, 3))
    vectors = [list(row) + [0, 1, -1, Q(3, 5)]
               for row in product(values, repeat=4)]
    cases = 0
    for a in vectors:
        for b in vectors:
            equal_call(candidate, original, a, b)
            cases += 1
    for width in range(10):
        equal_call(candidate, original, [Q(1, 7)] * width, [3] * width)
    for scalar in (True, 0.25, 2 + 3j):
        equal_call(candidate, original, [scalar] * 8, [1] * 8)
    return {"rational_pairs": cases, "fallback_widths": 10,
            "fallback_types": 3}


def cache_controls(original) -> dict:
    candidate = IntegerDot(original)
    a, b = [1] * 8, [2] * 8
    for changed in (9, Q(9), Q(1, 7), -3, 1):
        equal_call(candidate, original, a, b)
        a[0] = changed
        equal_call(candidate, original, a, b)
    for value in range(2 * MAX_CACHE_ROWS + 1):
        equal_call(candidate, original, [value] + [0] * 7, b)
        need(len(candidate.rows) <= MAX_CACHE_ROWS, "cache capacity")
    need(candidate.clears >= 2, "capacity control did not clear cache")
    before = candidate.calls
    equal_call(candidate, original, a, b)
    equal_call(candidate, original, a, b)
    need(candidate.calls == before + 2, "dot result was cached")
    return {"mutations": 5, "capacity_inputs": 2 * MAX_CACHE_ROWS + 1,
            "clears": candidate.clears}


def rejection_controls(original) -> int:
    rejected = 0
    candidate = IntegerDot(original)
    for a, b in (([1], [1, 2]), ([1] * 8, [1] * 7)):
        try:
            candidate(a, b)
        except RuntimeError as exc:
            need(str(exc) == "dot-product shape mismatch", "shape error changed")
            rejected += 1
        else:
            raise RuntimeError("bad shape accepted")
    for filename in SOURCE_HASHES:
        previous = SOURCE_HASHES[filename]
        try:
            SOURCE_HASHES[filename] = "0" * 64
            try:
                load_source()
            except ValueError as exc:
                need(str(exc) == "source hash mismatch: " + filename,
                     "wrong source rejection")
                rejected += 1
            else:
                raise RuntimeError("bad source pin accepted")
        finally:
            SOURCE_HASHES[filename] = previous
    a, b = [Q(1, 3)] * 8, [Q(2, 5)] * 8
    for field, bad in (("denominator", 1), ("numerators", (0,) * 8)):
        candidate = IntegerDot(original)
        candidate(a, b)
        candidate.rows[id(a)] = replace(candidate.rows[id(a)], **{field: bad})
        try:
            equal_call(candidate, original, a, b)
        except RuntimeError as exc:
            need(str(exc) == "dot mismatch", "wrong mutant rejection")
            rejected += 1
        else:
            raise RuntimeError("incorrect arithmetic accepted")
    return rejected + boundary_controls()


def boundary_controls() -> int:
    previous_limit, previous_argv = adapter.MAX_INPUT_BYTES, sys.argv
    rejected = 0
    try:
        adapter.MAX_INPUT_BYTES = 8
        try:
            load_source()
        except ValueError as exc:
            need(str(exc) == "source size limit: verify.py", "size boundary changed")
            rejected += 1
        else:
            raise RuntimeError("oversized source accepted")
        sys.argv = ["replay.py", "--write-certificate"]
        try:
            adapter.main()
        except ValueError as exc:
            need(str(exc) == "accelerated replay accepts no arguments", "CLI boundary changed")
            rejected += 1
        else:
            raise RuntimeError("writer option accepted")
    finally:
        adapter.MAX_INPUT_BYTES, sys.argv = previous_limit, previous_argv
    return rejected


def full_conformance() -> dict:
    baseline = load_source()
    expected = baseline.compute_certificate()
    candidate = load_source()
    original = candidate.dot
    integer_dot = IntegerDot(original)
    checked = 0

    def compare(a, b):
        nonlocal checked
        want, got = original(a, b), integer_dot(a, b)
        need(want == got and type(want) is type(got), "reached dot mismatch")
        checked += 1
        return got

    candidate.dot = compare
    actual = candidate.compute_certificate()
    need(actual == expected, "complete computed certificate differs")
    saved = json.loads(Path(candidate.__file__).with_name("certificate.json").read_text())
    candidate.compare_certificate(saved, actual)
    baseline.compare_certificate(saved, expected)
    need(checked == integer_dot.calls == 189904, "reached dot coverage changed")
    need(integer_dot.fallbacks == 0, "unexpected reached fallback")
    encoded = json.dumps(actual, sort_keys=True, separators=(",", ":")).encode()
    return {"checked_dot_calls": checked, "cache_hits": integer_dot.hits,
            "row_conversions": integer_dot.misses, "cache_clears": integer_dot.clears,
            "certificate_sha256": hashlib.sha256(encoded).hexdigest(),
            "inherited_controls": len(actual["negative_controls"]["rejected"]),
            "inherited_complex_controls": len(actual["negative_controls"]
                                               ["additional_complex_controls"])}


def receipt(result: dict, destination: Path) -> None:
    root = PACKAGE.parents[1]
    if destination.resolve().is_relative_to(root):
        raise ValueError("receipt must be outside the checkout")
    paths = [PACKAGE / name for name in ("README.md", "TASK.json", "SOURCES.json",
                                        "VERIFY.json", "replay.py", "verify.py",
                                        "benchmark.py")]
    paths += [root / "research/complex-paired26-completion" / name
              for name in sorted(SOURCE_HASHES)]
    hashes = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in paths}
    with destination.open("x", encoding="utf-8") as stream:
        json.dump({"result": result, "sha256": hashes}, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    original = load_source().dot
    result = {"arithmetic": arithmetic_controls(original),
              "cache": cache_controls(original),
              "rejecting_controls": rejection_controls(original),
              "full_conformance": full_conformance()}
    if args.receipt is not None:
        receipt(result, args.receipt)
    print("PASS_PAIRED26_INTEGER_DOT " + json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
