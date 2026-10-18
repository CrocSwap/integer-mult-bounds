#!/usr/bin/env python3
"""Source-pinned variable-rank diagonal-batching budget screen.

This verifies a local schedule and its optimistic moment, not a physical child
fusion, a six-unpaid endpoint, or a selected multiplication bound.
"""
from __future__ import annotations

import bisect
import collections
import gzip
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tarfile
import tempfile
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
PREFIX = "candidate/strict/global/base/providers/gauge44/"
MEMBERS = {
    "LOCAL-PROGRAMS.json.gz": "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a",
    "CANONICAL-WORD.json.gz": "16bc0ebb04b4be6c0ade74badc6a0c0cdba4215eda86e4ff9f13abf8ecebd219",
    "INDEPENDENT-LOCAL-REPLAY.json": "13dd18297162569532983db1a2ab67926b064330cd7edd3587e7b546b2dedf17",
}
CHECKER = ROOT / "research/complex-571-cold14-k492b/code/hpe_audit_local.py"
CHECKER_PASS = "PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY"
CEILING = ROOT / "research/complex-local-word-ceiling/ceiling.py"
EXPECTED_BASE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
CAP = 51


def need(ok: bool, message: str) -> None:
    if not ok:
        raise SystemExit("FAIL: " + message)


