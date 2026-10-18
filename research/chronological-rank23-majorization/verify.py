#!/usr/bin/env python3
"""Integer-only, source-bound majorization certificate; no optimizer imports."""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
import hashlib
import io
import itertools
import json
from pathlib import Path
import tarfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARCHIVE = "research/community-frontier1094-audit/selected-replay.tar.gz"
ARCHIVE_SHA = "f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6"
MEMBER = "candidate/strict/global/base/providers/gauge44/LOCAL-PROGRAMS.json.gz"
MEMBER_SHA = "241fde27d4e43f5a9cb6b128f9f76c5131a53d09f0371676163f914d0b0fef3a"
BASE = {1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}
OPTIMAL = {1: 2412, 2: 362, 3: 123, 4: 158, 5: 87, 6: 127,
           8: 9, 9: 1, 12: 4, 15: 5, 16: 3}
TYPES = {(2,): 362, (3,): 123, (2, 2): 16, (3, 2): 5,
         (3, 3): 124, (2, 2, 2): 3, (2, 2, 2, 2): 1,
         (3,) * 4: 3, (2, 2) + (3,) * 4: 1,
         (3,) * 8: 1, (2, 2) + (3,) * 8: 1,
         (2, 2) + (3,) * 24: 1}


class Invalid(ValueError):
    """An explicit certificate obligation failed (also under python -O)."""


def require(ok, label):
    if not ok:
        raise Invalid(label)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def load_programs(root=ROOT):
    raw = (root / ARCHIVE).read_bytes()
    require(sha(raw) == ARCHIVE_SHA, "archive pin")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r:gz") as stream:
        members = [m for m in stream.getmembers() if m.name == MEMBER]
        require(len(members) == 1 and members[0].isfile(), "unique source member")
        packed = stream.extractfile(members[0]).read()
    require(sha(packed) == MEMBER_SHA, "member pin")
    data = json.loads(gzip.decompress(packed))
    require(set(data) == {"forward", "backward"}, "complete orientations")
    return data


def split_runs(events):
    # Remove phase annotations first, then group by eligibility. Unlike the
    # predecessor, no numerical costs or interval optimizer are used.
    numbered = [(i, e) for i, e in enumerate(events) if e[0] != "phase"]
    def eligible(item):
        e = item[1]
        return e[0] == "climb" and e[5] in (2, 3)
    return [[(i, e[5]) for i, e in group]
            for yes, group in itertools.groupby(numbered, key=eligible) if yes]


def paid_profile(events):
    result = Counter()
    for e in events:
        if e[0] == "climb":
            result[e[5]] += 1
        elif e[0] == "center":
            result[e[4]] += 1
    return dict(sorted(result.items()))


def greedy_partition(run):
    require(bool(run) and all(x in (2, 3) for x in run), "rank alphabet")
    blocks, start, mass = [], 0, 0
    for end, rank in enumerate(run):
        if mass + rank > 16:
            blocks.append((start, end, mass))
            start, mass = end, 0
        mass += rank
    blocks.append((start, len(run), mass))
    return blocks


def validate_partition(run, blocks):
    cursor = 0
    for start, end, mass in blocks:
        require(start == cursor and start < end <= len(run), "partition coverage")
        require(mass == sum(run[start:end]), "partition mass")
        require(0 < mass <= 16, "block cap")
        cursor = end
    require(cursor == len(run), "partition coverage")


def prefix_maxima(run):
    """Max mass of at most k marked blocks, over EVERY full partition.

    Every partition ends with one allowed interval. Its last block is either
    unmarked or marked. Induction on prefix length gives the exhaustive DP;
    for a fixed partition the best k marks are its k largest masses.
    """
    n = len(run)
    table = [[0] * (n + 1) for _ in range(n + 1)]
    ways = [1] + [0] * n
    interval_count = 0
    for end in range(1, n + 1):
        choices, mass = [], 0
        for start in range(end - 1, -1, -1):
            mass += run[start]
            if mass > 16:
                break
            choices.append((start, mass))
            ways[end] += ways[start]
            interval_count += 1
        for k in range(1, n + 1):
            table[end][k] = max(
                max(table[start][k], table[start][k - 1] + mass)
                for start, mass in choices)
    return table[n][1:], ways[n], interval_count


def verify_majorization(masses, maxima, total):
    require(all(type(x) is int and 0 < x <= 16 for x in masses), "candidate block cap")
    require(sum(masses) == total, "candidate total")
    ordered = sorted(masses, reverse=True) + [0] * (len(maxima) - len(masses))
    require(len(ordered) == len(maxima), "candidate length")
    prefix = list(itertools.accumulate(ordered))
    require(all(x >= y for x, y in zip(prefix, maxima)), "majorization inequality")
    return prefix


def reject(label, action, expected):
    try:
        action()
    except Invalid as error:
        require(str(error) == expected, "wrong rejecting predicate: " + label)
        return
    # Outside the handler: disabling the detector must make the control fail.
    raise Invalid("unexpected acceptance: " + label)


