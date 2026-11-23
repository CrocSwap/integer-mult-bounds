"""Check the period invoice, 25-bit signed seams and predecessor cap."""
from dataclasses import replace
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import sys

RUNTIME = Path(sys.argv[1]).resolve()
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RUNTIME))
from upstream import install
install()
sys.path.append(str(HERE.parent / "tiered-native-multiplier" / "source"))

from activation import resource_receipt
from band_product import prepare_native
from check_stage_seam import verify_stage, verify_tape
from installations import ENTRY, TERMINAL, BINARY_C, GAUSSIAN_C, activation
from outer_budget import qualify
from outer_clock import financial_checks
from raw_binary_stage import binary_word
from retune import PROFILES
from staged_carriers import entrance_logs

ORDINARY = Q(11239, 8192)
GAUSSIAN = Q(64934, 524288)
PREVIOUS_GAUSSIAN = Q(64939, 524288)
TICK = 10**21
STOP = Q(1, 10**18)


def ordinary_upper(heights):
    r = Q(0)
    for index, h in enumerate(heights):
        u = min(TERMINAL.eta, (249 * (BINARY_C - ORDINARY / h) + r) / 250)
        r = u if index == len(heights) - 1 else Q((u * TICK).__floor__() - 1, TICK)
    return r


def gaussian_upper(h, debit=GAUSSIAN):
    return GAUSSIAN_C - debit / h


def rejected(function, label):
    try:
        function()
    except (AssertionError, ArithmeticError, ValueError):
        return label
    raise AssertionError(f"Negative control {label} was not rejected")


def relaxed_ordinary_upper(total):
    """Upper bound the ordinary rate under a maximum height sum.

    Intermediate floor ticks and the eta clamp are relaxed.  Cauchy gives
    w2/h2 + w3/h3 >= (sqrt(w2)+sqrt(w3))^2/(h2+h3).  We use a strict
    rational lower enclosure on 1/sqrt(250) and prove the resulting function
    increases from h1=8192, so even the relaxed shorter sum cannot pass.
    """
    m = total
    hmin = 8192
    w1 = Q(1, 62500)
    r = Q(6324555320336758663997787088865437067439, 10**41)
    assert r*r < Q(1, 250) < (r + Q(1, 10**41))**2
    assert w1 / hmin**2 < (1 + r)**2 / (m - hmin)**2
    loss_lower = w1 / hmin + (1 + r)**2 / (m - hmin)
    return BINARY_C * (1 - Q(1, 250**3)) - Q(249, 250) * ORDINARY * loss_lower


def predecessor_upper():
    previous = json.loads((HERE / "PREDECESSOR-RESULT.json").read_bytes())
    term = previous["terminal"]
    assert (tuple(term["ordinary_H"]), term["numerical_H"], Q(term["kappa"])) == (
        (8192, 38102, 604362), 18845936, Q(".00389846"))
    rate, height, cap = Q(term["kappa"]), term["numerical_H"], previous["complete_log2_C"]
    paid = rate + 5 * STOP
    gaussian = gaussian_upper(height, PREVIOUS_GAUSSIAN)
    assert Q(term["gaussian_rate"]) == gaussian
    assert gaussian_upper(height - 1, PREVIOUS_GAUSSIAN) < paid < gaussian
    assert ordinary_upper(term["ordinary_H"]) > gaussian
    assert cap == 1731 + 320 * sum(term["ordinary_H"]) + 220 * height == 4354317571
    assert (cap - 1731 - 220 * (height + 1)) // 320 == 650655
    assert relaxed_ordinary_upper(650655) < paid
    ceiling = gaussian - 5 * STOP
    assert ceiling == Q(15407802515941573408769828489,3952279237427200000000000000000)
    return ceiling


