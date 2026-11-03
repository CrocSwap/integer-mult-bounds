#!/usr/bin/env python3
"""One ordinary-work funding inequality for the PR6353 supplier word.

The charge walk is reimplemented here. It does not import the archived
replay, the caller pricing module, or the PR6353 constructor. Checks raise
ValueError, so they stay active when Python assertions are disabled.
"""
from collections import Counter
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CALLER = ROOT / "research/balanced-query-tree/CONTROLLER.json"
SOURCE_WORD = ROOT / "research/p104-native-input-lifting/WORD.json.gz"
SUPPLIER_WORD = HERE / "sources/pr6353-WORD.json.gz"
STATUS = "PASS_ONE_ORDINARY_WORK_BOUND"
SUPPLIER_SHA256 = "0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928"
FRAME_1094 = [7, 9, 35, 66, 400]
PAID_DELTA = {1: 14, 2: -4, 3: -3, 4: 4, 5: -5}
HELPER_DELTA = {5: 1, 8: 8, 9: -9}
CHANGED_FINALS = {226: 246, 297: 246, 361: 245, 393: 246, 451: 245,
                  484: 246, 703: 1094, 707: 246, 485: 246}
LOCAL_CAP = 10**7
RAW_CAP = 10**9
PUBLISHED_RAW = 194902768
PUBLISHED_ROUTES = 5368000
PUBLISHED_LOCAL = 5496694


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_word(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def dyadic_charge(event):
    """Scalar allowance of one SCALE, ADD or COPY event."""
    coefficient = Q(event[-2])
    numerator, denominator = abs(coefficient.numerator), coefficient.denominator
    need(denominator & (denominator - 1) == 0, "Dyadic scalar coefficient")
    need(abs(coefficient) + 1 < 2**16, "Fixed scalar growth bound")
    if event[0] == "SCALE":
        need(numerator & (numerator - 1) == 0, "Dyadic unit SCALE")
        return 2 * (abs(numerator.bit_length() - denominator.bit_length()) + int(coefficient < 0))
    need(event[0] in ("ADD", "COPY"), "Scalar opcode")
    return 2 * (3 + numerator.bit_length() - 1 + numerator.bit_count() + denominator.bit_length() - 1)


def walk_charges(word):
    """Running totals in program order."""
    paid = Counter()
    scalar = 0
    open_labels = set()
    peak = 0
    lifetimes = 0
    opened = Counter()
    for event in word["program"]:
        op, role = event[0], event[1]
        need(0 <= role < word["public"] + word["owned_fields"], "Role index")
        if op == "MOVE":
            _, _, origin, destination, _private = event
            paid[abs(len(word["frames"][destination]) - len(word["frames"][origin]))] += 1
        elif op == "INIT":
            need(role >= word["public"] and role not in open_labels, "Owned initialization")
            open_labels.add(role)
            opened[role] += 1
            lifetimes += 1
            peak = max(peak, len(open_labels))
            scalar += 2
        elif op == "CLEAR":
            need(role in open_labels, "Owned erasure of an open label")
            open_labels.remove(role)
            scalar += 2
        else:
            scalar += dyadic_charge(event)
    need(not open_labels, "Every owned label is cleared")
    return paid, scalar, lifetimes, peak, opened


def bucket_charges(word):
    """The same charges, summed from separate opcode buckets."""
    moves, scalars, opens = [], [], []
    open_labels = set()
    peak = 0
    for event in word["program"]:
        op, role = event[0], event[1]
        if op == "MOVE":
            _, _, origin, destination, _private = event
            moves.append(abs(len(word["frames"][destination]) - len(word["frames"][origin])))
        elif op == "INIT":
            open_labels.add(role)
            opens.append(role)
            peak = max(peak, len(open_labels))
            scalars.append(2)
        elif op == "CLEAR":
            open_labels.remove(role)
            scalars.append(2)
        else:
            scalars.append(dyadic_charge(event))
    return Counter(moves), sum(scalars), len(opens), peak, Counter(opens)


def helper_ranks(word):
    main = set(word["live"]) | {role + 112 for role in word["live"]}
    ranks = Counter()
    for role in range(word["public"]):
        if role in main:
            continue
        initial = word["frames"][word["initial"][role]]
        final = word["frames"][word["final"][role]]
        ranks[len(final) - len(initial)] += 1
    return ranks


def inventory(word):
    sequential = walk_charges(word)
    buckets = bucket_charges(word)
    need(sequential == buckets, "Program-order and opcode-bucket charges differ")
    paid, scalar, lifetimes, peak, opened = sequential
    helpers = helper_ranks(word)
    return {
        "paid": dict(paid),
        "helpers": dict(helpers),
        "paid_calls": sum(paid.values()),
        "paid_mass": sum(rank * count for rank, count in paid.items()),
        "helper_mass": sum(rank * count for rank, count in helpers.items()),
        "helper_count": sum(helpers.values()),
        "scalar": scalar,
        "lifetimes": lifetimes,
        "peak": peak,
        "opened": dict(opened),
        "public": word["public"],
        "owned_fields": word["owned_fields"],
        "ports": len(word["ports"]),
        "live": len(word["live"]),
    }


def route_allowance(row):
    """Declared local route allowance, in ordinary operations.

    The coefficients are the caller formula: one unit per paid move, two
    normalizer units per non-main public role, two adapter units per live
    port, four units per port and four units per owned lifetime, times 1000.
    """
    normalizers = 2 * (row["public"] - 2 * row["live"])
    adapters = 2 * row["live"]
    units = (row["paid_calls"] + normalizers + adapters
             + 4 * row["ports"] + 4 * row["lifetimes"])
    return units * 1000, normalizers, adapters


def raw_bound(event_count):
    """Declared complete ordinary-work expression for this fixed caller."""
    fields = 34 * 104
    return 19 * 10**7 + 16 * 1664 + fields * event_count + fields * (26 + 1000)


def positive_difference(new, old):
    delta = Counter(new)
    delta.subtract(old)
    return {key: value for key, value in sorted(delta.items()) if value}


def bind():
    raw = SUPPLIER_WORD.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SUPPLIER_SHA256, "PR6353 word bytes")
    source = load_word(SOURCE_WORD)
    supplier = load_word(SUPPLIER_WORD)
    changed = sorted(key for key in source if supplier.get(key) != source[key])
    need(changed == ["final", "frames", "program"], "Supplier edits are final, frames and program")
    need(supplier["ports"] == source["ports"] and supplier["ports"][0] == 11, "Ports stay the PR6349 ports")
    need(supplier["frames"][:1094] == source["frames"], "Original frames stay byte-for-byte")
    need(len(supplier["frames"]) == 1095 and supplier["frames"][1094] == FRAME_1094, "Frame 1094")
    finals = {role: supplier["final"][role]
              for role in range(source["public"])
              if supplier["final"][role] != source["final"][role]}
    need(finals == CHANGED_FINALS, "Exactly nine changed output frames")
    before, after = inventory(source), inventory(supplier)
    need(positive_difference(after["paid"], before["paid"]) == PAID_DELTA, "Local paid histogram")
    need(positive_difference(after["helpers"], before["helpers"]) == HELPER_DELTA, "Local productive histogram")
    need((before["scalar"], after["scalar"]) == (127088, 128694), "Scalar allowance endpoints")
    need((before["paid_calls"], after["paid_calls"]) == (3450, 3456), "Paid call counts")
    need((before["paid_mass"], after["paid_mass"]) == (5946, 5934), "Paid rank mass")
    need((before["helper_mass"], after["helper_mass"]) == (4226, 4214), "Helper rank mass")
    need((before["lifetimes"], after["lifetimes"], after["peak"]) == (32, 41, 13), "Owned lifetimes and peak")
    need(after["helper_count"] == 562 and after["public"] == 770 and after["owned_fields"] == 29,
         "Helper count and field inventory")
    opened = positive_difference(after["opened"], before["opened"])
    need(opened == {label: 1 for label in range(770, 779)}, "Nine extra openings of labels 770-778")
    routes, normalizers, adapters = route_allowance(after)
    local = after["scalar"] + routes
    need((normalizers, adapters, routes, local) == (1124, 208, PUBLISHED_ROUTES, PUBLISHED_LOCAL),
         "Published local ordinary allowance")
    need(local < LOCAL_CAP, "Local ordinary work is strictly inside 10^7")
    caller = json.loads(CALLER.read_text(encoding="utf-8"))
    need(len(caller["events"]) == 353 and caller["roles"] == 34 and caller["stages"] == 19,
         "Fixed caller census")
    raw_total = raw_bound(len(caller["events"]))
    need(raw_total == PUBLISHED_RAW and raw_total < RAW_CAP, "Caller-sized raw bound is strictly inside 10^9")
    return {"local": local, "routes": routes, "raw": raw_total, "scalar": after["scalar"],
            "paid_calls": after["paid_calls"], "lifetimes": after["lifetimes"]}


