"""Materialize 10-shortcut w5664 + 3-type (1, 2, 3) + periodic-integral suffix + 28-bit 6-stage proofs on #8057."""
from hashlib import sha256
import json

NEW_INSTALLATION = "cbf85060a63dc4433c706d71ec582b0ebe6a09bbe26963ff78acb4c08e5edd92"
RAW_FLOOR_IMAGES = {
    "before": "0c805a525322acf4eb03f083c2c763f3046c3d488e1f993beb484a3e2c2ff4a9",
    "after": "934d2ae0b305caa364f155cc407c0e8ca479837ba70b906b8f516f67a5cc17b6",
}
SHORTCUT_FILE = "w5664_shortcut10.json.gz"
SHORTCUT_SHA = "ce395afbf5c32be64c4e62389acaf9ce8cf8a9aaaa2fb7a278135bcfa0e635aa"
SHORTCUT_IMAGES = {
    "before": "b0f18924be837173ccbbd1b7814a7a9a27228d68ff0dcbaf44a90a2065d0574c",
    "after": "2e87911b30d2d6467ceca95c4455f71ac010d7d258af3ff167320763fbccfd84",
}
SHORTCUT_PATCH = """--- a/strong_complex.py
+++ b/strong_complex.py
@@ -8,6 +8,7 @@
 import json
 
 WORD = "38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb"
+SHORTCUT_WORD = "668125b34a34c9a59a97bd66a236118d1d32f19b60dcd872b29f7dd690be0c3e"
 LAYOUT = "0ce3f9e383fc4bfdd22612b9e34fc9759d97204215937b82d23aec2cedd9b8ee"
 ADDITIONAL = "6ff19e063214b1698165d9da1fcd6182d9b837ac2d6e61aa71658b629aabbc95"
 GRID = 154113755636630124932500335624192000
@@ -42,7 +43,14 @@
     graph, _ = reconstruct(parent, read("BANK-FACTORS.json.gz"))
     if digest(graph) != WORD or digest(layout) != LAYOUT:
         raise ValueError("The reconstructed Gaussian graph or its owner layout differs")
-    return graph, layout
+    shortcut = json.loads(gzip.decompress((Path(__file__).resolve().parent / "w5664_shortcut10.json.gz").read_bytes()))
+    if digest(shortcut) != SHORTCUT_WORD:
+        raise ValueError("The shortcut Gaussian graph differs")
+    if any(shortcut[key] != graph[key] for key in ("initial", "final", "frames", "first_output")):
+        raise ValueError("The shortcut word changed an endpoint, chart or output")
+    if (len(graph["moves"]), len(shortcut["moves"])) != (5674, 5664):
+        raise ValueError("The shortcut word does not remove exactly ten transfers")
+    return shortcut, layout
 
 
 def required_pairs(graph, layout):
@@ -85,7 +93,7 @@
 
     graph, layout = load_changed(data)
     catalogue = native_catalogue(graph, layout)
-    if digest(catalogue) != "8a9ff9558bf5fa3854699937fe063f98c86467d5d32a4488bfc878d2be081e70":
+    if digest(catalogue) != "34eef62b6701db0565dce3471f165f4224194ff2782be822774f9c1255553a8d":
         raise ValueError("The generated all-column Clifford catalogue differs")
     tables = Path(grade) / "retained/data"
     bases = read_json(tables / "CALLER-PHASE-BASES.json")["by_q"]
"""
RAW_FLOOR_PATCH = """--- a/raw_binary_stage.py
+++ b/raw_binary_stage.py
@@ -45,7 +45,7 @@
 @cache
 def binary_recipe(height):
     word = binary_word()
-    return Recipe(height, word.tagged.ambient, word.targets, word.paid, word.cells, BINARY_C)
+    return Recipe(height, word.tagged.ambient, word.targets, word.paid, word.cells, BINARY_C, level_floor=1156)
""" + " \n \n def run(recipe, fields, machine):\n"


def replace(path, replacements):
    source = path.read_text()
    for old, new in replacements:
        if source.count(old) != 1:
            raise ValueError(f"Expected one change point for {old!r} in {path.name}")
        source = source.replace(old, new)
    path.write_text(source)


POSITIVE_DEBIT_PY = '''"""Price the 3-type (1, 2, 3) Gaussian calendar using the exact periodic-integral suffix theorem."""

from fractions import Fraction as Q

from grades import UPPER_DIVISOR, WEIGHTS
from strict_moment import UNIT, power_interval
from unpowered_price import intervals

BAND_LOWER = 1164
POSITIVE_DEBIT = Q(32401, 262144)
DELTA = Q(1, 2**128)


def certify_loss(recipe, lower):
    """Return the exact finite price for this three-type numerical recipe."""
    c = recipe.trial
    t = 1 - c
    targets = recipe.targets.histogram
    paid = recipe.paid.histogram
    cells = recipe.cells
    assert lower == BAND_LOWER and recipe.ambient == 459
    assert max(targets) == 387 and min(paid) == Q(1, 2)
    assert all(w > 0 and 5 * r <= 4 * k for (r, k), w in cells.items())
    assert all(sum(w for (p, k), w in cells.items() if p == r) == 1 for r in paid)

    psi = Q(0)
    for (r, k), share in cells.items():
        floor = intervals(k, c)[0] * UNIT // intervals(r, c)[1]
        assert floor > UNIT
        psi += paid[r] * share * r * (Q(floor, UNIT) - 1) / c
    target_axes = sum(count * k for k, count in targets.items())
    assert target_axes == 746688 * (WEIGHTS[0] + 2 * WEIGHTS[1] + 3 * WEIGHTS[2])

    M = 2**1024
    scale = UPPER_DIVISOR * recipe.ambient // 2
    upper = 2 * (M // (2 * scale))
    assert 4 * max(targets) * (upper - 8) < M and 774 * (upper + 2) < M
    assert 7740 <= DELTA * upper
    assert (1 - DELTA) * M <= scale * upper
    assert upper > 774 * lower and M * DELTA >= 1
    assert t > Q(996, 1000) and power_interval(lower, t)[0] > 1024 * UNIT
    assert sum(WEIGHTS) / (t * Q(power_interval(lower, t)[0], UNIT)) + Q(2, M**5) < 2
    assert 2**46 < Q(M**4, 2**132)
    assert 2**20 < Q(M**4, 2**132)
    assert 2 * 52608 < M
    assert 4 * (lower + 2) * 6 < 5 * lower * 5
    assert 2**19 * (upper + lower) ** 77 + lower**77 < (M * lower) ** 77

    periodic_num = Q(0)
    for (r, k), share in cells.items():
        rk_hi = Q(intervals(r, t)[1], intervals(k, t)[0])
        lr2 = int(2 * lower * r)
        lkr2 = int(2 * lower * k + 8 * r)
        assert Q(lr2, 2) == lower * r and Q(lkr2, 2) == lower * k + 4 * r
        rkl_lo = Q(power_interval(lr2, t)[0], power_interval(lkr2, t)[1])
        assert Q(power_interval(lower, t)[1], power_interval(upper, t)[0]) < DELTA
        term = (9 * k - 8 * r) * rk_hi - r * rkl_lo + r * DELTA
        assert term > 0
        periodic_num += paid[r] * share * term
    fringe = periodic_num / (t * psi)
    assert fringe < Q("4.55615")

    finite_factor = (
        (1 + DELTA)
        * (1 + Q(4 * max(targets), scale))
        * Q(power_interval(scale * lower, c)[1], UNIT)
        * (1 + fringe / lower + DELTA)
        / (1 - DELTA) ** 4
    )
    assert UNIT * finite_factor < power_interval(2, POSITIVE_DEBIT)[0]
    assert UNIT * finite_factor >= power_interval(2, POSITIVE_DEBIT - Q(1, 524288))[1]
    return {
        "debit": str(POSITIVE_DEBIT),
        "lower_band": lower,
        "upper_divisor": UPPER_DIVISOR,
        "upper_scale": scale,
        "weighted_target_axes": target_axes,
        "fringe": str(fringe),
        "psi_lower": str(psi),
        "upper_factor": str(finite_factor),
    }
'''


