#!/usr/bin/env python3
"""Check the new 54-batch phase-B witness without importing a search engine."""
from __future__ import annotations

import argparse
import bisect
import collections
import copy
import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = ROOT / "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
MEMBER_SHA = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
PACKAGE_FILES = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json",
                 "CERTIFICATE.json", "verify.py")
BATCH_SIZE = 16
BATCH_COUNT = 54
MAX_EVENTS = 25000


def require(condition, message):
    if not condition:
        raise ValueError(message)


def bounded_read(path, limit):
    require(path.stat().st_size <= limit, "input size limit")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    require(len(data) <= limit, "input size limit")
    return data


def digest(data):
    return hashlib.sha256(data).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def load_programs():
    raw = bounded_read(ARCHIVE, 8 * 1024 * 1024)
    require(digest(raw) == ARCHIVE_SHA, "archive hash")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as archive:
        member = archive.getmember(MEMBER)
        require(member.isfile() and member.size <= 1024 * 1024, "member size/type")
        stream = archive.extractfile(member)
        require(stream is not None, "member absent")
        with stream:
            data = stream.read(member.size + 1)
    require(len(data) == member.size and digest(data) == MEMBER_SHA, "member hash")
    payload = gzip.decompress(data)
    require(len(payload) <= 8 * 1024 * 1024, "program payload size")
    programs = json.loads(payload)
    require(set(programs) == {"forward", "backward"}, "orientations")
    for events in programs.values():
        require(type(events) is list and len(events) <= MAX_EVENTS, "event bound")
    return programs


def roles(event):
    tag = event[0]
    if tag in ("climb", "adapter", "residual_adapter"):
        return {("L", event[2])}
    if tag == "center":
        return {("C", event[1])}
    if tag == "scalar":
        operation = event[1]
        require(operation[0] in {"scale", "copy", "add", "clear"}, "scalar tag")
        result = {tuple(operation[1])}
        if operation[0] in {"copy", "add"}:
            result.add(tuple(operation[2]))
        return result
    require(tag == "phase", "unknown event tag")
    return set()


def is_rank_one(event):
    return event[0] == "climb" and event[5] == 1


def phase_span(events):
    starts = [i + 1 for i, event in enumerate(events) if event == ["phase", "B"]]
    require(len(starts) == 1, "unique phase B")
    start = starts[0]
    stops = [i for i in range(start, len(events)) if events[i][0] == "phase"]
    require(bool(stops), "phase B terminal marker")
    return start, stops[0]


def windows(events):
    start, stop = phase_span(events)
    skeleton = [i for i in range(start, stop) if not is_rank_one(events[i])]
    touch_positions = collections.defaultdict(list)
    for position, event_id in enumerate(skeleton):
        for role in roles(events[event_id]):
            touch_positions[role].append(position)
    result = {}
    gap = 0
    for event_id in range(start, stop):
        event = events[event_id]
        if not is_rank_one(event):
            gap += 1
            continue
        require(event[1] == "B", "climb phase")
        positions = touch_positions[("L", event[2])]
        j = bisect.bisect_left(positions, gap)
        lower = positions[j - 1] + 1 if j else 0
        upper = positions[j] if j < len(positions) else len(skeleton)
        require(lower <= gap <= upper, "original interval membership")
        result[event_id] = (lower, upper, event[2], gap)
    require(gap == len(skeleton), "skeleton length")
    return result, skeleton, start, stop


