"""Check the literal raw ranks and a transport with a strict descent on every loan."""

from collections import Counter
from fractions import Fraction as F

from upstream import HERE, install

_, _, _, src = install()
from strong_complex import load_changed, word
from strict_moment import power_interval, UNIT


def ranks():
    graph, layout = load_changed(HERE / "inputs")
    raw = word(graph, layout)
    target = Counter(F(p.rank) for p in raw.targets)
    paid = Counter(F(p.rank) for p in raw.paid)
    paid[1] -= 1008
    paid[F(1, 2)] = 2016
    return target, paid


def intervals(r, t):
    if r == F(1, 2):
        low, high = power_interval(2, t)
        return (UNIT * UNIT // high, -(-UNIT * UNIT // low))
    return power_interval(int(r), t)


def certify(C, census=None):
    t = 1 - C
    targets, paid = ranks() if census is None else census
    target_mass = {k: n * intervals(k, t)[0] for k, n in targets.items()}
    paid_mass = {r: n * intervals(r, t)[1] for r, n in paid.items()}
    target_total, paid_total = sum(target_mass.values()), sum(paid_mass.values())
    if target_total <= paid_total:
        return 1 - F(paid_total, target_total), None
    margin = 1 - F(paid_total, target_total)
    capacity = {k: F(x * paid_total, target_total) for k, x in target_mass.items()}
    cells = {}
    for r in sorted(paid, reverse=True):
        remain = paid_mass[r]
        for k in sorted(targets, reverse=True):
            if 4 * k < 5 * r or not remain:
                break
            part = min(remain, capacity[k])
            if not part:
                continue
            cells[r, k] = F(part, paid_mass[r])
            capacity[k] -= part
            remain -= part
        if remain:
            raise AssertionError((r, remain))
    assert all(not x for x in capacity.values())
    assert all(sum(q for (p, k), q in cells.items() if p == r) == 1 for r in paid)
    for k in targets:
        incoming = sum(paid_mass[r] * q for (r, z), q in cells.items() if z == k)
        assert incoming == F(target_mass[k] * paid_total, target_total)
    return margin, cells
