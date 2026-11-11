#!/usr/bin/env python3
"""Both missing edges of each still-rejected dirty one-move G20 word.

The word and the dirty class are the merged #6923 contract. The first missing
edge is the edge inserted by open #7074. This file inserts that edge and the
next missing edge, both at rank 1, and decides whether any still-rejected word
becomes a strict saving. It does not import construct.py. Checks raise, so
optimization does not disable them.
"""

from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from multiprocessing import get_context
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]
PREDECESSOR = ROOT / "research" / "g20-length5plus-one-move"
_SPEC = spec_from_file_location("g20_length5plus_one_move_verify", PREDECESSOR / "verify.py")
predecessor = module_from_spec(_SPEC)
_SPEC.loader.exec_module(predecessor)
lemma = predecessor.lemma

DIRTY = 686779
LATER_MISSING = 686386
ONE_EMIT = 393
DISTINCT_PAIRS = 22709
THIRD_MISSING = 673425
SPLIT_LOSS = 12953
ELEMENTARY_LOSS = 5
SIGN_CHANGE = 3
PAIR_SHA256 = "8f38eb2f6e526ede87a62c1fc88c35fd5d3ba87a16f755df690a76cea5a68494"
SHAPE_SHA256 = "a185cc64ee40e0a746eb28e478d2f6e6c976833eb97fd43b453a4896441f1011"
FINGERPRINT = "461771548bef726d3739201450ffd2acd372e654bd14d6449bcee7ea79ac59ef"
SELECTED = "363005817/100000000000"
# Lexicographically first still-rejected word, in scalar-position order.
WITNESS = (
    1003, 8891, 0, 326, 326, 1, 591, 553, "missing", 3, 1, True, 12,
    583, 60, 583, 87, 1,
)
THIRD_EDGE = (467, 396)
# The four emission shapes the rank-split search does not settle.
UNCLASSIFIED = (
    (1, 1, ((1, -1), (2, 4), (3, -1)), 3),
    (1, 1, ((1, 1), (2, 3), (4, -1), (5, -1)), 3),
    (2, 1, ((1, 3), (2, 2), (3, -2)), 1),
    (2, 1, ((1, 3), (2, 3), (3, -1), (5, -1)), 1),
)
SIGN_DELTA = ((1, 1), (2, 3), (4, -1), (5, -1))
# Lexicographically first sign-changing emission. Not the #6923 repair on this
# interval, which moves the same correction to frame 358.
SIGN_WORD = (
    5661, 7047, 8, 360, 360, 358, 360, 131, 1, 1, 17, 52, 6, 179, 6, 593,
)
STATE = {}


def need(ok, message):
    if not ok:
        raise ValueError(message)


class Spy:
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


def strict_saving(delta):
    """Certificate that sum c_r r^t < 0 on (0, 1), or False if this search fails."""
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
        if not pos:
            return bool(neg) or used_split
        rank = min(pos)
        items = []
        for part, count in neg.items():
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
            neg[part] -= 1
        pos[rank] -= 1
        used_split = True


def certificate(delta):
    if delta == ():
        return "zero"
    if delta and all(count < 0 for _rank, count in delta):
        return "negative"
    loss = strict_loss(delta)
    saving = strict_saving(delta)
    if loss and saving:
        return "both"
    if loss:
        return "loss"
    if saving:
        return "saving"
    return "unclassified"


def positive_by_rewrite(delta, depth=0):
    """Strict loss by subadditive rewrites. False means this search found none."""
    acc = Counter({rank: count for rank, count in delta if count})
    if not acc:
        return False
    if all(count > 0 for count in acc.values()):
        return True
    if acc[1] < 0 and all(count > 0 for rank, count in acc.items() if rank != 1):
        higher = sum(count for rank, count in acc.items() if rank > 1)
        if higher > -acc[1]:
            return True
    if depth > 6:
        return False
    for rank, count in list(acc.items()):
        if count >= 0 or rank < 2:
            continue
        for left in range(1, rank):
            right = rank - left
            if right < left:
                break
            nxt = Counter(acc)
            nxt[rank] += 1
            nxt[left] -= 1
            nxt[right] -= 1
            packed = tuple(sorted((item, value) for item, value in nxt.items() if value))
            if positive_by_rewrite(packed, depth + 1):
                return True
    return False


