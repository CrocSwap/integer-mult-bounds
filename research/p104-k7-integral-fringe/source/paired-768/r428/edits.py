"""Exact source changes to the Round 420 price and stage verifiers."""

POSITIVE = (
    ("POSITIVE_DEBIT = Q(1039701, 2**23)", "POSITIVE_DEBIT = Q(1039699, 2**23)"),
    ('''    fringe = 10 * target_axes / (t * psi)
    assert target_axes == 677246016
    assert psi > Q("926190717.2837")
    assert fringe < Q("7.340806")''',
     '''    # The literal integral suffix is at most 10*k-5 for each target slot.
    # At grade <=258 the weighted slot count is at least target_axes/258.
    target_slots = sum(targets.values())
    assert target_axes == 677246016 and target_slots >= Q(target_axes, 258)
    old_fringe = 10 * target_axes / (t * psi)
    fringe = Q(515, 516) * old_fringe
    assert (10 * target_axes - 5 * target_slots) / (t * psi) <= fringe
    assert psi > Q("926190717.2837") and old_fringe < Q("7.340806")'''),
    ('''    common_factor = (
        (1 + DELTA)
        * Q(power_interval(scale * lower, c)[1], UNIT)
        * (1 + fringe / lower + DELTA)
        / (1 - DELTA) ** 4
    )
    finite_factor = period_upper * common_factor
    assert UNIT * finite_factor < power_interval(2, POSITIVE_DEBIT)[0]
    assert power_interval(2, POSITIVE_DEBIT - Q(1, 2**23))[1] < UNIT * finite_factor
    coarse_factor = (1 + 1 / x_lower) * common_factor
    assert power_interval(2, POSITIVE_DEBIT)[1] < UNIT * coarse_factor''',
     '''    common_factor = (
        (1 + DELTA) * Q(power_interval(scale * lower, c)[1], UNIT) / (1 - DELTA) ** 4
    )
    old_factor = period_upper * common_factor * (1 + old_fringe / lower + DELTA)
    finite_factor = period_upper * common_factor * (1 + fringe / lower + DELTA)
    old_debit = Q(1039701, 2**23)
    assert power_interval(2, old_debit - Q(1, 2**23))[1] < UNIT * old_factor
    assert UNIT * old_factor < power_interval(2, old_debit)[0]
    new_lo, new_hi = power_interval(2, POSITIVE_DEBIT)
    assert UNIT * finite_factor < new_lo <= new_hi < UNIT * old_factor
    coarse_factor = (1 + 1 / x_lower) * common_factor * (1 + old_fringe / lower + DELTA)
    assert power_interval(2, old_debit)[1] < UNIT * coarse_factor'''),
)

INDEPENDENT = (
    ('''    axes = sum(k * n for k, n in recipe.targets.histogram.items())
    fringe = 10 * axes / ((1 - c) * psi)
    assert psi > Q("926190717") and fringe < Q("7.340806")''',
     '''    histogram = recipe.targets.histogram
    axes = sum(k * n for k, n in histogram.items())
    suffix_bound = sum((10*k - 5) * n for k, n in histogram.items())
    assert axes == 677246016 and suffix_bound <= Q(515, 516) * 10 * axes
    old_fringe = 10 * axes / ((1 - c) * psi)
    fringe = Q(515, 516) * old_fringe
    assert psi > Q("926190717") and old_fringe < Q("7.340806")'''),
    ('''    common_factor = (
        (1 + delta)
        * powers(scale * LOWER, c)[1]
        * (1 + fringe / LOWER + delta)
        / (1 - delta) ** 4
    )
    coarse_factor = (1 + 1 / x_lower) * common_factor
    old_allowance = powers(2, Q(1039776, 2**23))[0]
    assert old_allowance - coarse_factor > Q("0.000000019")
    assert powers(2, Q(1039775, 2**23))[0] < coarse_factor
    upper = period_upper * common_factor
    new_lo, new_hi = powers(2, Q(1039701, 2**23))
    assert powers(2, Q(1039700, 2**23))[1] < upper < new_lo < new_hi < coarse_factor
    print("PASS_SHARPER_POSITIVE_PERIOD", "257/256", "1039701/8388608")''',
     '''    common_factor = (1 + delta) * powers(scale * LOWER, c)[1] / (1 - delta) ** 4
    coarse_factor = (1 + 1 / x_lower) * common_factor * (1 + old_fringe / LOWER + delta)
    old_allowance = powers(2, Q(1039776, 2**23))[0]
    assert old_allowance - coarse_factor > Q("0.000000019")
    assert powers(2, Q(1039775, 2**23))[0] < coarse_factor
    previous = period_upper * common_factor * (1 + old_fringe / LOWER + delta)
    period_lo, period_hi = powers(2, Q(1039701, 2**23))
    assert powers(2, Q(1039700, 2**23))[1] < previous < period_lo < period_hi < coarse_factor
    proposed = period_upper * common_factor * (1 + fringe / LOWER + delta)
    new_lo, new_hi = powers(2, Q(1039699, 2**23))
    assert proposed < new_lo < new_hi < previous
    print("PASS_GAUSSIAN_INTEGER_FRINGE", "515/516", "1039699/8388608")'''),
    ('''    assert TERMINAL.kappa - Q(".003900857267786") == Q(22107, 500000000000000)''',
     '''    assert TERMINAL.kappa - Q(".003900857267786") == Q(5611, 125000000000000)
    assert TERMINAL.kappa - Q(".003900857312000") == Q(337, 500000000000000)'''),
)

