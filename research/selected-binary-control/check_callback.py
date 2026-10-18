"""Independent numerical expectations and complete encoded-site checks."""
from dataclasses import replace
from hashlib import sha256
import json
import sys
from time import monotonic

import oracle
from check_words import audit
from controller import Callback, selected_offset
from matrices import Matrices
from records import Fields, Program, Tape
from sources import compile_specification, compile_templates
from stream import Counter, add_pass
from words import Arena, BLANK, LEFT, RIGHT, ZERO, Meter, Ring, Word, need


def snapshot(tape):
    need(tape.head == 1, "input/output head origin")
    return bytes(tape.cells).rstrip(bytes([BLANK]))


def clear_meters(*objects):
    for obj in objects:
        obj.meter = Meter()


def no_decode(action):
    previous = Word.inspect
    def forbidden(_word):
        raise ValueError("runtime word escaped to a host integer")
    Word.inspect = forbidden
    try:
        return action()
    finally:
        Word.inspect = previous


def audit_stacks(callback):
    for stack in (callback.pending, callback.values):
        for tape in (stack.tape, stack.reverse):
            need(snapshot(tape) == bytes([LEFT]), "erased continuation and reversal tapes")


def source_checkpoints(templates):
    # Retained q=3,w=2 raw literals from PR2234, independent of the fixture
    # constructor's basis/chart pullback. Compare the complete 64x64 arrays.
    checkpoints = (
        (((0, 1, 1), (0, 2, 1), (0, 4, 2), (0, 7, 1), (1, 7, 2),
          (2, 7, 2), (4, 7, 1), (7, 1, 1), (7, 2, 1), (7, 4, 2)),
         ((0, 4, 2), (1, 7, 2), (2, 7, 2), (7, 0, 1), (7, 1, 1),
          (7, 2, 1), (7, 4, 1), (7, 7, 1))),
        (((0, 0, 0), (0, 1, 1), (0, 8, 1), (8, 0, 1), (8, 8, 0)),
         ((1, 1, 1), (1, 8, 1))),
    )
    for template, (low_changes, high_changes) in zip(templates, checkpoints):
        low = [[int(i == j) for j in range(64)] for i in range(64)]
        high = [[0]*64 for _ in range(64)]
        for i, j, value in low_changes:
            low[i][j] = value
        for i, j, value in high_changes:
            high[i][j] = value
        observed = oracle.fixture(template, 2, high=1)
        need(observed == (tuple(map(tuple, low)), tuple(map(tuple, high))),
             "pinned selected raw-low/high checkpoint")
    return {"requests": 2, "raw_entries": 16384, "source_pr": 2234}


class OriginObserver:
    def __init__(self):
        self.last = None


class TracedPayload(Tape):
    """Checker-only bit-origin observation; no tag enters machine control."""
    def __init__(self, observer):
        super().__init__()
        self.observer, self.origins = observer, {}

    def read(self):
        value = super().read()
        if self.head in self.origins:
            self.observer.last = self.origins[self.head]
        return value

    def write(self, symbol):
        super().write(symbol)
        if symbol == BLANK:
            self.origins.pop(self.head, None)
        elif symbol in (0, 1) and self.observer.last is not None:
            self.origins[self.head] = self.observer.last


def encoded_matrix(arena, values):
    return [[arena.input(value) for value in row] for row in values]


