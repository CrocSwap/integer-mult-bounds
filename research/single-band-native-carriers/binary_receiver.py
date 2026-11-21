"""Run the funded binary graph in the public bank and return every physical loan."""

from functools import cache

from calibration import COMPACT
from compiler_cut import SourceRule
from epoch_tape import Compiler, run
from module_atoms import chart_width, total_width
from periodic import Job
from quotient_route import free_count, low_count
from raw_binary import job_frame
from receiver import OwnerBanks, Receiver as PhysicalReceiver
from streaming_routes import cold_swap_tape, erase, type_route
from strong_binary import StrongBinarySource, native_word


class NativeRule(SourceRule):
    def __init__(self, power):
        word = native_word(power)
        self.word = word
        self.ambient = word.ambient**word.power


@cache
def source_rule(power):
    return NativeRule(power)


@cache
def source_planner(power, floor):
    return Compiler(source_rule(power), floor)


class Receiver(PhysicalReceiver):
    def __init__(
        self, dimension, layout, previous=cold_swap_tape, *, direct=False, profile=COMPACT
    ):
        if dimension < 2:
            raise ValueError("Use a native rank of at least two")
        self.n, self.layout, self.previous = dimension, layout, previous
        self.direct, self.profile = direct, profile
        self.digits = chart_width(layout)
        self.modulus = 3**self.digits
        self.atom = 3 ** total_width(layout)
        self.low = 1 if direct else low_count(dimension)
        self.high = 1 if direct else 3 ** ((self.digits - 1) * free_count(dimension))
        self.rule = source_rule(profile.power)
        self.planner = source_planner(profile.power, profile.floor)
        self.owners = self.planner(dimension).width
        self.stock = self.owners * self.low * self.high
        self.arena = self.last_storage = None
        self.small = None

    def weighted(self, source, target, **shape):
        if not self.direct and shape["atoms"] <= self.n**8 and self.small is None:
            self.small = Receiver(
                self.n, self.layout, self.previous, direct=True, profile=self.profile
            )
        super().weighted(source, target, **shape)

    def compiled(self, source, target, f, unused, older, gap, suffix, weight):
        body = older * self.atom ** (2 * self.n * f) * gap * suffix
        bank_width = self.low * self.high * body
        with self.arena.frames("compiler", 3) as (backing, staged, result):

            def transition(src, dst, word):
                self.transition(src, dst, word, f, unused, older, gap, suffix, weight)

            banks = OwnerBanks(backing, self.n, unused * bank_width, transition)
            raw = StrongBinarySource(banks)
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
