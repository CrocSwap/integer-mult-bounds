#!/usr/bin/env python3
"""Length-5-and-longer G20 conjugations with one moved correction.

The A2 identity and the one-edge emitter are the #5708 contract. This file
does not import research/g20-conjugation-admission/construct.py. That module
is a pinned input. The length-1..4 one-move censuses are cited results and
are recomputed here only as controls.
"""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import gzip
import importlib.util
import json

_LEMMA = Path(__file__).with_name("lemma.py")
_spec = importlib.util.spec_from_file_location("g20_length5plus_lemma", _LEMMA)
lemma = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lemma)

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
EXPECTED = {
    "routes": 2369,
    "frames": 636,
    "base_paid": {1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10},
    "length4": 119,
    "length4_fixed_missing": 118,
    "length4_fixed_neutral": 1,
    "length4_assignments": 302260,
    "length4_local_feasible": 504,
    "length4_moved_missing": 504,
    "long_intervals": 1503,
    "long_missing": 1450,
    "long_zero": 14,
    "long_loss": 39,
}
LONG_SHAPES = {
    ((1, 2), (2, -1)): 15,
    ((1, 3), (2, 2)): 10,
    ((2, 2), (4, -1)): 5,
    ((1, 2), (2, 1), (3, 1)): 4,
    ((1, 1), (2, 3)): 2,
    ((1, 1), (2, 2), (5, -1)): 2,
    ((1, 1), (3, 1), (4, -1)): 1,
}
SAVING = ((1, 1), (2, -2), (3, 1))
LONG_COUNTS = {
    "intervals": 1384,
    "assignments": 10074275,
    "prefix_fail": 6114415,
    "pair_fail": 3272780,
    "dirty_fail": 686779,
    "clean_fail": 179,
    "repair": 2,
    "emit": 8,
    "failed_pair_replays": 112,
}
LENGTHS = {
    5: 133, 6: 86, 7: 79, 8: 124, 9: 95, 10: 129, 11: 100, 12: 151,
    13: 69, 14: 102, 15: 47, 16: 73, 17: 47, 18: 48, 19: 29, 20: 23,
    21: 9, 22: 9, 23: 8, 24: 3, 25: 2, 26: 4, 27: 4, 28: 1, 29: 2,
    30: 2, 31: 3, 33: 2,
}
# Independent emitter deltas against the published histogram. Each is a strict loss.
EMITS = (
    (6261, 11325, 7, 77, ((1, 5), (2, 1))),
    (6433, 11727, 7, 96, ((1, 5), (2, 1))),
    (7278, 10929, 6, 91, ((1, 1), (3, 2), (4, -1))),
    (7278, 10929, 6, 155, ((1, 3), (2, 3), (3, -1), (4, -1))),
    (7278, 10929, 6, 157, ((1, 3), (2, 3), (3, -1), (4, -1))),
    (7318, 10917, 3, 123, ((2, 3), (4, -1))),
    (7319, 10916, 3, 123, ((2, 3), (4, -1))),
    (7337, 10919, 2, 123, ((2, 3), (4, -1))),
)
REPAIRS = (
    (5661, 7047, 8, 358),
    (5765, 6907, 6, 417),
)


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load_pinned():
    sources = json.loads((PACKAGE / "SOURCES.json").read_text())
    wanted = {row["path"]: row["sha256"] for row in sources["files"] if row["usage"] == "input"}
    blobs = {}
    for name, expected in wanted.items():
        path = ROOT / name
        actual = digest(path)
        need(actual == expected, "input hash mismatch " + name)
        blobs[name] = path.read_bytes()
    readme = blobs["research/g20-conjugation-admission/README.md"].decode()
    source = blobs["research/g20-conjugation-admission/construct.py"].decode()
    need("one-to-three-contact conjugations" in readme, "README lost the conjugation sentence")
    need("local-only evidence, not replayed search" in readme, "README lost the local-only limit")
    need('out.extend([e[:3] + [f], extra[:3] + [f]])' in source,
         "constructor no longer puts the contact and correction on one chosen frame")
    word = json.loads(gzip.decompress(blobs["research/g20-conjugation-admission/WORD.json.gz"]))
    paths = json.loads(blobs["research/g20-conjugation-admission/PATHS.json"])
    local = json.loads(blobs["research/g20-conjugation-admission/LOCAL-RESULT.json"])
    return word, paths, local