def matrix_cases(templates, extra=None):
    rows = []
    cases = [
        (templates[0], 2, 1, False, False),
        (templates[1], 2, 1, True, False),
        (templates[0], 3, 2, False, False),
        (templates[0], 2, 0, False, True),
    ]
    if extra is not None:
        cases.append((extra, 2, 1, True, False))
    for template, width, high_value, bad, dense in cases:
        modulus = template.q**width
        low, digits = oracle.fixture(template, width, high=high_value, bad=bad)
        if dense:
            cap = template.q**(width-1)
            digits = tuple(tuple((17*i+13*j+1) % cap for j in range(64)) for i in range(64))
        arena = Arena(modulus.bit_length()+1)
        m = arena.input(modulus)
        high = encoded_matrix(arena, digits)
        original = [[bytes(word.cells) for word in row] for row in high]
        clear_meters(arena)
        ring = Ring(m)
        matrices = Matrices(ring)
        def calculate():
            p = matrices.prepare(low, high, template.q, template.preparation, template.rank)
            if bad:
                table, permutation = matrices.fallback(p)
            else:
                table, permutation = matrices.good_pivots(p, template.rank), ()
            return p, table, permutation
        started = monotonic()
        p, table, permutation = no_decode(calculate)
        actual = [[word.inspect() for word in row] for row in p]
        direct = oracle.projector(template, low, digits, width)
        need(actual == direct, "all 4096 binary projector entries")
        expected, expected_pi = oracle.fallback(direct, modulus) if bad else (
            oracle.good_pivots(direct, template.rank, modulus), ())
        need([value.inspect() for value in table] == expected and permutation == expected_pi,
             "complete binary preparation table")
        need(original == [[bytes(word.cells) for word in row] for row in high], "raw input words unchanged")
        digest = sha256(json.dumps([actual, expected, expected_pi], separators=(",", ":")).encode()).hexdigest()
        arena.free_many(*table)
        matrices.free(p)
        ring.close()
        operations = arena.meter.record()
        audit(arena, (m, *(word for row in high for word in row)))
        matrices.free(high)
        arena.free(m)
        audit(arena, ())
        rows.append({"request": template.record, "width": width, "bad": bad, "dense_high": dense,
                     "projector_entries": 4096, "table_entries": len(expected), "sha256": digest,
                     "operations": operations})
        print("matrix", width, bad, dense, round(monotonic()-started, 3), file=sys.stderr, flush=True)
    return rows


