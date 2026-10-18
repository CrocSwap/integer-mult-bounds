"""Exact source, counter, continuation and complete-stream checks.

Dense address formulas and direct tape inspection occur only in this checker.
Selected64 snapshots are finite slices, distinct from the complete m=2 cube.
"""
from collections import Counter
from hashlib import sha256
from itertools import product

from algebra import eye, fallback_table, good_pivots, inverse, multiply, projector
from control import Backend, GOOD, PAIR, UNIT, compile_program, compile_selected, evaluate, head_coefficient
from selected import prepare, raw_fixture, reduce_matrix, requests
from stream import add_site
from tapes import FieldBand, Stack, Tape, need


def reject(action, text):
    try:
        action()
    except ValueError as error:
        need(text in str(error), "intended failure control")
        return str(error)
    raise ValueError("failure control did not reject")


def bits(values, width=16):
    return tuple((value >> bit) & 1 for value in values for bit in range(width))


def payload(count):
    tape = Tape()
    for bit in bits([i ^ 0xa539 for i in range(count)]):
        tape.append(bit)
    tape.rewind()
    tape.meter.clear()
    return tape


def snapshot(tape):
    need(tape.head == 1 and tape.cells.get(0) == "^", "payload head and origin")
    return tuple(tape.cells[i] for i in range(1, len(tape.cells)))


def audit_local_work(backend, ancestor=(), origin=0):
    """Uncharged test instrumentation, outside the coefficient machine."""
    expected = {**{origin-len(ancestor)+i: x for i, x in enumerate(ancestor)}, origin: "^"}
    for stack in backend.last_work:
        need(stack.tape.low_seen >= origin and stack.reverse.low_seen >= 0,
             "relative stack trace excludes ancestors")
        need(stack.tape.cells == expected, "local stack cleanup and ancestor restoration")
        need(stack.tape.head == origin+1 and stack.reverse.head == 1 and stack.reverse.cells == {0: "^"},
             "empty reversal scratch and restored heads")


def translated_value(program, backend, index, ancestor, origin):
    # Preload the marked input interface before measured execution.
    work = (Stack(ancestor, origin), Stack(ancestor, origin))
    result = evaluate(program, backend, index, work)
    audit_local_work(backend, ancestor, origin)
    return result


def expected_add(coefficients, modulus, before, middle, tail_records):
    out, count = [], 0
    for c in coefficients:
        for _before in range(before):
            for x in range(modulus):
                for _middle in range(middle):
                    for y in range(modulus):
                        original_y = (y-c*x) % modulus
                        out.extend((count+original_y*tail_records+t) ^ 0xa539 for t in range(tail_records))
                    count += modulus*tail_records
    return bits(out)


def decoder_checks():
    cases = []
    for cap, dimensions in ((1, (2, 1)), (2, (2, 1)), (3, (2,)), (5, (1, 1))):
        band = FieldBand(cap, dimensions, tuple(range(len(dimensions))))
        expected = product(range(cap), repeat=sum(d*d for d in dimensions))
        count, more = 0, True
        for row in expected:
            need(more, "odometer retains the complete cube")
            decoded = sum((band.read_field(i, i, len(dimensions)) for i in range(len(dimensions))), ())
            need(decoded == row, "canonical lexicographic high prefix")
            count += 1
            more = band.advance()
        need(not more, "odometer completes exactly one cube")
        cases.append([cap, list(dimensions), count])
    translated = []
    for origin, ancestor in ((0, ()), (4096, (1,)*257), (10**30, (0, 1, "#")*13)):
        stack = Stack(ancestor, origin)
        records = [(0, 7, 2**301+19), (3, 8), (1, 0), (2, 2**97)]
        for row in records:
            stack.push(row)
        for row in reversed(records):
            need(stack.pop() == row, "serialized continuation round trip")
        need(stack.empty() and stack.tape.low_seen >= origin, "relative origin locality")
        need(stack.tape.cells == {**{origin-len(ancestor)+i: x for i, x in enumerate(ancestor)}, origin: "^"},
             "buried data unchanged and local record erased")
        translated.append(dict(stack.tape.meter))
    need(translated[0] == translated[1] == translated[2], "stack cost ignores absolute origin and ancestor length")
    return {"complete_prefixes": cases, "translated_stack_operations": translated[0]}