def source_pins() -> None:
    manifest = json.loads((HERE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = ROOT / row["path"]
            need(path.is_file(), "missing input " + row["path"])
            need(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"],
                 "input hash changed: " + row["path"])


def archive_members() -> dict[str, bytes]:
    raw = ARCHIVE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == ARCHIVE_SHA, "selected archive hash")
    out: dict[str, bytes] = {}
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as tar:
        for name, digest in MEMBERS.items():
            member = tar.extractfile(PREFIX + name)
            need(member is not None, "missing archive member " + name)
            data = member.read()
            need(hashlib.sha256(data).hexdigest() == digest, "archive member hash " + name)
            out[name] = data
    return out


def load_ceiling():
    spec = importlib.util.spec_from_file_location("pinned_ceiling", CEILING)
    need(spec is not None and spec.loader is not None, "load exact ceiling engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def split_phases(events: list) -> list[tuple[list | None, list]]:
    result: list[tuple[list | None, list]] = []
    marker: list | None = None
    body: list = []
    for event in events:
        if event[0] == "phase":
            if marker is not None or body:
                result.append((marker, body))
            marker, body = event, []
        else:
            body.append(event)
    result.append((marker, body))
    return result


def touched(event: list) -> set[tuple]:
    tag = event[0]
    if tag == "climb":
        return {("L", event[2])}
    if tag in ("adapter", "residual_adapter"):
        return {("L", event[2])}
    if tag == "center":
        return {("C", event[1])}
    if tag == "scalar":
        op = event[1]
        regs = {tuple(op[1])}
        if op[0] in ("copy", "add"):
            regs.add(tuple(op[2]))
        return regs
    return set()


def profile_of(events: list) -> dict[int, int]:
    counts: collections.Counter[int] = collections.Counter()
    for event in events:
        if event[0] == "climb":
            counts[int(event[5])] += 1
        elif event[0] == "center":
            counts[int(event[4])] += 1
    return dict(sorted(counts.items()))


def make_items(body: list) -> tuple[list, dict[int, list], dict[int, int], list]:
    """Create climb intervals between consecutive skeleton touches of L-dest."""
    skeleton = [event for event in body if event[0] != "climb"]
    skeleton_size = len(skeleton)
    climbs: list[tuple[int, int, list]] = []
    gap = 0
    for event in body:
        if event[0] == "climb":
            climbs.append((len(climbs), gap, event))
        else:
            gap += 1

    touch_positions: dict[tuple, list[int]] = collections.defaultdict(list)
    for position, event in enumerate(skeleton):
        for reg in touched(event):
            touch_positions[reg].append(position)

    windows: dict[int, tuple[int, int]] = {}
    gaps: dict[int, int] = {}
    events_by_id: dict[int, list] = {}
    same_destination_window: collections.Counter = collections.Counter()
    for item_id, original_gap, event in climbs:
        positions = touch_positions[("L", event[2])]
        j = bisect.bisect_left(positions, original_gap)
        lo = positions[j - 1] + 1 if j else 0
        hi = positions[j] if j < len(positions) else skeleton_size
        windows[item_id] = (lo, hi)
        gaps[item_id] = original_gap
        events_by_id[item_id] = event
        same_destination_window[(event[2], lo, hi)] += 1

    # Repeated same-register climbs in one commute window retain their order
    # and are excluded as a group from batching.
    candidates = []
    for item_id, _, event in climbs:
        lo, hi = windows[item_id]
        if same_destination_window[(event[2], lo, hi)] == 1:
            candidates.append({
                "id": item_id,
                "rank": int(event[5]),
                "destinations": frozenset((int(event[2]),)),
                "lo": lo,
                "hi": hi,
            })
    return candidates, events_by_id, gaps, skeleton


def batch_phase(body: list, cap: int = CAP) -> dict:
    candidates, events_by_id, original_gaps, skeleton = make_items(body)
    starts: dict[int, list[int]] = collections.defaultdict(list)
    by_id = {item["id"]: item for item in candidates}
    for item in candidates:
        starts[item["lo"]].append(item["id"])

    active: set[int] = set()
    batches: list[dict] = []
    for gap in range(len(skeleton) + 1):
        active.update(starts[gap])
        while True:
            due = [item_id for item_id in active if by_id[item_id]["hi"] == gap]
            if not due:
                break
            seed = min(due, key=lambda item_id:
                       (by_id[item_id]["hi"], -by_id[item_id]["rank"], item_id))
            first = by_id[seed]
            picked = [seed]
            weight = first["rank"]
            destinations = set(first["destinations"])
            alternatives = sorted(
                (item_id for item_id in active if item_id != seed
                 and not (by_id[item_id]["destinations"] & destinations)),
                key=lambda item_id: (by_id[item_id]["hi"], -by_id[item_id]["rank"], item_id),
            )
            for item_id in alternatives:
                item = by_id[item_id]
                if weight + item["rank"] <= cap:
                    picked.append(item_id)
                    weight += item["rank"]
                    destinations.update(item["destinations"])
                    if weight == cap:
                        break
            if len(picked) >= 2:
                for item_id in picked:
                    item = by_id[item_id]
                    need(item["lo"] <= gap <= item["hi"], "batch outside a member window")
                batches.append({"gap": gap, "members": picked, "rank": weight,
                                "destinations": sorted(destinations)})
                active.difference_update(picked)
            else:
                # This singleton expires here and remains an unbatched climb.
                active.remove(seed)
        active = {item_id for item_id in active if by_id[item_id]["hi"] > gap}

    batched_ids = {item_id for batch in batches for item_id in batch["members"]}
    all_climb_ids = set(events_by_id)
    need(len(batched_ids) == sum(len(batch["members"]) for batch in batches),
         "a climb appears in more than one batch")
    scheduled: dict[int, list] = collections.defaultdict(list)
    for batch in batches:
        scheduled[batch["gap"]].append(batch)

    stays: dict[int, list[int]] = collections.defaultdict(list)
    for item_id in all_climb_ids - batched_ids:
        stays[original_gaps[item_id]].append(item_id)
    reordered: list = []
    for gap in range(len(skeleton) + 1):
        for batch in scheduled[gap]:
            # Member climbs have disjoint destinations; original order is kept
            # for a canonical, deterministic serialization.
            reordered.extend(events_by_id[item_id]
                             for item_id in sorted(batch["members"]))
        reordered.extend(events_by_id[item_id] for item_id in sorted(stays[gap]))
        if gap < len(skeleton):
            reordered.append(skeleton[gap])

    need(collections.Counter(map(json.dumps, reordered)) ==
         collections.Counter(map(json.dumps, body)), "phase event multiset changed")
    need([event for event in reordered if event[0] != "climb"] == skeleton,
         "non-climb event order changed")
    return {"batches": batches, "reordered": reordered,
            "climbs": events_by_id, "candidate_count": len(candidates),
            "climb_count": len(all_climb_ids), "batched_ids": batched_ids}


def reorder_programs(programs: dict, cap: int = CAP) -> tuple[dict, dict, dict]:
    reordered_programs = {}
    fused_profiles = {}
    summaries = {}
    for orientation, events in programs.items():
        new_events = []
        batches_all = []
        candidate_count = climb_count = 0
        phase_rows = {}
        profile = collections.Counter(profile_of(events))
        for marker, body in split_phases(events):
            if marker is not None:
                new_events.append(marker)
            result = batch_phase(body, cap)
            new_events.extend(result["reordered"])
            phase_name = marker[1] if marker else "pre_phase"
            batches = result["batches"]
            candidate_count += result["candidate_count"]
            climb_count += result["climb_count"]
            phase_rows[phase_name] = {
                "climbs": result["climb_count"],
                "unique_window_candidates": result["candidate_count"],
                "batch_count": len(batches),
                "batched_rank_mass": sum(batch["rank"] for batch in batches),
            }
            for batch in batches:
                ranks = [int(result["climbs"][item_id][5]) for item_id in batch["members"]]
                need(sum(ranks) == batch["rank"], "batch rank mass")
                need(len(batch["members"]) >= 2, "nontrivial batch")
                need(len(batch["destinations"]) == len(batch["members"]),
                     "batch destinations are not distinct")
                need(batch["rank"] <= cap, "batch exceeds rank cap")
                batches_all.append({"phase": phase_name, "gap": batch["gap"],
                                    "member_ranks": ranks, "rank": batch["rank"]})
                for rank in ranks:
                    profile[rank] -= 1
                profile[batch["rank"]] += 1
        need(collections.Counter(map(json.dumps, new_events)) ==
             collections.Counter(map(json.dumps, events)), orientation + " event multiset")
        reordered_programs[orientation] = new_events
        fused_profiles[orientation] = dict(sorted((r, n) for r, n in profile.items() if n))
        summaries[orientation] = {
            "climbs": climb_count,
            "unique_window_candidates": candidate_count,
            "batched_rank_mass": sum(batch["rank"] for batch in batches_all),
            "batch_count": len(batches_all),
            "batch_rank_histogram": dict(sorted(collections.Counter(
                batch["rank"] for batch in batches_all).items())),
            "phases": phase_rows,
        }
    need(fused_profiles["forward"] == fused_profiles["backward"],
         "orientation fused profiles disagree")
    need(summaries["forward"] == summaries["backward"], "orientation schedules disagree")
    return reordered_programs, fused_profiles, summaries


def run_local_checker(word_bytes: bytes, programs: dict) -> dict | None:
    with tempfile.TemporaryDirectory() as temporary:
        directory = Path(temporary)
        (directory / "CANONICAL-WORD.json.gz").write_bytes(word_bytes)
        with gzip.open(directory / "LOCAL-PROGRAMS.json.gz", "wt") as stream:
            json.dump(programs, stream, separators=(",", ":"))
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(CHECKER), str(directory)],
            capture_output=True, text=True, check=False,
        )
        receipt = directory / "INDEPENDENT-LOCAL-REPLAY.json"
        if result.returncode or CHECKER_PASS not in result.stdout or not receipt.is_file():
            return None
        return json.loads(receipt.read_text())


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[sum(left[i][k] * right[k][j] for k in range(len(right)))
             for j in range(len(right[0]))] for i in range(len(left))]


