"""Choose six funded binary ranks and balance the chart width against tape motion."""

from fractions import Fraction


RANK_LOGS = (
    60_000_000_000,
    400_000_000_000,
    2_500_000_000_000,
    16_000_000_000_000,
    100_000_000_000_000,
    236_800_000_000_000,
)
SOURCE = Fraction(3_879_928_046_148, 10**15)
ORDINARY = Fraction(3_879_928_035_646, 10**15)
KAPPA = Fraction(387_992_803_556, 10**14)
ETA = Fraction(97, 25_000)
COMPLEX_LOG = 3_300_000_000


def ceiling_ratio(numerator, denominator):
    return (numerator + denominator - 1) // denominator


def quotient_entry_log(rank_log):
    """Return a sufficient width logarithm for all quotient rows and high lifts."""
    return ceiling_ratio((2 * rank_log + 64) * 25_000, 24_903)


def entrance_logs(rank_logs=RANK_LOGS):
    """Return the entry widths that admit a genuine native body at each stage."""
    cuts = []
    for rank_log in rank_logs:
        minimum = ceiling_ratio(250 * (rank_log + 64), 249)
        floor = rank_log + cuts[-1] + 64 if cuts else 0
        cuts.append(max(minimum, floor))
    return tuple(cuts)


def admitted_stage(digits, maximum=6, rank_logs=RANK_LOGS):
    if digits < 1 or not 0 <= maximum <= len(rank_logs):
        raise ValueError("Use a positive trit width and a supported stage")
    available = digits.bit_length() - 1
    cuts = entrance_logs(rank_logs)
    return next(
        (i for i in range(maximum, 0, -1) if available >= cuts[i - 1]),
        0,
    )


def stage_layout(digits, predecessor_width, ceil_root):
    """Return the two balanced component sizes and their multiplicities.

    The predecessor width is its complete entry value, or zero at the cold stage.
    ceil_root is the exact integer ceiling function used by the native package.
    """
    if digits < 1 or predecessor_width < 0:
        raise ValueError("Use a positive field and a nonnegative previous width")
    width = max(predecessor_width + 1, ceil_root(digits, 250))
    target = ceil_root(digits**97, 25_000)
    count = ceiling_ratio(width, target)
    short, longer = divmod(width, count)
    return longer, short + 1, count - longer, short


def prices(rank_logs=RANK_LOGS):
    """Bound the native paid moment by comparing exact integers and rationals."""
    previous = Fraction(0)
    out = []
    grid = 10**18
    for index, height in enumerate(rank_logs):
        # 32 (1+H/8192)^71 < 2^debit. A positive static gap funds every rank.
        top = 32 * (8192 + height) ** 71
        debit = (top - 1).bit_length() - 13 * 71
        assert top < 1 << (debit + 13 * 71)
        covered = SOURCE - Fraction(debit, height)
        bound = (249 * covered + previous) / 250
        at_grid = (bound * grid).__floor__() - 1
        rate = ORDINARY if index == len(rank_logs) - 1 else Fraction(at_grid, grid)
        assert previous < rate < min(bound, ETA)
        out.append((height, debit, covered, rate))
        previous = rate
    return tuple(out)


def strong_precision_log(rank_logs=RANK_LOGS):
    return entrance_logs(rank_logs)[-1] + COMPLEX_LOG + 1_024


def receipt():
    cuts = entrance_logs()
    s = strong_precision_log() + 1
    for i, (h, cut) in enumerate(zip(RANK_LOGS, cuts)):
        qcut = quotient_entry_log(h)
        assert (1 - ETA) * qcut >= 2 * h + 64 and qcut < 3 * h < 8 * h
        assert 249 * cut >= 250 * (h + 64)
        if i:
            assert cuts[i - 1] + 2 < h
            assert cut >= h + cuts[i - 1] + 64
        # Throughout the first complete connected product, every selected
        # width e is below 2^top. The next stage can only send max(E_i+1,
        # ceil(e_parent^(1/250))) down to this stage.
        top = cuts[i + 1] if i + 1 < len(cuts) else s
        if i + 1 < len(cuts):
            parent_top = cuts[i + 2] if i + 2 < len(cuts) else s
            assert parent_top + 250 < 250 * top and cuts[i] + 1 < top
        floor_log = cuts[i - 1] if i else 0
        assert top - floor_log <= 8 * h
    log_s = (s - 1).bit_length()
    assert s - 100 - 16 * (log_s + 1) - COMPLEX_LOG - 2 >= cuts[-1]
    old_h = 240_000_000_000_000
    ledger_floor = 234_000_000_000_000
    assert 32 * (8192 + ledger_floor) ** 71 > 1 << (923 + 2471)
    assert Fraction(249 * 2471, 250 * ledger_floor) > SOURCE - ORDINARY
    old_six_log = 2_881_869_654_258_596
    direct_binary_row_log = 1050 * sum(RANK_LOGS) + 448 * (3 * COMPLEX_LOG + s + 1)
    assert direct_binary_row_log < 2**59
    return {
        "ordinary_rate": str(ORDINARY),
        "complete_kappa": str(KAPPA),
        "stage_price_debits": [row[1] for row in prices()],
        "rank_log2": list(RANK_LOGS),
        "last_rank_log2_strict_lower_for_same_envelope_and_ordinary_price": ledger_floor,
        "stage_rates_in_units_of_1e_minus_18": [int(row[3] * 10**18) for row in prices()],
        "log2_trit_entries": list(cuts),
        "log2_public_precision_sufficient_connected": strong_precision_log(),
        "old_log2_public_precision_sufficient_connected": 16 * old_h,
        "old_necessary_public_log_floor_for_its_sixth_explicit_gate": old_six_log - 1,
        "first_connected_log2_simultaneous_rows_upper": direct_binary_row_log,
        "first_connected_log2_log3_simultaneous_rows_strict_upper": 59,
        "old_single_low_log2_log3_lower_floor": 2 * old_h - 1,
        "old_one_low_vs_all_new_log3_count_log2_ratio_lower_floor": 2 * old_h - 60,
        "fixed_native_log2_J_old": 20_000 * old_h,
        "fixed_native_log2_J_new": 20_000 * RANK_LOGS[-1],
    }


if __name__ == "__main__":
    import json

    print(json.dumps(receipt(), indent=2))
