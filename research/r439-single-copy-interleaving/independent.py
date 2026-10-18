#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Ross Richardson, with substantial OpenAI Codex assistance.
"""Independent set-valued replay of the fixed single-copy witness.

No primary/predecessor checker or constructor is imported.  The only circuit
input is the pinned PR1062 word.  Witness discovery is deliberately absent.
"""

import argparse
import copy
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from math import gcd
from pathlib import Path
from typing import NamedTuple


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/r439-bsection-stars-seed01/candidate.json.gz"
SOURCE_SHA256 = "b452d2c2b0b2a546d1105b1da9769aa78e5c54d6f00e97b30c77e3f54ce445ee"
PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}


class AuditError(ValueError):
    def __init__(self, stage, message):
        super().__init__(stage + ": " + message)
        self.stage = stage


def require(condition, stage, message):
    if not condition:
        raise AuditError(stage, message)


class Event(NamedTuple):
    kind: str
    dst: int
    src: int
    old_frame: int
    new_frame: int
    rank: int
    phase: int


def rational_rank(vectors):
    """Fraction-free elimination over Q, normalizing each residual by gcd."""
    pivots = []
    for vector in vectors:
        row = list(vector)
        for p, previous in pivots:
            if row[p]:
                factor, divisor = row[p], previous[p]
                row = [divisor * x - factor * y for x, y in zip(row, previous)]
                common = 0
                for x in row:
                    common = gcd(common, x)
                if common:
                    row = [x // common for x in row]
        nonzero = next((i for i, x in enumerate(row) if x), None)
        if nonzero is not None:
            pivots.append((nonzero, row))
    return len(pivots)


def xor_gate(rows, gate):
    _, destination, sources = gate
    for source in sources:
        rows[destination].symmetric_difference_update(rows[source])


def target_apply(rows, gate, v):
    _, destination, sources = gate
    for source in sources:
        rows[destination - v].symmetric_difference_update(rows[source - v])


def source_parts(word):
    v, n = word["v"], 2 * word["v"] + word["R"]
    require((v, n, len(word["ret"])) == (111, 661, 9), "source", "fixed dimensions")
    preparation, undo = word["D"][236:542], word["D"][653:959]
    require(len(undo) == 306 and preparation[::-1] == undo,
            "source", "target basis and its literal inverse")
    require(all(f == 0 and len(ss) == 1 and v <= d < 2 * v
                and v <= ss[0] < 2 * v and d != ss[0] for f, d, ss in undo),
            "source", "elementary target-only undo")
    # Moving undo after these gates is justified by disjoint register support.
    for gates, description in ((word["D"][959:], "D helper restoration"),
                               (word["A"], "A")):
        require(all(not v <= r < 2 * v for _, d, ss in gates for r in [d] + ss),
                "source", description + " must not touch targets")
    require(all(f == 0 for f, _, _ in word["D"]), "source", "D is at frame zero")
    require(len(set(word["ret"])) == 9, "source", "distinct retained totals")
    return v, n, undo


def split_and_scatter(word, witness):
    v, _, undo = source_parts(word)
    require(witness.get("schema_version") == 1, "witness", "schema version")
    require(witness.get("optimality_claim") is False, "witness", "no optimum claim")
    modes = {"literal306": [], "ideal303": [31, 51, 52]}
    order = witness.get("order")
    require(order in modes and witness.get("keep_undo_indices") == modes[order],
            "witness", "one of the two fixed orders")
    keep = set(modes[order])
    kept = [g for i, g in enumerate(undo) if i in keep]
    deferred = [g for i, g in enumerate(undo) if i not in keep]
    left, right = [{i} for i in range(v)], [{i} for i in range(v)]
    for g in undo:
        target_apply(left, g, v)
    for g in kept + deferred:
        target_apply(right, g, v)
    require(left == right, "split", "kept then deferred must equal original undo")
    column, taps = witness.get("column"), witness.get("taps")
    require(type(column) is int and 0 <= column < 9, "witness", "column range")
    require(isinstance(taps, list) and taps, "witness", "nonempty explicit taps")
    for tap in taps:
        require(isinstance(tap, list) and len(tap) == 2
                and all(type(x) is int for x in tap)
                and 0 <= tap[0] <= len(deferred) and 0 <= tap[1] < v,
                "witness", "cut and target range")
    # Every total has its own formal symbol. Inverting the fixed gate sequence
    # on the original scatter rows determines the unique cut-zero listing.
    transformed = [set(js) for js in word["scatter"]]
    for gate in reversed(deferred):
        target_apply(transformed, gate, v)
    # This is a forward, zero-start execution, not a suffix-vector constructor.
    response = [set() for _ in range(v)]
    at_cut = defaultdict(list)
    for cut, target in taps:
        at_cut[cut].append(target)
    for cut in range(len(deferred) + 1):
        for target in at_cut[cut]:
            response[target].symmetric_difference_update({column})
        if cut < len(deferred):
            target_apply(response, deferred[cut], v)
    required = [{column} if column in js else set() for js in word["scatter"]]
    require(response == required, "tap-response", "complete forward tap coefficient")
    # The published stream places the kept gates after the helper-only tail.
    # source_parts() proves that this relocation has disjoint support.
    modified_d = word["D"][:653] + word["D"][959:] + kept
    return modified_d, deferred, transformed, at_cut


def make_stream(word, witness=None):
    v, n, _ = source_parts(word)
    frame_sets = [set(frame) for frame in word["frames"]]
    ranks = [rational_rank(word["lines"][i] for i in frame) for frame in word["frames"]]
    zero = [i for i, rank in enumerate(ranks) if rank == 0]
    require(zero == [0], "frame", "unique zero frame")
    current, events = list(word["start"]), []

    def move(role, frame):
        old = current[role]
        if old != frame:
            require(frame_sets[old] < frame_sets[frame], "frame", "strict ordered inclusion")
            events.append(Event("move", role, -1, old, frame, ranks[frame] - ranks[old], 0))
            current[role] = frame

    def gates(sequence, phase):
        for frame, destination, sources in sequence:
            require(destination not in sources, "frame", "no self ADD")
            for role in [destination] + sources:
                move(role, frame)
            for source in sources:
                events.append(Event("add", destination, source, frame, frame, 0, phase))

    def copy_total(j):
        centre = word["ret"][j]
        f = current[centre]
        events.append(Event("copy", n, centre, f, 0, ranks[f], 3))

    def erase_total(j):
        centre = word["ret"][j]
        events.append(Event("erase", n, centre, current[centre], 0, 0, 3))

    def tap(target):
        require(current[v + target] == 0, "frame", "scatter target is at zero")
        events.append(Event("add", v + target, n, 0, 0, 0, 3))

    if witness is None:
        gates(word["D"], 1)
        gates(word["A"], 2)
        for j in range(9):
            copy_total(j)
            for target, row in enumerate(word["scatter"]):
                if j in row:
                    tap(target)
            erase_total(j)
    else:
        modified_d, deferred, transformed, at_cut = split_and_scatter(word, witness)
        gates(modified_d, 1)
        gates(word["A"], 2)
        late = witness["column"]
        for j in range(9):
            if j == late:
                continue
            copy_total(j)
            for target, row in enumerate(transformed):
                if j in row:
                    tap(target)
            erase_total(j)
        copy_total(late)
        for cut in range(len(deferred) + 1):
            for target in at_cut[cut]:
                tap(target)
            if cut < len(deferred):
                gates([deferred[cut]], 4)
        erase_total(late)
    gates(word["B"], 4)
    gates(word["C"], 5)
    for role, frame in enumerate(word["final"]):
        move(role, frame)
    return events, ranks


def replay(word, events, ranks, reverse=False):
    v, n = word["v"], 2 * word["v"] + word["R"]
    rows = [{i} for i in range(n)] + [set()]
    frames = list(word["final"] if reverse else word["start"]) + [0]
    norms, maximum = [1] * n + [0], 1
    live = None
    copies, erasures, adds = 0, 0, 0
    for event in reversed(events) if reverse else events:
        kind, d, s, old, new, charge, _ = event
        if kind == "move":
            before, after = (new, old) if reverse else (old, new)
            require(frames[d] == before, "frame", "MOVE starts at actual frame")
            require(charge == ranks[new] - ranks[old] and charge > 0,
                    "charge", "MOVE price")
            frames[d] = after
            continue
        if reverse and kind in ("copy", "erase"):
            kind = "erase" if kind == "copy" else "copy"
        if kind == "add":
            require(frames[d] == frames[s] == old == new,
                    "frame", "ADD operand frames")
            require((d != n and s != n) or live is not None,
                    "lifecycle", "temporary use outside COPY lifetime")
            rows[d].symmetric_difference_update(rows[s])
            norms[d] += norms[s]
            maximum = max(maximum, norms[d])
            adds += 1
        elif kind == "copy":
            require(d == n and live is None and not rows[n], "lifecycle", "single fresh COPY")
            require(frames[s] == old and frames[n] == new == 0,
                    "frame", "COPY source and destination frames")
            # Charge belongs to the forward COPY, even when ERASE is reversed.
            if not reverse:
                require(charge == ranks[old], "charge", "COPY price")
            rows[d] = set(rows[s])
            norms[d] = norms[s]
            maximum = max(maximum, norms[d])
            live = (s, old, frozenset(rows[s]))
            copies += 1
        elif kind == "erase":
            require(d == n and live is not None, "lifecycle", "ERASE needs live COPY")
            require(live[:2] == (s, old) and frames[s] == old and frames[n] == 0
                    and frozenset(rows[s]) == live[2] and rows[d] == rows[s],
                    "lifecycle", "ERASE exact equality and unchanged copied source")
            if reverse:
                require(charge == ranks[old], "charge", "reverse COPY price")
            rows[d] = set()
            norms[d], live = 0, None
            erasures += 1
        else:
            raise AuditError("record", "unknown record kind")
    require(live is None and not rows[n], "lifecycle", "temporary restored")
    require(frames[:-1] == list(word["start"] if reverse else word["final"]),
            "frame", "final frames")
    expected = [{i, i - v} if v <= i < 2 * v else {i} for i in range(n)]
    require(rows[:-1] == expected, "boundary", "all 661 independent dirty-input columns")
    require(copies == erasures == 9, "lifecycle", "nine COPY/ERASE pairs")
    return {"adds": adds, "copies": copies, "erasures": erasures, "majorant": maximum}


def native_records(events):
    """Project independent events into the existing six-int record convention."""
    records = []
    for kind, d, s, old, new, rank, phase in events:
        if kind == "move":
            records.append((0, d, old, new, rank, 0))
        elif kind == "add":
            records.append((1, d, s, 1, old, phase))
        else:
            records.append((2 if kind == "copy" else 3, s, d, old, new, rank))
    return records


def controls(word, witness, events, ranks):
    passed = []

    def reject(label, stage, action):
        try:
            action()
        except AuditError as error:
            require(error.stage == stage, "control", label + " rejected by wrong obligation")
            passed.append(label)
            return
        raise AuditError("control", "unexpected acceptance: " + label)

    bad = copy.deepcopy(witness)
    bad["taps"].pop()
    reject("omitted witness tap", "tap-response", lambda: split_and_scatter(word, bad))
    bad = copy.deepcopy(witness)
    bad["taps"][0][1] = (bad["taps"][0][1] + 1) % word["v"]
    reject("wrong witness target", "tap-response", lambda: split_and_scatter(word, bad))
    # Find the deferred target-target block, not an unrelated compensation ADD.
    index = next(i for i, e in enumerate(events) if e.kind == "add" and e.phase == 4
                 and e.old_frame == 0 and word["v"] <= e.dst < 2 * word["v"]
                 and word["v"] <= e.src < 2 * word["v"])
    bad_events = events[:index] + events[index + 1:]
    reject("unpaid omitted undo", "boundary", lambda: replay(word, bad_events, ranks))
    index = next(i for i, e in enumerate(events) if e.kind == "copy")
    bad_events = list(events)
    bad_events[index] = bad_events[index]._replace(rank=bad_events[index].rank - 1)
    reject("undercharged COPY", "charge", lambda: replay(word, bad_events, ranks))
    # Corrupt the live copied symbol immediately before ERASE with a zero-frame
    # target row. This keeps frame checks valid and isolates exact restoration.
    index = next(i for i, e in enumerate(events) if e.kind == "erase")
    temp = 2 * word["v"] + word["R"]
    bad_events = events[:index] + [Event("add", temp, word["v"], 0, 0, 0, 3)] + events[index:]
    reject("changed live copy", "lifecycle", lambda: replay(word, bad_events, ranks))
    # A different presentation of the same finite word must remain acceptable.
    equivalent = copy.deepcopy(witness)
    equivalent["taps"] = list(reversed(equivalent["taps"]))
    eq_events, eq_ranks = make_stream(word, equivalent)
    require(replay(word, eq_events, eq_ranks) == replay(word, events, ranks),
            "control", "tap listing order is not execution order")
    passed.append("accepted reordered tap list")
    return passed


def audit(witness_path=HERE / "WITNESS.json", source_path=SOURCE):
    raw = Path(source_path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "source", "source SHA256")
    word = json.loads(gzip.decompress(raw))
    witness = json.loads(Path(witness_path).read_text())
    original, original_ranks = make_stream(word)
    events, ranks = make_stream(word, witness)
    require(ranks == original_ranks, "frame", "unchanged geometry")
    original_moves = [e for e in original if e.kind == "move"]
    moves = [e for e in events if e.kind == "move"]
    require(moves == original_moves, "frame", "complete ordered MOVE stream")
    profile = Counter(e.rank for e in events if e.kind in ("move", "copy"))
    require(dict(profile) == PROFILE, "charge", "complete paid rank profile")
    old = [replay(word, original, ranks, reverse) for reverse in (False, True)]
    new = [replay(word, events, ranks, reverse) for reverse in (False, True)]
    _, deferred, transformed, _ = split_and_scatter(word, witness)
    base_counts = [sum(j in row for row in transformed) for j in range(9)]
    counts = list(base_counts)
    counts[witness["column"]] = len(witness["taps"])
    scatter = sum(counts)
    require(scatter == witness["expected_scatter_adds"], "bill", "scatter ADD invoice")
    require(new[0]["adds"] == new[1]["adds"] == witness["expected_total_adds"],
            "bill", "full ADD invoice")
    require(new[0]["adds"] == old[0]["adds"] - sum(map(len, word["scatter"])) + scatter,
            "bill", "every displaced undo remains charged")
    forward, backward = new[0]["majorant"], new[1]["majorant"]
    local, nine = 64 * forward ** 3 * backward ** 2, (1 << 18) * forward ** 5 * backward ** 4
    require(local < 1 << 104 and nine < 1 << 192, "precision", "inherited positive-majorant guards")
    return {
        "status": "PASS_INDEPENDENT_SINGLE_COPY_INTERLEAVING",
        "word_columns": 661, "orientations": 2, "deferred_undo_adds": len(deferred),
        "cut_zero_counts": base_counts, "witness_counts": counts,
        "scatter_adds": scatter, "full_adds": new[0]["adds"],
        "copy_ranks": [e.rank for e in events if e.kind == "copy"],
        "paid_profile": dict(sorted(profile.items())),
        "paid_rank_mass": sum(k * v for k, v in profile.items()),
        "majorants": [forward, backward], "guard_bits": [local.bit_length(), nine.bit_length()],
        "ordered_moves": len(moves), "controls": controls(word, witness, events, ranks),
        "optimality_claim": False, "new_kappa_claim": False,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--witness", type=Path, default=HERE / "WITNESS.json")
    parser.add_argument("--source", type=Path, default=SOURCE)
    arguments = parser.parse_args()
    print(json.dumps(audit(arguments.witness, arguments.source), sort_keys=True))