def check_batches(certificate, table, skeleton_size):
    require(set(certificate) == {"schema_version", "phase", "batch_size", "batches"},
            "certificate keys")
    require(certificate["schema_version"] == 1 and certificate["phase"] == "B",
            "certificate scope")
    require(certificate["batch_size"] == BATCH_SIZE, "batch size field")
    batches = certificate["batches"]
    require(type(batches) is list and len(batches) == BATCH_COUNT, "batch count")
    used = set()
    for batch in batches:
        require(set(batch) == {"gap", "event_ids"}, "batch keys")
        gap, ids = batch["gap"], batch["event_ids"]
        require(type(gap) is int and 0 <= gap <= skeleton_size, "gap range")
        require(type(ids) is list and len(ids) == BATCH_SIZE, "batch cardinality")
        require(all(type(i) is int and i in table for i in ids), "phase-B rank-one ids")
        require(len(set(ids)) == BATCH_SIZE and not used.intersection(ids),
                "disjoint event ids")
        require(len({table[i][2] for i in ids}) == BATCH_SIZE, "distinct destinations")
        require(all(table[i][0] <= gap <= table[i][1] for i in ids), "legal window")
        used.update(ids)
    return used


def reordered_ids(events, certificate, table, skeleton, start, stop, used):
    batches_at = collections.defaultdict(list)
    for batch in certificate["batches"]:
        batches_at[batch["gap"]].extend(batch["event_ids"])
    stay_at = collections.defaultdict(list)
    for event_id, (_, _, _, gap) in table.items():
        if event_id not in used:
            stay_at[gap].append(event_id)
    order = list(range(start))
    for gap in range(len(skeleton) + 1):
        order.extend(batches_at[gap])
        order.extend(stay_at[gap])
        if gap < len(skeleton):
            order.append(skeleton[gap])
    order.extend(range(stop, len(events)))
    require(sorted(order) == list(range(len(events))), "event permutation")
    require(order[:start] == list(range(start)) and
            order[stop:] == list(range(stop, len(events))), "outside phase unchanged")
    require([i for i in order[start:stop] if not is_rank_one(events[i])] == skeleton,
            "skeleton order")
    return order


def role_traces(events, order):
    traces = collections.defaultdict(list)
    for event_id in order:
        for role in roles(events[event_id]):
            traces[role].append(event_id)
    return dict(traces)


def check_trace_order(events, order):
    original = role_traces(events, range(len(events)))
    require(role_traces(events, order) == original, "complete shared-role traces")
    return len(original)


def check_contiguous_batches(order, certificate):
    positions = {event_id: i for i, event_id in enumerate(order)}
    for batch in certificate["batches"]:
        ids = batch["event_ids"]
        start = positions[ids[0]]
        require(order[start:start + BATCH_SIZE] == ids, "contiguous batch")


def check_orientation(events, certificate):
    table, skeleton, start, stop = windows(events)
    used = check_batches(certificate, table, len(skeleton))
    order = reordered_ids(events, certificate, table, skeleton, start, stop, used)
    role_count = check_trace_order(events, order)
    check_contiguous_batches(order, certificate)
    return {
        "events": len(events), "roles": role_count, "phase_B_climbs": len(table),
        "phase_B_skeleton": len(skeleton), "batches": len(certificate["batches"]),
        "batched_climbs": len(used), "unbatched_climbs": len(table) - len(used),
        "cardinality_upper_bound": len(table) // BATCH_SIZE,
        "changed_positions": sum(i != event_id for i, event_id in enumerate(order)),
        "original_word_sha256": digest(canonical(events)),
        "reordered_word_sha256": digest(canonical([events[i] for i in order])),
    }


