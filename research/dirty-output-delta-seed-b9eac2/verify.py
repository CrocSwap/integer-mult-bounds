#!/usr/bin/env python3
"""Verify a paired dirty-output wrapper around a rank-eight scalar child.

All map and gate calculations are exact integers/rationals. The only imported
module provides the repository's outward-rounded rational enclosures for
(r/73)^(1-a).
"""
from fractions import Fraction as Q
import hashlib
import itertools
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "complex-local-word-ceiling"))
import ceiling  # noqa: E402


def require(ok, message):
    if not ok:
        raise ValueError(message)


def dot8(x, y):
    require(len(x) == 8 and len(y) == 8, "rank-eight inputs required")
    return sum(a * b for a, b in zip(x, y))


def paired_wrapper(d1, d2, f):
    """Run two repetitions using only ADD, NEG, and the dirty child-plus call."""
    counts = {"ADD": 0, "NEG": 0, "child_rank8": 0}
    for _ in range(2):
        d1 = -d1
        counts["NEG"] += 1
        d2 = d2 + d1
        counts["ADD"] += 1
        d1 = -d1
        counts["NEG"] += 1
        d1 = d1 + f
        counts["child_rank8"] += 1
        d2 = d2 + d1
        counts["ADD"] += 1
    return (d1, d2), counts


def separate_calls(d1, d2, f):
    """Each dirty target receives two independent rank-eight child calls."""
    return (d1 + f + f, d2 + f + f)


def affine_wrapper():
    """Symbolically execute rows in variables (D1,D2,f), over Q."""
    rows = [[Q(1), Q(0), Q(0)], [Q(0), Q(1), Q(0)]]
    prefix_l1 = max(sum(abs(c) for c in row) for row in rows)
    difference_l1 = None
    for _ in range(2):
        rows[0] = [-v for v in rows[0]]
        prefix_l1 = max(prefix_l1, sum(abs(c) for c in rows[0]))
        rows[1] = [a + b for a, b in zip(rows[1], rows[0])]
        difference_l1 = sum(abs(c) for c in rows[1])
        prefix_l1 = max(prefix_l1, difference_l1)
        rows[0] = [-v for v in rows[0]]
        prefix_l1 = max(prefix_l1, sum(abs(c) for c in rows[0]))
        rows[0][2] += 1
        prefix_l1 = max(prefix_l1, sum(abs(c) for c in rows[0]))
        rows[1] = [a + b for a, b in zip(rows[1], rows[0])]
        prefix_l1 = max(prefix_l1, sum(abs(c) for c in rows[1]))
    return rows, prefix_l1, difference_l1


def mutated(d1, d2, f, fault):
    """Small incorrect variants used as negative controls."""
    for _ in range(2):
        d1 = -d1
        d2 = d2 + d1
        if fault != "omit_restore_neg":
            d1 = -d1
        d1 = d1 + f
        if fault != "omit_final_add":
            d2 = d2 + d1
    return d1, d2


def verify_map_and_controls():
    expected_rows = [[Q(1), Q(0), Q(2)], [Q(0), Q(1), Q(2)]]
    rows, prefix_l1, difference_l1 = affine_wrapper()
    require(rows == expected_rows, "symbolic affine map is not (D1+2f,D2+2f)")
    require(prefix_l1 == 3, "unexpected prefix coefficient L1 maximum")
    require(difference_l1 == 2, "temporary D2-D1 difference has unexpected L1")

    witness = (2, 5, 3)
    expected = separate_calls(*witness)
    require(expected == (8, 11), "positive witness setup changed")
    for fault in ("omit_restore_neg", "omit_final_add"):
        require(mutated(*witness, fault) != expected,
                "negative control unexpectedly implements the target map: " + fault)

    source_pairs = target_pairs = 0
    values = tuple(itertools.product((0, 1), repeat=8))
    dirty_values = tuple(itertools.product(range(-1, 2), repeat=2))
    for x in values:
        for y in values:
            f = dot8(x, y)
            for d1, d2 in dirty_values:
                got, counts = paired_wrapper(d1, d2, f)
                require(got == separate_calls(d1, d2, f),
                        "finite positive map check failed")
                require(counts == {"ADD": 4, "NEG": 4, "child_rank8": 2},
                        "gate/child invoice changed")
                target_pairs += 1
            source_pairs += 1
    require(source_pairs == 65_536, "Boolean source-pair census incomplete")
    require(target_pairs == 589_824, "dirty-target grid census incomplete")
    return source_pairs, target_pairs


def verify_moment_screen():
    record_path = ROOT / "certificates" / "selected-result.json"
    record_bytes = record_path.read_bytes()
    record = json.loads(record_bytes)
    require(hashlib.sha256(record_bytes).hexdigest() ==
            "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32",
            "selected record does not match the cycle pin")
    assembly_path = ROOT / record["certificate"]
    assembly_bytes = assembly_path.read_bytes()
    require(hashlib.sha256(assembly_bytes).hexdigest() == record["certificate_sha256"],
            "selected assembly hash mismatch")
    assembly = json.loads(assembly_bytes)
    a = Q(assembly["complex_lower"])
    require(a == Q(67018507072324140917, 40000000000000000000000),
            "complex endpoint changed from the pinned cycle value")

    phi8 = ceiling.child_cost(8, 73, a)
    phi1 = ceiling.child_cost(1, 73, a)
    baseline = (4 * phi8[0], 4 * phi8[1])
    candidate = (2 * phi8[0] + 8 * phi1[0],
                 2 * phi8[1] + 8 * phi1[1])
    require(candidate[1] < baseline[0],
            "rank-eight sharing fails the conservative scalar-gate moment screen")
    return a, phi8, phi1, baseline, candidate


def main():
    source_pairs, target_pairs = verify_map_and_controls()
    a, phi8, phi1, baseline, candidate = verify_moment_screen()
    ratio = Q(baseline[0] - candidate[1], baseline[0])
    print("PASS_DIRTY_OUTPUT_DELTA")
    print("map=(D1+2f,D2+2f); affine_prefix_L1_max=3; temporary_D2-D1_L1=2")
    print(f"boolean_source_pairs={source_pairs} dirty_target_cases={target_pairs}")
    print("invoice=4 rank8 baseline; 2 rank8 + 4 ADD + 4 NEG candidate")
    print(f"selected_a={a}")
    print(f"phi8_enclosure=[{float(phi8[0]):.16g},{float(phi8[1]):.16g}]")
    print(f"phi1_enclosure=[{float(phi1[0]):.16g},{float(phi1[1]):.16g}]")
    print(f"baseline_lower={float(baseline[0]):.16g} candidate_upper={float(candidate[1]):.16g}")
    print(f"certified_screen_saving_fraction_lower={float(ratio):.8%}")
    print("controls=PASS omit_restore_neg,omit_final_add")


if __name__ == "__main__":
    main()
