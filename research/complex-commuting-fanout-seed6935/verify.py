#!/usr/bin/env python3
"""Exact selected-word screen for nonconsecutive commuting shared-source fanouts."""
from bisect import bisect_left
from collections import Counter, defaultdict
from fractions import Fraction as Q
import gzip
import hashlib
import importlib.util
import itertools
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
            for key in tuple(pivots):
                if (pivots[key] >> pivot) & 1:
                    pivots[key] ^= x
            pivots[pivot] = x
    return tuple(pivots[key] for key in sorted(pivots, reverse=True))


def matmul(left, right):
    require(left and right and len(left[0]) == len(right), "matrix dimension mismatch")
    return [[sum((left[i][k] * right[k][j] for k in range(len(right))), Q(0))
             for j in range(len(right[0]))] for i in range(len(left))]


def identity(size):
    return [[Q(int(i == j)) for j in range(size)] for i in range(size)]


def operation_matrix(operation, size):
    """Exact register matrix for the selected word's ADD and SCALE operations."""
    matrix = identity(size)
    if operation[0] == "add":
        target, source = operation[1], operation[2]
        require(target != source, "self ADD is outside the pinned operation model")
        matrix[target][source] += Q(operation[3], operation[4])
    elif operation[0] == "scale":
        register = operation[1]
        matrix[register][register] = Q(operation[2], operation[3])
    else:
        raise ValueError("unsupported selected-word operation " + str(operation[0]))
    return matrix


def gap_commutes_with_fanout(operation, source, destinations):
    """Exact rank-one-matrix commutator criterion for one intervening gate.

    For an ADD b E_(u,v) and selected fanout a E_(d,source), the commutator
    vanishes exactly when u != source and v != d. A SCALE is diagonal and
    commutes exactly when it scales neither endpoint, or has unit factor.
    """
    if operation[0] == "add":
        if Q(operation[3], operation[4]) == 0:
            return True
        return operation[1] != source and operation[2] not in destinations
    if operation[0] == "scale":
        factor = Q(operation[2], operation[3])
        return factor == 1 or operation[1] not in ({source} | set(destinations))
    return False


def verify_fanout_map(coefficients):
    require(len(coefficients) == 3, "fanout requires three output coefficients")
    cs = [Q(value) for value in coefficients]
    require(all(value != 0 for value in cs), "zero coefficient in selected ADD")
    forward, inverse = identity(4), identity(4)
    for row, coefficient in enumerate(cs, start=1):
        forward[row][0] += coefficient
        inverse[row][0] -= coefficient
    require(matmul(forward, inverse) == identity(4), "fanout inverse is not exact")
    require(matmul(inverse, forward) == identity(4), "reverse fanout inverse is not exact")


def load_inputs():
    source_manifest = json.loads((PKG / "SOURCES.json").read_text())
    require(source_manifest.get("schema_version") == 1, "unsupported source manifest")
    require(source_manifest.get("base_commit") == BASE, "wrong source base")
    for item in source_manifest.get("files", []):
        path = ROOT / item["path"]
        require(path.is_file(), "missing pinned source " + item["path"])
        require(sha256(path.read_bytes()) == item["sha256"], "source hash mismatch " + item["path"])

    selected_path = ROOT / "certificates/selected-result.json"
    manifest_path = ROOT / "research/community-frontier1094-audit/SELECTED-SOURCE.json"
    assembly_path = ROOT / "research/community-frontier1094-audit/ASSEMBLY.json"
    require(sha256(selected_path.read_bytes()) == SELECTED_SHA, "selected record changed")
    require(sha256(manifest_path.read_bytes()) == MANIFEST_SHA, "selected source manifest changed")
    require(sha256(assembly_path.read_bytes()) == ASSEMBLY_SHA, "selected assembly changed")
    selected = json.loads(selected_path.read_text())
    require(selected.get("certificate_sha256") == ASSEMBLY_SHA, "selected record/certificate mismatch")

    compressed = (ROOT / WORD_PATH).read_bytes()
    require(sha256(compressed) == WORD_COMPRESSED_SHA, "compressed word hash mismatch")
    raw = gzip.decompress(compressed)
    require(sha256(raw) == WORD_SHA, "decompressed word hash mismatch")
    word = json.loads(raw)
    slot_pins = json.loads((ROOT / SLOT_PIN_PATH).read_text())
    require(slot_pins.get("word_sha256") == WORD_SHA, "selected slot pin mismatch")
    return word