RECEIPT_PY = '''"""Compute both signed invoices from the installed 3-type + periodic-suffix source."""

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
sys.path.append(str(HERE.parent / "tiered-native-multiplier"))
from activation import resource_receipt
from band_product import prepare_native
from grades import LOWER, SCALES, WEIGHTS
from independent_binary_price import raw_moments
from installations import BINARY_C, GAUSSIAN_C, ENTRY, TERMINAL, activation, at_public
from linear_geometry import entrance_geometry
from ordinary_carrier import stage_for_width_log
from ordinary_clock import first_stage_bound, polynomial_to_fibre_bound
from outer_budget import qualify
from outer_clock import financial_checks
from strict_moment import UNIT, power_interval
from staged_carriers import entrance_logs
from strong_binary import graph, caller
from strong_complex import load_changed, word
from transport import ceil
from unpowered_price import certify, intervals
from check_serial_setup import clock as native_clock

sys.path.append(str(HERE))
from positive_debit import certify_loss

DEBIT = Q(32401, 2**18)
ORDINARY_DEBIT = Q(1418665, 2**20)
ORDINARY_FLOOR = 1156
CHILD_TARIFF = Q(2401, 1024)


def tape_factor_periodic(ambient, rate, lower, paid, cells):
    delta = Q(1, 2**128)
    t = 1 - rate
    psi = sum(
        paid[r] * sh * r * (Q(intervals(k, rate)[0], intervals(r, rate)[1]) - 1) / rate
        for (r, k), sh in cells.items()
    )
    num = Q(0)
    for (r, k), sh in cells.items():
        rk_hi = Q(intervals(r, t)[1], intervals(k, t)[0])
        rkl_lo = Q(power_interval(lower * r, t)[0], power_interval(lower * k + 4 * r, t)[1])
        term = (9 * k - 8 * r) * rk_hi - r * rkl_lo + r * delta
        num += paid[r] * sh * term
    fringe = num / (t * psi)
    M = 1 << 1024
    scale = 1024 * ambient
    U = 2 * (M // (2 * scale))
    assert 1270 <= delta * U
    return (
        Q(256, 255)
        * Q(4097, 4096)
        * Q(1028, 1024)
        * Q(power_interval(scale * lower, rate)[1], UNIT)
        * (1 + fringe / lower + delta)
        / ((1 - delta) * (1 - delta) ** 3)
    )


def raw_counts(base, weights=WEIGHTS, scales=SCALES, splits=1008):
    targets = Counter(port.rank for port in base.targets)
    paid = Counter(port.rank for port in base.paid)
    t, p = Counter(), Counter()
    for s, w in zip(scales, weights, strict=True):
        for grade, entry in targets.items():
            t[s * grade] += w * entry
        for grade, entry in paid.items():
            p[s * grade] += w * entry
    p[1] -= splits * weights[0]
    p[Q(1, 2)] += 2 * splits * weights[0]
    return t, p


def total_interval(counts, trial=GAUSSIAN_C):
    ends = [0, 0]
    for grade, count in counts.items():
        for i, value in enumerate(intervals(grade, 1 - trial)):
            ends[i] += count * value
    return tuple(Q(value, UNIT) for value in ends)


def check_numerical(recipe):
    assert SCALES == (1, 2, 3) and WEIGHTS == (1, 45, 2025)
    base = word(*load_changed(RAW_DIR / "inputs"))
    t, p = raw_counts(base, WEIGHTS, SCALES)
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
    assert margin > 0 and cells == recipe.cells and len(cells) == 71
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
    assert min_share > Q(1, 2**28)
    assert prices[2, 168, 2, 387] / recipe.targets.variants[2].histogram[387] == Q(
        1, 624
    )
    assert (
        max(
            max(v.numerator.bit_length(), v.denominator.bit_length())
            for v in cells.values()
        )
        <= 280
    )
    assert recipe.ambient == 459 and LOWER == 1164
    finite_loss = certify_loss(recipe, LOWER)
    assert Q(finite_loss["debit"]) == DEBIT

    # Negative controls: #8073/#8089/#8090 2-type (5, 451) fails new GAUSSIAN_C; and capacity-cut control
    old_t, old_p = raw_counts(base, (5, 451), (1, 2))
    try:
        old_margin, _ = certify(GAUSSIAN_C, (old_t, old_p))
    except AssertionError:
        old_margin = -1
    assert old_margin is None or old_margin <= 0
    assert total_interval(old_t)[1] < total_interval(old_p)[0]
    high = total_interval({k: n for k, n in t.items() if k > 2})
    required = total_interval({r: n for r, n in p.items() if 5 * r > 8})
    assert high[0] - required[1] > 90000
    cuts = {"3type": [str(high[0] - required[1]), str(high[1] - required[0])]}
    return dict(
        trial=str(GAUSSIAN_C),
        weights=list(WEIGHTS),
        scales=list(SCALES),
        real_targets=[len(w.targets) for w in types],
        real_loans=[len(w.paid) for w in types],
        weighted_targets=t.total(),
        weighted_loans=p.total(),
        directed_margin=str(margin),
        grade_cells=len(cells),
        typed_cells=len(prices),
        min_individual_share=str(min_share),
        raw_loss=str(DEBIT),
        finite_loss=finite_loss,
        capacity_cut=cuts,
    )


def bank(profile):
    heights = profile.rank_logs
    booked, rates = Q(0), []
    for stage, height in enumerate(heights):
        assert height >= 3000
        upper = min(profile.eta, (249 * (BINARY_C - ORDINARY_DEBIT / height) + booked) / 250)
        selected = (
            profile.ordinary
            if stage + 1 == len(heights)
            else Q(int(upper * 10**21) - 1, 10**21)
        )
        assert booked < selected < upper
        rates.append(str(selected))
        booked = selected
    gaussian = GAUSSIAN_C - DEBIT / profile.complex_log
    signed = qualify(
        profile.kappa,
        Q(1, profile.positive_stop_denominator),
        profile.ordinary,
        gaussian,
    )
    stock = resource_receipt(profile)
    assert activation(profile) == stock["public_exponent_A"]
    cuts = tuple(stock["binary_cuts"])
    assert entrance_logs(heights) == cuts
    for i, cut in enumerate(cuts, 1):
        assert stage_for_width_log(cut - 1, len(heights), heights) == i - 1
        assert stage_for_width_log(cut, len(heights), heights) == i
        assert stage_for_width_log(cut, i - 1, heights) == i - 1
    if min(heights) >= 8192:
        assert 1 <= len(heights) <= 7
        # #8076: per-stage envelope grows by 3 per stage for CHILD_TARIFF 2401/1024.
        bound = 128 + 3 * len(heights) + 320 * sum(heights)
        additions = []
    else:
        assert heights == ENTRY.rank_logs
        costs = (first_stage_bound(profile.eta), polynomial_to_fibre_bound())
        additions = [
            max(0, e - 944 * h) for e, h in zip(costs, profile.rank_logs, strict=True)
        ]
        # #8076: charge the square of the new geometric child sum 2401 (+5 entry bits).
        bound = 40 + 22 + 16384 * sum(heights) + sum(additions)
    expense = max(84500001, 1602 + 220 * profile.complex_log + bound)
    return dict(
        kappa=str(profile.kappa),
        ordinary_H=list(heights),
        numerical_H=profile.complex_log,
        ordinary_rates=rates,
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
            assert ordinary.level_floor == ORDINARY_FLOOR
            assert (Counter(ordinary.targets), Counter(ordinary.paid)) == (target, paid)
    bit_margin, bit_cells = certify(BINARY_C, (target, paid))
    assert bit_margin > 0 and high[0].cells == bit_cells
    ordinary_upper = Q("2.5543284")
    assert tape_factor_periodic(134, BINARY_C, ORDINARY_FLOOR, paid, bit_cells) * CHILD_TARIFF < ordinary_upper
    assert ordinary_upper**1048576 < 2**1418665
    assert Q(75, 32) / CHILD_TARIFF == Q(2400, 2401)
    gaussian = check_numerical(high[-1])
    early, late = bank(ENTRY), bank(TERMINAL)
    A = activation(TERMINAL)
    threshold = (1 << A) + (-pow(2, A, 6)) % 6
    assert at_public(threshold - 6) is ENTRY and at_public(threshold) is TERMINAL
    premium = ceil((TERMINAL.kappa - ENTRY.kappa) * A)
    cost = 1 + max(early["log2_C"] + premium, late["log2_C"])
    assert cost == 171810078109 and premium == 242079
    assert early["log2_C"] == 125660246 and late["log2_B"] == 171798577106
    ordinary_floor = ORDINARY_DEBIT / (BINARY_C - TERMINAL.ordinary)
    positive_floor = DEBIT / (GAUSSIAN_C - TERMINAL.ordinary)
    assert (ceil(ordinary_floor), ceil(positive_floor)) == (268290534, 52270)
    older = Q(".003900857267786")
    ref_8090 = Q(".003900826966095")
    ref_8073 = Q(".003898219753506")
    ref_8089 = Q("0.0039")
    old_gaussian_inf = Q(17145637307, 2**42)
    gain = TERMINAL.kappa - older
    assert gain == Q(5057431, 10**15)
    assert TERMINAL.kappa > older > ref_8090 > ref_8089 > ref_8073 and TERMINAL.kappa > old_gaussian_inf
    assert financial_checks()["early_log2_C_bound"] == 84500000
    setup = native_clock()
    grade_count = len(low[-1].paid.histogram) + len(low[-1].targets.histogram)
    actual_roles = sum(len(v.targets) + len(v.paid) for v in high[-1].types())
    assert actual_roles == 1002096 < 2**20 and grade_count == 72 < 2**8
    assert len(low) + len(high) == 10 and 1 <= len(TERMINAL.rank_logs) <= 7
    assert max(h.bit_length() for h in (*ENTRY.rank_logs, ENTRY.complex_log, *TERMINAL.rank_logs, TERMINAL.complex_log)) == 28
    assert TERMINAL.complex_log < 2**25 and ENTRY.complex_log < 2**25
    # 28-bit indexed setup (see SETUP-28BIT.md): 92*H and 1024*H+(m+1).bit_length() stay strictly below w=2^38.
    assert 92 * (2**28 - 1) < 2**38 and 1024 * (2**28 - 1) + (len(TERMINAL.rank_logs) + 1).bit_length() == 274877905923 < 2**38
    assert 2 * 2048 * (2**25 + 1) + 10 * 2**24 == 137606729728 < 2**40
    assert TERMINAL.eta == Q(1, 256) and all(abs(x).bit_length() <= 128 for x in (TERMINAL.eta.numerator, TERMINAL.eta.denominator, TERMINAL.kappa.numerator, TERMINAL.kappa.denominator))
    grade_actions = 2**20 * 256 + 2**8 * 256 * 8 + 32 * (grade_count + 2)**2 + 2**12
    assert grade_actions < 2**32 and setup["all_setup"] < 2**228
    return dict(
        gaussian=gaussian,
        entry=early,
        terminal=late,
        previous_rate=str(older),
        previous_8090_rate=str(ref_8090),
        previous_8073_rate=str(ref_8073),
        previous_8089_rate=str(ref_8089),
        previous_2type_G_inf_rate=str(old_gaussian_inf),
        rate_delta=str(gain),
        rate_delta_vs_8073=str(TERMINAL.kappa - ref_8073),
        complete_log2_C=cost,
        ordinary_floor=ORDINARY_FLOOR,
        ordinary_matched_suffix_proof="periodic-integral-disjoint-intervals",
        ordinary_finite_debit=str(ORDINARY_DEBIT),
        ordinary_reserve="256/255",
        ordinary_child_tariff=str(CHILD_TARIFF),
        ordinary_child_contraction="2400/2401",
        ordinary_child_geometric_sum=2401,
        ordinary_entry_clock_extra=5,
        ordinary_terminal_clock_extra=3 * len(TERMINAL.rank_logs),
        entry_price_surcharge=premium,
        fixed_funding_height_floors=[ceil(ordinary_floor), ceil(positive_floor)],
        log2_fixed_setup_upper=setup["setup_exponent"],
        native_setup_transition_upper=setup["all_setup"],
        native_setup_grade_actions=grade_actions,
        actual_roles=actual_roles,
        grade_count=grade_count,
        max_native_H=max(*TERMINAL.rank_logs, ENTRY.complex_log, TERMINAL.complex_log),
    )


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
'''