def load_edges(paths):
    edges = {}
    outward = defaultdict(set)
    frames = set()
    for key, value in paths.items():
        left, right = key.split(":")
        need(len(value) == 1, "route " + key + " is not one edge")
        start, end, rank = value[0]
        need(start == int(left) and end == int(right), "route endpoints disagree with " + key)
        need(type(rank) is int and 1 <= rank <= 7, "route rank outside 1..7")
        edges[(start, end)] = rank
        outward[start].add(end)
        frames.add(start)
        frames.add(end)
    need(len(edges) == EXPECTED["routes"], "route count changed")
    need(len(frames) == EXPECTED["frames"], "frame count changed")
    return edges, outward, frames


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


def paid_histogram(records, width, owned, start, final, edges):
    rows = [1 << index for index in range(width)]
    state = start[:]
    paid = Counter()
    for event in records:
        op, dest = event[0], event[1]
        if op in ("ERASE", "INIT"):
            if dest not in owned or (op == "INIT" and rows[dest]):
                return "owned_op", None
            rows[dest] = 0
            state[dest] = event[2]
            continue
        if op != "ADD":
            return "opcode", None
        source, frame = event[2], event[3]
        if not rows[source]:
            continue
        for wire in (dest, source):
            origin = state[wire]
            if origin == frame:
                continue
            rank = edges.get((origin, frame))
            if rank is None:
                return "missing_edge", None
            if rows[wire]:
                paid[rank] += 1
            state[wire] = frame
        rows[dest] ^= rows[source]
    for dest, frame in enumerate(final):
        if dest in owned:
            if rows[dest]:
                return "owned_live", None
            state[dest] = frame
            continue
        origin = state[dest]
        if origin == frame:
            continue
        rank = edges.get((origin, frame))
        if rank is None:
            return "missing_edge", None
        if rows[dest]:
            paid[rank] += 1
        state[dest] = frame
    if state != final:
        return "final_state", None
    return None, paid


def correction(event, gate_dest, gate_source):
    dest, source = event[1], event[2]
    if dest == gate_source and source != gate_dest:
        return ["ADD", gate_dest, source]
    if source == gate_dest and dest != gate_source:
        return ["ADD", dest, gate_source]
    return None


def delta_of(paid, base):
    ranks = set(paid) | set(base)
    return tuple(sorted((rank, paid[rank] - base[rank]) for rank in ranks if paid[rank] != base[rank]))


def two_step_reaches(rows, state, contact, extra, edges):
    """Same rejection rule as replaying the contact and its correction.

    Both events use one frame. A dead event does not read that frame. A live
    event rejects when a wire is off the frame and the route table has no edge.
    The contact updates those wires before the correction reads them.
    """
    dest, source, frame = contact[1], contact[2], contact[3]
    extra_dest, extra_source, extra_frame = extra[1], extra[2], extra[3]
    if extra_frame != frame:
        return False
    contact_live = bool(rows[source])
    if contact_live:
        for wire in (dest, source):
            origin = state[wire]
            if origin != frame and (origin, frame) not in edges:
                return False
        dest_row = rows[dest] ^ rows[source]
    else:
        dest_row = rows[dest]
    if extra_source == dest and contact_live:
        corr_rows = dest_row
    else:
        corr_rows = rows[extra_source]
    if not corr_rows:
        return True

    def origin_after_contact(wire):
        if contact_live and wire in (dest, source) and state[wire] != frame:
            return frame
        return state[wire]

    for wire in (extra_dest, extra_source):
        origin = origin_after_contact(wire)
        if origin != frame and (origin, frame) not in edges:
            return False
    return True


