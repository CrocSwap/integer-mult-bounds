#!/usr/bin/env python3
"""Three or more moved corrections on length-5 G20 intervals.

The A2 identity, the constructor and the one-edge emitter are the #5708
contract, as restated by PR #6664 and reimplemented by PR #6963. This file
reimplements that emitter. It imports no predecessor verifier.

Domain: every A2 interval of the emitted #5708 word with exactly five
contacts, every set of three, four or five of its corrections, and every way
to place those corrections on route-table frames other than their contact
frames. The corrections that are not chosen stay on their contact frames.
Moved frames may coincide.

The emitter stops at the first missing route. Every such assignment has a
unique pair of earliest moved corrections. The word agrees with the two-move
word on that pair up through the record where that two-move word is rejected,
and that record is strictly before every later correction. Later frame choices
are therefore not read. The two-move classification is recomputed here; the
4,331 tail words are the only ones that enter the suffix, and each of them
misses an edge before the next correction. No assignment emits, so none lowers
the paid-query moment on (0, 1).
"""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASE_PAID = {1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10}
KAPPA = "781451/250000000"
ROUTES = 2369
FRAMES = 636
ALTERNATES = FRAMES - 1
INTERVALS = 133
PAIRS = 1330
TWO_MOVE_ASSIGNMENTS = INTERVALS * 10 * ALTERNATES * ALTERNATES
# PR #6963's two-move partition. Recomputed below and required to match.
EXPECTED_TWO_MOVE = {
    "pairs": PAIRS,
    "assignments": TWO_MOVE_ASSIGNMENTS,
    "prefix_fail": 86290150,
    "first_meet": 332300580,
    "first_hosts": 53012,
    "middle_fail": 116497735,
    "second_meet": 1196454,
    "full_replays": 4331,
    "tail_missing": 4331,
}
FIRST_INTERVAL = (1119, 8918)
FIRST_TWO_MOVE = {
    "pairs": 10,
    "assignments": 10 * ALTERNATES * ALTERNATES,
    "prefix_fail": 2419350,
    "first_meet": 1612900,
    "first_hosts": 0,
    "middle_fail": 0,
    "second_meet": 0,
    "full_replays": 0,
    "tail_missing": 0,
}
# Extensions of one two-move frame pair by every nonempty later-frame choice.
# A later correction has FRAMES choices (its contact frame, or one of the
# ALTERNATES others). The all-contact choice is the two-move word itself.
EXT_WEIGHT = {j: FRAMES ** (4 - j) - 1 for j in range(1, 5)}
TAIL_BY_J = {1: 4305, 2: 7, 3: 19, 4: 0}
TAIL_EXT = {1: 1107501953775, 2: 2831465, 3: 12065, 4: 0}
EARLY_EXT = {1: 13795440515782100, 2: 43385261204285, 3: 102163090060, 4: 0}
ASSIGNMENTS = 13840035444873750
PER_INTERVAL = ASSIGNMENTS // INTERVALS
LENGTHS = {
    0: 2, 1: 184, 2: 331, 3: 250, 4: 119, 5: 133, 6: 86, 7: 79, 8: 124,
    9: 95, 10: 129, 11: 100, 12: 151, 13: 69, 14: 102, 15: 47, 16: 73,
    17: 47, 18: 48, 19: 29, 20: 23, 21: 9, 22: 9, 23: 8, 24: 3, 25: 2,
    26: 4, 27: 4, 28: 1, 29: 2, 30: 2, 31: 3, 33: 2,
}
ONE_MOVE = (7337, 10919, 2, 123, ((2, 3), (4, -1)))
EARLY = ("prefix_fail", "first_meet", "middle_fail", "second_meet")


def need(ok, message):
    if not ok:
        raise ValueError(message)


def domain_by_masks(intervals=1):
    """Direct count: every subset of at least three corrections, 635 frames each."""
    total = 0
    sets = 0
    for mask in range(1 << 5):
        moved = bin(mask).count("1")
        if moved >= 3:
            sets += 1
            total += ALTERNATES ** moved
    return sets, total * intervals


def domain_by_earliest(intervals=1):
    """The same count grouped by the two earliest moved indexes."""
    total = 0
    for i in range(5):
        for j in range(i + 1, 5):
            total += ALTERNATES * ALTERNATES * EXT_WEIGHT[j]
    return total * intervals


