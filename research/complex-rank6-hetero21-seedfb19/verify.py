#!/usr/bin/env python3
"""Replay the exact (2,2,1,1)->6 selected-word screen."""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import json
import sys
import tarfile
from bisect import bisect_left
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/complex-local-word-ceiling"))
import ceiling as C  # noqa: E402

ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA256 = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
MEMBER_SHA256 = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
EXPECTED_STARTS = (16718, 16728, 16780, 16794, 16827, 16843, 16859,
                   16969, 16985, 17001, 17020, 17042, 17058)
GRID = Q(1, 10**12)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def selected_programs() -> dict[str, list]:
    archive = ARCHIVE.read_bytes()
    require(hashlib.sha256(archive).hexdigest() == ARCHIVE_SHA256,
            "selected replay archive pin")
    with tarfile.open(ARCHIVE, "r:gz") as tar:
        members = [item for item in tar.getmembers() if item.name == MEMBER]
        require(len(members) == 1, "exactly one selected gauge44 LOCAL-PROGRAMS member")
        stream = tar.extractfile(members[0])
        require(stream is not None, "selected provider member is readable")
        payload = stream.read()
    require(hashlib.sha256(payload).hexdigest() == MEMBER_SHA256,
            "selected provider member pin")
    result = json.loads(gzip.decompress(payload))
    require(set(result) == {"forward", "backward"}, "both selected orientations present")
    return result


def profile_of(events: list) -> dict[int, int]:
    counts: collections.Counter[int] = collections.Counter()
    for event in events:
        if event[0] == "climb":
            counts[int(event[5])] += 1
        elif event[0] == "center":
            counts[int(event[4])] += 1
    return dict(sorted(counts.items()))


def admissible_window(block: list) -> bool:
    if len(block) != 4 or not all(event[0] == "climb" for event in block):
        return False
    ranks = [int(event[5]) for event in block]
    destinations = [int(event[2]) for event in block]
    return sorted(ranks) == [1, 1, 2, 2] and len(set(destinations)) == 4


def enumerate_windows(events: list) -> list[dict]:
    windows = []
    for start in range(len(events) - 3):
        block = events[start:start + 4]
        if admissible_window(block):
            windows.append({
                "start": start,
                "end": start + 3,
                "ranks_in_order": [int(event[5]) for event in block],
                "destinations": [int(event[2]) for event in block],
            })
    return windows


def disjoint_schedule(windows: list[dict]) -> tuple[list[dict], int]:
    """Return earliest-finish packing and independently compute the optimum."""
    ordered = sorted(windows, key=lambda w: (w["end"], w["start"]))
    chosen = []
    last_end = -1
    for window in ordered:
        if window["start"] > last_end:
            chosen.append(window)
            last_end = window["end"]

    ends = [window["end"] for window in ordered]
    best = [0]
    for index, window in enumerate(ordered):
        predecessor_count = bisect_left(ends, window["start"], 0, index)
        best.append(max(best[-1], 1 + best[predecessor_count]))
    return chosen, best[-1]


def transformed_profile(groups: int) -> dict[int, int]:
    require(0 <= groups <= min(BASE_PROFILE[1] // 2, BASE_PROFILE[2] // 2),
            "fusion count within rank-one/rank-two inventory")
    result = dict(BASE_PROFILE)
    result[1] -= 2 * groups
    result[2] -= 2 * groups
    result[6] = groups
    return dict(sorted(result.items()))


def mass(profile: dict[int, int]) -> int:
    return sum(rank * count for rank, count in profile.items())


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[sum(left[i][k] * right[k][j] for k in range(len(right)))
             for j in range(len(right[0]))] for i in range(len(left))]


def block_diagonal(blocks: list[list[list[int]]]) -> list[list[int]]:
    size = sum(len(block) for block in blocks)
    result = [[0] * size for _ in range(size)]
    offset = 0
    for block in blocks:
        for i, row in enumerate(block):
            for j, value in enumerate(row):
                result[offset + i][offset + j] = value
        offset += len(block)
    return result


def check_identity_and_controls(sample: list) -> list[str]:
    a = [[1, 2], [3, 4]]
    b = [[0, 5], [6, 7]]
    c = [[2, 1], [0, 3]]
    d = [[3, 0], [1, 2]]
    left_blocks = [a, b, [[5]], [[7]]]
    right_blocks = [c, d, [[11]], [[13]]]
    product = matmul(block_diagonal(left_blocks), block_diagonal(right_blocks))
    expected = block_diagonal([
        matmul(a, c), matmul(b, d), [[55]], [[91]],
    ])
    require(product == expected, "positive exact block-diagonal multiplication identity")

    # The diagonal-input premise is real: a cross-block entry creates an
    # off-diagonal output that the direct-sum map does not promise to handle.
    bad_left = block_diagonal(left_blocks)
    bad_left[0][2] = 1
    bad_product = matmul(bad_left, block_diagonal(right_blocks))
    require(bad_product[0][2] != 0, "off-diagonal-support negative control")

    require(admissible_window(sample), "positive source-window control")
    wrong_rank = [event[:] for event in sample]
    wrong_rank[0][5] = 3
    require(not admissible_window(wrong_rank), "wrong-rank negative control")
    duplicate_column = [event[:] for event in sample]
    duplicate_column[-1][2] = duplicate_column[0][2]
    require(not admissible_window(duplicate_column), "duplicate-destination negative control")
    _, overlap_optimum = disjoint_schedule([
        {"start": 0, "end": 3}, {"start": 2, "end": 5},
    ])
    require(overlap_optimum == 1, "overlapping-window negative control")
    return [
        "exact block-diagonal identity on integer matrices",
        "off-diagonal support produces a cross-block output",
        "wrong-rank window rejected",
        "duplicate-destination window rejected",
        "overlapping windows not double-counted",
    ]