def meeting_wires(rows, contact, extra):
    dest, source = contact[1], contact[2]
    corr_dest, corr_source = extra[1], extra[2]
    wires = []
    if rows[source]:
        wires.extend((dest, source))
    corr_rows = rows[corr_source]
    if corr_source == dest and rows[source]:
        corr_rows = rows[dest] ^ rows[source]
    if corr_rows:
        moved = {dest, source} if rows[source] else set()
        if corr_source not in moved:
            wires.append(corr_source)
        if corr_dest not in moved:
            wires.append(corr_dest)
    return list(dict.fromkeys(wires))


def reachable(origin, outward):
    return outward[origin] | {origin}


def intervals_of(scalars, exact=None, minimum=None):
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
                        if extra is None or (exact is not None and len(changes) == exact):
                            rejected = True
                            break
                        changes.append((index, extra, event[3], event[1], event[2]))
                if rejected or not changes:
                    continue
                if exact is not None and len(changes) != exact:
                    continue
                if minimum is not None and len(changes) < minimum:
                    continue
                found.append((left, right, changes))
    return found


def skeleton(scalars, left, right, changes, override):
    replaced = {}
    for number, (index, extra, frame0, _dest, _source) in enumerate(changes):
        replaced[index] = (extra, override.get(number, frame0))
    out = []
    for index, event in enumerate(scalars):
        if index in (left, right):
            continue
        if index in replaced:
            extra, frame = replaced[index]
            out.append(event[:3] + [frame])
            out.append(extra + [frame])
        else:
            out.append(event)
    return out


def snapshots(skeleton_records, contact_positions, width, start):
    rows = [1 << index for index in range(width)]
    state = start[:]
    snaps = []
    cursor = 0
    for position, event in enumerate(skeleton_records):
        if cursor < len(contact_positions) and position == contact_positions[cursor]:
            snaps.append((rows[:], state[:]))
            cursor += 1
        op, dest = event[0], event[1]
        if op in ("ERASE", "INIT"):
            rows[dest] = 0
            state[dest] = event[2]
            continue
        source, frame = event[2], event[3]
        if not rows[source]:
            continue
        for wire in (dest, source):
            if state[wire] != frame:
                state[wire] = frame
        rows[dest] ^= rows[source]
    need(cursor == len(contact_positions), "missed a contact while snapshotting")
    return snaps


def contact_positions(scalars, left, right, changes):
    positions = []
    cursor = 0
    change_at = {change[0] for change in changes}
    for index, _event in enumerate(scalars):
        if index in (left, right):
            continue
        if index in change_at:
            positions.append(cursor)
            cursor += 2
        else:
            cursor += 1
    return positions


def clean(counter):
    return Counter({rank: count for rank, count in counter.items() if count})


def strict_loss(delta):
    """Positive by nonnegative terms or by repeated strict rank splits."""
    pos = Counter()
    neg = Counter()
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
        if len(items) > 12:
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


def classify_fixed(reason, paid, base, shapes):
    if reason is not None:
        need(reason == "missing_edge", "fixed word failed as " + reason)
        return "missing"
    delta = delta_of(paid, base)
    if delta == ():
        return "neutral"
    need(strict_loss(delta), "fixed shape is not a strict loss " + str(delta))
    shapes[delta] += 1
    return "loss"


def screen_exact4(scalars, edges, outward, frames, width, owned, start, final, base, expected):
    counts = Counter()
    for left, right, changes in intervals_of(scalars, exact=4):
        fixed = skeleton(scalars, left, right, changes, {})
        need(endpoint_ok(fixed, width, owned, expected), "length-4 endpoint failed")
        reason, paid = paid_histogram(fixed, width, owned, start, final, edges)
        if reason is not None:
            need(reason == "missing_edge", "fixed length-4 failed as " + reason)
            counts["fixed_missing"] += 1
        else:
            need(delta_of(paid, base) == (), "fixed length-4 emitted a changed histogram")
            counts["fixed_neutral"] += 1
        snaps = snapshots(fixed, contact_positions(scalars, left, right, changes), width, start)
        for number, (rows0, state0) in enumerate(snaps):
            _index, extra, frame0, dest, source = changes[number]
            contact = ["ADD", dest, source, frame0]
            wires = meeting_wires(rows0, contact, extra)
            need(wires, "a length-4 correction is dead at the meeting")
            cand = None
            for wire in wires:
                reach = reachable(state0[wire], outward)
                cand = reach if cand is None else cand & reach
            cand.discard(frame0)
            for frame in frames:
                if frame == frame0:
                    continue
                counts["assignments"] += 1
                local = two_step_reaches(
                    rows0, state0, ["ADD", dest, source, frame], extra + [frame], edges)
                if local != (frame in cand):
                    counts["filter_gaps"] += 1
                if not local:
                    counts["local_fail"] += 1
                    continue
                counts["local_feasible"] += 1
                rewritten = skeleton(scalars, left, right, changes, {number: frame})
                need(endpoint_ok(rewritten, width, owned, expected), "moved length-4 endpoint failed")
                reason, _paid = paid_histogram(rewritten, width, owned, start, final, edges)
                need(reason == "missing_edge", "moved length-4 frame emitted or failed as " + str(reason))
                counts["moved_missing"] += 1
    return counts


