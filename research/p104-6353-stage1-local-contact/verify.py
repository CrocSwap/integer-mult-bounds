#!/usr/bin/env python3
"""Bind one PR6353 caller stage to its declared LOCAL factors.

The fixed PR6348 caller is on canonical main. Its first LOCAL event is stage 1
on roles 0 and 1. This verifier rebuilds that stage's physical contacts from
the pinned port recipes and compares them with D_1 and D_1 Q^{-1}. It does not
import the author caller, physical checker, or PR6353 constructor.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
"""
from hashlib import sha256
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
DIMENSION = 161
STAGE = 1
WORD_SHA256 = "0c83c1f1dee8c9442558719510a61b89f38c2dbfc8fb565ba035660d2a68d928"
WORD_BLOB = "03ea7690285d4cda72815f962d5710ab96e08490"
SOURCE_HEAD = "db2a20bc50bc7a8a4db931af85ce7f012ae7c3c3"
CHANGED_FINALS = {
    226: 246, 297: 246, 361: 245, 393: 246, 451: 245,
    484: 246, 485: 246, 703: 1094, 707: 246,
}
FRAME_1094 = [7, 9, 35, 66, 400]
MOVE_1094 = ["MOVE", 703, 712, 1094, False]
PINS = {
    "research/balanced-query-tree/CONTROLLER.json":
        "6fd67eaabe659956d6694471d3fd7d2824c0a4a79cf3b8f22922f7189b11b91f",
    "research/balanced-query-tree/physical.py":
        "3288421e7c3ca7116c96996984983ff44e2b601e38f808c4b46e518fbda9851b",
    "research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json":
        "c5916ff312678f12aba403847643fbbc29f643acec60bdf836fa56cd3e8251fa",
    "research/p104-native-input-lifting/WORD.json.gz":
        "1415a62059ed62d0b4657db91f7ec01b23c117f5f2744746d93c880bd777be92",
}
# Frozen from the first successful independent run. A formula drift fails closed.
CONTACT_SHA256 = "ac69d4f31e86ae776ee15457d2362bf06b0daf777a7fe80b300c31632ece3498"


def need(ok, message):
    if not ok:
        raise ValueError(message)


def load_bytes(path):
    data = Path(path).read_bytes()
    expect = PINS.get(path)
    if expect is not None:
        need(sha256(data).hexdigest() == expect, "Pinned bytes changed: " + path)
    return data


def norm(terms):
    totals = {}
    for axis, value in terms:
        if axis:
            totals[axis] = totals.get(axis, 0) + value
    return tuple(sorted((axis, value % 4) for axis, value in totals.items() if value % 4))


def act(columns, value):
    result = 0
    while value:
        low = value & -value
        result ^= columns[low.bit_length() - 1]
        value ^= low
    return result


def polynomial(terms, dimension):
    linear = [0] * dimension
    quadratic = [0] * dimension
    for axis, value in terms:
        support = [i for i in range(dimension) if axis >> i & 1]
        for i in support:
            linear[i] = (linear[i] + value) % 4
            if value % 2:
                for j in support:
                    if i < j:
                        quadratic[i] ^= 1 << j
    return tuple(linear), tuple(quadratic)


