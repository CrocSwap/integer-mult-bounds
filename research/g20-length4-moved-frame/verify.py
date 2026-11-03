#!/usr/bin/env python3
"""Length-4 G20 conjugations with one correction moved off its contact frame.

The A2 identity and the one-edge emitter are the #5708 contract. This file
does not import research/g20-conjugation-admission/construct.py or the
length-1..3 moved-frame verifier. Both are pinned inputs or cited results.
"""

from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import gzip
import json

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
EXPECTED = {
    "routes": 2369,
    "frames": 636,
    "base_paid": {1: 1281, 2: 1338, 3: 58, 4: 57, 5: 102, 6: 10},
    "length4": 119,
    "fixed_missing": 118,
    "fixed_neutral": 1,
    "neutral_left": 9399,
    "neutral_right": 10815,
    "neutral_dest": 560,
    "neutral_source": 315,
    "assignments": 302260,
    "local_feasible": 504,
    "moved_missing": 504,
    "moved_emitted": 0,
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
    rows = rows[:]
    state = state[:]
    for event in (contact, extra):
        dest, source, frame = event[1], event[2], event[3]
        if not rows[source]:
            continue
        for wire in (dest, source):
            origin = state[wire]
            if origin == frame:
                continue
            if (origin, frame) not in edges:
                return False
            state[wire] = frame
        rows[dest] ^= rows[source]
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


def screen_length4(scalars, edges, outward, frames, width, owned, start, final, base, expected):
    counts = Counter()
    neutral = None
    for left, right, changes in intervals_of(scalars, exact=4):
        need(len(changes) == 4, "length filter drifted")
        for _index, _extra, frame0, _dest, _source in changes:
            need(frame0 in frames, "contact frame is outside the route table")
        fixed = skeleton(scalars, left, right, changes, {})
        need(endpoint_ok(fixed, width, owned, expected), "length-4 endpoint failed")
        reason, paid = paid_histogram(fixed, width, owned, start, final, edges)
        if reason is not None:
            need(reason == "missing_edge", "fixed length-4 failed as " + reason)
            counts["fixed_missing"] += 1
        else:
            need(delta_of(paid, base) == (), "fixed length-4 emitted a changed histogram")
            counts["fixed_neutral"] += 1
            need(neutral is None, "more than one neutral length-4 word")
            neutral = (left, right, scalars[left][1], scalars[left][2])
        snaps = snapshots(fixed, contact_positions(scalars, left, right, changes), width, start)
        need(len(snaps) == 4, "snapshot count is not four")
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
                if local and frame not in cand:
                    counts["filter_gaps"] += 1
                if not local:
                    counts["local_fail"] += 1
                    continue
                counts["local_feasible"] += 1
                rewritten = skeleton(scalars, left, right, changes, {number: frame})
                need(endpoint_ok(rewritten, width, owned, expected), "moved frame changed the scalar endpoint")
                reason, _paid = paid_histogram(rewritten, width, owned, start, final, edges)
                need(reason == "missing_edge", "moved length-4 frame emitted or failed as " + str(reason))
                counts["moved_missing"] += 1
    counts["length4"] = counts["fixed_missing"] + counts["fixed_neutral"]
    return counts, neutral


def recount_long(scalars, edges, width, owned, start, final, base, expected):
    missing = zero = 0
    shapes = Counter()
    for left, right, changes in intervals_of(scalars, minimum=4):
        fixed = skeleton(scalars, left, right, changes, {})
        need(endpoint_ok(fixed, width, owned, expected), "long fixed endpoint failed")
        reason, paid = paid_histogram(fixed, width, owned, start, final, edges)
        if reason is not None:
            need(reason == "missing_edge", "long fixed failed as " + reason)
            missing += 1
            continue
        delta = delta_of(paid, base)
        if delta == ():
            zero += 1
            continue
        need(strict_loss(delta), "long fixed shape is not a strict loss " + str(delta))
        shapes[delta] += 1
    return missing, zero, shapes


def controls(edges, outward, scalars, width, owned, start, final):
    need(strict_loss(((1, 2), (2, -1))), "2 H1 - H2 must be a strict loss")
    need(not strict_loss(SAVING), "H1 - 2 H2 + H3 must not be called a loss")
    need(not strict_loss(()), "an empty change is not a strict loss")
    need(all(strict_loss(shape) for shape in LONG_SHAPES), "a published long shape lost its sign")
    # Delete an edge the published word actually traverses.
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
    need(used[1] not in (outward[used[0]] - {used[1]}), "neighbor set did not shrink")


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
    counts, neutral = screen_length4(
        scalars, edges, outward, frames, width, owned, start, final, base, expected)
    need(neutral == (
        EXPECTED["neutral_left"], EXPECTED["neutral_right"],
        EXPECTED["neutral_dest"], EXPECTED["neutral_source"]),
         "neutral length-4 word moved " + str(neutral))
    for key in ("length4", "fixed_missing", "fixed_neutral", "assignments",
                "local_feasible", "moved_missing"):
        need(counts[key] == EXPECTED[key], key + " changed to " + str(counts[key]))
    need(counts["filter_gaps"] == 0, "meeting filter omitted a locally feasible frame")
    need(counts["local_feasible"] == counts["moved_missing"], "a feasible move emitted")
    need(counts["local_fail"] + counts["local_feasible"] == counts["assignments"],
         "local partition does not cover the assignments")
    need(EXPECTED["moved_emitted"] == 0, "the claimed emission count is not zero")
    missing, zero, shapes = recount_long(
        scalars, edges, width, owned, start, final, base, expected)
    need(missing == EXPECTED["long_missing"], "long missing count changed")
    need(zero == EXPECTED["long_zero"], "long neutral count changed")
    need(dict(shapes) == LONG_SHAPES, "long loss shapes changed " + str(shapes))
    need(missing + zero + sum(shapes.values()) == EXPECTED["long_intervals"],
         "long census does not add")
    controls(edges, outward, scalars, width, owned, start, final)
    print(
        "PASS_G20_LENGTH4_MOVED_FRAME"
        " intervals={length4} fixed_missing={fixed_missing} fixed_neutral={fixed_neutral}"
        " moved_assignments={assignments} local_fail={local_fail}"
        " local_feasible={local_feasible} missing_edge={moved_missing}"
        " emitted=0 savings=0"
        " long_control={long_intervals}/{long_missing}/{long_zero}/{long_loss}"
        " no_new_kappa=true".format(
            length4=counts["length4"], fixed_missing=counts["fixed_missing"],
            fixed_neutral=counts["fixed_neutral"], assignments=counts["assignments"],
            local_fail=counts["local_fail"], local_feasible=counts["local_feasible"],
            moved_missing=counts["moved_missing"],
            long_intervals=EXPECTED["long_intervals"], long_missing=missing,
            long_zero=zero, long_loss=sum(shapes.values())))


if __name__ == "__main__":
    main()