def replay_moved(scalars, left, right, changes, number, frame, width, owned, start, final, edges, expected):
    rewritten = skeleton(scalars, left, right, changes, {number: frame})
    need(endpoint_ok(rewritten, width, owned, expected), "moved frame changed the scalar endpoint")
    return paid_histogram(rewritten, width, owned, start, final, edges)


def screen_long(scalars, edges, outward, frames, width, owned, start, final, base, expected):
    counts = Counter()
    shapes = Counter()
    by_length = Counter()
    neutrals = []
    emits = []
    repairs = []
    other_frames = len(frames) - 1
    prefix_checked = set()
    for left, right, changes in intervals_of(scalars, minimum=5):
        length = len(changes)
        by_length[length] += 1
        counts["intervals"] += 1
        for _index, _extra, frame0, _dest, _source in changes:
            need(frame0 in frames, "contact frame is outside the route table")
        fixed = skeleton(scalars, left, right, changes, {})
        need(endpoint_ok(fixed, width, owned, expected), "long endpoint failed")
        reason, paid = paid_histogram(fixed, width, owned, start, final, edges)
        kind = classify_fixed(reason, paid, base, shapes)
        counts["fixed_" + kind] += 1
        if kind == "neutral":
            neutrals.append((left, right, scalars[left][1], scalars[left][2], length))
        positions = contact_positions(scalars, left, right, changes)
        prepared = lemma.walk_fixed(
            fixed, width, start, final, owned, edges, save_at=positions)
        syncs = lemma.sync_after(
            prepared, [position + 1 for position in positions], width, final, owned)
        fail_at = prepared["fail_at"]
        fail = prepared["fail"]
        for number, (_index, extra, frame0, dest, source) in enumerate(changes):
            position = positions[number]
            counts["assignments"] += other_frames
            if position not in prepared["befores"]:
                counts["prefix_fail"] += other_frames
                if length not in prefix_checked:
                    frame = min(frame for frame in frames if frame != frame0)
                    moved_reason, _moved_paid = replay_moved(
                        scalars, left, right, changes, number, frame,
                        width, owned, start, final, edges, expected)
                    need(moved_reason == "missing_edge", "a prefix failure emitted")
                    prefix_checked.add(length)
                continue
            rows0, state0 = prepared["befores"][position]
            wires = meeting_wires(rows0, ["ADD", dest, source, frame0], extra)
            need(wires, "a long correction is dead at the meeting")
            cand = None
            for wire in wires:
                reach = reachable(state0[wire], outward)
                cand = reach if cand is None else cand & reach
            cand.discard(frame0)
            outside = min((frame for frame in frames if frame != frame0 and frame not in cand), default=None)
            if outside is not None:
                outside_ok, _overlay, _paid = lemma.apply_pair(
                    rows0, state0, dest, source, extra[1], extra[2], outside, edges)
                need(not outside_ok, "meeting filter rejected a frame the pair accepts")
            fixed_ok, fixed_overlay, fixed_paid = lemma.apply_pair(
                rows0, state0, dest, source, extra[1], extra[2], frame0, edges)
            nxt = syncs[position + 1]
            if not fixed_ok:
                counts["pair_fail"] += other_frames - len(cand)
                for frame in sorted(cand):
                    moved_reason, _moved_paid = replay_moved(
                        scalars, left, right, changes, number, frame,
                        width, owned, start, final, edges, expected)
                    need(moved_reason == "missing_edge", "a failed contact pair was repaired into an emission")
                    counts["failed_pair_replays"] += 1
                continue
            counts["pair_fail"] += other_frames - len(cand)
            for frame in sorted(cand):
                pair_ok, _overlay, _paid = lemma.apply_pair(
                    rows0, state0, dest, source, extra[1], extra[2], frame, edges)
                need(pair_ok, "meeting filter accepted a frame the pair rejects")
                label, _delta = lemma.classify_frame(
                    rows0, state0, dest, source, extra[1], extra[2], frame,
                    fixed_overlay, fixed_paid, nxt, fail_at, fail, edges)
                need(label != "pair_fail", "classifier rejected a frame that passes the pair")
                counts[label] += 1
                if label == "emit":
                    moved_reason, moved_paid = replay_moved(
                        scalars, left, right, changes, number, frame,
                        width, owned, start, final, edges, expected)
                    need(moved_reason is None, "lemma emission does not emit")
                    delta = delta_of(moved_paid, base)
                    need(strict_loss(delta), "emitted shape is not a strict loss " + str(delta))
                    emits.append((left, right, number, frame, delta))
                elif label == "repair":
                    moved_reason, _moved_paid = replay_moved(
                        scalars, left, right, changes, number, frame,
                        width, owned, start, final, edges, expected)
                    need(moved_reason == "missing_edge", "a repair candidate emitted")
                    repairs.append((left, right, number, frame))
                else:
                    need(label in ("dirty_fail", "clean_fail"), "unknown class " + label)
    need(prefix_checked == set(by_length),
         "prefix control missed a length " + str(sorted(set(by_length) - prefix_checked)))
    covered = (
        counts["prefix_fail"] + counts["pair_fail"] + counts["dirty_fail"]
        + counts["clean_fail"] + counts["repair"] + counts["emit"]
        + counts["failed_pair_replays"])
    need(covered == counts["assignments"], "assignment partition failed " + str(dict(counts)))
    return counts, shapes, by_length, neutrals, emits, repairs



