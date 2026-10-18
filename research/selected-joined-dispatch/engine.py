"""Joined normalizers, generated controls and completed embedded children.

The payload path uses only sequential record tapes. Dense address maps live
in the separate checker. The generic caller uses two complementary m=2
projectors and makes no claim about the selected64 owner/hosting schedule.
"""
from collections import Counter
from dataclasses import dataclass, replace
from math import prod

from algebra import Header, fallback, gl2, good, lifts, need
from control import Program, value
from parking import Parking
from streams import RecordMeter, Shape, Tape, add_pass, copy, ordinary_swap, sign_pass


@dataclass(frozen=True)
class ChildRequest:
    shape: Shape
    program: Program
    prefix_count: int
    records: int
    parent_atoms: int
    label: str

    def admit(self, source, histories):
        need(0 < self.shape.atoms < self.parent_atoms, "proper completed child")
        need(len(histories) == self.prefix_count and len(source.records) == self.records
             == self.prefix_count * self.shape.records, "one complete high packet at child entry")
        need(self.program.size == self.shape.atoms and
             all(len(h) == self.program.depth for h in histories), "child global field scope")
        need(source.head == 0, "child entry head origin")


class Engine:
    def __init__(self, leaf_cutoff=1, fault=None, recurse_one_unit=False):
        self.leaf_cutoff, self.fault = leaf_cutoff, fault
        need(leaf_cutoff >= 1, "positive completed-leaf cutoff")
        self.recurse_one_unit, self.unit_recursed = recurse_one_unit, False
        self.meter = RecordMeter()
        self.control = Counter()
        self.parking = Parking(self.meter)
        self.calls = []
        self.node_calls = 0
        self.residuals = Counter()
        self.skipped_reversal = False
        self.last_request = None

    def weight(self, program, history, index):
        return value(program, history, index, self.control,
                     low_only=self.fault == "low_only_generated_header")

    def leaf(self, source, histories, shape, program):
        need(program.size == shape.atoms and len(source.records) == len(histories) * shape.records,
             "completed leaf extent")
        for i in range(shape.atoms):
            first, second = i, 2 * shape.atoms - 1 - i
            def swap(tape):
                return ordinary_swap(tape, shape, first, second, program.q, program.width)
            def coefficient(history): return self.weight(program, history, i)
            source = swap(source)
            source = add_pass(source, shape, histories, first, second, coefficient)
            source = swap(source)
            source = add_pass(source, shape, histories, first, second,
                              lambda h: -pow(coefficient(h), -1, shape.modulus) % shape.modulus)
            source = swap(source)
            source = add_pass(source, shape, histories, first, second, coefficient)
            source = swap(source)
            source = sign_pass(source, shape, second)
        need(source.head == 0 and len(source.records) == len(histories) * shape.records,
             "completed leaf return")
        self.meter["completed_leaves"] += 1
        return source

    def dispatch(self, source, histories, headers, shape, program,
                 first, second, width, kind, label, field=0, reverse=False):
        child_shape = shape.child(first, second, width)
        child_program = program.child(kind, headers[0], size=width, field=field, reverse=reverse)
        need(child_program.size == width, "generated descriptor and emitted width")
        frozen = tuple(history + (header,) for history, header in zip(histories, headers))
        if (self.fault == "compact_history_after_reset" and program.steps
                and program.steps[-1].kind == "unit"):
            frozen = tuple(h[program.depth:] for h in frozen)
        elif self.fault == "compact_history" and program.depth:
            frozen = tuple(h[1:] for h in frozen)
        request = ChildRequest(child_shape, child_program, len(histories), len(source.records),
                               shape.atoms, label)
        request.admit(source, frozen)
        self.last_request = request
        self.calls.append((shape.atoms, width, len(histories), len(source.records),
                           child_program.depth, label))
        result = self.caller(source, frozen, child_shape, child_program)
        request.admit(result, frozen)
        return result

    def execute_good(self, source, histories, headers, shape, program):
        m, f, rank = headers[0].dimension, shape.atoms // headers[0].dimension, len(headers[0].axes)
        forms = tuple(good(h) for h in headers)
        schedule = []
        for j in range(f):
            for index, (i, k, _) in enumerate(forms[0].rows):
                schedule.append(("head", i * f + j, k * f + j, index, j, 1))
            for index, (i, k, _) in enumerate(forms[0].columns):
                schedule.append(("tail", m * f + i * f + f - 1 - j,
                                 m * f + k * f + f - 1 - j, index, j, -1))
            for i in range(m):
                for k in range(m):
                    schedule.append(("cross", m * f + i * f + f - 1 - j, k * f + j, i * m + k, j, 1))
        controls = tuple(zip(histories, forms))
        def execute_slot(tape, slot):
            kind, target, src, index, j, sign = slot
            def coefficient(control):
                history, form = control
                def a(i): return self.weight(program, history, i * f + j)
                if kind == "head":
                    i, k, c = form.rows[index]
                    result = c * a(i) * pow(a(k), -1, shape.modulus)
                elif kind == "tail":
                    result = form.columns[index][2]
                else:
                    i, k = divmod(index, m)
                    result = form.cross[i][k] * pow(a(k), -1, shape.modulus)
                return sign * result % shape.modulus
            return add_pass(tape, shape, controls, src, target, coefficient)
        for slot in schedule:
            source = execute_slot(source, slot)
        width = rank * f
        source = self.dispatch(source, histories, headers, shape, program,
                               0, 2 * m * f - width, width, "good", "good residual")
        for slot in reversed(schedule):
            source = execute_slot(source, (*slot[:5], -slot[5]))
        return source

    def execute_fallback(self, source, histories, headers, shape, program):
        forms = tuple(fallback(h) for h in headers)
        signature = lambda form: tuple((op.kind, op.target, op.source, op.weight_kind) for op in form.operations)
        need(all(signature(form) == signature(forms[0]) for form in forms), "one low-class fallback schedule")
        m, f = headers[0].dimension, shape.atoms // headers[0].dimension
        controls = tuple(zip(histories, forms))
        for position, operation in enumerate(forms[0].operations):
            if operation.kind == "lower":
                for j in range(f):
                    target = operation.target * f + (j if operation.target < m else f - 1 - j)
                    src = operation.source * f + (j if operation.source < m else f - 1 - j)
                    def coefficient(control):
                        history, form = control
                        op = form.operations[position]
                        def bank(row):
                            return self.weight(program, history, row * f + j) if row < m else 1
                        return (op.scalar * bank(op.permutation[op.first]) *
                                pow(bank(op.permutation[op.second]), -1, shape.modulus)) % shape.modulus
                    source = add_pass(source, shape, controls, src, target, coefficient)
            elif operation.kind == "sign":
                for j in range(f):
                    source = sign_pass(source, shape, operation.target * f + j)
            else:
                i, k = operation.target, operation.source
                need(i < k, "ordered fallback pair")
                same = (i < m) == (k < m)
                def reversal(tape, before):
                    if not same or not f // 2:
                        return tape
                    if before and self.fault == "omit_reversal" and not self.skipped_reversal:
                        self.skipped_reversal = True
                        return tape
                    return self.dispatch(tape, histories, headers, shape, program,
                                         k * f, (k + 1) * f - f // 2, f // 2,
                                         "unit", "orientation reversal")
                source = reversal(source, True)
                source = self.dispatch(source, histories, headers, shape, program, i * f, k * f, f,
                                       operation.weight_kind, "fallback " + operation.weight_kind,
                                       field=i, reverse=i >= m)
                source = reversal(source, False)
        return source

    def residual(self, source, histories, headers, shape, program):
        need(len(headers) == len(histories) and headers, "all current high headers")
        need(all(h.specification == headers[0].specification for h in headers), "one current low class")
        need(shape.atoms % headers[0].dimension == 0 and program.size == shape.atoms,
             "residual atom blocks")
        low = Header(headers[0].q, headers[0].width, headers[0].low, headers[0].axes)
        try:
            good(low)
            branch = "good"
        except ValueError:
            branch = "fallback"
        self.residuals[branch] += 1
        if branch == "good":
            return self.execute_good(source, histories, headers, shape, program)
        return self.execute_fallback(source, histories, headers, shape, program)

    def node_packet(self, source, histories, headers, shape, program, observer=None):
        """One complete high packet; the same header returns after both residuals."""
        need(all(h.dimension == 2 for h in headers), "complementary two-dimensional caller")
        for axis in (0, 1):
            current = tuple(replace(h, axes=(axis,)) for h in headers)
            source = self.residual(source, histories, current, shape, program)
            if observer is not None:
                observer(axis, source)
        need(source.head == 0, "two-residual return head")
        self.node_calls += 1
        return source

    def caller(self, source, histories, shape, program):
        need(len(source.records) == len(histories) * shape.records and shape.atoms == program.size,
             "complete caller input")
        force = (self.recurse_one_unit and not self.unit_recursed and shape.atoms > 1
                 and program.steps and program.steps[-1].kind == "unit")
        if force:
            self.unit_recursed = True
            self.meter["unit_reset_internal_calls"] += 1
        if shape.atoms <= self.leaf_cutoff and not force:
            return self.leaf(source, histories, shape, program)
        need(shape.atoms % 2 == 0, "generic caller uses even atom widths")
        low_classes = gl2(program.q)
        high_count = program.q**(4 * (program.width - 1))
        stock = len(low_classes) * high_count
        need(shape.unused % stock == 0, "fresh complete GL2 stock")
        self.meter["fresh_stock_calls"] += 1
        self.meter["fresh_low_packets"] += len(low_classes)
        child_shape = replace(shape, unused=shape.unused // stock)
        block = child_shape.records
        for low_index, low in enumerate(low_classes):
            headers = tuple(lifts(low, program.q, program.width))
            selected = Tape(self.meter)
            source.rewind()
            before, take = low_index * high_count * block, high_count * block
            after = shape.records - before - take
            expanded_histories, current = [], []
            for history in histories:
                source.skip(before); copy(source, selected, take); source.skip(after)
                expanded_histories.extend([history] * high_count)
                current.extend(headers)
            source.finished(); source.rewind(); selected.rewind()
            frame = self.parking.push(source)
            try:
                result = self.node_packet(selected, tuple(expanded_histories), tuple(current),
                                          child_shape, program)
            finally:
                source = self.parking.pop(frame)
            replacement = Tape(self.meter)
            result.rewind()
            for _ in histories:
                copy(source, replacement, before)
                source.skip(take); copy(result, replacement, take)
                copy(source, replacement, after)
            source.finished(); result.finished()
            source.erase(); result.erase(); replacement.rewind()
            source = replacement
        return source
