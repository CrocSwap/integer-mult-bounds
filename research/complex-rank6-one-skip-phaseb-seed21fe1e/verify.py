#!/usr/bin/env python3
"""Exact census and zero-overhead screen for one skipped Phase B child."""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import tarfile


PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
ARCHIVE = ROOT / "research/complex-t16-rare-pattern-exchanges/upstream1087.tar.gz"
ARCHIVE_SHA256 = "d4acf04daef85d4514f80ec5fcd2492d0c60e5d6c49fa71b3e6523f8db2dea86"
RESULT = PACKAGE / "RESULT.json"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def scalar_registers(node):
    """Return every local register referenced by an L-index in a scalar AST."""
    found = set()
    if isinstance(node, list):
        if len(node) == 2 and node[0] == "L" and type(node[1]) is int:
            found.add(node[1])
        else:
            for child in node:
                found.update(scalar_registers(child))
    return found


def gf2_basis(rows):
    """Canonical high-pivot basis for an integer-row span over GF(2)."""
    pivots = {}
    for value in rows:
        x = int(value)
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                for q, y in tuple(pivots.items()):
                    if (y >> p) & 1:
                        pivots[q] = y ^ x
                pivots[p] = x
                break
    return [pivots[p] for p in sorted(pivots, reverse=True)]


def structural_candidate(ranks, registers, skipped_register):
    return (sorted(ranks) == [1, 1, 1, 3]
            and len(set(registers)) == 4
            and skipped_register not in set(registers))


def commutes_with_gap(gap_events, selected_registers):
    selected = set(selected_registers)
    return all(event[0] != "scalar"
               or not (scalar_registers(event[1]) & selected)
               for event in gap_events)


def load_archive():
    raw = ARCHIVE.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    need(digest == ARCHIVE_SHA256, "provider archive SHA256 mismatch")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        names = archive.getnames()
        local_names = [n for n in names if n.endswith("evidence/local/LOCAL-PROGRAMS.json.gz")]
        word_names = [n for n in names if n.endswith("evidence/local/CANONICAL-WORD.json.gz")]
        need(len(local_names) == len(word_names) == 1, "archive member inventory mismatch")
        programs = json.loads(gzip.decompress(archive.extractfile(local_names[0]).read()))
        word = json.loads(gzip.decompress(archive.extractfile(word_names[0]).read()))
    return digest, programs, word["frames"]


def phase_b(events):
    marks = [(i, event[1]) for i, event in enumerate(events) if event[0] == "phase"]
    pairs = [(j, marks[j][0], marks[j + 1][0])
             for j in range(len(marks) - 1) if marks[j][1] == "B"]
    need(len(pairs) == 1, "expected exactly one bounded Phase B interval")
    _j, marker, end = pairs[0]
    return events[marker + 1:end]