def controls(edges, outward, scalars, width, owned, start, final):
    need(strict_loss(((1, 2), (2, -1))), "2 H1 - H2 must be a strict loss")
    need(not strict_loss(SAVING), "H1 - 2 H2 + H3 must not be called a loss")
    need(not strict_loss(()), "an empty change is not a strict loss")
    need(all(strict_loss(shape) for shape in LONG_SHAPES), "a published long shape lost its sign")
    rows = [1 << index for index in range(width)]
    state = start[:]
    used = None
    for event in scalars:
        if event[0] != "ADD" or not rows[event[2]]:
            if event[0] in ("ERASE", "INIT"):
                rows[event[1]] = 0
                state[event[1]] = event[2]
            continue
        for wire in (event[1], event[2]):
            if state[wire] != event[3]:
                used = (state[wire], event[3])
                break
        if used:
            break
        for wire in (event[1], event[2]):
            state[wire] = event[3]
        rows[event[1]] ^= rows[event[2]]
    need(used in edges, "published word used no route on the first live ADD")
    broken = dict(edges)
    del broken[used]
    reason, _paid = paid_histogram(scalars, width, owned, start, final, broken)
    need(reason == "missing_edge", "deleting a used edge still emitted")


def main():
    word, paths, local = load_pinned()
    published = {int(rank): count for rank, count in local["stats"]["paid"].items()}
    need(published == EXPECTED["base_paid"], "LOCAL-RESULT paid histogram drifted")
    edges, outward, frames = load_edges(paths)
    scalars = [event[:] for event in word["records"] if event[0] not in ("Q", "ZERO_Q")]
    width = len(word["start"])
    owned = set(word["owned"])
    start = word["start"][:]
    final = word["final"][:]
    expected = expected_rows(width, owned)
    need(endpoint_ok(scalars, width, owned, expected), "published word misses its scalar endpoint")
    reason, base = paid_histogram(scalars, width, owned, start, final, edges)
    need(reason is None, "published word does not emit")
    need(dict(base) == EXPECTED["base_paid"], "base histogram drifted")
    controls(edges, outward, scalars, width, owned, start, final)
    short = screen_exact4(
        scalars, edges, outward, frames, width, owned, start, final, base, expected)
    need(short["fixed_missing"] == EXPECTED["length4_fixed_missing"], "length-4 missing drifted")
    need(short["fixed_neutral"] == EXPECTED["length4_fixed_neutral"], "length-4 neutral drifted")
    need(short["assignments"] == EXPECTED["length4_assignments"], "length-4 assignments drifted")
    need(short["local_feasible"] == EXPECTED["length4_local_feasible"], "length-4 feasible drifted")
    need(short["moved_missing"] == EXPECTED["length4_moved_missing"], "length-4 missing moves drifted")
    need(short["filter_gaps"] == 0, "length-4 meeting filter disagreed")
    need(short["local_fail"] + short["local_feasible"] == short["assignments"],
         "length-4 local partition failed")
    counts, shapes, by_length, neutrals, emits, repairs = screen_long(
        scalars, edges, outward, frames, width, owned, start, final, base, expected)
    fixed_total = counts["fixed_missing"] + counts["fixed_neutral"] + counts["fixed_loss"]
    need(fixed_total == counts["intervals"], "fixed classes do not cover the intervals")
    need(counts["intervals"] == LONG_COUNTS["intervals"], "interval count changed")
    need(dict(by_length) == LENGTHS, "length histogram changed " + str(dict(by_length)))
    need(len(neutrals) == counts["fixed_neutral"], "neutral list drifted")
    need(counts["intervals"] + EXPECTED["length4"] == EXPECTED["long_intervals"],
         "length split does not recover the #6305 interval total")
    need(counts["fixed_missing"] + EXPECTED["length4_fixed_missing"] == EXPECTED["long_missing"],
         "length split does not recover the #6305 missing total")
    need(counts["fixed_neutral"] + EXPECTED["length4_fixed_neutral"] == EXPECTED["long_zero"],
         "length split does not recover the #6305 neutral total")
    need(counts["fixed_loss"] == EXPECTED["long_loss"], "length-5-and-above losses drifted")
    need(dict(shapes) == LONG_SHAPES, "long loss shapes changed " + str(dict(shapes)))
    for key, value in LONG_COUNTS.items():
        need(counts[key] == value, key + " changed to " + str(counts[key]))
    need(tuple(emits) == EMITS, "emitted witnesses changed " + str(emits))
    need(tuple(repairs) == REPAIRS, "repair witnesses changed " + str(repairs))
    print(
        "PASS_G20_LENGTH5PLUS_ONE_MOVE"
        " intervals={intervals} lengths={lengths}"
        " fixed_missing={fixed_missing} fixed_neutral={fixed_neutral} fixed_loss={fixed_loss}"
        " assignments={assignments} prefix_fail={prefix_fail} pair_fail={pair_fail}"
        " dirty_fail={dirty_fail} clean_fail={clean_fail}"
        " failed_pair_replays={failed_pair_replays} repairs={repair} emitted={emit}"
        " savings=0 length4_control={length4}/{feasible}"
        " no_new_kappa=true".format(
            intervals=counts["intervals"], lengths=len(LENGTHS),
            fixed_missing=counts["fixed_missing"],
            fixed_neutral=counts["fixed_neutral"],
            fixed_loss=counts["fixed_loss"],
            assignments=counts["assignments"],
            prefix_fail=counts["prefix_fail"],
            pair_fail=counts["pair_fail"],
            dirty_fail=counts["dirty_fail"],
            clean_fail=counts["clean_fail"],
            failed_pair_replays=counts["failed_pair_replays"],
            repair=counts["repair"], emit=counts["emit"],
            length4=EXPECTED["length4"],
            feasible=EXPECTED["length4_local_feasible"]))


if __name__ == "__main__":
    main()
