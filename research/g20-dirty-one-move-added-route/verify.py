#!/usr/bin/env python3
"""One added route at the first missing edge of each dirty one-move failure.

The word, route table and one-move classifier are the #6923 contract. This
file replays that classifier and then inserts the first missing edge. It does
not import research/g20-conjugation-admission/construct.py. That module is a
pinned input. Checks raise exceptions, so optimization does not disable them.
"""

from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from multiprocessing import get_context
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent
PREDECESSOR = ROOT / "research" / "g20-length5plus-one-move"
_SPEC = spec_from_file_location(
    "g20_length5plus_one_move_verify", PREDECESSOR / "verify.py")
predecessor = module_from_spec(_SPEC)
_SPEC.loader.exec_module(predecessor)
lemma = predecessor.lemma

DIRTY = 686779
LATER_MISSING = 686386
EMITTED = 393
DISTINCT_PAIRS = 22709
MAX_MULTIPLICITY = 1841
PAIR_SHA256 = "8f38eb2f6e526ede87a62c1fc88c35fd5d3ba87a16f755df690a76cea5a68494"
SELECTED_KAPPA = "781451/250000000"
LENGTHS = (
    (5, 52977), (6, 3410), (7, 41503), (8, 9599), (9, 37141), (10, 21719),
    (11, 39043), (12, 37949), (13, 53725), (14, 44620), (15, 43293),
    (16, 32472), (17, 49579), (18, 27302), (19, 31519), (20, 18228),
    (21, 25320), (22, 7272), (23, 24621), (24, 8181), (25, 7275),
    (26, 12739), (27, 15762), (28, 3636), (29, 7883), (30, 7580),
    (31, 12732), (33, 9699),
)
# (paying uses of the added edge, histogram difference of every other edge, count)
SHAPES = (
    (1, ((1, -3), (2, 2)), 8),
    (1, ((1, -2), (2, 5)), 2),
    (1, ((1, -1), (2, 1)), 7),
    (1, ((1, -1), (2, 3), (4, -1)), 2),
    (1, ((1, 1), (2, 2), (5, -1)), 1),
    (1, ((1, 1), (2, 3)), 1),
    (1, ((1, 1), (2, 3), (5, -1)), 1),
    (1, ((1, 1), (3, 3), (4, -1)), 2),
    (1, ((1, 2), (3, 2)), 3),
    (1, ((1, 3), (2, 2)), 1),
    (1, ((1, 3), (2, 3)), 2),
    (1, ((1, 3), (2, 3), (3, -1)), 1),
    (1, ((2, 3), (4, -1)), 2),
    (1, ((2, 3), (5, -1)), 2),
    (1, ((2, 4),), 8),
    (1, ((2, 4), (4, -1)), 9),
    (1, ((3, -1), (4, 1)), 1),
    (1, ((4, 2),), 1),
    (2, ((1, 1), (2, 2), (3, 1)), 2),
    (2, ((1, 1), (2, 2), (3, 1), (4, -1)), 3),
    (2, ((1, 1), (2, 2), (5, -1)), 1),
    (2, ((1, 1), (2, 3)), 1),
    (2, ((1, 1), (2, 3), (3, -1), (4, -1)), 9),
    (2, ((1, 1), (2, 3), (3, 1), (4, -1)), 22),
    (2, ((1, 1), (2, 4), (5, -1)), 2),
    (2, ((1, 1), (2, 5)), 3),
    (2, ((1, 1), (3, -1), (4, 2)), 1),
    (2, ((1, 1), (3, 1), (4, 2)), 2),
    (2, ((1, 1), (3, 4), (4, -1)), 2),
    (2, ((1, 2), (2, 1), (3, 3)), 2),
    (2, ((1, 2), (2, 3)), 6),
    (2, ((1, 2), (2, 3), (3, -1)), 3),
    (2, ((1, 2), (2, 3), (3, 1)), 6),
    (2, ((1, 3), (2, 2)), 1),
    (2, ((1, 3), (2, 4)), 10),
    (2, ((1, 3), (3, 2)), 1),
    (2, ((2, 2),), 1),
    (2, ((2, 3),), 27),
    (2, ((2, 3), (4, -1)), 33),
    (2, ((2, 4),), 1),
    (2, ((3, 3),), 6),
    (2, ((4, 2),), 3),
    (2, ((4, 3),), 3),
    (3, ((1, 1), (2, 2), (3, 3), (5, -1)), 2),
    (3, ((1, 1), (2, 5), (5, -1)), 10),
    (3, ((1, 1), (2, 6)), 12),
    (3, ((1, 2), (2, 1), (3, 4)), 3),
    (3, ((1, 2), (2, 4), (3, 1)), 3),
    (3, ((1, 3), (2, 2), (3, 3)), 10),
    (3, ((1, 3), (2, 5)), 44),
    (3, ((2, 2), (4, 2)), 8),
    (3, ((2, 5), (4, -1)), 96),
)
ELEMENTARY = (
    ((1, -2), (2, 2)),
    ((1, -1), (2, 5)),
    ((1, 1), (3, -1), (4, 1)),
)
RANKS = (1, 2, 3, 4, 5, 6, 7)
# Lexicographically first emission: positions, correction, moved frame,
# missing origin, missing target, paying uses, other-edge delta.
WITNESS = (5760, 6924, 6, 429, 429, 575, 1, ((1, -1), (2, 3), (4, -1)))
# Every frame from 326 through 635 except these seven has 1,841 dirty
# failures whose first missing edge lands on frame 1.
HEAVY_GAPS = (507, 519, 520, 521, 522, 523, 524)
HEAVY = tuple((origin, 1) for origin in range(326, 636) if origin not in HEAVY_GAPS)
STATE = {}


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Spy:
    """First missing lookup in the published route table."""

    def __init__(self, base):
        self.base = base
        self.miss = None

    def get(self, key, default=None):
        if key in self.base:
            return self.base[key]
        if self.miss is None:
            self.miss = key
        return default


