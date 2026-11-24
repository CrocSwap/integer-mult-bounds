"""Exact changes for the narrower quotient domain and directly bounded debit."""

RECEIPT = (
    ("ORDINARY_DEBIT = Q(1414569, 2**20)", "ORDINARY_DEBIT = Q(1411929, 2**20)"),
    ("CHILD_TARIFF = Q(10981863, 4703998)", "CHILD_TARIFF = Q(15009853977, 6430103800)"),
    ("def tape_factor_periodic(ambient, rate, lower, paid, cells):\n    delta",
     "def tape_factor_periodic(ambient, rate, lower, paid, cells, *, upper=True):\n    hi, lo = (1, 0) if upper else (0, 1)\n    delta"),
    ("Q(intervals(k, rate)[0], intervals(r, rate)[1])", "Q(intervals(k, rate)[lo], intervals(r, rate)[hi])"),
    ("Q(intervals(r, t)[1], intervals(k, t)[0])", "Q(intervals(r, t)[hi], intervals(k, t)[lo])"),
    ("Q(power_interval(lower * r, t)[0], power_interval(lower * k + 4 * r, t)[1])",
     "Q(power_interval(lower * r, t)[lo], power_interval(lower * k + 4 * r, t)[hi])"),
    ("Q(power_interval(scale * lower, rate)[1], UNIT)", "Q(power_interval(scale * lower, rate)[hi], UNIT)"),
    ('''    contraction = exact_mean / CHILD_TARIFF''',
     '''    peer_tariff = Q(10981863, 4703998)
    peer_debit = Q(1414569, 2**20)
    assert exact_mean / peer_tariff == Q(2390, 2391)
    x16 = 3**14
    mean16 = Q(21*x16 + 3, 9*x16 - 1)
    assert 1 < mean16 == Q(6277647, 2690420) < exact_mean
    contraction = mean16 / CHILD_TARIFF'''),
    ('''    ratio = CHILD_TARIFF / old_tariff
    assert ratio == Q(5622713856, 5647149599)
    new_lo, new_hi = (2*Q(p, UNIT) for p in power_interval(2, ORDINARY_DEBIT - 1))
    # Keep the directed full old proof, including the entire 256/255 reserve.
    assert full_factor * CHILD_TARIFF < old_upper * ratio < new_lo <= new_hi < old_upper''',
     '''    ratio = peer_tariff / old_tariff
    assert ratio == Q(5622713856, 5647149599)
    peer_lo, peer_hi = (2*Q(p, UNIT) for p in power_interval(2, peer_debit - 1))
    assert full_factor*peer_tariff < old_upper*ratio < peer_lo <= peer_hi < old_upper
    assert CHILD_TARIFF / peer_tariff == Q(20592774709, 20595165100)
    factor_lower = tape_factor_periodic(134, BINARY_C, ORDINARY_FLOOR, paid, bit_cells, upper=False)
    assert 0 < factor_lower <= full_factor
    for tariff, tick in ((peer_tariff, 1412105), (CHILD_TARIFF, 1411929)):
        allowance = 2*Q(power_interval(2, Q(tick, 2**20) - 1)[0], UNIT)
        rejected = 2*Q(power_interval(2, Q(tick - 1, 2**20) - 1)[1], UNIT)
        assert rejected < factor_lower*tariff <= full_factor*tariff < allowance'''),
    ("== (268290493, 52270)", "== (268290534, 52270)"),
    ('''    previous = Q(".003900862325217")
    gain = TERMINAL.kappa - previous
    assert TERMINAL.kappa == Q(".003900862339776")
    assert previous - older == Q(5057431, 10**15)
    assert gain == Q(14559, 10**15)''',
     '''    peer8097 = Q(".003900862325217")
    previous = Q(".003900862339776")
    repriced = Q(".003900862348535")
    gain = TERMINAL.kappa - previous
    assert TERMINAL.kappa == Q(".003900862349161")
    assert peer8097 - older == Q(5057431, 10**15)
    assert previous - peer8097 == Q(14559, 10**15)
    assert gain == Q(9385, 10**15) and TERMINAL.kappa - repriced == Q(626, 10**15)'''),
    ('''    assert previous < old_ceiling <= previous + Q(1, 10**15)
    assert old_ceiling < TERMINAL.kappa < new_ceiling < gaussian_ceiling
    assert new_ceiling <= TERMINAL.kappa + Q(1, 10**15)''',
     '''    grid = Q(1, 10**15)
    actual_previous = guarded_ordinary(peer_debit)
    tight_previous = guarded_ordinary(Q(1412105, 2**20))
    assert peer8097 < old_ceiling <= peer8097 + grid
    assert previous < actual_previous <= previous + grid
    assert repriced < tight_previous <= repriced + grid
    assert old_ceiling < actual_previous < tight_previous < TERMINAL.kappa < new_ceiling < gaussian_ceiling
    assert new_ceiling <= TERMINAL.kappa + grid'''),
    ("        previous_rate=str(previous),", "        previous_rate=str(previous),\n        previous_repriced_rate=str(repriced),\n        previous_8097_rate=str(peer8097),"),
)

