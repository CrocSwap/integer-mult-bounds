"""Suspend a streamed numerical epoch inside one of its real paid singleton calls."""

from fractions import Fraction as F
from random import Random
from upstream import install

install()
from check_band import Chart, ChartJob
from periodic import Rule
from transport import Plan


def sample(plan, seed, reenter=None):
    rule = Rule(2, (2, 2), (1, 1, 1, 1))

    class Nested(Chart):
        nested = False

        def leaf(self, job):
            if not self.nested and reenter is not None:
                self.nested = True
                reenter()
            super().leaf(job)

    chart = Nested(rule, ((1, 1), (1, 1)), plan.n)
    random = Random(seed)
    fields = []
    for owner in range(plan.width):
        fields.append(ChartJob(owner, tuple(random.sample(range(plan.n), plan.n)), 0))
        chart.data[owner] = [random.randrange(17) for _ in range(plan.n)]
        chart.chart[owner] = 0
    plan.decode(fields, 5, 0, chart, plan.events())
    assert chart.leaves == plan.leaves_per_epoch and chart.freed == chart.serial
    assert not any(chart.chart.values()) and chart.nested == (reenter is not None)
    return chart.data


if __name__ == "__main__":
    plan = Plan(
        224,
        (2, 2),
        (1, 1, 1, 1),
        {(1, 2): F(1)},
        F(1),
        12,
        34,
        1536,
        9,
        32,
        width=2048,
        delay_base=4,
        scale_step=F(2),
        padding=1,
    )
    expected = sample(plan, 992)
    inside = sample(plan, 1436)

    def nested():
        assert sample(plan, 1436) == inside

    assert sample(plan, 992, nested) == expected
    print(
        "nested same-program stream restored both complete 2,048-row schedules; leaves each",
        plan.leaves_per_epoch,
    )
