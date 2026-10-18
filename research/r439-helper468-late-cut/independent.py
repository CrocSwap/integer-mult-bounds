#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Set-valued scalar replay and integer minor/normal geometry certificates."""
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HELPER = 468


def require(ok, message):
    if not ok:
        raise ValueError(message)


def mask_hex(values):
    return format(sum(1 << i for i in values), "x")


def primitive(row):
    divisor = math.gcd(*row)
    if not divisor:
        return row
    row = [x//divisor for x in row]
    if next(x for x in row if x) < 0:
        row = [-x for x in row]
    return row


def integer_basis(vectors):
    matrix = [primitive(list(row)) for row in vectors if any(row)]
    if not matrix:
        return ()
    rank = 0
    for col in range(len(matrix[0])):
        pivot = next((i for i in range(rank, len(matrix)) if matrix[i][col]), None)
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        selected = matrix[rank]
        entry = selected[col]
        for i, row in enumerate(matrix):
            if i != rank and row[col]:
                factor = row[col]
                matrix[i] = primitive([entry*x-factor*y for x, y in zip(row, selected)])
        rank += 1
    return tuple(tuple(row) for row in matrix[:rank])


def bareiss(matrix):
    """Exact determinant using integer divisions; no rational elimination."""
    a = [row[:] for row in matrix]
    if not a:
        return 1
    sign, previous = 1, 1
    for col in range(len(a)-1):
        pivot = next((i for i in range(col, len(a)) if a[i][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            sign = -sign
        entry = a[col][col]
        for i in range(col+1, len(a)):
            for j in range(col+1, len(a)):
                numerator = a[i][j]*entry-a[i][col]*a[col][j]
                quotient, remainder = divmod(numerator, previous)
                require(remainder == 0, "nonexact Bareiss division")
                a[i][j] = quotient
            a[i][col] = 0
        previous = entry
    return sign*a[-1][-1]


def inverse_sets(rows):
    left = [set(row) for row in rows]
    right = [{i} for i in range(len(rows))]
    for col in reversed(range(len(rows))):
        pivot = next((i for i in range(col+1) if col in left[i]), None)
        require(pivot is not None, "independent singular boundary")
        left[col], left[pivot] = left[pivot], left[col]
        right[col], right[pivot] = right[pivot], right[col]
        for i in range(len(rows)):
            if i != col and col in left[i]:
                left[i].symmetric_difference_update(left[col])
                right[i].symmetric_difference_update(right[col])
    require(left == [{i} for i in range(len(rows))], "independent inverse residual")
    return right


class Geometry:
    def __init__(self, word, certificate):
        self.word = word
        self.bases = [integer_basis(word["lines"][i] for i in frame) for frame in word["frames"]]
        self.cases = {}
        for case in [*certificate["cases"], certificate["full_frame"]]:
            self.validate_case(case)
            self.cases[tuple(case["frames"])] = case
        for i in range(word["v"]):
            target_frame = word["final"][word["v"]+i]
            normal = word["lines"][i]
            require(self.rank(target_frame) == 7 and any(normal), "target is not a hyperplane")
            require(all(sum(x*y for x, y in zip(normal, word["lines"][j])) == 0
                        for j in word["frames"][target_frame]), "wrong target normal")
        require(self.rank(1) == 8 and all(word["final"][i] == 1 for i in range(661)
                                        if not 111 <= i < 222), "non-target final contract changed")

    def rank(self, frame):
        return len(self.bases[frame])

    @lru_cache(maxsize=None)
    def contained(self, small, large):
        return len(integer_basis([*self.bases[small], *self.bases[large]])) == self.rank(large)

    def validate_case(self, case):
        word = self.word
        union = {i for f in case["frames"] for i in word["frames"][f]}
        lines, columns, dimension = case["basis_lines"], case["minor_columns"], case["rank"]
        require(dimension in (7, 8) and len(lines) == len(set(lines)) == dimension and
                set(lines) <= union and len(columns) == len(set(columns)) == dimension and
                all(0 <= i < 8 for i in columns), "bad determinant witness dimensions")
        value = bareiss([[word["lines"][i][j] for j in columns] for i in lines])
        require(value != 0 and str(value) == case["minor_determinant"], "minor witness disagreement")
        if dimension == 7:
            normal = case["annihilating_normal"]
            require(len(normal) == 8 and any(normal) and
                    all(sum(x*y for x, y in zip(normal, word["lines"][i])) == 0 for i in union),
                    "invalid rank-seven upper-bound normal")
            witness = case["target208_separation"]
            target = word["final"][208]
            require(witness["frame"] in case["frames"] and
                    witness["line"] in word["frames"][witness["frame"]] and
                    len(witness["normal"]) == 8 and any(witness["normal"]), "invalid separating witness")
            require(all(sum(x*y for x, y in zip(witness["normal"], word["lines"][i])) == 0
                        for i in word["frames"][target]), "separator does not annihilate target208")
            value = sum(x*y for x, y in zip(witness["normal"], word["lines"][witness["line"]]))
            require(value != 0 and value == witness["dot"], "separator does not detect the join")

    def join_rank(self, frames):
        require(frames in self.cases, "missing explicit geometry case")
        return self.cases[frames]["rank"]

    def join_contained_in_target(self, frames, target):
        normal = self.word["lines"][target-self.word["v"]]
        return all(sum(x*y for x, y in zip(normal, self.word["lines"][i])) == 0
                   for i in self.cases[frames]["basis_lines"])


def replay(word, geometry):
    n, v = 661, 111
    frames = word["start"][:]
    rows = [{i} for i in range(n)]
    for section in ("D", "A"):
        for frame, target, sources in word[section]:
            for register in [target, *sources]:
                require(geometry.contained(frames[register], frame), "independent prefix descent")
                frames[register] = frame
            for source in sources:
                rows[target].symmetric_difference_update(rows[source])
    require(all(frames[i] == 0 for i in range(v, 2*v)), "independent scatter frame changed")
    snapshots = [set(rows[i]) for i in word["ret"]]
    require(len(snapshots) == 9, "wrong retained snapshots")
    for i, sources in enumerate(word["scatter"]):
        for index in sources:
            rows[v+i].symmetric_difference_update(snapshots[index])
    inverse = inverse_sets(rows)
    events, records = [], []

    def cut():
        current = frames[HELPER]
        record = dict(cut=len(events), helper_frame=current, helper_rank=geometry.rank(current))
        if record["helper_rank"] > 7:
            record["reason"] = "helper_already_rank8"
            records.append(record)
            return
        restore = inverse[HELPER]
        dirt = {i for i, row in enumerate(rows) if HELPER in row}
        participants = restore | dirt | {HELPER}
        frame_ids = tuple(sorted({frames[i] for i in participants}))
        dimension = geometry.join_rank(frame_ids)
        record.update(restore_hex=mask_hex(restore), dirt_hex=mask_hex(dirt),
                      participants_hex=mask_hex(participants), join_frames=list(frame_ids), join_rank=dimension)
        if dimension == 8:
            record["reason"] = "footprint_rank8"
        else:
            illegal, lost = [], []
            for target in range(v, 2*v):
                if geometry.join_contained_in_target(frame_ids, target):
                    continue
                if target in participants:
                    illegal.append(target)
                missing = (inverse[target] ^ inverse[target-v]) & participants
                if missing:
                    lost.append([target, mask_hex(missing)])
            record.update(illegal_target_promotions=illegal, lost_target_inputs=lost)
            record["reason"] = ("illegal_target_promotion" if illegal else
                                "lost_target_input" if lost else "not_excluded")
        records.append(record)

    cut()
    for section in ("B", "C"):
        for gate, (frame, target, sources) in enumerate(word[section]):
            require(len(set([target, *sources])) == len(sources)+1, "independent gate operands")
            for register in [target, *sources]:
                previous = frames[register]
                require(geometry.contained(previous, frame), "independent suffix descent")
                if previous != frame:
                    require(geometry.rank(frame) > geometry.rank(previous), "independent redundant MOVE")
                    frames[register] = frame
                    events.append([section, gate, "MOVE", register, previous, frame])
                    cut()
            for offset, source in enumerate(sources):
                rows[target].symmetric_difference_update(rows[source])
                for row in inverse:
                    if target in row:
                        row.symmetric_difference_update({source})
                events.append([section, gate, "ADD", target, source, offset])
                cut()
    for register, frame in enumerate(word["final"]):
        previous = frames[register]
        require(geometry.contained(previous, frame), "independent final descent")
        if previous != frame:
            require(geometry.rank(frame) > geometry.rank(previous), "independent final alias")
            frames[register] = frame
            events.append(["final", register, "MOVE", register, previous, frame])
            cut()
    expected = [{i, i-v} if v <= i < 2*v else {i} for i in range(n)]
    require(rows == expected and inverse == expected and frames == word["final"],
            "independent full dirty/inverse endpoint changed")
    return events, records


def main():
    try:
        sources = json.loads((HERE / "SOURCES.json").read_text())
        for source in sources["archives"]:
            name = Path(source["local_path"])
            require(not name.is_absolute() and ".." not in name.parts, "unsafe archive path")
            require(hashlib.sha256((HERE/name).read_bytes()).hexdigest() == source["sha256"], "source archive drift")
        word = json.loads(gzip.decompress((HERE / "inputs/PR589-WORD.json.gz").read_bytes()))
        geometry_certificate = json.loads((HERE / "generated/GEOMETRY.json").read_text())
        geometry = Geometry(word, geometry_certificate)
        events, records = replay(word, geometry)
        require(events == json.loads((HERE / "generated/EVENTS.json").read_text()), "independent event coverage changed")
        recorded = [json.loads(row) for row in (HERE / "generated/CUTS.jsonl").read_text().splitlines()]
        require(records == recorded, "independent complete cut ledger changed")
        raw = "".join(json.dumps(row, sort_keys=True, separators=(",", ":"))+"\n" for row in records).encode()
        counts = Counter(row["reason"] for row in records)
        general_start = next(row["cut"] for row in records
                             if row["helper_rank"] == 8 or row.get("join_rank") == 8)
        require(all(row["helper_rank"] == 8 or row.get("join_rank") == 8
                    for row in records[general_start:]), "independent late footprint returns below eight")
        summary = dict(helper=HELPER, registers=661, targets=111, cuts=len(records), events=len(events),
                       event_kinds=dict(Counter(e[2] for e in events)), reasons=dict(sorted(counts.items())),
                       not_excluded=[row["cut"] for row in records if row["reason"] == "not_excluded"],
                       complete_forward_and_inverse_endpoint=True,
                       first_rank8_cut=next(row["cut"] for row in records if row["helper_rank"] == 8),
                       arbitrary_suffix_rank8_from_cut=general_start,
                       arbitrary_suffix_excluded_cuts=len(records)-general_start,
                       first_rank8_footprint_event=events[general_start-1],
                       earlier_two_sided_rank7_cuts=general_start,
                       eligible_current_rank_histogram=dict(Counter(row["helper_rank"] for row in records
                                                                    if row["helper_rank"] <= 7)),
                       geometry_cases=len(geometry_certificate["cases"]),
                       geometry_sha256=hashlib.sha256(json.dumps(geometry_certificate, sort_keys=True,
                                                                 separators=(",", ":")).encode()).hexdigest(),
                       ledger_sha256=hashlib.sha256(raw).hexdigest(),
                       events_sha256=hashlib.sha256(json.dumps(events, separators=(",", ":")).encode()).hexdigest())
        require(json.loads(json.dumps(summary)) == json.loads((HERE / "generated/CERTIFICATE.json").read_text()),
                "independent summary changed")
        require(not summary["not_excluded"], "independent cut survives")
        print("PASS_INDEPENDENT_R439_HELPER468 cuts=4874 excluded=4874 integer_geometry_cases=9 arbitrary_suffix_from=177")
    except (OSError, ValueError, KeyError, TypeError) as error:
        print("REJECT_INDEPENDENT_R439_HELPER468: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
