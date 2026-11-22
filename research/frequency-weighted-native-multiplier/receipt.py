"""Compute both signed invoices from the installed frequency-weighted source."""

from collections import Counter, defaultdict
from fractions import Fraction as Q
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
runtime = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(runtime))
from upstream import HERE as RAW_DIR, install

install()
sys.path.append(str(HERE.parent / "tiered-native-multiplier" / "source"))
sys.path.append(str(HERE / "portable"))
from activation import resource_receipt
from band_product import prepare_native
from grades import SCALES, WEIGHTS
from independent_binary_price import raw_moments
from installations import BINARY_C, GAUSSIAN_C, ENTRY, TERMINAL, activation, at_public
from linear_geometry import entrance_geometry
from ordinary_clock import first_stage_bound, polynomial_to_fibre_bound
from outer_budget import qualify
from outer_clock import financial_checks
from strict_moment import UNIT, power_interval
from strong_binary import graph, caller
from strong_complex import load_changed, word
from transport import ceil
from unpowered_price import certify, intervals
from verify_receipt import verify as fixed_installation

DEBIT = Q(151553, 2**20)


def tape_factor(ambient, rate):
    delta, lower = Q(1, 2**128), 32768
    return (
        Q(256, 255)
        * Q(4097, 4096)
        * Q(1028, 1024)
        * Q(power_interval(1024 * ambient * lower, rate)[1], UNIT)
        * (1 + Q(64, lower) + delta)
        / ((1 - Q(10, lower)) * (1 - delta) ** 3)
    )


def raw_counts(base, multiplicity):
    targets = Counter(port.rank for port in base.targets)
    paid = Counter(port.rank for port in base.paid)
    t, p = targets.copy(), paid.copy()
    for grade, number in targets.items():
        t[2 * grade] += multiplicity * number
    for grade, number in paid.items():
        p[2 * grade] += multiplicity * number
    p[1] -= 1008
    p[Q(1, 2)] += 2016
    return t, p


def total_interval(counts):
    ends = [0, 0]
    for grade, count in counts.items():
        for i, value in enumerate(intervals(grade, 1 - GAUSSIAN_C)):
            ends[i] += count * value
    return tuple(Q(value, UNIT) for value in ends)


def check_numerical(recipe):
    assert SCALES == (1, 2) and WEIGHTS == (1, 90)
    base = word(*load_changed(RAW_DIR / "inputs"))
    t, p = raw_counts(base, 90)
    assert (recipe.targets.histogram, recipe.paid.histogram) == (t, p)
    types = recipe.types()
    for variant, target, paid in zip(
        types, recipe.targets.variants, recipe.paid.variants, strict=True
    ):
        assert Counter(variant.targets) == target.histogram
        assert Counter(variant.paid) == paid.histogram
    t_lo, t_hi = total_interval(t)
    p_lo, p_hi = total_interval(p)
    assert t_lo > p_hi and p_lo / t_hi > Q(99, 100) and p_lo > 10
    assert 1 - GAUSSIAN_C > Q(996, 1000) and Q(
        power_interval(max(t), GAUSSIAN_C)[1], UNIT
    ) < Q(106, 100)
    margin, cells = certify(GAUSSIAN_C, (t, p))
    assert margin > Q(689, 10**15) and cells == recipe.cells and len(cells) == 51
    prices = recipe.typed_cells()
    rows, loads = defaultdict(Q), defaultdict(Q)
    min_share = 1
    for (a, r, b, k), share in prices.items():
        count = recipe.targets.variants[b].histogram[k]
        unit_share = share / count
        assert 5 * r <= 4 * k
        rows[a, r] += share
        loads[b, k] += (
            WEIGHTS[a]
            * recipe.paid.variants[a].histogram[r]
            * unit_share
            * Q(intervals(r, 1 - GAUSSIAN_C)[1], UNIT)
        )
        min_share = min(min_share, unit_share)
    assert all(
        rows[a, r] == 1 for a, v in enumerate(recipe.paid.variants) for r in v.histogram
    )
    for b, variant in enumerate(recipe.targets.variants):
        for k in variant.histogram:
            assert (
                0 < loads[b, k] <= WEIGHTS[b] * Q(intervals(k, 1 - GAUSSIAN_C)[0], UNIT)
            )
    assert min_share > Q(1, 2**26)
    assert prices[1, 112, 1, 258] / recipe.targets.variants[1].histogram[258] == Q(
        1, 624
    )
    assert (
        max(
            max(v.numerator.bit_length(), v.denominator.bit_length())
            for v in cells.values()
        )
        <= 261
    )
    assert recipe.ambient == 306 and tape_factor(recipe.ambient, GAUSSIAN_C) < Q(
        power_interval(2, DEBIT)[0], UNIT
    )
    cuts = {}
    for weight in (90, 91):
        chosen, required = raw_counts(base, weight)
        cap = total_interval({k: n for k, n in chosen.items() if k > 2})
        load = total_interval({r: n for r, n in required.items() if 5 * r > 8})
        net = total_interval(chosen)[0] - total_interval(required)[1]
        if weight == 90:
            assert cap[0] - load[1] > 494
        else:
            assert cap[1] - load[0] < -1515 and net > Q(3, 100)
        cuts[weight] = [str(cap[0] - load[1]), str(cap[1] - load[0])]
    return dict(
        trial=str(GAUSSIAN_C),
        weights=list(WEIGHTS),
        real_targets=[len(w.targets) for w in types],
        real_loans=[len(w.paid) for w in types],
        weighted_targets=t.total(),
        weighted_loans=p.total(),
        directed_margin=str(margin),
        grade_cells=len(cells),
        typed_cells=len(prices),
        min_individual_share=str(min_share),
        raw_loss=str(DEBIT),
        capacity_cut=cuts,
    )