INDEPENDENT_PRICE_PY = '''"""Independently verify 3-type Gaussian & K7 periodic-integral debits on a 192-bit dyadic grid."""

from collections import Counter
from fractions import Fraction as Q
from math import ceil, isqrt
from pathlib import Path
import sys

IMAGE = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(IMAGE))
from upstream import install

install()
from band_product import prepare_native
from grades import LOWER, SCALES, UPPER_DIVISOR, WEIGHTS
from independent_binary_price import raw_moments
from installations import BINARY_C, TERMINAL
from strong_binary import caller, graph
from strong_complex import load_changed, word
from unpowered_price import certify

GRID = 1 << 192


def powers(base, exponent):
    assert base > 0 and 0 < exponent < 1
    assert exponent.denominator.bit_count() == 1
    number = Q(base) * GRID
    low, high = number.__floor__(), ceil(number)
    lower_result = upper_result = GRID
    for bit in range(exponent.denominator.bit_length() - 2, -1, -1):
        low = isqrt(low * GRID)
        high = isqrt(high * GRID - 1) + 1
        if exponent.numerator >> bit & 1:
            lower_result = lower_result * low // GRID
            upper_result = ceil(Q(upper_result * high, GRID))
    return Q(lower_result, GRID), Q(upper_result, GRID)


def weighted():
    recipe = prepare_native(TERMINAL)[-1]
    c = recipe.trial
    t = 1 - c
    assert SCALES == (1, 2, 3) and WEIGHTS == (1, 45, 2025) and LOWER == 1164
    psi = sum(
        recipe.paid.histogram[r] * share * r * (powers(Q(k, r), c)[0] - 1) / c
        for (r, k), share in recipe.cells.items()
    )
    delta = Q(1, 2**128)
    num = Q(0)
    for (r, k), share in recipe.cells.items():
        rk_hi = powers(Q(r, k), t)[1]
        rkl_lo = powers(Q(LOWER * r, LOWER * k + 4 * r), t)[0]
        num += recipe.paid.histogram[r] * share * ((9 * k - 8 * r) * rk_hi - r * rkl_lo + r * delta)
    fringe = num / (t * psi)
    assert psi > Q("6293598593") and fringe < Q("4.55615")
    scale = UPPER_DIVISOR * recipe.ambient // 2
    upper = (
        (1 + delta)
        * (1 + Q(4 * 387, scale))
        * powers(scale * LOWER, c)[1]
        * (1 + fringe / LOWER + delta)
        / (1 - delta) ** 4
    )
    lower = powers(2, Q(32401, 262144))[0]
    finer_upper = powers(2, Q(64801, 524288))[1]
    assert lower > upper and upper >= finer_upper
    # Negative control: naive 10*k suffix charge at (LOWER=1164, scale=395658) fails 32401/262144
    axes = sum(k * n for k, n in recipe.targets.histogram.items())
    naive_fringe = 10 * axes / (t * sum(recipe.paid.histogram[r] * sh * r * (powers(Q(k, r), c)[1] - 1) / c for (r, k), sh in recipe.cells.items()))
    naive_lo = ((1 + delta) * (1 + Q(4 * 387, scale)) * powers(scale * LOWER, c)[0] * (1 + naive_fringe / LOWER + delta) / (1 - delta) ** 4)
    assert naive_lo > powers(2, Q(32401, 262144))[1]


def ordinary_debit():
    bt, bp = raw_moments(graph(), caller())
    margin, cells = certify(BINARY_C, (bt, bp))
    assert margin > 0
    c = BINARY_C
    t = 1 - c
    delta = Q(1, 2**128)
    lower = 1156
    psi = sum(bp[r] * sh * r * (powers(Q(k, r), c)[0] - 1) / c for (r, k), sh in cells.items())
    num = sum(
        bp[r] * sh * ((9 * k - 8 * r) * powers(Q(r, k), t)[1] - r * powers(Q(lower * r, lower * k + 4 * r), t)[0] + r * delta)
        for (r, k), sh in cells.items()
    )
    fringe = num / (t * psi)
    child_tariff = Q(2401, 1024)
    predecessor_tariff = Q(47, 20)
    hi = (
        child_tariff
        * Q(256, 255)
        * Q(4097, 4096)
        * Q(1028, 1024)
        * powers(1024 * 134 * lower, c)[1]
        * (1 + fringe / lower + delta)
        / ((1 - delta) ** 4)
    )
    lo = (
        child_tariff
        * Q(256, 255)
        * Q(4097, 4096)
        * Q(1028, 1024)
        * powers(1024 * 134 * lower, c)[0]
        * (1 + fringe / lower + delta)
        / ((1 - delta) ** 4)
    )
    allowance_lo = 2 * powers(2, Q(370089, 2**20))[0]  # 1418665/2^20 = 1 + 370089/2^20
    finer_hi = 2 * powers(2, Q(370088, 2**20))[1]      # 1418664/2^20 fails!
    assert allowance_lo - hi > 0 and lo > finer_hi
    assert Q(75, 32) / child_tariff == Q(2400, 2401)
    assert Q(1418665, 2**20) < Q(1420718, 2**20) < Q(1424116, 2**20) < Q(1430037, 2**20) < Q(11178, 8192) < Q(11204, 8192)
    assert Q(1, 1 - Q(75, 32) / predecessor_tariff) == 376 and Q(1, 1 - Q(75, 32) / child_tariff) == 2401
    print("PASS_INDEPENDENT_PERIODIC_DEBITS", "ord=1418665/2^20", "pos=32401/262144", "2400/2401", "reserve=256/255", flush=True)


def rounded_peer():
    raw = word(*load_changed(IMAGE / "inputs"))

    def scales(ports):
        single = Counter(port.rank for port in ports)
        combined = single.copy()
        combined.update({8 * rank: count for rank, count in single.items()})
        return combined

    targets, paid = scales(raw.targets), scales(raw.paid)
    paid[1] -= 1006
    paid[Q(1, 4)] += 1006
    paid[Q(3, 4)] += 1006
    assert (targets.total(), paid.total()) == (105216, 563182)
    c = Q(4286126377, 2**40)
    endpoints = {r: powers(r, 1 - c) for r in (targets | paid)}

    def mass(rows, index):
        return sum(n * endpoints[r][index] for r, n in rows)

    tlo, thi = (mass(targets.items(), i) for i in (0, 1))
    plo, phi = (mass(paid.items(), i) for i in (0, 1))
    assert tlo > phi and plo / thi > Q(99, 100)
    for rank in sorted(paid)[1:]:
        load = mass(((r, n) for r, n in paid.items() if r >= rank), 1)
        cap = mass(((k, n) for k, n in targets.items() if 5 * rank <= 4 * k), 0)
        assert load <= cap * plo / thi
    delta, lower = Q(1, 2**128), 32768
    factor = (
        Q(256, 255)
        * Q(4097, 4096)
        * Q(1028, 1024)
        * powers(1024 * 1224 * lower, c)[1]
        * (1 + Q(64, lower) + delta)
        / ((1 - Q(10, lower)) * (1 - delta) ** 3)
    )
    assert factor**256 < 2**39
    peer_8073 = Q(".003898219753506")
    peer_8088 = Q(".003899574328473")
    peer_8089 = Q("0.0039")
    peer_8090 = Q(".003900826966095")
    peer_8094 = Q(".003900857267786")
    inf_8073 = Q(17145637307, 2**42)
    assert TERMINAL.kappa - peer_8094 == Q(5057431, 10**15)
    assert TERMINAL.kappa - peer_8073 == Q(2642571711, 10**15)
    assert TERMINAL.kappa > peer_8094 > peer_8090 > peer_8089 > peer_8088 > inf_8073 > peer_8073


if __name__ == "__main__":
    if not __debug__:
        raise ValueError("Run with assertions enabled")
    weighted()
    ordinary_debit()
    rounded_peer()
    print("PASS_INDEPENDENT_3TYPE_AND_PERIODIC_PRICES")
'''


