"""Execute the positive complex tensor with the complete periodic supplier."""

from spool import Arena, quarter, scratch, snapshot, transfer


def power_le(base, power, ceiling):
    value = 1
    while power:
        if power & 1:
            value *= base
            if value > ceiling:
                return False
        power //= 2
        if power:
            base = min(ceiling + 1, base * base)
    return True


def one_axis(field, bit):
    tail = 1 << bit
    out = field.blank()
    size = field.component_bytes
    with (
        snapshot(field.stream, field.count * field.record) as src,
        scratch() as first,
        scratch() as second,
    ):

        def read(tape):
            return (
                int.from_bytes(tape.read(size), "little", signed=True),
                int.from_bytes(tape.read(size), "little", signed=True),
            )

        def write(tape, a, b):
            if (a | b) & 1:
                raise ArithmeticError("The positive kernel left its represented common grid")
            tape.write((a // 2).to_bytes(size, "little", signed=True))
            tape.write((b // 2).to_bytes(size, "little", signed=True))

        for _ in range(field.count // (2 * tail)):
            first.seek(0)
            transfer(src, first, tail * field.record)
            first.seek(0)
            second.seek(0)
            for _ in range(tail):
                a, b = read(first)
                c, d = read(src)
                write(out.stream, a - b + c + d, a + b - c + d)
                write(second, a + b + c - d, b - a + c + d)
            second.seek(0)
            transfer(second, out.stream, tail * field.record)
    field.replace(out)


class Positive:
    def __init__(self, word, physical, carrier, denominator=10**14):
        self.word, self.physical, self.carrier, self.denominator = (
            word,
            physical,
            carrier,
            denominator,
        )
        self.rule = self.planner = self._owners = None

    @property
    def owners(self):
        from periodic import make_planner

        if self._owners is not None:
            return self._owners
        self.rule = self.word.rule()
        self.planner = make_planner(self.rule)
        self._owners = self.planner(self.carrier).width
        if self._owners <= 1 or self._owners & (self._owners - 1):
            raise ValueError("Use an admitted dyadic positive batch")
        return self._owners

    def apply(self, field, low, selected, columns):
        if field.arena is None:
            raise ValueError("The top numerical field needs a physical stack frame")
        if (
            selected < 0
            or low < columns.suffix
            or not 0 <= columns.offset < columns.window
            or low + selected * columns.window > field.ambient_bits
        ):
            raise ValueError("The selected numerical pack is outside this complete field")
        self._run(field, low, selected, columns, selected)

    def hadamard(self, field, low, selected, columns):
        """Run the unnormalised H tensor on the caller's represented integers."""
        if (
            selected < 0
            or low < columns.suffix
            or not 0 <= columns.offset < columns.window
            or low + selected * columns.window > field.ambient_bits
        ):
            raise ValueError("The complete selected H windows do not fit")
        widened = field.component_bytes + (2 * selected + 33) // 8 + 1
        arena = Arena(field.ambient_bits, widened)
        working = arena.field()
        working.write((a << selected, b << selected) for a, b in field.values())
        first = low + columns.offset
        step = columns.window
        mask = sum(1 << (first + step * i) for i in range(selected))

        def phases(addr):
            return (addr & mask).bit_count()

        working.phase(phases, columns.suffix)
        self.apply(working, low, selected, columns)
        working.phase(phases, columns.suffix)
        shift = selected - selected // 2
        discarded = (1 << shift) - 1

        def restored():
            for a, b in working.values():
                if selected % 2:
                    a, b = a + b, b - a
                a, b = quarter((a, b), -(selected // 2))
                if (a | b) & discarded:
                    raise ArithmeticError("The raw H did not return to its input integer grid")
                yield a >> shift, b >> shift

        field.write(restored())
        working.retire()
        arena.close()

    def _run(self, field, low, selected, columns, root_width):
        from periodic import Job, run

        k = columns.window
        if selected <= self.carrier or power_le(selected, self.denominator, root_width):
            for i in range(selected):
                one_axis(field, low + i * k + columns.offset)
            return
        mult, extra = divmod(selected, self.carrier)
        for i in range(selected - extra, selected):
            one_axis(field, low + i * k + columns.offset)
        rows = self.owners
        remain = field.ambient_bits - (rows.bit_length() - 1)
        if remain < max(
            low + (selected - extra) * k,
            columns.u + (mult - 1) * columns.digit,
            columns.t + (mult - 1) * columns.digit,
        ):
            raise ValueError("No independent leading row stock at this positive call")
        total = field.count * field.record
        part = total // rows
        with field.arena.child(remain) as frame:
            # Stage inputs before the child opens its own head.
            with snapshot(field.stream, total) as incoming:
                fields = {}
                for i in range(rows):
                    owned = frame.field()
                    transfer(incoming, owned.stream, part)
                    fields[i] = owned
            raw = self.physical(fields, columns, low=low, bundle=mult, slots=self.carrier)
            outer = self

            class Machine:
                def native(self, ports, cols):
                    return outer.word.native(ports, cols, raw)

                def zero(self, exemplar):
                    job = raw.fresh(exemplar, len(exemplar.axes), ("periodic-zero",))
                    return Job(job.owner, exemplar.axes)

                def retire_zero(self, job):
                    raw.retire(job)

                def leaf(self, job):
                    if len(job.axes) != 1:
                        raise ValueError("A positive leaf must contain one complete group")
                    outer._run(
                        fields[job.owner], low + job.axes[0] * mult * k, mult, columns, root_width
                    )

            lanes = [Job(i, tuple(range(self.carrier))) for i in range(rows)]
            run(self.rule, self.carrier, lanes, Machine(), planner=self.planner)
            if len(fields) != rows:
                raise ValueError("A complete positive call has outstanding private owners")
            # Use the scratch head only after all paid subcalls have returned.
            with scratch() as outgoing:
                for i in range(rows):
                    returned = fields.pop(i)
                    returned.stream.seek(0)
                    transfer(returned.stream, outgoing, part)
                    returned.retire()
                outgoing.seek(0)
                field.stream.seek(0)
                transfer(outgoing, field.stream, total)
