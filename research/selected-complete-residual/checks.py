"""Independent endpoint and complete-fibre checks for the residual trace."""
from pathlib import Path
from collections import Counter
from hashlib import sha256
import json
import sys
from time import monotonic

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "vendor"))
sys.path.insert(0, str(HERE))

from forms import fallback_form, good_form
from matrices import Matrices
from numeric import Page, selected_coefficient, selected_page
import oracle
import bitstream
import cardinality
import stream as retained_stream
import stream_runner
from plan import Reference, Request, compile_plan
from records import Fields, Program, Tape, RECORD_END, append_word, read_word, seek_record
from sources import compile_specification, compile_templates
from trace import execute
from words import Arena, BLANK, LEFT, Ring, Word, need


def no_decode(action):
    previous = Word.inspect
    def reject(_word):
        raise ValueError("runtime numerical decoding")
    Word.inspect = reject
    try:
        return action()
    finally:
        Word.inspect = previous


def audit(arena, live):
    need(arena.live == {word.slot for word in live}, "exact owned live roles")
    need(arena.template.head == 1, "restored extent template")
    for word in arena.words:
        need(word.head == 1, "restored numerical word")
        if word.slot not in arena.live:
            need(word.cells[0] == LEFT and all(x == BLANK for x in word.cells[1:]),
                 "erased numerical scratch")


def small_forms():
    arena = Arena(4)
    modulus = arena.input(5)
    ring = Ring(modulus)
    p = [[arena.input(x) for x in row] for row in ((2, 1, 2), (1, 2, 2), (1, 1, 3))]
    form = no_decode(lambda: good_form(p, 2, ring))
    later = form.rows[2][2].inspect()
    need(later == 3 and -1*pow(2, -1, 5) % 5 == 2, "chronological second good pivot")
    form.close(ring)
    Matrices(ring).free(p)
    ring.close()
    arena.free(modulus)
    audit(arena, ())

    arena = Arena(5)
    modulus = arena.input(9)
    ring = Ring(modulus)
    p = [[arena.input(x) for x in row] for row in ((3, 3), (1, 7))]
    form = no_decode(lambda: fallback_form(p, ring))
    diagonal = [x.inspect() for x in form.diagonal]
    need(diagonal == [7, 1, 1, 4] and form.permutation == (0, 2, 1, 3),
         "independent fallback diagonal and permutation")
    count = len(form.reductions)
    form.close(ring)
    Matrices(ring).free(p)
    ring.close()
    arena.free(modulus)
    audit(arena, ())
    return {"later_head": later, "fallback_diagonal": diagonal, "reductions": count}


class FixtureWeights:
    """Encoded arbitrary unit-vector fixture, outside the generated program."""
    def __init__(self, arena, values):
        self.arena, self.tape = arena, Tape()
        for value in values:
            word = arena.input(value)
            append_word(self.tape, word)
            self.tape.append(RECORD_END)
            arena.free(word)
        self.tape.rewind()
        self.original = bytes(self.tape.cells)

    def __call__(self, coordinate):
        seek_record(self.tape, coordinate)
        result = read_word(self.tape, self.arena)
        need(self.tape.read() == RECORD_END, "complete fixture weight")
        self.tape.rewind()
        return result

    def close(self):
        need(bytes(self.tape.cells) == self.original and self.tape.head == 1, "preserved encoded weights")
        self.tape.clear()


def expected_operator(projector, columns, weights, modulus):
    """Direct weighted raw-projector formula; no adapter or trace input."""
    m, rows = len(projector), [{} for _ in range(2*len(projector)*columns)]
    for j in range(columns):
        for i in range(m):
            hi, ti, ai = i*columns+j, (2*m-1-i)*columns+columns-1-j, weights[i*columns+j]
            for k in range(m):
                hk, tk, ak = k*columns+j, (2*m-1-k)*columns+columns-1-j, weights[k*columns+j]
                p, inv = projector[i][k], pow(ak, -1, modulus)
                for row, column, value in ((hi, hk, int(i == k)-ai*p*inv), (hi, tk, ai*p),
                                           (ti, hk, p*inv), (ti, tk, int(i == k)-p)):
                    if value % modulus:
                        rows[row][column] = value % modulus
    return rows


