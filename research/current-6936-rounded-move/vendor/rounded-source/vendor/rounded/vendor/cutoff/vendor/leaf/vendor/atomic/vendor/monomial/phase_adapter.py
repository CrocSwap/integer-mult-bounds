"""Paid current signed-format and 23-field context join to unchanged #3087.

Runtime shapes stay on encoded Count tapes. The complete untouched back suffix
is folded into additional coefficient fields, so every one receives its phase.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from contextlib import ExitStack
from phase_binding import activate, need

S = activate()
from cardinal_counts import Count, positive
from compact_counts import power_two
from encoded import compare, divide, subtract
from records import Tape
from scratch_pool import ScratchPool
from session import OuterScope, erase_marker
from stream import Counter
from codec import Cohort, collect_tapes, execution

SCHEMA = S.provider.SCHEMA


def scale(value, multiplier):
    need(type(multiplier) is int and multiplier >= 0, "fixed template multiplier")
    if multiplier == 0:
        return Count.literal(0)
    out = Count(value)
    if multiplier != 1:
        out.multiply_small(multiplier)
    return out


class Provider:
    def __init__(self, literal, native_factory, inverse=False):
        need(type(inverse) is bool, "compiled monomial direction")
        self.rank = len(literal["matrix_rows"])
        need(1 <= self.rank <= 73, "fixed source monomial rank")
        self.inverse = inverse
        self.vectors = tuple("v" + str(i) for i in range(self.rank))
        self.names = ("u", "u_rest", "t", "t_rest", "before", *self.vectors, "after", "b")
        with collect_tapes() as tapes:
            native = native_factory()
            need(type(native) is S.source.ordinary.Ordinary and native.observe is None
                 and native.runtime.observe is None, "same closed ordinary supplier without payload callback")
            self.engine = S.engine.MonomialEngine(self.names, self.vectors, literal, native)
            self.pool = ScratchPool(192)
            self.scope = OuterScope(self.pool)
            self.bridge, self.field_guide, self.header_guide, self.length_guide = (Tape() for _ in range(4))
        self.cohort = Cohort(tapes, native)
        self.calls = 0

    @property
    def port_count(self):
        return self.cohort.port_count

    def bind(self, work):
        self.cohort.bind(work)

    def read_header(self, context):
        return S.provider.Provider.read_header(self, context)

    def component_width(self, field):
        """Read only the first component's format length, never its integer."""
        width = Count.literal(0)
        while field.read() in (0, 1):
            width.increment()
            field.move(1)
        need(field.read() == 2, "first canonical signed component terminator")
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
        for name in ("outer", "rows", "row_bits", "record_bits", "f", "K", "G", "H"):
            positive(header[name])
        one, two = own(Count.literal(1)), own(Count.literal(2))
        need(compare(h, two) >= 0 and compare(header["rho"], header["K"]) < 0,
             "signed width and selected current residue")
        n = own(subtract(header["f"], one))
        compact = own(Count.product(n, header["G"]))
        rest = own(subtract(header["H"], compact))
        twice_H = own(scale(header["H"], 2))
        before = own(subtract(header["active_start"], twice_H))
        chunk = own(Count.product(header["f"], header["K"]))
        active_end = own(scale(chunk, self.rank))
        active_end.add(header["active_start"])
        after = own(subtract(header["back_start"], active_end))
        tail = own(subtract(header["within_bits"], header["back_start"]))
        need(compare(tail, header["H"]) >= 0, "entire current back reservation")
        suffix = own(subtract(tail, compact))
        fibre = own(power_two(suffix))
        top = own(subtract(header["K"], one))
        rho = own(subtract(top, header["rho"]))
        selected = own(scale(header["f"], self.rank))
        selected.add(header["remainder"])
        rank = own(Count.literal(self.rank))
        need(compare(selected, header["selected_axes"]) == 0
             and compare(header["remainder"], rank) < 0
             and compare(header["selected_axes"], header["d"]) <= 0,
             "current active width, fixed rank and untouched ordinary remainder")
        complete = own(power_two(header["within_bits"]))
        expected = own(Count.product(complete, header["record_bits"]))
        need(compare(expected, header["row_bits"]) == 0, "exact complete current physical row")
        pair_codes = own(Count(h))
        pair_codes.increment()
        pair_codes.multiply_small(6)
        base_coefficients, remainder = divide(header["record_bits"], pair_codes)
        own(base_coefficients); own(remainder)
        need(remainder.zero(), "record_bits equals 6 r (h+1)")
        positive(base_coefficients)
        coefficients = own(Count.product(base_coefficients, fibre))
        rows = own(Count.product(header["outer"], header["rows"]))
        widths = (compact, rest, compact, rest, before,
                  *(chunk for _ in self.vectors), after, compact)
        return widths, rho, coefficients, rows

    def rewind_field(self, field):
        self.field_guide.rewind()
        while self.field_guide.read() != 4:
            need(self.field_guide.read() == 1, "complete current field guide")
            field.move(-1)
            self.field_guide.step(1)
        self.field_guide.rewind()

    def import_field(self, field, h):
        """Strip actual component delimiters, preserving every signed bit."""
        while field.read() != 4:
            for _ in (0, 1):
                remaining = Counter(h)
                try:
                    while not remaining.finished:
                        value = field.read()
                        need(value in (0, 1), "uniform complete signed component")
                        self.bridge.append(value)
                        self.field_guide.append(1)
                        field.move(1)
                        remaining.decrement()
                finally:
                    remaining.close()
                need(field.read() == 2, "exact signed component delimiter")
                self.field_guide.append(1)
                field.move(1)
        self.bridge.rewind()
        self.rewind_field(field)

    def export_field(self, field, returned, h):
        """Reinsert the exact complete format at the unchanged common grid."""
        returned.rewind()
        self.field_guide.rewind()
        while returned.read() != 4:
            for _ in (0, 1):
                remaining = Counter(h)
                try:
                    while not remaining.finished:
                        value = returned.read()
                        need(value in (0, 1) and field.read() in (0, 1)
                             and self.field_guide.read() == 1, "exact returned signed component")
                        field.write(value)
                        field.move(1)
                        returned.step(1)
                        self.field_guide.step(1)
                        remaining.decrement()
                finally:
                    remaining.close()
                need(field.read() == 2 and self.field_guide.read() == 1,
                     "same complete signed component boundary")
                field.write(2)
                field.move(1)
                self.field_guide.step(1)
        need(field.read() == self.field_guide.read() == 4, "exact full-format return frontier")
        self.rewind_field(field)
        self.field_guide.clear()
        returned.rewind()

    def run(self, field, context):
        """Current CodedPort field and BinaryContextPort at their local origins.

        SignedHeadroomError preserves field and context and allows a valid
        retry. The all-size theorem concerns valid format and descriptors;
        arbitrary malformed/interrupted execution has no rollback claim.
        """
        need(self.cohort.ports is not None and field.tape is not context.tape
             and all(field.tape is not port and context.tape is not port for port in self.cohort.ports),
             "distinct public/current-context and private physical segments")
        self.cohort.start()
        try:
            with execution(), self.scope.installed(), ExitStack() as cleanup:
                header = self.read_header(context)
                for value in header.values():
                    cleanup.callback(value.close)
                h = self.component_width(field)
                cleanup.callback(h.close)
                widths, rho, coefficients, rows = self.prepare(header, h, cleanup)
                self.import_field(field, h)
                with self.scope.suspended():
                    returned = self.engine.run(self.bridge, widths, header["f"], header["K"],
                        header["G"], rho, h, coefficients, rows, self.inverse)
                self.export_field(field, returned, h)
                returned.clear()
                erase_marker(returned)
                self.bridge.clear()
            self.pool.empty()
            self.calls += 1
        finally:
            self.cohort.finish()
