#!/usr/bin/env python3
"""Independent product-enumeration verifier for the TRIO-cycle certificate."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def differences(points: tuple[int, ...]) -> set[int]:
    # Deliberately recompute from scratch instead of sharing search.py's
    # incrementally accumulated packed difference mask.
    return {
        points[i] ^ points[j]
        for i in range(len(points))
        for j in range(i + 1, len(points))
    }


def enumerate_certificate() -> dict:
    walks = 0
    endpoints = 0
    histogram = Counter()
    maximum = -1
    maximum_prefixes = None
    full = 0
    digest = hashlib.sha256()

    # With q0=0, q1=1, q2=3 fixed, each of the next nine steps has six
    # coordinate choices. Reject collisions only; there is no coverage prune.
    for flips in itertools.product(range(6), repeat=9):
        points = [0, 1, 3]
        seen = {0, 1, 3}
        for coordinate in flips:
            nxt = points[-1] ^ (1 << coordinate)
            if nxt in seen:
                break
            points.append(nxt)
            seen.add(nxt)
        else:
            walks += 1
            if points[-1].bit_count() != 3:
                continue
            endpoints += 1
            pts = tuple(points)
            diff = differences(pts)
            size = len(diff)
            histogram[str(size)] += 1
            packed = sum(1 << mask for mask in diff)
            digest.update(bytes(pts) + packed.to_bytes(8, "big"))
            if size > maximum:
                maximum = size
                maximum_prefixes = list(pts)
            if len(diff) == 63 and diff == set(range(1, 64)):
                full += 1

    return {
        "normalized_simple_walks": walks,
        "closing_weight_three_candidates": endpoints,
        "coverage_histogram": dict(sorted(histogram.items(), key=lambda kv: int(kv[0]))),
        "maximum_coverage": maximum,
        "full_cover_witnesses": full,
        "maximum_example_prefixes": maximum_prefixes,
        "endpoint_records_sha256": digest.hexdigest(),
    }


def main() -> None:
    certificate = json.loads((HERE / "CERTIFICATE.json").read_text())
    observed = enumerate_certificate()
    expected = {
        key: certificate["counts"][key]
        for key in (
            "normalized_simple_walks",
            "closing_weight_three_candidates",
            "coverage_histogram",
            "maximum_coverage",
            "full_cover_witnesses",
        )
    }
    expected["maximum_example_prefixes"] = certificate["maximum_example_prefixes"]
    expected["maximum_example_missing_masks"] = certificate["maximum_example_missing_masks"]
    expected["endpoint_records_sha256"] = certificate["endpoint_records_sha256"]
    observed["maximum_example_missing_masks"] = sorted(
        set(range(1, 64))
        - differences(tuple(observed["maximum_example_prefixes"]))
    )
    if observed != expected:
        raise SystemExit(f"certificate mismatch\nobserved={observed}\nexpected={expected}")
    if observed["normalized_simple_walks"] != 1_098_204:
        raise SystemExit("unexpected normalized domain size")
    if observed["closing_weight_three_candidates"] != 709_812:
        raise SystemExit("unexpected closing-edge candidate count")
    if observed["maximum_coverage"] != 49 or observed["full_cover_witnesses"] != 0:
        raise SystemExit("unexpected coverage endpoint")

    # Predecessor positive control from PR #2128: its 14 boundary prefixes
    # realize all 63 nonzero masks under the same pair-difference criterion.
    control = certificate["positive_control_pr2128"]
    prefixes = tuple(control["prefixes"])
    steps = control["steps"]
    if len(prefixes) != 14 or len(set(prefixes)) != 14:
        raise SystemExit("PR #2128 control prefixes are not 14 distinct vertices")
    if [prefixes[0]] + [prefixes[i - 1] ^ steps[i - 1] for i in range(1, 14)] != list(prefixes):
        raise SystemExit("PR #2128 control prefix replay mismatch")
    if prefixes[-1] ^ steps[-1] != prefixes[0]:
        raise SystemExit("PR #2128 control does not close")
    if sum(x.bit_count() for x in steps) != control["source_adds"]:
        raise SystemExit("PR #2128 source-add bill mismatch")
    diff = differences(prefixes)
    if diff != set(range(1, 64)):
        raise SystemExit("PR #2128 positive control misses a required mask")
    if control["calls"] + control["readouts"] != control["root_queries"]:
        raise SystemExit("PR #2128 root-query bill mismatch")

    # Negative controls: the maximal example misses masks; deleting one of
    # its points cannot cover all 63 masks; a weight-one closing edge violates
    # the claimed operation profile.
    max_prefixes = tuple(certificate["maximum_example_prefixes"])
    max_diff = differences(max_prefixes)
    if len(max_diff) != 49 or len(set(range(1, 64)) - max_diff) != 14:
        raise SystemExit("maximal example negative control changed")
    if len(differences(max_prefixes[:-1])) >= 63:
        raise SystemExit("deleted-point negative control failed")
    if (max_prefixes[-1] ^ max_prefixes[0]).bit_count() != 3:
        raise SystemExit("closing-edge profile control failed")
    print(
        "PASS_TRIO_CYCLE_VERIFY "
        f"walks={observed['normalized_simple_walks']} "
        f"endpoints={observed['closing_weight_three_candidates']} "
        f"max={observed['maximum_coverage']} "
        f"full={observed['full_cover_witnesses']} "
        "pr2128=63/63 controls=3"
    )


if __name__ == "__main__":
    main()
