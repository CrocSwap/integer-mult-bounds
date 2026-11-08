"""One-hop classification of a single moved A2 correction.

Moving one correction changes the frame of the contact and that correction.
Later ADD targets stay on the contact-frame skeleton. A wire whose frame
disagrees with that skeleton is dirty. Its next live route, erasure, or final
assignment writes the same target in both words, so the wire agrees again
after that one event. Dirtiness does not spread. The moved word therefore
emits only when the contact pair and each dirty wire's one later route exist,
and every unchanged route exists.
"""

from collections import Counter


def walk_fixed(skeleton, width, start, final, owned, edges, save_at=()):
    rows = [1 << index for index in range(width)]
    state = start[:]
    paid = Counter()
    info = [None] * len(skeleton)
    fail_at = None
    fail = None
    befores = {}
    wanted = set(save_at)
    for position, event in enumerate(skeleton):
        if position in wanted:
            befores[position] = (rows[:], state[:])
        op, dest = event[0], event[1]
        if op in ("ERASE", "INIT"):
            if dest not in owned or (op == "INIT" and rows[dest]):
                fail_at = position
                fail = ("owned_op", dest)
                break
            info[position] = ("erase", dest)
            rows[dest] = 0
            state[dest] = event[2]
            continue
        if op != "ADD":
            fail_at = position
            fail = ("opcode", None)
            break
        source, frame = event[2], event[3]
        if not rows[source]:
            info[position] = ("dead",)
            continue
        dest_pays = bool(rows[dest])
        failed_on = None
        for wire in (dest, source):
            origin = state[wire]
            if origin == frame:
                continue
            rank = edges.get((origin, frame))
            if rank is None:
                failed_on = wire
                break
            if rows[wire]:
                paid[rank] += 1
            state[wire] = frame
        if failed_on is not None:
            fail_at = position
            fail = ("route", dest, source, frame, dest_pays, failed_on)
            break
        info[position] = ("add", dest, source, frame, dest_pays)
        rows[dest] ^= rows[source]
    final_rows = rows[:]
    if fail_at is None:
        for dest, frame in enumerate(final):
            if dest in owned:
                if rows[dest]:
                    fail_at = len(skeleton)
                    fail = ("owned_live", dest)
                    break
                state[dest] = frame
                continue
            origin = state[dest]
            if origin == frame:
                continue
            rank = edges.get((origin, frame))
            if rank is None:
                fail_at = len(skeleton)
                fail = ("final", dest, frame, bool(rows[dest]))
                break
            if rows[dest]:
                paid[rank] += 1
            state[dest] = frame
        if fail_at is None and state != final:
            fail_at = len(skeleton)
            fail = ("final_state", None)
    return {
        "info": info,
        "rows": None,
        "fail_at": fail_at,
        "fail": fail,
        "paid": None if fail_at is not None else paid,
        "final_rows": final_rows,
        "befores": befores,
    }


def sync_after(prepared, save_at, width, final, owned):
    """Next synchronizer of each wire strictly after selected indexes."""
    info = prepared["info"]
    fail_at = prepared["fail_at"]
    fail = prepared["fail"]
    final_rows = prepared["final_rows"]
    nxt = [("after_fail", fail_at if fail_at is not None else len(info))] * width
    if fail_at is None:
        for wire, frame in enumerate(final):
            if wire in owned:
                nxt[wire] = ("owned", len(info))
            else:
                nxt[wire] = ("route", frame, bool(final_rows[wire]), len(info))
    elif fail_at == len(info) and fail is not None and fail[0] == "final":
        _kind, dest, frame, pays = fail
        for wire in range(dest):
            if wire in owned:
                nxt[wire] = ("owned", len(info))
            else:
                nxt[wire] = ("route", final[wire], bool(final_rows[wire]), len(info))
        nxt[dest] = ("route", frame, pays, len(info))
    elif fail_at == len(info) and fail is not None and fail[0] == "owned_live":
        dest = fail[1]
        for wire in range(dest):
            if wire in owned:
                nxt[wire] = ("owned", len(info))
            else:
                nxt[wire] = ("route", final[wire], bool(final_rows[wire]), len(info))
        nxt[dest] = ("owned_live", len(info))
    elif fail_at is not None and fail_at < len(info) and fail is not None and fail[0] == "route":
        _kind, dest, source, frame, dest_pays, failed_on = fail
        nxt[dest] = ("route", frame, dest_pays, fail_at)
        if failed_on == source:
            nxt[source] = ("route", frame, True, fail_at)
    saved = {}
    wanted = set(save_at)
    for position in range(len(info) - 1, -1, -1):
        if position in wanted:
            saved[position] = nxt[:]
        item = info[position]
        if item is None or item[0] == "dead":
            continue
        if item[0] == "erase":
            nxt[item[1]] = ("erase", position)
            continue
        if item[0] != "add":
            continue
        _kind, dest, source, frame, dest_pays = item
        nxt[dest] = ("route", frame, dest_pays, position)
        nxt[source] = ("route", frame, True, position)
    return saved