def load_pinned():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    blobs = {}
    for row in sources["files"]:
        if row["usage"] != "input":
            continue
        data = (ROOT / row["path"]).read_bytes()
        need(sha256(data).hexdigest() == row["sha256"], "input hash mismatch " + row["path"])
        blobs[row["path"]] = data
    source = blobs["research/g20-conjugation-admission/construct.py"].decode()
    need("out.extend([e[:3] + [f], extra[:3] + [f]])" in source,
         "constructor no longer puts the contact and correction on one chosen frame")
    word = json.loads(gzip.decompress(blobs["research/g20-conjugation-admission/WORD.json.gz"]))
    paths = json.loads(blobs["research/g20-conjugation-admission/PATHS.json"])
    local = json.loads(blobs["research/g20-conjugation-admission/LOCAL-RESULT.json"])
    selected = json.loads(blobs["certificates/selected-result.json"])
    return word, paths, local, selected


def load_edges(paths):
    edges = {}
    frames = set()
    for key, value in paths.items():
        left, right = key.split(":")
        need(len(value) == 1, "route " + key + " is not one edge")
        start, end, rank = value[0]
        need(start == int(left) and end == int(right), "route endpoints disagree with " + key)
        need(type(rank) is int and 1 <= rank <= 7, "route rank outside 1..7")
        edges[(start, end)] = rank
        frames.update((start, end))
    need(len(edges) == ROUTES, "route count changed")
    need(len(frames) == FRAMES, "frame count changed")
    return edges, sorted(frames)


def expected_rows(width, owned):
    rows = []
    for index in range(width):
        if index in owned:
            rows.append(0)
            continue
        row = 1 << index
        if 111 <= index < 222:
            row ^= 1 << (index - 111)
        rows.append(row)
    return rows


def endpoint_ok(records, width, owned, expected):
    rows = [1 << index for index in range(width)]
    for event in records:
        op, dest = event[0], event[1]
        if op == "ADD":
            rows[dest] ^= rows[event[2]]
        elif op == "ERASE":
            if dest not in owned:
                return False
            rows[dest] = 0
        elif op == "INIT":
            if dest not in owned or rows[dest]:
                return False
        else:
            return False
    return rows == expected


class Machine:
    """The one-edge emitter: rows, wire frames and the paid histogram."""

    def __init__(self, rows, state, paid, edges, owned):
        self.rows, self.state, self.paid = rows, state, paid
        self.edges, self.owned = edges, owned

    def copy(self):
        return Machine(self.rows[:], self.state[:], Counter(self.paid), self.edges, self.owned)

    def step(self, event):
        """Apply one record; return None or a rejection reason."""
        op, dest = event[0], event[1]
        rows, state = self.rows, self.state
        if op in ("ERASE", "INIT"):
            if dest not in self.owned or (op == "INIT" and rows[dest]):
                return "owned_op"
            rows[dest] = 0
            state[dest] = event[2]
            return None
        if op != "ADD":
            return "opcode"
        source, frame = event[2], event[3]
        if not rows[source]:
            return None
        for wire in (dest, source):
            origin = state[wire]
            if origin == frame:
                continue
            rank = self.edges.get((origin, frame))
            if rank is None:
                return "missing_edge"
            if rows[wire]:
                self.paid[rank] += 1
            state[wire] = frame
        rows[dest] ^= rows[source]
        return None

    def run(self, records):
        for event in records:
            reason = self.step(event)
            if reason is not None:
                return reason
        return None

    def finish(self, final):
        rows, state = self.rows, self.state
        for dest, frame in enumerate(final):
            if dest in self.owned:
                if rows[dest]:
                    return "owned_live"
                state[dest] = frame
                continue
            origin = state[dest]
            if origin == frame:
                continue
            rank = self.edges.get((origin, frame))
            if rank is None:
                return "missing_edge"
            if rows[dest]:
                self.paid[rank] += 1
            state[dest] = frame
        return None if state == final else "final_state"


def fresh(width, start, edges, owned):
    return Machine([1 << index for index in range(width)], start[:], Counter(), edges, owned)