def block_diagonal(blocks: list[list[list[int]]]) -> list[list[int]]:
    size = sum(len(block) for block in blocks)
    out = [[0] * size for _ in range(size)]
    offset = 0
    for block in blocks:
        for i, row in enumerate(block):
            for j, value in enumerate(row):
                out[offset + i][offset + j] = value
        offset += len(block)
    return out


def check_direct_sum_identity() -> None:
    left = [[[2, 1], [0, 3]], [[1, 4, 2], [0, 2, 1], [3, 0, 1]], [[5]]]
    right = [[[1, 0], [2, 1]], [[2, 1, 0], [1, 3, 2], [0, 4, 1]], [[7]]]
    got = matmul(block_diagonal(left), block_diagonal(right))
    expected = block_diagonal([matmul(a, b) for a, b in zip(left, right)])
    need(got == expected, "heterogeneous block-diagonal multiplication identity")
    dirty = [[17 + i if i == j else 3 for j in range(6)] for i in range(6)]
    updated = [[dirty[i][j] + got[i][j] for j in range(6)] for i in range(6)]
    restored = [[updated[i][j] - got[i][j] for j in range(6)] for i in range(6)]
    need(restored == dirty, "dirty-output additive update/restore fixture")
    bad = block_diagonal(left)
    bad[0][2] = 1
    leaked = matmul(bad, block_diagonal(right))
    need(leaked[0][2] != 0, "off-diagonal input control does not detect leakage")