def sign_change_controls():
    """Shape B is positive at 1/2 and negative at 4/5. Both comparisons are integral."""
    # 3*sqrt(2) > 1 because 18 > 1, so 3*sqrt(2) - 1 > 0.
    need(18 > 1, "3*sqrt(2) is not above 1")
    # (3*sqrt(2) - 1)^2 = 19 - 6*sqrt(2) > 5 iff 14 > 6*sqrt(2) iff 196 > 72.
    need(14 * 14 > 36 * 2, "half-exponent lower bound failed")
    # 2^(4/5) <= 35/20, 4^(4/5) >= 60/20, 5^(4/5) >= 72/20.
    need(35 ** 5 >= 16 * 20 ** 5, "upper bound for 2^(4/5) failed")
    need(60 ** 5 <= 256 * 20 ** 5, "lower bound for 4^(4/5) failed")
    need(72 ** 5 <= 625 * 20 ** 5, "lower bound for 5^(4/5) failed")
    need(20 + 3 * 35 < 60 + 72, "shape B is not negative at 4/5")


def route_walk(records, rows, state, pos0, patch_at, patch_frame, edges, owned, final):
    """Published hop rule, inserting up to two missing edges at rank 1.

    The first inserted pair is the edge #7074 adds. The second is the edge
    that rejects that one-edge walk. A third distinct missing pair rejects.
    `paid` counts published edges only.
    """
    rows = rows[:]
    state = state[:]
    paid = Counter()
    inserted = []
    slot_of = {}
    uses = [0, 0]
    first_pays = None
    second_pays = None
    rejected = None
    get = edges.get

    def take(wire, frame, pays):
        nonlocal first_pays, second_pays, rejected
        origin = state[wire]
        if origin == frame:
            return True
        pair = (origin, frame)
        rank = get(pair)
        if rank is None:
            slot = slot_of.get(pair)
            if slot is None:
                if len(inserted) >= 2:
                    rejected = pair
                    return False
                slot = len(inserted)
                inserted.append(pair)
                slot_of[pair] = slot
                if slot == 0:
                    first_pays = bool(pays)
                else:
                    second_pays = bool(pays)
            if pays:
                uses[slot] += 1
        elif pays:
            paid[rank] += 1
        state[wire] = frame
        return True

    for position in range(pos0, len(records)):
        event = records[position]
        op, dest = event[0], event[1]
        if op in ("ERASE", "INIT"):
            if dest not in owned or (op == "INIT" and rows[dest]):
                return "owned_op", inserted, uses, paid, first_pays, second_pays, rejected
            rows[dest] = 0
            state[dest] = event[2]
            continue
        if op != "ADD":
            return "opcode", inserted, uses, paid, first_pays, second_pays, rejected
        source = event[2]
        if patch_at is not None and (position == patch_at or position == patch_at + 1):
            frame = patch_frame
        else:
            frame = event[3]
        if not rows[source]:
            continue
        for wire in (dest, source):
            if not take(wire, frame, bool(rows[wire])):
                return "missing", inserted, uses, paid, first_pays, second_pays, rejected
        rows[dest] ^= rows[source]
    for dest, frame in enumerate(final):
        if dest in owned:
            if rows[dest]:
                return "owned_live", inserted, uses, paid, first_pays, second_pays, rejected
            state[dest] = frame
            continue
        if not take(dest, frame, bool(rows[dest])):
            return "missing", inserted, uses, paid, first_pays, second_pays, rejected
    if state != final:
        return "final_state", inserted, uses, paid, first_pays, second_pays, rejected
    return "emit", inserted, uses, paid, first_pays, second_pays, rejected


def fresh_rows(width):
    return [1 << index for index in range(width)]


def patched(records, position, frame):
    out = [event[:] for event in records]
    for index in (position, position + 1):
        out[index] = out[index][:3] + [frame]
    return out


def fold(acc, rec):
    digest = sha256(repr(rec).encode()).digest()
    return bytes(left ^ right for left, right in zip(acc, digest))