def first_failure(records, width, start, final, edges, owned):
    """Return (reason, index) for the first rejection, or (None, None) on emission.

    A rejection inside finish() is reported at index len(records), after every
    record. The paid histogram is not meaningful on a rejection.
    """
    machine = fresh(width, start, edges, owned)
    for index, event in enumerate(records):
        reason = machine.step(event)
        if reason is not None:
            return reason, index
    reason = machine.finish(final)
    if reason is not None:
        return reason, len(records)
    return None, None


def correction(event, gate_dest, gate_source):
    dest, source = event[1], event[2]
    if dest == gate_source and source != gate_dest:
        return ["ADD", gate_dest, source]
    if source == gate_dest and dest != gate_source:
        return ["ADD", dest, gate_source]
    return None


def scan_intervals(scalars, lengths, cap):
    groups = defaultdict(list)
    for index, event in enumerate(scalars):
        if event[0] == "ADD":
            groups[(event[1], event[2])].append(index)
    found = []
    for (gate_dest, gate_source), positions in groups.items():
        for left_at, left in enumerate(positions):
            for right in positions[left_at + 1:]:
                changes = []
                rejected = False
                for index in range(left + 1, right):
                    event = scalars[index]
                    if event[0] in ("ERASE", "INIT") and event[1] in (gate_dest, gate_source):
                        rejected = True
                        break
                    if event[0] == "ADD" and (event[1] == gate_source or event[2] == gate_dest):
                        extra = correction(event, gate_dest, gate_source)
                        if extra is None or len(changes) == cap:
                            rejected = True
                            break
                        changes.append((index, extra, event[3]))
                if rejected or len(changes) not in lengths:
                    continue
                found.append((left, right, changes, gate_dest, gate_source))
    return sorted(found, key=lambda item: (item[0], item[1], item[3], item[4]))


def length_histogram(scalars):
    groups = defaultdict(list)
    for index, event in enumerate(scalars):
        if event[0] == "ADD":
            groups[(event[1], event[2])].append(index)
    counts = Counter()
    capped = 0
    cap = 64
    for (gate_dest, gate_source), positions in groups.items():
        for left_at, left in enumerate(positions):
            for right in positions[left_at + 1:]:
                changes = 0
                rejected = False
                for index in range(left + 1, right):
                    event = scalars[index]
                    if event[0] in ("ERASE", "INIT") and event[1] in (gate_dest, gate_source):
                        rejected = True
                        break
                    if event[0] == "ADD" and (event[1] == gate_source or event[2] == gate_dest):
                        extra = correction(event, gate_dest, gate_source)
                        if extra is None or changes == cap:
                            if extra is not None and changes == cap:
                                capped += 1
                            rejected = True
                            break
                        changes += 1
                if not rejected:
                    counts[changes] += 1
    return counts, capped


def skeleton(scalars, left, right, changes, override):
    replaced = {index: (extra, override.get(number, frame0))
                for number, (index, extra, frame0) in enumerate(changes)}
    out, contacts = [], []
    for index, event in enumerate(scalars):
        if index in (left, right):
            continue
        if index in replaced:
            extra, frame = replaced[index]
            contacts.append(len(out))
            out.append(event[:3] + [frame])
            out.append(extra + [frame])
        else:
            out.append(event)
    return out, contacts


def delta_of(paid, base):
    ranks = set(paid) | set(base)
    return tuple(sorted(
        (rank, paid[rank] - base[rank]) for rank in ranks if paid[rank] != base[rank]))


def clean(counter):
    return Counter({rank: count for rank, count in counter.items() if count})


def strict_loss(delta):
    """Positive by nonnegative terms or by repeated strict rank splits."""
    pos, neg = Counter(), Counter()
    for rank, count in delta:
        if count > 0:
            pos[rank] += count
        elif count < 0:
            neg[rank] += -count
    used_split = False
    while True:
        pos, neg = clean(pos), clean(neg)
        if not neg:
            return bool(pos) or used_split
        rank = min(neg)
        items = []
        for part, count in pos.items():
            items.extend([part] * count)
        if len(items) > 14:
            return False
        found = None
        for mask in range(1, 1 << len(items)):
            bits = [items[i] for i in range(len(items)) if mask >> i & 1]
            if len(bits) >= 2 and sum(bits) == rank:
                found = bits
                break
        if found is None:
            return False
        for part in found:
            pos[part] -= 1
        neg[rank] -= 1
        used_split = True