CHECK_PLACEMENT_PY = '''"""Check the true 3-type weighted Gaussian exterior owner [2, 168, 2, 387] at both installed ranks."""

from fractions import Fraction as Q
from itertools import islice
import json
from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()
from upstream import HERE

_, _, _, source = install()
from strong_complex import artifacts
from clock_ports import clock_word
from grades import numerical_recipe, LOWER, UPPER_DIVISOR, WEIGHTS
from installations import ENTRY, TERMINAL, GAUSSIAN_C
from unpowered_price import certify
from periodic import Job
from raw48 import ComplexRaw
from transport import axes, ceil

A = artifacts(source / "research/grade14-native-realization", HERE / "inputs")
w = clock_word(A)
recipe = numerical_recipe(TERMINAL.complex_log)
targets, paid = recipe.targets, recipe.paid
c = GAUSSIAN_C
margin, flows = certify(c, (targets.histogram, paid.histogram))
assert margin > 0 and flows == recipe.cells and flows[168, 387] == 1
assert paid.variants[0].histogram[168] == 0 and paid.variants[1].histogram[168] == 0 and paid.variants[2].histogram[168] > 0
assert (
    targets.variants[0].histogram[387] == 0
    and targets.variants[1].histogram[387] == 0
    and targets.variants[2].histogram[387] == 624
)
pi = flows[168, 387] * WEIGHTS[2] / targets.histogram[387]
assert pi == Q(1, 624)
roots = tuple(
    p.tag for p in w.targets if p.rank == 129 and p.tag[:2] == ("root", "rotated")
)
assert len(roots) == 384


class Column:
    window = 1
    swap = None


class Field:
    def __init__(self):
        self.swaps = []

    def swap(self, l, r, n, service):
        self.swaps.append((l, r, n))


out = []
for H in (ENTRY.complex_log, TERMINAL.complex_log):
    M = 1 << H
    scale = UPPER_DIVISOR * recipe.ambient // 2
    assert UPPER_DIVISOR == 1724 and scale == 395658
    U = 2 * (M // (2 * scale))
    e = 2 * (3 * U // 8)
    lo, hi = Q(e * 387, 168), Q((e + 2) * 387, 168)
    assert LOWER < e < U < lo < hi < M
    assert WEIGHTS[2] * (hi - lo) * M * pi > 4
    size = 387 * (e - 8)
    period = 4 * ceil(Q(M, 4 * size))
    tickets = tuple(islice(axes(M, size, period, 0), 3))
    f = Field()
    raw = ComplexRaw(A, {}, Column(), low=0, bundle=1, slots=M)
    raw.align(f, Job(0, tickets), tuple(range(3)))
    assert period == 1364 and tickets == (0, 272, 545) and f.swaps[0] == (1, 272, 1)
    out.append(
        dict(
            H=H,
            cell=[2, 168, 2, 387],
            share=str(pi),
            rotated_roots=len(roots),
            first_root=roots[0],
            period=period,
            tickets=tickets,
            first_swap=f.swaps[0],
        )
    )
print(json.dumps(out, indent=2))
'''