def observe_trace(page, atoms, modulus, fault=None):
    """Checker-only sparse action on every address basis column."""
    rows = [{i: 1} for i in range(atoms)]
    counts, children = Counter(), Counter()
    boundary, omitted, skip = None, False, False
    trace_hash = sha256()
    iterator = execute(page)
    while True:
        try:
            event = no_decode(lambda: next(iterator))
        except StopIteration:
            break
        first = event.first.inspect()
        second = event.second.inspect() if event.second is not None else None
        need(0 <= first < atoms and (second is None or 0 <= second < atoms), "physical emitted extent")
        counts[event.kind] += 1
        if event.kind in ("enter", "return"):
            data = (first, second, event.width.inspect(), event.depth.inspect(), event.child_kind,
                    event.field, event.reverse, event.source_code, event.half)
            need(event.parent_identity is page.parent_identity, "unchanged parent program identity")
            need(data[3] == page.depth.inspect()+1 and data[7] == page.source_code,
                 "original current-field extension")
            if event.kind == "enter":
                need(boundary is None and first+data[2] <= second and second+data[2] <= atoms,
                     "one disjoint completed child frame")
                boundary = data
                children[(event.child_kind, data[2])] += 1
                skip = fault == "omit_reversal" and not omitted and event.child_kind == "unit" and data[2] == 1
                omitted = omitted or skip
            else:
                need(boundary == data, "child return restores parent frame")
                boundary, skip = None, False
            trace_hash.update(json.dumps([event.kind, data], separators=(",", ":")).encode())
            continue
        value = None
        if event.kind == "add":
            reference = event.request.reference
            if fault in ("final_permutation", "redirected_pair") and reference is not None and reference.kind == "shear":
                def wrong_ratio():
                    pi = page.form.permutation if fault == "final_permutation" else reference.permutation
                    a, b = reference.first, reference.second
                    if fault == "redirected_pair" and a < b:
                        a, b = b, a
                    result = page.ratio(page.form.reductions[reference.index].scalar,
                                        page.bank(pi[a], event.request.coordinate),
                                        page.bank(pi[b], event.request.coordinate))
                    if reference.sign < 0:
                        opposite = page.ring.negate(result)
                        page.ring.arena.free(result)
                        result = opposite
                    return result
                word = no_decode(wrong_ratio)
            else:
                word = no_decode(lambda: page.evaluate(event.request))
            value = word.inspect()
            page.ring.arena.free(word)
            if fault == "wrong_inverse" and event.request.kind == "child" and event.request.negative_inverse:
                value = -value % modulus
            if fault == "inverse_adapter" and not omitted and event.request.reverse_adapter and value:
                value = -value % modulus
                omitted = True
            need(first > second, "later-target emitted ADD")
            counts["zero_add" if value == 0 else "nonzero_add"] += 1
        trace_hash.update(json.dumps([event.kind, first, second, value], separators=(",", ":")).encode())
        if skip:
            continue
        if event.kind == "atom_swap":
            rows[first], rows[second] = rows[second], rows[first]
        elif event.kind == "sign":
            rows[first] = {column: -value % modulus for column, value in rows[first].items()}
        else:
            need(event.kind == "add", "closed primitive trace alphabet")
            if value:
                row = dict(rows[first])
                for column, scalar in rows[second].items():
                    total = (row.get(column, 0)+value*scalar) % modulus
                    if total:
                        row[column] = total
                    else:
                        row.pop(column, None)
                rows[first] = row
    need(boundary is None, "closed residual child frames")
    return rows, {"events": dict(counts), "children": [[kind, width, count] for (kind, width), count in sorted(children.items())],
                  "trace_sha256": trace_hash.hexdigest(), "address_columns": atoms}


def small_trace(columns=1, fault=None):
    m, modulus = 2, 9
    p = [[3, 3], [1, 7]]
    weights = [2, 5] if columns == 1 else [2, 4, 8, 5, 7, 2]
    need(len(weights) == m*columns, "small trace fixture extent")
    arena, indices = Arena(5), Arena(8, capacity=256)
    encoded_modulus, f, depth = arena.input(modulus), indices.input(columns), indices.input(0)
    ring = Ring(encoded_modulus)
    encoded = [[arena.input(value) for value in row] for row in p]
    form = no_decode(lambda: fallback_form(encoded, ring))
    plan = compile_plan([[x % 3 for x in row] for row in p], 1, 3, False)
    table = FixtureWeights(arena, weights)
    page = Page(plan, form, ring, indices, f, table, depth, 22, object())
    rows, receipt = observe_trace(page, 2*m*columns, modulus, fault)
    expected = expected_operator(p, columns, weights, modulus)
    need((rows == expected) == (fault is None), "complete independently specified small operator")
    if columns == 1 and fault is None:
        need([[row.get(j, 0) for j in range(4)] for row in rows] ==
             [[7, 6, 6, 6], [2, 3, 8, 5], [5, 5, 3, 8], [6, 6, 6, 7]],
             "independent numerical fallback checkpoint")
    if fault == "final_permutation":
        need(rows[1].get(0) == 4, "final-permutation numerical witness")
    if fault == "redirected_pair":
        need(rows[1].get(3) == 2, "redirected-pair numerical witness")
    page.close()
    table.close()
    Matrices(ring).free(encoded)
    ring.close()
    arena.free(encoded_modulus)
    indices.free_many(f, depth)
    audit(arena, ())
    audit(indices, ())
    return receipt