def bank(profile):
    h1, h2 = profile.rank_logs
    first = (249 * (BINARY_C - Q(11, 8 * h1))) / 250
    booked = Q(int(min(first, profile.eta) * 10**21) - 1, 10**21)
    second = (249 * (BINARY_C - Q(11, 8 * h2)) + booked) / 250
    assert h1 >= 3000 and booked < profile.ordinary < min(second, profile.eta)
    gaussian = GAUSSIAN_C - DEBIT / profile.complex_log
    signed = qualify(
        profile.kappa,
        Q(1, profile.positive_stop_denominator),
        profile.ordinary,
        gaussian,
    )
    stock = resource_receipt(profile)
    assert activation(profile) == stock["public_exponent_A"]
    if h1 >= 8192:
        assert h2 >= 8192
        bound = 128 + 320 * (h1 + h2)
        additions = []
    else:
        costs = (first_stage_bound(profile.eta), polynomial_to_fibre_bound())
        additions = [
            max(0, e - 944 * h) for e, h in zip(costs, profile.rank_logs, strict=True)
        ]
        bound = 40 + 17 + 16384 * (h1 + h2) + sum(additions)
    expense = max(84500001, 1602 + 220 * profile.complex_log + bound)
    return dict(
        kappa=str(profile.kappa),
        ordinary_H=[h1, h2],
        numerical_H=profile.complex_log,
        ordinary_rates=[str(booked), str(profile.ordinary)],
        gaussian_rate=str(gaussian),
        signed=signed,
        stock=stock,
        geometry=entrance_geometry(activation(profile)),
        binary_surcharges=additions,
        log2_B=bound,
        log2_C=expense,
    )


def check():
    low, high = prepare_native()
    assert low[-1].cells is high[-1].cells and low[-1].targets is high[-1].targets
    assert (
        low[0].cells is high[0].cells and low[-1].trial == high[-1].trial == GAUSSIAN_C
    )
    target, paid = raw_moments(graph(), caller())
    for profile, recipes in zip((ENTRY, TERMINAL), (low, high), strict=True):
        assert tuple(v.rank_log for v in recipes) == (
            *profile.rank_logs,
            profile.complex_log,
        )
        for ordinary in recipes[:-1]:
            assert ordinary.ambient == 134 and ordinary.trial == BINARY_C
            assert (Counter(ordinary.targets), Counter(ordinary.paid)) == (target, paid)
    bit_margin, bit_cells = certify(BINARY_C, (target, paid))
    assert bit_margin > 0 and high[0].cells == bit_cells
    assert (tape_factor(134, BINARY_C) * Q(47, 20)) ** 8 < 2**11
    gaussian = check_numerical(high[-1])
    early, late = bank(ENTRY), bank(TERMINAL)
    A = activation(TERMINAL)
    threshold = (1 << A) + (-pow(2, A, 6)) % 6
    assert at_public(threshold - 6) is ENTRY and at_public(threshold) is TERMINAL
    premium = ceil((TERMINAL.kappa - ENTRY.kappa) * A)
    cost = 1 + max(early["log2_C"] + premium, late["log2_C"])
    assert cost == 309506891 and premium == 510
    ordinary_floor = Q(11, 8) / (BINARY_C - TERMINAL.ordinary)
    positive_floor = DEBIT / (GAUSSIAN_C - TERMINAL.ordinary)
    assert (ceil(ordinary_floor), ceil(positive_floor)) == (515494, 542294)
    older = Q(".0038982")
    gain = TERMINAL.kappa - older
    assert gain == Q(1, 50_000_000_000)
    assert financial_checks()["early_log2_C_bound"] == 84500000
    setup = fixed_installation()
    return dict(
        gaussian=gaussian,
        entry=early,
        terminal=late,
        previous_rate=str(older),
        rate_delta=str(gain),
        complete_log2_C=cost,
        entry_price_surcharge=premium,
        fixed_funding_height_floors=[ceil(ordinary_floor), ceil(positive_floor)],
        log2_fixed_setup_upper=setup["trace_exponent"],
        log2_portable_setup_guard=setup["conservative_exponent"],
        log2_native_setup_upper=228,
        portable_setup_transition_upper=setup["transitions"],
        max_native_H=max(*TERMINAL.rank_logs, TERMINAL.complex_log),
    )


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