CHECK_CALENDAR_PY = '''"""Exercise 3-type cross-type loans across all three kinds on real dirty finite chart records."""

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
from typed_transport import NativeType, TypedPlan, decode_header


def run():
    a = Rule(2, (2,), (1, 1))
    b = Rule(2, (2, 2), (1, 1, 1, 1))
    c = Rule(2, (2,), (1, 1))
    types = tuple(NativeType(s.targets, s.paid, m) for s, m in ((a, 1), (b, 2), (c, 3)))
    shares = {
        (0, 1, 1, 2): Q(1),
        (1, 1, 0, 2): Q(1, 7),
        (1, 1, 1, 2): Q(3, 7),
        (1, 1, 2, 2): Q(3, 7),
        (2, 1, 0, 2): Q(1, 7),
        (2, 1, 1, 2): Q(3, 7),
        (2, 1, 2, 2): Q(3, 7),
    }
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
    edges = {(kind, r.kind) for (e, kind, j), xs in p.send.items() for r in xs}
    assert (0, 1) in edges and (1, 2) in edges and (2, 0) in edges
    ca = Chart(a, ((1, 1),), p.n)
    cb = Chart(b, ((1, 1), (1, 1)), p.n)
    cc = Chart(c, ((1, 1),), p.n)
    cb.data, cb.chart = ca.data, ca.chart
    cc.data, cc.chart = ca.data, ca.chart

    class Machine:
        zero = staticmethod(ca.zero)
        leaf = staticmethod(ca.leaf)
        retire_zero = staticmethod(ca.retire_zero)

        @staticmethod
        def native(ports, tagged):
            cols, kind = decode_header(tagged)
            return (ca, cb, cc)[kind].native(ports, cols)

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
        and cc.raw
        and ca.noncommuting
        and cb.noncommuting
        and cc.noncommuting
    )
    z = -(-p.width // p.source_width)
    assert ca.leaves == z * p.rounds * p.leaves_per_epoch
    assert p.width != p.source_width
    print(
        "PASS_THREE_NATIVE_TYPES",
        p.width,
        p.source_width,
        z,
        (ca.raw, cb.raw, cc.raw),
        ca.leaves,
        (ca.noncommuting, cb.noncommuting, cc.noncommuting),
        ca.freed,
        sorted(edges),
    )


if __name__ == "__main__":
    run()
'''


