"""Serialized refinement of PR2310's iterative generated-weight evaluator.

The program, pending/value stacks and temporary table pages use tape symbols.
Bounded decoded operands and arithmetic use host integers under the separate
schoolbook lowering. Exact field-code equality binds the source vocabulary.
"""
from collections import Counter
from math import gcd

from algebra import fallback_table, good_pivots
from selected import prepare
from tapes import Records, Stack, need


GOOD, PAIR, UNIT = 0, 1, 2


def compile_program(q, width, size, unit, events, ancestor=(), origin=0):
    need(q >= 3 and q % 2 and width >= 1 and size > 0 and gcd(unit, q) == 1,
         "root ring, extent and unit")
    rows = [(q, width, size, unit, len(events))]
    for kind, code, rank, field, reverse, half in events:
        f = size // 64
        need(f > 0 and 1 <= rank <= 42 and kind in (GOOD, PAIR, UNIT), "selected step")
        need((kind == PAIR and 0 <= field < 127 and reverse == (field >= 64)) or
             (kind != PAIR and field == 0 and not reverse), "physical pair orientation")
        need(kind == UNIT or not half, "orientation reset")
        child = rank*f if kind == GOOD else f//2 if half else f
        need(0 < child < size, "proper serialized child")
        rows.append((kind, code, rank, field, int(reverse), int(half), size, child))
        size = child
    return Records(rows, ancestor, origin)


def compile_selected(q, width, size, unit, events, specifications, ancestor=(), origin=0):
    """Admit the retained Good/Pair/unit grammar using actual selected lows.

    This uses the proved selected residual grammar, not a replay of the full
    family/owner macroplan. The source vocabulary has already bound requests.
    """
    for kind, code, rank, _field, _reverse, _half in events:
        need(code in specifications, "selected source vocabulary")
        request, low = specifications[code]
        need(rank == request.rank, "actual selected rank")
        p = prepare(request, low, (0,)*4096, q, 1)
        try:
            good_pivots(p, rank, q)
            good = True
        except ValueError as error:
            need(str(error) == "nongeneric low class", "low-class preparation")
            good = False
        need(good == (kind == GOOD), "actual low-class descent branch")
    return compile_program(q, width, size, unit, events, ancestor, origin)


class Backend:
    """Finite source vocabulary plus the canonical generated-field band.

    A code identifies an exact (request, raw low) pair. With fixed q and the
    selected catalogue this vocabulary is finite, independently of w/e.
    """
    def __init__(self, q, width, specifications, band, depth):
        self.q, self.width = q, width
        self.specifications, self.band, self.depth = specifications, band, depth
        self.meter = Counter()
        self.field_reads = []
        self.page_open = False

    def projector(self, slot, code, scope):
        need(code in self.specifications, "known exact source code")
        digits = self.band.read_field(slot, code, scope)
        request, low = self.specifications[code]
        self.field_reads.append(slot)
        self.meter["full_ring_preparations"] += 1
        return prepare(request, low, digits, self.q, self.width)

    def table(self, slot, code, kind):
        need(not self.page_open, "no live numerical page at preparation entry")
        p = self.projector(slot, code, self.depth)
        request, _low = self.specifications[code]
        modulus = self.q ** self.width
        pivots, diagonal, permutation = (1,)*64, (1,)*128, tuple(range(128))
        if kind == GOOD:
            pivots = good_pivots(p, request.rank, modulus) + (1,)*(64-request.rank)
        else:
            need(kind == PAIR, "coefficient-bearing table")
            diagonal, permutation = fallback_table(p, modulus)
        page = Records((pivots, diagonal, permutation))
        self.page_open = True
        decoded = tuple(page.get(i) for i in range(3))
        page.tape.clear()
        need(page.tape.read() is None, "erase numerical table page")
        self.page_open = False
        self.meter.update({"table_" + k: v for k, v in page.tape.meter.items()})
        return decoded


def evaluate(program, backend, index, work=None):
    q, width, root_size, unit, depth = program.get(0)
    need((q, width, depth) == (backend.q, backend.width, backend.depth), "one bound control context")
    final_size = program.get(depth)[7] if depth else root_size
    need(0 <= index < final_size, "final generated index")
    modulus = q ** width
    pending, values = (Stack(), Stack()) if work is None else work
    need(pending.empty() and values.empty(), "marked-empty local continuation roles")
    backend.last_work = (pending, values)  # Checker observation only.
    pending.push((0, depth, index))
    while not pending.empty():
        event = pending.pop()
        backend.meter["continuation_records"] += 1
        if event[0] == 1:
            values.push((event[1],))
        elif event[0] == 2:
            value, = values.pop()
            values.push((value * event[1] % modulus,))
            backend.meter["ring_macros"] += 1
        elif event[0] == 3:
            denominator, = values.pop()
            numerator, = values.pop()
            need(gcd(denominator, modulus) == 1, "generated denominator unit")
            values.push((event[1] * numerator * pow(denominator, -1, modulus) % modulus,))
            backend.meter["ring_macros"] += 3
        else:
            need(event[0] == 0, "finite continuation tag")
            _, level, coordinate = event
            backend.meter["weight_requests"] += 1
            if level == 0:
                need(coordinate < root_size, "root coordinate")
                values.push((unit % modulus,))
                continue
            kind, code, rank, field, reverse, half, parent_size, size = program.get(level)
            need(coordinate < size, "serialized child coordinate")
            if kind == UNIT:
                values.push((1,))
                continue
            pivots, diagonal, permutation = backend.table(level-1, code, kind)
            f = parent_size // 64
            if kind == GOOD:
                pending.push((2, pivots[coordinate // f]))
                pending.push((0, level-1, coordinate))
            else:
                need(kind == PAIR, "serialized generated kind")
                j = f-1-coordinate if reverse else coordinate
                pending.push((3, diagonal[field]))
                for row in (field, permutation[field]):
                    pending.push((0, level-1, row*f+j) if row < 64 else (1, 1))
    result, = values.pop()
    need(values.empty() and pending.empty() and not backend.page_open, "closed local evaluation")
    need(gcd(result, modulus) == 1, "completed unit result")
    for name, stack in (("pending", pending), ("values", values)):
        backend.meter.update({name + "_" + k: v for k, v in stack.tape.meter.items()})
        backend.meter.update({name + "_reverse_" + k: v for k, v in stack.reverse.meter.items()})
    return result


def head_coefficient(program, backend, current_code, target_row, column=0, inverse=False):
    _q, _w, root_size, _unit, depth = program.get(0)
    size = program.get(depth)[7] if depth else root_size
    f = size // 64
    need(f > 0 and 0 < target_row < 64 and 0 <= column < f, "selected first-column head slot")
    p = backend.projector(depth, current_code, depth+1)
    modulus = backend.q ** backend.width
    ell = -p[target_row][0] * pow(p[0][0], -1, modulus) % modulus
    numerator = evaluate(program, backend, target_row*f+column)
    denominator = evaluate(program, backend, column)
    result = ell * numerator * pow(denominator, -1, modulus) % modulus
    need(not backend.page_open, "numerical page closed before payload")
    return -result % modulus if inverse else result