def reference(events, field_rows, specifications, root_size, unit, modulus, index):
    sizes = [root_size]
    tables = []
    for event, (_code, digits) in zip(events, field_rows):
        kind, code, rank, field, reverse, half = event
        f = sizes[-1]//64
        sizes.append(rank*f if kind == 0 else f//2 if half else f)
        if kind == 2:
            tables.append(None)
        else:
            spec = specifications[code]
            width = 1
            while spec.template.q**width != modulus:
                width += 1
            p = oracle.projector(spec.template, spec.low, digits, width)
            tables.append(oracle.good_pivots(p, rank, modulus) if kind == 0 else oracle.fallback(p, modulus))
    def value(level, coordinate):
        if level == 0:
            return unit % modulus
        kind, code, rank, field, reverse, half = events[level-1]
        if kind == 2:
            return 1
        f = sizes[level-1]//64
        if kind == 0:
            return value(level-1, coordinate)*tables[level-1][coordinate//f] % modulus
        diagonal, pi = tables[level-1]
        column = f-1-coordinate if reverse else coordinate
        def bank(row):
            return value(level-1, row*f+column) if row < 64 else 1
        return diagonal[field]*bank(pi[field])*pow(bank(field), -1, modulus) % modulus
    return value(len(events), index), sizes[-1]


def context_fixture(template, kind="good", variant=0, width=2, root_size=None):
    good_low, good_digits = oracle.fixture(template, width, high=variant, unit_low=True)
    bad_low, bad_digits = oracle.fixture(template, width, high=1, bad=True, row=9)
    current_low, current_digits = oracle.fixture(template, width, high=0, unit_low=True, row=63)
    specs = {11: compile_specification(11, template, good_low),
             33: compile_specification(33, template, bad_low),
             44: compile_specification(44, template, good_low),
             22: compile_specification(22, template, current_low)}
    if kind == "good":
        root_size = 4096 if root_size is None else root_size
        events = ((0, 11, 7, 0, False, False),)
        fields = ((11, good_digits), (22, current_digits))
    elif kind in ("pair_forward", "pair_reverse"):
        root_size = 64**4+17 if root_size is None else root_size
        field, reverse = (9, False) if kind == "pair_forward" else (118, True)
        events = ((0, 11, 7, 0, False, False), (1, 33, 7, field, reverse, False))
        fields = ((11, good_digits), (33, bad_digits), (22, current_digits))
    else:
        need(kind in ("unit_reset", "orientation_reset"), "fixture chain kind")
        root_size = 64**4+17 if root_size is None else root_size
        _dead_low, dead = oracle.fixture(template, width, high=(variant+1) % template.q, unit_low=True)
        events = ((0, 11, 7, 0, False, False), (2, 33, 7, 0, False, kind == "orientation_reset"),
                  (0, 44, 7, 0, False, False))
        fields = ((11, dead), (33, bad_digits), (44, good_digits), (22, current_digits))
    return specs, events, fields, root_size


def one_callback(template, kind, variant=0, width=2, source_value=4, root_size=None):
    specs, events, field_rows, root_size = context_fixture(template, kind, variant, width, root_size)
    original_width = width*root_size
    need((width-1)**10000 < original_width**17 <= width**10000, "callback root-coupled fixture")
    modulus = template.q**width
    residues, indices = Arena(modulus.bit_length()+1), Arena(root_size.bit_length()+1, capacity=256)
    m, source = residues.input(modulus), residues.input(source_value)
    column = indices.input(0)
    program = Program.fixture(indices, residues, root_size, 2, events)
    fields = Fields.fixture(indices, residues, field_rows)
    original = (snapshot(program.tape), snapshot(fields.tape), bytes(m.cells), bytes(source.cells), bytes(column.cells))
    def calculate():
        callback = Callback(ring, indices, program, fields, specs, 22)
        outputs = []
        # Fixture index loading is outside runtime; preload before no_decode
        # in the caller below, then consume only encoded words here.
        for word in sample_indices:
            outputs.append(callback.weight(word))
        offset = callback.offset(63, column, source)
        prepared = tuple(sorted(callback.prepared_codes))
        callback.close()
        audit_stacks(callback)
        return outputs, offset, prepared
    if kind == "pair_reverse":
        points = (0, 24575, 24576, 28671)
    elif kind == "pair_forward":
        points = (0, 4095, 4096, 28671)
    else:
        points = (0,)
    sample_indices = tuple(indices.input(value) for value in points)
    clear_meters(residues, indices, program.tape, fields.tape)
    started = monotonic()
    ring = Ring(m)
    outputs, offset, prepared = no_decode(calculate)
    observed = [word.inspect() for word in outputs]
    expected = [reference(events, field_rows, specs, root_size, 2, modulus, value)[0] for value in points]
    need(observed == expected, "binary generated weights and reversal boundary")
    _value, final_size = reference(events, field_rows, specs, root_size, 2, modulus, 0)
    current = specs[22]
    p = oracle.projector(current.template, current.low, field_rows[-1][1], width)
    ai = reference(events, field_rows, specs, root_size, 2, modulus, 63*(final_size//64))[0]
    a0 = reference(events, field_rows, specs, root_size, 2, modulus, 0)[0]
    coefficient = -p[63][0]*pow(p[0][0], -1, modulus)*ai*pow(a0, -1, modulus) % modulus
    need(offset.inspect() == coefficient*source_value % modulus, "complete binary selected offset")
    if kind == "pair_reverse":
        need(observed[0] != observed[-1], "reversal has a numerical effect")
    if "reset" in kind:
        need(prepared == (22, 44), "unit reset retains global slot two and avoids dead preparation")
    need(original == (snapshot(program.tape), snapshot(fields.tape), bytes(m.cells), bytes(source.cells), bytes(column.cells)),
         "callback input streams and words unchanged")
    returned = offset.inspect()
    residues.free_many(*outputs, offset)
    indices.free_many(*sample_indices)
    ring.close()
    audit(residues, (m, source))
    audit(indices, (column,))
    operations = {"residues": residues.meter.record(), "indices": indices.meter.record(),
                  "program": program.tape.meter.record(), "fields": fields.tape.meter.record()}
    residues.free_many(m, source)
    indices.free(column)
    audit(residues, ())
    audit(indices, ())
    print("callback", kind, variant, round(monotonic()-started, 3), file=sys.stderr, flush=True)
    return {"kind": kind, "variant": variant, "width": width, "root_size": root_size,
            "indices": list(points), "weights": observed, "coefficient": coefficient, "source": source_value,
            "offset": returned, "prepared_codes": prepared, "operations": operations}


def counter_cases():
    rows = []
    for value in range(129):
        arena = Arena(max(2, value.bit_length()+1), capacity=4)
        word = arena.input(value)
        counter = Counter(word)
        steps = 0
        while not counter.finished:
            counter.decrement()
            steps += 1
        need(steps == value and snapshot(counter.tape) == bytes((LEFT, ZERO, RIGHT)), "complete ripple countdown")
        counter.close()
        need(snapshot(counter.tape) == bytes((LEFT,)), "counter erasure")
        arena.free(word)
        audit(arena, ())
        rows.append(counter.tape.meter.record())
    return {"complete_ranges": 129, "largest_range_operations": rows[-1]}


def payload_site(template):
    specs, events, field_rows, root_size = context_fixture(template)
    modulus = template.q**2
    residues, indices = Arena(modulus.bit_length()+1), Arena(root_size.bit_length()+1, capacity=256)
    m, column = residues.input(modulus), indices.input(0)
    program = Program.fixture(indices, residues, root_size, 1, events)
    fields = Fields.fixture(indices, residues, field_rows)
    extents = [Arena(value.bit_length()+1, capacity=4) for value in (2, 3, 32)]
    before, middle, suffix = (arena.input(value) for arena, value in zip(extents, (2, 3, 32)))
    records = 2*modulus*3*modulus*2
    observer = OriginObserver()
    source = TracedPayload(observer)
    for record in range(records):
        for bit in range(16):
            source.append(((record ^ 0xa539) >> bit) & 1)
    source.rewind()
    source.origins = {i+1: i for i in range(records*16)}
    original = snapshot(source)
    clear_meters(residues, indices, program.tape, fields.tape, source, *extents)
    ring = Ring(m)
    callback = Callback(ring, indices, program, fields, specs, 22)
    started = monotonic()
    output, traffic = no_decode(lambda: add_pass(source, ring, before, middle, suffix,
                                               lambda: callback.coefficient(63, column),
                                               lambda: TracedPayload(observer)))
    # Independent dense address oracle, only in this checker.
    expected, expected_origins, start = [], [], 0
    for _before in range(2):
        for x in range(modulus):
            for _middle in range(3):
                for y in range(modulus):
                    original_y = (y-4*x) % modulus
                    for tail in range(2):
                        value = (start+original_y*2+tail) ^ 0xa539
                        expected.extend((value >> bit) & 1 for bit in range(16))
                        expected_origins.extend(16*(start+original_y*2+tail)+bit for bit in range(16))
                start += modulus*2
    need(snapshot(output) == bytes([LEFT]+expected), "encoded offsets reach the complete payload endpoint")
    need([output.origins[i+1] for i in range(records*16)] == expected_origins,
         "every payload bit has its exact expected source coordinate")
    restored, inverse_traffic = no_decode(lambda: add_pass(output, ring, before, middle, suffix,
                                                         lambda: callback.coefficient(63, column, True),
                                                         lambda: TracedPayload(observer)))
    need(snapshot(restored) == original and snapshot(source) == original, "recomputed inverse restores arbitrary payload")
    need([restored.origins[i+1] for i in range(records*16)] == list(range(records*16)),
         "inverse restores every individual bit coordinate")
    callback.close()
    audit_stacks(callback)
    ring.close()
    audit(residues, (m,))
    audit(indices, (column,))
    digest = sha256(snapshot(output)).hexdigest()
    operations = {"residues": residues.meter.record(), "indices": indices.meter.record(),
                  "program": program.tape.meter.record(), "fields": fields.tape.meter.record()}
    residues.free(m)
    indices.free(column)
    for arena, extent in zip(extents, (before, middle, suffix)):
        arena.free(extent)
        audit(arena, ())
    print("payload", records, round(monotonic()-started, 3), file=sys.stderr, flush=True)
    return {"records": records, "bits": records*16, "coefficient": 4, "payload_sha256": digest,
            "forward": traffic, "inverse": inverse_traffic, "operations": operations}