def expect_failure(action, label):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError("Control was accepted: " + label)


def controls():
    supplier = load_word(SUPPLIER_WORD)
    source = load_word(SOURCE_WORD)
    caller = json.loads(CALLER.read_text(encoding="utf-8"))
    out = {}
    slack = LOCAL_CAP - PUBLISHED_LOCAL
    out["cap_equality"] = expect_failure(
        lambda: need(PUBLISHED_LOCAL + slack < LOCAL_CAP, "Equality is not strict"),
        "cap equality")
    supplier_length = raw_bound(len(supplier["program"]))
    out["supplier_length"] = expect_failure(
        lambda: need(supplier_length == PUBLISHED_RAW, "Supplier program length reproduces the published raw bound"),
        "supplier program length")
    need(supplier_length == 256089712 and supplier_length < RAW_CAP,
         "The longer substitution is a different number still under the cap")
    bad = json.loads(json.dumps(supplier))
    bad["final"][703] = source["final"][703]
    out["restored_rank"] = expect_failure(
        lambda: need(positive_difference(helper_ranks(bad), helper_ranks(source)) == HELPER_DELTA,
                     "Restoring frame 127 keeps the productive debit"),
        "restored helper 703")
    scale = next(event for event in supplier["program"] if event[0] == "SCALE")
    broken = json.loads(json.dumps(supplier))
    broken["program"][supplier["program"].index(scale)] = ["SCALE", scale[1], "3", scale[3]]
    out["nonunit_scale"] = expect_failure(lambda: walk_charges(broken), "non-unit SCALE")
    need(raw_bound(len(caller["events"])) == PUBLISHED_RAW, "Control setup still sees the caller")
    return out


def main():
    result = bind()
    rejected = controls()
    need(set(rejected) == {"cap_equality", "supplier_length", "restored_rank", "nonunit_scale"},
         "All four controls rejected")
    print(STATUS)
    print("local", result["local"], "routes", result["routes"], "raw", result["raw"])


if __name__ == "__main__":
    main()
