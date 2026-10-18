"""Independent event comparison and nested fixed-role checkpoint checks."""
from hashlib import sha256
from dataclasses import replace
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import loader
codec = loader.activate()
from numeric import Geometry
from plan import Command, Plan, Reference
from records import Tape, append_word
from residual_blocks import Cursor, events
from role_parking import BODY, FiniteFields, RoleParking, transfer
from trace import execute
from words import Arena, BLANK, RIGHT, Unsigned, need


def snapshot(tape):
    return bytes(tape.cells[1:]).rstrip(bytes([BLANK]))


def value(word):
    if word is None:
        return None
    return bytes(word.cells[1:-1])


def signature(event, page):
    if event.kind in ("enter", "invoke", "return"):
        need(event.parent_identity is page.parent_identity,
             "trace boundary belongs to the expected parent")
    request = event.request
    return (event.kind, value(event.first), value(event.second), value(event.width), value(event.depth),
            event.child_kind, event.field, event.reverse, event.source_code, event.half,
            None if request is None else
            (request.kind, value(request.coordinate), request.reference, request.reverse_adapter,
             request.child_kind, request.field, request.reverse, request.negative_inverse, request.half))


def collect(iterator, page):
    try:
        return [signature(event, page) for event in iterator]
    finally:
        iterator.close()


def cursor_checks():
    digest = sha256()
    total = cases = checkpoints = 0
    plans = [Plan(64, rank, True, (
        Command("add", 1, 0, Reference("head", 0, 1, 0)),
        Command("add", 65, 64, Reference("tail", 0, sign=-1)),
    )) for rank in (1, 7, 42)]
    plans.append(Plan(64, 1, False, (
        Command("child", 0, 1, Reference("pair")),
        Command("add", 65, 0, Reference("shear", 0)),
        Command("child", 64, 65, Reference("pair")),
        Command("sign", 127, -1, Reference("fixed", sign=-1)),
        Command("child", 0, 64, Reference("unit")),
    )))
    for plan, width in product(plans, (1, 2, 3, 63, 64, 65, 127, 128, 129)):
        arena = Arena(18, 128)
        columns, depth = arena.input(width), arena.input(9)
        page = Geometry(plan, arena, columns, depth, 23, object())
        retained = frozenset(arena.live)
        tape = Tape()
        try:
            expected = collect(execute(page), page)
            need(arena.live == retained, "source trace releases its numerical locals")
            actual = []
            cursor = Cursor(plan)
            while not cursor.done:
                block = cursor.take()
                # Serialize the return state BEFORE the block, then discard the
                # cursor object. The resumed object receives no prior Python state.
                cursor.save(tape)
                del cursor
                actual.extend(collect(events(page, block), page))
                cursor = Cursor.restore(plan, tape)
                tape.clear()
                need(arena.live == retained, "one block closes its encoded column and child geometry")
                checkpoints += 1
            need(actual == expected, "same full event sequence after finite-cursor reconstruction")
            digest.update(repr(actual).encode())
            total += len(actual)
            cases += 1
        finally:
            tape.clear()
            page.close()
            arena.free_many(columns, depth)
            need(not arena.live, "closed cursor fixture bank")
    return dict(cases=cases, compared_events=total, serialized_return_cursors=checkpoints,
                digest=digest.hexdigest())


def parent_controls():
    """Reject each wrong-parent boundary before deterministic projection.

    Credit starship-s's public audit of PR2809 head38af8fb, Discussion2319
    comment18960884. Test both independently supplied streams; object addresses
    never enter the stable receipt.
    """
    global execute, events
    rejected = []
    for path in ("reference", "reconstructed"):
        for kind in ("enter", "invoke", "return"):
            for variant, identity in (("none", None), ("foreign", object())):
                original = execute if path == "reference" else events
                changed = []
                def wrong_parent(*args):
                    iterator = original(*args)
                    try:
                        for event in iterator:
                            if event.kind == kind:
                                changed.append(kind)
                                event = replace(event, parent_identity=identity)
                            yield event
                    finally:
                        iterator.close()
                if path == "reference":
                    execute = wrong_parent
                else:
                    events = wrong_parent
                try:
                    try:
                        cursor_checks()
                    except ValueError as error:
                        need(str(error) == "trace boundary belongs to the expected parent" and changed,
                             "wrong-parent control reaches its intended boundary")
                        rejected.append(path + ":" + kind + ":" + variant)
                    else:
                        raise ValueError("wrong parent escaped the continuation checker")
                finally:
                    if path == "reference":
                        execute = original
                    else:
                        events = original
    return rejected


