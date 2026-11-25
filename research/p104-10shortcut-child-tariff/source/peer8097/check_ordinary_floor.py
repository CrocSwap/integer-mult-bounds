"""Check the literal ordinary floor, periodic-integral suffix envelope, and finite replay."""
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction as Q
from hashlib import sha256
import json
from math import gcd
from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()
LOWER = 1156


def ceil(x):
    return -(-x.numerator // x.denominator)


def all_size_stock(word, c, intervals, unit):
    """Discharge the parameterized TRANSFER.md hypotheses with the periodic-integral suffix bound."""
    from strict_moment import power_interval

    t = 1 - c
    targets, paid = Counter(word.targets), Counter(word.paid)
    assert max(targets) <= 134 and min(paid) >= 1
    assert all(5 * r <= 4 * k for r, k in word.cells)
    assert all(sum(p for (u, k), p in word.cells.items() if u == r) == 1 for r in paid)
    t_lower = {k: intervals(k, t)[0] for k in targets}
    p_upper = {r: intervals(r, t)[1] for r in paid}
    t_hi = sum(n * intervals(k, t)[1] for k, n in targets.items())
    p_lo = sum(n * intervals(r, t)[0] for r, n in paid.items())
    assert sum(targets[k] * v for k, v in t_lower.items()) > sum(paid[r] * v for r, v in p_upper.items())
    assert 100 * p_lo > 99 * t_hi
    for k, n in targets.items():
        load = sum(paid[r] * p * p_upper[r] for (r, s), p in word.cells.items() if s == k)
        assert 0 < load <= n * t_lower[k]

    psi = sum(
        paid[r] * p * r * (Q(intervals(k, c)[0], intervals(r, c)[1]) - 1) / c
        for (r, k), p in word.cells.items()
    )
    target_axes = sum(k * n for k, n in targets.items())
    assert target_axes == 286098 and target_axes < 2**25

    H = 1024
    N = 1 << H
    V = N**6
    ambient = 134
    U = 2 * (N // (2048 * ambient))
    delta = Q(1, 2**128)
    assert LOWER % 2 == 0 and 8 < LOWER and 24 * (LOWER + 2) < 25 * LOWER
    assert (LOWER - 8, LOWER - 6) == (1148, 1150)
    assert max(Q(k, r) for r, k in word.cells) * LOWER < U
    assert max(Q(k, r) for r, k in word.cells) * (U + 2) < N
    assert 4 * max(targets) * (U - 8) < N and U * ambient <= Q(N, 1024)
    assert U * 1024 * ambient >= (1 - delta) * N
    assert 1270 <= delta * U

    periodic_num = Q(0)
    for (r, k), p in word.cells.items():
        rk_hi = Q(intervals(r, t)[1], intervals(k, t)[0])
        rkl_lo = Q(power_interval(LOWER * r, t)[0], power_interval(LOWER * k + 4 * r, t)[1])
        assert Q(power_interval(LOWER, t)[1], power_interval(U, t)[0]) < delta
        term = (9 * k - 8 * r) * rk_hi - r * rkl_lo + r * delta
        assert term > 0
        periodic_num += paid[r] * p * term
    fringe = periodic_num / (t * psi)
    assert 0 < fringe < Q("4.53") and psi > 1

    assert Q(6, 5) ** 4 > 2 and Q(6, 5) ** 73 > 2**19
    assert len(word.paid) < 2**19
    assert 2**19 * Q(1, 1024 * ambient * LOWER) ** 77 + Q(1, N**77) < 1
    lower_power = Q(intervals(LOWER, t)[0], unit)
    assert lower_power > 1024 and Q(1, t * lower_power) + Q(2, N**5) < 2
    assert c.denominator.bit_length() - 1 <= 60 and Q(1, N) - Q(1, 2 ** (64 * (H + 1))) > Q(1, 512 * N)
    grid_error_bits = 397 + 31 * H + 6 * H + 3 - 64 * (H + 1)
    assert grid_error_bits < -132
    assert c > 0 and 1 < LOWER and U <= N
    suffix_birth_error = Q(20 * U * target_axes, V) / psi
    integer_mass_error = Q(2**46, N**4)
    delay_end_error = Q(2**20, N**4)
    assert suffix_birth_error < Q(2**30, N**5) < Q(1, 2**132)
    assert integer_mass_error < Q(1, 2**132) and delay_end_error < Q(1, 2**132)
    assert 4 * Q(1, 2**132) < delta
    assert 4096 * 2 * len(word.targets) < N**2
    assert (1 - delta) * psi - Q(1, 2**130) > 1
    assert (1 - Q(1, N)) / Q(257, 256) > Q(1, 2)
    return {
        "fringe_upper_1e9": ceil(fringe * 10**9),
        "psi_lower_floor": int(psi),
        "grid_absolute_error_exponent_at_H1024": grid_error_bits,
        "suffix_target_axes": target_axes,
        "suffix_birth_error_upper_at_H1024": "2^30/N^5",
        "normalized_error_allowance": "2^-128",
        "birth_bound": "2V",
        "copy_group_bound": "3N^3",
        "whole_field_width": "N^92",
        "first_two_columns": [LOWER - 8, LOWER - 6],
        "minimum_positive_scale_h_guard": 1024,
    }


@dataclass(frozen=True)
class Pow2:
    """Symbolic exact power of two 2**exp."""

    exp: int

    def __pow__(self, power):
        assert type(power) is int and power >= 0
        return Pow2(self.exp * power)

    def __floordiv__(self, divisor):
        assert type(divisor) is int and divisor > 0
        return FloorPow2(self.exp, divisor)


@dataclass(frozen=True)
class FloorPow2:
    """Symbolic exact quotient (2**exp) // divisor."""

    exp: int
    divisor: int

    def __rmul__(self, factor):
        assert type(factor) is int and factor > 0
        return TimesFloorPow2(factor, self.exp, self.divisor)


@dataclass(frozen=True)
class TimesFloorPow2:
    """Symbolic exact product factor * ((2**exp) // divisor)."""

    factor: int
    exp: int
    divisor: int


class ShiftCount(int):
    """Exponent wrapper intercepting 1 << height inside unmodified Recipe.open()."""

    def __rlshift__(self, base):
        assert base == 1
        return Pow2(int(self))


def realize(value):
    """Evaluate symbolic power-of-two expressions back to exact Python integers."""
    if isinstance(value, Pow2):
        return 1 << value.exp
    if isinstance(value, FloorPow2):
        return (1 << value.exp) // value.divisor
    if isinstance(value, TimesFloorPow2):
        return value.factor * ((1 << value.exp) // value.divisor)
    return value


def bound_recipe(old, lower):
    """Pass the proposed literal cutoff through the unmodified Recipe.open seam."""
    import transport

    H = old.rank_log
    assert old.level_floor == lower and old.width_log == 92 * H
    expected_divisor = 2048 * old.ambient

    def call_arguments(symbolic):
        real_plan = transport.Plan
        old_rank, old_width = old.rank_log, old.width_log
        try:
            if symbolic:
                old.rank_log, old.width_log = ShiftCount(H), ShiftCount(92 * H)
            transport.Plan = lambda *args, **kwargs: (args, kwargs)
            return old.open()
        finally:
            old.rank_log, old.width_log, transport.Plan = old_rank, old_width, real_plan

    sym_args, sym_kw = call_arguments(True)
    n, targets, paid, cells, t, l, u, volume, ticks, rounds = sym_args
    assert n == Pow2(H) and (l, u) == (lower, TimesFloorPow2(2, H, expected_divisor)) and t == 1 - old.trial
    assert targets is old.targets and paid is old.paid and cells is old.cells
    assert (volume, ticks, rounds) == (Pow2(6 * H), Pow2(82 * H), Pow2(2 * H))
    assert sym_kw == {"width": Pow2(92 * H), "delay_base": 1 << 19}

    literal_cross_checked = H <= 2_000_000
    if literal_cross_checked:
        lit_args, lit_kw = call_arguments(False)
        assert tuple(map(realize, sym_args)) == lit_args
        assert {k: realize(v) for k, v in sym_kw.items()} == lit_kw

    return {
        "height": H,
        "lower": lower,
        "ambient": old.ambient,
        "first_columns": lower - 8,
        "plan_arguments_checked": True,
        "literal_cross_checked": literal_cross_checked,
        "trace": "symbolic-exact-operator-interception",
    }


def finite_plan(word, c):
    """Replay a two-port cut fixture on one occupied K7 edge and verify pointwise + periodic suffix bounds."""
    from transport import Measure, Plan
    from strict_moment import UNIT
    from unpowered_price import intervals

    r, k = max(word.cells, key=lambda edge: Q(edge[0], edge[1]))
    hi = 2 * ceil(Q((LOWER + 4) * k, 2 * r)) + 4
    n = 1 << (4 * k * hi - 1).bit_length()
    volume = 8 * hi**2
    ticks, radix = 5, 4
    t = 1 - c
    plan = Plan(n, (k,), (r,), {(r, k): Q(1)}, t, LOWER, hi, volume, ticks, n, delay_base=radix)
    assert plan.bands.start == LOWER and LOWER - 2 not in plan.count
    mass = Measure(t, volume, 64 * n.bit_length())
    contacts = []
    suffix_bound_unit = (volume / t) * (
        (9 * k - 8 * r) * Q(UNIT, intervals(Q(LOWER * k, r), t)[0])
        - r * Q(UNIT, intervals(Q(LOWER * k, r) + 4, t)[1])
        + r * Q(UNIT, intervals(hi, t)[0])
    )
    empirical_suffix = 0
    for d in range(LOWER, hi, 2):
        for i in range(1):
            for link in plan.receive.get((d, i), ()):
                e = link.band
                dif = r * (e - 8) - k * (d - 8)
                assert 0 <= dif <= 10 * k - 8 * r - 2 * gcd(r, k)
                empirical_suffix += link.count * dif
    assert empirical_suffix <= ticks * suffix_bound_unit

    for d in (LOWER, LOWER + 2):
        assert plan.count[d] == ceil(mass.mass(d, d + 2)[1])
        grants = []
        for i in range(1):
            assert plan.receive[d, i]
            for link in plan.receive[d, i]:
                e = link.band
                a, b = max(e, Q(d * k, r)), min(e + 2, Q((d + 2) * k, r))
                grant = mass.mass(a, b)[0]
                assert link.count == grant.numerator // grant.denominator
                assert 0 < grant and 2 * plan.delay[d] < plan.delay[e]
                assert 0 <= r * (e - 8) - k * (d - 8) <= 10 * k - 8 * r - 2 * gcd(r, k)
                grants.append((i, link.port, e, link.count))
        contacts.append((d, plan.count[d], grants))

    live, pending, held = {}, {}, Counter()
    axes = opens = closes = loans = 0
    first_counts = Counter()
    for op, frame, *args in plan.events():
        if op == 0:
            assert frame not in live
            columns, *bindings = args
            size = k * columns
            parents = []
            cursor = iter(bindings)
            for kind in cursor:
                if kind == 1:
                    sender, prefix = pending.pop(next(cursor))
                    assert sender in live and prefix == size
                    held[sender] += 1
                    parents.append(sender)
                    loans += 1
                    if columns in (LOWER - 8, LOWER - 6):
                        first_counts[columns] += 1
                elif kind == 2:
                    _, width, period = next(cursor), next(cursor), next(cursor)
                    assert width == size and period % 4 == 0
                else:
                    assert kind == 0 and next(cursor) == size
            live[frame] = parents
            opens += 1
        elif op == 1:
            serial, size, selected = args
            assert frame in live and held[frame] == 0
            axes += size - selected
            if selected:
                assert serial not in pending
                pending[serial] = (frame, selected)
        else:
            assert op == 2 and held[frame] == 0
            for sender in live.pop(frame):
                held[sender] -= 1
                assert held[sender] >= 0 and sender in live
            closes += 1
    assert not live and not pending and not any(held.values()) and opens == closes
    assert axes == plan.leaves_per_epoch and len(first_counts) == 2
    return {
        "tested_occupied_K7_grade": [r, k],
        "lower": LOWER,
        "upper": hi,
        "carrier": n,
        "first_band_contacts": contacts,
        "native_opens": opens,
        "native_closes": closes,
        "returned_paid_prefixes": loans,
        "paid_singletons": axes,
        "lower_return_counts": dict(first_counts),
        "empirical_suffix_axes": empirical_suffix,
        "periodic_suffix_bound": float(ticks * suffix_bound_unit),
        "extent": "complete fixture event stream",
    }


def check():
    from band_product import prepare_native
    from installations import BINARY_C, ENTRY, TERMINAL
    from raw_binary_stage import binary_word
    from strict_moment import UNIT
    from unpowered_price import intervals

    stage = (RUNTIME / "raw_binary_stage.py").read_bytes()
    assert (
        sha256(stage).hexdigest()
        == "934d2ae0b305caa364f155cc407c0e8ca479837ba70b906b8f516f67a5cc17b6"
    )
    assert (
        sha256((RUNTIME / "transport.py").read_bytes()).hexdigest()
        == "9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818"
    )
    assert TERMINAL.rank_logs == (8192, 63614, 1005821, 15903360, 251454111, 268435455) and TERMINAL.complex_log == 52270
    word = binary_word()
    assert (len(word.targets), len(word.paid), len(word.cells)) == (18906, 104652, 24)
    a, b = prepare_native()
    ordinary = (*a[:-1], *b[:-1])
    assert tuple(recipe.rank_log for recipe in ordinary) == (*ENTRY.rank_logs, *TERMINAL.rank_logs)
    assert (a[-1].rank_log, b[-1].rank_log) == (1024, 52270)
    openings = [bound_recipe(recipe, LOWER) for recipe in ordinary]
    stock = all_size_stock(word, BINARY_C, intervals, UNIT)
    finite = finite_plan(word, BINARY_C)
    assert finite["tested_occupied_K7_grade"] == [49, 64]
    assert finite["native_opens"] > 0 and finite["returned_paid_prefixes"] > 0
    print(
        "PASS_LITERAL_ORDINARY_FLOOR",
        json.dumps(
            {
                "new_binary_openings": openings,
                "binary_all_size": stock,
                "binary_integer_fixture": finite,
            },
            sort_keys=True,
        ),
        flush=True,
    )


if __name__ == "__main__":
    check()
