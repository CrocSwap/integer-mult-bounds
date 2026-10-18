# SPDX-License-Identifier: Apache-2.0
# Cinna Davis, with substantial OpenAI Codex assistance.
"""Exact late-cut ledger; footprint argument follows Ross Richardson / PR1256."""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
import json
import math

HELPER = 468


def require(ok, message):
    if not ok:
        raise ValueError(message)


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length()-1
        mask ^= bit


def invert(matrix):
    left = matrix[:]
    right = [1 << i for i in range(len(left))]
    for col in range(len(left)):
        pivot = next((i for i in range(col, len(left)) if left[i] & (1 << col)), None)
        require(pivot is not None, "singular scalar boundary")
        left[col], left[pivot] = left[pivot], left[col]
        right[col], right[pivot] = right[pivot], right[col]
        for i in range(len(left)):
            if i != col and left[i] & (1 << col):
                left[i] ^= left[col]
                right[i] ^= right[col]
    require(left == [1 << i for i in range(len(left))], "inverse residual")
    return right


def rref(vectors):
    rows = []
    for vector in vectors:
        row = list(map(Fraction, vector))
        for pivot, basis in rows:
            coefficient = row[pivot]
            row = [a-coefficient*b for a, b in zip(row, basis)]
        pivot = next((i for i, value in enumerate(row) if value), None)
        if pivot is None:
            continue
        coefficient = row[pivot]
        row = [value/coefficient for value in row]
        rows = [(p, [a-basis[pivot]*b for a, b in zip(basis, row)])
                for p, basis in rows]
        rows.append((pivot, row))
        rows.sort()
    return tuple(tuple(row) for _, row in rows)


def contains_basis(small, large):
    pivots = [(next(i for i, x in enumerate(row) if x), row) for row in large]
    for vector in small:
        row = list(vector)
        for pivot, basis in pivots:
            coefficient = row[pivot]
            row = [a-coefficient*b for a, b in zip(row, basis)]
        if any(row):
            return False
    return True


class Geometry:
    def __init__(self, word):
        self.word = word
        self.bases = [rref(word["lines"][i] for i in frame) for frame in word["frames"]]

    def rank(self, frame):
        return len(self.bases[frame])

    @lru_cache(maxsize=None)
    def contained(self, small, large):
        return contains_basis(self.bases[small], self.bases[large])

    @lru_cache(maxsize=None)
    def join(self, frame_ids):
        return rref(row for f in frame_ids for row in self.bases[f])

    @lru_cache(maxsize=None)
    def join_contained(self, frame_ids, terminal):
        return contains_basis(self.join(frame_ids), self.bases[terminal])

    def separation(self, frame_ids, terminal):
        """A rational annihilator of the target frame detecting the join."""
        import math
        large = self.bases[terminal]
        pivots = {next(i for i, x in enumerate(row) if x): row for row in large}
        for free in range(self.word["h"]):
            if free in pivots:
                continue
            normal = [Fraction(i == free) for i in range(self.word["h"])]
            for p, row in pivots.items():
                normal[p] = -row[free]
            scale = 1
            for x in normal:
                scale = math.lcm(scale, x.denominator)
            normal = [int(x*scale) for x in normal]
            for f in frame_ids:
                for line in self.word["frames"][f]:
                    dot = sum(x*y for x, y in zip(normal, self.word["lines"][line]))
                    if dot:
                        return dict(normal=normal, frame=f, line=line, dot=dot)
        raise ValueError("no separating normal for an excluded join")


def add(rows, inverse, target, source):
    require(target != source, "self ADD")
    rows[target] ^= rows[source]
    tbit, sbit = 1 << target, 1 << source
    for i, row in enumerate(inverse):
        if row & tbit:
            inverse[i] ^= sbit