def apply_pair(rows, state, dest, source, extra_dest, extra_source, frame, edges):
    overlay = {}
    paid = Counter()

    def current(wire):
        return overlay[wire] if wire in overlay else state[wire]

    def hop(wire, pays):
        origin = current(wire)
        if origin == frame:
            return True
        rank = edges.get((origin, frame))
        if rank is None:
            return False
        if pays:
            paid[rank] += 1
        overlay[wire] = frame
        return True

    row_dest = rows[dest]
    row_source = rows[source]
    if row_source:
        if not hop(dest, bool(row_dest)) or not hop(source, True):
            return False, None, None
        row_dest ^= row_source
    if extra_source == dest:
        extra_row = row_dest
    else:
        extra_row = rows[extra_source]
    if extra_row:
        if extra_dest == dest:
            extra_dest_row = row_dest
        elif extra_dest == source:
            extra_dest_row = rows[source]
        else:
            extra_dest_row = rows[extra_dest]
        if not hop(extra_dest, bool(extra_dest_row)) or not hop(extra_source, True):
            return False, None, None
    return True, overlay, paid


def frame_of(overlay, state, wire):
    return overlay[wire] if wire in overlay else state[wire]


def classify_frame(rows, state, dest, source, extra_dest, extra_source, frame,
                   fixed_overlay, fixed_paid, nxt, fail_at, fail, edges):
    ok, overlay, paid = apply_pair(
        rows, state, dest, source, extra_dest, extra_source, frame, edges)
    if not ok:
        return "pair_fail", None
    touched = set(overlay) | set(fixed_overlay)
    dirty = []
    for wire in touched:
        moved = frame_of(overlay, state, wire)
        fixed = frame_of(fixed_overlay, state, wire)
        if moved != fixed:
            dirty.append((wire, moved, fixed))
    delta = Counter(paid)
    delta.subtract(fixed_paid)
    active = {wire for wire, _moved, _fixed in dirty}
    checks = []
    for wire, moved, fixed in dirty:
        kind = nxt[wire]
        position = kind[-1]
        checks.append((position, wire, moved, fixed, kind))
    checks.sort()
    for position, wire, moved, fixed, kind in checks:
        if fail_at is not None and position > fail_at:
            return ("repair" if fail is not None and fail[0] in ("route", "final")
                    and _failure_wire(fail) in active else "clean_fail"), None
        name = kind[0]
        if name in ("erase", "owned", "owned_live", "after_fail"):
            if name == "owned_live":
                return "clean_fail", None
            if name == "after_fail":
                return "clean_fail", None
            active.discard(wire)
            continue
        if name != "route":
            return "repair", None
        _name, target, pays, _position = kind
        if moved != target:
            rank = edges.get((moved, target))
            if rank is None:
                return "dirty_fail", None
            if pays:
                delta[rank] += 1
        if fixed != target:
            rank = edges.get((fixed, target))
            if rank is None:
                return "repair", None
            if pays:
                delta[rank] -= 1
        active.discard(wire)
        if fail_at is not None and position == fail_at and _failure_wire(fail) == wire:
            if active:
                return "repair", None
            return "repair", None
    if fail_at is None:
        return "emit", delta
    if fail is not None and _failure_wire(fail) in active:
        return "repair", None
    return "clean_fail", None


def _failure_wire(fail):
    if fail is None:
        return None
    if fail[0] in ("route",):
        return fail[5]
    if fail[0] in ("final", "owned_live", "owned_op"):
        return fail[1]
    return None