def load_ceiling_module():
    path = ROOT / CEILING_PATH
    spec = importlib.util.spec_from_file_location("pinned_complex_ceiling", path)
    require(spec is not None and spec.loader is not None, "cannot load pinned ceiling module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def advance_one(current, operation, target, profile):
    if operation[0] == "add":
        registers = [operation[1], operation[2]]
        require(registers[0] != registers[1], "ADD must touch two distinct registers")
    elif operation[0] == "scale":
        registers = [operation[1]]
        require(Q(operation[2], operation[3]) != 0, "zero SCALE is outside the reversible word")
    else:
        raise ValueError("unsupported selected-word operation " + str(operation[0]))
    old_frames = []
    deltas = []
    for register in registers:
        require(type(register) is int and 0 <= register < len(current), "register out of range")
        old = current[register]
        require(span(list(old) + list(target)) == target, "nonmonotone frame at operation")
        delta = len(target) - len(old)
        require(delta >= 0, "negative frame increment")
        old_frames.append(old)
        deltas.append(delta)
        if delta:
            profile[delta] += 1
    for register in registers:
        current[register] = target
    return old_frames, deltas


def reconstruct_word(word):
    report = word.get("report", {})
    require((report.get("m"), report.get("h"), report.get("v"), report.get("R")) == (73, 9, 112, 480),
            "selected word dimensions or inventory mismatch")
    register_count = 2 * 112 + 480
    current = [tuple() for _ in range(register_count)]
    for index, port in enumerate(word["ports"]):
        current[index] = span([port])
    for register, frame in word.get("start_extra", {}).items():
        current[int(register)] = span(frame)

    profile = Counter()
    sections = {}
    for section in ("A", "B"):
        rows = []
        operations = word.get(section)
        require(isinstance(operations, list), "missing word section " + section)
        for index, operation in enumerate(operations):
            target = span(operation[-1])
            old_frames, deltas = advance_one(current, operation, target, profile)
            rows.append({"index": index, "operation": operation, "target": target,
                         "old_frames": old_frames, "deltas": deltas})
        sections[section] = rows

    for cleanup_index, frame in word.get("early_cleanup", []):
        operation = word["cleanup"][cleanup_index]
        advance_one(current, operation, span(frame), profile)

    full = span([1 << index for index in range(9)])
    final_frames = {int(register): span(frame) for register, frame in word.get("helper_final", {}).items()}
    for register in range(register_count):
        if 112 <= register < 224:
            port = word["ports"][register - 112]
            target = span([value for value in range(1, 512) if (value & port).bit_count() % 2 == 0])
        else:
            target = final_frames.get(register, full)
        old = current[register]
        require(span(list(old) + list(target)) == target, "nonmonotone terminal frame")
        delta = len(target) - len(old)
        require(delta >= 0, "negative terminal frame increment")
        if delta:
            profile[delta] += 1
        current[register] = target
    profile.update(Counter(report.get("centre_ranks", [])))
    declared = {int(rank): int(count) for rank, count in report.get("local_profile", {}).items()}
    require(declared == BASE_PROFILE, "selected report profile mismatch")
    require(dict(sorted(profile.items())) == BASE_PROFILE, "full selected local profile reconstruction mismatch")
    return sections, profile


def candidate_for(section, triple, rows):
    operations = [row["operation"] for row in triple]
    if not all(operation[0] == "add" for operation in operations):
        return None
    sources = [operation[2] for operation in operations]
    destinations = [operation[1] for operation in operations]
    if len(set(sources)) != 1 or len(set(destinations)) != 3 or sources[0] in destinations:
        return None
    source = sources[0]
    if [row["deltas"][1] for row in triple] != [0, 0, 0]:
        return None
    if sum(row["deltas"][0] > 0 for row in triple) < 2:
        return None
    source_frame = triple[0]["old_frames"][1]
    if any(row["old_frames"][1] != source_frame for row in triple):
        return None
    if any(span(list(source_frame) + list(row["target"])) != row["target"] for row in triple):
        return None

    indices = [row["index"] for row in triple]
    require(indices == sorted(set(indices)), "candidate gate indices are not distinct and ordered")
    chosen_indices = set(indices)
    gaps = [rows[index]["operation"] for index in range(indices[0] + 1, indices[-1])
            if index not in chosen_indices]
    if not all(gap_commutes_with_fanout(operation, source, destinations) for operation in gaps):
        return None

    coefficients = [Q(operation[3], operation[4]) for operation in operations]
    verify_fanout_map(coefficients)
    ranks = [row["deltas"][0] for row in triple]
    joint_rank = sum(ranks)
    if not 0 < joint_rank < M:
        return None
    return {
        "section": section,
        "indices": indices,
        "start": indices[0],
        "end": indices[-1],
        "source": source,
        "destinations": destinations,
        "coefficients": [str(value) for value in coefficients],
        "target_ranks": ranks,
        "joint_rank": joint_rank,
        "source_frame_rank": len(source_frame),
        "target_frame_ranks": [len(row["target"]) for row in triple],
        "gap_operations": len(gaps),
        "gap_adds": sum(operation[0] == "add" for operation in gaps),
        "gap_scales": sum(operation[0] == "scale" for operation in gaps),
        "consecutive": indices == list(range(indices[0], indices[0] + 3)),
    }


def enumerate_candidates(sections):
    result = {}
    for section, rows in sections.items():
        by_source = defaultdict(list)
        for row in rows:
            operation = row["operation"]
            if operation[0] == "add" and row["deltas"][1] == 0:
                by_source[operation[2]].append(row)
        candidates = []
        for source_rows in by_source.values():
            for triple in itertools.combinations(source_rows, 3):
                candidate = candidate_for(section, triple, rows)
                if candidate is not None:
                    candidates.append(candidate)
        candidates.sort(key=lambda item: (item["end"], item["start"], item["indices"]))
        result[section] = candidates
    return result


def candidate_weight(candidate, ceiling, exponent):
    direct = sum((ceiling.child_cost(rank, M, exponent)[1]
                  for rank in candidate["target_ranks"] if rank), Q(0))
    joint = ceiling.child_cost(candidate["joint_rank"], M, exponent)[0]
    weight = direct - joint
    require(weight > 0, "candidate has no positive ideal moment saving")
    return weight


def weighted_interval_schedule(candidates, weights):
    """Exact interval DP; candidate intervals are closed [first gate, last gate]."""
    ordered = sorted(candidates, key=lambda item: (item["end"], item["start"], item["indices"]))
    ends = [item["end"] for item in ordered]
    best = [Q(0)] * (len(ordered) + 1)
    choice = [None] * (len(ordered) + 1)
    previous = [0] * (len(ordered) + 1)
    for offset, candidate in enumerate(ordered, start=1):
        predecessor_count = bisect_left(ends, candidate["start"], 0, offset - 1)
        take_value = best[predecessor_count] + weights(candidate)
        skip_value = best[offset - 1]
        if take_value > skip_value:
            best[offset] = take_value
            choice[offset] = candidate
            previous[offset] = predecessor_count
        else:
            best[offset] = skip_value
    selected = []
    cursor = len(ordered)
    while cursor:
        if choice[cursor] is not None:
            selected.append(choice[cursor])
            cursor = previous[cursor]
        else:
            cursor -= 1
    selected.reverse()
    return best[-1], selected


def apply_profile(groups):
    result = Counter(BASE_PROFILE)
    for group in groups:
        for rank in group["target_ranks"]:
            if rank:
                result[rank] -= 1
                require(result[rank] >= 0, "profile removes a missing direct child")
        result[group["joint_rank"]] += 1
    return {rank: count for rank, count in sorted(result.items()) if count}


def section_record(candidates, ceiling, exponent):
    saving, selected = weighted_interval_schedule(
        candidates, lambda candidate: candidate_weight(candidate, ceiling, exponent))
    count, count_selected = weighted_interval_schedule(candidates, lambda candidate: Q(1))
    return {
        "candidate_count": len(candidates),
        "consecutive_candidate_count": sum(item["consecutive"] for item in candidates),
        "nonconsecutive_candidate_count": sum(not item["consecutive"] for item in candidates),
        "maximum_disjoint_intervals": len(count_selected),
        "maximum_target_saving_intervals": len(selected),
        "maximum_target_saving": str(saving),
        "selected_nonconsecutive_count": sum(not item["consecutive"] for item in selected),
        "candidates": candidates,
        "count_schedule": count_selected,
        "target_schedule": selected,
        "count_weight": str(count),
    }


def build_certificate():
    word = load_inputs()
    sections, reconstructed = reconstruct_word(word)
    candidates_by_section = enumerate_candidates(sections)
    ceiling = load_ceiling_module()

    baseline_low, baseline_high = ceiling.ceiling(BASE_PROFILE, M, FAMILIES, STAGES, CENTRE)
    target_exponent = baseline_high * Q(105, 100)
    baseline_at_target = ceiling.relax(BASE_PROFILE, M, FAMILIES, STAGES, CENTRE, target_exponent)
    require(baseline_at_target[0] > 1, "five-percent target is below baseline ceiling")

    sections_out = {
        section: section_record(candidates_by_section[section], ceiling, target_exponent)
        for section in ("A", "B")
    }
    target_groups = [candidate for section in ("A", "B")
                     for candidate in sections_out[section]["target_schedule"]]
    count_groups = [candidate for section in ("A", "B")
                    for candidate in sections_out[section]["count_schedule"]]
    profile = apply_profile(target_groups)
    count_profile = apply_profile(count_groups)

    baseline_mass = sum(rank * count for rank, count in BASE_PROFILE.items())
    profile_mass = sum(rank * count for rank, count in profile.items())
    require(baseline_mass == profile_mass == 5586, "rank mass changed under fanout replacement")
    require(sum(rank * count for rank, count in count_profile.items()) == 5586,
            "rank mass changed under count-optimal replacement")

    total_saving = sum((Q(sections_out[section]["maximum_target_saving"])
                        for section in ("A", "B")), Q(0))
    normalized_saving = total_saving / Q(FAMILIES, STAGES)
    best_moment_lower = ceiling.down(baseline_at_target[0] - normalized_saving)
    target_margin = best_moment_lower - 1
    require(target_margin > 0, "commuting C3 intervals may reach the 5-percent target")

    target_low, target_high = ceiling.ceiling(profile, M, FAMILIES, STAGES, CENTRE)
    count_low, count_high = ceiling.ceiling(count_profile, M, FAMILIES, STAGES, CENTRE)
    gain_percent = (target_high / baseline_high - 1) * 100
    count_gain_percent = (count_high / baseline_high - 1) * 100
    total_groups = len(target_groups)
    nonconsecutive_groups = sum(not item["consecutive"] for item in target_groups)
    require(total_groups == 27 and nonconsecutive_groups == 4,
            "target-optimal schedule does not match the pinned finite result")
    require(sum(record["candidate_count"] for record in sections_out.values()) == 54,
            "unexpected exhaustive candidate count")
    require(sum(record["nonconsecutive_candidate_count"] for record in sections_out.values()) == 22,
            "unexpected nonconsecutive candidate count")
    require(sum(record["maximum_disjoint_intervals"] for record in sections_out.values()) == 27,
            "unexpected maximum disjoint interval count")

    return {
        "status": "PASS_COMMUTING_FANOUT_FINITE_SCREEN",
        "scope": {
            "word": "selected width-73 rational ADD word, sections A and B",
            "group": "three ADD gates, one unchanged source frame, three distinct destinations, at least two positive target-rank increments",
            "commutation": "every unselected gate between the first and last selected gate commutes exactly with each selected shear",
            "interval_rule": "selected closed gate-index intervals are pairwise disjoint",
            "omitted_costs": ["adapter", "copy", "helper", "hosting", "frame transition", "restoration", "precision"],
        },
        "base_commit": BASE,
        "catalogue_priority_revision": 3,
        "catalogue_sha256": CATALOG_SHA,
        "selected_record_sha256": SELECTED_SHA,
        "compressed_word_sha256": WORD_COMPRESSED_SHA,
        "word_sha256": WORD_SHA,
        "reconstructed_baseline_profile": {str(k): v for k, v in sorted(reconstructed.items())},
        "baseline_profile": {str(k): v for k, v in sorted(BASE_PROFILE.items())},
        "baseline_ceiling_interval": [str(baseline_low), str(baseline_high)],
        "five_percent_target_exponent": str(target_exponent),
        "baseline_moment_interval_at_target": [str(item) for item in baseline_at_target],
        "sections": sections_out,
        "target_saving_schedule": target_groups,
        "count_maximizing_schedule": count_groups,
        "target_saving_schedule_group_count": total_groups,
        "target_saving_schedule_nonconsecutive_count": nonconsecutive_groups,
        "target_saving_schedule_profile": {str(k): v for k, v in sorted(profile.items())},
        "target_saving_schedule_mass": profile_mass,
        "target_saving_schedule_ceiling_interval": [str(target_low), str(target_high)],
        "target_saving_schedule_gain_percent": str(gain_percent),
        "count_schedule_profile": {str(k): v for k, v in sorted(count_profile.items())},
        "count_schedule_ceiling_interval": [str(count_low), str(count_high)],
        "count_schedule_gain_percent": str(count_gain_percent),
        "maximum_saving_normalized_per_call": str(normalized_saving),
        "moment_lower_bound_at_target_after_maximum_saving": str(best_moment_lower),
        "strict_margin_above_one": str(target_margin),
        "maximum_saving_is_favorable": "each direct child uses an upper cost endpoint and each joined child a lower cost endpoint; all additional mechanism costs are zero",
        "claim_url": "https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18923131",
        "predecessor": "https://github.com/CrocSwap/integer-mult-bounds/pull/1799",
    }


def main():
    write = len(sys.argv) == 2 and sys.argv[1] == "--write"
    require(len(sys.argv) == 1 or write, "usage: verify.py [--write]")
    result = build_certificate()
    output = PKG / "CERTIFICATE.json"
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if write:
        output.write_text(encoded)
    else:
        require(output.is_file(), "missing CERTIFICATE.json; run verify.py --write once")
        require(output.read_text() == encoded, "committed certificate differs from exact replay")
    print("PASS_COMMUTING_FANOUT_FINITE_SCREEN")


if __name__ == "__main__":
    main()