def work(chunk):
    edges = STATE["edges"]
    outward = STATE["outward"]
    scalars = STATE["scalars"]
    width = STATE["width"]
    owned = STATE["owned"]
    start = STATE["start"]
    final = STATE["final"]
    base = STATE["base"]
    pairs = Counter()
    lengths = Counter()
    one_emit = 0
    still = 0
    outcomes = Counter()
    certificates = Counter()
    shapes = Counter()
    mismatches = 0
    walk_gaps = 0
    hist_gaps = 0
    first_pays_count = 0
    fingerprint = bytes(32)
    witness = None
    saving = None
    sign_word = None
    by_length = {}
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
        for number, (index, extra, frame0, dest, source) in enumerate(changes):
            position = positions[number]
            if position not in prepared["befores"]:
                continue
            rows0, state0 = prepared["befores"][position]
            wires = predecessor.meeting_wires(rows0, ["ADD", dest, source, frame0], extra)
            cand = None
            for wire in wires:
                reach = predecessor.reachable(state0[wire], outward)
                cand = reach if cand is None else cand & reach
            if cand is None:
                continue
            cand = set(cand)
            cand.discard(frame0)
            fixed_ok, fixed_overlay, fixed_paid = lemma.apply_pair(
                rows0, state0, dest, source, extra[1], extra[2], frame0, edges)
            if not fixed_ok or not cand:
                continue
            nxt = syncs[position + 1]
            for frame in cand:
                spy = Spy(edges)
                label, _delta = lemma.classify_frame(
                    rows0, state0, dest, source, extra[1], extra[2], frame,
                    fixed_overlay, fixed_paid, nxt, fail_at, fail, spy)
                if label != "dirty_fail":
                    continue
                reason, inserted, uses, paid, first_pays, second_pays, rejected = route_walk(
                    fixed, rows0, state0, position, position, frame,
                    edges, owned, final)
                if not inserted or inserted[0] != spy.miss:
                    mismatches += 1
                    continue
                pairs[inserted[0]] += 1
                lengths[length] += 1
                if first_pays:
                    first_pays_count += 1
                if reason == "emit" and len(inserted) == 1:
                    one_emit += 1
                    continue
                still += 1
                second = inserted[1] if len(inserted) >= 2 else None
                third = rejected
                if reason == "emit" and second is not None:
                    kind_name = "emit"
                    full_reason, full_inserted, full_uses, full_paid, _fp, _sp, full_rejected = route_walk(
                        fixed, fresh_rows(width), start, 0, position, frame, edges, owned, final)
                    if (full_reason, full_inserted, tuple(full_uses), full_rejected) != (
                            reason, inserted, tuple(uses), rejected):
                        walk_gaps += 1
                    records = patched(fixed, position, frame)
                    enlarged = dict(edges)
                    enlarged[inserted[0]] = 1
                    enlarged[second] = 1
                    hist_reason, hist_paid = predecessor.paid_histogram(
                        records, width, owned, start, final, enlarged)
                    expect = clean(Counter(full_paid))
                    expect[1] += full_uses[0] + full_uses[1]
                    expect = clean(expect)
                    if hist_reason is not None or hist_paid != expect:
                        hist_gaps += 1
                    other = predecessor.delta_of(full_paid, base)
                    total = Counter({rank: count for rank, count in other})
                    total[1] += full_uses[0] + full_uses[1]
                    delta = tuple(sorted(
                        (rank, count) for rank, count in total.items() if count))
                    kind = certificate(delta)
                    certificates[kind] += 1
                    shapes[(full_uses[0], full_uses[1], delta, kind)] += 1
                    if kind in ("saving", "negative"):
                        candidate = (left, right, number, frame, inserted[0], second, delta, kind)
                        if saving is None or candidate < saving:
                            saving = candidate
                    if delta == SIGN_DELTA:
                        sign_candidate = (
                            left, right, number, frame,
                            inserted[0][0], inserted[0][1], second[0], second[1],
                            full_uses[0], full_uses[1], length,
                            scalars[left][1], scalars[left][2], extra[1], extra[2], frame0,
                        )
                        if sign_word is None or sign_candidate < sign_word:
                            sign_word = sign_candidate
                else:
                    kind_name = reason
                    outcomes[reason] += 1
                rec = (
                    left, right, number, frame,
                    inserted[0][0], inserted[0][1],
                    None if second is None else second[0],
                    None if second is None else second[1],
                    None if third is None else third[0],
                    None if third is None else third[1],
                    kind_name,
                )
                fingerprint = fold(fingerprint, rec)
                candidate = (
                    left, right, number, frame,
                    inserted[0][0], inserted[0][1],
                    None if second is None else second[0],
                    None if second is None else second[1],
                    kind_name, uses[0], uses[1], bool(second_pays), length,
                    scalars[left][1], scalars[left][2],
                    extra[1], extra[2], frame0,
                )
                if witness is None or candidate < witness:
                    witness = candidate
                if length not in by_length or candidate < by_length[length]:
                    by_length[length] = candidate
    return {
        "pairs": pairs,
        "lengths": lengths,
        "one_emit": one_emit,
        "still": still,
        "outcomes": outcomes,
        "certificates": certificates,
        "shapes": shapes,
        "mismatches": mismatches,
        "walk_gaps": walk_gaps,
        "hist_gaps": hist_gaps,
        "first_pays": first_pays_count,
        "fingerprint": fingerprint,
        "witness": witness,
        "saving": saving,
        "sign_word": sign_word,
        "by_length": by_length,
    }