def controls():
    maxima, _, _ = prefix_maxima((3,) * 8)
    require(verify_majorization([15, 9], maxima, 24) ==
            verify_majorization([9, 15], maxima, 24), "block-order positive control")
    reject("inferior legal packing", lambda: verify_majorization([12, 12], maxima, 24),
           "majorization inequality")
    reject("missing mass", lambda: verify_majorization([15, 8], maxima, 24), "candidate total")
    reject("over-cap block", lambda: validate_partition((3,) * 8, [(0, 6, 18), (6, 8, 6)]), "block cap")
    reject("partition gap", lambda: validate_partition((3,) * 8, [(0, 5, 15), (6, 8, 6)]), "partition coverage")
    reject("wrong block mass", lambda: validate_partition((3,) * 8, [(0, 5, 14), (5, 8, 9)]), "partition mass")
    # Just ONE initial 2 refutes an extrapolation to every rank-2/3 string.
    run = (2,) + (3,) * 5
    broad_max, _, _ = prefix_maxima(run)
    reject("unrestricted greedy extrapolation",
           lambda: verify_majorization([14, 3], broad_max, 17), "majorization inequality")
    require(verify_majorization([15, 2], broad_max, 17)[0] == 15, "escaped-family positive control")
    a, b = ["climb", "test", 0, 0, 0, 2], ["climb", "test", 0, 0, 0, 3]
    require([tuple(r for _, r in run) for run in split_runs([a, ["phase"], b])] == [(2, 3)], "phase gauge")
    require([tuple(r for _, r in run) for run in split_runs([a, ["scalar"], b])] == [(2,), (3,)], "scalar barrier")
    require([tuple(r for _, r in run) for run in split_runs([a, ["center", 0, 0, 0, 2], b])] == [(2,), (3,)], "centre barrier")
    return {"rejection_controls": 6, "positive_controls": 5}


def compute(root=ROOT):
    programs = load_programs(root)
    type_rows = []
    for run, multiplicity in sorted(TYPES.items(), key=lambda item: (len(item[0]), item[0])):
        blocks = greedy_partition(run)
        validate_partition(run, blocks)
        maxima, ways, intervals = prefix_maxima(run)
        prefix = verify_majorization([b[2] for b in blocks], maxima, sum(run))
        require(prefix == maxima, "sharp sorted-prefix bounds")
        type_rows.append({"ranks": list(run), "multiplicity_per_orientation": multiplicity,
                          "partition": [list(b) for b in blocks], "sorted_prefix_maxima": maxima,
                          "all_legal_partitions": ways, "allowed_intervals": intervals})
    orientations = {}
    for name, events in sorted(programs.items()):
        require(len(events) == 24767, "source event count")
        require(paid_profile(events) == BASE, "complete source paid profile")
        runs = split_runs(events)
        census = Counter(tuple(r for _, r in run) for run in runs)
        require(census == TYPES, "complete run census")
        profile = Counter(BASE)
        schedule, grouped, mass = [], 0, 0
        for run in runs:
            ranks = tuple(r for _, r in run)
            for start, end, size in greedy_partition(ranks):
                if end - start > 1:
                    grouped += end - start
                    mass += size
                    for r in ranks[start:end]:
                        profile[r] -= 1
                    profile[size] += 1
                    schedule.append([run[start][0], run[end-1][0], size, list(ranks[start:end])])
        require(dict(profile) == OPTIMAL, "complete optimal paid profile")
        require(sum(r * c for r, c in profile.items()) == 5586, "full paid mass")
        require((len(runs), sum(map(len, runs)), len(schedule), grouped, mass) ==
                (641, 850, 162, 365, 1039), "coverage totals")
        orientations[name] = {"events": len(events), "runs": len(runs), "eligible_calls": 850,
                              "merged_blocks": len(schedule), "merged_calls": grouped,
                              "merged_mass": mass, "run_indices_sha256": sha(canonical(runs)),
                              "schedule": schedule}
    require(orientations["forward"] == orientations["backward"], "both orientation schedules")
    return {"schema_version": 1, "scope": "contiguous-rank23-cap16; 0<q<1; no_new_kappa",
            "archive_sha256": ARCHIVE_SHA, "member_sha256": MEMBER_SHA,
            "base_profile": {str(k): v for k, v in BASE.items()},
            "optimal_profile": {str(k): v for k, v in OPTIMAL.items()},
            "rank_mass": 5586, "run_types": type_rows, "orientations": orientations,
            "controls": controls()}


def read_fixed(path):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            require(k not in result, "duplicate receipt key")
            result[k] = v
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="explicitly create absent RESULT.json")
    args = parser.parse_args()
    expected = compute()
    result_path = HERE / "RESULT.json"
    if args.write:
        with result_path.open("x") as out:
            json.dump(expected, out, indent=2, sort_keys=True)
            out.write("\n")
    require(canonical(read_fixed(result_path)) == canonical(expected), "complete fixed receipt")
    print("PASS_CHRONOLOGICAL_RANK23_MAJORIZATION orientations=2 run_types=12 "
          "runs_per_orientation=641 merged_blocks=162 mass=5586 powers=all_0<q<1 no_new_kappa")


if __name__ == "__main__":
    main()
