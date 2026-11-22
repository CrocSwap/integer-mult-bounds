"""Run retimed loans from distinct positive-word calls through moving parent charts."""

from itertools import chain
from random import Random

from upstream import install

install()
from check_band import Chart, ChartJob
from periodic import Rule


def test(ticks=45):
    raw = Chart(Rule(4, (4, 4), (2, 2, 2, 2)), ((2, 2), (2, 2)), 37)
    rng = Random(3009317)
    parents = {}
    original = {}
    active = {}
    complete = []
    for birth in range(ticks):
        ports = []
        for port in range(2):
            owner = 2 * birth + port
            axes = tuple(rng.sample(range(raw.n), 32))
            row = [rng.randrange(17) for _ in range(raw.n)]
            raw.data[owner] = row.copy()
            raw.chart[owner] = 0
            original[owner] = [
                4 * a % 17 if i in axes else a for i, a in enumerate(row)
            ]
            ports.append(ChartJob(owner, axes, 0))
        parents[birth] = raw.native(ports, 8)

    def leaf(job):
        for i in range(len(job.axes)):
            raw.leaf(job.select((i,)))

    def finish(iterator):
        assert next(iterator, None) is None

    exemplar = ChartJob(0, tuple(range(16)), 0)
    cross_returns = 0
    for tick in range(ticks + 32):
        for item in active.pop(tick, []):
            finish(item[0])
            for loan in item[1]:
                raw.retire_zero(loan)
        born = tick - 32
        if born >= 0 and born in parents:
            finish(parents.pop(born))
        jobs = []
        for step in range(4):
            source = tick - 8 * step
            if source in parents:
                request = next(parents[source])
                assert len(request.axes) == 16
                jobs.append(request)
            else:
                jobs.append(None)
        if tick >= ticks:
            for job in filter(None, jobs):
                leaf(job)
        else:
            # Two unequal parent births issue to each one of these two real children.
            for a, b in ((0, 2), (1, 3)):
                ports, padded = [], []
                for job in (jobs[a], jobs[b]):
                    if job is None:
                        job = raw.zero(exemplar)
                        padded.append(job)
                    ports.append(job)
                if not padded:
                    assert ports[0].owner // 2 != ports[1].owner // 2
                    cross_returns += 1
                iterator = raw.native(ports, 4)
                active.setdefault(tick + 4, []).append((iterator, padded))
                complete.append((tick, iterator))
        for start, it in complete:
            if start <= tick < start + 4:
                leaf(next(it))

    assert not parents and not active
    assert raw.data == original and not any(raw.chart.values())
    assert raw.serial == raw.freed and raw.noncommuting and cross_returns
    return ticks, raw.raw, cross_returns, raw.leaves, raw.freed, raw.noncommuting


if __name__ == "__main__":
    print(
        "ticks, native calls, crossing returns, primitive leaves, retired zeros, noncommuting frames",
        *test(),
    )
