"""Check literal row addresses, complete complex phase, weighted BIT and ownership."""

from collections import Counter
from random import Random
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from periodic import Job, Rule, make_planner, period, row_axes, run


class Machine:
    def __init__(self, rule, partition):
        self.rule = rule
        self.partition = partition
        assert tuple(sum(splits) for splits in partition) == rule.targets
        assert tuple(r for splits in partition for r in splits) == rule.paid
        self.next_owner = -1
        self.data = {}
        self.geometry = {}
        self.frames = self.issued = self.leaves = self.zeros = self.freed = 0

    def native(self, ports, columns):
        assert len({p.owner for p in ports}) == len(ports)
        self.frames += 1
        for p, splits, target in zip(ports, self.partition, self.rule.targets, strict=True):
            assert len(p.axes) == target * columns and len(set(p.axes)) == len(p.axes)
            cursor = 0
            for split in splits:
                width = split * columns
                self.issued += 1
                yield Job(p.owner, p.axes[cursor:cursor + width])
                cursor += width
            assert cursor == len(p.axes)

    def zero(self, exemplar):
        n = self.geometry[exemplar.owner]
        owner = self.next_owner
        self.next_owner -= 1
        self.zeros += 1
        self.data[owner] = self.initial(owner, n)
        self.geometry[owner] = n
        return Job(owner, exemplar.axes)

    def retire_zero(self, job):
        state = self.data.pop(job.owner)
        self.geometry.pop(job.owner)
        assert job.owner < 0 and self.is_zero(state)
        self.freed += 1


def sweep(machine, n, *, axes=None):
    rule = machine.rule
    planner = make_planner(rule)
    p = planner(n)
    fields = [Job(i, tuple(axes[i]) if axes is not None else tuple(range(n)))
              for i in range(p.width)]
    for field in fields:
        machine.data[field.owner] = machine.initial(field.owner, n)
        machine.geometry[field.owner] = n
    run(rule, n, fields, machine, planner=planner)
    assert machine.leaves == p.leaves and machine.zeros == machine.freed
    assert set(machine.data) == set(range(p.width))
    return p


def check_subsets():
    count = fives = 0
    for active in range(4, 257, 4):
        for rank in range(1, active // 4 + 1):
            k = period(active, rank)
            rows = [tuple(row_axes(active, rank, k, j)) for j in range(k)]
            assert all(len(row) == len(set(row)) == rank for row in rows)
            hits = Counter(i for row in rows for i in row)
            assert set(hits) == set(range(active))
            assert all(hits[i] in (1, 5) for i in range(active))
            assert sum(hits[i] == 5 for i in hits) == (k * rank - active) // 4
            count += 1
            fives += int(5 in hits.values())
    return count, fives


def walsh(values):
    a = values.copy()
    width = 1
    while width < len(a):
        for i in range(0, len(a), width * 2):
            for j in range(i, i + width):
                x, y = a[j], a[j + width]
                a[j], a[j + width] = x + y, x - y
        width *= 2
    return a


def spectral_quarters(reals, imags):
    """Use the exact spectral action i^popcount and two unnormalized WHTs."""
    real = walsh(reals)
    imag = walsh(imags)
    for j in range(len(real)):
        phase = j.bit_count() % 4
        a, b = real[j], imag[j]
        real[j], imag[j] = ((a, b), (-b, a), (-a, -b), (b, -a))[phase]
    return walsh(real), walsh(imag)


class ComplexMachine(Machine):
    def initial(self, owner, n):
        size = 1 << n
        if owner < 0:
            return [0] * size, [0] * size, [0]
        random = Random(94051991 + owner)
        return ([random.randrange(-7, 8) for _ in range(size)],
                [random.randrange(-7, 8) for _ in range(size)], [0])

    def is_zero(self, state):
        return not any(state[0]) and not any(state[1])

    def leaf(self, job):
        self.leaves += 1
        reals, imags, den = self.data[job.owner]
        width = 1 << job.axes[0]
        den[0] += 1
        for block in range(0, len(reals), 2 * width):
            for j in range(block, block + width):
                k = j + width
                a, b, c, d = reals[j], imags[j], reals[k], imags[k]
                reals[j] = a - b + c + d
                imags[j] = a + b + d - c
                reals[k] = a + b + c - d
                imags[k] = b - a + c + d


def check_complex():
    m = ComplexMachine(Rule(3, (2, 3), (1, 1, 1, 1, 1)), ((1, 1), (1, 1, 1)))
    n = 12
    p = sweep(m, n)
    mistake_count = 0
    for owner, (real, imag, den) in m.data.items():
        a, b, _ = m.initial(owner, n)
        expected_a, expected_b = spectral_quarters(a, b)
        assert den[0] >= n
        scale = 1 << (den[0] - n)
        assert [z * scale for z in expected_a] == real
        assert [z * scale for z in expected_b] == imag
        # Missing all i factors leaves at least one wrong dense output on every lane.
        if [z << den[0] for z in a] != real:
            mistake_count += 1
    assert mistake_count == p.width
    return n, p.width, p.copies * p.owners_per_copy, m.frames, m.leaves


class BitMachine(Machine):
    """Use a non-coordinate projector chart, an exterior weight and reversed tail."""

    def initial(self, owner, n):
        random = Random(7957 + owner)
        # The chart is fixed at the full-field boundary. U = I + a e_0 e_last^T.
        a = 1 + (abs(owner) % 21)
        weights = [random.choice((1, 2, 4, 5, 7, 8, 10, 11, 13)) for _ in range(n)]
        inverse = [pow(w, -1, 27) for w in weights]
        heads = [0] * n if owner < 0 else [random.randrange(27) for _ in range(n)]
        physical = [0] * n if owner < 0 else [random.randrange(27) for _ in range(n)]
        return heads, physical, a, weights, inverse

    def is_zero(self, state):
        return not any(state[0]) and not any(state[1])

    def leaf(self, job):
        self.leaves += 1
        heads, physical, a, weights, inverse = self.data[job.owner]
        j = job.axes[0]
        n = len(heads)

        def difference(i):
            return physical[n - 1 - i] - inverse[i] * heads[i]

        # Column Ue_j times row e_j^T U^-1. Pull the physical weight outside D.
        d = difference(j)
        if j == 0:
            d -= a * difference(n - 1)

        def transfer(i, value):
            heads[i] = (heads[i] + weights[i] * value) % 27
            physical[n - 1 - i] = (physical[n - 1 - i] - value) % 27

        transfer(j, d)
        if j == n - 1:
            transfer(0, a * d)


def check_bit(n, rule, partitions):
    m = BitMachine(rule, partitions)
    p = make_planner(rule)(n)
    rng = Random(338833)
    orders = [rng.sample(range(n), n) for _ in range(p.width)]
    sweep(m, n, axes=orders)
    for owner, state in m.data.items():
        before_h, before_t, _, w, inv = m.initial(owner, n)
        assert state[0] == [(before_t[n - 1 - i] * w[i]) % 27 for i in range(n)]
        assert state[1][::-1] == [(before_h[i] * inv[i]) % 27 for i in range(n)]
    return n, p.width, p.copies * p.owners_per_copy, m.frames, m.leaves, m.zeros


if __name__ == "__main__":
    print("row tapes, degree-five examples", *check_subsets())
    print("exact Gaussian arrays", *check_complex())
    r = Rule(4, (3, 4), (1, 2, 2, 2))
    print("non-coordinate weighted BIT", *check_bit(51, r, ((1, 2), (2, 2))))
    deep = Rule(3, (3,), (1, 2))
    print("nested exit weighted BIT", *check_bit(325, deep, ((1, 2),)))