CHECK_OWNERSHIP_PY = '''"""Check independent 3-type source numbering, deadlines and return of all borrowed owners."""

from fractions import Fraction as Q
from collections import Counter
import json
from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()
from typed_transport import TypedPlan, NativeType, decode_header


def run(w0, w1, w2, ticks, lower, upper, volume, n, rounds, delay):
    types = (
        NativeType((2,), (1, 1), w0),
        NativeType((2, 2), (1, 1, 1, 1), w1),
        NativeType((2,), (1, 1), w2),
    )
    rem = 2 * w1 + w2
    shares = {
        (0, 1, 1, 2): Q(1),
        (1, 1, 0, 2): Q(w0, rem),
        (1, 1, 1, 2): Q(2 * w1 - w0, rem),
        (1, 1, 2, 2): Q(w2, rem),
        (2, 1, 0, 2): Q(w0, rem),
        (2, 1, 1, 2): Q(2 * w1 - w0, rem),
        (2, 1, 2, 2): Q(w2, rem),
    }
    p = TypedPlan(
        n,
        types,
        shares,
        Q(1),
        lower,
        upper,
        volume,
        ticks,
        rounds,
        delay_base=delay,
        scale_step=Q(2),
        padding=1,
    )
    M = max(p.count.values())
    bands = len(p.bands)

    def frame_info(ident):
        packed, rep = divmod(ident, M)
        packed, typ = divmod(packed, len(types))
        birth, offset = divmod(packed, bands)
        band = lower + 2 * offset
        assert rep < p.count[(band, typ)]
        return typ, birth, band, rep

    ext = sorted(
        (src.base, src.base + src.count * ticks * (rounds // src.period), src)
        for group in p.sources.values()
        for src in group
        if rounds // src.period
    )
    end = 0
    for lo, hi, src in ext:
        assert lo == end and lo < hi
        end = hi
    assert end == p.source_width
    opened = {}
    borrowers = {}
    serials = {}
    kinds = Counter()
    transfers = Counter()
    flats = external = zero = last = peak = depth = close_on_due = child_tail = 0
    periods = Counter()
    for rec in p.events():
        op, ident, *xs = rec
        kind, birth, e, rep = frame_info(ident)
        w = types[kind]
        step = p.delay[e]
        if op == 0:
            assert ident not in opened
            cols, dkind = decode_header(xs[0])
            assert (cols, dkind) == (e - 8, kind)
            tick = birth
            it = iter(xs[1:])
            origins = []
            d = 1
            for k in w.targets:
                tag = next(it)
                if tag == 1:
                    par, expected, t0, pkind = serials.pop(next(it))
                    assert (
                        t0 == tick and par not in borrowers and expected == k * (e - 8)
                    )
                    borrowers[par] = ident
                    origins.append(par)
                    d = max(d, opened[par][2] + 1)
                    transfers[pkind, kind] += 1
                elif tag == 2:
                    base, size, period = next(it), next(it), next(it)
                    assert size == k * (e - 8) and period == 4 * (-(-n // (4 * size)))
                    assert 0 <= base <= base + rounds // period <= p.source_width
                    if rounds >= period:
                        external += 1
                    periods[period] += 1
                else:
                    assert tag == 0 and next(it) == k * (e - 8)
                    zero += 1
            assert next(it, None) is None
            opened[ident] = [0, origins, d]
            peak = max(peak, len(opened))
            depth = max(depth, d)
        elif op == 1:
            j, parents, d = opened[ident]
            tick = birth + step * j
            assert ident not in borrowers
            serial, size, sel = xs
            assert size == (e - 8) * w.paid[j] and sel <= size
            if sel:
                serials[serial] = (ident, sel, tick, kind)
            flats += size - sel
            if tick >= ticks:
                child_tail += int(sel != 0)
            opened[ident][0] += 1
        else:
            j, parents, d = opened.pop(ident)
            assert j == len(w.paid) and ident not in borrowers
            tick = birth + step * j
            for par in parents:
                assert borrowers.pop(par) == ident
                pk, pb, pe, pr = frame_info(par)
                assert p.delay[pe] >= step
                due = pb + opened[par][0] * p.delay[pe]
                assert tick <= due
                close_on_due += int(tick == due)
            kinds[kind] += 1
        assert tick >= last, (tick, last, op, e, kind)
        last = tick
    assert flats == p.leaves_per_epoch and not (
        opened or borrowers or serials or child_tail
    )
    assert kinds == Counter(
        {a: ticks * sum(v for (e, b), v in p.count.items() if b == a) for a in range(len(types))}
    )
    assert depth <= 1 + max(b.bit_length() for b in p.bands)
    return dict(
        weights=(w0, w1, w2),
        raw_frames=sum(kinds.values()),
        directed_bindings={str(k): v for k, v in transfers.items()},
        depth=depth,
        peak_simultaneous_frames=peak,
        external_opens=external,
        zeros=zero,
        external_rows=end,
        positive_periods=sorted(periods),
        leaf_axes=flats,
        same_tick_return_before_next_loan=close_on_due,
    )


out = [
    run(1, 3, 5, 12, 10, 82, 1700, 1024, 96, 4),
    run(1, 45, 2025, 8, 10, 42, 450, 384, 32, 4),
]
print(json.dumps(out, indent=2))
'''


CHECK_EXTERIOR_PY = '''"""Run all three first independent exterior births through the actual 3-type decoder and Raw48."""

from collections import Counter, defaultdict
from functools import cache
from fractions import Fraction as Q
from pathlib import Path
import sys

RUNTIME = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(RUNTIME))
from upstream import install

install()
from band_product import production_supplier
from installations import GAUSSIAN_C
from periodic import Job
from transport import Measure, Source, ceil, axes
from unpowered_price import certify
from typed_transport import TypedPlan
from typed_raw import TypedRaw

sys.path.append(str(Path(__file__).resolve().parent))
from check_raw import Axes, WitnessRaw, RayField, basis, final_ray, rot


def run():
    M = 8192
    L = 10
    U = 12
    V = 2**48
    R = M
    K = 1
    c = GAUSSIAN_C
    dens = Measure(1 - c, V, 64 * M.bit_length())
    producer = production_supplier(1024, 10**18)
    a, w = producer.physical, producer.word
    types = producer.recipe.types()
    assert len(types) == 3
    hist_t = Counter()
    hist_p = Counter()
    ids = defaultdict(list)
    for t, spec in enumerate(types):
        for i, k in enumerate(spec.targets):
            hist_t[k] += spec.multiplicity
            ids[t, k].append(i)
        for r in spec.paid:
            hist_p[r] += spec.multiplicity
    _, cells = certify(c, (hist_t, hist_p))
    assert cells == producer.recipe.cells
    assert 4 * U < 5 * L

    class FirstReplicas(TypedPlan):
        """Project three independent exterior births from the single test bin."""

        def __init__(self):
            self.n, self.types, self.ticks, self.rounds, self.bands = (
                M,
                types,
                K,
                R,
                range(L, U, 2),
            )
            self.delay = {L: 1}
            self.count = {(L, kind): 1 for kind in range(len(types))}
            self.sources, self.receive, self.send = {}, {}, {}

    p = FirstReplicas()
    full_counts = tuple(ceil(spec.multiplicity * dens.mass(L, U)[1]) for spec in types)
    first = set()
    base = 0
    for kind, spec in enumerate(types):
        chunks = {r: [] for r in set(spec.paid)}
        for (r, k), share in cells.items():
            if r not in chunks:
                continue
            left = max(U, Q(L * k, r))
            right = Q(U * k, r)
            mass = dens.mass(left, right)[0]
            for b, other in enumerate(types):
                if not ids[b, k]:
                    continue
                grant = int(
                    spec.multiplicity * mass * share * other.multiplicity / hist_t[k]
                )
                size = (L - 8) * k
                period = 4 * ceil(Q(M, 4 * size))
                if grant:
                    chunks[r].append((b, k, grant, period))
        sizes = {
            r: sum(len(ids[b, k]) * grant * (R // period) for b, k, grant, period in cs)
            for r, cs in chunks.items()
        }
        for r in spec.paid:
            if any((b, k) not in first for b, k, grant, period in chunks[r]):
                current = base
                for b, k, grant, period in chunks[r]:
                    for i in ids[b, k] if (b, k) not in first else ():
                        p.sources[L, b, i] = [Source(0, grant, current, period)]
                        current += grant * (R // period)
                    if (b, k) in first:
                        current += len(ids[b, k]) * grant * (R // period)
                    first.add((b, k))
                assert current == base + sizes[r]
            base += sizes[r]
    assert len(p.sources) == sum(len(s.targets) for s in types)
    p.source_width = base
    p.width = 1 << (4096 * base - 1).bit_length()
    assert min(full_counts) > 1
    clock, call = next(
        (i, row[1]) for i, row in enumerate(a.instructions()) if row[0] == "NATIVE"
    )
    pawn = next(
        i for i, tag in enumerate(w.targets) if tag.tag == ("helper", clock, call, 1544)
    )
    true = {}
    stock = [0, 0]
    fields = {}
    for kind, s in enumerate(types):
        for i, k in enumerate(s.targets):
            [ext] = p.sources[L, kind, i]
            owner = ext.base
            assert owner not in fields
            fields[owner] = RayField(stock)
            true[owner] = (2 * k, ext.period)

    @cache
    def placement(size, period):
        seq = tuple(axes(M, size, period, 0))
        claimed = set(seq)
        assert len(claimed) == size
        reverse = [0] * M
        for j, q in enumerate(seq):
            reverse[q] = j
        pos = size
        for q in range(M):
            if q not in claimed:
                reverse[q] = pos
                pos += 1
        assert pos == M
        return tuple(reverse)

    class Rows:
        def __getitem__(self, i):
            return Job(i, placement(*true[i]))

    expected = {}
    for kind, s in enumerate(types):
        cols = 2 * (1 + kind)
        [e] = p.sources[L, kind, pawn]
        origins = tuple((37 * i + 11 + 17 * kind) % 512 for i in range(cols))
        z = ((3 if not kind else -7 + kind) << 2048, (5 if not kind else 2 + kind) << 2048)
        fields[e.base].data = z, tuple(basis(i) for i in origins)
        output = tuple(final_ray(i) for i in origins)
        z = rot(z, sum(phase for v, phase in output))
        expected[e.base] = (
            (z[0] // 16**cols, z[1] // 16**cols),
            tuple(v for v, phase in output),
        )
    physical = WitnessRaw(a, fields, Axes(), low=0, bundle=1, slots=M)
    adapter = TypedRaw(w, physical)
    bills = [0, 0]

    class Machine:
        native = staticmethod(adapter.native)

        def leaf(self, job):
            (i,) = job.axes
            bills[0] += 1
            f = fields[job.owner]
            if f.data is not None:
                f.paid(i)
                bills[1] += 1

        @staticmethod
        def zero(exemplar):
            raise AssertionError(
                "All tested genuine first replicas received exterior fields"
            )

        retire_zero = staticmethod(physical.retire)

    p.decode(Rows(), 0, 0, Machine(), p.events())
    assert (
        bills[0] == p.leaves_per_epoch
        and {i: f.data for i, f in fields.items() if f.data is not None} == expected
    )
    assert len(fields) == sum(len(s.targets) for s in types) and all(
        f.writes and f.live for f in fields.values()
    )
    for f in fields.values():
        f.retire()
    assert stock[0] == 0
    print(
        "PASS_EXTERIOR_3TYPE_RAW",
        full_counts,
        p.source_width.bit_length(),
        len(fields),
        sum(len(s.paid) for s in types),
        bills,
        stock,
        flush=True,
    )


if __name__ == "__main__":
    run()
'''


