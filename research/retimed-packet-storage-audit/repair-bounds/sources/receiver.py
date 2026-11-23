"""Run the actual binary supplier on canonical charts or directly on the body."""

from contextlib import contextmanager
from functools import partial
from math import prod

from compiler_cut import source_planner, source_rule
from direct_body import direct_line, direct_route
from growing_binary import pipe
from module_atoms import chart_width, lower_tape, pair_shape, total_width
from periodic import Job, run
from raw_binary import Banks, BinarySource, job_frame
from stack_tapes import Arena
from streaming_routes import cold_swap_tape, erase, type_route, work_tapes
from ternary_leaf import select_pivot

from quotient_route import (
    canonical_lows,
    free_count,
    low_count,
    quotient_right_route,
    representative,
)
from same_order_body import SameOrderBody
from five_exchange import same_order_line


class OwnerBanks(Banks):
    """Use the original owner and XOR instructions with the new full-field transition."""

    def __init__(self, tape, dimension, volume, route):
        self.tape = tape
        self.dimension = dimension
        self.volume = volume
        self.transition = route
        self.capacity = 0
        self.vacant = []
        self.live = set()

    def route(self, owner, word):
        with work_tapes(1) as (out,):
            self.start(owner)
            self.transition(self.tape, out, word)
            out.seek(0)
            self.install(owner, out)


