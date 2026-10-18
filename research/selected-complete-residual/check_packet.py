"""Complete GL2 high cube through the same binary residual trace."""
from collections import Counter
from hashlib import sha256
from itertools import product
import sys
from time import monotonic

import bitstream
import cardinality
from checks import FixtureWeights, audit, expected_operator, no_decode
from forms import fallback_form, good_form
from matrices import Matrices
from numeric import Geometry, Page
import oracle
import packet
from plan import compile_plan
from records import FINITE_BITS, RECORD_END, Tape, append_finite, append_word, read_finite, read_word
import stream as retained_stream
from words import Arena, BLANK, LEFT, Ring, need


def complete_cube(limit=None, bad=False):
    started = monotonic()
    q, modulus, weights = 3, 9, (2, 5)
    low = ((0, 2), (1, 1)) if bad else ((1, 1), (0, 1))
    highs = list(product(range(q), repeat=4))
    if limit is not None:
        highs = highs[:limit]
    need(highs, "nonempty prefix fixture")
    arena, indices, counts = Arena(5), Arena(8, capacity=256), Arena(len(highs).bit_length()+1, capacity=4)
    m = arena.input(modulus)
    ring = Ring(m)
    f, depth, parent_size, one = indices.input(1), indices.input(0), indices.input(2), indices.input(1)
    number = counts.input(len(highs))
    spectator = Arena(2, capacity=4)
    extent = spectator.input(1)
    directory = Tape()
    for high in highs:
        append_finite(directory, 22)
        for value in high:
            word = arena.input(value)
            append_word(directory, word)
            arena.free(word)
        directory.append(RECORD_END)
    directory.rewind()
    original_directory = bytes(directory.cells)
    low_projector = oracle.multiply([[row[0]] for row in low], oracle.inverse(low, q)[:1], q)
    plan = compile_plan(low_projector, 1, q, not bad)
    identity = object()
    geometry = Geometry(plan, indices, f, depth, 22, identity)
    table = FixtureWeights(arena, weights)
    calls = [0]

    def coefficient(fields, request):
        calls[0] += 1
        fields.rewind()
        need(read_finite(fields, FINITE_BITS) == 22, "current packet raw source code")
        high = [[read_word(fields, arena) for _ in range(2)] for _ in range(2)]
        need(fields.read() == RECORD_END, "complete packet high matrix")
        fields.step(1)
        need(fields.read() == BLANK, "one packet current field")
        fields.rewind()
        cap = arena.literal(3)
        for row in high:
            for digit in row:
                need(ring.raw.compare(digit, cap) < 0, "packet high digit range")
        arena.free(cap)
        matrices = Matrices(ring)
        header = matrices.raw_header(low, high, q)
        projector = matrices.projector(header, 1)
        form = fallback_form(projector, ring) if bad else good_form(projector, 1, ring)
        page = Page(plan, form, ring, indices, f, table, depth, 22, identity)
        result = page.evaluate(request)
        page.close()
        matrices.free(high)
        matrices.free(header)
        matrices.free(projector)
        return result

    live, erased, observer = set(), [0], [None]
    class AuditTape(Tape):
        def __init__(self):
            super().__init__()
            live.add(self)

        def clear(self):
            super().clear()
            need(self.head == 1 and bytes(self.cells).rstrip(bytes([BLANK])) == bytes([LEFT]),
                 "erased packet scratch")
            need(not getattr(self, "origins", {}), "erased packet origin tags")
            if self in live:
                live.remove(self)
                erased[0] += 1

    class PayloadTape(AuditTape):
        def __init__(self):
            super().__init__()
            self.origins = {}

        def read(self):
            value = super().read()
            if self.head in self.origins:
                observer[0] = self.origins[self.head]
            return value

        def write(self, value):
            super().write(value)
            if value == BLANK:
                self.origins.pop(self.head, None)
            elif value in (0, 1) and observer[0] is not None:
                self.origins[self.head] = observer[0]

    body = modulus**4
    source = PayloadTape()
    for i in range(len(highs)*body):
        source.append(((i*7) ^ (i >> 4) ^ 0x47) & 1)
    source.rewind()
    source.origins = {i+1: i for i in range(len(highs)*body)}
    original = bytes(source.cells)
    previous = bitstream.Tape, cardinality.Tape, retained_stream.Tape, packet.Tape
    bitstream.Tape, cardinality.Tape, retained_stream.Tape, packet.Tape = PayloadTape, AuditTape, AuditTape, AuditTape
    boundaries = Counter()
    try:
        output = no_decode(lambda: packet.run(source, geometry, parent_size, ring, q, extent, extent,
                                             number, one, directory, coefficient, PayloadTape,
                                             lambda kind: boundaries.update([kind])))
    finally:
        bitstream.Tape, cardinality.Tape, retained_stream.Tape, packet.Tape = previous
    for prefix, high in enumerate(highs):
        g = [[low[i][j]+3*high[2*i+j] for j in range(2)] for i in range(2)]
        p = oracle.multiply([[row[0]] for row in g], oracle.inverse(g, modulus)[:1], modulus)
        expected = expected_operator(p, 1, weights, modulus)
        for address in range(body):
            digits, remaining = [0]*4, address
            for j in range(3, -1, -1):
                digits[j], remaining = remaining % modulus, remaining//modulus
            target = 0
            for row in expected:
                target = modulus*target+sum(value*digits[column] for column, value in row.items()) % modulus
            old_index, new_index = prefix*body+address, prefix*body+target
            need(output.origins.get(new_index+1) == old_index and output.cells[new_index+1] == original[old_index+1],
                 "complete raw-high cube and Boolean fibre endpoint")
    expected_children = sum(command.kind == "child" for command in plan.commands) if bad else 1
    need(boundaries == {"enter": expected_children, "return": expected_children},
         "each child occurs once across the high packet")
    need(live == {source, output}, "closed packet scratch inventory")
    need(bytes(source.cells) == original and bytes(directory.cells) == original_directory and
         source.head == output.head == directory.head == 1, "packet source/directory preservation")
    digest, scratch = sha256(bytes(output.cells)).hexdigest(), erased[0]
    source.clear()
    output.clear()
    geometry.close()
    table.close()
    ring.close()
    arena.free(m)
    indices.free_many(f, depth, parent_size, one)
    counts.free(number)
    spectator.free(extent)
    for work in (arena, indices, counts, spectator):
        audit(work, ())
    print("complete high packet", len(highs), len(highs)*body, round(monotonic()-started, 3), file=sys.stderr, flush=True)
    return {"prefixes": len(highs), "bad": bad, "complete_high_cube": limit is None, "bits": len(highs)*body,
            "child_entries": boundaries["enter"], "child_returns": boundaries["return"],
            "coefficient_preparations": calls[0], "scratch_tapes_checked": scratch, "payload_sha256": digest}