def orientation_census(events, frame_table):
    phase = phase_b(events)
    calls = [(i, event) for i, event in enumerate(phase) if event[0] == "climb"]
    scalars = [event for event in phase if event[0] == "scalar"]
    histogram = Counter(int(event[5]) for _, event in calls)
    need((len(phase), len(calls), len(scalars)) == (3870, 1952, 1918),
         "Phase B event census changed")
    need(histogram == {1: 1160, 2: 352, 3: 344, 4: 96},
         "Phase B climb histogram changed")

    consecutive = []
    for start in range(len(calls) - 3):
        chosen = calls[start:start + 4]
        ranks = [int(event[5]) for _, event in chosen]
        registers = [int(event[2]) for _, event in chosen]
        if sorted(ranks) == [1, 1, 1, 3] and len(set(registers)) == 4:
            consecutive.append({"start": start, "end": start + 3})
    need(len(consecutive) == 12,
         "consecutive rank/register positive-control count changed")

    raw = []
    for start in range(len(calls) - 4):
        span = calls[start:start + 5]
        for skipped_position in (1, 2, 3):
            skipped = span[skipped_position][1]
            selected = [record for j, record in enumerate(span) if j != skipped_position]
            selected_events = [event for _i, event in selected]
            ranks = [int(event[5]) for event in selected_events]
            registers = [int(event[2]) for event in selected_events]
            if not structural_candidate(ranks, registers, int(skipped[2])):
                continue

            first_event = selected[0][0]
            last_event = selected[-1][0]
            gap = phase[first_event + 1:last_event]
            selected_registers = set(registers)
            touched_gap = []
            gap_scalar_count = 0
            for local_index, event in enumerate(gap, first_event + 1):
                if event[0] == "scalar":
                    gap_scalar_count += 1
                    overlap = sorted(scalar_registers(event[1]) & selected_registers)
                    if overlap:
                        touched_gap.append({"event_index": local_index,
                                            "selected_registers_touched": overlap})

            source_rows = [row for event in selected_events
                           for row in frame_table[int(event[3])]]
            target_rows = [row for event in selected_events
                           for row in frame_table[int(event[4])]]
            source_basis = gf2_basis(source_rows)
            target_basis = gf2_basis(target_rows)
            raw.append({
                "start_child_call": start,
                "skipped_position": skipped_position,
                "selected_event_indices": [int(i) for i, _event in selected],
                "selected_ranks": ranks,
                "selected_registers": registers,
                "skipped_register": int(skipped[2]),
                "source_frame_ids": [int(event[3]) for event in selected_events],
                "target_frame_ids": [int(event[4]) for event in selected_events],
                "source_union_basis": [str(x) for x in source_basis],
                "target_union_basis": [str(x) for x in target_basis],
                "source_union_rank": len(source_basis),
                "target_union_rank": len(target_basis),
                "intervening_scalar_event_count": gap_scalar_count,
                "intervening_scalar_touch_events": touched_gap,
            })

    touch_histogram = Counter(len(row["intervening_scalar_touch_events"]) for row in raw)
    source_target_rank_histogram = Counter(
        f"{row['source_union_rank']}:{row['target_union_rank']}" for row in raw)
    commuting = [row for row in raw if not row["intervening_scalar_touch_events"]]
    need(len(raw) == 67, "raw one-skip candidate census changed")
    need(touch_histogram == {2: 63, 12: 4},
         "one-skip scalar-touch control histogram changed")
    need(not commuting, "a no-buffer commuting one-skip candidate survived")

    return {
        "phase_event_count": len(phase),
        "climb_count": len(calls),
        "scalar_count": len(scalars),
        "climb_rank_histogram": {str(k): histogram[k] for k in sorted(histogram)},
        "consecutive_rank_register_windows": len(consecutive),
        "raw_one_skip_candidates": len(raw),
        "scalar_touch_event_histogram": {str(k): touch_histogram[k]
                                         for k in sorted(touch_histogram)},
        "source_target_union_rank_histogram": {
            k: source_target_rank_histogram[k] for k in sorted(source_target_rank_histogram)},
        "strict_commuting_candidates": len(commuting),
        "raw_candidates_with_exact_frame_unions": raw,
    }


def load_ceiling_module():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def profile(k):
    return {1: Q(2412 - 3 * k), 2: Q(418), 3: Q(432 - k),
            4: Q(142), 5: Q(82), 6: Q(k), 8: Q(8)}


def cost_screen():
    ceiling = load_ceiling_module()
    selected = json.loads((ROOT / "research/complex-local-word-ceiling/RESULT.json")
                          .read_text(encoding="utf-8"))
    base_profile = {int(r): int(n)
                    for r, n in selected["selected"]["local_profile_per_call"].items()}
    need(base_profile == {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8},
         "selected local profile changed")
    base_bracket = ceiling.ceiling(base_profile, 73, 896, 9, 64)
    need(base_bracket[1] == Q(selected["ceiling"]["a_ceiling"]),
         "selected ceiling does not replay")
    target = base_bracket[1] * Q(105, 100)
    need(target == Q(35491136290869, 20000000000000000),
         "pinned five-percent threshold changed")

    at_target_0 = ceiling.relax(profile(0), 73, 896, 9, 64, target)
    at_target_1 = ceiling.relax(profile(1), 73, 896, 9, 64, target)
    slope_high = at_target_1[1] - at_target_0[0]
    need(slope_high < 0, "one-block relaxation is not monotonically improving")

    brackets = {}
    for k in (79, 134, 135):
        bracket = ceiling.ceiling(profile(k), 73, 896, 9, 64)
        brackets[str(k)] = [str(value) for value in bracket]
    at_target_79 = ceiling.relax(profile(79), 73, 896, 9, 64, target)
    need(Q(brackets["79"][1]) < target and at_target_79[0] > 1,
         "generous 79-block profile unexpectedly meets the 5-percent gate")
    need(Q(brackets["134"][1]) < target,
         "134-block negative boundary control changed")
    need(Q(brackets["135"][0]) > target,
         "135-block positive boundary control changed")
    return {
        "selected_profile": {str(r): n for r, n in sorted(base_profile.items())},
        "selected_ceiling_bracket": [str(value) for value in base_bracket],
        "five_percent_a_target": str(target),
        "one_block_relaxation_slope_upper_at_target": str(slope_high),
        "zero_extra_cost_ceiling_brackets": brackets,
        "79_block_relaxation_at_target": [str(value) for value in at_target_79],
        "all_scalar_frame_copy_hosting_precision_restoration_costs": "waived",
    }


