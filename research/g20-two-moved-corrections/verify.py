#!/usr/bin/env python3
"""Short G20 conjugations with two corrections moved off their contact frames.

The A2 identity, the constructor and the one-edge emitter are the #5708
contract, as restated by PR #6337 and PR #6633. This file reimplements the
emitter; it imports no predecessor verifier.

Domain: every A2 interval of the emitted #5708 word with exactly 2, 3 or 4
contacts, every pair i < j of its corrections, and every pair of frames
(f_i, f_j) of the route table with f_i, f_j different from the contact
frames. The other corrections stay on their contact frames.

Every assignment is classified by an exact prefix replay:

  prefix_fail  the shared prefix up to contact i misses a route;
  first_meet   the moved pair (contact i, correction i) at f_i misses a route;
  middle_fail  the records between correction i and contact j miss a route;
  second_meet  the moved pair (contact j, correction j) at f_j misses a route;
  tail_missing the full replay misses a later route;
  neutral / loss / saving  the full replay emits with that paid change
               (no assignment reaches these classes).

The first four classes depend only on a prefix of the rewritten word, and
the emitter rejects at the first missing route, so each is a rejection of
the full word. Controls replay 25 full words from scratch per rejection
class, and the same emitter reproduces the PR #6337 one-move census.
"""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
BASE_PAID = {1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10}
ROUTES = 2369
FRAMES = 636
EXPECTED_COUNTS = {
    "assignments": 723788875,
    "prefix_fail": 80241775,
    "first_meet": 607824540,
    "first_hosts": 28137,
    "middle_fail": 35467290,
    "second_meet": 255171,
    "full_replays": 99,
    "tail_missing": 99,
}
EXPECTED_BY_LENGTH = {
    2: {"intervals": 331, "pairs": 331, "assignments": 133467475},
    3: {"intervals": 250, "pairs": 750, "assignments": 302418750},
    4: {"intervals": 119, "pairs": 714, "assignments": 287902650},
}
ONE_MOVE_SHAPES = {((4, 1),): 2, ((2, 5), (4, -2)): 24}


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
    need('out.extend([e[:3] + [f], extra[:3] + [f]])' in source,
         "constructor no longer puts the contact and correction on one chosen frame")
    word = json.loads(gzip.decompress(blobs["research/g20-conjugation-admission/WORD.json.gz"]))
    paths = json.loads(blobs["research/g20-conjugation-admission/PATHS.json"])
    local = json.loads(blobs["research/g20-conjugation-admission/LOCAL-RESULT.json"])
    return word, paths, local


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

    def run_unchecked(self, records):
        """Snapshot semantics of the predecessors: move wires, check nothing."""
        rows, state = self.rows, self.state
        for event in records:
            op, dest = event[0], event[1]
            if op in ("ERASE", "INIT"):
                rows[dest] = 0
                state[dest] = event[2]
                continue
            source, frame = event[2], event[3]
            if rows[source]:
                state[dest] = state[source] = frame
                rows[dest] ^= rows[source]

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


def intervals_of(scalars, lengths):
    groups = defaultdict(list)
    for index, event in enumerate(scalars):
        if event[0] == "ADD":
            groups[(event[1], event[2])].append(index)
    found = []
    top = max(lengths)
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
                        if extra is None or len(changes) == top:
                            rejected = True
                            break
                        changes.append((index, extra, event[3]))
                if rejected or len(changes) not in lengths:
                    continue
                found.append((left, right, changes))
    return sorted(found)


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
    return tuple(sorted((rank, paid[rank] - base[rank]) for rank in ranks if paid[rank] != base[rank]))


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


def census(scalars, edges, frames, width, owned, start, final, base, expected):
    """Resume each assignment from cached prefix states of the same word."""
    counts = Counter()
    shapes = Counter()
    by_length = defaultdict(Counter)
    emitted = []
    samples = defaultdict(list)
    for left, right, changes in intervals_of(scalars, (2, 3, 4)):
        length = len(changes)
        by_length[length]["intervals"] += 1
        fixed, contacts = skeleton(scalars, left, right, changes, {})
        need(endpoint_ok(fixed, width, owned, expected), "contact-frame endpoint failed")
        others = [[f for f in frames if f != change[2]] for change in changes]
        snaps = []
        machine = fresh(width, start, edges, owned)
        cursor = 0
        alive = True
        for position in contacts:
            if alive and machine.run(fixed[cursor:position]) is not None:
                alive = False
            snaps.append(machine.copy() if alive else None)
            cursor = position
        for i in range(length):
            for j in range(i + 1, length):
                block = len(others[i]) * len(others[j])
                by_length[length]["pairs"] += 1
                by_length[length]["assignments"] += block
                counts["assignments"] += block
            if snaps[i] is None:
                for j in range(i + 1, length):
                    counts["prefix_fail"] += len(others[i]) * len(others[j])
                    samples["prefix_fail"].append((left, right, i, j, others[i][0], others[j][0]))
                continue
            for f_i in others[i]:
                at = snaps[i].copy()
                c_i = contacts[i]
                if at.run([moved(fixed[c_i], f_i), moved(fixed[c_i + 1], f_i)]) is not None:
                    for j in range(i + 1, length):
                        counts["first_meet"] += len(others[j])
                        samples["first_meet"].append((left, right, i, j, f_i, others[j][0]))
                    continue
                counts["first_hosts"] += 1
                cursor = c_i + 2
                for j in range(i + 1, length):
                    c_j = contacts[j]
                    if at is None or at.run(fixed[cursor:c_j]) is not None:
                        at = None
                        counts["middle_fail"] += len(others[j])
                        samples["middle_fail"].append((left, right, i, j, f_i, others[j][0]))
                        continue
                    for f_j in others[j]:
                        tail = at.copy()
                        if tail.run([moved(fixed[c_j], f_j), moved(fixed[c_j + 1], f_j)]) is not None:
                            counts["second_meet"] += 1
                            samples["second_meet"].append((left, right, i, j, f_i, f_j))
                            continue
                        counts["full_replays"] += 1
                        reason = tail.run(fixed[c_j + 2:]) or tail.finish(final)
                        if reason is not None:
                            need(reason == "missing_edge", "moved word failed as " + reason)
                            counts["tail_missing"] += 1
                            samples["tail_missing"].append((left, right, i, j, f_i, f_j))
                            continue
                        delta = delta_of(tail.paid, base)
                        emitted.append((left, right, i, j, f_i, f_j, delta))
                        by_length[length]["emitted"] += 1
                        if delta == ():
                            counts["neutral"] += 1
                        elif strict_loss(delta):
                            counts["loss"] += 1
                            shapes[delta] += 1
                        else:
                            counts["saving_or_unsigned"] += 1
                    if at.run(fixed[c_j:c_j + 2]) is not None:
                        at = None
                    cursor = c_j + 2
    return counts, shapes, by_length, emitted, samples


