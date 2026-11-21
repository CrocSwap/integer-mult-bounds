"""Compare the emitted single-band calls against independent finite oracles."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import prod
from random import Random

from epoch_tape import Compiler as make_planner, run
from check_periodic import BitMachine
from check_powered import Toy
from periodic import Job, Rule
from powered import Port, PoweredWord


def census(rule, n, floor):
    limit = (n - n % 4) // 4
    high = Fraction(limit, rule.ambient)
    ratio = Fraction(min(rule.targets), max(rule.paid))
    g = 0
    while ratio**g <= high:
        g += 1
    nodes = {}
    for d in range(g + 1):
        for p in product(range(len(rule.paid)), repeat=d):
            for a in product(range(len(rule.targets)), repeat=g - d):
                x = Fraction(
                    prod(rule.paid[j] for j in p) * prod(rule.targets[i] for i in a),
                    max(rule.paid) ** g,
                )
                if floor <= x <= high:
                    nodes[p, a] = int(x) - 1
    roots = {}
    costs = [0, 0]
    for (p, a), c in nodes.items():
        for i, k in enumerate(rule.targets):
            if (p[:-1], (i,) + a) not in nodes:
                roots[p, a, i] = k * c
        for j, r in enumerate(rule.paid):
            child = (p + (j,), a[1:])
            if child in nodes:
                costs[1] += r * c - rule.targets[a[0]] * nodes[child]
            else:
                costs[0] += r * c
    if not roots:
        return 1, n, costs
    qs = [(1 << (((n - n % 4 + size - 1) // size) - 1).bit_length()) for size in roots.values()]
    groups = sum(max(qs) // q for q in qs)
    width = 1 << (15 * groups - 1).bit_length()
    leaves = max(qs) * ((width + groups - 1) // groups) * sum(costs) + (n % 4) * width
    return width, leaves, costs


@dataclass(frozen=True)
class ChartJob:
    owner: int
    axes: tuple
    basis: int

    def select(self, indices):
        return ChartJob(self.owner, tuple(self.axes[i] for i in indices), self.basis)


class Chart:
    """Check each loan in its live chart before its native parent resumes."""

    def __init__(self, rule, partitions, n):
        self.rule, self.partitions, self.n = rule, partitions, n
        self.data, self.chart = {}, {}
        self.serial = self.leaves = self.freed = self.raw = self.noncommuting = 0
        assert tuple(map(sum, partitions)) == rule.targets
        assert tuple(r for part in partitions for r in part) == rule.paid

    def zero(self, exemplar):
        self.serial += 1
        owner = -self.serial
        self.data[owner] = [0] * self.n
        self.chart[owner] = 0
        return ChartJob(owner, exemplar.axes, 0)

    def retire_zero(self, job):
        assert self.chart.pop(job.owner) == 0
        assert not any(self.data.pop(job.owner))
        self.freed += 1

    def leaf(self, job):
        assert job.basis == self.chart[job.owner]
        (axis,) = job.axes
        payload = self.data[job.owner]
        payload[axis] = 4 * payload[axis] % 17
        self.leaves += 1

    def native(self, ports, columns):
        assert len({p.owner for p in ports}) == len(ports)
        self.raw += 1
        for port, splits, target in zip(ports, self.partitions, self.rule.targets, strict=True):
            assert port.basis == self.chart[port.owner]
            assert len(port.axes) == target * columns and len(set(port.axes)) == len(port.axes)
            payload = self.data[port.owner]
            first, last = port.axes[0], port.axes[-1]
            before = payload.copy()
            payload[first] = (payload[first] + 3 * payload[last]) % 17
            self.chart[port.owner] += 1
            cursor = 0
            for step, split in enumerate(splits):
                size = split * columns
                axes = port.axes[cursor : cursor + size]
                if step % 2:
                    # Change the full active chart between successive dependent cuts.
                    payload[first], payload[last] = payload[last], payload[first]
                    self.chart[port.owner] += 1
                    if ((first in axes) != (last in axes)) and (payload[first] or payload[last]):
                        self.noncommuting += 1
                    axes = tuple(last if i == first else first if i == last else i for i in axes)
                expected = payload.copy()
                for i in axes:
                    expected[i] = 4 * expected[i] % 17
                yield ChartJob(port.owner, axes, self.chart[port.owner])
                assert payload == expected
                if step % 2:
                    payload[first], payload[last] = payload[last], payload[first]
                    self.chart[port.owner] -= 1
                cursor += size
            payload[first] = (payload[first] - 3 * payload[last]) % 17
            self.chart[port.owner] -= 1
            expected = before
            for i in port.axes:
                expected[i] = 4 * expected[i] % 17
            assert payload == expected and port.basis == self.chart[port.owner]


def run_chart(rule, partitions, n, floor):
    planner = make_planner(rule, floor)
    plan = planner(n)
    backend = Chart(rule, partitions, n)
    rng = Random(812)
    fields = []
    original = {}
    for i in range(plan.width):
        fields.append(ChartJob(i, tuple(rng.sample(range(n), n)), 0))
        original[i] = [rng.randrange(17) for _ in range(n)]
        backend.data[i] = original[i].copy()
        backend.chart[i] = 0
    run(rule, n, fields, backend, planner=planner)
    assert backend.data == {i: [4 * x % 17 for x in data] for i, data in original.items()}
    assert backend.leaves == plan.leaves and backend.serial == backend.freed
    assert backend.noncommuting > 0 and not any(backend.chart.values())
    return plan.width, backend.raw, backend.noncommuting, backend.leaves


def weighted_swap():
    rule, partitions, n = Rule(5, (5,), (2, 2, 1)), ((2, 2, 1),), 323
    machine = BitMachine(rule, partitions)
    planner = make_planner(rule, 4)
    p = planner(n)
    rng = Random(338833)
    fields = [Job(i, tuple(rng.sample(range(n), n))) for i in range(p.width)]
    for field in fields:
        machine.data[field.owner] = machine.initial(field.owner, n)
        machine.geometry[field.owner] = n
    run(rule, n, fields, machine, planner=planner)
    for i, state in machine.data.items():
        heads, tail, _, w, inv = machine.initial(i, n)
        assert state[0] == [(tail[n - 1 - j] * w[j]) % 27 for j in range(n)]
        assert state[1][::-1] == [(heads[j] * inv[j]) % 27 for j in range(n)]
    assert machine.leaves == p.leaves and machine.zeros == machine.freed
    return n, p.width, machine.frames, machine.leaves, machine.zeros


def powered():
    floor, cap = 3, 2
    word = PoweredWord(
        4,
        (Port(("small",), 1), Port(("large",), 4)),
        (Port(("a",), 1), Port(("b",), 3), Port(("c",), 1)),
        2,
        floor,
        cap,
        cap,
    )
    rule = word.rule()
    n = 323
    planner = make_planner(rule, 4)
    p = planner(n)
    machine = Toy(n, word)
    fields = [Job(~i, tuple((j + i) % n for j in range(n))) for i in range(p.width)]
    original = {f.owner: [(j * 3 - f.owner + 1) % 17 for j in range(n)] for f in fields}
    machine.data.update({i: x.copy() for i, x in original.items()})
    run(rule, n, fields, machine, planner=planner)
    assert machine.data == {i: [4 * x % 17 for x in a] for i, a in original.items()}
    assert machine.leaves == p.leaves and not machine.guard and machine.live_centres > 0
    return n, p.width, machine.raw_frames, machine.private, machine.live_centres, machine.leaves


if __name__ == "__main__":

    class StoppedRule:
        ambient = 134**480

        @property
        def targets(self):
            raise AssertionError("A stopped call tried to generate the native catalogue")

        paid = targets

    assert make_planner(StoppedRule(), 1 << 42)(2).leaves == 2
    rules = [
        Rule(5, (4, 5), (2, 2, 2, 2, 1)),
        Rule(5, (5,), (2, 2, 1)),
        Rule(3, (2, 3), (1, 1, 1, 1, 1)),
    ]
    cases = 0
    for rule in rules:
        for floor in (2, 4, 8):
            planner = make_planner(rule, floor)
            for n in (1, 16, 24, 32, 48, 81, 129, 193, 256, 323):
                p = planner(n)
                w, leaves, ends = census(rule, n, floor)
                assert (w, leaves) == (p.width, p.leaves)
                if p.forest:
                    assert ends == [p.forest.terminal_axes, p.forest.fringe_axes]
                cases += 1
    print("exact Fraction graph censuses", cases)
    print(
        "chart-dependent loan and ordered returns", *run_chart(rules[0], ((2, 2), (2, 2, 1)), 81, 4)
    )
    print(
        "simultaneous ordered returns and fringe", *run_chart(rules[2], ((1, 1), (1, 1, 1)), 48, 2)
    )
    print("non-coordinate weighted swap including positive fringe", *weighted_swap())
    print("tagged powered raw source", *powered())
