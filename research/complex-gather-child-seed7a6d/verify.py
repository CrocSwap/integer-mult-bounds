#!/usr/bin/env python3
"""Exact bounded screen for three-source, one-destination gather children."""
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
SEED = "7a6da0d3a89bdb0425f85454db15342b"
CATALOG_SHA = "6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075"
SELECTED_SHA = "10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32"
MANIFEST_SHA = "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b"
ASSEMBLY_SHA = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"
REVIEW_SHA = "7e76d2c38e5fce30587835b7251df1430488ae4dd372611ef69a3f03f476b6cb"
CEILING_SHA = "86a1432870b3b21d8454106ec9162fddc0471472d9214c590a1420f2426cedfc"
SLOT_PIN_SHA = "55dd229684febecb80638eff9c6b3986623e8539c6c956753b350209c3e0efe2"
WORD_PATH = "research/r480-owner-optimum/inputs/local/FULL-WORD.json.gz"
WORD_COMPRESSED_SHA = "49596aa4ed4fd36cd4582fd0e8ddeb09fd80370a7d8aea1ede52a135b536d289"
WORD_SHA = "c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8"
SLOT_PIN_PATH = "research/gauge44-slots/construction/slots/SLOT-PINS-k8.json"
M, FAMILIES, STAGES, CENTRE = 73, 896, 9, 64
BASE_PROFILE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
EXPECTED_COUNTS = {"A": 3451, "B": 1846}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def span(vectors):
    """Canonical F2 row space as descending-pivot integer masks."""
    pivots = {}
    for value in vectors:
        require(type(value) is int and value >= 0, "frame vector must be a nonnegative integer")
        x = value
        for pivot in sorted(pivots, reverse=True):
            if (x >> pivot) & 1:
                x ^= pivots[pivot]
        if x:
            pivot = x.bit_length() - 1
            for key in tuple(pivots):
                if (pivots[key] >> pivot) & 1:
                    pivots[key] ^= x
            pivots[pivot] = x
    return tuple(pivots[key] for key in sorted(pivots, reverse=True))


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
    deltas, old_frames = [], []
    for register in touched:
        require(type(register) is int and 0 <= register < len(current), "register out of range")
        old = current[register]
        require(span(list(old) + list(target)) == target, "word frame is not monotone")
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


def load_sources():
    sources = json.loads((PKG / "SOURCES.json").read_text())
    require(sources.get("schema_version") == 1 and sources.get("base_commit") == BASE,
            "wrong source-manifest base")
    for item in sources["files"]:
        path = ROOT / item["path"]
        require(path.is_file(), "missing pinned input: " + item["path"])
        require(sha256(path.read_bytes()) == item["sha256"], "working source hash mismatch: " + item["path"])
    require(sources["files"][1]["sha256"] == CATALOG_SHA, "catalogue hash changed")
    require(sources["files"][2]["sha256"] == REVIEW_SHA, "selected review hash changed")
    require(sources["files"][3]["sha256"] == ASSEMBLY_SHA, "selected assembly hash changed")
    require(sources["files"][4]["sha256"] == MANIFEST_SHA, "selected source manifest hash changed")
    require(sources["files"][5]["sha256"] == CEILING_SHA, "ceiling implementation hash changed")
    require(sources["files"][6]["sha256"] == SLOT_PIN_SHA, "slot pin hash changed")

    selected_path = ROOT / "certificates/selected-result.json"
    selected_bytes = selected_path.read_bytes()
    require(sha256(selected_bytes) == SELECTED_SHA, "selected record changed")
    selected = json.loads(selected_bytes)
    require(selected.get("certificate_sha256") == ASSEMBLY_SHA, "selected record/certificate binding mismatch")

    compressed = (ROOT / WORD_PATH).read_bytes()
    require(sha256(compressed) == WORD_COMPRESSED_SHA, "compressed local word changed")
    raw = gzip.decompress(compressed)
    require(sha256(raw) == WORD_SHA, "decompressed local word changed")
    slot_pins = json.loads((ROOT / SLOT_PIN_PATH).read_text())
    require(slot_pins.get("word_sha256") == WORD_SHA, "slot pin does not identify this word")
    word = json.loads(raw)
    return word