def build_result():
    archive_hash, programs, frame_table = load_archive()
    need(set(programs) == {"forward", "backward"}, "orientation inventory changed")
    full_censuses = {name: orientation_census(programs[name], frame_table)
                     for name in ("forward", "backward")}
    need(full_censuses["forward"] == full_censuses["backward"],
         "forward/backward Phase B censuses or frame-union records disagree")
    common_frame_unions = full_censuses["forward"]["raw_candidates_with_exact_frame_unions"]
    orientations = {}
    for name, census in full_censuses.items():
        census = dict(census)
        del census["raw_candidates_with_exact_frame_unions"]
        orientations[name] = census
    strict_total = sum(item["strict_commuting_candidates"]
                       for item in orientations.values())
    raw_total = sum(item["raw_one_skip_candidates"] for item in orientations.values())
    consecutive_total = sum(item["consecutive_rank_register_windows"]
                            for item in orientations.values())
    # Counts here are per orientation. The selected provider uses one orientation
    # per replica; this is the within-orientation profile ceiling, not a pooled sum.
    need(raw_total // 2 == 67 and consecutive_total // 2 == 12 and strict_total == 0,
         "orientation-normalized candidate cap changed")
    return {
        "status": "PASS_PHASEB_ONE_SKIP_COMMUTATION_BOUND",
        "provider_archive_sha256": archive_hash,
        "phase_b_by_orientation": orientations,
        "one_skip_candidate_exact_frame_unions": common_frame_unions,
        "optimistic_block_cap_per_orientation": 79,
        "cap_derivation": "67 raw one-skip rank/register candidates + 12 consecutive rank/register windows; this deliberately waives the scalar-commutation rejection and any overlap between block windows",
        "strict_commuting_candidates_per_orientation": 0,
        "cost_screen": cost_screen(),
        "conclusion": "This one-skipped-child, register-disjoint scalar-commuting Phase B class has no valid placements. Even granting all 67 raw one-skip candidates and all 12 consecutive candidates simultaneously, the exact moment-only ceiling at 79 blocks remains below the 5-percent target. This is a scoped Phase B envelope, not a supplier, complete selected-word construction, or kappa result.",
    }


def negative_controls():
    need(structural_candidate([1, 1, 1, 3], [1, 2, 3, 4], 9),
         "synthetic structural positive control failed")
    need(not structural_candidate([1, 1, 1, 3], [1, 2, 3, 4], 3),
         "skipped-register alias negative control failed")
    selected = [1, 2, 3, 4]
    disjoint_scalar = ["scalar", ["scale", ["L", 90], 2, -1], 0]
    touching_scalar = ["scalar", ["scale", ["L", 3], 2, -1], 0]
    need(commutes_with_gap([disjoint_scalar], selected),
         "register-disjoint scalar positive control failed")
    need(not commutes_with_gap([touching_scalar], selected),
         "selected-register scalar negative control failed")
    need(hashlib.sha256(b"pinned").hexdigest() != ARCHIVE_SHA256,
         "archive-drift negative control fixture is degenerate")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-result", action="store_true",
                        help="write the computed census while preparing this package")
    args = parser.parse_args()
    negative_controls()
    result = build_result()
    if args.write_result:
        RESULT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                          encoding="utf-8")
        print("WROTE", RESULT.relative_to(ROOT))
        return
    expected = json.loads(RESULT.read_text(encoding="utf-8"))
    need(result == expected, "recomputed census/cost evidence differs from RESULT.json")
    one = result["phase_b_by_orientation"]["forward"]
    print("PASS_PHASEB_ONE_SKIP_COMMUTATION_BOUND",
          "raw=", one["raw_one_skip_candidates"],
          "commuting=", one["strict_commuting_candidates"],
          "consecutive=", one["consecutive_rank_register_windows"],
          "cap=", result["optimistic_block_cap_per_orientation"],
          "k79=", result["cost_screen"]["zero_extra_cost_ceiling_brackets"]["79"][1])


if __name__ == "__main__":
    main()
