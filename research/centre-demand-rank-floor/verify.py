#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Exact demand-rank floor for the selected centre path (card centre-path-sharing).

Scoped finite computation on the pinned selected replay archive. Recomputes the
consumer demand matrix of the eight COPY/ERASE centre totals, its exact rational
rank and an explicit nonzero minor, the forward/backward gather equality, and
the 144-call centre-row owner inventory. No kappa, supplier admission or
physical replay is claimed.
"""
import argparse
import gzip
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import sys
import tarfile

sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
MEMBER = "candidate/strict/global/base/split-centres/GLOBAL-TEMPLATE.json.gz"
SOURCE_ROWS = [229, 224, 227, 225, 243, 241, 259, 257]
MINOR_ROWS = [112, 117, 118, 120, 113, 116, 115, 123]
MINOR_COLS = [0, 1, 2, 3, 4, 5, 6, 7]
CONSUMER_FIRST, CONSUMER_LAST = 112, 223
CENTRES, FANOUT = 8, 28


def need(ok, message):
    if not ok:
        raise ValueError(message)


def rank_q(matrix):
    m = [row[:] for row in matrix]
    if not m:
        return 0
    rows, cols = len(m), len(m[0])
    rank = 0
    for c in range(cols):
        piv = None
        for i in range(rank, rows):
            if m[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        m[rank], m[piv] = m[piv], m[rank]
        pivot = m[rank][c]
        m[rank] = [x / pivot for x in m[rank]]
        for i in range(rows):
            if i != rank and m[i][c] != 0:
                factor = m[i][c]
                m[i] = [a - factor * b for a, b in zip(m[i], m[rank])]
        rank += 1
    return rank


def det_q(matrix):
    m = [row[:] for row in matrix]
    size = len(m)
    need(all(len(row) == size for row in m), "determinant needs a square matrix")
    det = Q(1)
    for c in range(size):
        piv = None
        for i in range(c, size):
            if m[i][c] != 0:
                piv = i
                break
        need(piv is not None, "singular minor in det_q")
        if piv != c:
            m[c], m[piv] = m[piv], m[c]
            det = -det
        det *= m[c][c]
        inv = Q(1) / m[c][c]
        for i in range(c + 1, size):
            if m[i][c] != 0:
                factor = m[i][c] * inv
                m[i] = [a - factor * b for a, b in zip(m[i], m[c])]
    return det


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def parse_centre(events, label):
    first = events.index(["phase", "centers"])
    last = events.index(["phase", "B"])
    block = events[first + 1:last]
    need(len(block) == 32 * CENTRES, label + " centre phase is not 256 macros")
    sources, fanout = [], {}
    for k in range(CENTRES):
        chunk = block[32 * k:32 * (k + 1)]
        source = None
        entries = []
        for event in chunk:
            need(event[0] in ("scalar", "center"), label + " unexpected event kind")
            if event[0] == "center":
                need(event[1] == k and event[4] == 8, label + " centre ascent changed")
                continue
            op = event[1]
            if op[0] == "clear":
                need(op[1] == ["C", k], label + " scratch clear changed")
                continue
            if op[0] == "copy":
                need(op[1] == ["C", k] and op[2][0] == "L", label + " copy changed")
                need(source is None, label + " two copies in one centre")
                source = op[2][1]
                continue
            need(op[0] == "add", label + " unexpected scalar op")
            left, right, num, den = op[1], op[2], op[3], op[4]
            if den == 1 and left[0] == "L" and right == ["C", k]:
                need(source is None or source == left[1], label + " source subtraction changed")
                source = left[1]
                continue
            need(den == 4 and num in (1, -1), label + " fanout coefficient changed")
            if left[0] == "L" and right == ["C", k]:
                entries.append((left[1], Q(num, den)))
            elif left == ["C", k] and right[0] == "L":
                entries.append((right[1], Q(num, den)))
            else:
                raise ValueError(label + " unexpected gather event")
        need(source is not None, label + " centre has no source row")
        need(len(entries) == FANOUT, label + " centre fanout count changed")
        need(len({r for r, _ in entries}) == FANOUT, label + " repeated fanout row")
        sources.append(source)
        fanout[k] = entries
    need(len(set(sources)) == CENTRES, label + " source rows are not distinct")
    return sources, fanout


def demand_matrix(fanout, width):
    matrix = [[Q(0)] * CENTRES for _ in range(width)]
    for k, entries in fanout.items():
        for row, coefficient in entries:
            matrix[row][k] += coefficient
    return matrix


def source_pins():
    manifest = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    inputs = {}
    for row in manifest["files"]:
        if row["usage"] == "input":
            path = (ROOT / row["path"]).resolve()
            need(path.is_relative_to(ROOT) and path.is_file(), "invalid input path")
            need(hashlib.sha256(path.read_bytes()).hexdigest() == row["sha256"], "source drift")
            inputs[row["path"]] = row["sha256"]
    need(ARCHIVE in inputs, "archive not declared as input")
    return inputs


def compute():
    inputs = source_pins()
    consumed = {}
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        raw = archive.extractfile(archive.getmember(MEMBER)).read()
    consumed[MEMBER] = hashlib.sha256(raw).hexdigest()
    template = json.loads(gzip.decompress(raw))

    programs = template["local_programs"]
    results = {}
    for label in ("forward", "backward"):
        sources, fanout = parse_centre(programs[label], label)
        matrix = demand_matrix(fanout, CONSUMER_LAST + 1)
        rows = list(range(CONSUMER_FIRST, CONSUMER_LAST + 1))
        rank = rank_q([matrix[r] for r in rows])
        results[label] = (sources, fanout, matrix, rank)

    sources_f, fanout_f, matrix_f, rank_f = results["forward"]
    sources_b, fanout_b, matrix_b, rank_b = results["backward"]
    need(sources_f == sources_b == SOURCE_ROWS, "source rows changed")
    need(rank_f == rank_b == CENTRES, "demand rank is not eight")
    gather_equal = all(matrix_b[r][c] == matrix_f[r][c]
                       for r in range(CONSUMER_FIRST, CONSUMER_LAST + 1)
                       for c in range(CENTRES))
    need(gather_equal, "gather matrix differs from fanout matrix")

    minor = [[matrix_f[row][c] for c in MINOR_COLS] for row in MINOR_ROWS]
    determinant = det_q(minor)
    need(determinant != 0, "pinned minor is singular")
    scaled = determinant * (4 ** CENTRES)
    need(scaled.denominator == 1, "minor determinant is not an integer fourth")

    calls = template["calls"]
    need(len(calls) == 144, "call count changed")
    orientations = {}
    stages = {}
    lookups = {"present": 0, "missing": 0}
    assignments = {}
    for call in calls:
        orientations[call["orientation"]] = orientations.get(call["orientation"], 0) + 1
        stages[call["stage"]] = stages.get(call["stage"], 0) + 1
        owners = {p[0]: digest(p[1]) for p in call["owners"]}
        key = []
        for row in SOURCE_ROWS:
            if row in owners:
                lookups["present"] += 1
                key.append(owners[row])
            else:
                lookups["missing"] += 1
                key.append("MISSING")
        assignments.setdefault(tuple(key), 0)
        assignments[tuple(key)] += 1
    need(orientations == {"forward": 80, "backward": 64}, "orientation mix changed")
    need(all(stages.get(s, 0) == 16 for s in range(9)) and len(stages) == 9, "stage mix changed")
    need(lookups["present"] + lookups["missing"] == 144 * CENTRES, "owner lookup count changed")

    receipt = {
        "status": "PASS_CENTRE_DEMAND_RANK_FLOOR",
        "consumed_member_payload_sha256": consumed,
        "centre_path": {
            "totals_per_call": CENTRES,
            "source_rows": SOURCE_ROWS,
            "scratch_namespace": [23408, 23416],
            "fanout_rows_per_total": FANOUT,
            "consumer_rows": [CONSUMER_FIRST, CONSUMER_LAST],
            "coefficients": ["-1/4", "1/4"],
        },
        "demand": {
            "matrix": "112 by 8, consumer row by centre total, forward fanout",
            "rank_forward": rank_f,
            "rank_backward": rank_b,
            "gather_equals_fanout": gather_equal,
            "minor_rows": MINOR_ROWS,
            "minor_cols": MINOR_COLS,
            "minor_determinant": str(determinant),
            "minor_determinant_scaled_by_4pow8": int(scaled),
        },
        "calls": {
            "total": len(calls),
            "orientations": orientations,
            "stages": stages,
            "owner_lookups": lookups,
            "distinct_source_row_assignments": len(assignments),
            "assignment_group_sizes": sorted(assignments.values(), reverse=True),
            "note": ("owner nominations do not carry the centre source rows for %d of %d "
                     "lookups; the data-row instantiation lives in route_semantics "
                     "(cover class d*rho(stage,port)), not decoded here"
                     % (lookups["missing"], lookups["present"] + lookups["missing"])),
        },
        "controls": [
            "zero one demand column: rank drops below eight (rejected)",
            "merge two demand columns: rank drops below eight (rejected)",
            "flip one fanout coefficient sign: gather equality fails (rejected)",
            "permute source rows: pinned source tuple fails (rejected)",
        ],
        "scope": ("smallest instance of the card question; no shared centre, no "
                  "changed endpoint, no kappa, no supplier admission"),
        "input_sha256": inputs,
    }
    return receipt


def controls():
    programs = load_template()["local_programs"]
    sources, fanout = parse_centre(programs["forward"], "control")
    matrix = demand_matrix(fanout, CONSUMER_LAST + 1)
    rows = list(range(CONSUMER_FIRST, CONSUMER_LAST + 1))

    zeroed = [[Q(0)] * CENTRES for _ in range(len(matrix))]
    for r in rows:
        for c in range(CENTRES):
            zeroed[r][c] = matrix[r][c]
    for r in rows:
        zeroed[r][0] = Q(0)
    need(rank_q([zeroed[r] for r in rows]) == CENTRES - 1, "zero-column control did not drop rank")

    merged = [[Q(0)] * CENTRES for _ in range(len(matrix))]
    for r in rows:
        for c in range(CENTRES):
            merged[r][c] = matrix[r][c]
    for r in rows:
        merged[r][0] += merged[r][1]
        merged[r][1] = Q(0)
    need(rank_q([merged[r] for r in rows]) == CENTRES - 1, "merge control did not drop rank")

    flipped = {k: list(v) for k, v in fanout.items()}
    row0, coefficient0 = flipped[0][0]
    flipped[0][0] = (row0, -coefficient0)
    matrix_flipped = demand_matrix(flipped, CONSUMER_LAST + 1)
    _, fanout_b = parse_centre(programs["backward"], "control")
    matrix_b = demand_matrix(fanout_b, CONSUMER_LAST + 1)
    same = all(matrix_b[r][c] == matrix_flipped[r][c]
               for r in rows for c in range(CENTRES))
    need(not same, "sign-flip control was not detected by gather equality")

    mutated = [list(event) for event in programs["forward"]]
    first = mutated.index(["phase", "centers"])
    copies = [first + 1 + 32 * k + 1 for k in range(CENTRES)]
    a, b = copies[0], copies[1]
    mutated[a] = ["scalar", ["copy", ["C", 0], ["L", SOURCE_ROWS[1]]], mutated[a][2]]
    mutated[b] = ["scalar", ["copy", ["C", 1], ["L", SOURCE_ROWS[0]]], mutated[b][2]]
    swapped, _ = parse_centre(mutated, "control")
    need(tuple(swapped) != tuple(SOURCE_ROWS), "swap control left the source tuple unchanged")
    rejected = False
    try:
        need(swapped == SOURCE_ROWS, "source rows changed")
    except ValueError:
        rejected = True
    need(rejected, "swap control was not rejected by the pinned source tuple")
    return True


def load_template():
    with tarfile.open(ROOT / ARCHIVE, "r:gz") as archive:
        raw = archive.extractfile(archive.getmember(MEMBER)).read()
    return json.loads(gzip.decompress(raw))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate RESULT.json")
    args = parser.parse_args()
    controls()
    receipt = compute()
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    target = HERE / "RESULT.json"
    if args.write:
        target.write_text(text, encoding="utf-8", newline="\n")
    else:
        need(target.is_file(), "RESULT.json is missing; run verify.py --write")
        need(target.read_bytes() == text.encode("utf-8"), "RESULT.json differs from recomputation")
    demand = receipt["demand"]
    calls = receipt["calls"]
    print("PASS_CENTRE_DEMAND_RANK_FLOOR demand_rank %d totals %d consumer_rows %d "
          "minor_det %s calls %d owner_lookups_missing %d no_new_kappa"
          % (demand["rank_forward"], receipt["centre_path"]["totals_per_call"],
             CONSUMER_LAST - CONSUMER_FIRST + 1, demand["minor_determinant"], calls["total"],
             calls["owner_lookups"]["missing"]))


if __name__ == "__main__":
    main()
