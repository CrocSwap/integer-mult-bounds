#!/usr/bin/env python3
"""Exact Phase B rank-shape occurrence envelope for the pinned provider."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
from io import BytesIO


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
ARCHIVE_SHA256 = "d4acf04daef85d4514f80ec5fcd2492d0c60e5d6c49fa71b3e6523f8db2dea86"
PROGRAMS_MEMBER = "evidence/local/LOCAL-PROGRAMS.json.gz"
PROGRAMS_SHA256 = "172dc3d23e437909ddc01d07b12ede735afbb5bb6145f1ddf5c2e03097dfebe2"
CANONICAL_MEMBER = "evidence/local/CANONICAL-WORD.json.gz"
CANONICAL_SHA256 = "92941c2b718b533f1d3addb710d261a6e2b9ec5d19f0051d79775b08cb2571ed"
SELECTED_SHA256 = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
CEILING_SHA256 = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
RESULT_PATH = PACKAGE / "RESULT.json"


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def source_pins() -> dict[str, str]:
    task = json.loads((PACKAGE / "TASK.json").read_text(encoding="utf-8"))
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    need(task["base_commit"] == manifest["base_commit"], "task/source base mismatch")
    selected = (ROOT / "certificates/selected-result.json").read_bytes()
    need(sha256(selected) == SELECTED_SHA256, "selected-record hash mismatch")
    result = {}
    for row in manifest["files"]:
        payload = (ROOT / row["path"]).read_bytes()
        need(sha256(payload) == row["sha256"], "source hash mismatch: " + row["path"])
        result[row["path"]] = row["sha256"]
    return result


def gf2_rank(rows: list[int]) -> int:
    pivots: dict[int, int] = {}
    for original in rows:
        value = int(original)
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def is_block_group(events: list[list], expected_ranks=(1, 1, 1, 3)) -> bool:
    return (
        len(events) == 4
        and all(isinstance(event, list) and len(event) >= 6 and event[0] == "climb"
                for event in events)
        and sorted(int(event[5]) for event in events) == list(expected_ranks)
        and len({int(event[2]) for event in events}) == 4
    )


def dynamic_disjoint_count(candidate_starts: list[int], child_count: int) -> int:
    starts = set(candidate_starts)
    dp = [0] * (child_count + 4)
    for i in range(child_count - 1, -1, -1):
        take = 1 + dp[i + 4] if i in starts else 0
        dp[i] = max(dp[i + 1], take)
    return dp[0]


def greedy_disjoint_starts(candidate_starts: list[int]) -> list[int]:
    chosen = []
    last_used = -1
    for start in sorted(candidate_starts):
        if start > last_used:
            chosen.append(start)
            last_used = start + 3
    return chosen


def program_data(archive_bytes: bytes) -> tuple[dict, dict, dict[str, str]]:
    need(sha256(archive_bytes) == ARCHIVE_SHA256, "selected provider archive hash mismatch")
    with tarfile.open(fileobj=BytesIO(archive_bytes), mode="r:gz") as archive:
        compressed_programs = archive.extractfile(PROGRAMS_MEMBER)
        compressed_canonical = archive.extractfile(CANONICAL_MEMBER)
        checks_member = archive.extractfile("evidence/local/LOCAL-CHECKS.json")
        need(compressed_programs is not None and compressed_canonical is not None and checks_member is not None,
             "selected archive is missing a pinned local member")
        programs_bytes = compressed_programs.read()
        canonical_bytes = compressed_canonical.read()
        checks_bytes = checks_member.read()
    need(sha256(programs_bytes) == PROGRAMS_SHA256, "local-program member hash mismatch")
    need(sha256(canonical_bytes) == CANONICAL_SHA256, "canonical-word member hash mismatch")
    programs = json.loads(gzip.decompress(programs_bytes))
    canonical = json.loads(gzip.decompress(canonical_bytes))
    checks = json.loads(checks_bytes)
    for direction in ("forward", "backward"):
        digest = sha256(json.dumps(programs[direction], sort_keys=True, separators=(",", ":")).encode())
        need(digest == checks[direction]["sha256"], direction + " complete-event digest mismatch")
    return programs, canonical, {
        PROGRAMS_MEMBER: sha256(programs_bytes),
        CANONICAL_MEMBER: sha256(canonical_bytes),
        "evidence/local/LOCAL-CHECKS.json": sha256(checks_bytes),
    }


def phase_bounds(events: list[list]) -> tuple[int, int]:
    markers = [(i, event[1]) for i, event in enumerate(events)
               if isinstance(event, list) and len(event) == 2 and event[0] == "phase"]
    starts = [i for i, name in markers if name == "B"]
    ends = [i for i, name in markers if name == "cleanup_tail"]
    need(len(starts) == len(ends) == 1 and starts[0] < ends[0], "Phase B markers are not unique and ordered")
    return starts[0], ends[0]


def candidate_windows(events: list[list], canonical: dict) -> dict:
    start, end = phase_bounds(events)
    phase = events[start + 1:end]
    histogram = Counter(event[0] for event in phase)
    climbs = [(global_index, event) for global_index, event in enumerate(phase, start + 1)
              if isinstance(event, list) and event and event[0] == "climb"]
    climb_histogram = Counter(int(event[5]) for _, event in climbs)

    raw_count = sum(
        is_block_group(phase[i:i + 4])
        for i in range(max(0, len(phase) - 3))
    )

    frames = canonical["frames"]
    records = []
    starts = []
    for ordinal in range(len(climbs) - 3):
        group = climbs[ordinal:ordinal + 4]
        child_events = [event for _, event in group]
        if not is_block_group(child_events):
            continue

        event_indices = [int(index) for index, _ in group]
        registers = [int(event[2]) for event in child_events]
        source_ids = [int(event[3]) for event in child_events]
        target_ids = [int(event[4]) for event in child_events]
        source_frames = [frames[index] for index in source_ids]
        target_frames = [frames[index] for index in target_ids]
        selected_indices = set(event_indices)
        between = [(i, events[i]) for i in range(event_indices[0] + 1, event_indices[-1])
                   if i not in selected_indices]
        need(all(isinstance(event, list) and event and event[0] == "scalar"
                  for _, event in between), "a non-scalar event lies between Phase B climb calls")
        register_set = set(registers)
        scalar_payload = []
        scalar_candidate_register_touch_count = 0
        for scalar_index, scalar_event in between:
            operation = scalar_event[1]
            refs = {int(arg[1]) for arg in operation[1:]
                    if isinstance(arg, list) and len(arg) >= 2 and arg[0] == "L"}
            scalar_payload.append([scalar_index, scalar_event])
            scalar_candidate_register_touch_count += len(refs & register_set)

        source_rows = [row for frame in source_frames for row in frame]
        target_rows = [row for frame in target_frames for row in frame]
        source_union = gf2_rank(source_rows)
        target_union = gf2_rank(target_rows)
        source_max = max(map(len, source_frames))
        target_max = max(map(len, target_frames))
        records.append({
            "start_climb_ordinal": ordinal,
            "event_indices": event_indices,
            "ranks": [int(event[5]) for event in child_events],
            "registers": registers,
            "source_frame_ids": source_ids,
            "target_frame_ids": target_ids,
            "source_frame_dimensions": [len(frame) for frame in source_frames],
            "target_frame_dimensions": [len(frame) for frame in target_frames],
            "source_frame_union_rank": source_union,
            "target_frame_union_rank": target_union,
            "source_union_excess_vs_largest": source_union - source_max,
            "target_union_excess_vs_largest": target_union - target_max,
            "intervening_scalar_event_count": len(between),
            "intervening_scalar_candidate_register_touch_count": scalar_candidate_register_touch_count,
            "intervening_scalar_payload_sha256": sha256(
                json.dumps(scalar_payload, sort_keys=True, separators=(",", ":")).encode()
            ),
        })
        starts.append(ordinal)

    return {
        "phase_marker_indices": {"B": start, "cleanup_tail": end},
        "event_count": len(phase),
        "event_type_histogram": dict(sorted(histogram.items())),
        "climb_count": len(climbs),
        "climb_rank_histogram": {str(k): climb_histogram[k] for k in sorted(climb_histogram)},
        "raw_four_event_windows": raw_count,
        "consecutive_child_order_candidates": records,
        "candidate_count": len(records),
        "maximum_disjoint_count_greedy": len(greedy_disjoint_starts(starts)),
        "maximum_disjoint_start_ordinals": greedy_disjoint_starts(starts),
        "maximum_disjoint_count_dp": dynamic_disjoint_count(starts, len(climbs)),
    }


def load_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    need(sha256(path.read_bytes()) == CEILING_SHA256, "ceiling engine hash mismatch")
    spec = importlib.util.spec_from_file_location("pinned_phaseb_ceiling", path)
    need(spec is not None and spec.loader is not None, "cannot import the pinned ceiling engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def profile(k: int) -> dict[int, int]:
    return {1: 2412 - 3 * k, 2: 418, 3: 432 - k, 4: 142, 5: 82, 6: k, 8: 8}


def cost_screen(candidate_count: int) -> dict:
    selected = json.loads((ROOT / "research/complex-local-word-ceiling/RESULT.json").read_text())
    base = {int(rank): int(count) for rank, count in selected["selected"]["local_profile_per_call"].items()}
    need(base == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}, "selected profile drift")
    engine = load_ceiling()
    baseline = engine.ceiling(base, 73, 896, 9, 64)
    target = baseline[1] * Q(105, 100)
    at_count = engine.ceiling(profile(candidate_count), 73, 896, 9, 64)
    at_134 = engine.ceiling(profile(134), 73, 896, 9, 64)
    at_135 = engine.ceiling(profile(135), 73, 896, 9, 64)
    need(baseline[1] == Q(1690054109089, 10**15), "baseline upper endpoint changed")
    need(at_count[1] < target, "candidate count unexpectedly reaches the 5% target")
    need(at_134[1] < target < at_135[0], "adjacent 134/135 target controls changed")
    need(sum(r * n for r, n in profile(candidate_count).items()) == 5586,
         "block replacement must preserve rank mass")
    return {
        "selected_profile": {str(rank): n for rank, n in sorted(base.items())},
        "rank_mass": 5586,
        "per_block_profile_delta": {"1": -3, "3": -1, "6": 1},
        "candidate_blocks": candidate_count,
        "candidate_profile_zero_extra_cost": {str(rank): n for rank, n in sorted(profile(candidate_count).items())},
        "baseline_ceiling": [str(x) for x in baseline],
        "candidate_ceiling": [str(x) for x in at_count],
        "five_percent_target": str(target),
        "candidate_gain_upper_over_baseline_lower": str(at_count[1] / baseline[0] - 1),
        "zero_extra_cost_minimum_blocks": 135,
        "134_block_ceiling": [str(x) for x in at_134],
        "135_block_ceiling": [str(x) for x in at_135],
        "frame_scalar_copy_hosting_precision_restoration_charges": 0,
        "interpretation": "An optimistic ceiling screen over the consecutive child-call candidate envelope; no frame-compatible realization or complete child interface is asserted.",
    }


def build_result() -> dict:
    source_pins()
    archive_bytes = (ROOT / ARCHIVE).read_bytes()
    programs, canonical, member_hashes = program_data(archive_bytes)
    forward = candidate_windows(programs["forward"], canonical)
    backward = candidate_windows(programs["backward"], canonical)
    need(forward["event_count"] == backward["event_count"] == 3870, "Phase B event count changed")
    need(forward["event_type_histogram"] == backward["event_type_histogram"] == {"climb": 1952, "scalar": 1918},
         "Phase B event-type histogram changed")
    need(forward["climb_rank_histogram"] == backward["climb_rank_histogram"] ==
         {"1": 1160, "2": 352, "3": 344, "4": 96}, "Phase B climb-rank histogram changed")
    need(forward["raw_four_event_windows"] == backward["raw_four_event_windows"] == 0,
         "a directly consecutive raw-event block appeared")
    need(forward["candidate_count"] == backward["candidate_count"] == 12,
         "Phase B child-order candidate census changed")
    need(forward["maximum_disjoint_count_dp"] == backward["maximum_disjoint_count_dp"] == 12,
         "maximum disjoint schedule changed")
    need(forward["maximum_disjoint_count_greedy"] == backward["maximum_disjoint_count_greedy"] == 12,
         "greedy schedule disagrees with the maximum count")

    scalar_fields = {
        "intervening_scalar_event_count",
        "intervening_scalar_candidate_register_touch_count",
        "intervening_scalar_payload_sha256",
    }
    signature = lambda row: {k: v for k, v in row.items() if k not in scalar_fields}
    forward_signatures = [signature(row) for row in forward["consecutive_child_order_candidates"]]
    backward_signatures = [signature(row) for row in backward["consecutive_child_order_candidates"]]
    need(forward_signatures == backward_signatures,
         "forward/backward candidate addresses or frame transitions differ")
    signature_digest = sha256(json.dumps(forward_signatures, sort_keys=True, separators=(",", ":")).encode())
    forward["candidate_climb_frame_signature_sha256"] = signature_digest
    backward_summary = {k: v for k, v in backward.items() if k != "consecutive_child_order_candidates"}
    backward_summary["candidate_climb_frame_signature_sha256"] = signature_digest
    cost = cost_screen(forward["maximum_disjoint_count_dp"])
    return {
        "schema_version": 1,
        "scope": "Pinned selected provider Phase B only; four consecutive climb calls in child-call order, ranks {1,1,1,3}, distinct registers; all intervening scalar events are waived in the optimistic screen.",
        "archive_sha256": ARCHIVE_SHA256,
        "archive_member_compressed_sha256": member_hashes,
        "selected_record_sha256": SELECTED_SHA256,
        "forward": forward,
        "backward": backward_summary,
        "cost_screen": cost,
        "limitations": [
            "Candidate windows are rank and register filters, not a demonstrated placement of the predecessor tensor.",
            "Frame union ranks are exact incidence data; they are not converted into an interface tariff.",
            "No nonconsecutive child collection, changed source word, other phase, supplier admission, or kappa change is claimed.",
        ],
    }


def controls() -> None:
    valid = [["climb", "B", q, 0, 1, r] for q, r in ((10, 3), (11, 1), (12, 1), (13, 1))]
    need(is_block_group(valid), "positive rank-shape control rejected")
    need(not is_block_group(valid[:3] + [["climb", "B", 13, 0, 1, 2]]), "wrong-rank control accepted")
    duplicate = [valid[0], valid[1], valid[2], ["climb", "B", 10, 0, 1, 1]]
    need(not is_block_group(duplicate), "duplicate-register control accepted")
    need(not is_block_group(valid[:2] + [["scalar", ["add", ["L", 1], ["L", 2], 1, 1], 0]] + valid[2:]),
         "raw-event scalar-crossing control accepted")
    need(dynamic_disjoint_count([0, 1, 4], 8) == 2, "overlapping-block dynamic control failed")
    need(greedy_disjoint_starts([0, 1, 4]) == [0, 4], "overlapping-block greedy control failed")


def main() -> None:
    source_pins()
    controls()
    result = build_result()
    expected = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    need(result == expected, "computed Phase B occurrence certificate differs from RESULT.json")
    print("PASS_PHASEB_RANKSHAPE_SCREEN windows=12 disjoint=12 target_minimum=135 gain_upper_pct="
          f"{float(Q(result['cost_screen']['candidate_gain_upper_over_baseline_lower']) * 100):.6f}")


if __name__ == "__main__":
    main()
