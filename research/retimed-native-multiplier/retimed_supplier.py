"""Use the unpowered, physically tagged 48-call word in the complete positive receiver."""

from fractions import Fraction as F
from collections import Counter

from upstream import HERE, install

_, _, _, source = install()
from positive import Positive as RetainedPositive, one_axis, power_le
from periodic import Job
from raw48 import ComplexRaw
from spool import scratch, snapshot, transfer
from strong_complex import artifacts, word
from transport import Recipe
from installations import GAUSSIAN_C
from unpowered_price import certify


class Raw:
    def __init__(self, tagged, physical):
        self.tagged = tagged
        self.physical = physical

    def native(self, ports, columns):
        if columns <= 0 or columns % 2:
            raise ValueError("Each split needs a positive even column count.")
        inputs = []
        for label, job in zip(self.tagged.targets, ports, strict=True):
            if len(job.axes) != label.rank * columns:
                raise ValueError("The target rank does not fit its issued axes.")
            inputs.append((label.tag, job))
        iterator = self.physical.raw(inputs, columns)
        split = 0
        for label in self.tagged.paid:
            tag, job = next(iterator)
            if tag != label.tag or len(job.axes) != label.rank * columns:
                raise ArithmeticError(
                    "The next native cut differs from its installed tag or extent."
                )
            if label.rank == 1 and split < 1008:
                yield job.select(range(columns // 2))
                yield job.select(range(columns // 2, columns))
                split += 1
            else:
                yield job
        if split != 1008 or next(iterator, None) is not None:
            raise ArithmeticError(
                "The native circuit did not close on its final paid cut."
            )


def source_ranks(tagged):
    slots = []
    split = 0
    for port in tagged.paid:
        if port.rank == 1 and split < 1008:
            slots.extend((F(1, 2), F(1, 2)))
            split += 1
        else:
            slots.append(F(port.rank))
    if split != 1008:
        raise ArithmeticError("The positive word has too few rank-one cuts.")
    return tuple(p.rank for p in tagged.targets), tuple(slots)


class Positive(RetainedPositive):
    def __init__(self, rank_log, denominator=10**14):
        atlas = artifacts(
            source / "research/grade14-native-realization", HERE / "inputs"
        )
        native = word(atlas.graph, atlas.layout)
        super().__init__(native, atlas, 1 << rank_log, denominator)

        targets, paid = source_ranks(native)
        margin, cells = certify(GAUSSIAN_C, (Counter(targets), Counter(paid)))
        if cells is None or margin <= 0:
            raise ArithmeticError("The Gaussian word has insufficient column capacity")
        self.recipe = Recipe(rank_log, native.ambient, targets, paid, cells, GAUSSIAN_C)

    @property
    def owners(self):
        return self.recipe.width

    def _run(self, field, low, selected, columns, root_width):
        window = columns.window
        n = self.carrier
        if selected <= n or power_le(selected, self.denominator, root_width):
            for i in range(selected):
                one_axis(field, low + i * window + columns.offset)
            return
        bundle, extra = divmod(selected, n)
        for i in range(selected - extra, selected):
            one_axis(field, low + i * window + columns.offset)
        rows = self.owners
        remain = field.ambient_bits - (rows.bit_length() - 1)
        if remain < max(
            low + (selected - extra) * window,
            columns.u + (bundle - 1) * columns.digit,
            columns.t + (bundle - 1) * columns.digit,
        ):
            raise ValueError("The positive field has no independent row reserve.")
        total = field.count * field.record
        part = total // rows
        with field.arena.child(remain) as frame:
            fields = {}
            with snapshot(field.stream, total) as incoming:
                for i in range(rows):
                    fields[i] = frame.field()
                    transfer(incoming, fields[i].stream, part)
            physical = ComplexRaw(
                self.physical, fields, columns, low=low, bundle=bundle, slots=n
            )
            adapter = Raw(self.word, physical)
            outer = self

            class Machine:
                native = staticmethod(adapter.native)

                @staticmethod
                def zero(exemplar):
                    return physical.fresh(
                        exemplar, len(exemplar.axes), ("transport-zero",)
                    )

                retire_zero = staticmethod(physical.retire)

                @staticmethod
                def leaf(job):
                    (axis,) = job.axes
                    outer._run(
                        fields[job.owner],
                        low + axis * bundle * window,
                        bundle,
                        columns,
                        root_width,
                    )

            lanes = [Job(i, tuple(range(n))) for i in range(rows)]
            self.recipe.open().run(lanes, Machine())
            if len(fields) != rows:
                raise ArithmeticError(
                    "A native owner is still active at the positive return."
                )
            with scratch() as outgoing:
                for i in range(rows):
                    owned = fields.pop(i)
                    owned.stream.seek(0)
                    transfer(owned.stream, outgoing, part)
                    owned.retire()
                outgoing.seek(0)
                field.stream.seek(0)
                transfer(outgoing, field.stream, total)
