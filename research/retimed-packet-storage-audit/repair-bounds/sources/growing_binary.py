"""Run weighted ordinary recursion on unbroken fresh and ancestral cover packets."""

from contextlib import contextmanager
from functools import lru_cache, partial
from math import prod

from compiler_cut import chart, low_size, odometer, source_planner, source_rule
from factored_frames import Frame, inverse_word
from module_atoms import (
    chart_width,
    lower_tape,
    ordinary_shell,
    pair_shape,
    total_width,
    weighted_pair,
)
from periodic import Job, run
from raw_binary import Banks, BinarySource, job_frame
from streaming_routes import cold_swap_tape, copy_bytes, erase, regular, right_route, type_route
from stack_tapes import Arena
from ternary_leaf import lower_coefficient, lower_slot, ordered_chart, pivot_pairs, select_pivot


def pipe(arena, kind, source, target, volume, schedule):
    with arena.frames(kind, 2) as (current, other):
        copy_bytes(source, current, volume)
        for gate in schedule:
            current.seek(0)
            gate(current, other)
            erase(current)
            current, other = other, current
        current.seek(0)
        copy_bytes(current, target, volume)


def high_tuple(value, radix, count):
    digits = [0] * count
    for j in reversed(range(count)):
        value, digits[j] = divmod(value, radix)
    return tuple(digits)


def one_weight(row, axis):
    return 1