def moved(record, frame):
    return record[:3] + [frame]


def remember(bucket, sample, limit=25):
    if len(bucket) < limit:
        bucket.append(sample)


def walk(machine, records, base_index):
    for offset, event in enumerate(records):
        reason = machine.step(event)
        if reason is not None:
            return reason, base_index + offset
    return None, None


def census(scalars, edges, frames, width, owned, start, final, expected):
    """Classify every two-move pair, and weigh every three-or-more extension."""
    frame_set = set(frames)
    items = scan_intervals(scalars, frozenset((5,)), 5)
    need(len(items) == INTERVALS, "length-5 interval count changed")
    need(len({(item[0], item[1]) for item in items}) == INTERVALS, "length-5 gates are not unique")
    need(min((item[0], item[1]) for item in items) == FIRST_INTERVAL,
         "the first length-5 interval moved")
    counts = Counter()
    first = Counter()
    samples = defaultdict(list)
    tails = []
    early_ext = Counter({j: 0 for j in range(1, 5)})
    tail_ext = Counter({j: 0 for j in range(1, 5)})
    tails_j = Counter({j: 0 for j in range(1, 5)})
    first_ext = 0
    gaps = Counter()
    for left, right, changes, gate_dest, gate_source in items:
        track = (left, right) == FIRST_INTERVAL
        need(len(changes) == 5, "a length-5 interval has another contact count")
        if track:
            need(scalars[left] == ["ADD", 572, 22, 1], "first left gate changed")
            need(scalars[right] == ["ADD", 572, 22, 24], "first right gate changed")
            need((gate_dest, gate_source) == (572, 22), "first gate operands changed")
        fixed, contacts = skeleton(scalars, left, right, changes, {})
        need(len(contacts) == 5, "skeleton dropped a contact")
        for index in range(4):
            need(contacts[index + 1] >= contacts[index] + 2, "corrections are not separated")
        need(endpoint_ok(fixed, width, owned, expected), "contact-frame endpoint failed")
        others = []
        for change in changes:
            need(change[2] in frame_set, "contact frame is outside the route table")
            alts = [frame for frame in frames if frame != change[2]]
            need(len(alts) == ALTERNATES, "alternate-frame count changed")
            others.append(alts)
        two_word, _ = skeleton(scalars, left, right, changes, {0: others[0][0], 1: others[1][0]})
        three_word, _ = skeleton(
            scalars, left, right, changes,
            {0: others[0][0], 1: others[1][0], 2: others[2][0]})
        need(endpoint_ok(two_word, width, owned, expected), "two-move endpoint failed")
        need(endpoint_ok(three_word, width, owned, expected), "three-move endpoint failed")
        snaps = []
        machine = fresh(width, start, edges, owned)
        cursor = 0
        alive = True
        for position in contacts:
            if alive:
                reason = machine.run(fixed[cursor:position])
                if reason is not None:
                    need(reason == "missing_edge", "prefix failed as " + reason)
                    alive = False
            snaps.append(machine.copy() if alive else None)
            cursor = position

        def charge(kind, j, n):
            nonlocal first_ext
            counts[kind] += n
            weight = n * EXT_WEIGHT[j]
            if track:
                first[kind] += n
                first_ext += weight
            if kind == "tail_missing":
                tail_ext[j] += weight
                tails_j[j] += n
            else:
                early_ext[j] += weight

        for i in range(5):
            for j in range(i + 1, 5):
                block = ALTERNATES * ALTERNATES
                counts["pairs"] += 1
                counts["assignments"] += block
                if track:
                    first["pairs"] += 1
                    first["assignments"] += block
            if snaps[i] is None:
                for j in range(i + 1, 5):
                    charge("prefix_fail", j, ALTERNATES * ALTERNATES)
                    if j < 4:
                        remember(samples["prefix_fail"],
                                 (left, right, i, j, others[i][0], others[j][0]))
                continue
            for f_i in others[i]:
                at = snaps[i].copy()
                c_i = contacts[i]
                meet = at.run([moved(fixed[c_i], f_i), moved(fixed[c_i + 1], f_i)])
                if meet is not None:
                    need(meet == "missing_edge", "first meeting failed as " + meet)
                    for j in range(i + 1, 5):
                        charge("first_meet", j, ALTERNATES)
                        if j < 4:
                            remember(samples["first_meet"], (left, right, i, j, f_i, others[j][0]))
                    continue
                counts["first_hosts"] += 1
                if track:
                    first["first_hosts"] += 1
                cursor = c_i + 2
                for j in range(i + 1, 5):
                    c_j = contacts[j]
                    reason = None
                    if at is not None:
                        reason = at.run(fixed[cursor:c_j])
                    if at is None or reason is not None:
                        if reason is not None:
                            need(reason == "missing_edge", "middle failed as " + reason)
                        at = None
                        charge("middle_fail", j, ALTERNATES)
                        if j < 4:
                            remember(samples["middle_fail"],
                                     (left, right, i, j, f_i, others[j][0]))
                        continue
                    for f_j in others[j]:
                        tail = at.copy()
                        pair = [moved(fixed[c_j], f_j), moved(fixed[c_j + 1], f_j)]
                        pair_reason = tail.run(pair)
                        if pair_reason is not None:
                            need(pair_reason == "missing_edge",
                                 "second meeting failed as " + pair_reason)
                            charge("second_meet", j, 1)
                            if j < 4:
                                remember(samples["second_meet"], (left, right, i, j, f_i, f_j))
                            continue
                        counts["full_replays"] += 1
                        if track:
                            first["full_replays"] += 1
                        suffix_reason, fail_at = walk(tail, fixed[c_j + 2:], c_j + 2)
                        if suffix_reason is None:
                            suffix_reason = tail.finish(final)
                            fail_at = len(fixed)
                        need(suffix_reason == "missing_edge",
                             "tail failed as " + str(suffix_reason))
                        need(j < 4, "a length-5 tail has no correction after index 4")
                        next_contact = contacts[j + 1]
                        need(c_j + 2 <= fail_at < next_contact,
                             "tail rejection is not strictly before the next correction")
                        gaps[next_contact - fail_at] += 1
                        charge("tail_missing", j, 1)
                        tails.append((left, right, i, j, f_i, f_j, fail_at, next_contact))
                    if at is not None:
                        advance = at.run(fixed[c_j:c_j + 2])
                        if advance is not None:
                            need(advance == "missing_edge",
                                 "contact-frame bridge failed as " + advance)
                            at = None
                    cursor = c_j + 2
    return items, counts, first, samples, tails, early_ext, tail_ext, tails_j, first_ext, gaps


