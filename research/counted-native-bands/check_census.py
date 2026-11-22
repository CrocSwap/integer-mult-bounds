"""Compare the compressed counts and the streamed loans with independent labelled executions."""

from collections import Counter
from random import Random

from check_band import Chart, ChartJob, census as labelled_oracle
from counted_band import GradeRule, split_runs
from epoch_tape import Compiler as Installed, run
from periodic import Rule
from powered import Port
from smooth_word import SmoothWord
from stream_epoch import Compiler


class LiteralRule:
    def __init__(self, rule):
        self.source, self.ambient = rule, rule.ambient

    def grades(self):
        return Counter(self.source.targets), Counter(self.source.paid)

    def target_ranks(self):
        return iter(self.source.targets)

    def paid_ranks(self):
        return iter(self.source.paid)


def cases():
    totals = 0
    for cap in range(1, 30):
        for rank in range(1, 257):
            pieces = list(split_runs(rank, cap))
            assert sum(k * count for k, count in pieces) == rank
            assert all(0 < k <= cap and count >= 1 for k, count in pieces)
            assert rank <= cap or all(k == cap or k & (k - 1) == 0 for k, _ in pieces)
    for v in range(1, 5):
        def labels(values):
            return tuple(Port((i,), rank) for i, rank in enumerate(values))
        word = SmoothWord(9, labels([4, 8, 9]), labels([1, 2, 3, 7]), v, 4, 2, 2)
        targets, paid = GradeRule(word).grades()
        literal = word.rule()
        assert (targets, paid) == (Counter(literal.targets), Counter(literal.paid))
        for tag, original in enumerate(word.paid):
            blocks = list(word.blocks((tag,) * v))
            assert [b.first for b in blocks] == list(cumulative(b.rank for b in blocks))
            assert sum(b.rank for b in blocks) == original.rank**v
        totals += sum(paid.values())
    counts = 0
    for plain in (Rule(5, (5,), (2, 2, 1)), Rule(6, (4, 6), (2, 1, 2)),
                  Rule(8, (4, 6, 8), (1, 2)), Rule(8, (8, 8), (4, 4, 2))):
        for floor in (2, 3, 5):
            new = Compiler(LiteralRule(plain), floor)
            for n in (1, 20, 101, 197, 293, 323, 423, 517, 725):
                plan = new(n)
                width, leaves, separate = labelled_oracle(plain, n, floor)
                assert (plan.width, plan.leaves) == (width, leaves)
                if plan.forest:
                    assert [plan.forest.terminal, plan.forest.fringe] == separate
                counts += 1
    return totals, counts


def cumulative(lengths):
    offset = 0
    for size in lengths:
        yield offset
        offset += size


def tensor_slices():
    from check_powered import Toy
    from periodic import Job

    word = SmoothWord(4, (Port(("small",), 1), Port(("large",), 4)),
                      (Port(("a",), 1), Port(("b",), 3), Port(("c",), 1)), 3, 3, 2, 2)
    machine = Toy(128, word)
    fields = [Job(-1, tuple(reversed(range(128))))]
    before = [(17 + 7 * i) % 17 for i in range(128)]
    machine.data[-1] = before.copy()
    ranks = []
    for job in word.native(fields, 2, machine):
        ranks.append(len(job.axes) // 2)
        for i in range(len(job.axes)):
            machine.leaf(job.select((i,)))
    assert ranks == [b.rank for b in word.paid_paths()]
    assert [b.rank for b in word.blocks((1, 1, 1))] == [8, 8, 8, 2, 1]
    assert machine.data == {-1: [4 * v % 17 for v in before]} and not machine.guard
    return len(ranks), machine.raw_frames, machine.private


def chronology():
    rule = Rule(3, (2, 3), (1, 1, 1, 1, 1))
    parts = ((1, 1), (1, 1, 1))
    rank = 51
    lite = LiteralRule(rule)
    compiler = Compiler(lite, 2)
    plan = compiler(rank)
    oldplan = Installed(rule, 2)(rank)
    assert plan.forest and plan.forest.fringe > 0 and rank % 4 == 3
    assert (plan.width, plan.leaves) == (oldplan.width, oldplan.leaves)
    signals = Counter()
    def one(nested):
        rng = Random(26711 + nested)
        backend = Chart(rule, parts, rank)
        jobs = [ChartJob(i, tuple(rng.sample(range(rank), rank)), 0) for i in range(plan.width)]
        before = {j.owner: [rng.randrange(17) for _ in j.axes] for j in jobs}
        backend.data = {i: values.copy() for i, values in before.items()}
        backend.chart = dict.fromkeys(before, 0)
        original = backend.leaf
        def leaf(job):
            if not nested and not signals["inner"]:
                signals["inner"] += 1
                one(True)
            original(job)
        backend.leaf = leaf
        run(lite, rank, jobs, backend, planner=compiler)
        assert backend.data == {i: [4 * x % 17 for x in a] for i, a in before.items()}
        assert backend.leaves == plan.leaves and backend.serial == backend.freed
        assert backend.raw and backend.noncommuting and not any(backend.chart.values())
        signals.update({"raw": backend.raw, "leaves": backend.leaves, "freed": backend.freed})
    one(False)
    return rank, plan.width, dict(signals)


if __name__ == "__main__":
    print("paid occurrences and labelled census cases", *cases(), flush=True)
    print("true powered slices, raw frames and restored private owners", *tensor_slices())
    print("nested arbitrary-input executions", *chronology(), flush=True)