INDEPENDENT = (
    ('''    print("PASS_EXACT_TARIFF_TRANSFER", str(tariff), "ord=1414569/2^20", "reserve=256/255", "clock_budget=2401", flush=True)''',
     '''    print("PASS_EXACT_TARIFF_TRANSFER", str(tariff), "ord=1414569/2^20", "reserve=256/255", "clock_budget=2401", flush=True)

    psi_hi = sum(bp[r] * sh * r * (powers(Q(k, r), c)[1] - 1) / c for (r, k), sh in cells.items())
    num_lo = sum(
        bp[r] * sh * ((9*k - 8*r)*powers(Q(r, k), t)[0] - r*powers(Q(lower*r, lower*k + 4*r), t)[1] + r*delta)
        for (r, k), sh in cells.items()
    )
    assert 0 < num_lo <= num and 0 < psi <= psi_hi
    fringe_lo = num_lo/(t*psi_hi)
    factor_lo = (lo/child_tariff)*(1 + fringe_lo/lower + delta)/(1 + fringe/lower + delta)
    factor_hi = hi/child_tariff
    x16 = 3**14
    mean16 = Q(21*x16 + 3, 9*x16 - 1)
    tighter = mean16/contraction
    assert mean16 == Q(6277647, 2690420) and tighter == Q(15009853977, 6430103800)
    for candidate, tick in ((tariff, 1412105), (tighter, 1411929)):
        accepted = 2*powers(2, Q(tick, 2**20) - 1)[0]
        rejected = 2*powers(2, Q(tick - 1, 2**20) - 1)[1]
        assert rejected < factor_lo*candidate <= factor_hi*candidate < accepted
    print("PASS_MINIMAL_TARIFF_DEBITS", "1412105", "1411929", "2^20", flush=True)'''),
    ('''    assert TERMINAL.kappa - peer_8097 == Q(14559, 10**15)''',
     '''    peer_8098 = Q(".003900862339776")
    assert peer_8098 - peer_8097 == Q(14559, 10**15)
    assert TERMINAL.kappa - peer_8098 == Q(9385, 10**15)
    assert TERMINAL.kappa - Q(".003900862348535") == Q(626, 10**15)'''),
)

SEAM = (
    ('''    ORDINARY = Q(1414569, 2**20)  # exact tariff, same L=1156 and full 256/255 reserve''',
     '''    PEER8098_ORDINARY = Q(1414569, 2**20)
    PEER8098_TIGHT = Q(1412105, 2**20)
    PEER8098_KAPPA = Q(".003900862339776")
    PEER8098_REPRICED = Q(".003900862348535")
    ORDINARY = Q(1411929, 2**20)  # N>=16, same L=1156 and full 256/255 reserve'''),
    ('assert TERMINAL.kappa == Q(".003900862339776")','assert TERMINAL.kappa == Q(".003900862349161")'),
    ('''    assert old_upper < paid < ordinary_upper(ranks) < gaussian_upper(TERMINAL.complex_log)''',
     '''    peer8098 = ordinary_upper(ranks, debit=PEER8098_ORDINARY)
    peer8098_tight = ordinary_upper(ranks, debit=PEER8098_TIGHT)
    assert PEER8098_KAPPA < peer8098 - 5*STOP <= PEER8098_KAPPA + Q(1, 10**15)
    assert PEER8098_REPRICED < peer8098_tight - 5*STOP <= PEER8098_REPRICED + Q(1, 10**15)
    assert old_upper < peer8098 < peer8098_tight < paid < ordinary_upper(ranks) < gaussian_upper(TERMINAL.complex_log)'''),
    ('''        rejected(lambda: require_funding(ranks, TERMINAL.complex_log, kappa=TERMINAL.kappa + Q(1, 10**15)),''',
     '''        rejected(lambda: require_funding(ranks, TERMINAL.complex_log, debit=PEER8098_ORDINARY),
                 "peer8098-booked-debit-at-new-rate"),
        rejected(lambda: require_funding(ranks, TERMINAL.complex_log, debit=PEER8098_TIGHT),
                 "peer8098-tight-debit-at-new-rate"),
        rejected(lambda: require_funding(ranks, TERMINAL.complex_log, kappa=TERMINAL.kappa + Q(1, 10**15)),'''),
)

EDITS = {"receipt.py": RECEIPT, "independent_price.py": INDEPENDENT, "check_stage_seam.py": SEAM}