EDITS = {
    "bootstrap.py": (
        (
            'for name in ("grades.py", "typed_raw.py", "typed_transport.py"):',
            'for name in ("grades.py", "typed_raw.py", "typed_transport.py", "w5664_shortcut10.json.gz"):',
        ),
    ),
    "runtime.patch": (
        ("+GAUSSIAN_C = Q(17145637167, 2**42)", "+GAUSSIAN_C = Q(17166573920, 2**42)"),
        ('+TERMINAL = Profile((8192, 129414, 524288), 483871, Q(".00389821"))',
         '+TERMINAL = Profile((8192, 63614, 1005821, 15903360, 251454111, 268435455), 52270, Q(".003900862325217"), Q(1, 256))'),
    ),
    "typed_transport.py": (
        (
            '''def column_header(columns, kind):
    """Write the type in the low bit of a positive even column count."""
    if columns < 2 or columns % 2 or kind not in (0, 1):
        raise ValueError("Invalid two-type column descriptor")
    return columns + kind''',
            '''def column_header(columns, kind):
    """Pack type kind (0, 1, or 2) into the low two bits of a positive even column count."""
    if columns < 2 or columns % 2 or kind not in (0, 1, 2):
        raise ValueError("Invalid typed column descriptor")
    return (columns << 1) + kind


def decode_header(header):
    """Recover columns and native type kind from a packed column header."""
    kind = header & 3
    columns = (header >> 2) << 1
    if columns < 2 or kind not in (0, 1, 2):
        raise ValueError("Invalid packed typed column header")
    return columns, kind''',
        ),
        (
            "if len(types) != 2 or lower <= 8 or upper <= lower or lower % 2 or upper % 2:",
            "if len(types) not in (2, 3) or lower <= 8 or upper <= lower or lower % 2 or upper % 2:",
        ),
        (
            "                (birth * span + (e - self.bands.start) // 2) * 2 + a",
            "                (birth * span + (e - self.bands.start) // 2) * len(self.types) + a",
        ),
    ),
    "typed_raw.py": (
        (
            """        kind = header % 2
        columns = header - kind
        if columns <= 0 or len(ports) != len(self.word.targets):
            raise ValueError("Every raw type needs a complete positive even-width job")
        if len({p.owner for p in ports}) != len(ports):
            raise ValueError("Two productive ports share a live field")
        width = columns * (1 + kind)""",
            """        kind = header & 3
        columns = (header >> 2) << 1
        if columns <= 0 or columns % 2 or kind not in (0, 1, 2) or len(ports) != len(self.word.targets):
            raise ValueError("Every raw type needs a complete positive even-width job")
        if len({p.owner for p in ports}) != len(ports):
            raise ValueError("Two productive ports share a live field")
        width = columns * (1 + kind)""",
        ),
    ),
    "grades.py": (
        ("WEIGHTS = (1, 90)", "WEIGHTS = (1, 45, 2025)"),
        ("SCALES = (1, 2)", "SCALES = (1, 2, 3)"),
        ("LOWER = 2048", "LOWER = 1164\nUPPER_DIVISOR = 1724"),
        (
            """        self.variants = (
            GradeVariant(ports, raw, 1, splits),
            GradeVariant(ports, raw, 2, 0),
        )""",
            "        self.variants = tuple(GradeVariant(ports, raw, s, splits if s == 1 else 0) for s in SCALES)",
        ),
        ("2048 * self.ambient", "UPPER_DIVISOR * self.ambient"),
        (
            "return WeightedRecipe(rank_log, 2 * word.ambient, targets, paid, cells, GAUSSIAN_C)",
            "return WeightedRecipe(rank_log, max(SCALES) * word.ambient, targets, paid, cells, GAUSSIAN_C)",
        ),
    ),
    "check_raw.py": (
        ("from typed_raw import TypedRaw", "from typed_raw import TypedRaw\nfrom typed_transport import column_header"),
        (
            "for kind, (spec, cols) in enumerate(zip(types, (2, 4))):",
            "for kind, (spec, cols) in enumerate(zip(types, (2, 4, 6))):",
        ),
        (
            "raw = WitnessRaw(a, fields, Axes(), low=0, bundle=1, slots=2 * 306)",
            "raw = WitnessRaw(a, fields, Axes(), low=0, bundle=1, slots=2 * 459)",
        ),
        (
            "it = TypedRaw(w, raw).native(jobs, 2 + kind)",
            "it = TypedRaw(w, raw).native(jobs, column_header(2, kind))",
        ),
    ),
    "check_nested.py": (
        ("from typed_raw import TypedRaw", "from typed_raw import TypedRaw\nfrom typed_transport import column_header"),
        (
            "        * cells[1, 2]\n        * 90",
            "        * cells[1, 2]\n        * types[0].multiplicity\n        * types[1].multiplicity",
        ),
        (
            "share == cells[1, 2] * 90 / t[2]",
            "share == cells[1, 2] * types[1].multiplicity / t[2]",
        ),
        (
            "and grant.numerator // grant.denominator == 899557645",
            "and 400_000_000 < grant.numerator // grant.denominator < 500_000_000",
        ),
        (
            "assert cells[1, 2] > Q(99, 100) and 24 * 1 == 12 * 2",
            "assert cells[1, 2] > Q(1, 2) and cells[1, 3] > Q(2, 5) and 24 * 1 == 12 * 2 == 8 * 3",
        ),
        (
            "    op = method.native(rows, P)",
            "    op = method.native(rows, column_header(P, 0))",
        ),
        (
            "        call2 = method.native(cr, S // 2 + 1)",
            "        call2 = method.native(cr, column_header(S // 2, 1))",
        ),
        (
            '    assert stock[0] == 0 and uses[1] > 0',
            '    # Exercise second cross-type loan: Type 1 (cols=8 -> width=16) -> Type 2 (k=3, S=24 -> cols=8, kind=2)\n'
            '    grant12 = Measure(1 - C, 2**48, 64 * n.bit_length()).mass(24, 26)[0] * cells[2, 3] * types[1].multiplicity * types[2].multiplicity / t[3]\n'
            '    assert grant12 > 0 and system.recipe.typed_cells()[1, 2, 2, 3] > 0\n'
            '    child2 = next(i for i, k in enumerate(word.targets) if k.rank == 1 and k.tag == ("helper", 9977, 0, 1315))\n'
            '    assert child2 == 10611\n'
            '    big1, small2 = types[1], types[2]\n'
            '    rows3 = [Job(i, range(8 * k)) for i, k in enumerate(big1.targets)]\n'
            '    fields3 = {i: ProductField(stock) for i in range(2 * len(word.targets))}\n'
            '    fields3[pawn].data = z, (initial(x0),) * lanes\n'
            '    exp3 = fields3[pawn].copy()\n'
            '    for i in range(8 * 16):\n'
            '        exp3.paid(i)\n'
            '    phys3 = ComplexRaw(art, fields3, Axes(), low=0, bundle=1, slots=n)\n'
            '    meth3 = TypedRaw(word, phys3)\n'
            '    op3 = meth3.native(rows3, column_header(8, 1))\n'
            '    u3 = [0, 0]\n'
            '    lent3 = False\n'
            '    for r3 in big1.paid:\n'
            '        job3 = next(op3)\n'
            '        f3 = fields3[job3.owner]\n'
            '        if lent3 or r3 < 4 or f3.data is None:\n'
            '            for ax in job3.axes:\n'
            '                f3.paid(ax)\n'
            '            continue\n'
            '        lent3 = True\n'
            '        assert len(job3.axes) == 8 * r3 and tuple(job3.axes[:24]) == tuple(range(24))\n'
            '        for ax in job3.axes[24:]:\n'
            '            f3.paid(ax)\n'
            '        pref3 = job3.select(range(24))\n'
            '        due3 = f3.copy()\n'
            '        for ax in pref3.axes:\n'
            '            due3.paid(ax)\n'
            '        cr3 = [Job(i + len(word.targets), range(8 * k)) for i, k in enumerate(small2.targets)]\n'
            '        cr3[child2] = pref3\n'
            '        call3 = meth3.native(cr3, column_header(8, 2))\n'
            '        for g3 in small2.paid:\n'
            '            ln3 = next(call3)\n'
            '            ow3 = fields3[ln3.owner]\n'
            '            assert len(ln3.axes) == 8 * g3\n'
            '            if ow3.data is not None:\n'
            '                u3[1] += 1\n'
            '            for ax in ln3.axes:\n'
            '                ow3.paid(ax)\n'
            '            u3[0] += 1\n'
            '        assert next(call3, None) is None and f3.data == due3.data\n'
            '        due3.retire()\n'
            '    assert next(op3, None) is None and lent3 and fields3[pawn].data == exp3.data and u3[1] > 0\n'
            '    exp3.retire()\n'
            '    for f3 in fields3.values():\n'
            '        f3.retire()\n'
            '    assert stock[0] == 0 and uses[1] > 0',
        ),
    ),
    "verify.py": (
        (
            '("check_calendar.py", "check_ownership.py")',
            '("check_calendar.py", "check_ownership.py", "check_cutoff.py", "check_stage_seam.py", "check_ordinary_floor.py")',
        ),
        (
            "recipe.ambient == 306\n            and len(recipe.cells) == 51",
            "recipe.ambient == 459\n            and len(recipe.cells) == 71",
        ),
    ),
}