def clean(counter):
    return Counter({rank: count for rank, count in counter.items() if count})


def strict_loss(delta):
    """Positive by nonnegative terms or by repeated strict rank splits.

    This is the #6923 test. A negative rank that is not a sum of two or more
    positive parts returns False: the search found no split certificate.
    """
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
            bits = [items[index] for index in range(len(items)) if mask >> index & 1]
            if len(bits) >= 2 and sum(bits) == rank:
                found = bits
                break
        if found is None:
            return False
        for part in found:
            pos[part] -= 1
        neg[rank] -= 1
        used_split = True


def rank_one(other, uses):
    acc = Counter({rank: count for rank, count in other})
    acc[1] += uses
    return tuple(sorted((rank, count) for rank, count in acc.items() if count))


def loss_certificate(delta):
    """Strict loss on (0, 1), or None when this package has no certificate."""
    if delta == ((1, -2), (2, 2)):
        # 2*(2^t - 1). For t > 0, 2^t > 2^0 = 1.
        return "2(2^t-1)"
    if delta == ((1, -1), (2, 5)):
        # 5*2^t - 1 > 5*1 - 1 = 4, because 2^t > 1.
        return "5*2^t-1"
    if delta == ((1, 1), (3, -1), (4, 1)):
        # 1^t + 4^t - 3^t > 0 because 4^t > 3^t and 1^t = 1.
        return "1+4^t-3^t"
    if strict_loss(delta):
        return "split"
    return None


def route_walk(records, rows, state, pos0, patch_at, patch_frame, edges, owned,
               final, supply):
    """Same hop rule as paid_histogram, optionally inserting one missing edge.

    The inserted edge is the first missing pair. Later hops may use it again.
    Its paying uses are counted separately from the published-edge histogram.
    """
    rows = rows[:]
    state = state[:]
    paid = Counter()
    added = None
    uses = 0
    first_pays = None
    get = edges.get

    def take(wire, frame, pays):
        nonlocal added, uses, first_pays
        origin = state[wire]
        if origin == frame:
            return True
        pair = (origin, frame)
        rank = get(pair)
        if rank is None:
            if added is None:
                added = pair
                first_pays = bool(pays)
            if not supply or pair != added:
                return False
            if pays:
                uses += 1
        elif pays:
            paid[rank] += 1
        state[wire] = frame
        return True

    for position in range(pos0, len(records)):
        event = records[position]
        op, dest = event[0], event[1]
        if op in ("ERASE", "INIT"):
            if dest not in owned or (op == "INIT" and rows[dest]):
                return "owned_op", added, uses, None, first_pays
            rows[dest] = 0
            state[dest] = event[2]
            continue
        if op != "ADD":
            return "opcode", added, uses, None, first_pays
        source = event[2]
        if patch_at is not None and (position == patch_at or position == patch_at + 1):
            frame = patch_frame
        else:
            frame = event[3]
        if not rows[source]:
            continue
        for wire in (dest, source):
            if not take(wire, frame, bool(rows[wire])):
                return "missing", added, uses, None, first_pays
        rows[dest] ^= rows[source]
    for dest, frame in enumerate(final):
        if dest in owned:
            if rows[dest]:
                return "owned_live", added, uses, None, first_pays
            state[dest] = frame
            continue
        if not take(dest, frame, bool(rows[dest])):
            return "missing", added, uses, None, first_pays
    if state != final:
        return "final_state", added, uses, None, first_pays
    return "emit", added, uses, paid, first_pays


