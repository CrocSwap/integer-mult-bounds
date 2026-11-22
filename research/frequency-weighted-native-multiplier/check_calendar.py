"""Exercise cross-type loans on real dirty finite chart records."""

from fractions import Fraction as Q
from random import Random
from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()
from check_band import Chart, ChartJob
from periodic import Rule
from typed_transport import NativeType, TypedPlan


def run():
    a = Rule(2, (2,), (1, 1))
    b = Rule(2, (2, 2), (1, 1, 1, 1))
    types = tuple(NativeType(s.targets, s.paid, m) for s, m in ((a, 1), (b, 2)))
    shares = {(0, 1, 1, 2): Q(1), (1, 1, 0, 2): Q(1, 4), (1, 1, 1, 2): Q(3, 4)}
    p = TypedPlan(
        192,
        types,
        shares,
        Q(1),
        10,
        30,
        1200,
        5,
        16,
        delay_base=4,
        scale_step=Q(2),
        padding=1,
    )
    # Each side of the funding exchange must have at least one real loan.
    edges = {(kind, r.kind) for (e, kind, j), xs in p.send.items() for r in xs}
    assert (0, 1) in edges and (1, 0) in edges
    ca = Chart(a, ((1, 1),), p.n)
    cb = Chart(b, ((1, 1), (1, 1)), p.n)
    cb.data, cb.chart = ca.data, ca.chart

    class Machine:
        zero = staticmethod(ca.zero)
        leaf = staticmethod(ca.leaf)
        retire_zero = staticmethod(ca.retire_zero)

        @staticmethod
        def native(ports, tagged):
            return (ca, cb)[tagged % 2].native(ports, tagged - tagged % 2)

    rand = Random(8582)
    rows = []
    initial = {}
    for i in range(p.width):
        row = ChartJob(i, tuple(rand.sample(range(p.n), p.n)), 0)
        rows.append(row)
        initial[i] = [rand.randrange(17) for _ in range(p.n)]
        ca.data[i] = initial[i].copy()
        ca.chart[i] = 0
    p.run(rows, Machine())
    assert ca.data == {i: [(4 * x) % 17 for x in row] for i, row in initial.items()}
    assert (
        not any(ca.chart.values())
        and ca.freed == ca.serial
        and ca.raw
        and cb.raw
        and ca.noncommuting
        and cb.noncommuting
    )
    z = -(-p.width // p.source_width)
    assert ca.leaves == z * p.rounds * p.leaves_per_epoch
    assert p.width != p.source_width
    print(
        "PASS_TWO_NATIVE_TYPES",
        p.width,
        p.source_width,
        z,
        (ca.raw, cb.raw),
        ca.leaves,
        (ca.noncommuting, cb.noncommuting),
        ca.freed,
        edges,
    )


if __name__ == "__main__":
    run()