def materialize(package):
    from pathlib import Path

    word_bytes = (Path(__file__).resolve().parent / SHORTCUT_FILE).read_bytes()
    if sha256(word_bytes).hexdigest() != SHORTCUT_SHA:
        raise ValueError("The shortcut word archive differs")
    (package / SHORTCUT_FILE).write_bytes(word_bytes)
    for name, replacements in EDITS.items():
        replace(package / name, replacements)
    (package / "positive_debit.py").write_text(POSITIVE_DEBIT_PY)
    (package / "receipt.py").write_text(RECEIPT_PY)
    (package / "independent_price.py").write_text(INDEPENDENT_PRICE_PY)
    (package / "check_placement.py").write_text(CHECK_PLACEMENT_PY)
    (package / "check_calendar.py").write_text(CHECK_CALENDAR_PY)
    (package / "check_ownership.py").write_text(CHECK_OWNERSHIP_PY)
    (package / "check_exterior.py").write_text(CHECK_EXTERIOR_PY)
    with (package / "runtime.patch").open("a") as patch:
        patch.write(RAW_FLOOR_PATCH)
        patch.write(SHORTCUT_PATCH)
    path = package / "SOURCES.json"
    pins = json.loads(path.read_bytes())
    pins["runtime_images"]["installations.py"]["after"] = NEW_INSTALLATION
    pins["runtime_images"]["raw_binary_stage.py"] = RAW_FLOOR_IMAGES
    pins["runtime_images"]["strong_complex.py"] = SHORTCUT_IMAGES
    for name in ("runtime.patch", "typed_raw.py", "typed_transport.py", "grades.py", SHORTCUT_FILE):
        pins["local_sources"][name] = sha256((package / name).read_bytes()).hexdigest()
    pins["runtime_images"]["grades.py"]["after"] = pins["local_sources"]["grades.py"]
    path.write_text(json.dumps(pins, indent=2) + "\n")