def check():
    key = next(k for k, p in PROFILES.items() if Q(p["kappa"]) == TERMINAL.kappa)
    expected = PROFILES[key]
    ranks = tuple(TERMINAL.rank_logs)
    assert ranks == expected["heights"] and TERMINAL.complex_log == expected["gaussian"]
    old_ceiling = predecessor_upper()
    assert TERMINAL.kappa > old_ceiling
    assert TERMINAL.kappa - Q(".00389846") == Q(101,200000000000000)
    paid = TERMINAL.kappa + 5 * STOP
    assert TERMINAL.ordinary == paid
    assert ordinary_upper(ranks) > paid
    assert gaussian_upper(TERMINAL.complex_log) > paid
    assert gaussian_upper(TERMINAL.complex_log, PREVIOUS_GAUSSIAN) < paid
    assert gaussian_upper(TERMINAL.complex_log - 2) < paid < gaussian_upper(TERMINAL.complex_log - 1)
    assert 0 < paid < GAUSSIAN_C and GAUSSIAN > 0
    # For every positive Gaussian height, its finite cap is strictly below
    # this raw trial.  Thus this source alone cannot fund kappa = .0039.
    assert GAUSSIAN_C < Q(".0039") + 5 * STOP
    height_cap = 2**expected.get("max_height_bits", 20)
    assert all(8192 <= h < height_cap for h in ranks)
    assert 1024 <= TERMINAL.complex_log < height_cap

    # The inherited high-fibre proof only uses H >= 8192. At its endpoint,
    # u >= 2**30; the displayed dyadic induction closes all larger u.
    assert TERMINAL.eta == Q(39, 10000) and TERMINAL.eta > Q(1, 258)
    assert TERMINAL.eta * 8192 - 1 > 30
    assert 2660000 * (30 + 2) < 2**30 and 2 * (30 + 2) >= 30 + 3
    assert 17**16 * 10**(21 * 16) < 2**1182

    stock = resource_receipt(TERMINAL)
    cuts = tuple(stock["binary_cuts"])
    assert tuple(entrance_logs(ranks)) == cuts == (8290, 46456, 650883)
    assert (stock["public_exponent_A"], stock["first_public_offset"]) == (19497093, 4)
    assert stock["absolute_log2_private_control_envelope"] == 19298236419
    assert all(cuts[i - 1] + 2 < ranks[i] for i in range(1, len(ranks)))
    assert activation(TERMINAL) == stock["public_exponent_A"]
    assert stock["retimed_first_stripe_margin"] > 1024
    assert stock["retimed_all_size_margin_floor"] > 1024
    signed = qualify(TERMINAL.kappa, STOP, paid, gaussian_upper(TERMINAL.complex_log))
    assert (signed["strict"], signed["functional"]) == (54, 4)
    assert financial_checks()["early_log2_C_bound"] == 84500000
    logB = 128 + 320 * sum(ranks)
    late = 1602 + 220 * TERMINAL.complex_log + logB
    conversion = ((TERMINAL.kappa - ENTRY.kappa) * activation(TERMINAL)).__ceil__()
    assert conversion == expected["premium"]
    assert conversion - 1 < (TERMINAL.kappa - ENTRY.kappa) * activation(TERMINAL) <= conversion
    assert 1 + max(125660241 + conversion, late) == expected["total"]
    assert expected["total"] == 4354317451 < 4354317571 < expected["total"] + 220

    old_ranks = (8192, 124649, 524288)
    assert ordinary_upper(old_ranks) <= paid and gaussian_upper(490950) <= paid
    h1, h2, h3 = ranks
    assert ordinary_upper((h1, h2 - 1, h3)) <= paid
    assert ordinary_upper((h1, h2, h3 - 1)) <= paid

    def require_funding(proposed_ranks, proposed_gaussian):
        if ordinary_upper(proposed_ranks) <= paid or gaussian_upper(proposed_gaussian) <= paid:
            raise ArithmeticError("Profile does not fund the terminal price")

    def require_budget(cap):
        if 1 + max(125660241 + conversion, late) > cap:
            raise ArithmeticError("The full recurring invoice exceeds the declared cap")

    controls = [
        rejected(lambda: require_funding((h1, h2 - 1, h3), TERMINAL.complex_log), "second-ordinary-height-minus-one"),
        rejected(lambda: require_funding((h1, h2, h3 - 1), TERMINAL.complex_log), "third-ordinary-height-minus-one"),
        rejected(lambda: require_funding(old_ranks, 490950), "old-heights-at-new-rate"),
        rejected(lambda: qualify(TERMINAL.kappa, STOP, paid, gaussian_upper(TERMINAL.complex_log - 2)), "below-minimum-gaussian-height"),
        rejected(lambda: qualify(TERMINAL.kappa, STOP, paid, gaussian_upper(TERMINAL.complex_log, PREVIOUS_GAUSSIAN)), "previous-gaussian-booking"),
        rejected(lambda: qualify(TERMINAL.kappa, STOP, paid - STOP, gaussian_upper(TERMINAL.complex_log)), "outer-ordinary-margin-removed"),
        rejected(lambda: resource_receipt(replace(TERMINAL, rank_logs=(h1, cuts[0] + 2, h3))), "prefix-height-at-previous-cut"),
        rejected(lambda: require_budget(expected["total"] - 1), "recurring-bound-minus-one"),
    ]
    assert sha256((RUNTIME / "installations.py").read_bytes()).hexdigest() == expected["image_sha"]
    assert expected["total"] > 318292011
    assert sha256((RUNTIME / "strong-bit.json.gz").read_bytes()).hexdigest() == (
        "9e7392c52bcf29c0cc58c54c619f95c28f476394c33e8e0a5aa30c9557d31362")
    old = replace(TERMINAL, rank_logs=(8192,38102,604362), complex_log=18845936, kappa=Q(".00389846"))
    old_native, new_native = prepare_native(old), prepare_native(TERMINAL)
    word = binary_word()
    assert (len(word.targets), len(word.paid), len(word.cells)) == (18906, 104652, 24)
    assert old_native[0] is new_native[0]
    assert old_native[-1].targets is new_native[-1].targets and old_native[-1].cells is new_native[-1].cells
    assert all(v.level_floor == 18960 and v.targets is word.targets and v.paid is word.paid and v.cells is word.cells
               for v in (*old_native[:-1], *new_native[:-1]))

    def round_up(n):
        return ((n + 9999) // 10000) * 10000
    direct = [verify_stage(TERMINAL, cuts, i, round_up(cuts[i - 1])) for i in (2, 3)]
    compiled = [verify_stage(TERMINAL, cuts, i, round_up(9 * ranks[i - 1])) for i in (2, 3)]
    assert all(item["direct"] for item in direct) and not any(item["direct"] for item in compiled)
    tapes = [verify_tape(1, [0, 1], [2, 1]), verify_tape(2, [1, 7], [3, 1])]
    print("PASS_25BIT_PERIOD_PROFILE", json.dumps({
        "profile": key, "kappa": str(TERMINAL.kappa), "heights": ranks,
        "gaussian_height": TERMINAL.complex_log, "binary_cuts": cuts,
        "signed": signed, "conversion_bits": conversion, "log2_B": logB,
        "complete_log2_C": expected["total"], "stock": stock,
        "prior_stopped_cap": str(old_ceiling), "controls": controls,
        "minimum_gaussian_height_for_target": TERMINAL.complex_log - 1,
        "ordinary_margin": str(ordinary_upper(ranks) - paid),
        "gaussian_margin": str(gaussian_upper(TERMINAL.complex_log) - paid),
        "direct_stage_seams": direct, "compiled_stage_seams": compiled,
        "signed_tape_controls": tapes,
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    check()