def fresh_rows(width):
    return [1 << index for index in range(width)]


def patched(records, position, frame):
    out = [event[:] for event in records]
    for index in (position, position + 1):
        out[index] = out[index][:3] + [frame]
    return out


def full_walk(records, position, frame, supply):
    return route_walk(
        records, fresh_rows(STATE["width"]), STATE["start"], 0, position, frame,
        STATE["edges"], STATE["owned"], STATE["final"], supply)


def controls():
    edges = STATE["edges"]
    width = STATE["width"]
    owned = STATE["owned"]
    start = STATE["start"]
    final = STATE["final"]
    scalars = STATE["scalars"]
    base = STATE["base"]
    need(2 > 1 and 4 > 3 and 5 > 1, "integer comparisons used by the elementary losses")
    need(loss_certificate(((1, -2), (2, 2))) == "2(2^t-1)", "elementary shape drifted")
    need(loss_certificate(((1, -1), (2, 5))) == "5*2^t-1", "elementary shape drifted")
    need(loss_certificate(((1, 1), (3, -1), (4, 1))) == "1+4^t-3^t", "elementary shape drifted")
    need(strict_loss(((1, 2), (2, -1))), "2 H1 - H2 must be a strict loss")
    need(not strict_loss(predecessor.SAVING), "the published saving shape must not be called a loss")
    need(not strict_loss(()), "an empty change is not a strict loss")
    reason, added, uses, paid, first_pays = full_walk(scalars, None, None, False)
    need(reason == "emit" and added is None and uses == 0 and first_pays is None
         and paid == base, "published walk drifted")
    direct_reason, direct_paid = predecessor.paid_histogram(
        scalars, width, owned, start, final, edges)
    need(direct_reason is None and direct_paid == base, "published histogram drifted")
    compared = 0
    for left, right, changes in STATE["intervals"]:
        if compared >= 30:
            break
        fixed = predecessor.skeleton(scalars, left, right, changes, {})
        positions = predecessor.contact_positions(scalars, left, right, changes)
        prepared = lemma.walk_fixed(
            fixed, width, start, final, owned, edges, save_at=positions)
        syncs = lemma.sync_after(
            prepared, [item + 1 for item in positions], width, final, owned)
        for number, (_index, extra, frame0, dest, source) in enumerate(changes):
            if compared >= 30:
                break
            position = positions[number]
            if position not in prepared["befores"]:
                continue
            rows0, state0 = prepared["befores"][position]
            wires = predecessor.meeting_wires(rows0, ["ADD", dest, source, frame0], extra)
            cand = None
            for wire in wires:
                reach = predecessor.reachable(state0[wire], STATE["outward"])
                cand = reach if cand is None else cand & reach
            cand.discard(frame0)
            fixed_ok, fixed_overlay, fixed_paid = lemma.apply_pair(
                rows0, state0, dest, source, extra[1], extra[2], frame0, edges)
            if not fixed_ok or not cand:
                continue
            frame = min(cand)
            spy = Spy(edges)
            label, _delta = lemma.classify_frame(
                rows0, state0, dest, source, extra[1], extra[2], frame,
                fixed_overlay, fixed_paid, syncs[position + 1],
                prepared["fail_at"], prepared["fail"], spy)
            if label != "dirty_fail":
                continue
            suffix = route_walk(
                fixed, rows0, state0, position, position, frame, edges, owned, final, True)
            whole = full_walk(fixed, position, frame, True)
            bare = full_walk(fixed, position, frame, False)
            need(suffix[0] == whole[0] and suffix[1] == whole[1] == spy.miss == bare[1],
                 "suffix, full walk and classifier disagree")
            need(bare[0] == "missing", "bare walk did not stop")
            compared += 1
    need(compared == 30, "control found only " + str(compared) + " dirty failures")
    for left, right, number, frame, delta in predecessor.EMITS:
        found = False
        for ileft, iright, changes in STATE["intervals"]:
            if ileft != left or iright != right:
                continue
            fixed = predecessor.skeleton(scalars, ileft, iright, changes, {})
            positions = predecessor.contact_positions(scalars, ileft, iright, changes)
            reason, added, uses, paid, _pays = full_walk(fixed, positions[number], frame, False)
            got = predecessor.delta_of(paid, base) if reason == "emit" else None
            need(reason == "emit" and added is None and uses == 0 and got == delta,
                 "known emission drifted " + str((left, reason, got)))
            direct_reason, direct_paid = predecessor.replay_moved(
                scalars, left, right, changes, number, frame,
                width, owned, start, final, edges, STATE["expected_rows"])
            need(direct_reason is None and predecessor.delta_of(direct_paid, base) == delta,
                 "direct emission drifted")
            found = True
            break
        need(found, "known emission interval missing")
    for left, right, number, frame in predecessor.REPAIRS:
        found = False
        for ileft, iright, changes in STATE["intervals"]:
            if ileft != left or iright != right:
                continue
            fixed = predecessor.skeleton(scalars, ileft, iright, changes, {})
            positions = predecessor.contact_positions(scalars, ileft, iright, changes)
            prepared = lemma.walk_fixed(
                fixed, width, start, final, owned, edges, save_at=positions)
            syncs = lemma.sync_after(
                prepared, [item + 1 for item in positions], width, final, owned)
            position = positions[number]
            rows0, state0 = prepared["befores"][position]
            _index, extra, frame0, dest, source = changes[number]
            fixed_ok, fixed_overlay, fixed_paid = lemma.apply_pair(
                rows0, state0, dest, source, extra[1], extra[2], frame0, edges)
            need(fixed_ok, "repair control has no contact-frame pair")
            label, _delta = lemma.classify_frame(
                rows0, state0, dest, source, extra[1], extra[2], frame,
                fixed_overlay, fixed_paid, syncs[position + 1],
                prepared["fail_at"], prepared["fail"], edges)
            need(label == "repair", "repair control classified as " + str(label))
            found = True
            break
        need(found, "repair interval missing")