class Weighted:
    """One stopped compiler and one product-atom layout for a complete coarse tree."""

    def __init__(self, dimension, layout, previous_swap=cold_swap_tape):
        if dimension < 2:
            raise ValueError("A growing receiver needs a carrier of dimension at least two")
        self.n = dimension
        self.layout = layout
        self.previous = previous_swap
        self.digits = chart_width(layout)
        self.modulus = 3**self.digits
        self.atom = 3 ** total_width(layout)
        self.high_radix = 3 ** (self.digits - 1)
        self.high = self.high_radix ** (dimension**2)
        self.low = low_size(dimension)
        self.rule = source_rule()
        self.planner = source_planner()
        self.owners = self.planner(dimension).width
        self.stock = self.owners * self.low * self.high
        self.standard = Frame(dimension, (), (0,))
        self.arena = None
        self.last_storage = None

    @contextmanager
    def storage(self):
        outer = self.arena is None
        if outer:
            self.arena = Arena()
        try:
            yield self.arena
        finally:
            if outer:
                self.last_storage = self.arena.counts()
                self.arena.close()
                self.arena = None

    def exposed_leaf(self, source, target, low, f, unused, older, gap, suffix, weight):
        """The one low is fixed. Every unused digit and current and older high remains live."""
        n, A, modulus = self.n, self.atom, self.modulus
        rows = self.high * older
        dims = [unused, rows] + [A] * (n * f) + [gap] + [A] * (n * f)
        low_g = [low[i : i + n] for i in range(0, n * n, n)]
        low_u, low_v = self.standard.covered_line(low_g, 1)
        pivot = select_pivot(low_u, low_v)
        pairs = pivot_pairs(n, pivot)

        @lru_cache(maxsize=1)
        def lifted(index):
            high = high_tuple(index, self.high_radix, n * n)
            u, v = self.standard.covered_line(chart(low, high, n), self.digits)
            _, b, c = ordered_chart(u, v, pivot, modulus)
            return b, c, pow(c[0], -1, modulus)

        def physical(block, j):
            if block < n:
                return 2 + block * f + j
            return 3 + block * f + f - 1 - j

        def child(left, right, central):
            start = left * f
            end = right * f
            front = A**start
            middle = gap * A ** (end - start - f)
            last = suffix * A ** (2 * n * f - end - f)
            if central:

                def child_weight(row, j):
                    high, old = divmod(row // front, older)
                    _, c, _ = lifted(high)
                    return weight(old, pivot * f + j) * c[0] % modulus
            else:
                child_weight = one_weight
            return partial(
                self.weighted,
                atoms=f,
                available=unused,
                older=rows * front,
                gap=middle,
                suffix=last,
                weight=child_weight,
            )

        def shear(src, dest, i, sweep, j, undo):
            x, y = physical(src, j), physical(dest, j)
            visible = prod(dims[2:x])
            # The transposition moves both the pivot and the ancestral index.
            ii = pivot if i == 0 else 0 if i == pivot else i

            def coefficients():
                for _ in range(unused):
                    for high in range(self.high):
                        b, c, inv = lifted(high)
                        for old in range(older):
                            a = lower_coefficient(
                                sweep,
                                i,
                                b,
                                c,
                                weight(old, pivot * f + j),
                                weight(old, ii * f + j),
                                inv,
                                modulus,
                            )
                            yield visible, -a if undo else a

            shape = pair_shape(dims, x, y, suffix)
            return partial(
                lower_tape,
                layout=self.layout,
                prefix=shape[0],
                gap=shape[1],
                suffix_bytes=shape[2],
                runs=coefficients,
            )

        def schedule():
            for l, r in pairs:
                yield child(l, r, False)
            slots = range(4 * (n - 1))
            for undo in (False, True):
                if undo:
                    yield child(0, 2 * n - 1, True)
                for k in reversed(slots) if undo else slots:
                    dest, src, i = lower_slot(n, k)
                    for j in range(f):
                        yield shear(src, dest, i, k // (n - 1), j, undo)
            for l, r in reversed(pairs):
                yield child(l, r, False)

        with self.storage() as arena:
            pipe(arena, "exposed-leaf", source, target, prod(dims) * suffix, schedule())

    def line(self, source, target, frame, f, unused, older, gap, suffix, weight):
        """Run the whole matcher and each entire true-low child packet, then restore all rows."""
        body = older * self.atom ** (2 * self.n * f) * gap * suffix
        word = frame.matcher_to(self.standard)
        with self.arena.frames("line", 3) as (routed, split, completed):
            right_route(
                source, routed, self.n, self.digits, unused, body, word, previous_swap=self.previous
            )
            routed.seek(0)
            type_route(routed, split, unused, self.low, self.high * body)
            erase(routed)
            length = unused * self.high * body
            pending, answers = self.arena.pending, self.arena.answers
            before, after = pending.top, answers.top
            pending.push_reverse(split, self.low * length)
            erase(split)
            for low in odometer(3, self.n**2):
                if regular(low, self.n):
                    with self.arena.frames("low-packet", 2) as (argument, reply):
                        pending.pop_forward(argument, length)
                        argument.seek(0)
                        self.exposed_leaf(
                            argument, reply, low, f, unused, older, gap, suffix, weight
                        )
                        reply.seek(0)
                        answers.append(reply, length)
            if pending.top != before:
                raise ArithmeticError("The low dispatcher did not consume its whole packet")
            answers.take_answers(after, completed)
            completed.seek(0)
            type_route(completed, routed, unused, self.low, self.high * body, inverse=True)
            routed.seek(0)
            right_route(
                routed,
                target,
                self.n,
                self.digits,
                unused,
                body,
                tuple(inverse_word(word)),
                previous_swap=self.previous,
            )

    def compiled(self, source, target, f, unused, older, gap, suffix, weight):
        """Feed all independent compiler owners; each leaf consumes its own true chart."""
        body = older * self.atom ** (2 * self.n * f) * gap * suffix
        with self.arena.frames("compiler", 3) as (backing, staged, result):
            banks = Banks(backing, self.n, self.digits, unused, body, self.previous)
            raw = BinarySource(banks)
            type_route(source, staged, unused, self.owners, self.low * self.high * body)
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
                    frame = job_frame(job, core.n)
                    with core.arena.frames("issued-leaf", 1) as (out,):
                        banks.start(job.owner)
                        core.line(backing, out, frame, f, unused, older, gap, suffix, weight)
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
                raise ArithmeticError("The full binary return retained an owner")
            result.seek(0)
            type_route(
                result, target, unused, self.owners, self.low * self.high * body, inverse=True
            )

    def weighted(self, source, target, *, atoms, available, older, gap, suffix, weight=one_weight):
        """Input is [available][older][head][gap][tail][suffix], with the complete fresh divisor."""
        f, remainder = divmod(atoms, self.n)
        unused = 0
        if f:
            unused, rem = divmod(available, self.stock)
            if rem or not unused:
                raise ValueError("The active call lacks a complete independent fresh stock")
        dims = [available * older] + [self.atom] * atoms + [gap] + [self.atom] * atoms

        def stopped(j):
            head = self.n * f + j
            x = 1 + head
            y = 2 + atoms + remainder - 1 - j
            shape = pair_shape(dims, x, y, suffix)
            visible = self.atom**head

            def coefficients():
                for _ in range(available):
                    for old in range(older):
                        yield visible, weight(old, head)

            return partial(
                weighted_pair,
                layout=self.layout,
                prefix=shape[0],
                gap=shape[1],
                suffix_bytes=shape[2],
                weight=None,
                previous_swap=self.previous,
                runs=coefficients,
            )

        def schedule():
            for j in range(remainder):
                yield stopped(j)
            if f:
                yield partial(
                    self.compiled,
                    f=f,
                    unused=unused,
                    older=older,
                    gap=gap * self.atom ** (2 * remainder),
                    suffix=suffix,
                    weight=weight,
                )

        with self.storage() as arena:
            pipe(arena, "weighted", source, target, prod(dims) * suffix, schedule())

    def body_ordinary(self, source, target, atoms, available, older, gap, suffix):
        """Run both actual compiled returns. The supplied stock is part of the addressed input."""

        def rev(s, t):
            self.weighted(
                s, t, atoms=atoms, available=available, older=older, gap=gap, suffix=suffix
            )

        with self.storage():
            ordinary_shell(source, target, self.layout, atoms, available * older, gap, suffix, rev)
