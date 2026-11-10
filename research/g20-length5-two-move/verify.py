#!/usr/bin/env python3
"""Length-5 G20 conjugations with two corrections moved off their contact frames.

The A2 identity, the constructor and the one-edge emitter are the #5708
contract, as restated by PR #6664. This file reimplements that emitter. It
imports no predecessor verifier.

Domain: every A2 interval of the emitted #5708 word with exactly 5 contacts,
every pair i < j of its corrections, and every pair of frames (f_i, f_j) of
the route table with f_i different from contact i's frame and f_j different
from contact j's frame. The other three corrections stay on their contact
frames. f_i may equal f_j.

Every assignment is classified by an exact prefix replay:

  prefix_fail  the shared prefix up to contact i misses a route;
  first_meet   the moved pair (contact i, correction i) at f_i misses a route;
  middle_fail  the records between correction i and contact j miss a route;
  second_meet  the moved pair (contact j, correction j) at f_j misses a route;
  tail_missing the full replay misses a later route;
  neutral / loss / saving  the full replay emits with that paid change
               (no assignment reaches these classes).

The first four classes depend only on a prefix of the rewritten word, and the
emitter rejects at the first missing route, so each is a rejection of the full
word. The 4,331 tail words are rebuilt and emitted from scratch. Twenty-five
words from each earlier class are rebuilt the same way. One published
length-5 one-move emission is replayed as a positive control that this emitter
can see a paid-histogram change. That control is one assignment, not the
one-move census.
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
ASSIGNMENTS = INTERVALS * 10 * ALTERNATES * ALTERNATES
EXPECTED_COUNTS = {
    "pairs": PAIRS,
    "assignments": ASSIGNMENTS,
    "prefix_fail": 86290150,
    "first_meet": 332300580,
    "first_hosts": 53012,
    "middle_fail": 116497735,
    "second_meet": 1196454,
    "full_replays": 4331,
    "tail_missing": 4331,
}
FIRST_INTERVAL = (1119, 8918)
FIRST_COUNTS = {
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
# Lengths 2..4 are PR #6664's interval totals. The length-at-least-5 total is
# PR #6923's 1,384. Length 5 is the domain censused here.
LENGTHS = {
    0: 2, 1: 184, 2: 331, 3: 250, 4: 119, 5: 133, 6: 86, 7: 79, 8: 124,
    9: 95, 10: 129, 11: 100, 12: 151, 13: 69, 14: 102, 15: 47, 16: 73,
    17: 47, 18: 48, 19: 29, 20: 23, 21: 9, 22: 9, 23: 8, 24: 3, 25: 2,
    26: 4, 27: 4, 28: 1, 29: 2, 30: 2, 31: 3, 33: 2,
}
ONE_MOVE = (7337, 10919, 2, 123, ((2, 3), (4, -1)))
REJECTION = ("prefix_fail", "first_meet", "middle_fail", "second_meet", "tail_missing")


def need(ok, message):
    if not ok:
        raise ValueError(message)


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


def emit(records, width, start, final, edges, owned):
    machine = fresh(width, start, edges, owned)
    reason = machine.run(records) or machine.finish(final)
    return reason, (None if reason else machine.paid)


def correction(event, gate_dest, gate_source):
    dest, source = event[1], event[2]
    if dest == gate_source and source != gate_dest:
        return ["ADD", gate_dest, source]
    if source == gate_dest and dest != gate_source:
        return ["ADD", dest, gate_source]
    return None


def scan_intervals(scalars, lengths, cap):
    """Every A2 interval whose contact count is in `lengths`.

    An interval that grows past `cap` contacts is rejected and counted in the
    cap total. Callers that want the true length histogram pass a cap above
    every interval the word contains.
    """
    groups = defaultdict(list)
    for index, event in enumerate(scalars):
        if event[0] == "ADD":
            groups[(event[1], event[2])].append(index)
    found = []
    capped = 0
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
                            if extra is not None and len(changes) == cap:
                                capped += 1
                            rejected = True
                            break
                        changes.append((index, extra, event[3]))
                if rejected or len(changes) not in lengths:
                    continue
                found.append((left, right, changes, gate_dest, gate_source))
    return sorted(found, key=lambda item: (item[0], item[1], item[3], item[4])), capped


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
    """The rewritten word plus the skeleton position of each contact."""
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


def census(scalars, edges, frames, width, owned, start, final, base, expected):
    """Resume each assignment from cached prefix states of the same word."""
    frame_set = set(frames)
    items = scan_intervals(scalars, frozenset((5,)), 5)[0]
    need(len(items) == INTERVALS, "length-5 interval count changed")
    need(len({(item[0], item[1]) for item in items}) == INTERVALS, "length-5 gates are not unique")
    need(min((item[0], item[1]) for item in items) == FIRST_INTERVAL,
         "the first length-5 interval moved")
    counts = Counter()
    first = Counter()
    samples = defaultdict(list)
    tails = []
    emitted = []
    for left, right, changes, gate_dest, gate_source in items:
        track = (left, right) == FIRST_INTERVAL
        need(len(changes) == 5, "a length-5 interval has another contact count")
        if track:
            need(scalars[left] == ["ADD", 572, 22, 1], "first left gate changed")
            need(scalars[right] == ["ADD", 572, 22, 24], "first right gate changed")
            need((gate_dest, gate_source) == (572, 22), "first gate operands changed")
        fixed, contacts = skeleton(scalars, left, right, changes, {})
        need(endpoint_ok(fixed, width, owned, expected), "contact-frame endpoint failed")
        others = []
        for change in changes:
            need(change[2] in frame_set, "contact frame is outside the route table")
            alts = [frame for frame in frames if frame != change[2]]
            need(len(alts) == ALTERNATES, "alternate-frame count changed")
            others.append(alts)
        alternate = {0: others[0][0], 1: others[1][0]}
        moved_word, _ = skeleton(scalars, left, right, changes, alternate)
        need(endpoint_ok(moved_word, width, owned, expected), "two-move endpoint failed")
        snaps = []
        machine = fresh(width, start, edges, owned)
        cursor = 0
        alive = True
        for position in contacts:
            if alive and machine.run(fixed[cursor:position]) is not None:
                alive = False
            snaps.append(machine.copy() if alive else None)
            cursor = position
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
                    counts["prefix_fail"] += ALTERNATES * ALTERNATES
                    if track:
                        first["prefix_fail"] += ALTERNATES * ALTERNATES
                    remember(samples["prefix_fail"],
                             (left, right, i, j, others[i][0], others[j][0]))
                continue
            for f_i in others[i]:
                at = snaps[i].copy()
                c_i = contacts[i]
                if at.run([moved(fixed[c_i], f_i), moved(fixed[c_i + 1], f_i)]) is not None:
                    for j in range(i + 1, 5):
                        counts["first_meet"] += ALTERNATES
                        if track:
                            first["first_meet"] += ALTERNATES
                        remember(samples["first_meet"], (left, right, i, j, f_i, others[j][0]))
                    continue
                counts["first_hosts"] += 1
                if track:
                    first["first_hosts"] += 1
                cursor = c_i + 2
                for j in range(i + 1, 5):
                    c_j = contacts[j]
                    if at is None or at.run(fixed[cursor:c_j]) is not None:
                        at = None
                        counts["middle_fail"] += ALTERNATES
                        if track:
                            first["middle_fail"] += ALTERNATES
                        remember(samples["middle_fail"],
                                 (left, right, i, j, f_i, others[j][0]))
                        continue
                    for f_j in others[j]:
                        tail = at.copy()
                        pair = [moved(fixed[c_j], f_j), moved(fixed[c_j + 1], f_j)]
                        if tail.run(pair) is not None:
                            counts["second_meet"] += 1
                            if track:
                                first["second_meet"] += 1
                            remember(samples["second_meet"], (left, right, i, j, f_i, f_j))
                            continue
                        counts["full_replays"] += 1
                        if track:
                            first["full_replays"] += 1
                        reason = tail.run(fixed[c_j + 2:]) or tail.finish(final)
                        if reason is not None:
                            need(reason == "missing_edge", "moved word failed as " + reason)
                            counts["tail_missing"] += 1
                            if track:
                                first["tail_missing"] += 1
                            tails.append((left, right, i, j, f_i, f_j))
                            continue
                        delta = delta_of(tail.paid, base)
                        emitted.append((left, right, i, j, f_i, f_j, delta))
                    if at.run(fixed[c_j:c_j + 2]) is not None:
                        at = None
                    cursor = c_j + 2
    return items, counts, first, samples, tails, emitted


def one_move_control(scalars, items, edges, width, owned, start, final, base, expected):
    """Replay the published length-5 one-move emission. One assignment only."""
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
    reason, paid = emit(words, width, start, final, edges, owned)
    need(reason is None, "published length-5 one-move witness no longer emits")
    need(delta_of(paid, base) == shape, "published length-5 one-move shape changed")
    need(strict_loss(shape), "published length-5 one-move shape is not a strict loss")


def control_samples(scalars, items, samples, tails, width, start, final, edges, owned):
    """Cold replays: 25 words from each prefix class, and every tail word."""
    by_key = {(left, right): changes for left, right, changes, _gate_dest, _gate_source in items}
    checked = 0
    for kind in REJECTION[:-1]:
        need(len(samples[kind]) == 25, kind + " sample count changed")
        for left, right, i, j, f_i, f_j in samples[kind]:
            words, _contacts = skeleton(scalars, left, right, by_key[(left, right)], {i: f_i, j: f_j})
            reason, _paid = emit(words, width, start, final, edges, owned)
            need(reason == "missing_edge", kind + " sample emitted or failed as " + str(reason))
            checked += 1
    need(len(tails) == EXPECTED_COUNTS["tail_missing"], "tail list does not match the census")
    for left, right, i, j, f_i, f_j in tails:
        words, _contacts = skeleton(scalars, left, right, by_key[(left, right)], {i: f_i, j: f_j})
        reason, _paid = emit(words, width, start, final, edges, owned)
        need(reason == "missing_edge", "tail sample emitted or failed as " + str(reason))
        checked += 1
    return checked


def main():
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
    reason, base = emit(scalars, width, start, final, edges, owned)
    need(reason is None and dict(base) == BASE_PAID, "published word does not emit its histogram")
    histogram, capped = length_histogram(scalars)
    need(capped == 0, "the length scan hit its cap")
    need(dict(histogram) == LENGTHS, "A2 length histogram changed " + str(dict(histogram)))
    need(sum(count for length, count in histogram.items() if length >= 5) == 1384,
         "length-at-least-5 interval total changed")
    need(histogram[2] == 331 and histogram[3] == 250 and histogram[4] == 119,
         "short-interval control disagrees with PR6664")
    items, counts, first, samples, tails, emitted = census(
        scalars, edges, frames, width, owned, start, final, base, expected)
    need(dict(counts) == EXPECTED_COUNTS, "two-move census changed " + str(dict(counts)))
    need({key: first[key] for key in FIRST_COUNTS} == FIRST_COUNTS,
         "first-interval census changed " + str(dict(first)))
    rejected = sum(counts[kind] for kind in REJECTION)
    need(rejected == counts["assignments"] == ASSIGNMENTS,
         "rejection classes do not partition the assignments")
    need(not emitted, "a two-move assignment emitted")
    one_move_control(scalars, items, edges, width, owned, start, final, base, expected)
    checked = control_samples(scalars, items, samples, tails, width, start, final, edges, owned)
    need(checked == 100 + EXPECTED_COUNTS["tail_missing"], "cold-replay count changed")
    need(strict_loss(((1, 2), (2, -1))) and not strict_loss(((1, 1), (2, -2), (3, 1))),
         "strict-loss classifier control failed")
    print(
        "PASS_G20_LENGTH5_TWO_MOVE"
        " intervals=133 pairs=1330 assignments={assignments}"
        " prefix_fail={prefix_fail} first_meet={first_meet} middle_fail={middle_fail}"
        " second_meet={second_meet} full_replays={full_replays} tail_missing={tail_missing}"
        " emitted=0 savings=0"
        " first_interval=1119-8918/4032250/0"
        " cold_replays={checked} one_move_control=3H2-H4"
        " length6_open=86 no_new_kappa=true".format(checked=checked, **counts))


if __name__ == "__main__":
    main()