def work(chunk):
    edges = STATE["edges"]
    outward = STATE["outward"]
    scalars = STATE["scalars"]
    width = STATE["width"]
    owned = STATE["owned"]
    start = STATE["start"]
    final = STATE["final"]
    base = STATE["base"]
    expected_rows = STATE["expected_rows"]
    outcomes = Counter()
    pairs = Counter()
    lengths = Counter()
    shapes = Counter()
    mismatches = 0
    first_pays_count = 0
    sampled = set()
    witness = None
    for left, right, changes in chunk:
        length = len(changes)
        fixed = predecessor.skeleton(scalars, left, right, changes, {})
        positions = predecessor.contact_positions(scalars, left, right, changes)
        prepared = lemma.walk_fixed(
            fixed, width, start, final, owned, edges, save_at=positions)
        syncs = lemma.sync_after(
            prepared, [item + 1 for item in positions], width, final, owned)
        fail_at = prepared["fail_at"]
        fail = prepared["fail"]
        for number, (_index, extra, frame0, dest, source) in enumerate(changes):
            position = positions[number]
            if position not in prepared["befores"]:
                continue
            need(fixed[position][0] == "ADD" and fixed[position + 1][0] == "ADD",
                 "contact pair is not two ADDs")
            need(fixed[position + 1][1] == extra[1] and fixed[position + 1][2] == extra[2],
                 "correction operands moved")
            rows0, state0 = prepared["befores"][position]
            wires = predecessor.meeting_wires(rows0, ["ADD", dest, source, frame0], extra)
            need(wires, "a long correction is dead at the meeting")
            cand = None
            for wire in wires:
                reach = predecessor.reachable(state0[wire], outward)
                cand = reach if cand is None else cand & reach
            cand.discard(frame0)
            fixed_ok, fixed_overlay, fixed_paid = lemma.apply_pair(
                rows0, state0, dest, source, extra[1], extra[2], frame0, edges)
            if not fixed_ok:
                continue
            nxt = syncs[position + 1]
            for frame in cand:
                spy = Spy(edges)
                label, _delta = lemma.classify_frame(
                    rows0, state0, dest, source, extra[1], extra[2], frame,
                    fixed_overlay, fixed_paid, nxt, fail_at, fail, spy)
                if label != "dirty_fail":
                    continue
                reason, added, uses, _paid, first_pays = route_walk(
                    fixed, rows0, state0, position, position, frame,
                    edges, owned, final, True)
                if spy.miss is None or added != spy.miss:
                    mismatches += 1
                outcomes[reason] += 1
                pairs[added] += 1
                lengths[length] += 1
                if first_pays:
                    first_pays_count += 1
                if reason == "missing":
                    if length not in sampled:
                        sampled.add(length)
                        enlarged = dict(edges)
                        enlarged[added] = 1
                        sample_reason, _sample_paid = predecessor.paid_histogram(
                            patched(fixed, position, frame), width, owned, start, final, enlarged)
                        need(sample_reason == "missing_edge",
                             "later-missing sample emitted at length " + str(length))
                    continue
                need(reason == "emit", "dirty failure ended as " + str(reason))
                whole_reason, whole_added, whole_uses, whole_paid, whole_pays = full_walk(
                    fixed, position, frame, True)
                need((whole_reason, whole_added, whole_uses, whole_pays) == (
                    "emit", added, uses, first_pays), "full walk disagrees with the suffix")
                need(uses >= 1 and first_pays is True, "an emission did not pay the added route")
                other = predecessor.delta_of(whole_paid, base)
                shapes[(uses, other)] += 1
                paid_by_rank = {}
                records = patched(fixed, position, frame)
                need(predecessor.endpoint_ok(records, width, owned, expected_rows),
                     "added route changed the scalar endpoint")
                for rank in RANKS:
                    enlarged = dict(edges)
                    enlarged[added] = rank
                    rank_reason, rank_paid = predecessor.paid_histogram(
                        records, width, owned, start, final, enlarged)
                    expect = Counter(whole_paid)
                    expect[rank] += uses
                    need(rank_reason is None and rank_paid == expect,
                         "independent histogram mismatch at rank " + str(rank))
                    paid_by_rank[rank] = rank_paid
                for rank in RANKS[1:]:
                    need(predecessor.delta_of(paid_by_rank[rank], paid_by_rank[1]) == (
                        (1, -uses), (rank, uses)), "rank shift is not a pure bin move")
                candidate = (left, right, number, frame, added[0], added[1], uses, other)
                if witness is None or candidate < witness:
                    witness = candidate
    return {
        "outcomes": outcomes,
        "pairs": pairs,
        "lengths": lengths,
        "shapes": shapes,
        "mismatches": mismatches,
        "first_pays": first_pays_count,
        "sampled": sampled,
        "witness": witness,
    }


