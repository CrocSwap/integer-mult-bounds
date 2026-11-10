"""Current coded positive rank-one Gaussian leaf with complete physical return.

Runtime widths and coordinates stay on encoded tapes. The exact C kernel,
finite carry, axis traversal and O(f V) tariff are inherited from #3091.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import ExitStack
from leaf_sources import activate, need

S = activate()
from cardinal_counts import Count, positive
from compact_counts import power_two
from encoded import compare, divide, subtract
from records import Tape
from scratch_pool import ScratchPool
from session import OuterScope, erase_marker
from stream import Counter

SCHEMA = S.header.SCHEMA


class LeafCohort:
    """Published symbol codec, without an unused ordinary/parking engine."""
    def __init__(self, tapes):
        S.codec.install_tape_methods()
        self.tapes = tuple(tapes)
        self.markers = []
        for tape in self.tapes:
            need(tape.head == 1 and tape.cells[0] in (2, 4)
                 and all(x == 4 for x in tape.cells[1:]), "compiled blank leaf baseline")
            self.markers.append(tape.cells[0])
        self.ports = None

    def bind(self, ports):
        need(len(ports) == len(self.tapes) and len(set(map(id, ports))) == len(ports),
             "exact fixed distinct leaf inventory")
        self.ports = tuple(ports)
        for tape, port in zip(self.tapes, ports):
            tape.native_port = S.codec.SymbolPort(port)

    def start(self):
        need(self.ports is not None, "leaf ports fixed before input")
        for tape, marker in zip(self.tapes, self.markers):
            tape.native_port.initialize(marker)
            tape.head = 1  # observer only; no runtime address is read

    def finish(self):
        for port in self.ports:
            S.abi.retire(port)


class Provider:
    NAMES = ("before", "selected", "after")

    def __init__(self, inverse=False):
        need(type(inverse) is bool, "compiled Gaussian direction")
        self.inverse = inverse
        with S.codec.collect_tapes() as tapes:
            self.engine = S.coefficient.CoefficientEngine(self.NAMES, "selected")
            self.pool = ScratchPool(128)
            self.scope = OuterScope(self.pool)
            self.bridge, self.field_guide, self.header_guide, self.length_guide = (Tape() for _ in range(4))
        self.cohort = LeafCohort(tapes)

    @property
    def port_count(self):
        return len(self.cohort.tapes)

    def bind(self, work):
        self.cohort.bind(work)

    def read_header(self, context):
        return S.header.Provider.read_header(self, context)

    def component_width(self, field):
        width = Count.literal(0)
        while field.read() in (0, 1):
            width.increment()
            field.move(1)
        need(field.read() == 2, "canonical signed component delimiter")
        remaining = Counter(width)
        try:
            while not remaining.finished:
                field.move(-1)
                remaining.decrement()
        finally:
            remaining.close()
        return width

    def prepare(self, header, h, cleanup):
        def own(value):
            cleanup.callback(value.close)
            return value
        for name in ("outer", "rows", "f", "K", "record_bits", "row_bits", "cutoff"):
            positive(header[name])
        one, two = own(Count.literal(1)), own(Count.literal(2))
        need(compare(h, two) >= 0 and compare(header["rho"], header["K"]) < 0,
             "signed width and current offset")
        need(compare(header["f"], header["cutoff"]) <= 0,
             "elementary PAID branch f <= cutoff")
        selected = own(Count.product(header["f"], header["K"]))
        end = own(Count(selected))
        end.add(header["active_start"])
        after = own(subtract(header["within_bits"], end))
        top = own(subtract(header["K"], one))
        rho = own(subtract(top, header["rho"]))
        complete = own(power_two(header["within_bits"]))
        row = own(Count.product(complete, header["record_bits"]))
        need(compare(row, header["row_bits"]) == 0, "exact complete coded row extent")
        pair = own(Count(h))
        pair.increment()
        pair.multiply_small(6)
        coefficients, remainder = divide(header["record_bits"], pair)
        own(coefficients); own(remainder)
        need(remainder.zero(), "record_bits equals 6 r (h+1)")
        positive(coefficients)
        rows = own(Count.product(header["outer"], header["rows"]))
        return (header["active_start"], selected, after), rho, coefficients, rows

    def rewind_field(self, field):
        self.field_guide.rewind()
        while self.field_guide.read() != 4:
            need(self.field_guide.read() == 1, "complete field guide")
            field.move(-1)
            self.field_guide.step(1)
        self.field_guide.rewind()

    def import_field(self, field, h):
        while field.read() != 4:
            for _ in (0, 1):
                remaining = Counter(h)
                try:
                    while not remaining.finished:
                        bit = field.read()
                        need(bit in (0, 1), "complete uniform signed field")
                        self.bridge.append(bit)
                        self.field_guide.append(1)
                        field.move(1)
                        remaining.decrement()
                finally:
                    remaining.close()
                need(field.read() == 2, "exact component delimiter")
                self.field_guide.append(1)
                field.move(1)
        self.bridge.rewind()
        self.rewind_field(field)

    def export_field(self, field, returned, h):
        returned.rewind(); self.field_guide.rewind()
        while returned.read() != 4:
            for _ in (0, 1):
                remaining = Counter(h)
                try:
                    while not remaining.finished:
                        bit = returned.read()
                        need(bit in (0, 1) and field.read() in (0, 1)
                             and self.field_guide.read() == 1, "complete returned signed component")
                        field.write(bit)
                        field.move(1); returned.step(1); self.field_guide.step(1)
                        remaining.decrement()
                finally:
                    remaining.close()
                need(field.read() == 2 and self.field_guide.read() == 1,
                     "preserved component delimiter")
                field.move(1); self.field_guide.step(1)
        need(field.read() == self.field_guide.read() == 4, "exact complete return extent")
        self.rewind_field(field)
        self.field_guide.clear()
        returned.rewind()

    def run(self, field, context):
        """In-place current leaf; preserve parent on named arithmetic rejection.

        Caller guarantees genuinely disjoint complete physical segments, valid
        context/format, signed exactness and the completed shape/leaf premise.
        Object guards reject obvious aliases but not hidden overlapping wrappers.
        """
        need(self.cohort.ports is not None and field.tape is not context.tape
             and all(field.tape is not port and context.tape is not port for port in self.cohort.ports),
             "distinct current field, context and owned work")
        self.cohort.start()
        try:
            with S.codec.execution(), self.scope.installed(), ExitStack() as cleanup:
                header = self.read_header(context)
                for value in header.values():
                    cleanup.callback(value.close)
                h = self.component_width(field)
                cleanup.callback(h.close)
                widths, rho, coefficients, rows = self.prepare(header, h, cleanup)
                self.import_field(field, h)
                with self.scope.suspended():
                    returned = self.engine.run_leaf(self.bridge, widths, header["f"], header["K"],
                        rho, h, coefficients, rows, self.inverse)
                self.export_field(field, returned, h)
                returned.clear(); erase_marker(returned); self.bridge.clear()
            self.pool.empty()
        finally:
            self.cohort.finish()