RECEIPT = (
    ("DEBIT = Q(1039701, 2**23)", "DEBIT = Q(1039699, 2**23)"),
    ("== (134136243, 208653)", "== (134145234, 208653)"),
    ('''    gain = TERMINAL.kappa - older
    assert TERMINAL.kappa == Q(".003900857312000")
    assert gain == Q(22107, 500000000000000)''',
     '''    previous = Q(".003900857312000")
    gain = TERMINAL.kappa - previous
    assert TERMINAL.kappa == Q(".003900857312674")
    assert previous - older == Q(22107, 500000000000000)
    assert gain == Q(337, 500000000000000)'''),
    ('''    assert TERMINAL.kappa - frozen_tariff == Q(857, 20000000000000)
    positive_ceiling = GAUSSIAN_C - DEBIT / TERMINAL.complex_log - 5 * stop
    assert TERMINAL.kappa < positive_ceiling <= TERMINAL.kappa + Q(1, 10**15)''',
     '''    assert previous - frozen_tariff == Q(857, 20000000000000)
    previous_positive = GAUSSIAN_C - Q(1039701, 2**23) / TERMINAL.complex_log - 5 * stop
    assert previous < previous_positive <= previous + Q(1, 10**15)
    positive_ceiling = GAUSSIAN_C - DEBIT / TERMINAL.complex_log - 5 * stop
    prior_booked = Q(late["ordinary_rates"][-2])
    last_height = TERMINAL.rank_logs[-1]
    ordinary_ceiling = min(
        TERMINAL.eta, (249 * (BINARY_C - ORDINARY_DEBIT / last_height) + prior_booked) / 250
    ) - 5 * stop
    assert previous_positive < TERMINAL.kappa < ordinary_ceiling < positive_ceiling
    assert ordinary_ceiling <= TERMINAL.kappa + Q(1, 10**15)'''),
    ("        previous_rate=str(older),", "        previous_rate=str(previous),"),
)

SEAM = (
    ('''    GAUSSIAN=Q(1039701,2**23)  # sharper four-aligned period bound''',
     '''    PERIOD_GAUSSIAN=Q(1039701,2**23)
    PERIOD_KAPPA=Q(".003900857312000")
    GAUSSIAN=Q(1039699,2**23)  # book a conservative two-tick integral fringe reduction'''),
    ('assert TERMINAL.kappa==Q(".003900857312000")', 'assert TERMINAL.kappa==Q(".003900857312674")'),
    ("assert ordinary_upper(ranks)>gaussian_upper(TERMINAL.complex_log)>paid",
     "assert gaussian_upper(TERMINAL.complex_log)>ordinary_upper(ranks)>paid"),
    ('''    assert TERMINAL.kappa+GRID>=gaussian_upper(TERMINAL.complex_log)-5*STOP''',
     '''    period_crossing=gaussian_upper(TERMINAL.complex_log,PERIOD_GAUSSIAN)-5*STOP
    assert PERIOD_KAPPA<period_crossing<=PERIOD_KAPPA+GRID
    assert period_crossing<TERMINAL.kappa
    assert TERMINAL.kappa+GRID>=ordinary_upper(ranks)-5*STOP'''),
    ('''        rejected(lambda:require_funding(ranks,TERMINAL.complex_log,kappa=TERMINAL.kappa+GRID),
                 "next-displayed-kappa-at-fixed-gaussian-height"),''',
     '''        rejected(lambda:require_funding(ranks,TERMINAL.complex_log,gaussian_debit=PERIOD_GAUSSIAN),
                 "period-only-gaussian-debit-at-new-rate"),
        rejected(lambda:require_funding(ranks,TERMINAL.complex_log,kappa=TERMINAL.kappa+GRID),
                 "next-displayed-kappa-at-fixed-five-stage-profile"),'''),
)

EDITS = {
    "positive_debit.py": POSITIVE,
    "independent_price.py": INDEPENDENT,
    "receipt.py": RECEIPT,
    "check_stage_seam.py": SEAM,
}