def pullback_cube():
    q, modulus, cap = 3, 9, 3
    s, low = [[4, 1], [1, 2]], eye(2)
    low_product = multiply(low, s, modulus)
    prepared_low = [[x % q for x in row] for row in low_product]
    carry = [[x // q for x in row] for row in low_product]
    band = FieldBand(cap, (2,), (91,))
    coefficients, images, changes = [], set(), 0
    for _ in range(cap**4):
        high = band.read_field(0, 91, 1)
        g = [[low[i][j]+q*high[2*i+j] for j in range(2)] for i in range(2)]
        h = multiply(g, s, modulus)
        mapped = multiply([list(high[:2]), list(high[2:])], s, cap)
        mapped = tuple((mapped[i][j]+carry[i][j]) % cap for i in range(2) for j in range(2))
        need(tuple((h[i][j]-prepared_low[i][j])//q % cap for i in range(2) for j in range(2)) == mapped,
             "full affine high carry")
        images.add(mapped)
        changes += mapped != high
        p = projector(h, 1, modulus)
        coefficients.append(-p[1][0]*pow(p[0][0], -1, modulus) % modulus)
        band.advance()
    need(len(images) == cap**4 and changes > 0, "nontrivial complete high-cube bijection")
    calls, visits = [], []
    def coefficient(prefix):
        if prefix == 0:
            band.set_digits(((0, 0, 0, 0),))
        high = band.read_field(0, 91, 1)
        visits.append(high)
        g = [[low[i][j]+q*high[2*i+j] for j in range(2)] for i in range(2)]
        p = projector(multiply(g, s, modulus), 1, modulus)
        result = -p[1][0]*pow(p[0][0], -1, modulus) % modulus
        calls.append(result)
        band.advance()
        return result
    count = cap**4 * modulus**2
    source = payload(count)
    out, traffic = add_site(source, cap**4, modulus, 1, 1, 16, coefficient)
    need(calls == coefficients*2 and visits[:81] == visits[81:], "same raw order and coefficients on merge")
    need(snapshot(out) == expected_add(coefficients, modulus, 1, 1, 1), "complete raw-prefix payload endpoint")
    wrong = list(reversed(coefficients))
    need(expected_add(wrong, modulus, 1, 1, 1) != snapshot(out), "header-order fault changes actual endpoint")
    inverse_calls = []
    def inverse_coefficient(prefix):
        value = -coefficient(prefix) % modulus
        inverse_calls.append(value)
        return value
    restored, _ = add_site(out, 81, modulus, 1, 1, 16, inverse_coefficient)
    need(snapshot(restored) == snapshot(source), "inverse site recomputation restores complete packet")
    return {"complete_high_matrices": 81, "records": count, "changed_high_coordinates": changes,
            "coefficient_histogram": dict(Counter(coefficients)), "payload_sha256": sha256(bytes(snapshot(out))).hexdigest(),
            "tape_operations": traffic}


def selected_site(copy, move):
    result = []
    # Exact raw fixtures extracted from pinned PR2234, before this adapter.
    # They prevent a matching error in fixture construction and preparation
    # from canceling an incorrect owner chart or image/kernel basis.
    raw_checkpoints = (
        ([(0,1,1),(0,2,1),(0,4,2),(0,7,1),(1,7,2),(2,7,2),(4,7,1),
          (7,1,1),(7,2,1),(7,4,2)],
         [(0,4,2),(1,7,2),(2,7,2),(7,0,1),(7,1,1),(7,2,1),(7,4,1),(7,7,1)]),
        ([(0,0,0),(0,1,1),(0,8,1),(8,0,1),(8,8,0)], [(1,1,1),(1,8,1)]),
    )
    for request, (low_entries, high_entries) in zip((copy, move), raw_checkpoints):
        expected_low, expected_high = eye(64), [[0]*64 for _ in range(64)]
        for i, j, value in low_entries:
            expected_low[i][j] = value
        for i, j, value in high_entries:
            expected_high[i][j] = value
        actual_low, actual_high = raw_fixture(request, 3, 2, high=1)
        need(actual_low == tuple(map(tuple, expected_low)) and
             actual_high == tuple(x for row in expected_high for x in row),
             "pinned selected raw fixture before new preparation")
        rows = []
        for high in range(3):
            low, digits = raw_fixture(request, 3, 2, high=high)
            band = FieldBand(3, (64,), (7,))
            band.set_digits((digits,))
            backend = Backend(3, 2, {7: (request, low)}, band, 0)
            program = compile_program(3, 2, 64, 1, ())
            c = head_coefficient(program, backend, 7, request.rank)
            need(c == (0, 6, 3)[high], "retained selected-site coefficient")
            rows.append(c)
        result.append({"request": request.record, "same_low_coefficients": rows})
    older = [raw_fixture(copy, 3, 2, high=t, unit_low=True) for t in range(3)]
    current_low, current_digits = raw_fixture(copy, 3, 2, high=0, row=63, unit_low=True)
    need(len({low for low, _ in older}) == 1, "one older low class")
    band = FieldBand(3, (64, 64), (11, 22), (1, 0, "#"), 1234)
    specs = {11: (copy, older[0][0]), 22: (copy, current_low)}
    backend = Backend(3, 2, specs, band, 1)
    program = compile_selected(3, 2, 4096, 1, ((GOOD, 11, 7, 0, False, False),), specs)
    calls, invocation_meters = [], []
    def coefficient(prefix, inverse=False):
        band.set_digits((older[prefix][1], current_digits))
        before = backend.meter.copy()
        value = head_coefficient(program, backend, 22, 63, inverse=inverse)
        audit_local_work(backend)
        invocation_meters.append(dict(backend.meter-before))
        calls.append(value)
        return value
    expected = [4, 7, 1]
    records = 3*2*9*2*9*2
    source = payload(records)
    output, traffic = add_site(source, 3, 9, 2, 2, 32, coefficient)
    need(calls == expected*2, "actual current and generated older coefficients")
    need(snapshot(output) == expected_add(expected, 9, 2, 2, 2), "selected coefficient reaches complete finite site")
    inverse_output, _ = add_site(output, 3, 9, 2, 2, 32, lambda p: coefficient(p, True))
    need(snapshot(inverse_output) == snapshot(source), "selected inverse site and scratch closure")
    need(band.tape.low_seen >= 1234, "decoder excludes parked ancestor")
    # Incoming weights cannot read the current field even though preparation can.
    fresh = reject(lambda: backend.table(1, 22, GOOD), "frozen slot excludes current field")
    wrong = reject(lambda: band.read_field(0, 22, 1), "exact raw field specification")
    need(not backend.page_open, "no retained numerical table after selected pass")
    return {"source_sites": result, "joined_site_coefficients": expected, "slice_records": records,
            "slice_scope": "Three selected64 raw-prefix snapshots, complete reduced before/X/middle/Y/suffix domains; not the selected64 full high cube or full 128-atom body.",
            "payload_sha256": sha256(bytes(snapshot(output))).hexdigest(),
            "local_control": dict(backend.meter), "payload_operations": traffic,
            "controls": {"current_capture": fresh, "wrong_source": wrong}}, (specs, older, current_digits)


def recursive_reference(events, tables, root_size, unit, modulus, index):
    """Attributed PR2188/2234 grammar; no serialized program or stack reuse."""
    sizes = [root_size]
    for kind, _code, rank, _field, _reverse, half in events:
        f = sizes[-1] // 64
        sizes.append(rank*f if kind == GOOD else f//2 if half else f)
    def value(level, coordinate):
        if level == 0:
            return unit % modulus
        kind, _code, _rank, field, reverse, _half = events[level-1]
        if kind == UNIT:
            return 1
        f = sizes[level-1] // 64
        pivots, diagonal, pi = tables[level-1]
        if kind == GOOD:
            return value(level-1, coordinate) * pivots[coordinate//f] % modulus
        j = f-1-coordinate if reverse else coordinate
        def bank(row):
            return value(level-1, row*f+j) if row < 64 else 1
        return diagonal[field] * bank(pi[field]) * pow(bank(field), -1, modulus) % modulus
    return value(len(events), index)


def chain_checks(copy):
    q, width, modulus, root_size = 3, 2, 9, 64**4+17
    bad_low, bad_digits = raw_fixture(copy, q, width, bad=True)
    good = [raw_fixture(copy, q, width, high=t, unit_low=True) for t in range(3)]
    specs = {11: (copy, good[0][0]), 33: (copy, bad_low), 44: (copy, good[0][0])}
    cases, controls, comparisons = [], {}, 0
    for label, middle in (
        ("pair_forward", (PAIR, 33, 7, 1, False, False)),
        ("pair_reverse", (PAIR, 33, 7, 126, True, False)),
        ("unit_reset", (UNIT, 33, 7, 0, False, False)),
        ("orientation_reset", (UNIT, 33, 7, 0, False, True)),
    ):
        events = ((GOOD, 11, 7, 0, False, False), middle, (GOOD, 44, 7, 0, False, False))
        program = compile_selected(q, width, root_size, 2, events, specs)
        final_size = program.get(3)[7]
        indices = sorted({0, final_size//2, final_size-1})
        outputs = []
        for variant in range(3):
            band = FieldBand(3, (64,)*3, (11, 33, 44))
            # Vary the live suffix; at the reset the first field is dead.
            fields = (good[0][1], bad_digits, good[variant][1])
            band.set_digits(fields)
            backend = Backend(q, width, specs, band, 3)
            tables = []
            for slot, event in enumerate(events):
                if event[0] == UNIT:
                    tables.append(((), (), ()))
                    continue
                request, low = specs[event[1]]
                p = prepare(request, low, fields[slot], q, width)
                if event[0] == GOOD:
                    tables.append((good_pivots(p, 7, modulus), (), ()))
                else:
                    diagonal, pi = fallback_table(p, modulus)
                    tables.append(((), diagonal, pi))
            observed = []
            for index in indices:
                actual = translated_value(program, backend, index, (0, 1, "#"), 10**20)
                expected = recursive_reference(events, tables, root_size, 2, modulus, index)
                need(actual == expected, "serialized machine refines retained recursive grammar")
                observed.append(actual)
                comparisons += 1
            if middle[0] == UNIT:
                need(set(backend.field_reads) == {2}, "reset keeps original live slot and avoids dead fields")
                band.set_digits((good[variant][1], bad_digits, good[variant][1]))
                need(evaluate(program, backend, 0) == observed[0], "dead high change leaves value unchanged")
                compact = FieldBand(3, (64, 64), (33, 44))
                compact.set_digits((bad_digits, good[variant][1]))
                controls[label + "_compacted_slots"] = reject(
                    lambda: evaluate(program, Backend(q, width, specs, compact, 3), 0),
                    "frozen slot excludes current field")
            else:
                need(observed[0] != (2, 5, 8)[variant], "pair continuation contributes a nonidentity factor")
            outputs.append(observed)
        need(len({row[0] for row in outputs}) > 1, "live high fields change a generated value")
        cases.append({"kind": label, "indices": indices, "values_by_live_high": outputs})
    controls["wrong_pair_orientation"] = reject(
        lambda: compile_program(q, width, root_size, 2, ((PAIR, 33, 7, 126, False, False),)),
        "physical pair orientation")
    controls["pair_on_good_class"] = reject(
        lambda: compile_selected(q, width, root_size, 2, ((PAIR, 11, 7, 1, False, False),), specs),
        "actual low-class descent branch")
    controls["wrong_selected_rank"] = reject(
        lambda: compile_selected(q, width, root_size, 2, ((GOOD, 11, 1, 0, False, False),), specs),
        "actual selected rank")
    return {"cases": cases, "coordinate_equalities": comparisons, "controls": controls}


def binding_controls(copy):
    q, width, modulus = 3, 2, 9
    low, digits = raw_fixture(copy, q, width)
    p = prepare(copy, low, digits, q, width)
    raw = [[low[i][j]+q*digits[64*i+j] for j in range(64)] for i in range(64)]
    wrong_raw = projector(raw, copy.rank, modulus)
    wrong_common = multiply(raw, reduce_matrix(copy.source_sigma, modulus), modulus)
    wrong_chart = multiply(multiply(wrong_common, reduce_matrix(copy.base, modulus), modulus),
                           inverse(wrong_common, modulus), modulus)
    need(p != wrong_raw and p != wrong_chart, "prepared/raw and COPY chart faults change the projector")
    need((p[0][0], wrong_chart[0][0]) == (4, 0), "source COPY projector witness")
    return {"raw_as_prepared": [p[1][0], wrong_raw[1][0]],
            "double_copy_chart": [p[0][0], wrong_chart[0][0]]}


def locality_checks(copy):
    low, digits = raw_fixture(copy, 3, 2, high=0, unit_low=True)
    receipts = []
    for origin, ancestor_size, spectator_bits in ((0, 0, 1), (8192, 257, 1024), (10**40, 1023, 4096)):
        ancestor = (1,)*ancestor_size
        band = FieldBand(3, (64,), (11,), ancestor, origin)
        band.set_digits((digits,))
        program = compile_selected(3, 2, 4096, 1, ((GOOD, 11, 7, 0, False, False),),
                                   {11: (copy, low)}, ancestor, origin)
        backend = Backend(3, 2, {11: (copy, low)}, band, 1)
        # Arbitrary spectator metadata has its own tape and no coefficient API.
        spectator = Tape()
        for _ in range(spectator_bits):
            spectator.append(1)
        spectator.rewind()
        spectator.meter.clear()
        owned = (band.tape, band.schema.tape, program.tape)
        before = [dict(t.cells) for t in owned]
        for tape in owned:
            tape.meter.clear()
        value = translated_value(program, backend, 0, ancestor, origin)
        need(value == 2 and not spectator.meter, "coefficient ignores arbitrary spectator metadata")
        need(before == [t.cells for t in owned], "readonly program and generated prefix")
        need(band.tape.head == program.tape.head == origin+1 and band.schema.tape.head == 1,
             "restore local input heads")
        need(min(band.tape.low_seen, program.tape.low_seen) >= origin, "no ancestor scan")
        receipts.append({"control": dict(backend.meter), "field": dict(band.tape.meter),
                         "schema": dict(band.schema.tape.meter), "program": dict(program.tape.meter)})
    need(receipts[0] == receipts[1] == receipts[2], "same local work under translation and spectator growth")
    return {"translations": [0, 8192, 10**40], "ancestor_lengths": [0, 257, 1023],
            "spectator_metadata_bits": [1, 1024, 4096], "identical_local_operations": receipts[0]}


def run():
    copy, move = requests()
    return {"decoder": decoder_checks(), "complete_pullback_cube": pullback_cube(),
            "selected_site": selected_site(copy, move)[0], "serialized_chains": chain_checks(copy),
            "source_binding_controls": binding_controls(copy), "locality": locality_checks(copy)}
