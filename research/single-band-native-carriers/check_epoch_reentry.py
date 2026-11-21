"""Run a complete nested invocation on the same installed file before a parent resumes."""

from random import Random

from upstream import install

install()
from check_band import Chart, ChartJob
from epoch_tape import Compiler, run
from periodic import Rule


class Transfers:
    def __init__(self, stream):
        self.stream = stream
        self.seeks = []
        self.bytes = 0

    def seek(self, offset):
        self.seeks.append((self.stream.tell(), offset))
        return self.stream.seek(offset)

    def read(self, size):
        data = self.stream.read(size)
        self.bytes += len(data)
        return data

    def tell(self):
        return self.stream.tell()


def trial():
    n = 323
    rule = Rule(5, (5,), (2, 2, 1))
    compiler_for_rank = Compiler(rule, 4)
    plan = compiler_for_rank(n)
    program = compiler_for_rank.image(n)
    assert program is compiler_for_rank.image(n)
    physical = Transfers(program.stream)
    program.stream = physical
    suspended = []

    def exercise(nested):
        rng = Random(19921 if nested else 19801)
        machine = Chart(rule, ((2, 2, 1),), n)
        original = {i: [rng.randrange(17) for _ in range(n)] for i in range(plan.width)}
        fields = [ChartJob(i, tuple(rng.sample(range(n), n)), 0) for i in original]
        machine.data = {i: a.copy() for i, a in original.items()}
        machine.chart = dict.fromkeys(original, 0)
        primitive = machine.leaf

        def leaf(job):
            if not nested and not suspended:
                suspended.append(physical.tell())
                assert 0 < suspended[0] < program.size
                exercise(True)
                assert physical.tell() == program.size
            primitive(job)

        machine.leaf = leaf
        run(rule, n, fields, machine, planner=compiler_for_rank)
        assert machine.data == {i: [4 * x % 17 for x in z] for i, z in original.items()}
        assert machine.leaves == plan.leaves and machine.serial == machine.freed
        assert not any(machine.chart.values())

    try:
        exercise(False)
    finally:
        program.stream = physical.stream
    assert (program.size, suspended[0]) in physical.seeks
    assert physical.bytes == 2 * plan.rounds * program.size
    moved = sum(abs(a - b) for a, b in physical.seeks)
    assert moved <= program.size * 2 * plan.rounds * program.records
    return n, plan.width, program.records, program.size, suspended[0], physical.bytes, moved


if __name__ == "__main__":
    print(
        "nested epoch rank, lanes, records, bytes, suspended offset, bytes read, seek distance",
        *trial(),
    )