def ceiling_strings(profile: dict[int, int]) -> list[str]:
    return [str(endpoint) for endpoint in C.ceiling(
        profile, 73, 896, 9, 64, grid=GRID,
    )]


def build_certificate() -> dict:
    selected = ROOT / "certificates/selected-result.json"
    require(hashlib.sha256(selected.read_bytes()).hexdigest() == SELECTED_SHA256,
            "selected-record SHA-256 pin")
    programs = selected_programs()
    orientations = {}
    sample = None
    for orientation in ("backward", "forward"):
        events = programs[orientation]
        require(len(events) == 24767, f"{orientation} complete event count")
        require(profile_of(events) == BASE_PROFILE, f"{orientation} paid profile")
        windows = enumerate_windows(events)
        chosen, optimum = disjoint_schedule(windows)
        starts = tuple(window["start"] for window in chosen)
        require(len(windows) == 28, f"{orientation} admissible-window census")
        require(optimum == 13 == len(chosen), f"{orientation} maximum disjoint packing")
        require(starts == EXPECTED_STARTS, f"{orientation} exact optimal schedule")
        orientations[orientation] = {
            "event_count": len(events),
            "profile": {str(k): v for k, v in sorted(profile_of(events).items())},
            "admissible_windows": windows,
            "admissible_window_count": len(windows),
            "maximum_disjoint_count": optimum,
            "one_maximum_schedule": chosen,
        }
        if sample is None:
            sample = events[windows[0]["start"]:windows[0]["end"] + 1]

    require(sample is not None, "at least one source window exists")
    controls = check_identity_and_controls(sample)
    groups = 13
    profile13 = transformed_profile(groups)
    base_ceiling = ceiling_strings(BASE_PROFILE)
    ceiling13 = ceiling_strings(profile13)
    profile125 = transformed_profile(125)
    profile126 = transformed_profile(126)
    ceiling125 = ceiling_strings(profile125)
    ceiling126 = ceiling_strings(profile126)
    target = Q(base_ceiling[1]) * Q(21, 20)
    require(mass(BASE_PROFILE) == mass(profile13) == 5586,
            "rank mass preserved by each (2,2,1,1)->6 fusion")
    require(Q(ceiling13[1]) < target,
            "13-block zero-charge ceiling misses the five-percent target")
    require(Q(ceiling125[1]) < target < Q(ceiling126[0]),
            "126 zero-charge blocks are the first to cross the five-percent target")
    require(Q(ceiling13[1]) / Q(base_ceiling[0]) - 1 < Q(1, 200),
            "13-block ideal gain is below one half percent")
    return {
        "schema_version": 1,
        "source": {
            "selected_record_sha256": SELECTED_SHA256,
            "archive_sha256": ARCHIVE_SHA256,
            "member": MEMBER,
            "member_sha256": MEMBER_SHA256,
        },
        "fusion": {
            "rank_multiset": [1, 1, 2, 2],
            "child_rank": 6,
            "rank_mass_before": 6,
            "rank_mass_after": 6,
            "identity": "diag(A2,B2,a,b) diag(C2,D2,c,d) = diag(A2*C2,B2*D2,a*c,b*d)",
        },
        "orientations": orientations,
        "profiles_and_ceilings": {
            "baseline_profile": {str(k): v for k, v in BASE_PROFILE.items()},
            "baseline_ceiling_bracket": base_ceiling,
            "maximum_source_schedule_groups": groups,
            "maximum_source_profile": {str(k): v for k, v in profile13.items()},
            "maximum_source_ceiling_bracket": ceiling13,
            "five_percent_threshold_from_baseline_upper": str(target),
            "maximum_source_passes_five_percent": False,
            "zero_charge_groups_125_profile": {str(k): v for k, v in profile125.items()},
            "zero_charge_groups_125_ceiling_bracket": ceiling125,
            "zero_charge_groups_126_profile": {str(k): v for k, v in profile126.items()},
            "zero_charge_groups_126_ceiling_bracket": ceiling126,
            "minimum_zero_charge_groups_for_five_percent": 126,
            "maximum_source_relative_gain_upper_vs_baseline_lower": str(
                Q(ceiling13[1]) / Q(base_ceiling[0]) - 1
            ),
        },
        "controls": controls,
        "scope": "Only contiguous four-event windows in the two pinned selected traces; all non-child charges are waived for the optimistic ceiling screen.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write the deterministic certificate")
    args = parser.parse_args()
    certificate = build_certificate()
    destination = HERE / "CERTIFICATE.json"
    encoded = json.dumps(certificate, indent=2) + "\n"
    if args.write:
        destination.write_text(encoded, encoding="utf-8")
    else:
        require(destination.read_text(encoding="utf-8") == encoded,
                "committed certificate differs from exact replay")
    print("PASS_MIXED_RANK21_BLOCK_SCREEN windows=28 disjoint=13 target_minimum=126 profile_gain_below_0.5_percent")


if __name__ == "__main__":
    main()