def one_move_control(scalars, edges, frames, width, owned, start, final, base, expected):
    """The PR #6337 one-move domain (1..3 contacts) on the same emitter."""
    hosts = 0
    shapes = Counter()
    for left, right, changes in intervals_of(scalars, (1, 2, 3)):
        fixed, contacts = skeleton(scalars, left, right, changes, {})
        need(endpoint_ok(fixed, width, owned, expected), "one-move endpoint failed")
        for i, c_i in enumerate(contacts):
            loose = fresh(width, start, edges, owned)
            loose.run_unchecked(fixed[:c_i])
            head = fresh(width, start, edges, owned)
            prefix_ok = head.run(fixed[:c_i]) is None
            for f_i in frames:
                if f_i == changes[i][2]:
                    continue
                pair = [moved(fixed[c_i], f_i), moved(fixed[c_i + 1], f_i)]
                if loose.copy().run(pair) is not None:
                    continue
                hosts += 1
                if not prefix_ok:
                    continue
                at = head.copy()
                reason = at.run(pair) or at.run(fixed[c_i + 2:]) or at.finish(final)
                if reason is None:
                    shapes[delta_of(at.paid, base)] += 1
    return hosts, shapes


def control_samples(scalars, samples, width, start, final, edges, owned):
    """Full replays of the first sampled assignment per prefix class reject."""
    intervals = {(left, right): changes for left, right, changes in intervals_of(scalars, (2, 3, 4))}
    checked = 0
    for kind in ("prefix_fail", "first_meet", "middle_fail", "second_meet", "tail_missing"):
        for left, right, i, j, f_i, f_j in samples[kind][:25]:
            words, _ = skeleton(scalars, left, right, intervals[(left, right)], {i: f_i, j: f_j})
            reason, _ = emit(words, width, start, final, edges, owned)
            need(reason == "missing_edge", kind + " sample emitted or failed as " + str(reason))
            checked += 1
    return checked


def main():
    word, paths, local = load_pinned()
    published = {int(rank): count for rank, count in local["stats"]["paid"].items()}
    need(published == BASE_PAID, "LOCAL-RESULT paid histogram drifted")
    edges, frames = load_edges(paths)
    scalars = [event[:] for event in word["records"] if event[0] not in ("Q", "ZERO_Q")]
    width = len(word["start"])
    owned = set(word["owned"])
    start, final = word["start"][:], word["final"][:]
    expected = expected_rows(width, owned)
    need(endpoint_ok(scalars, width, owned, expected), "published word misses its scalar endpoint")
    reason, base = emit(scalars, width, start, final, edges, owned)
    need(reason is None and dict(base) == BASE_PAID, "published word does not emit its histogram")
    counts, shapes, by_length, emitted, samples = census(
        scalars, edges, frames, width, owned, start, final, base, expected)
    need(dict(counts) == EXPECTED_COUNTS, "two-move census changed " + str(dict(counts)))
    need({k: dict(v) for k, v in by_length.items()} == EXPECTED_BY_LENGTH,
         "per-length census changed " + str(dict(by_length)))
    rejected = sum(counts[k] for k in ("prefix_fail", "first_meet", "middle_fail",
                                       "second_meet", "tail_missing"))
    need(rejected == counts["assignments"], "rejection classes do not partition the assignments")
    need(not emitted and not shapes, "a two-move assignment emitted")
    checked = control_samples(scalars, samples, width, start, final, edges, owned)
    need(checked == 125, "sampled full-replay controls changed")
    hosts, one_shapes = one_move_control(scalars, edges, frames, width, owned, start, final, base, expected)
    need(hosts == 28149 and dict(one_shapes) == ONE_MOVE_SHAPES,
         "one-move control disagrees with PR6337 " + str((hosts, dict(one_shapes))))
    need(all(strict_loss(shape) for shape in ONE_MOVE_SHAPES), "a one-move shape lost its sign")
    need(strict_loss(((1, 2), (2, -1))) and not strict_loss(((1, 1), (2, -2), (3, 1))),
         "strict-loss classifier control failed")
    print(
        "PASS_G20_TWO_MOVED_CORRECTIONS"
        " intervals=331/250/119 pairs=1795 assignments={assignments}"
        " prefix_fail={prefix_fail} first_meet={first_meet} middle_fail={middle_fail}"
        " second_meet={second_meet} full_replays={full_replays} tail_missing={tail_missing}"
        " emitted=0 savings=0 sampled_controls={checked}"
        " one_move_control=28149/26 no_new_kappa=true".format(checked=checked, **counts))


if __name__ == "__main__":
    main()