def replay(witness):
    """Independent full-word replay of the lexicographically first word."""
    left, right, number, frame = witness[:4]
    edges = STATE["edges"]
    scalars = STATE["scalars"]
    width = STATE["width"]
    owned = STATE["owned"]
    start = STATE["start"]
    final = STATE["final"]
    base = STATE["base"]
    found = None
    for ileft, iright, changes in STATE["intervals"]:
        if ileft == left and iright == right:
            found = changes
            break
    need(found is not None, "witness interval missing")
    fixed = predecessor.skeleton(scalars, left, right, found, {})
    positions = predecessor.contact_positions(scalars, left, right, found)
    position = positions[number]
    prepared = lemma.walk_fixed(
        fixed, width, start, final, owned, edges, save_at=positions)
    rows0, state0 = prepared["befores"][position]
    suffix = route_walk(
        fixed, rows0, state0, position, position, frame, edges, owned, final)
    whole = route_walk(
        fixed, fresh_rows(width), start, 0, position, frame, edges, owned, final)
    need((suffix[0], suffix[1], tuple(suffix[2]), suffix[4], suffix[5], suffix[6]) == (
        whole[0], whole[1], tuple(whole[2]), whole[4], whole[5], whole[6]),
         "suffix and full walk disagree on the inserted edges")
    reason, inserted, uses, paid, first_pays, second_pays, rejected = whole
    records = patched(fixed, position, frame)
    need(predecessor.endpoint_ok(records, width, owned, STATE["expected_rows"]),
         "moved endpoint changed")
    one = dict(edges)
    one[inserted[0]] = 1
    one_reason, one_paid = predecessor.paid_histogram(
        records, width, owned, start, final, one)
    need(one_reason == "missing_edge" and one_paid is None, "one edge emitted")
    both = dict(edges)
    both[inserted[0]] = 1
    both[inserted[1]] = 1
    both_reason, both_paid = predecessor.paid_histogram(
        records, width, owned, start, final, both)
    if reason == "emit":
        expect = clean(Counter(paid))
        expect[1] += uses[0] + uses[1]
        expect = clean(expect)
        need(both_reason is None and both_paid == expect, "histogram mismatch")
        delta = predecessor.delta_of(both_paid, base)
    else:
        need(both_reason == "missing_edge" and both_paid is None, "both edges emitted unexpectedly")
        delta = None
    if reason != "emit":
        high = dict(edges)
        high[inserted[0]] = 7
        high[inserted[1]] = 7
        high_reason, high_paid = predecessor.paid_histogram(
            records, width, owned, start, final, high)
        need(high_reason == "missing_edge" and high_paid is None,
             "a higher rank emitted a rejected word")
    return {
        "first": inserted[0],
        "second": inserted[1],
        "third": rejected,
        "reason": reason,
        "uses": (uses[0], uses[1]),
        "first_pays": first_pays,
        "second_pays": second_pays,
        "delta": delta,
    }


