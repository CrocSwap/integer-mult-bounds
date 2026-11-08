"""Execute source-emitted global switches through the retained physical root.

Unbounded integers, positions and countdowns remain encoded on Count tapes.
Payload arithmetic below uses only binary digits and a one-bit carry. The
constructor and source-control preparation are outside a sealed invocation.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
Retained physical root/router/Count/ownership implementations are credited.
"""
from composed_sources import active
active()
from composed_engine import ComposedRoot, production_layer
from cardinal_counts import Count, positive
from compact_counts import append_bits, copy_bits, power_two
from encoded import compare, subtract
from frontend import END, HADAMARD, SIGNS, HALF
from grid_boundary import GridBoundary
from records import Tape
from router_metadata import owned
from scratch_pool import ScratchPool
from session import (OuterScope, borrowed_count, borrowed_tape, erase_marker,
                     initialize_marker, sealed_constructors)
from stream import Counter
from words import BLANK, LEFT, need


def digit(source):
    value = source.read()
    need(value in (0, 1), "complete binary compiler control or payload")
    source.step(1)
    return value


def repeat_copy(source, target, count, flip=0):
    source.rewind()
    remaining = Counter(count)
    try:
        while not remaining.finished:
            target.append(digit(source) ^ flip)
            remaining.decrement()
        need(source.read() == BLANK, "complete phase-product prefix")
    finally:
        source.rewind()
        remaining.close()


