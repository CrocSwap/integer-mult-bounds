"""Serialized child extensions on the same raw-prefix field band."""
from controller import Callback
from records import BLANK, FINITE_BITS, RECORD_END, ROOT, STEP, Program, append_finite, append_word
from words import need


def extend(incoming, request):
    parent = incoming.program
    index, residue = incoming.index, incoming.residue
    need(request.child_kind in ("good", "pair", "unit"), "serialized child kind")
    kind = {"good": 0, "pair": 1, "unit": 2}[request.child_kind]
    specification = incoming.specifications[incoming.current_code]
    rank = specification.template.rank
    f, remainder = incoming.raw.divmod(incoming.final_size, incoming.sixty_four)
    index.free(remainder)
    if kind == 0:
        size = incoming.raw.times_small(f, rank)
    elif request.half:
        need(kind == 2, "only orientation unit children halve")
        size, remainder = incoming.raw.divmod(f, incoming.two_index)
        index.free(remainder)
    else:
        size = index.copy(f)
    index.free(f)
    need(not size.zero() and incoming.raw.compare(request.coordinate, size) < 0,
         "requested completed-child coordinate")
    new_depth = incoming.plus(incoming.depth, incoming.one_index)
    out = Program(index, residue, parent.code_bits)
    out.tape.append(ROOT)
    for word in (incoming.root_size, incoming.root_unit, new_depth):
        append_word(out.tape, word)
    out.tape.append(RECORD_END)
    parent.tape.rewind()
    while parent.tape.read() != RECORD_END:
        parent.tape.step(1)
    parent.tape.step(1)
    while parent.tape.read() != BLANK:
        out.tape.append(parent.tape.read())
        parent.tape.step(1)
    parent.tape.rewind()
    out.tape.append(STEP)
    metadata = (kind, incoming.current_code, rank, request.field, int(request.reverse), int(request.half))
    for position, value in enumerate(metadata):
        append_finite(out.tape, value, parent.code_bits if position == 1 else FINITE_BITS)
    append_word(out.tape, incoming.final_size)
    append_word(out.tape, size)
    out.tape.append(RECORD_END)
    out.tape.rewind()
    index.free_many(size, new_depth)
    return out


def coefficient(ring, index, program, fields, specifications, current_code, request):
    """Evaluate an actual appended leaf program; no fresh current field exists."""
    parent, leaf, extended = None, None, None
    protected_residues, protected_indices = frozenset(ring.arena.live), frozenset(index.live)
    try:
        parent = Callback(ring, index, program, fields, specifications, current_code, allow_fallback=True)
        extended = extend(parent, request)
        leaf = Callback(ring, index, extended, fields, specifications, current_code,
                        allow_fallback=True, leaf=True)
        value = leaf.weight(request.coordinate)
        if request.negative_inverse:
            inverse = ring.inverse(value)
            need(inverse is not None, "serialized child weight unit")
            opposite = ring.negate(inverse)
            ring.arena.free_many(value, inverse)
            value = opposite
        leaf.close()
        parent.close()
        extended.tape.clear()
        return value
    except ValueError:
        if leaf is not None:
            leaf.abort()
        if parent is not None:
            parent.abort()
        if extended is not None:
            extended.tape.clear()
        ring.arena.rollback(protected_residues)
        index.rollback(protected_indices)
        program.tape.rewind()
        fields.tape.rewind()
        raise