def reconstruct_word(word):
    report = word.get("report", {})
    require(report.get("m") == M and report.get("h") == STAGES, "wrong local word dimensions")
    v, helpers = report.get("v"), report.get("R")
    require(v == 112 and helpers == 480, "wrong port/helper inventory")
    count = 2 * v + helpers
    current = [tuple() for _ in range(count)]
    for index, port in enumerate(word["ports"]):
        current[index] = span([port])
    for register, frame in word.get("start_extra", {}).items():
        current[int(register)] = span(frame)

    section_rows, op_counts = {}, {}
    profile = Counter()
    for section in ("A", "B"):
        rows = []
        operations = word.get(section)
        require(isinstance(operations, list) and len(operations) == EXPECTED_COUNTS[section],
                "wrong section operation inventory: " + section)
        for index, operation in enumerate(operations):
            target = span(operation[-1])
            old_frames, deltas = advance_one(current, operation, target, profile)
            rows.append({"operation": operation, "target": target,
                         "old_frames": old_frames, "deltas": deltas})
        section_rows[section] = rows
        op_counts[section] = len(operations)

    for cleanup_index, frame in word.get("early_cleanup", []):
        operation = word["cleanup"][cleanup_index]
        advance_one(current, operation, span(frame), profile)

    full = span([1 << bit for bit in range(9)])
    final_frames = {int(register): span(frame) for register, frame in word.get("helper_final", {}).items()}
    for register in range(count):
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
    reported = {int(key): int(value) for key, value in report.get("local_profile", {}).items()}
    require(reported == BASE_PROFILE, "report local profile changed")
    require(dict(sorted(profile.items())) == BASE_PROFILE, "independently reconstructed full profile mismatch")
    return section_rows, op_counts, count, dict(sorted(profile.items()))


def gather_matrices(coefficients):
    require(len(coefficients) == 3, "three-source gather needs three coefficients")
    values = [Q(value) for value in coefficients]
    forward = [[Q(int(row == col)) for col in range(4)] for row in range(4)]
    inverse = [[Q(int(row == col)) for col in range(4)] for row in range(4)]
    for index, coefficient in enumerate(values, start=1):
        forward[0][index] += coefficient
        inverse[0][index] -= coefficient
    return forward, inverse


def matmul(left, right):
    require(left and right and len(left[0]) == len(right), "matrix shape mismatch")
    return [[sum((left[i][k] * right[k][j] for k in range(len(right))), Q(0))
             for j in range(len(right[0]))] for i in range(len(left))]


def matvec(matrix, vector):
    return [sum((matrix[i][j] * vector[j] for j in range(len(vector))), Q(0))
            for i in range(len(matrix))]


def verify_gather_map(candidate):
    forward, inverse = gather_matrices(candidate["coefficients"])
    identity = [[Q(int(i == j)) for j in range(4)] for i in range(4)]
    require(matmul(forward, inverse) == identity and matmul(inverse, forward) == identity,
            "gather map is not exactly invertible on arbitrary dirty registers")
    return True


def candidate_from_rows(section, start, rows):
    """Recognize three same-value source writes to one destination."""
    if len(rows) != 3:
        return None
    operations = [row["operation"] for row in rows]
    if not all(isinstance(op, list) and op and op[0] == "add" for op in operations):
        return None
    destinations = [op[1] for op in operations]
    sources = [op[2] for op in operations]
    if len(set(destinations)) != 1 or len(set(sources)) != 3:
        return None
    destination = destinations[0]
    if destination in sources:
        return None
    frame_ranks = [list(row["deltas"]) for row in rows]
    positive_ranks = [value for pair in frame_ranks for value in pair if value > 0]
    if len(positive_ranks) < 2:
        return None
    coefficients = []
    for operation in operations:
        try:
            coefficient = Q(operation[3], operation[4])
        except (TypeError, ZeroDivisionError) as exc:
            raise ValueError("invalid exact ADD coefficient") from exc
        coefficients.append(str(coefficient))
    target_total = rank(rows[-1]["target"]) - rank(rows[0]["old_frames"][0])
    source_total = sum(rank(row["target"]) - rank(row["old_frames"][1]) for row in rows)
    joint_rank = target_total + source_total
    require(joint_rank == sum(positive_ranks), "touched-register frame increments do not telescope")
    candidate = {
        "section": section,
        "start": start,
        "indices": [start, start + 1, start + 2],
        "destination": destination,
        "sources": sources,
        "coefficients": coefficients,
        "frame_ranks": frame_ranks,
        "positive_ranks": positive_ranks,
        "joint_rank": joint_rank,
        "source_frame_ranks": [rank(row["old_frames"][1]) for row in rows],
        "target_frame_ranks": [rank(row["target"]) for row in rows],
    }
    for row in rows:
        require(span(list(row["old_frames"][1]) + list(row["target"])) == row["target"],
                "source value is not available in the destination frame")
    verify_gather_map(candidate)
    return candidate


