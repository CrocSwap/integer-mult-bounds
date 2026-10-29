#!/usr/bin/env python3
"""Recompute the exact centre-demand rank for the selected gauge44 provider."""
import gzip
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SELECTED = "certificates/selected-result.json"
SOURCE_MANIFEST = "research/community-frontier1094-audit/SELECTED-SOURCE.json"
ASSEMBLY = "research/community-frontier1094-audit/ASSEMBLY.json"
GLOBAL = "research/gauge44-slots-t16/evidence/global/GLOBAL-TEMPLATE.json.gz"
LOCAL = "research/gauge44-slots-t16/evidence/local/LOCAL-PROGRAMS.json.gz"
EXPECTED_COMMIT = "20ecf2891d80b5acf18d980b2164fb44ea7faa90"
EXPECTED_SELECTED_SHA256 = "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129"
EXPECTED_SOURCE_SHA256 = "79b3de5db3dbcb9829789ba58e9e45758926031e2a7d80667a08429d369be53b"
EXPECTED_GLOBAL_SHA256 = "f713f8e66aaeaebb8202fe72bf36c7d23497152497342c27892e0fda3092f95b"
EXPECTED_LOCAL_SHA256 = "172dc3d23e437909ddc01d07b12ede735afbb5bb6145f1ddf5c2e03097dfebe2"
EXPECTED_ASSEMBLY_SHA256 = "1122cb3a575f8c788345fc1bf4c108ac7c3250fb81a5988671f5eb04b3ab3045"
SOURCE_ROWS = (92, 57, 81, 224, 11, 240, 9, 256)
CONSUMER_ROWS = tuple(range(112, 224))
MINOR_ROWS = (112, 117, 118, 120, 113, 116, 115, 123)
CENTRES = 8


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def json_file(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def gzip_json(path):
    return json.loads(gzip.decompress((ROOT / path).read_bytes()))


def source_binding():
    pins = json_file(f"{HERE.relative_to(ROOT)}/SOURCES.json")
    need(pins["base_commit"] == EXPECTED_COMMIT, "package base commit changed")
    inputs = {row["path"]: row["sha256"] for row in pins["files"]
              if row["usage"] == "input"}
    expected = {
        SELECTED: EXPECTED_SELECTED_SHA256,
        SOURCE_MANIFEST: EXPECTED_SOURCE_SHA256,
        ASSEMBLY: EXPECTED_ASSEMBLY_SHA256,
        GLOBAL: EXPECTED_GLOBAL_SHA256,
        LOCAL: EXPECTED_LOCAL_SHA256,
    }
    need(set(inputs) == set(expected), "package inputs differ from pinned source set")
    for path, digest in expected.items():
        need(inputs[path] == digest, f"SOURCES.json pin changed for {path}")
        need(sha256((ROOT / path).read_bytes()) == digest, f"source byte drift: {path}")

    record = json_file(SELECTED)
    need(record["source_manifest"] == SOURCE_MANIFEST, "selected source manifest changed")
    need(record["certificate"] == ASSEMBLY, "selected certificate path changed")
    need(record["certificate_sha256"] == EXPECTED_ASSEMBLY_SHA256,
         "selected certificate digest changed")
    manifest = json_file(SOURCE_MANIFEST)
    files = manifest["files"]
    need(files.get(GLOBAL) == EXPECTED_GLOBAL_SHA256,
         "selected source manifest does not bind the global template")
    need(files.get(LOCAL) == EXPECTED_LOCAL_SHA256,
         "selected source manifest does not bind the local program")
    need(record["kappa"] == "836330098538459/500000000000000000",
         "selected record no longer names the launch-pinned result")
    return {
        "base_commit": EXPECTED_COMMIT,
        "selected_record_sha256": EXPECTED_SELECTED_SHA256,
        "selected_source_manifest_sha256": EXPECTED_SOURCE_SHA256,
        "assembly_sha256": EXPECTED_ASSEMBLY_SHA256,
        "global_template_sha256": EXPECTED_GLOBAL_SHA256,
        "local_programs_sha256": EXPECTED_LOCAL_SHA256,
        "selected_kappa": record["kappa"],
    }


def location(value, kind):
    return (isinstance(value, list) and len(value) == 2 and value[0] == kind
            and isinstance(value[1], int))


def scalar_ops(segment):
    for pos, event in enumerate(segment):
        if isinstance(event, list) and len(event) >= 2 and event[0] == "scalar":
            if isinstance(event[1], list) and event[1]:
                yield pos, event[1]


def centre_segment(events, orientation):
    markers = [i for i, event in enumerate(events)
               if event == ["phase", "centers"]]
    need(len(markers) == 1, "expected one centers phase")
    start = markers[0] + 1
    end = next((i for i in range(start, len(events))
                if isinstance(events[i], list) and len(events[i]) == 2
                and events[i][0] == "phase"), len(events))
    segment = events[start:end]
    centers = [(i, e) for i, e in enumerate(segment)
               if isinstance(e, list) and e and e[0] == "center"]
    need(len(segment) == 256, "centre phase event count changed")
    need(len(centers) == CENTRES, "centre event count changed")
    by_id = {event[1]: (pos, event) for pos, event in centers}
    need(set(by_id) == set(range(CENTRES)), "centre ids are not 0..7")
    for k, (pos, event) in by_id.items():
        need(event[-1] == 8, f"centre {k} is not rank 8")
        if orientation == "forward":
            need(event[2:4] == [413 + k, 0], f"forward centre frame changed: {k}")
        else:
            need(event[2:4] == [0, 413 + k], f"backward centre frame changed: {k}")
    return segment, by_id


def parse_orientation(events, orientation):
    segment, centers = centre_segment(events, orientation)
    ops = list(scalar_ops(segment))
    sources = []
    demand = {k: [] for k in range(CENTRES)}

    for k in range(CENTRES):
        center_pos, _ = centers[k]
        scratch = ["C", k]
        clears = [(pos, op) for pos, op in ops
                  if op[0] == "clear" and len(op) == 2 and op[1] == scratch]
        need(len(clears) == 2, f"private centre clear/restore count changed: C{k}")
        if orientation == "forward":
            copies = [(pos, op) for pos, op in ops
                      if op[0] == "copy" and len(op) == 3
                      and op[1] == scratch and location(op[2], "L")]
            need(len(copies) == 1, f"forward source copy count changed: C{k}")
            copy_pos, copy_op = copies[0]
            clear_positions = sorted(pos for pos, _ in clears)
            need(clear_positions[0] < copy_pos, f"forward C{k} is copied before clear")
            need(copy_pos < center_pos, f"forward C{k} is copied after its centre")
            sources.append(copy_op[2][1])

            writes_k = [(pos, op) for pos, op in ops
                        if op[0] == "add" and len(op) == 5
                        and location(op[1], "L") and op[2] == scratch
                        and op[3] in (-1, 1) and op[4] == 4]
            need(len(writes_k) == 28, f"forward fanout count changed: C{k}")
            need(all(pos > center_pos for pos, _ in writes_k),
                 f"forward C{k} fanout precedes its centre")
            rows = [op[1][1] for _, op in writes_k]
            need(len(set(rows)) == 28, f"forward C{k} repeats a consumer")
            need(clear_positions[1] > max(pos for pos, _ in writes_k),
                 f"forward C{k} is not cleared after fanout")
            demand[k] = [(op[1][1], Fraction(op[3], op[4])) for _, op in writes_k]
        else:
            gathers = [(pos, op) for pos, op in ops
                       if op[0] == "add" and len(op) == 5
                       and op[1] == scratch and location(op[2], "L")
                       and op[3] in (-1, 1) and op[4] == 4]
            need(len(gathers) == 28, f"backward gather count changed: C{k}")
            clear_positions = sorted(pos for pos, _ in clears)
            need(clear_positions[0] < min(pos for pos, _ in gathers),
                 f"backward C{k} is read before clear")
            need(all(pos < center_pos for pos, _ in gathers),
                 f"backward C{k} gather follows its centre")
            rows = [op[2][1] for _, op in gathers]
            need(len(set(rows)) == 28, f"backward C{k} repeats a consumer")
            demand[k] = [(op[2][1], Fraction(op[3], op[4])) for _, op in gathers]

            restores = [(pos, op) for pos, op in ops
                        if op[0] == "add" and len(op) == 5
                        and location(op[1], "L") and op[2] == scratch]
            need(len(restores) == 1, f"backward source restore count changed: C{k}")
            restore_pos, restore_op = restores[0]
            need(restore_pos > center_pos and restore_op[3:] == [-1, 1],
                 f"backward source restoration changed: C{k}")
            need(clear_positions[1] > restore_pos,
                 f"backward C{k} is not cleared after source restoration")
            sources.append(restore_op[1][1])

    if orientation == "forward":
        observed = []
        for _, op in ops:
            if op[0] == "add" and len(op) == 5 and location(op[1], "L") \
                    and op[1][1] in CONSUMER_ROWS:
                need(location(op[2], "C") and op[3] in (-1, 1) and op[4] == 4,
                     "forward centre phase has an unmodelled consumer update")
                observed.append((op[1][1], op[2][1], Fraction(op[3], op[4])))
        expected = [(row, k, coefficient) for k, entries in demand.items()
                    for row, coefficient in entries]
        need(sorted(observed) == sorted(expected),
             "forward demand matrix omits or duplicates a consumer update")
    else:
        observed = []
        for _, op in ops:
            if op[0] == "add" and len(op) == 5 and location(op[2], "L") \
                    and op[2][1] in CONSUMER_ROWS:
                need(location(op[1], "C") and op[3] in (-1, 1) and op[4] == 4,
                     "backward centre phase has an unmodelled consumer read")
                observed.append((op[2][1], op[1][1], Fraction(op[3], op[4])))
        expected = [(row, k, coefficient) for k, entries in demand.items()
                    for row, coefficient in entries]
        need(sorted(observed) == sorted(expected),
             "backward demand matrix omits or duplicates a consumer read")

    rows = sorted({row for entries in demand.values() for row, _ in entries})
    matrix = {row: [Fraction(0) for _ in range(CENTRES)] for row in rows}
    for k, entries in demand.items():
        for row, coefficient in entries:
            matrix[row][k] += coefficient
    return tuple(sources), rows, matrix, [centers[k][1] for k in range(CENTRES)]


def rank_and_rows(matrix, rows):
    work = [[matrix[row][col] for col in range(CENTRES)] for row in rows]
    labels = list(rows)
    rank = 0
    for col in range(CENTRES):
        pivot = next((i for i in range(rank, len(work)) if work[i][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        labels[rank], labels[pivot] = labels[pivot], labels[rank]
        value = work[rank][col]
        work[rank] = [x / value for x in work[rank]]
        for i in range(len(work)):
            if i != rank and work[i][col]:
                factor = work[i][col]
                work[i] = [x - factor * y for x, y in zip(work[i], work[rank])]
        rank += 1
    return rank, labels[:rank]


def determinant(square):
    work = [list(row) for row in square]
    value = Fraction(1)
    for col in range(len(work)):
        pivot = next((i for i in range(col, len(work)) if work[i][col]), None)
        need(pivot is not None, "reported minor is singular")
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            value = -value
        scale = work[col][col]
        value *= scale
        work[col] = [x / scale for x in work[col]]
        for i in range(col + 1, len(work)):
            factor = work[i][col]
            if factor:
                work[i] = [x - factor * y for x, y in zip(work[i], work[col])]
    return value


def matrix_rank(matrix, rows):
    return rank_and_rows(matrix, rows)[0]


def compute():
    binding = source_binding()
    global_template = gzip_json(GLOBAL)
    programs = gzip_json(LOCAL)
    provider = global_template["local_providers"]["gauge44"]
    scratch_namespace = global_template["private_namespace"]["centers"]
    need(scratch_namespace == [7168, 7176], "physical private-centre namespace changed")
    need(provider["centers"] == list(SOURCE_ROWS), "provider source-row declaration changed")
    need(provider["local_programs_sha256"] == EXPECTED_LOCAL_SHA256,
         "provider local-program digest changed")
    need(provider["local_programs"] == programs,
         "inline gauge44 provider differs from selected LOCAL-PROGRAMS")
    need(global_template["provider_dispatch"].startswith("For each indivisible local_cover_sweep"),
         "selected provider dispatch contract changed")

    calls = global_template["calls"]
    orientations = {direction: sum(c["orientation"] == direction for c in calls)
                    for direction in ("forward", "backward")}
    need(len(calls) == 72 and orientations == {"forward": 40, "backward": 32},
         "selected call schedule changed")
    for call in calls:
        need(call["provider_id"] == "gauge44", "a selected call uses another provider")
        direction = call["orientation"]
        need(direction in programs, "call has unknown orientation")
        checked = provider["local_program_checks"][direction]
        need(call["local_program_sha256"] == checked["sha256"],
             "call local-program hash differs from provider check")
        need(checked["events"] == len(programs[direction]),
             "provider event count differs from local program")
        need(checked["all_columns"] == 716, "selected local interface column count changed")
        need(checked["private_centers_cleared"], "private centre clearing is not certified")

    global_programs = provider["local_programs"]
    forward = parse_orientation(global_programs["forward"], "forward")
    backward = parse_orientation(global_programs["backward"], "backward")
    sources_f, rows_f, matrix_f, centres_f = forward
    sources_b, rows_b, matrix_b, centres_b = backward
    need(sources_f == sources_b == SOURCE_ROWS, "source/restore row tuple changed")
    need(len(set(sources_f)) == CENTRES, "source rows are not independent distinct coordinates")
    need(set(sources_f).isdisjoint(CONSUMER_ROWS), "source and consumer coordinates overlap")
    need(rows_f == rows_b == list(CONSUMER_ROWS), "consumer rows changed")
    need(matrix_f == matrix_b, "backward gather differs from forward fanout")
    need([(e[1], e[2], e[-1]) for e in centres_f]
         == [(e[1], e[3], e[-1]) for e in centres_b],
         "forward/backward centre ids, frames or ranks differ")
    for k in range(CENTRES):
        nonzero = [matrix_f[row][k] for row in rows_f if matrix_f[row][k]]
        need(len(nonzero) == 28 and all(x in (Fraction(1, 4), Fraction(-1, 4))
                                        for x in nonzero),
             f"coefficient column changed: {k}")

    rank, minor_rows = rank_and_rows(matrix_f, rows_f)
    need(rank == CENTRES, "selected demand rank is below eight")
    need(tuple(minor_rows) == MINOR_ROWS, "independent-row witness changed")
    minor = [[matrix_f[row][col] for col in range(CENTRES)] for row in minor_rows]
    minor_det = determinant(minor)
    need(minor_det == Fraction(-1, 16384), "exact nonzero minor determinant changed")

    zeroed = {row: list(values) for row, values in matrix_f.items()}
    for row in rows_f:
        zeroed[row][0] = Fraction(0)
    merged = {row: list(values) for row, values in matrix_f.items()}
    for row in rows_f:
        merged[row][1] = merged[row][0]
    zero_rank = matrix_rank(zeroed, rows_f)
    merged_rank = matrix_rank(merged, rows_f)
    need(zero_rank == merged_rank == 7, "rank-dropping controls did not reduce rank to seven")

    checks = provider["local_program_checks"]
    need(all(checks[d]["paid_profile"].get("8") == 8 for d in ("forward", "backward")),
         "selected rank-8 centre profile changed")
    return {
        "status": "PASS_SELECTED_PROVIDER_CENTRE_DEMAND_RANK",
        "source_binding": binding,
        "decoder": {
            "provider_id": "gauge44",
            "global_template_version": global_template["version"],
            "calls": len(calls),
            "orientations": orientations,
            "events_per_orientation": {d: len(global_programs[d])
                                       for d in ("forward", "backward")},
            "checked_input_columns": 716,
        },
        "centre_path": {
            "totals_per_invocation": CENTRES,
            "source_rows_forward": list(sources_f),
            "source_rows_restored_backward": list(sources_b),
            "private_scratch": ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7"],
            "physical_private_scratch_range": scratch_namespace,
            "centre_ranks": [event[-1] for event in centres_f],
            "centre_frames_forward": [event[2] for event in centres_f],
            "consumer_rows": [rows_f[0], rows_f[-1]],
            "consumers_per_total": [28] * CENTRES,
            "coefficients": ["-1/4", "1/4"],
        },
        "demand": {
            "shape": [len(rows_f), CENTRES],
            "rank_forward": rank,
            "rank_backward": rank,
            "backward_equals_forward": True,
            "independent_rows": list(minor_rows),
            "minor_determinant": str(minor_det),
            "minor_determinant_times_4_pow_8": int(minor_det * 4 ** CENTRES),
        },
        "lower_bound": {
            "exact_linear_scalar_channels_per_invocation": CENTRES,
            "selected_rank_8_centre_charge_per_invocation": CENTRES * 8,
            "charged_floor_scope": "64 only under the retained rank-8-per-channel carrier restriction; arbitrary changed decoder factors are not covered",
        },
        "controls": {
            "zero_one_demand_column_rank": zero_rank,
            "merge_two_demand_columns_rank": merged_rank,
        },
        "scope": "Exact linear-information floor for the selected gauge44 provider's pinned 112-row centre endpoint. No cross-call physical eligibility or universal cost bound for changed decoder graphs.",
    }


def main():
    result = compute()
    rendered = json.dumps(result, indent=1, sort_keys=True) + "\n"
    target = HERE / "RESULT.json"
    if sys.argv[1:] == ["--write"]:
        target.write_text(rendered, encoding="utf-8")
    else:
        need(target.read_text(encoding="utf-8") == rendered,
             "RESULT.json differs from exact recomputation; run verify.py --write")
    print("PASS_SELECTED_PROVIDER_CENTRE_DEMAND_RANK rank=8 channels>=8 minor=-1/16384 observed_rank8_charge=64")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError, ZeroDivisionError) as exc:
        print(f"FAIL_SELECTED_PROVIDER_CENTRE_DEMAND_RANK: {exc}")
        raise SystemExit(1)
