"""Check actual raw labels and replay the full tensor, strictifier and periodic flow."""

from collections import Counter
from itertools import islice
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))

from periodic import Job, make_planner, run
from powered import Port, PoweredWord
from tagged_sources import read_words


def first_index(ports, rank):
    return next(i for i, port in enumerate(ports) if port.rank == rank)


def actual_sources():
    bit, comp = read_words()
    assert (len(bit.targets), len(bit.paid)) == (20706, 107460)
    assert (len(comp.targets), len(comp.paid)) == (52512, 283152)
    for word, expected in ((bit, 46116), (comp, 37920)):
        assert Counter(x.rank for x in word.paid)[2] == expected
        assert len({p.tag for p in word.targets}) == len(word.targets)
        assert len({p.tag for p in word.paid}) == len(word.paid)
        assert all(1 <= t.rank <= word.ambient for t in (*word.targets, *word.paid))
        repeat = (first_index(word.paid, 2),) * word.power
        unit, = word.blocks(repeat)
        assert unit.first == 0 and unit.rank == 2 ** word.power
        assert unit.tags == (word.paid[repeat[0]].tag,) * word.power
    # The first real occurrence controls the BIT slab, even with the same multiset.
    j4, j14, j21 = (first_index(bit.paid, r) for r in (4, 14, 21))
    inside = (j4,) * 181 + (j14,) * 133 + (j21,) * 164
    p, q = tuple(bit.blocks((j4, j14) + inside)), tuple(bit.blocks((j14, j4) + inside))
    assert [a.rank for a in p] == [10 ** 480, q[0].rank - 10 ** 480]
    assert len(q) == 1 and p[1].first == p[0].rank
    ids = tuple(first_index(bit.targets, r) for r in (4, 64))
    assert bit.target((ids[0],) * 240 + (ids[1],) * 240).rank == bit.floor ** bit.power
    c17 = first_index(comp.targets, 17)
    assert comp.target((c17,) * comp.power).rank == comp.floor ** comp.power
    # Do not enumerate the remaining blocks of this high-grade actual coefficient.
    j = first_index(comp.paid, 56)
    first, second = islice(comp.blocks((j,) * comp.power), 2)
    assert (first.first, first.rank, second.first, second.rank) == (0, 10**264, 10**264, 10**264)
    for name, word in (("BIT", bit), ("complex", comp)):
        print(name, len(word.targets), len(word.paid), word.targets[0].tag, word.paid[0].tag)
    print("paired BIT slabs", len(p), len(q), "real floor ranks", 16, 17)


class Toy:
    def __init__(self, world, word):
        self.world = world
        self.word = word
        self.data = {}
        self.serial = 0
        self.guard = {}
        self.private = self.live_centres = self.raw_frames = self.leaves = 0

    def fresh(self, exemplar, rank, tag):
        assert exemplar.owner in self.data and rank <= self.world
        key = self.serial
        self.serial += 1
        self.private += 1
        self.data[key] = [0] * self.world
        self.guard[key] = tag
        return Job(key, tuple(range(rank)))

    def zero(self, exemplar):
        job = self.fresh(exemplar, len(exemplar.axes), ("replica-padding",))
        return Job(job.owner, exemplar.axes)

    def retire(self, job):
        assert job.owner in self.guard and not any(self.data.pop(job.owner))
        del self.guard[job.owner]

    retire_zero = retire

    def raw(self, ports, columns):
        ((t0, small), (t1, large)) = ports
        assert (t0, t1) == tuple(t.tag for t in self.word.targets)
        assert len(small.axes) == columns and len(large.axes) == 4 * columns
        assert small.owner != large.owner
        self.raw_frames += 1
        # The original positive owner is now parked in a fresh full centre.
        private = self.fresh(large, len(large.axes), ("raw-centre",))
        self.data[private.owner], self.data[large.owner] = self.data[large.owner], self.data[private.owner]
        self.live_centres += int(any(self.data[private.owner]))
        actual = Job(private.owner, large.axes)
        yield self.word.paid[0].tag, small
        yield self.word.paid[1].tag, actual.select(range(3 * columns))
        yield self.word.paid[2].tag, actual.select(range(3 * columns, 4 * columns))
        self.data[private.owner], self.data[large.owner] = self.data[large.owner], self.data[private.owner]
        self.retire(private)

    def native(self, fields, columns):
        return self.word.native(fields, columns, self)

    def leaf(self, job):
        self.leaves += 1
        (i,) = job.axes
        # 4 is an exact fourth root in Z/17. This oracle uses the typed ordinals.
        self.data[job.owner][i] = 4 * self.data[job.owner][i] % 17


def nested_compilation():
    targets = (Port(("one-axis",), 1), Port(("four-axis",), 4))
    paid = (Port(("first",), 1), Port(("middle",), 3), Port(("last",), 1))
    for floor, cap in ((3, 2), (2, 1)):
        word = PoweredWord(4, targets, paid, 2, floor, cap, cap)
        rule = word.rule()
        n = 67
        planner = make_planner(rule)
        p = planner(n)
        backend = Toy(n, word)
        fields = [Job(~i, tuple((j + i) % n for j in range(n))) for i in range(p.width)]
        original = {field.owner: [(j * 11 - field.owner * 3 + 1) % 17 for j in range(n)]
                    for field in fields}
        backend.data.update({owner: state.copy() for owner, state in original.items()})
        run(rule, n, fields, backend, planner=planner)
        assert backend.leaves == p.leaves and not backend.guard and backend.live_centres > 0
        assert backend.data == {o: [4 * z % 17 for z in state] for o, state in original.items()}
        assert (sum(1 for _, k in word.target_paths() if not k) > 0
                and any(len(b.tags) == 2 and b.first > 0 for b in word.paid_paths()))
        print("strict powered tape", floor, cap, p.width, backend.raw_frames,
              backend.private, backend.live_centres, backend.leaves)


if __name__ == "__main__":
    actual_sources()
    nested_compilation()