def rank_shift(word):
    """Raising the first added edge from rank 1 to 7 moves its paying uses."""
    left, right, number, frame = word[:4]
    first = (word[4], word[5])
    second = (word[6], word[7])
    uses0 = word[8]
    edges = STATE["edges"]
    found = None
    for ileft, iright, changes in STATE["intervals"]:
        if ileft == left and iright == right:
            found = changes
            break
    need(found is not None, "sign-changing interval missing")
    fixed = predecessor.skeleton(STATE["scalars"], left, right, found, {})
    position = predecessor.contact_positions(STATE["scalars"], left, right, found)[number]
    records = patched(fixed, position, frame)
    width, owned, start, final = STATE["width"], STATE["owned"], STATE["start"], STATE["final"]
    low = dict(edges)
    low[first] = 1
    low[second] = 1
    high = dict(edges)
    high[first] = 7
    high[second] = 1
    low_reason, low_paid = predecessor.paid_histogram(records, width, owned, start, final, low)
    high_reason, high_paid = predecessor.paid_histogram(records, width, owned, start, final, high)
    need(low_reason is None and high_reason is None, "rank shift did not emit")
    expect = Counter(low_paid)
    expect[1] -= uses0
    expect[7] += uses0
    need(clean(expect) == high_paid, "rank shift is not a pure bin move")