def initial_boundary(word, geometry):
    n, v = 2*word["v"]+word["R"], word["v"]
    require((n, v, word["h"]) == (661, 111, 8), "wrong pinned dimensions")
    frames = word["start"][:]
    rows = [1 << i for i in range(n)]
    for section in ("D", "A"):
        for frame, target, sources in word[section]:
            for register in [target, *sources]:
                require(geometry.contained(frames[register], frame), "prefix frame descent")
                frames[register] = frame
            for source in sources:
                require(target != source, "prefix self ADD")
                rows[target] ^= rows[source]
    require(all(frames[i] == 0 for i in range(v, 2*v)), "wrong scatter target frame")
    for i, sources in enumerate(word["scatter"]):
        for index in sources:
            rows[v+i] ^= rows[word["ret"][index]]
    require(len(word["ret"]) == 9, "retained COPY/ERASE inventory changed")
    return frames, rows, invert(rows)


def suffix_events(word, initial, geometry):
    frames = initial[:]
    events = []
    for section in ("B", "C"):
        for gate, (frame, target, sources) in enumerate(word[section]):
            require(len(set([target, *sources])) == len(sources)+1, "invalid gate operands")
            for register in [target, *sources]:
                previous = frames[register]
                require(geometry.contained(previous, frame), "suffix frame descent")
                if previous != frame:
                    require(geometry.rank(frame) > geometry.rank(previous), "redundant frame alias")
                    events.append([section, gate, "MOVE", register, previous, frame])
                    frames[register] = frame
            for offset, source in enumerate(sources):
                events.append([section, gate, "ADD", target, source, offset])
    for register, frame in enumerate(word["final"]):
        previous = frames[register]
        require(geometry.contained(previous, frame), "final frame descent")
        if previous != frame:
            require(geometry.rank(frame) > geometry.rank(previous), "redundant final alias")
            events.append(["final", register, "MOVE", register, previous, frame])
            frames[register] = frame
    return events


def inspect_cut(word, geometry, frames, rows, inverse, event_index):
    current = frames[HELPER]
    record = dict(cut=event_index, helper_frame=current, helper_rank=geometry.rank(current))
    if record["helper_rank"] > 7:
        record["reason"] = "helper_already_rank8"
        return record
    restore = inverse[HELPER]
    dirt = sum(1 << i for i, row in enumerate(rows) if row & (1 << HELPER))
    participants = restore | dirt | (1 << HELPER)
    frame_ids = tuple(sorted({frames[i] for i in bits(participants)}))
    joined = geometry.join(frame_ids)
    record.update(restore_hex=format(restore, "x"), dirt_hex=format(dirt, "x"),
                  participants_hex=format(participants, "x"), join_frames=list(frame_ids),
                  join_rank=len(joined))
    if len(joined) > 7:
        record["reason"] = "footprint_rank8"
        return record
    lost, illegal = [], []
    for target in range(word["v"], 2*word["v"]):
        if geometry.join_contained(frame_ids, word["final"][target]):
            continue
        if participants & (1 << target):
            illegal.append(target)
        missing = (inverse[target] ^ inverse[target-word["v"]]) & participants
        if missing:
            lost.append([target, format(missing, "x")])
    record.update(illegal_target_promotions=illegal, lost_target_inputs=lost)
    record["reason"] = ("illegal_target_promotion" if illegal else
                        "lost_target_input" if lost else "not_excluded")
    return record


def ledger_bytes(records):
    return "".join(json.dumps(row, sort_keys=True, separators=(",", ":"))+"\n"
                   for row in records).encode()


