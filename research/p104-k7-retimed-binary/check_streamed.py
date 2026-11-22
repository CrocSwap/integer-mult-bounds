"""Run a fixed-width cohort across ragged group and period boundaries."""

from fractions import Fraction as F
from random import Random
from upstream import install

install()
from check_band import Chart, ChartJob
from periodic import Rule
from transport import Plan


def check():
    source = Rule(2, (2, 2), (1, 1, 1, 1))
    plan = Plan(
        224,
        source.targets,
        source.paid,
        {(1, 2): F(1)},
        F(1),
        12,
        34,
        1536,
        9,
        32,
        width=4096,
        delay_base=4,
        scale_step=F(2),
        padding=1,
    )
    assert plan.width % plan.source_width and plan.width > 2 * plan.source_width
    assert any(
        plan.rounds % s.period for sources in plan.sources.values() for s in sources
    )
    assert not hasattr(plan, "image")
    chart = Chart(source, ((1, 1), (1, 1)), plan.n)
    rng = Random(1389)
    lanes = []
    original = {}
    for i in range(plan.width):
        lane = ChartJob(i, tuple(rng.sample(range(plan.n), plan.n)), 0)
        original[i] = [rng.randrange(17) for _ in lane.axes]
        chart.data[i] = original[i].copy()
        chart.chart[i] = 0
        lanes.append(lane)
    plan.run(lanes, chart)
    z = -(-plan.width // plan.source_width)
    assert all(
        chart.data[i] == [4 * x % 17 for x in row] for i, row in original.items()
    )
    assert chart.leaves == z * plan.rounds * plan.leaves_per_epoch
    assert not any(chart.chart.values()) and chart.freed == chart.serial
    print(
        "fixed width / slots / groups / actual leaves / raw / zero returns / chart checks",
        plan.width,
        plan.source_width,
        z,
        chart.leaves,
        chart.raw,
        chart.freed,
        chart.noncommuting,
    )


if __name__ == "__main__":
    check()