def selected_trace(template, high=1, bad=False, columns=1, width=2, chronological=False, ancestor=False):
    started = monotonic()
    q, modulus, root_size = template.q, template.q**width, 64*columns
    if chronological:
        need(template.q == 5 and template.rank == 7, "actual rank-seven chronology fixture")
        h = oracle.eye(64)
        for i, row in zip((0, 1, 7), ((2, 1, -1), (1, 2, -1), (1, 1, -1))):
            for j, value in zip((0, 1, 7), row):
                h[i][j] = value % modulus
        raw = oracle.multiply(h, oracle.inverse(oracle.reduce_rational(template.preparation, modulus), modulus), modulus)
        low = tuple(tuple(value % q for value in row) for row in raw)
        digits = tuple(tuple(value//q for value in row) for row in raw)
    else:
        low, digits = oracle.fixture(template, width, high=high, bad=bad,
                                     unit_low=ancestor, row=63 if ancestor else None)
    specification = compile_specification(22, template, low)
    low_projector = oracle.projector(template, low, ((0,)*64,)*64, 1)
    plan = compile_plan(low_projector, template.rank, q, specification.good)
    specifications, events, field_rows = {22: specification}, (), ((22, digits),)
    expected_weights = [2]*(64*columns)
    if ancestor:
        need(template.rank == 7 and columns == 1, "generated ancestor fixture")
        root_size = 64*18
        prior_low, prior_high = oracle.fixture(template, width, high=1, unit_low=True)
        specifications[11] = compile_specification(11, template, prior_low)
        events = ((0, 11, 7, 0, False, False),)
        field_rows = ((11, prior_high), (22, digits))
        pivots = oracle.good_pivots(oracle.projector(template, prior_low, prior_high, width), 7, modulus)
        expected_weights = [2*pivots[i//18] % modulus for i in range(64)]
        need(len(set(expected_weights)) > 1, "nonconstant selected generated weights")
    arena, indices = Arena(modulus.bit_length()+1), Arena(root_size.bit_length()+1, capacity=256)
    encoded_modulus = arena.input(modulus)
    program = Program.fixture(indices, arena, root_size, 2, events)
    fields = Fields.fixture(indices, arena, field_rows)
    original = bytes(program.tape.cells), bytes(fields.tape.cells)
    ring = Ring(encoded_modulus)
    page, incoming = no_decode(lambda: selected_page(plan, ring, indices, program, fields, specifications, 22))
    if chronological:
        need(page.form.rows[68][2].inspect() == 8, "actual selected later-pivot coefficient")
    rows, receipt = observe_trace(page, 128*columns, modulus)
    direct = oracle.projector(template, low, digits, width)
    if chronological:
        need([[direct[i][j] for j in (0, 1, 7)] for i in (0, 1, 7)] ==
             [[2, 1, modulus-3], [1, 2, modulus-3], [1, 1, modulus-2]],
             "independent selected chronology projector checkpoint")
    need(rows == expected_operator(direct, columns, expected_weights, modulus),
         "complete actual selected weighted operator")
    page.close()
    indices.free(page.columns)
    incoming.close()
    ring.close()
    need(original == (bytes(program.tape.cells), bytes(fields.tape.cells)) and
         program.tape.head == fields.tape.head == 1, "selected raw/program preservation")
    arena.free(encoded_modulus)
    audit(arena, ())
    audit(indices, ())
    receipt.update({"source": template.record, "high": high, "bad": bad, "columns": columns, "width": width,
                    "chronological": chronological, "ancestor": ancestor,
                    "residue_operations": arena.meter.record(), "index_operations": indices.meter.record()})
    print("selected trace", template.record[0], bad, columns, round(monotonic()-started, 3), file=sys.stderr, flush=True)
    return receipt


def bit_trace(good=False, width=2, parent_atoms=2):
    """Complete four-atom Boolean fibre, including spectator bits and origins."""
    started = monotonic()
    q, before_count, suffix_count = 3, 2, 2
    modulus = q**width
    p = [[value % modulus for value in row] for row in ([[2, 8], [2, 8]] if good else [[3, 3], [1, 7]])]
    weights = [2, 5 % modulus]
    arena, indices = Arena(modulus.bit_length()+1), Arena(8, capacity=256)
    encoded_modulus = arena.input(modulus)
    f, depth, parent_size = indices.input(1), indices.input(0), indices.input(parent_atoms)
    ring = Ring(encoded_modulus)
    encoded = [[arena.input(value) for value in row] for row in p]
    form = no_decode(lambda: good_form(encoded, 1, ring) if good else fallback_form(encoded, ring))
    plan = compile_plan([[x % q for x in row] for row in p], 1, q, good)
    table = FixtureWeights(arena, weights)
    page = Page(plan, form, ring, indices, f, table, depth, 22, object())
    extents = Arena(3, capacity=4)
    before, suffix = extents.input(before_count), extents.input(suffix_count)
    registry, observer, erased = set(), [None], [0]

    class AuditTape(Tape):
        def __init__(self):
            super().__init__()
            registry.add(self)

        def clear(self):
            super().clear()
            need(self.head == 1 and bytes(self.cells).rstrip(bytes([BLANK])) == bytes([LEFT]),
                 "erased cardinality, counter and payload scratch")
            need(not getattr(self, "origins", {}), "erased payload-origin scratch")
            if self in registry:
                registry.remove(self)
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

    source = PayloadTape()
    atoms = 2*parent_atoms
    body = modulus**atoms
    volume = before_count*body*suffix_count
    for i in range(volume):
        source.append(((i*17) ^ (i >> 3) ^ 0x39) & 1)
    source.rewind()
    source.origins = {i+1: i for i in range(volume)}
    original = bytes(source.cells)
    old = bitstream.Tape, cardinality.Tape, retained_stream.Tape
    bitstream.Tape, cardinality.Tape, retained_stream.Tape = PayloadTape, AuditTape, AuditTape
    calls = [0]
    def coefficient(request):
        calls[0] += 1
        return page.evaluate(request)
    try:
        output = no_decode(lambda: stream_runner.run(source, page, parent_size, ring, q, before, suffix,
                                                      coefficient, PayloadTape))
    finally:
        bitstream.Tape, cardinality.Tape, retained_stream.Tape = old
    core_expected = expected_operator(p, 1, weights, modulus)
    expected = [{i: 1} for i in range(atoms)]
    def embed(i):
        return i if i < 2 else i+2*(parent_atoms-2)
    for i, row in enumerate(core_expected):
        expected[embed(i)] = {embed(j): value for j, value in row.items()}
    for prefix in range(before_count):
        for address in range(body):
            digits, remaining = [0]*atoms, address
            for j in range(atoms-1, -1, -1):
                digits[j], remaining = remaining % modulus, remaining//modulus
            moved = [sum(value*digits[column] for column, value in row.items()) % modulus for row in expected]
            target = 0
            for digit in moved:
                target = target*modulus+digit
            for tail in range(suffix_count):
                old_index = (prefix*body+address)*suffix_count+tail
                new_index = (prefix*body+target)*suffix_count+tail
                need(output.origins.get(new_index+1) == old_index, "complete residual bit origin")
                need(output.cells[new_index+1] == original[old_index+1], "complete residual Boolean payload")
    need(source.head == output.head == 1 and bytes(source.cells) == original, "preserved fibre source")
    need(registry == {source, output}, "only source and output payload tapes remain")
    checked_scratch = erased[0]
    digest = sha256(bytes(output.cells)).hexdigest()
    source.clear()
    output.clear()
    page.close()
    table.close()
    Matrices(ring).free(encoded)
    ring.close()
    arena.free(encoded_modulus)
    indices.free_many(f, depth, parent_size)
    extents.free_many(before, suffix)
    audit(arena, ())
    audit(indices, ())
    audit(extents, ())
    print("complete bit trace", good, volume, round(monotonic()-started, 3), file=sys.stderr, flush=True)
    return {"good": good, "width": width, "parent_atoms": parent_atoms, "bits": volume,
            "address_columns": atoms, "coefficient_calls": calls[0],
            "payload_sha256": digest, "scratch_tapes_checked": checked_scratch}


def serialized_children(templates):
    results = []
    for template, bad, columns, ancestor in ((templates[0], False, 1, False), (templates[1], True, 2, False),
                                            (templates[0], False, 1, True)):
        low, digits = oracle.fixture(template, 2, high=1, bad=bad, unit_low=ancestor, row=63 if ancestor else None)
        spec = compile_specification(22, template, low)
        plan = compile_plan(oracle.projector(template, low, ((0,)*64,)*64, 1), template.rank, 3, spec.good)
        root_size, specifications, events, rows = 64*columns, {22: spec}, (), ((22, digits),)
        if ancestor:
            root_size = 64*18
            prior_low, prior_high = oracle.fixture(template, 2, high=1, unit_low=True)
            specifications[11] = compile_specification(11, template, prior_low)
            events = ((0, 11, 7, 0, False, False),)
            rows = ((11, prior_high), (22, digits))
        arena, indices = Arena(5), Arena(root_size.bit_length()+1, capacity=256)
        modulus = arena.input(9)
        ring = Ring(modulus)
        program = Program.fixture(indices, arena, root_size, 2, events)
        fields = Fields.fixture(indices, arena, rows)
        original = bytes(program.tape.cells), bytes(fields.tape.cells)
        page, incoming = no_decode(lambda: selected_page(plan, ring, indices, program, fields, specifications, 22))
        cases = [("good", 0, False, False, i, negative) for i, negative in ((0, False), (6, False), (0, True))] if not bad else [
            ("pair", 1, False, False, 0, False), ("pair", 126, True, False, 0, False),
            ("pair", 126, True, False, 1, True), ("unit", 0, False, False, 1, False),
            ("unit", 0, False, True, 0, False)]
        for kind, field, reverse, half, coordinate, negative in cases:
            index = indices.input(coordinate)
            request = Request("child", index, child_kind=kind, field=field, reverse=reverse,
                              half=half, negative_inverse=negative)
            expected = no_decode(lambda: page.evaluate(request))
            actual = no_decode(lambda: selected_coefficient(plan, ring, indices, program, fields, specifications, 22, request))
            need(actual.inspect() == expected.inspect(), "actual serialized child weight")
            results.append([kind, field, reverse, half, coordinate, negative, actual.inspect(), ancestor])
            arena.free_many(expected, actual)
            indices.free(index)
            need(original == (bytes(program.tape.cells), bytes(fields.tape.cells)) and
                 program.tape.head == fields.tape.head == 1, "serialized child preserves its parent")
        page.close()
        indices.free(page.columns)
        incoming.close()
        ring.close()
        arena.free(modulus)
        audit(arena, ())
        audit(indices, ())
    return results


def shared_low_callbacks(template):
    base_low, _high = oracle.fixture(template, 2, high=0)
    spec = compile_specification(22, template, base_low)
    plan = compile_plan(oracle.projector(template, base_low, ((0,)*64,)*64, 1), 1, 3, True)
    heads, children = [], []
    for high in range(3):
        low, digits = oracle.fixture(template, 2, high=high)
        need(low == base_low, "one shared fixed-low trace")
        arena, indices = Arena(5), Arena(8, capacity=256)
        modulus, coordinate = arena.input(9), indices.input(0)
        ring = Ring(modulus)
        program = Program.fixture(indices, arena, 64, 2, ())
        fields = Fields.fixture(indices, arena, ((22, digits),))
        original = bytes(program.tape.cells), bytes(fields.tape.cells)
        for target, request in ((heads, Request("adapter", coordinate, Reference("head", 0, 1, 0))),
                                (children, Request("child", coordinate, child_kind="good"))):
            value = no_decode(lambda: selected_coefficient(plan, ring, indices, program, fields, {22: spec}, 22, request))
            target.append(value.inspect())
            arena.free(value)
        ring.close()
        need(original == (bytes(program.tape.cells), bytes(fields.tape.cells)) and
             program.tape.head == fields.tape.head == 1, "shared-low callbacks preserve raw inputs")
        arena.free(modulus)
        indices.free(coordinate)
        audit(arena, ())
        audit(indices, ())
    need(heads == [0, 6, 3] and children == [2, 8, 5], "same-low numerical variation")
    return {"heads": heads, "child_weights": children, "shared_low_classes": 1}


def run_source():
    import check_packet
    three, five = compile_templates(3), compile_templates(5)
    return {
        "selected": [selected_trace(three[0]), selected_trace(three[1], bad=True, columns=2),
                     selected_trace(five[0], chronological=True), selected_trace(three[0], ancestor=True)],
        "shared_low_callbacks": shared_low_callbacks(three[1]),
        "serialized_children": serialized_children(three),
        "complete_bit_traces": [bit_trace(True), bit_trace(False), bit_trace(False, width=1, parent_atoms=3)],
        "fallback_packet": check_packet.complete_cube(2, bad=True),
        "scope": "Complete selected address-column traces and separate complete Boolean residual/packet traces. No full selected GL64 Boolean payload, larger recursive child or global caller execution.",
    }


if __name__ == "__main__":
    print(small_forms())
    print(small_trace())
    print(small_trace(3))
    print(small_trace(3, "omit_reversal"))
    print(small_trace(1, "wrong_inverse"))