class GlobalBoundary:
    """One fixed owner; the caller consumes its protected output before reuse."""
    def __init__(self, root, observe=None):
        need(isinstance(root, ComposedRoot), "actual authenticated composed-H owner")
        self.root = root
        # Optional checker instrumentation; return values never affect control.
        # Production has no host counter update for each payload coefficient.
        self.observe = observe
        self.grid = GridBoundary()
        self.pool = ScratchPool(128)
        self.scope = OuterScope(self.pool)
        self.output = Tape()
        self.current = None
        self.closed = True
        self.calls = dict(gathers=0, raw_H=0, signs=0, exact_divisions=0)
        for tape in (*self.pool.tapes, self.output):
            erase_marker(tape)

    def idle(self):
        self.root.idle()
        need(self.root.closed and self.root.current is None and self.root.output.read() == BLANK
             and self.grid.closed and self.grid.output.read() == BLANK,
             "consumed complete global-H children")

    def rearm(self):
        need(self.closed and self.current is None and self.output.read() == BLANK,
             "consume the previous compiler-boundary output")
        self.idle()
        initialize_marker(self.output)
        for tape in self.pool.tapes:
            initialize_marker(tape)
        self.closed = False

    def accept(self, returned):
        following = self.pool.acquire()
        try:
            append_bits(returned, following)
            following.rewind()
        except BaseException:
            following.clear()
            raise
        finally:
            returned.clear()
            erase_marker(returned)
        self.current.clear()
        self.current = following

    def replace_owned(self, following):
        following.rewind()
        self.current.clear()
        self.current = following

    def gather(self, descriptor, n, precision, support, position_width, width, coefficients, rows):
        self.idle()
        with owned(Count.product(width, coefficients)) as (record,):
            record.multiply_small(2)
            with self.scope.suspended():
                returned = self.root.router.run(
                    borrowed_tape(self.current), borrowed_tape(descriptor),
                    *(borrowed_count(x) for x in (n, precision, support, position_width, record, rows)))
            self.accept(returned)
        self.calls["gathers"] += 1

    def raw_h(self, positions, n, g, position_width, width, coefficients, rows, gaussians):
        # P=w+g; using the physical word width, |z|<2^(w-p) is automatic.
        # The g low zeros encode z/2^(w-p) on the P-grid. All H0 return
        # numerators are divisible as needed, so its final truncation is exact.
        with owned(Count(width), Count.literal(2)) as (precision, two):
            precision.add(g)
            self.idle()
            with self.scope.suspended():
                returned = self.grid.expand(borrowed_tape(self.current),
                    *(borrowed_count(x) for x in (width, g, two, gaussians)))
            self.accept(returned)
            self.idle()
            with self.scope.suspended():
                returned = self.root.run(borrowed_tape(self.current), borrowed_tape(positions),
                    *(borrowed_count(x) for x in (n, precision, g, position_width, coefficients, rows)))
            self.accept(returned)
            result_width = Count(precision)
            result_width.add(two)
        self.calls["raw_H"] += 1
        return result_width

    def product_signs(self, code, coarse_blocks, axes, axis_size):
        """Sequential Kronecker expansion costs a geometric sum, not g per bit.

        The code cursor is deliberately advanced over this one diagonal's
        tables. The enclosing program restores its borrowed head on return.
        """
        output = self.pool.acquire()
        blocks = Counter(coarse_blocks)
        current = following = None
        try:
            while not blocks.finished:
                current = self.pool.acquire()
                current.append(0)
                current.rewind()
                length = Count.literal(1)
                remaining_axes = Counter(axes)
                try:
                    while not remaining_axes.finished:
                        following = self.pool.acquire()
                        entries = Counter(axis_size)
                        try:
                            while not entries.finished:
                                bit = digit(code)
                                if self.observe is not None:
                                    self.observe("control_bits")
                                repeat_copy(current, following, length, bit)
                                entries.decrement()
                        finally:
                            entries.close()
                        current.clear()
                        current, following = following, None
                        current.rewind()
                        updated = Count.product(length, axis_size)
                        length.close()
                        length = updated
                        remaining_axes.decrement()
                    append_bits(current, output)
                finally:
                    length.close()
                    remaining_axes.close()
                    if current is not None:
                        current.clear()
                        current = None
                blocks.decrement()
            output.rewind()
            return output
        except BaseException:
            output.clear()
            raise
        finally:
            blocks.close()
            for value in (current, following):
                if value is not None:
                    value.clear()

    def signed_component(self, source, output, width, negate):
        remaining = Counter(width)
        carry = int(negate)
        old_sign = new_sign = 0
        try:
            while not remaining.finished:
                old_sign = digit(source)
                total = (old_sign ^ int(negate)) + carry
                new_sign = total & 1
                carry = total >> 1
                output.append(new_sign)
                remaining.decrement()
            need(not (negate and old_sign and new_sign), "signed phase headroom")
        finally:
            remaining.close()

    def apply_signs(self, mask, width, addresses, coefficients, rows):
        following = self.pool.acquire()
        remaining_rows = Counter(rows)
        self.current.rewind()
        try:
            while not remaining_rows.finished:
                mask.rewind()
                remaining_addresses = Counter(addresses)
                try:
                    while not remaining_addresses.finished:
                        sign = digit(mask)
                        if self.observe is not None:
                            self.observe("mask_bits")
                        remaining_coefficients = Counter(coefficients)
                        try:
                            while not remaining_coefficients.finished:
                                for _ in (0, 1):
                                    self.signed_component(self.current, following, width, sign)
                                    if sign and self.observe is not None:
                                        self.observe("component_negations")
                                remaining_coefficients.decrement()
                        finally:
                            remaining_coefficients.close()
                        remaining_addresses.decrement()
                    need(mask.read() == BLANK, "complete original-frame product diagonal")
                finally:
                    remaining_addresses.close()
                remaining_rows.decrement()
            need(self.current.read() == BLANK, "complete global diagonal payload")
            self.replace_owned(following)
            following = None
            self.calls["signs"] += 1
        finally:
            remaining_rows.close()
            self.current.rewind()
            mask.rewind()
            if following is not None:
                following.clear()

    def exact_divide(self, width, low, output_width, gaussians):
        # Check discarded bits before calling a generic toward-zero codec.
        # An accidentally rounded switch is not an admitted exact switch.
        with owned(subtract(width, low), Count(gaussians)) as (kept, components):
            components.multiply_small(2)
            remaining = Counter(components)
            self.current.rewind()
            try:
                while not remaining.finished:
                    discard = Counter(low)
                    try:
                        while not discard.finished:
                            need(digit(self.current) == 0, "exact compiled switch divisibility")
                            discard.decrement()
                    finally:
                        discard.close()
                    retain = Counter(kept)
                    try:
                        while not retain.finished:
                            digit(self.current)
                            retain.decrement()
                    finally:
                        retain.close()
                    remaining.decrement()
                need(self.current.read() == BLANK, "complete exact switch quotient")
            finally:
                self.current.rewind()
                remaining.close()
        self.idle()
        with self.scope.suspended():
            returned = self.grid.truncate(borrowed_tape(self.current),
                *(borrowed_count(x) for x in (width, low, output_width, gaussians)))
        self.accept(returned)
        self.calls["exact_divisions"] += 1

    def run(self, payload, forward, inverse, program, n, p, initial_width, g, local_bits,
            position_width, support, coefficients, rows):
        """Run one complete emitted Beneš route on every original coarse label.

        Input/output fields are signed integers with the same external p-grid.
        All descriptors are borrowed; the physical result is a protected port.
        """
        source, code = borrowed_tape(payload), borrowed_tape(program)
        need(source is not self.output and code is not self.output and source is not code,
             "distinct borrowed compiler payload and program")
        for value in (n, initial_width, g, local_bits, position_width, coefficients, rows):
            positive(value)
        need(compare(initial_width, p) >= 0, "signed component width covers the external grid")
        self.rearm()
        width = positions = mask = None
        source.rewind()
        code.rewind()
        try:
            with sealed_constructors(), self.scope.installed():
                with owned(Count.literal(2)) as (two,):
                    need(compare(initial_width, two) >= 0, "signed component width at least two")
                with owned(Count.product(g, local_bits), power_two(n), power_two(local_bits),
                           Count(initial_width)) as (local_total, addresses, axis_size, route_precision):
                    need(compare(local_total, n) <= 0, "complete microbox layout fits global address")
                    route_precision.add(g)
                    with owned(subtract(n, local_total)) as (coarse_bits,):
                        with owned(power_two(coarse_bits), Count.product(addresses, coefficients)) as (coarse_blocks, one_row):
                            with owned(Count.product(one_row, rows)) as (gaussians,):
                                with owned(Count.product(gaussians, initial_width)) as (total,):
                                    total.multiply_small(2)
                                    self.current = self.pool.acquire()
                                    copy_bits(source, self.current, total)
                                need(source.read() == BLANK, "complete original global Gaussian packet")
                                source.rewind()
                                self.current.rewind()
                                self.gather(forward, n, route_precision, support, position_width,
                                            initial_width, coefficients, rows)
                                width = Count(initial_width)
                                state = 0  # Four finite states per complete source switch.
                                while True:
                                    opcode = digit(code) | (digit(code) << 1)
                                    if opcode == END:
                                        need(state == 0 and code.read() == BLANK, "complete compiled global route")
                                        break
                                    need(opcode == (HADAMARD, SIGNS, HADAMARD, HALF)[state],
                                         "chronological complete source switch")
                                    if opcode == HADAMARD:
                                        positions = self.pool.acquire()
                                        with owned(Count.product(g, position_width)) as (bits,):
                                            copy_bits(code, positions, bits)
                                        positions.rewind()
                                        following = self.raw_h(positions, n, g, position_width,
                                                               width, coefficients, rows, gaussians)
                                        positions.clear()
                                        positions = None
                                        width.close()
                                        width = following
                                    elif opcode == SIGNS:
                                        mask = self.product_signs(code, coarse_blocks, g, axis_size)
                                        self.apply_signs(mask, width, addresses, coefficients, rows)
                                        mask.clear()
                                        mask = None
                                    else:
                                        self.exact_divide(width, g, initial_width, gaussians)
                                        width.close()
                                        width = Count(initial_width)
                                    state = (state+1) % 4
                                self.gather(inverse, n, route_precision, support, position_width,
                                            width, coefficients, rows)
                                self.idle()
                                append_bits(self.current, self.output)
                if width is not None:
                    width.close()
                    width = None
                self.current.clear()
                self.current = None
                self.pool.empty()
        finally:
            source.rewind()
            code.rewind()
            forward.rewind()
            inverse.rewind()
            for value in (width, positions, mask, self.current):
                if value is not None:
                    value.close() if isinstance(value, Count) else value.clear()
            self.current = None
            # Success restores every owned role. Interrupted child execution
            # retains the predecessor's narrower successful-input contract.
            if not self.pool.live:
                for tape in self.pool.tapes:
                    erase_marker(tape)
            self.output.rewind()
            self.closed = True
        return self.output


def production_boundary():
    """Bind the source compiler interface to two actual fresh production natives.

    As in the predecessor, compilation has a fixed construction-dependent cost.
    Finite verification uses its declared q=2 fixture rather than allocating the
    full production native source. It does not change this production factory.
    """
    return GlobalBoundary(production_layer())