def one_move_control(scalars, items, edges, width, owned, start, final, base, expected):
    """Replay the published length-5 one-move emission. One assignment, not in this domain."""
    left, right, index, frame, shape = ONE_MOVE
    matches = [item for item in items if item[0] == left and item[1] == right]
    need(len(matches) == 1, "the length-5 one-move witness interval is missing")
    _left, _right, changes, gate_dest, gate_source = matches[0]
    need((gate_dest, gate_source) == (349, 340), "witness gate operands changed")
    need(scalars[left][:3] == ["ADD", 349, 340] and scalars[right][:3] == ["ADD", 349, 340],
         "witness outer gates changed")
    contact_at, extra, contact_frame = changes[index]
    need(contact_at == 7343, "witness contact index changed")
    need(scalars[contact_at][:3] == ["ADD", 340, 670], "witness contact changed")
    need(extra == ["ADD", 349, 670] and contact_frame == 506, "witness correction changed")
    need(frame != contact_frame, "the control frame is the contact frame")
    words, _contacts = skeleton(scalars, left, right, changes, {index: frame})
    need(endpoint_ok(words, width, owned, expected), "one-move control misses its endpoint")
    machine = fresh(width, start, edges, owned)
    need(machine.run(words) is None and machine.finish(final) is None,
         "published length-5 one-move witness no longer emits")
    need(delta_of(machine.paid, base) == shape, "published length-5 one-move shape changed")
    need(strict_loss(shape), "published length-5 one-move shape is not a strict loss")