def enumerate_windows(section_rows):
    result = {}
    for section, rows in section_rows.items():
        candidates = []
        for start in range(len(rows) - 2):
            candidate = candidate_from_rows(section, start, rows[start:start + 3])
            if candidate is not None:
                candidates.append(candidate)
        result[section] = candidates
    return result


def weighted_schedule(candidates, operation_count, weights):
    """Exact interval DP. Windows are length three; gate indices may not overlap."""
    by_start = {item["start"]: item for item in candidates}
    require(len(by_start) == len(candidates), "duplicate candidate start")
    values = [Q(0)] * (operation_count + 1)
    choices = [[] for _ in range(operation_count + 1)]
    for end in range(1, operation_count + 1):
        values[end] = values[end - 1]
        choices[end] = choices[end - 1]
        start = end - 3
        if start >= 0 and start in by_start:
            value = values[start] + weights[start]
            if value > values[end]:
                values[end] = value
                choices[end] = choices[start] + [by_start[start]]
    return values[-1], choices[-1]


def profile_after(groups, baseline=BASE_PROFILE):
    result = Counter(baseline)
    for group in groups:
        ranks = group["positive_ranks"]
        require(group["joint_rank"] == sum(ranks), "bad gather rank record")
        for value in ranks:
            if value:
                result[value] -= 1
                require(result[value] >= 0, "candidate schedule removes absent rank mass")
        result[group["joint_rank"]] += 1
    return {value: count for value, count in sorted(result.items()) if count}


