#!/usr/bin/env python3
"""Exact scoped screen for three-output shared-source child windows."""
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PKG = Path(__file__).resolve().parent
BASE = "0b1cccf86e2f5132ed286a26ef0a681a495740ea"
CATALOG_SHA = "6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075"
SELECTED_SHA = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
WORD_PATH = "research/r480-owner-optimum/inputs/local/FULL-WORD.json.gz"
WORD_COMPRESSED_SHA = "49596aa4ed4fd36cd4582fd0e8ddeb09fd80370a7d8aea1ede52a135b536d289"
WORD_SHA = "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8"
SLOT_PIN_PATH = "research/gauge44-slots/construction/slots/SLOT-PINS-k8.json"
MANIFEST_SHA = "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b"
ASSEMBLY_SHA = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"
CEILING_PATH = "research/complex-local-word-ceiling/ceiling.py"
M, FAMILIES, STAGES, CENTRE = 73, 896, 9, 64
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def load_ceiling_module():
    path = ROOT / CEILING_PATH
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    require(spec is not None and spec.loader is not None, "cannot load pinned ceiling module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def span(vectors):
    """Canonical F2 row space as a descending-pivot tuple of integer masks."""
    pivots = {}
    for value in vectors:
        require(type(value) is int and value >= 0, "frame vector must be a nonnegative integer")
        x = value
        for pivot in sorted(pivots, reverse=True):
            if (x >> pivot) & 1:
                x ^= pivots[pivot]
        if x:
            pivot = x.bit_length() - 1
            for k in tuple(pivots):
                if (pivots[k] >> pivot) & 1:
                    pivots[k] ^= x
            pivots[pivot] = x
    return tuple(pivots[k] for k in sorted(pivots, reverse=True))


def rank(vectors):
    return len(span(vectors))


def touched_registers(operation):
    require(isinstance(operation, list) and len(operation) >= 2, "malformed word operation")
    if operation[0] == "add":
        require(len(operation) >= 6, "malformed add operation")
        return [operation[1], operation[2]]
    return [operation[1]]


def advance_one(current, operation, target, profile):
    touched = touched_registers(operation)
    deltas = []
    old_frames = []
    for register in touched:
        require(type(register) is int and 0 <= register < len(current), "register out of range")
        old = current[register]
        require(span(list(old) + list(target)) == target, "word frame is not monotone at an operation")
        delta = rank(target) - rank(old)
        require(delta >= 0, "negative frame increment")
        deltas.append(delta)
        old_frames.append(old)
    for delta in deltas:
        if delta:
            profile[delta] += 1
    for register in touched:
        current[register] = target
    return old_frames, deltas


def candidate_from_rows(section, start, rows):
    """Return a C3 window or None. Rows are three chronological gate records."""
    if len(rows) != 3:
        return None
    operations = [row["operation"] for row in rows]
    if not all(isinstance(op, list) and op and op[0] == "add" for op in operations):
        return None
    sources = [op[2] for op in operations]
    destinations = [op[1] for op in operations]
    if len(set(sources)) != 1 or sources[0] in destinations or len(set(destinations)) != 3:
        return None
    source = sources[0]
    source_deltas = [row["deltas"][1] for row in rows]
    target_ranks = [row["deltas"][0] for row in rows]
    if source_deltas != [0, 0, 0] or sum(x > 0 for x in target_ranks) < 2:
        return None
    source_frame = rows[0]["old_frames"][1]
    if any(row["old_frames"][1] != source_frame for row in rows):
        return None
    for row in rows:
        if span(list(source_frame) + list(row["target"])) != row["target"]:
            return None
    child_rank = sum(target_ranks)
    if not 0 < child_rank < M:
        return None
    coefficients = []
    for op in operations:
        try:
            coefficient = Q(op[3], op[4])
        except (TypeError, ZeroDivisionError) as exc:
            raise ValueError("bad exact ADD coefficient") from exc
        require(coefficient != 0, "zero ADD coefficient in candidate")
        coefficients.append(str(coefficient))
    item = {
        "section": section,
        "start": start,
        "indices": [start, start + 1, start + 2],
        "source": source,
        "targets": destinations,
        "coefficients": coefficients,
        "target_ranks": target_ranks,
        "joint_rank": child_rank,
        "source_frame_rank": rank(source_frame),
        "target_frame_ranks": [rank(row["target"]) for row in rows],
    }
    verify_fanout_map(item)
    return item


def matmul(left, right):
    require(left and right and len(left[0]) == len(right), "matrix dimension mismatch")
    return [[sum((left[i][k] * right[k][j] for k in range(len(right))), Q(0))
             for j in range(len(right[0]))] for i in range(len(left))]


def fanout_matrices(coefficients):
    require(len(coefficients) == 3, "C3 needs three output coefficients")
    cs = [Q(value) for value in coefficients]
    forward = [[Q(int(i == j)) for j in range(4)] for i in range(4)]
    inverse = [[Q(int(i == j)) for j in range(4)] for i in range(4)]
    for i, coefficient in enumerate(cs, start=1):
        forward[i][0] += coefficient
        inverse[i][0] -= coefficient
    return forward, inverse


def verify_fanout_map(candidate):
    forward, inverse = fanout_matrices(candidate["coefficients"])
    identity = [[Q(int(i == j)) for j in range(4)] for i in range(4)]
    require(matmul(forward, inverse) == identity and matmul(inverse, forward) == identity,
            "C3 map does not preserve arbitrary dirty inputs invertibly")
    return True


def load_sources():
    manifest = json.loads((PKG / "SOURCES.json").read_text())
    require(manifest.get("schema_version") == 1, "unsupported source manifest")
    require(manifest.get("base_commit") == BASE, "wrong exact base commit")
    for item in manifest.get("files", []):
        path = ROOT / item["path"]
        require(path.is_file(), "missing pinned source: " + item["path"])
        require(sha256(path.read_bytes()) == item["sha256"], "source hash mismatch: " + item["path"])
    selected_path = ROOT / "certificates/selected-result.json"
    require(sha256(selected_path.read_bytes()) == SELECTED_SHA, "selected record changed")
    source_manifest = ROOT / "research/community-frontier1094-audit/SELECTED-SOURCE.json"
    assembly = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
    require(sha256(source_manifest.read_bytes()) == MANIFEST_SHA, "selected source manifest changed")
    require(sha256(assembly.read_bytes()) == ASSEMBLY_SHA, "selected assembly certificate changed")
    selected = json.loads(selected_path.read_text())
    require(selected.get("certificate_sha256") == ASSEMBLY_SHA, "selected record/certificate binding mismatch")
    word_path = ROOT / WORD_PATH
    compressed = word_path.read_bytes()
    require(sha256(compressed) == WORD_COMPRESSED_SHA, "compressed selected word changed")
    raw = gzip.decompress(compressed)
    require(sha256(raw) == WORD_SHA, "decompressed selected word changed")
    slot_pins = json.loads((ROOT / SLOT_PIN_PATH).read_text())
    require(slot_pins.get("word_sha256") == WORD_SHA, "selected slot output does not pin this word")
    word = json.loads(raw)
    return word, manifest


def reconstruct_word(word):
    report = word.get("report", {})
    require(report.get("m") == M and report.get("h") == 9, "wrong selected word dimensions")
    v, helpers = report.get("v"), report.get("R")
    require(type(v) is int and type(helpers) is int and v == 112 and helpers == 480,
            "wrong selected word port/helper inventory")
    n_registers = 2 * v + helpers
    current = [tuple() for _ in range(n_registers)]
    profile = Counter()
    for i, port in enumerate(word["ports"]):
        current[i] = span([port])
    for register, frame in word.get("start_extra", {}).items():
        current[int(register)] = span(frame)

    section_rows = {}
    operation_counts = {}
    for section in ("A", "B"):
        rows = []
        operations = word.get(section)
        require(isinstance(operations, list), "missing word section " + section)
        for index, operation in enumerate(operations):
            target = span(operation[-1])
            old_frames, deltas = advance_one(current, operation, target, profile)
            rows.append({"operation": operation, "target": target,
                         "old_frames": old_frames, "deltas": deltas})
        section_rows[section] = rows
        operation_counts[section] = len(operations)

    for cleanup_index, frame in word.get("early_cleanup", []):
        operation = word["cleanup"][cleanup_index]
        target = span(frame)
        advance_one(current, operation, target, profile)

    full = span([1 << i for i in range(9)])
    final_frames = {int(register): span(frame)
                    for register, frame in word.get("helper_final", {}).items()}
    for register in range(n_registers):
        if v <= register < 2 * v:
            port = word["ports"][register - v]
            target = span([x for x in range(1, 512) if (x & port).bit_count() % 2 == 0])
        else:
            target = final_frames.get(register, full)
        old = current[register]
        require(span(list(old) + list(target)) == target, "nonmonotone terminal frame")
        delta = rank(target) - rank(old)
        require(delta >= 0, "negative terminal frame increment")
        if delta:
            profile[delta] += 1
        current[register] = target

    profile.update(Counter(report.get("centre_ranks", [])))
    require({int(k): int(value) for k, value in report.get("local_profile", {}).items()} == BASE_PROFILE,
            "selected word report has unexpected local profile")
    require(dict(sorted(profile.items())) == BASE_PROFILE, "reconstructed full local profile mismatch")
    return section_rows, operation_counts, n_registers, profile


def enumerate_windows(section_rows):
    found = {}
    for section, rows in section_rows.items():
        items = []
        for start in range(len(rows) - 2):
            candidate = candidate_from_rows(section, start, rows[start:start + 3])
            if candidate is not None:
                items.append(candidate)
        found[section] = items
    return found


def saving_upper(candidate, ceiling, saving):
    ranks = [r for r in candidate["target_ranks"] if r]
    direct_upper = sum((ceiling.child_cost(r, M, saving)[1] for r in ranks), Q(0))
    joint_lower = ceiling.child_cost(candidate["joint_rank"], M, saving)[0]
    weight = direct_upper - joint_lower
    require(weight > 0, "candidate lacks a certified positive ideal moment saving")
    return weight


def weighted_schedule(candidates, operation_count, weights):
    """Exact maximum-weight non-overlapping intervals, each covering 3 gates."""
    by_start = {item["start"]: item for item in candidates}
    require(len(by_start) == len(candidates), "duplicate candidate start")
    values = [Q(0)] * (operation_count + 1)
    choices = [[] for _ in range(operation_count + 1)]
    for end in range(1, operation_count + 1):
        values[end] = values[end - 1]
        choices[end] = choices[end - 1]
        start = end - 3
        if start >= 0 and start in by_start:
            candidate_value = values[start] + weights[start]
            if candidate_value > values[end]:
                values[end] = candidate_value
                choices[end] = choices[start] + [by_start[start]]
    return values[operation_count], choices[operation_count]


def profile_after(groups, baseline=BASE_PROFILE):
    result = Counter(baseline)
    for group in groups:
        ranks = group["target_ranks"]
        require(len(ranks) == 3 and group["joint_rank"] == sum(ranks), "bad C3 profile record")
        for r in ranks:
            if r:
                result[r] -= 1
                require(result[r] >= 0, "profile removes a missing child")
        result[group["joint_rank"]] += 1
    return {rank_value: count for rank_value, count in sorted(result.items()) if count}


def compute_certificate():
    word, source_manifest = load_sources()
    section_rows, operation_counts, n_registers, reconstructed = reconstruct_word(word)
    candidates_by_section = enumerate_windows(section_rows)
    ceiling = load_ceiling_module()
    baseline_lo, baseline_hi = ceiling.ceiling(BASE_PROFILE, M, FAMILIES, STAGES, CENTRE)
    target_saving = baseline_hi * Q(105, 100)
    baseline_moment = ceiling.relax(BASE_PROFILE, M, FAMILIES, STAGES, CENTRE, target_saving)
    require(baseline_moment[0] > 1, "five-percent target is not above the baseline ceiling")

    max_saving = Q(0)
    max_group_count = 0
    selected = []
    per_section = {}
    all_candidates = []
    for section in ("A", "B"):
        candidates = candidates_by_section[section]
        all_candidates.extend(candidates)
        weights = {item["start"]: saving_upper(item, ceiling, target_saving)
                   for item in candidates}
        saving, chosen = weighted_schedule(candidates, operation_counts[section], weights)
        max_saving += saving
        selected.extend(chosen)
        count_weights = {item["start"]: Q(1) for item in candidates}
        count, count_chosen = weighted_schedule(candidates, operation_counts[section], count_weights)
        max_group_count += int(count)
        patterns = Counter(tuple(item["target_ranks"]) for item in candidates)
        per_section[section] = {
            "operation_count": operation_counts[section],
            "candidate_windows": len(candidates),
            "candidate_rank_patterns": {",".join(map(str, key)): patterns[key]
                                        for key in sorted(patterns)},
            "max_nonoverlap_windows": len(count_chosen),
            "max_weight_windows": len(chosen),
        }

    maximum_saving_normalized = max_saving / Q(FAMILIES, STAGES)
    best_moment_lower = ceiling.down(baseline_moment[0] - maximum_saving_normalized)
    margin = best_moment_lower - 1
    require(margin > 0, "bounded C3 family may pass the five-percent screen")

    candidate_profile = profile_after(selected)
    baseline_mass = sum(r * count for r, count in BASE_PROFILE.items())
    candidate_mass = sum(r * count for r, count in candidate_profile.items())
    require(baseline_mass == candidate_mass == 5586, "rank mass changed under C3 replacement")
    candidate_lo, candidate_hi = ceiling.ceiling(candidate_profile, M, FAMILIES, STAGES, CENTRE)
    gain_percent = (candidate_hi / baseline_hi - 1) * 100

    certificate = {
        "status": "PASS_SCOPED_C3_FANOUT_OBSTRUCTION",
        "base_commit": BASE,
        "priority_revision": 3,
        "seed": "c309ff190ac582a9bdcf59a3422822e8",
        "track": "complex-mechanisms",
        "task_id": "complex-new-helper-inventory",
        "catalog_sha256": CATALOG_SHA,
        "selected_record_sha256": SELECTED_SHA,
        "selected_source_manifest_sha256": MANIFEST_SHA,
        "selected_assembly_sha256": ASSEMBLY_SHA,
        "source_word": {
            "path": WORD_PATH,
            "compressed_sha256": WORD_COMPRESSED_SHA,
            "decompressed_sha256": WORD_SHA,
            "m": M,
            "ports": word["report"]["v"],
            "helpers": word["report"]["R"],
            "registers": n_registers,
            "operations": operation_counts,
        },
        "baseline_profile": {str(k): v for k, v in sorted(reconstructed.items())},
        "baseline_rank_mass": baseline_mass,
        "baseline_ceiling_a": [str(baseline_lo), str(baseline_hi)],
        "five_percent_target_a": str(target_saving),
        "baseline_moment_at_target": [str(baseline_moment[0]), str(baseline_moment[1])],
        "candidate_windows": all_candidates,
        "candidate_windows_by_section": per_section,
        "maximum_disjoint_window_count": max_group_count,
        "maximum_saving_upper_unscaled": str(max_saving),
        "maximum_saving_upper_normalized": str(maximum_saving_normalized),
        "best_possible_moment_lower_at_target": str(best_moment_lower),
        "strict_margin_above_one": str(margin),
        "max_weight_schedule": selected,
        "max_weight_schedule_profile": {str(k): v for k, v in candidate_profile.items()},
        "max_weight_schedule_rank_mass": candidate_mass,
        "max_weight_schedule_ceiling_a": [str(candidate_lo), str(candidate_hi)],
        "max_weight_schedule_gain_percent_upper": str(gain_percent),
        "per_group_exact_maps_verified": len(all_candidates),
        "cost_ledger": {
            "charged": "Each candidate replaces its positive target climbs t1,t2,t3 by one rank R=t1+t2+t3 child; source and target ranks remain fully represented in the transformed profile.",
            "assumed_zero_for_favorable_screen": [
                "extra source copies or fanout adapters",
                "new helper capacity or helper operations",
                "additional source-read cost",
                "additional frame transitions beyond the transformed profile",
                "restoration cost",
                "precision or phase conversion",
                "whole-call hosting and owner changes",
            ],
            "interpretation": "The C3 child interface is hypothetical. The negative result is stronger than a physical-cost failure: even the zero-overhead rank profile misses the five-percent gate."
        },
        "scope": "All length-three windows of consecutive ADDs within A or B having one stable source register/value, three distinct destination registers, zero source-frame increment at each gate, and at least two positive destination-frame increments; schedules are arbitrary non-overlapping subsets of this exact finite set.",
        "limits": [
            "No claim about nonconsecutive or reordered gates, other fanout arities, other local words, or changed coverage laws.",
            "No physically admitted C3 supplier or new kappa is claimed.",
            "This does not prove that all shared-source or block-climb interfaces fail."
        ]
    }
    return certificate


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    write = argv == ["--write"]
    require(not argv or write, "usage: verify.py [--write]")
    certificate = compute_certificate()
    path = PKG / "CERTIFICATE.json"
    if write:
        path.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n")
    else:
        require(path.is_file(), "missing CERTIFICATE.json; run verify.py --write once")
        recorded = json.loads(path.read_text())
        require(recorded == certificate, "CERTIFICATE.json differs from exact replay")
    pct = float(Q(certificate["max_weight_schedule_gain_percent_upper"]))
    raw = sum(x["candidate_windows"] for x in certificate["candidate_windows_by_section"].values())
    print(f"PASS_SCOPED_C3_FANOUT_OBSTRUCTION windows={raw} max_nonoverlap={certificate['maximum_disjoint_window_count']} gain={pct:.10f}%")
    print("PASS_C3_ARBITRARY_DIRTY_MAPS count=" + str(certificate["per_group_exact_maps_verified"]))
    print("LIMIT consecutive selected-word domain only; zero adapter/restoration/hosting charges; no supplier admission or new kappa")


if __name__ == "__main__":
    main()
