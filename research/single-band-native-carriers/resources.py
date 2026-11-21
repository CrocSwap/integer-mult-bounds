"""Compute the complete entrance and the costs for each fully priced installation."""

from fractions import Fraction

from calibration import COMPLEX_POWER, PROFILES, SETUP_DEGREE, prices
from check_activation_space import receipt
from linear_geometry import entrance_geometry
from staged_carriers import entrance_logs


def requirements(profile):
    bit_loss, complex_loss, rates = prices(profile)
    ranks = profile.rank_logs
    cuts = entrance_logs(ranks)
    hmax = max(*ranks, profile.complex_log)
    # All per-stage programs persist. J includes each generator and its scratch.
    jlog = hmax * SETUP_DEGREE
    total_log = jlog + (len(ranks) + 1).bit_length()
    stock = receipt(
        ranks, profile.complex_log, cuts[-1], total_log, profile.power, complex_power=COMPLEX_POWER
    )
    s = stock["initial_s"]
    # Each small rank really reaches a body and a positive stopped call into its predecessor.
    for i, h in enumerate(ranks):
        assert 512 * profile.power <= h
        assert (
            h
            >= 2
            + (134**profile.power).bit_length()
            + (127**profile.power).bit_length()
            + profile.floor.bit_length()
        )
        assert not i or cuts[i - 1] < h
        assert cuts[i] >= (250 * (h + 64) + 248) // 249
    assert 512 * COMPLEX_POWER <= profile.complex_log
    assert prices(profile)[2][-1][-1] == profile.ordinary
    assert 872 * COMPLEX_POWER * (profile.complex_log + 1) ** 2 < (
        1 << min(1024, profile.complex_log)
    )
    assert s - 100 - 7 * (s - 1).bit_length() >= cuts[-1] + profile.complex_log + 2
    assert Fraction(1, 250) > profile.eta > profile.ordinary > profile.kappa
    return {
        "kappa": str(profile.kappa),
        "binary_rank_logs": ranks,
        "complex_rank_log": profile.complex_log,
        "binary_entrance_logs": cuts,
        "full_binary_debit": bit_loss,
        "full_positive_debit": complex_loss,
        "ordinary_rate": str(profile.ordinary),
        "component_exponent": str(profile.eta),
        "rate_ticks_e18": [int(rate * 10**18) for _, _, rate in rates],
        "log2_dominant_J": jlog,
        "log2_all_fixed_setup_upper": total_log,
        "log2_rank_part_of_recurring_envelope": 100 * jlog,
        **stock,
    }


def all_profiles():
    old = 355_763_540_965_264
    return {
        "previous": {
            "rank_logs": (
                60_000_000_000,
                400_000_000_000,
                2_500_000_000_000,
                16_000_000_000_000,
                100_000_000_000_000,
                236_800_000_000_000,
            ),
            "complex_rank_log": 3_300_000_000,
            "log2_dominant_J": 4_736_000_000_000_000_000,
            "connected_precision_exponent": old,
            "geometry": entrance_geometry(old, quadratic=True),
        },
        **{name: requirements(profile) for name, profile in PROFILES.items()},
    }