def contact(old, new, route, dimension):
    """Route old onto new up to one even translation, then check the inverse."""
    moved = norm((act(route, axis), value) for axis, value in old)
    left, right = polynomial(moved, dimension), polynomial(new, dimension)
    need(left[1] == right[1], "Contact quadratic forms differ")
    delta = tuple((right_i - left_i) % 4 for left_i, right_i in zip(left[0], right[0]))
    need(all(value in (0, 2) for value in delta), "Contact linear phase is not an even translation")
    shift = sum((value // 2) << i for i, value in enumerate(delta))
    forwarded = polynomial(norm([*moved, (shift, 2)]), dimension)
    need(forwarded == right, "Forward contact phase differs")
    inverse_shift = act(route, shift)
    inverse = norm([(act(route, axis), value) for axis, value in new] + [(inverse_shift, 2)])
    need(polynomial(inverse, dimension) == polynomial(old, dimension), "Inverse contact phase differs")
    return shift, inverse_shift


def axes_of(dimension):
    return tuple(1 << i for i in range(dimension))


def bind_port(q, recipe, stage, axes, corrupt=None):
    basis = list(recipe["idle_children"][0]["orthogonal_axes"][:8])
    if corrupt == "basis":
        basis[0] ^= 1
    need(all((item & q).bit_count() % 2 == 0 for item in basis), "Fresh basis meets the central port")
    need(all((a & b).bit_count() % 2 == int(i == j)
             for i, a in enumerate(basis) for j, b in enumerate(basis)),
         "Fresh basis is not orthonormal")
    swaps = [item ^ axes[9 + 8 * (stage - 1) + i] for i, item in enumerate(basis)]
    route = tuple(
        vector ^ act(swaps, sum(((vector & swap).bit_count() % 2) << i for i, swap in enumerate(swaps)))
        for vector in axes)
    need(all(act(route, route[i]) == axes[i] for i in range(len(axes))), "Route is not an involution")
    need(all((a & b).bit_count() % 2 == int(i == j)
             for i, a in enumerate(route) for j, b in enumerate(route)),
         "Route is not orthogonal")
    need(act(route, q) == q, "Route moves the central port")
    fresh = axes[9 + 8 * (stage - 1):9 + 8 * stage]
    central = axes[:9]
    raw_x = norm((axis, 1) for axis in axes[:9 + 8 * (stage - 1)])
    raw_y = norm([*raw_x, (q, -1)])
    spectator = norm((axis, 1) for axis in axes[9:9 + 8 * stage])
    entry_x, entry_y = norm([*spectator, (q, 1)]), spectator
    exit_x = norm([*spectator, *((axis, 1) for axis in central)])
    exit_y = norm([*exit_x, (q, -1)])
    out_x = norm((axis, 1) for axis in axes[:9 + 8 * stage])
    out_y = norm([*out_x, (q, -1)])
    names = (
        ("entry_x", raw_x, entry_x), ("entry_y", raw_y, entry_y),
        ("exit_x", exit_x, out_x), ("exit_y", exit_y, out_y))
    maps = {name: contact(old, new, route, len(axes)) for name, old, new in names}
    delta = norm((axis, 1) for axis in fresh)
    if corrupt == "diagonal":
        delta = tuple(item for item in delta if item[0] != fresh[0])
    for incoming, outgoing in ((raw_x, out_x), (raw_y, out_y)):
        difference = norm([*outgoing, *((axis, -value) for axis, value in incoming)])
        need(polynomial(difference, len(axes)) == polynomial(delta, len(axes)),
             "Diagonal is not D_s")
    cross = norm([*out_y, *((axis, -value) for axis, value in raw_x)])
    expect = norm([*delta, (q, -1)])
    if corrupt == "cross":
        expect = delta
    need(polynomial(cross, len(axes)) == polynomial(expect, len(axes)), "Cross term is not D_s Q^{-1}")
    need(all(value.bit_count() <= 17 for value in maps.values() for value in value),
         "Translation uses more than seventeen axes")
    return {
        "q": q,
        "fresh_axes": [axis.bit_length() - 1 for axis in fresh],
        "central_axes": [axis.bit_length() - 1 for axis in central],
        "translations": {name: [shift, inverse] for name, (shift, inverse) in maps.items()},
    }


def rejects(fn):
    try:
        fn()
    except ValueError:
        return True
    return False


def owned_boundary(program):
    labels = set(range(770, 779))
    inits, clears = set(), set()
    owned_moves = 0
    for event in program:
        if event[0] == "INIT" and event[1] in labels:
            inits.add(event[1])
        elif event[0] == "CLEAR" and event[1] in labels:
            clears.add(event[1])
        elif event[0] == "MOVE" and event[1] in labels and event[4] is True:
            owned_moves += 1
    need(inits == labels and clears == labels, "Labels 770-778 are not each opened and cleared")
    need(owned_moves > 0, "No owned transport on the new labels")
    return owned_moves


def main():
    caller = json.loads(load_bytes("research/balanced-query-tree/CONTROLLER.json"))
    phases = json.loads(load_bytes(
        "research/kappa-0023-productive-jobs/dependencies/kappa-next-regime/direct-decoder/sources/DATA-PHASES.json"))
    source = json.loads(gzip.decompress(load_bytes("research/p104-native-input-lifting/WORD.json.gz")))
    changed_bytes = (HERE / "sources/pr6353-WORD.json.gz").read_bytes()
    need(sha256(changed_bytes).hexdigest() == WORD_SHA256, "Vendored PR6353 word hash")
    changed = json.loads(gzip.decompress(changed_bytes))
    # Pin the declared physical checker as bytes only. The formulas below are rederived.
    load_bytes("research/balanced-query-tree/physical.py")

    events = caller["events"]
    local = [event for event in events if event[0] == "LOCAL"]
    need(caller["ambient_rank"] == DIMENSION and caller["stages"] == 19, "Caller ambient rank and stage count")
    need(local[0] == ["LOCAL", STAGE, 0, 1], "First LOCAL event is stage 1 on roles 0 and 1")
    need([event[1] for event in local] == list(range(1, 20)), "Nineteen LOCAL stages in order")
    need(events.index(local[0]) == 21, "Stage-1 LOCAL is caller event 21")

    need(source["ports"] == changed["ports"] and len(changed["ports"]) == 104, "PR6353 keeps the 104 source ports")
    finals = {role: changed["final"][role] for role in range(770) if changed["final"][role] != source["final"][role]}
    need(finals == CHANGED_FINALS, "Exactly the nine declared output-frame changes")
    need(changed["frames"][1094] == FRAME_1094 and changed["program"][12917] == MOVE_1094,
         "Frame 1094 and the role-703 entrance move")
    need(changed["program"][12917][4] is False, "The frame-1094 entrance move is not an owned transport")
    owned_moves = owned_boundary(changed["program"])
    need(all(event[2] < 34 and event[3] < 34 for event in local), "LOCAL roles stay inside the 34 caller fields")
    need(labels_disjoint(local), "Caller LOCAL roles are disjoint from owned labels 770-778")

    recipes = {recipe["q"]: recipe for recipe in phases["recipes"]}
    need(len(recipes) == len(phases["recipes"]), "Port phase recipes have distinct q")
    missing = [q for q in changed["ports"] if q not in recipes]
    need(not missing, "A caller port has no phase recipe")
    axes = axes_of(DIMENSION)
    records = [bind_port(q, recipes[q], STAGE, axes) for q in changed["ports"]]
    body = json.dumps(records, separators=(",", ":"), sort_keys=True).encode()
    digest = sha256(body).hexdigest()
    if CONTACT_SHA256 is not None:
        need(digest == CONTACT_SHA256, "Frozen stage-1 contact digest")
    q0 = changed["ports"][0]
    probe = recipes[q0]
    need(rejects(lambda: bind_port(q0, probe, STAGE, axes, corrupt="diagonal")), "Dropping a fresh axis must fail")
    need(rejects(lambda: bind_port(q0, probe, STAGE, axes, corrupt="cross")), "Dropping Q^{-1} must fail")
    need(rejects(lambda: bind_port(q0, probe, STAGE, axes, corrupt="basis")), "A tilted fresh basis must fail")

    result = {
        "status": "PASS_P104_6353_STAGE1_LOCAL_CONTACT",
        "source_head": SOURCE_HEAD,
        "word_blob": WORD_BLOB,
        "local_event_index": 21,
        "local_event": local[0],
        "ports": len(records),
        "contacts": 4 * len(records),
        "diagonal": "D_1",
        "cross": "D_1 Q^{-1}",
        "fresh_axes": records[0]["fresh_axes"],
        "central_axes": records[0]["central_axes"],
        "first_port": records[0]["q"],
        "first_port_translations": records[0]["translations"],
        "owned_moves_on_labels_770_778": owned_moves,
        "contact_sha256": digest,
        "not_checked": [
            "LOCAL stages 2 through 19",
            "caller endpoint phases, whole idles and central-square columns",
            "funding, compiler and outer predicates",
            "native_all_columns at widths other than this stage-1 contact",
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    print(result["status"])


def labels_disjoint(local):
    used = {role for event in local for role in event[2:4]}
    return used.isdisjoint(set(range(770, 779)))


if __name__ == "__main__":
    main()