def nested_roles(depth=1500):
    """One iterative control loop; encoded depth and no parent object stack."""
    residues, indices = Arena(3, 4), Arena(12, 8)
    numerical = codec.BankParking(residues, indices)
    roles = tuple(Tape() for _ in range(4))
    streams = RoleParking(numerical, roles)
    schema = FiniteFields((2, indices.capacity))
    result = Tape()  # Protected return port, outside the reusable role bank.
    current, root = indices.input(depth), True
    raw = Unsigned(indices)
    entered = returned = 0
    while not current.zero():
        schema.write(roles[0], (int(root), current.slot))
        append_word(roles[1], current)
        roles[1].rewind()
        for symbol in BODY:
            roles[2].append(symbol)
        roles[2].rewind()
        one = indices.literal(1)
        following = raw.subtract_exact(current, one)
        indices.free(one)
        streams.park()
        numerical.park((frozenset(), {following.slot}))
        current, root = following, False
        need(all(not snapshot(tape) and tape.head == 1 for tape in roles),
             "same empty canonical role bank for the child")
        entered += 1
    indices.free(current)
    result.append(1)
    while not root:
        numerical.restore()
        streams.restore()
        root_label, slot = schema.read(roles[0])
        root = bool(root_label)
        current = indices.words[slot]
        need(slot in indices.live, "restored finite slot names a live parent word")
        current.rewind()
        while current.read() != RIGHT:
            need(roles[1].read() == current.read(), "restored data role matches its numerical word")
            roles[1].step(1)
            current.step(1)
        need(roles[1].read() == 5 and snapshot(roles[2]) == bytes(BODY) and
             not snapshot(roles[3]), "nonempty and empty canonical roles restore in fixed order")
        current.rewind()
        indices.free(current)
        for tape in roles:
            tape.clear()
        result.append(1)
        returned += 1
    result.rewind()
    need(entered == returned == depth and snapshot(result) == bytes([1]) * (depth + 1),
         "protected child output survives all matched parent restorations")
    need(not indices.live and not residues.live and numerical.machine.tapes[0] == {} and
         numerical.machine.tapes[1] == {0: "^"}, "complete numerical, role and stack cleanup")
    # Per level: four stream records (4*(4+13+12) bits), one numerical
    # record (1+3+12 bits), and two matched frame pairs.
    need(numerical.machine.counts["steps"] == depth * (5 * 132 + 7 * 5 + 3 * 2),
         "exact composed PR2635 table invoice, including empty roles")
    output = dict(frames=depth, maximum_index_slots=len(indices.words), stream_roles=len(roles),
                  protected_return_symbols=depth + 1, parking_charge=numerical.machine.counts,
                  codec_charge=numerical.codec_counts)
    result.clear()
    return output


def transfer_checks():
    for old, new in product((b"", bytes(BODY), bytes([0, 1]) * 32), repeat=2):
        source, target = Tape(), Tape()
        for symbol in new:
            source.append(symbol)
        for symbol in old:
            target.append(symbol)
        transfer(source, target)
        need(not snapshot(source) and snapshot(target) == new and source.head == target.head == 1,
             "owned result transfer replaces the complete canonical body")
    rejected = 0
    for body in (b"", bytes([1, 1]), bytes([0, 1, 0])):
        tape = Tape()
        for symbol in body:
            tape.append(symbol)
        tape.rewind()
        try:
            FiniteFields((3,)).read(tape)
        except ValueError:
            rejected += 1
    need(rejected == 3, "reject short, out-of-range and overlong finite state")
    numerical = codec.BankParking(Arena(3, 2), Arena(3, 2))
    role = Tape()
    role.append(1)
    role.rewind()
    parking = RoleParking(numerical, (role,))
    parking.park()
    role.append(0)
    role.rewind()
    try:
        parking.restore()
    except ValueError as error:
        need(str(error) == "child clears canonical roles before return", "dirty-role failure cause")
    else:
        raise ValueError("dirty child role was overwritten on parent restoration")
    role.clear()
    parking.restore()
    need(snapshot(role) == bytes([1]), "dirty-role rejection preserves the complete parked parent")
    return dict(transfers=9, malformed_controls_rejected=rejected, dirty_role_rejected=True)


if __name__ == "__main__":
    result = dict(cursor=cursor_checks(), roles=nested_roles(), transfer=transfer_checks(), parents=parent_controls())
    print(json.dumps(result, sort_keys=True, indent=2))
    print("PASS_FIXED_ROLE_CONTINUATIONS")