def cold_controls(scalars, items, samples, tails, frames, width, start, final, edges, owned):
    """From-scratch replays of every tail and of 25 early extensions per class."""
    by_key = {(left, right): changes for left, right, changes, _gate_dest, _gate_source in items}
    alts_of = {}
    checked_early = 0
    for kind in EARLY:
        need(len(samples[kind]) == 25, kind + " sample count changed")
        for left, right, i, j, f_i, f_j in samples[kind]:
            changes = by_key[(left, right)]
            if (left, right) not in alts_of:
                alts_of[(left, right)] = [
                    [frame for frame in frames if frame != change[2]] for change in changes]
            alts = alts_of[(left, right)]
            two, contacts = skeleton(scalars, left, right, changes, {i: f_i, j: f_j})
            three, again = skeleton(
                scalars, left, right, changes,
                {i: f_i, j: f_j, j + 1: alts[j + 1][0]})
            need(contacts == again, "a third move shifted later record positions")
            two_reason, two_at = first_failure(two, width, start, final, edges, owned)
            three_reason, three_at = first_failure(three, width, start, final, edges, owned)
            need(two_reason == "missing_edge" and three_reason == "missing_edge",
                 kind + " extension emitted or failed as " + str(three_reason))
            need(two_at == three_at < contacts[j + 1],
                 kind + " extension changed the rejecting record")
            checked_early += 1
    need(len(tails) == EXPECTED_TWO_MOVE["tail_missing"], "tail list does not match the census")
    maximal = set()
    for left, right, i, j, f_i, f_j, fail_at, next_contact in tails:
        changes = by_key[(left, right)]
        if (left, right) not in alts_of:
            alts_of[(left, right)] = [
                [frame for frame in frames if frame != change[2]] for change in changes]
        alts = alts_of[(left, right)]
        two, contacts = skeleton(scalars, left, right, changes, {i: f_i, j: f_j})
        third = {i: f_i, j: f_j, j + 1: alts[j + 1][0]}
        three, again = skeleton(scalars, left, right, changes, third)
        need(contacts == again and contacts[j + 1] == next_contact,
             "tail skeleton disagreed with the census")
        two_reason, two_at = first_failure(two, width, start, final, edges, owned)
        three_reason, three_at = first_failure(three, width, start, final, edges, owned)
        need(two_reason == "missing_edge" and two_at == fail_at,
             "cold two-move tail disagrees with the resumed census")
        need(three_reason == "missing_edge" and three_at == fail_at < next_contact,
             "moving the next correction changed the rejecting record")
        if j not in maximal:
            maximal.add(j)
            every = {i: f_i, j: f_j}
            every.update({k: alts[k][0] for k in range(j + 1, 5)})
            full, full_contacts = skeleton(scalars, left, right, changes, every)
            need(full_contacts == contacts, "moving every later correction shifted positions")
            full_reason, full_at = first_failure(full, width, start, final, edges, owned)
            need(full_reason == "missing_edge" and full_at == fail_at,
                 "moving every later correction changed the rejecting record")
    need(maximal == {1, 2, 3}, "a tail index with a later correction was not cold-checked")
    return checked_early, len(tails), len(maximal)


