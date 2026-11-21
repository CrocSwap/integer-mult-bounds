"""Use the installed epoch inside the physical positive tensor receiver."""

from positive import Positive as PhysicalPositive, one_axis, power_le
from spool import scratch, snapshot, transfer


class Positive(PhysicalPositive):
    @property
    def owners(self):
        from epoch_tape import Compiler
        from calibration import COMPLEX_FLOOR

        if self._owners is not None:
            return self._owners
        self.rule = self.word.rule()
        self.planner = Compiler(self.rule, COMPLEX_FLOOR)
        self._owners = self.planner(self.carrier).width
        if self._owners <= 1 or self._owners & (self._owners - 1):
            raise ValueError("Use an admitted dyadic positive batch")
        return self._owners

    def _run(self, field, low, selected, columns, root_width):
        from epoch_tape import run
        from periodic import Job

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