def main():
    selected = json.loads((ROOT / "certificates" / "selected-result.json").read_text())
    need(selected["kappa"] == SELECTED, "selected kappa changed")
    word, paths, local = predecessor.load_pinned()
    published = {int(rank): count for rank, count in local["stats"]["paid"].items()}
    need(published == predecessor.EXPECTED["base_paid"], "paid histogram drifted")
    edges, outward, _frames = predecessor.load_edges(paths)
    scalars = [event[:] for event in word["records"] if event[0] not in ("Q", "ZERO_Q")]
    width = len(word["start"])
    owned = set(word["owned"])
    start = word["start"][:]
    final = word["final"][:]
    expected_rows = predecessor.expected_rows(width, owned)
    reason, base = predecessor.paid_histogram(scalars, width, owned, start, final, edges)
    need(reason is None and base == Counter(published), "published walk drifted")
    intervals = predecessor.intervals_of(scalars, minimum=5)
    need(len(intervals) == predecessor.LONG_COUNTS["intervals"], "interval count changed")
    need(strict_loss(((1, 2), (2, -1))) and not strict_loss(predecessor.SAVING), "loss control")
    # 2^t - 2 < 0 on (0, 1). The published saving shape is not always found by this split.
    need(strict_saving(((2, 1), (1, -2))) and not strict_saving(((1, 2), (2, -1))), "saving control")
    need(not strict_loss(()) and not strict_saving(()), "zero control")
    sign_change_controls()
    need(positive_by_rewrite(UNCLASSIFIED[0][2]), "shape A is not an elementary loss")
    need(not positive_by_rewrite(UNCLASSIFIED[1][2]), "shape B must stay unclassified by the rewrite")
    need(positive_by_rewrite(UNCLASSIFIED[2][2]), "shape C is not an elementary loss")
    need(positive_by_rewrite(UNCLASSIFIED[3][2]), "shape D is not an elementary loss")
    for _uses0, _uses1, delta, _count in UNCLASSIFIED:
        need(certificate(delta) == "unclassified", "special shape drifted " + str(delta))
    STATE.update({
        "edges": edges, "outward": outward, "scalars": scalars, "width": width,
        "owned": owned, "start": start, "final": final, "base": base,
        "intervals": intervals, "expected_rows": expected_rows,
    })
    chunks = [intervals[index:index + 20] for index in range(0, len(intervals), 20)]
    pairs = Counter()
    lengths = Counter()
    one_emit = 0
    still = 0
    outcomes = Counter()
    certificates = Counter()
    shapes = Counter()
    mismatches = 0
    walk_gaps = 0
    hist_gaps = 0
    first_pays = 0
    fingerprint = bytes(32)
    witness = None
    saving = None
    sign_word = None
    by_length = {}
    ctx = get_context("fork")
    done = 0
    with ctx.Pool(4) as pool:
        for part in pool.imap_unordered(work, chunks):
            pairs.update(part["pairs"])
            lengths.update(part["lengths"])
            one_emit += part["one_emit"]
            still += part["still"]
            outcomes.update(part["outcomes"])
            certificates.update(part["certificates"])
            shapes.update(part["shapes"])
            mismatches += part["mismatches"]
            walk_gaps += part["walk_gaps"]
            hist_gaps += part["hist_gaps"]
            first_pays += part["first_pays"]
            for length, candidate in part["by_length"].items():
                if length not in by_length or candidate < by_length[length]:
                    by_length[length] = candidate
            fingerprint = bytes(left ^ right for left, right in zip(fingerprint, part["fingerprint"]))
            if part["witness"] is not None and (witness is None or part["witness"] < witness):
                witness = part["witness"]
            if part["saving"] is not None and (saving is None or part["saving"] < saving):
                saving = part["saving"]
            if part["sign_word"] is not None and (sign_word is None or part["sign_word"] < sign_word):
                sign_word = part["sign_word"]
            done += 1
    lines = ["{}\t{}\t{}".format(origin, target, count)
             for (origin, target), count in sorted(pairs.items())]
    digest = sha256(("\n".join(lines) + "\n").encode()).hexdigest()
    shape_lines = []
    for (uses0, uses1, delta, kind), count in sorted(shapes.items()):
        shape_lines.append("{}\t{}\t{}\t{}\t{}".format(uses0, uses1, delta, kind, count))
    shape_digest = sha256(("\n".join(shape_lines) + "\n").encode()).hexdigest()
    unclassified = tuple(sorted(
        (uses0, uses1, delta, count)
        for (uses0, uses1, delta, kind), count in shapes.items()
        if kind == "unclassified"))
    need(digest == PAIR_SHA256, "pair hash mismatch " + digest)
    need(shape_digest == SHAPE_SHA256, "shape hash mismatch " + shape_digest)
    need(fingerprint.hex() == FINGERPRINT, "fingerprint mismatch " + fingerprint.hex())
    need(one_emit == ONE_EMIT and still == LATER_MISSING, "split mismatch")
    need(len(pairs) == DISTINCT_PAIRS, "pair count mismatch")
    need(one_emit + still == DIRTY, "dirty mismatch")
    need(mismatches == 0 and walk_gaps == 0 and hist_gaps == 0, "walk mismatch")
    need(first_pays == DIRTY, "a first missing hop did not pay")
    need(outcomes == Counter({"missing": THIRD_MISSING}), "third-missing count changed")
    need(certificates == Counter({"loss": SPLIT_LOSS, "unclassified": ELEMENTARY_LOSS + SIGN_CHANGE}),
         "certificate counts changed " + str(dict(certificates)))
    need(unclassified == UNCLASSIFIED, "unclassified shapes changed " + str(unclassified))
    need(sum(count for _uses0, _uses1, _delta, count in unclassified) == ELEMENTARY_LOSS + SIGN_CHANGE,
         "special shape count drifted")
    need(witness == WITNESS, "lexicographic witness changed " + str(witness))
    need(saving is None, "a split or negative shape was called a saving")
    need(len(by_length) == 28, "length sample count changed")
    checked = replay(witness)
    need(checked["reason"] == "missing" and checked["third"] == THIRD_EDGE, "witness replay drifted")
    need(checked["first"] == (WITNESS[4], WITNESS[5]) and checked["second"] == (WITNESS[6], WITNESS[7]),
         "witness edges drifted")
    for length in sorted(by_length):
        sample = replay(by_length[length])
        need(sample["reason"] == by_length[length][8], "length sample drifted at " + str(length))
    need(sign_word is not None, "the sign-changing shape had no word")
    sign_replay = replay(sign_word)
    need(sign_replay["reason"] == "emit" and sign_replay["delta"] == SIGN_DELTA,
         "sign-changing replay drifted " + str(sign_replay))
    need(sign_replay["uses"] == (sign_word[8], sign_word[9]), "sign-changing uses drifted")
    rank_shift(sign_word)
    need(sign_word == SIGN_WORD, "sign-changing word changed " + str(sign_word))
    print(
        "PASS_G20_DIRTY_SECOND_EDGE"
        " still={still} third_missing={third} split_loss={loss}"
        " elementary_loss={elementary} sign_change={sign} savings=0"
        " witness={left}-{right}/{number}/{frame}/{first}/{second}/third={third_edge}"
        " no_new_kappa=true".format(
            still=LATER_MISSING, third=THIRD_MISSING, loss=SPLIT_LOSS,
            elementary=ELEMENTARY_LOSS, sign=SIGN_CHANGE,
            left=WITNESS[0], right=WITNESS[1], number=WITNESS[2], frame=WITNESS[3],
            first="{}-{}".format(WITNESS[4], WITNESS[5]),
            second="{}-{}".format(WITNESS[6], WITNESS[7]),
            third_edge="{}-{}".format(*THIRD_EDGE)))


if __name__ == "__main__":
    main()