def main():
    sets, masked = domain_by_masks()
    need(sets == 16, "a length-5 interval does not have 16 subsets of size at least 3")
    need(masked == PER_INTERVAL, "mask count disagrees with the recorded per-interval total")
    need(domain_by_earliest() == PER_INTERVAL,
         "earliest-pair grouping disagrees with the mask count")
    need(sum(TAIL_EXT.values()) + sum(EARLY_EXT.values()) == ASSIGNMENTS,
         "recorded extension classes do not partition the domain")
    need(ASSIGNMENTS == INTERVALS * PER_INTERVAL, "interval total does not match")
    for j, count in TAIL_BY_J.items():
        need(count * EXT_WEIGHT[j] == TAIL_EXT[j], "tail extension weight changed at j=" + str(j))
    word, paths, local, selected = load_pinned()
    need(selected["kappa"] == KAPPA, "selected kappa changed")
    published = {int(rank): count for rank, count in local["stats"]["paid"].items()}
    need(published == BASE_PAID, "LOCAL-RESULT paid histogram drifted")
    edges, frames = load_edges(paths)
    scalars = [event[:] for event in word["records"] if event[0] not in ("Q", "ZERO_Q")]
    width = len(word["start"])
    need(len(scalars) == 11930 and width == 685, "scalar program shape changed")
    owned = set(word["owned"])
    start, final = word["start"][:], word["final"][:]
    expected = expected_rows(width, owned)
    need(endpoint_ok(scalars, width, owned, expected), "published word misses its scalar endpoint")
    base_machine = fresh(width, start, edges, owned)
    need(base_machine.run(scalars) is None and base_machine.finish(final) is None,
         "published word does not emit")
    base = base_machine.paid
    need(dict(base) == BASE_PAID, "published word does not emit its histogram")
    histogram, capped = length_histogram(scalars)
    need(capped == 0, "the length scan hit its cap")
    need(dict(histogram) == LENGTHS, "A2 length histogram changed " + str(dict(histogram)))
    need(sum(count for length, count in histogram.items() if length >= 5) == 1384,
         "length-at-least-5 interval total changed")
    need(histogram[2] == 331 and histogram[3] == 250 and histogram[4] == 119,
         "short-interval control disagrees with PR6664")
    need(histogram[6] == 86, "length-6 interval count changed")
    items, counts, first, samples, tails, early_ext, tail_ext, tails_j, first_ext, gaps = census(
        scalars, edges, frames, width, owned, start, final, expected)
    need(dict(counts) == EXPECTED_TWO_MOVE, "two-move census changed " + str(dict(counts)))
    need({key: first[key] for key in FIRST_TWO_MOVE} == FIRST_TWO_MOVE,
         "first-interval two-move census changed " + str(dict(first)))
    need(sum(counts[kind] for kind in EARLY) + counts["tail_missing"] == counts["assignments"],
         "two-move classes do not partition the pairs")
    need(dict(tails_j) == TAIL_BY_J, "tail index distribution changed " + str(dict(tails_j)))
    need(dict(early_ext) == EARLY_EXT, "early extension weights changed " + str(dict(early_ext)))
    need(dict(tail_ext) == TAIL_EXT, "tail extension weights changed " + str(dict(tail_ext)))
    need(sum(early_ext.values()) + sum(tail_ext.values()) == ASSIGNMENTS,
         "extensions do not partition the three-or-more domain")
    need(first_ext == PER_INTERVAL and first["tail_missing"] == 0,
         "the first length-5 interval is not an all-early three-move block")
    need(dict(gaps) and min(gaps) == 2 and max(gaps) == 329,
         "tail gap before the next correction changed " + str(dict(gaps)))
    need(tails[0] == (5673, 7030, 1, 2, 594, 353, 6306, 6547),
         "the first tail word changed " + str(tails[0]))
    one_move_control(scalars, items, edges, width, owned, start, final, base, expected)
    early_n, tail_n, maximal_n = cold_controls(
        scalars, items, samples, tails, frames, width, start, final, edges, owned)
    need(early_n == 100 and tail_n == 4331 and maximal_n == 3, "cold-replay count changed")
    need(strict_loss(((1, 2), (2, -1))) and not strict_loss(((1, 1), (2, -2), (3, 1))),
         "strict-loss classifier control failed")
    left, right, i, j, f_i, f_j, fail_at, next_contact = tails[0]
    print(
        "PASS_G20_LENGTH5_THREE_MOVE"
        " intervals=133 assignments={assignments}"
        " early_extensions={early} tail_extensions={tail}"
        " tails=4331 tail_j1=4305 tail_j2=7 tail_j3=19"
        " min_gap={min_gap} max_gap={max_gap}"
        " emitted=0 savings=0"
        " first_interval=1119-8918/{per_interval}/0"
        " first_tail={left}-{right}/{i}/{j}/{f_i}/{f_j}/{fail_at}/{next_contact}"
        " cold_early=100 cold_tails=4331 cold_maximal=3"
        " one_move_control=3H2-H4"
        " length6_open=86 no_new_kappa=true".format(
            assignments=ASSIGNMENTS,
            early=sum(early_ext.values()),
            tail=sum(tail_ext.values()),
            min_gap=min(gaps),
            max_gap=max(gaps),
            per_interval=PER_INTERVAL,
            left=left, right=right, i=i, j=j, f_i=f_i, f_j=f_j,
            fail_at=fail_at, next_contact=next_contact))


if __name__ == "__main__":
    main()