def certify(shapes):
    savings = 0
    certificates = Counter()
    for (uses, other), count in shapes.items():
        delta = rank_one(other, uses)
        kind = loss_certificate(delta)
        need(kind is not None, "no loss certificate for " + str((uses, other, delta)))
        need(uses >= 1, "emission did not use the added route")
        certificates[kind] += count
        # A higher rank replaces uses jobs of rank 1 by uses jobs of that rank.
        # r^t > 1^t for r > 1 and t in (0, 1), so the moment stays positive.
    need(sum(certificates.values()) == EMITTED, "certificate count drifted")
    return savings, certificates


def main():
    selected = json.loads((ROOT / "certificates" / "selected-result.json").read_text())
    need(selected["kappa"] == SELECTED_KAPPA, "selected kappa changed")
    word, paths, local = predecessor.load_pinned()
    published = {int(rank): count for rank, count in local["stats"]["paid"].items()}
    need(published == predecessor.EXPECTED["base_paid"], "LOCAL-RESULT paid histogram drifted")
    edges, outward, _frames = predecessor.load_edges(paths)
    scalars = [event[:] for event in word["records"] if event[0] not in ("Q", "ZERO_Q")]
    width = len(word["start"])
    owned = set(word["owned"])
    start = word["start"][:]
    final = word["final"][:]
    expected_rows = predecessor.expected_rows(width, owned)
    reason, base = predecessor.paid_histogram(scalars, width, owned, start, final, edges)
    need(reason is None and base == Counter(published), "published word does not match its histogram")
    intervals = predecessor.intervals_of(scalars, minimum=5)
    need(len(intervals) == predecessor.LONG_COUNTS["intervals"], "interval count changed")
    need(predecessor.LONG_COUNTS["dirty_fail"] == DIRTY, "predecessor dirty count changed")
    STATE.update({
        "edges": edges, "outward": outward, "scalars": scalars, "width": width,
        "owned": owned, "start": start, "final": final, "base": base,
        "intervals": intervals, "expected_rows": expected_rows,
    })
    controls()
    chunks = [intervals[index:index + 20] for index in range(0, len(intervals), 20)]
    outcomes = Counter()
    pairs = Counter()
    lengths = Counter()
    shapes = Counter()
    mismatches = 0
    first_pays = 0
    sampled = set()
    witness = None
    ctx = get_context("fork")
    with ctx.Pool(4) as pool:
        for part in pool.imap_unordered(work, chunks):
            outcomes.update(part["outcomes"])
            pairs.update(part["pairs"])
            lengths.update(part["lengths"])
            shapes.update(part["shapes"])
            mismatches += part["mismatches"]
            first_pays += part["first_pays"]
            sampled.update(part["sampled"])
            if part["witness"] is not None and (witness is None or part["witness"] < witness):
                witness = part["witness"]
    need(sum(outcomes.values()) == DIRTY, "dirty count changed " + str(dict(outcomes)))
    need(outcomes["missing"] == LATER_MISSING and outcomes["emit"] == EMITTED,
         "outcome split changed " + str(dict(outcomes)))
    need(mismatches == 0, "classifier and walk disagree on the first missing edge")
    need(first_pays == DIRTY, "a first missing hop did not pay")
    need(len(pairs) == DISTINCT_PAIRS, "pair count changed " + str(len(pairs)))
    need(max(pairs.values()) == MAX_MULTIPLICITY, "maximum multiplicity changed")
    lines = ["{}\t{}\t{}".format(origin, target, count)
             for (origin, target), count in sorted(pairs.items())]
    digest = sha256(("\n".join(lines) + "\n").encode()).hexdigest()
    need(digest == PAIR_SHA256, "pair table hash changed " + digest)
    need(tuple(sorted(lengths.items())) == LENGTHS, "length histogram changed " + str(dict(lengths)))
    need(sum(count for _length, count in LENGTHS) == DIRTY, "length histogram is short")
    heavy = tuple(sorted(pair for pair, count in pairs.items() if count == MAX_MULTIPLICITY))
    need(len(HEAVY) == 303 and len(HEAVY) * MAX_MULTIPLICITY == 557823,
         "heavy multiplicity arithmetic drifted")
    need(heavy == HEAVY, "maximum-multiplicity pairs changed " + str(heavy))
    got_shapes = tuple(sorted(
        (uses, other, count) for (uses, other), count in shapes.items()))
    need(got_shapes == SHAPES, "emission shapes changed " + str(got_shapes))
    need(sampled == {length for length, _count in LENGTHS},
         "a length had no later-missing replay " + str(sorted(sampled)))
    _savings, certificates = certify(shapes)
    need(certificates["split"] == 382, "split count changed " + str(certificates["split"]))
    need(sum(certificates[name] for name in ("2(2^t-1)", "5*2^t-1", "1+4^t-3^t")) == 11,
         "elementary count changed")
    need(witness == WITNESS, "witness changed " + str(witness))
    left, right, number, frame, origin, target, uses, _other = witness
    print(
        "PASS_G20_DIRTY_ONE_MOVE_ADDED_ROUTE"
        " dirty={dirty} pairs={pairs} later_missing={missing} emitted={emitted}"
        " savings=0 mismatches=0 first_hop_pays={pays}"
        " max_multiplicity={mult} pair_sha256={digest}"
        " split={split} elementary={elementary}"
        " witness={left}-{right}/{number}/{frame}/{origin}-{target}/uses{uses}"
        " no_new_kappa=true".format(
            dirty=DIRTY, pairs=DISTINCT_PAIRS, missing=LATER_MISSING, emitted=EMITTED,
            pays=first_pays, mult=MAX_MULTIPLICITY, digest=digest,
            split=certificates["split"],
            elementary=sum(certificates[name] for name in (
                "2(2^t-1)", "5*2^t-1", "1+4^t-3^t")),
            left=left, right=right, number=number, frame=frame,
            origin=origin, target=target, uses=uses))


if __name__ == "__main__":
    main()