def determinant(matrix):
    a = [list(map(Fraction, row)) for row in matrix]
    value = Fraction(1)
    for column in range(len(a)):
        pivot = next((i for i in range(column, len(a)) if a[i][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            a[column], a[pivot] = a[pivot], a[column]
            value = -value
        entry = a[column][column]
        value *= entry
        for i in range(column+1, len(a)):
            factor = a[i][column]/entry
            a[i] = [x-factor*y for x, y in zip(a[i], a[column])]
    return value


def geometry_witness(word, geometry, frame_ids):
    union = sorted({i for f in frame_ids for i in word["frames"][f]})
    chosen = []
    for i in union:
        if len(rref(word["lines"][j] for j in chosen+[i])) > len(chosen):
            chosen.append(i)
    dimension = len(chosen)
    columns = next(c for c in itertools.combinations(range(word["h"]), dimension)
                   if determinant([[word["lines"][i][j] for j in c] for i in chosen]))
    value = determinant([[word["lines"][i][j] for j in columns] for i in chosen])
    result = dict(frames=list(frame_ids), rank=dimension, basis_lines=chosen,
                  minor_columns=list(columns), minor_determinant=str(value))
    if dimension == 7:
        joined = geometry.join(frame_ids)
        pivots = {next(i for i, x in enumerate(row) if x): row for row in joined}
        free = next(i for i in range(word["h"]) if i not in pivots)
        normal = [Fraction(i == free) for i in range(word["h"])]
        for p, row in pivots.items():
            normal[p] = -row[free]
        scale = math.lcm(*(x.denominator for x in normal))
        normal = [int(x*scale) for x in normal]
        divisor = math.gcd(*normal)
        normal = [x//divisor for x in normal]
        if next(x for x in normal if x) < 0:
            normal = [-x for x in normal]
        require(all(sum(x*y for x, y in zip(normal, word["lines"][i])) == 0 for i in union),
                "join normal is not an annihilator")
        result["annihilating_normal"] = normal
        result["target208_separation"] = geometry.separation(frame_ids, word["final"][208])
    return result


def census(word):
    geometry = Geometry(word)
    frames, rows, inverse = initial_boundary(word, geometry)
    events = suffix_events(word, frames, geometry)
    records = [inspect_cut(word, geometry, frames, rows, inverse, 0)]
    for index, event in enumerate(events, 1):
        if event[2] == "MOVE":
            _, _, _, register, previous, frame = event
            require(frames[register] == previous, "MOVE chronology disagreement")
            frames[register] = frame
        else:
            _, _, _, target, source, _ = event
            add(rows, inverse, target, source)
        records.append(inspect_cut(word, geometry, frames, rows, inverse, index))
    expected = [(1 << i) ^ ((1 << (i-word["v"])) if word["v"] <= i < 2*word["v"] else 0)
                for i in range(len(rows))]
    require(rows == expected and inverse == expected, "full dirty endpoint or inverse changed")
    require(frames == word["final"], "final frame inventory changed")
    counts = Counter(record["reason"] for record in records)
    general_start = next(record["cut"] for record in records
                         if record["helper_rank"] == 8 or record.get("join_rank") == 8)
    require(all(record["helper_rank"] == 8 or record.get("join_rank") == 8
                for record in records[general_start:]), "later proper-frame footprint unexpectedly returns")
    frame_sets = sorted({tuple(record["join_frames"]) for record in records if "join_frames" in record})
    geometry_certificate = dict(
        cases=[geometry_witness(word, geometry, frame_ids) for frame_ids in frame_sets],
        full_frame=geometry_witness(word, geometry, (1,)))
    summary = dict(helper=HELPER, registers=len(rows), targets=word["v"], cuts=len(records),
                   events=len(events), event_kinds=dict(Counter(e[2] for e in events)),
                   reasons=dict(sorted(counts.items())), not_excluded=[r["cut"] for r in records
                                                                   if r["reason"] == "not_excluded"],
                   complete_forward_and_inverse_endpoint=True,
                   first_rank8_cut=next(r["cut"] for r in records if r["helper_rank"] == 8),
                   arbitrary_suffix_rank8_from_cut=general_start,
                   arbitrary_suffix_excluded_cuts=len(records)-general_start,
                   first_rank8_footprint_event=events[general_start-1],
                   earlier_two_sided_rank7_cuts=general_start,
                   eligible_current_rank_histogram=dict(Counter(r["helper_rank"] for r in records
                                                                if r["helper_rank"] <= 7)),
                   geometry_cases=len(frame_sets),
                   geometry_sha256=hashlib.sha256(json.dumps(geometry_certificate, sort_keys=True,
                                                             separators=(",", ":")).encode()).hexdigest(),
                   ledger_sha256=hashlib.sha256(ledger_bytes(records)).hexdigest(),
                   events_sha256=hashlib.sha256(json.dumps(events, separators=(",", ":")).encode()).hexdigest())
    return events, records, summary, geometry_certificate
