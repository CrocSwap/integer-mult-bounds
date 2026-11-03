#!/usr/bin/env python3
"""Finite conformance of the new Gray enumerator and its complete consumer.

Produced by Nick Petalas. Apache-2.0. PR3773's geometry/histogram remain
James Reed's results. This checks implementation equivalence, not novelty
or independent mathematical acceptance of those results.
"""

import argparse
from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
from io import StringIO
from itertools import product
import json
from pathlib import Path
import runpy
import tempfile

PACKAGE = Path(__file__).resolve().parent
REPLAY = runpy.run_path(str(PACKAGE / "replay.py"))
gray_counts = REPLAY["gray_counts"]
load_consumer = REPLAY["load_consumer"]
require = REPLAY["require"]
MARKER = "PASS_CORE_SECTION_CAPACITY pairs=3780 sections=127 no_new_kappa\n"


def direct_counts(coordinates, dimension):
    return tuple(sum((mask & value).bit_count() % 2 == 0
                     for value in coordinates)
                 for mask in range(1 << dimension))


def verify_small():
    cases = 0
    masks = 0
    for dimension in range(5):
        for size in range(4):
            for coordinates in product(range(1 << dimension), repeat=size):
                observed = gray_counts(coordinates, dimension)
                require(observed == direct_counts(coordinates, dimension),
                        "small complete mask table differs")
                cases += 1
                masks += len(observed)
    coordinates = tuple((37 * index) % 1024 for index in range(256))
    require(gray_counts(coordinates, 10) == direct_counts(coordinates, 10),
            "capacity-boundary mask table differs")
    return {"small_coordinate_lists": cases, "small_masks": masks,
            "capacity_boundary_masks": 1024}


def verify_complete():
    consumer = load_consumer()
    calls = []

    def checked_sections(coordinates, dimension):
        observed = gray_counts(coordinates, dimension)
        require(observed == direct_counts(coordinates, dimension),
                "reached core mask table differs")
        require(dimension == 7 and len(coordinates) == 24,
                "source adapter reached a different domain")
        calls.append((dimension, len(coordinates), len(observed) - 1))
        return Counter(observed[1:])

    consumer.gray_sections = checked_sections
    output = StringIO()
    with redirect_stdout(output):
        consumer.main()
    require(output.getvalue() == MARKER, "complete scientific stdout differs")
    require(len(calls) == 3780, "a complete core invocation is missing")
    sections = sum(row[2] for row in calls)
    return {"core_calls": len(calls), "nonzero_mask_sections": sections,
            "reference_parity_evaluations": sum(n * q for _, n, q in calls),
            "gray_column_bit_tests": sum(d * n for d, n, _ in calls),
            "gray_xor_updates": sections,
            "complete_stdout_sha256": sha256(output.getvalue().encode()).hexdigest()}


def rejected(operation, expected):
    try:
        operation()
    except (ValueError, FileNotFoundError, SystemExit) as error:
        require(expected in str(error), "control failed for a different reason")
        return 1
    raise ValueError("control accepted: " + expected)


def verify_boundaries():
    invalid = (((), -1, "dimension must"), ((), 11, "dimension must"),
               ((), True, "dimension must"), ((), 1.0, "dimension must"),
               ((-1,), 2, "coordinate outside"), ((4,), 2, "coordinate outside"),
               ((True,), 2, "coordinate outside"), ((1.0,), 2, "coordinate outside"),
               ((0,) * 257, 2, "at most 256"), ({0}, 2, "at most 256"))
    controls = sum(rejected(lambda c=c, d=d: gray_counts(c, d),
                            expected) for c, d, expected in invalid)
    controls += rejected(lambda: load_consumer("missing"), "unknown engine")
    payloads = REPLAY["authenticate"]()
    with tempfile.TemporaryDirectory(prefix="core-gray-controls-") as directory:
        root = Path(directory)
        for name, payload in payloads.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)
        for name, payload in payloads.items():
            path = root / name
            path.write_bytes(payload + b"\n")
            controls += rejected(lambda: load_consumer(root=root), "source drift")
            path.unlink()
            controls += rejected(lambda: load_consumer(root=root), name)
            path.write_bytes(payload)
    return controls


def verify_mutations():
    mutants = (
        lambda c, d: Counter(gray_counts(c, d)),  # Incorrectly includes mask zero.
        lambda c, d: Counter(gray_counts(c, d)[1:-1]),
        lambda c, d: Counter(len(c) - count for count in gray_counts(c, d)[1:]),
        lambda c, d: Counter(gray_counts(c[1:], d)[1:]),
    )
    controls = 0
    for mutant in mutants:
        consumer = load_consumer()
        consumer.gray_sections = mutant
        controls += rejected(consumer.main, "a section histogram moved")
    consumer = load_consumer()
    consumer.EXPECTED = {0: 2, 8: 15, 12: 96, 16: 15}
    controls += rejected(consumer.main, "a section histogram moved")
    consumer = load_consumer()
    original_span = consumer.span_coordinates
    consumer.span_coordinates = lambda values: (6, original_span(values)[1])
    controls += rejected(consumer.main, "a common core moved")
    return controls


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    result = {**verify_small(), **verify_complete(),
              "boundary_controls": verify_boundaries(),
              "scientific_mutation_controls": verify_mutations(),
              "status": "PASS_CORE_SECTION_GRAY_REPLAY"}
    result["package_sha256"] = {
        path.name: sha256(path.read_bytes()).hexdigest()
        for path in sorted(PACKAGE.iterdir()) if path.is_file()}
    if args.receipt:
        target = args.receipt.resolve()
        require(not target.is_relative_to(REPLAY["ROOT"]),
                "receipts must stay outside the checkout")
        target.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