class Receiver(SameOrderBody):
    def __init__(self, dimension, layout, previous=cold_swap_tape, *, direct=False):
        if dimension < 2:
            raise ValueError("Use a native rank of at least two")
        self.n, self.layout, self.previous = dimension, layout, previous
        self.direct = direct
        self.digits = chart_width(layout)
        self.modulus = 3**self.digits
        self.atom = 3 ** total_width(layout)
        self.low = 1 if direct else low_count(dimension)
        self.high = 1 if direct else 3 ** ((self.digits - 1) * free_count(dimension))
        self.rule = source_rule()
        self.planner = source_planner()
        self.owners = self.planner(dimension).width
        self.stock = self.owners * self.low * self.high
        self.arena = self.last_storage = None
        self.small = None

    def weighted(self, source, target, **shape):
        if not self.direct and shape["atoms"] <= self.n**8:
            if self.small is None:
                self.small = Receiver(self.n, self.layout, self.previous, direct=True)
            self.small.arena = self.arena
            try:
                self.small.weighted(source, target, **shape)
            finally:
                self.small.arena = None
            return
        super().weighted(source, target, **shape)

    @contextmanager
    def storage(self):
        top = self.arena is None
        if top:
            self.arena = Arena()
        try:
            yield self.arena
        finally:
            if top:
                self.last_storage = self.arena.counts()
                self.arena.close()
                self.arena = None

    def compensate(self, source, target, lower, f, older, gap, suffix, weight):
        """Solve L times the returned tail equals the old tail. Normalize heads by A."""
        n = self.n
        dims = [older] + [self.atom] * (n * f) + [gap] + [self.atom] * (n * f)
        volume = prod(dims) * suffix

        def shear(i, k, j, head, entry):
            offset = 1 if head else n * f + 2
            src = offset + k * f + j
            dst = offset + i * f + j
            front = prod(dims[1:src])

            def coefficients():
                for old in range(older):
                    value = -entry
                    if head:
                        value *= weight(old, i * f + j) * pow(
                            weight(old, k * f + j), -1, self.modulus
                        )
                    yield front, value % self.modulus

            p, g, s = pair_shape(dims, src, dst, suffix)
            return partial(
                lower_tape, layout=self.layout, prefix=p, gap=g, suffix_bytes=s, runs=coefficients
            )

        def schedule():
            for i, row in enumerate(lower):
                for k in range(i):
                    if row[k]:
                        for j in range(f):
                            for head in (True, False):
                                yield shear(i, k, j, head, row[k])

        pipe(self.arena, "triangular-body", source, target, volume, schedule())

    def transition(self, source, target, word, f, unused, older, gap, suffix, weight):
        if self.direct:
            direct_route(self, source, target, word, f, unused, older, gap, suffix, weight)
            return
        body = older * self.atom ** (2 * self.n * f) * gap * suffix

        def compensate(src, dst, lower, size):
            self.compensate(src, dst, lower, f, older, gap, suffix, weight)

        quotient_right_route(
            source,
            target,
            self.n,
            self.digits,
            unused,
            body,
            word,
            previous_swap=self.previous,
            transform=compensate,
        )

    def serve_line(self, source, target, frame, f, unused, older, gap, suffix, weight):
        """Evaluate the requested projector in each live chart at its actual paid position."""
        if self.direct:
            if not frame.word:
                (axis,) = frame.mask
                head = self.atom ** (axis * f)
                mid = self.atom ** ((self.n - 1) * f) * gap
                tail = self.atom ** ((self.n - axis - 1) * f) * suffix

                def child_weight(row, j):
                    return weight(row // head, axis * f + j)

                self.weighted(
                    source,
                    target,
                    atoms=f,
                    available=unused,
                    older=older * head,
                    gap=mid,
                    suffix=tail,
                    weight=child_weight,
                )
                return
            direct_line(self, source, target, frame, f, unused, older, gap, suffix, weight)
            return
        body = older * self.atom ** (2 * self.n * f) * gap * suffix
        packet = self.high * body
        length = unused * packet
        with self.arena.frames("chart-line", 2) as (split, completed):
            type_route(source, split, unused, self.low, packet)
            pending, answers = self.arena.pending, self.arena.answers
            before, after = pending.top, answers.top
            pending.push_reverse(split, self.low * length)
            erase(split)
            for low in canonical_lows(self.n):
                low_rows = tuple(low[i : i + self.n] for i in range(0, self.n**2, self.n))
                pivot = select_pivot(*frame.covered_line(low_rows, 1))

                def factors(high):
                    return frame.covered_line(
                        representative(low, high, self.n, self.digits), self.digits
                    )

                with self.arena.frames("chart-packet", 2) as (argument, reply):
                    pending.pop_forward(argument, length)
                    argument.seek(0)
                    same_order_line(
                        self,
                        argument,
                        reply,
                        pivot=pivot,
                        factors=factors,
                        f=f,
                        unused=unused,
                        heights=self.high,
                        older=older,
                        gap=gap,
                        suffix=suffix,
                        weight=weight,
                    )
                    reply.seek(0)
                    answers.append(reply, length)
            if pending.top != before:
                raise ArithmeticError("The issued line left an unfinished chart")
            answers.take_answers(after, completed)
            completed.seek(0)
            type_route(completed, target, unused, self.low, packet, inverse=True)

    def compiled(self, source, target, f, unused, older, gap, suffix, weight):
        body = older * self.atom ** (2 * self.n * f) * gap * suffix
        bank_width = self.low * self.high * body
        with self.arena.frames("compiler", 3) as (backing, staged, result):

            def transition(src, dst, word):
                self.transition(src, dst, word, f, unused, older, gap, suffix, weight)

            banks = OwnerBanks(backing, self.n, unused * bank_width, transition)
            raw = BinarySource(banks)
            type_route(source, staged, unused, self.owners, bank_width)
            staged.seek(0)
            jobs = []
            for _ in range(self.owners):
                owner = banks.zero()
                banks.install(owner, staged)
                jobs.append(Job(owner, tuple(range(self.n))))
            erase(staged)
            core = self

            class Machine:
                def leaf(self, job):
                    with core.arena.frames("issued-leaf", 1) as (out,):
                        banks.start(job.owner)
                        core.serve_line(
                            backing,
                            out,
                            job_frame(job, core.n),
                            f,
                            unused,
                            older,
                            gap,
                            suffix,
                            weight,
                        )
                        out.seek(0)
                        banks.install(job.owner, out)

                def native(self, ports, columns):
                    return core.rule.word.native(ports, columns, raw)

                def zero(self, exemplar):
                    return Job(banks.zero(), exemplar.axes)

                def retire_zero(self, job):
                    banks.retire(job.owner, require_zero=True)

            run(self.rule, self.n, jobs, Machine(), planner=self.planner)
            for job in jobs:
                banks.read(job.owner, result)
                banks.retire(job.owner)
            if banks.live:
                raise ArithmeticError("The periodic supplier retained a live owner")
            result.seek(0)
            type_route(result, target, unused, self.owners, bank_width, inverse=True)