def discover(table):
    """Reproduce the first witness, with no attempt to improve it further."""
    remaining = set(table)
    endpoints = sorted({upper for _, upper, _, _ in table.values()})
    batches = []
    for _ in range(len(table) // BATCH_SIZE):
        choices = []
        for gap in endpoints:
            available = [i for i in remaining if table[i][0] <= gap <= table[i][1]]
            if len(available) < BATCH_SIZE:
                continue
            available.sort(key=lambda i: (table[i][1] - table[i][0], table[i][1], i))
            take = available[:BATCH_SIZE]
            require(len({table[i][2] for i in take}) == BATCH_SIZE,
                    "discovery requires distinct active destinations")
            width_sum = sum(table[i][1] - table[i][0] for i in take)
            choices.append((width_sum, gap, take))
        if not choices:
            break
        _, gap, take = min(choices)
        batches.append({"gap": gap, "event_ids": take})
        remaining.difference_update(take)
    return {"schema_version": 1, "phase": "B", "batch_size": BATCH_SIZE,
            "batches": batches}


def expect_rejection(events, certificate, message):
    try:
        check_orientation(events, certificate)
    except ValueError as error:
        require(str(error) == message, "unexpected rejection: " + str(error))
    else:
        raise ValueError("accepted faulty witness: " + message)


def negative_controls(events, certificate):
    controls = []
    changed = copy.deepcopy(certificate)
    changed["batches"][0]["event_ids"].pop()
    controls.append((changed, "batch cardinality"))
    changed = copy.deepcopy(certificate)
    changed["batches"][1]["event_ids"][0] = changed["batches"][0]["event_ids"][0]
    controls.append((changed, "disjoint event ids"))
    changed = copy.deepcopy(certificate)
    changed["batches"][0]["gap"] = -1
    controls.append((changed, "gap range"))
    table, skeleton, _, _ = windows(events)
    changed = copy.deepcopy(certificate)
    changed["batches"][0]["event_ids"][0] = skeleton[0]
    controls.append((changed, "phase-B rank-one ids"))
    changed = copy.deepcopy(certificate)
    changed["batches"][0]["event_ids"][0] = next(
        i for i, event in enumerate(events) if is_rank_one(event) and event[1] == "A")
    controls.append((changed, "phase-B rank-one ids"))
    changed = copy.deepcopy(certificate)
    first = changed["batches"][0]
    illegal = next(g for g in range(len(skeleton) + 1)
                   if any(not table[i][0] <= g <= table[i][1] for i in first["event_ids"]))
    first["gap"] = illegal
    controls.append((changed, "legal window"))
    changed = copy.deepcopy(certificate)
    first_ids = changed["batches"][0]["event_ids"]
    same_register = next(i for i in table if i not in first_ids and
                         table[i][2] == table[first_ids[0]][2])
    first_ids[1] = same_register
    controls.append((changed, "distinct destinations"))
    for faulty, message in controls:
        expect_rejection(events, faulty, message)
    check_forbidden_swap(events)
    return len(controls) + 1


def check_forbidden_swap(events):
    start, stop = phase_span(events)
    site = next(i for i in range(start + 1, stop) if is_rank_one(events[i]) and
                roles(events[i]).intersection(roles(events[i - 1])))
    order = list(range(len(events)))
    order[site - 1], order[site] = order[site], order[site - 1]
    try:
        check_trace_order(events, order)
    except ValueError as error:
        require(str(error) == "complete shared-role traces", "wrong swap rejection")
    else:
        raise ValueError("accepted climb crossing its own preceding operation")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-discovery", action="store_true")
    parser.add_argument("--write-certificate", type=Path)
    args = parser.parse_args()
    programs = load_programs()
    if args.write_certificate:
        candidate = discover(windows(programs["forward"])[0])
        for events in programs.values():
            check_orientation(events, candidate)
        with args.write_certificate.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(candidate, indent=2) + "\n")
    certificate = json.loads(bounded_read(HERE / "CERTIFICATE.json", 64 * 1024))
    if args.check_discovery:
        require(discover(windows(programs["forward"])[0]) == certificate,
                "deterministic discovery equality")
    summaries = {}
    controls = 0
    for orientation, events in sorted(programs.items()):
        summaries[orientation] = check_orientation(events, certificate)
        controls += negative_controls(events, certificate)
    receipt = {
        "status": "PASS_PHASE_B_54_BATCHES", "claim_type": "finite_certificate",
        "orientations": summaries, "rejected_controls": controls,
        "archive_sha256": ARCHIVE_SHA, "member_sha256": MEMBER_SHA,
        "package_sha256": {name: digest(bounded_read(HERE / name, 512 * 1024))
                           for name in PACKAGE_FILES},
    }
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