def load_ceiling():
    path = ROOT / "research/complex-local-word-ceiling/ceiling.py"
    spec = importlib.util.spec_from_file_location("pinned_gather_ceiling", path)
    require(spec is not None and spec.loader is not None, "cannot load pinned ceiling routine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def saving_upper(candidate, ceiling, target_a):
    positive = candidate["positive_ranks"]
    direct_upper = sum((ceiling.child_cost(value, M, target_a)[1] for value in positive), Q(0))
    joint_lower = ceiling.child_cost(candidate["joint_rank"], M, target_a)[0]
    saving = direct_upper - joint_lower
    require(saving > 0, "qualified gather window does not lower the ideal q-moment")
    return saving


def compute_certificate():
    word = load_sources()
    section_rows, op_counts, register_count, reconstructed = reconstruct_word(word)
    candidates_by_section = enumerate_windows(section_rows)
    ceiling = load_ceiling()
    baseline_lo, baseline_hi = ceiling.ceiling(BASE_PROFILE, M, FAMILIES, STAGES, CENTRE)
    target_a = baseline_hi * Q(105, 100)
    baseline_moment = ceiling.relax(BASE_PROFILE, M, FAMILIES, STAGES, CENTRE, target_a)
    require(baseline_moment[0] > 1, "five-percent target is below baseline ceiling")

    all_candidates, chosen, per_section = [], [], {}
    maximum_saving = Q(0)
    maximum_count = 0
    for section in ("A", "B"):
        candidates = candidates_by_section[section]
        all_candidates.extend(candidates)
        weights = {item["start"]: saving_upper(item, ceiling, target_a) for item in candidates}
        section_saving, selected = weighted_schedule(candidates, op_counts[section], weights)
        maximum_saving += section_saving
        chosen.extend(selected)
        _, count_choice = weighted_schedule(candidates, op_counts[section],
                                             {item["start"]: Q(1) for item in candidates})
        maximum_count += len(count_choice)
        patterns = Counter((item["joint_rank"], tuple(tuple(row) for row in item["frame_ranks"]))
                           for item in candidates)
        per_section[section] = {
            "operation_count": op_counts[section],
            "candidate_windows": len(candidates),
            "rank_patterns": {json.dumps(key, separators=(",", ":")): patterns[key]
                              for key in sorted(patterns)},
            "maximum_nonoverlap_window_count": len(count_choice),
            "maximum_saving_schedule_window_count": len(selected),
        }

    normalized_saving = maximum_saving / Q(FAMILIES, STAGES)
    best_moment_lower = ceiling.down(baseline_moment[0] - normalized_saving)
    margin = best_moment_lower - 1
    transformed = profile_after(chosen)
    baseline_mass = sum(value * count for value, count in BASE_PROFILE.items())
    transformed_mass = sum(value * count for value, count in transformed.items())
    require(baseline_mass == transformed_mass == 5586, "gather replacement changed rank mass")
    candidate_lo, candidate_hi = ceiling.ceiling(transformed, M, FAMILIES, STAGES, CENTRE)
    gain_percent = (candidate_hi / baseline_hi - 1) * 100

    return {
        "status": "SCOPED_GATHER_SCREEN",
        "base_commit": BASE,
        "seed": SEED,
        "track": "complex-mechanisms",
        "task_id": "complex-rank-shape-decoder",
        "priority_revision": 3,
        "catalog_sha256": CATALOG_SHA,
        "selected_record_sha256": SELECTED_SHA,
        "selected_source_manifest_sha256": MANIFEST_SHA,
        "selected_assembly_sha256": ASSEMBLY_SHA,
        "source_word": {
            "path": WORD_PATH,
            "compressed_sha256": WORD_COMPRESSED_SHA,
            "decompressed_sha256": WORD_SHA,
            "m": M,
            "ports": 112,
            "helpers": 480,
            "registers": register_count,
            "operations": op_counts,
        },
        "reconstructed_base_profile": reconstructed,
        "baseline_profile": BASE_PROFILE,
        "baseline_rank_mass": baseline_mass,
        "baseline_ceiling_a": [str(baseline_lo), str(baseline_hi)],
        "screen_target_a": str(target_a),
        "baseline_moment_at_target": [str(baseline_moment[0]), str(baseline_moment[1])],
        "candidate_windows_by_section": per_section,
        "candidate_windows": all_candidates,
        "maximum_disjoint_window_count": maximum_count,
        "max_saving_schedule": chosen,
        "max_saving_schedule_profile": transformed,
        "max_saving_schedule_rank_mass": transformed_mass,
        "max_saving_schedule_ceiling_a": [str(candidate_lo), str(candidate_hi)],
        "max_saving_schedule_gain_percent": str(gain_percent),
        "maximum_saving_upper_normalized": str(normalized_saving),
        "best_possible_moment_lower_at_target": str(best_moment_lower),
        "strict_margin_above_one": str(margin),
        "screen_passes_five_percent": margin <= 0,
        "per_group_exact_maps_verified": len(all_candidates),
        "cost_ledger": {
            "charged": "Each selected gather window replaces every positive destination and source frame increment across its three gates by one rank-R child, where R is the sum of all those increments.",
            "assumed_zero_for_favorable_screen": [
                "three source reads and collection into one gather child",
                "extra source copies or fanout adapters",
                "new helper capacity or helper operations",
                "additional frame transitions",
                "restoration cost",
                "precision or phase conversion",
                "whole-call hosting and owner changes",
            ],
            "interpretation": "Source values remain fixed, but their frame increments are included in R. The gather-child interface is hypothetical. The screen is a favorable rank-profile bound; a passing ceiling would still require a physical implementation and complete invoice."
        },
        "scope": "All length-three windows of consecutive ADDs within A or B having one common destination, three distinct source registers different from the destination, and at least two positive frame increments across the three destination/source register pairs; schedules are arbitrary non-overlapping subsets of this exact finite set.",
        "limits": [
            "No claim about nonconsecutive or reordered gates, other gather arities, other words, or changed coverage laws.",
            "No physical multi-source child, supplier admission, or new kappa is claimed.",
            "The non-overlap schedule ignores additional register or interface conflicts and is therefore deliberately favorable."
        ]
    }


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
        canonical = json.loads(json.dumps(certificate, sort_keys=True))
        require(recorded == canonical, "CERTIFICATE.json differs from exact replay")
    count = sum(row["candidate_windows"] for row in certificate["candidate_windows_by_section"].values())
    gain = float(Q(certificate["max_saving_schedule_gain_percent"]))
    margin = Q(certificate["strict_margin_above_one"])
    print(f"PASS_C3_GATHER_CENSUS windows={count} max_nonoverlap={certificate['maximum_disjoint_window_count']}")
    print(f"PASS_C3_GATHER_MAPS count={certificate['per_group_exact_maps_verified']}")
    print(f"SCREEN_C3_GATHER gain={gain:.10f}% five_percent_pass={certificate['screen_passes_five_percent']} moment_margin={float(margin):.15g}")
    print("LIMIT consecutive selected-word domain only; zero gathering/copy/helper/restoration/hosting charges; no physical admission or new kappa")


if __name__ == "__main__":
    main()