def main() -> None:
    source_pins()
    selected = json.loads((ROOT / "certificates/selected-result.json").read_text())
    need(selected["decimal"] == "0.001672660197076918", "selected kappa value")
    members = archive_members()
    programs = json.loads(gzip.decompress(members["LOCAL-PROGRAMS.json.gz"]))
    word = json.loads(gzip.decompress(members["CANONICAL-WORD.json.gz"]))
    pinned_local = json.loads(members["INDEPENDENT-LOCAL-REPLAY.json"])
    need(set(programs) == {"forward", "backward"}, "both selected orientations")
    for orientation, events in programs.items():
        need(len(events) == 24767, orientation + " selected event count")
        need(profile_of(events) == EXPECTED_BASE, orientation + " selected profile")

    original_receipt = run_local_checker(members["CANONICAL-WORD.json.gz"], programs)
    need(original_receipt is not None, "independent checker accepts pinned source")
    need(original_receipt["local"] == pinned_local["local"] and
         original_receipt["paid_profiles"] == pinned_local["paid_profiles"],
         "source checker receipt differs from pinned selected receipt")

    reordered, profiles, summaries = reorder_programs(programs)
    moved_receipt = run_local_checker(members["CANONICAL-WORD.json.gz"], reordered)
    need(moved_receipt is not None, "independent checker rejects the moved climbs")
    need(moved_receipt["local"] == original_receipt["local"] and
         moved_receipt["paid_profiles"] == original_receipt["paid_profiles"],
         "commuting reorder changed the unreduced local receipt")

    summary = summaries["forward"]
    need(summary["climbs"] == summary["unique_window_candidates"] == 3486,
         "all source climbs have one legal commute window")
    need(summary["batched_rank_mass"] == 5520 and summary["batch_count"] == 256,
         "weighted schedule mass/group count")
    need(profiles["forward"] == {
        2: 97, 4: 9, 6: 8, 8: 22, 9: 1, 11: 1, 12: 2, 13: 2, 14: 1,
        15: 5, 16: 15, 17: 1, 18: 1, 19: 1, 20: 2, 22: 1, 24: 2,
        25: 2, 30: 1, 40: 13, 48: 1, 49: 2, 50: 2, 51: 73,
    }, "exact weighted-batch profile")
    need(sum(r * n for r, n in profiles["forward"].items()) == 5586,
         "weighted batching preserves total rank mass")
    need(max(profiles["forward"]) == CAP and CAP == 51,
         "selected halving rank cap")
    check_direct_sum_identity()

    ceiling = load_ceiling()
    target = Q(1, 9)
    target_moments = {}
    for unpaid in (1, 5, 6):
        lower, upper = ceiling.relax(profiles["forward"], 73, 896, 9, 64,
                                     target, R=CAP, unpaid=unpaid)
        target_moments[str(unpaid)] = {"lower": str(lower), "upper": str(upper),
                                       "upper_decimal": format(float(upper), ".15f")}
    need(Q(target_moments["1"]["lower"]) > 1, "selected one-unpaid target control")
    need(Q(target_moments["5"]["lower"]) > 1, "five-unpaid target control")
    need(Q(target_moments["6"]["upper"]) < 1, "six-unpaid candidate passes at a=1/9")

    # At the target, compute the sharp integer rank-one-equivalent extra local
    # charge that can displace ideal rank-51 idle mass under this model.
    fee = 0
    while fee < 20:
        trial = dict(profiles["forward"])
        trial[1] = trial.get(1, 0) + fee
        if ceiling.relax(trial, 73, 896, 9, 64, target,
                         R=CAP, unpaid=6)[1] >= 1:
            break
        fee += 1
    need(fee == 7, "rank-one fee boundary first-fail value")
    fee_rows = {}
    for value in (fee - 1, fee):
        trial = dict(profiles["forward"])
        trial[1] = trial.get(1, 0) + value
        lo, hi = ceiling.relax(trial, 73, 896, 9, 64, target,
                               R=CAP, unpaid=6)
        fee_rows[str(value)] = {"lower": str(lo), "upper": str(hi),
                                "upper_decimal": format(float(hi), ".15f")}
    need(Q(fee_rows["6"]["upper"]) < 1 and Q(fee_rows["7"]["lower"]) > 1,
         "exact rank-one fee boundary")

    # Exact rational endpoints establish a narrow local ceiling bracket above
    # a=1/9. This remains a relaxation for the complex side only.
    a_lo, a_hi = Q(559, 5000), Q(1119, 10000)  # 0.1118 and 0.1119
    lo_moment = ceiling.relax(profiles["forward"], 73, 896, 9, 64,
                              a_lo, R=CAP, unpaid=6)
    hi_moment = ceiling.relax(profiles["forward"], 73, 896, 9, 64,
                              a_hi, R=CAP, unpaid=6)
    need(lo_moment[1] < 1 and hi_moment[0] > 1, "local ceiling bracket")

    result = {
        "status": "PASS_COMPLEX_WEIGHTED_DIAGONAL_RANK51_SCREEN; no supplier or selected kappa claim",
        "selected_kappa": selected["decimal"],
        "target_kappa": "1/10",
        "target_primitive_saving_a": "1/9",
        "candidate": {
            "orientation_summaries": summaries,
            "fused_local_profile": {str(r): n for r, n in profiles["forward"].items()},
            "rank_mass_before_and_after": 5586,
            "weighted_batches": 256,
            "climb_rank_mass_batched": 5520,
            "climb_rank_mass_total": 5522,
            "rank_cap": CAP,
            "unpaid_coordinates": 6,
            "centre_mass": 64,
            "moment_at_target": target_moments,
            "extra_rank_one_fee_boundary": {
                "idle_displacing_convention": True,
                "six_passes_seven_fails": fee_rows,
            },
            "local_ceiling_a_bracket": {
                "lower_passes": str(a_lo), "upper_passes": str(lo_moment[1]),
                "first_tested_fail": str(a_hi), "lower_fail_moment": str(hi_moment[0]),
                "kappa_lower_from_a_lower": str(a_lo / (1 + a_lo)),
                "kappa_upper_from_first_tested_fail": str(a_hi / (1 + a_hi)),
            },
        },
        "checks": [
            "both source orientations and original paid profile reconstructed",
            "every climb commute window computed from the pinned event stream",
            "weighted batches have intersecting windows, distinct destinations and rank sum at most 51",
            "independent scalar/frame/wrapper checker accepts the reordered un-fused climbs",
            "heterogeneous block-diagonal product identity and dirty additive control",
            "exact outward-rational target moments and fee boundary",
        ],
        "limits": [
            "The six-unpaid coverage law is hypothetical; no six-plane or other dirty-input endpoint is constructed.",
            "The batch profile assumes zero charge for gathering, frames, hosting, precision, output delivery and restoration.",
            "The rank-sum child is justified only by the generic direct-sum algebra; selected physical fusion is not implemented.",
            "The complex-side relaxation does not price or improve the separate bit supplier, so selected kappa is unchanged.",
            "The 6-unit fee allowance displaces ideal rank-51 idle mass and is not a realized interface invoice.",
            "The outer all-size/compiler, global hosting and transfer obligations remain inherited and unproved here.",
        ],
    }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    check_direct_sum_identity()
    print("PASS_COMPLEX_WEIGHTED_DIAGONAL_RANK51_SCREEN")
    print("  groups=256; batched climb mass=5520/5522; profile mass=5586")
    print("  target a=1/9 moment upper=", target_moments["6"]["upper_decimal"])
    print("  rank-one-equivalent added fee: 6 passes, 7 fails")
    print("  no supplier, selected kappa change, or bit-side claim")


if __name__ == "__main__":
    main()
