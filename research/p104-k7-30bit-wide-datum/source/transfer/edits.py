"""Exact tariff-transfer changes to the materialized #8097 verifiers."""

RECEIPT = (
    ("ORDINARY_DEBIT = Q(1418665, 2**20)", "ORDINARY_DEBIT = Q(1414569, 2**20)"),
    ("CHILD_TARIFF = Q(2401, 1024)", "CHILD_TARIFF = Q(10981863, 4703998)\nRECURSIVE_CLOCK_BUDGET = 2401"),
    ('''    ordinary_upper = Q("2.5543284")
    assert tape_factor_periodic(134, BINARY_C, ORDINARY_FLOOR, paid, bit_cells) * CHILD_TARIFF < ordinary_upper
    assert ordinary_upper**1048576 < 2**1418665
    assert Q(75, 32) / CHILD_TARIFF == Q(2400, 2401)''',
     '''    full_factor = tape_factor_periodic(134, BINARY_C, ORDINARY_FLOOR, paid, bit_cells)
    old_tariff = Q(2401, 1024)
    old_upper = Q("2.5543284")
    assert full_factor * old_tariff < old_upper
    assert old_upper**1048576 < 2**1418665
    assert Q(75, 32) / old_tariff == Q(2400, 2401)

    x = 3**7  # The conserved quotient mean decreases with N, and N>=9.
    exact_mean = Q(21*x + 3, 9*x - 1)
    assert exact_mean == Q(22965, 9841) < Q(2390, 1024)
    assert all(height >= 4 for profile in (ENTRY, TERMINAL) for height in profile.rank_logs)
    contraction = exact_mean / CHILD_TARIFF
    geometric_sum = 1 / (1 - contraction)
    assert contraction == Q(2390, 2391) and geometric_sum == 2391 < RECURSIVE_CLOCK_BUDGET
    assert RECURSIVE_CLOCK_BUDGET < 8*376 and (Q(7, 10)*RECURSIVE_CLOCK_BUDGET)**2 < 2**22
    ratio = CHILD_TARIFF / old_tariff
    assert ratio == Q(5622713856, 5647149599)
    new_lo, new_hi = (2*Q(p, UNIT) for p in power_interval(2, ORDINARY_DEBIT - 1))
    # Keep the directed full old proof, including the entire 256/255 reserve.
    assert full_factor * CHILD_TARIFF < old_upper * ratio < new_lo <= new_hi < old_upper'''),
    ("== (268290534, 52270)", "== (268290493, 52270)"),
    ('''    gain = TERMINAL.kappa - older
    assert gain == Q(5057431, 10**15)''',
     '''    previous = Q(".003900862325217")
    gain = TERMINAL.kappa - previous
    assert TERMINAL.kappa == Q(".003900862339776")
    assert previous - older == Q(5057431, 10**15)
    assert gain == Q(14559, 10**15)

    stop = Q(1, TERMINAL.positive_stop_denominator)

    def guarded_ordinary(debit):
        booked = Q(0)
        for height in TERMINAL.rank_logs:
            upper = min(TERMINAL.eta, (249 * (BINARY_C - debit / height) + booked) / 250)
            booked = Q(int(upper * 10**21) - 1, 10**21)
        return upper - 5*stop

    old_ceiling = guarded_ordinary(Q(1418665, 2**20))
    new_ceiling = guarded_ordinary(ORDINARY_DEBIT)
    gaussian_ceiling = GAUSSIAN_C - DEBIT / TERMINAL.complex_log - 5*stop
    assert previous < old_ceiling <= previous + Q(1, 10**15)
    assert old_ceiling < TERMINAL.kappa < new_ceiling < gaussian_ceiling
    assert new_ceiling <= TERMINAL.kappa + Q(1, 10**15)'''),
    ('''    assert grade_actions < 2**32 and setup["all_setup"] < 2**228''',
     '''    # Recompute both enlarged lookup and serial action count for all ten recipes.
    actions = 2**68 + 2**40
    lookup = 8*(4*setup["max_datum_bits"]*actions)*512*128
    expanded_setup = (actions + 1)*(lookup + setup["local_arithmetic"] + 2**120)*2**32
    assert grade_actions < 2**32 and setup["all_setup"] < expanded_setup < 2**228'''),
    ("        previous_rate=str(older),", "        previous_rate=str(previous),\n        previous_8094_rate=str(older),"),
    ('''        ordinary_child_contraction="2400/2401",
        ordinary_child_geometric_sum=2401,''',
     '''        ordinary_child_contraction=str(contraction),
        ordinary_child_geometric_sum=int(geometric_sum),
        ordinary_child_geometric_budget=RECURSIVE_CLOCK_BUDGET,'''),
    ('''        native_setup_transition_upper=setup["all_setup"],''',
     '''        native_setup_transition_upper=expanded_setup,'''),
)

INDEPENDENT = (
    ('''    print("PASS_INDEPENDENT_PERIODIC_DEBITS", "ord=1418665/2^20", "pos=32401/262144", "2400/2401", "reserve=256/255", flush=True)''',
     '''    print("PASS_INDEPENDENT_PERIODIC_DEBITS", "ord=1418665/2^20", "pos=32401/262144", "2400/2401", "reserve=256/255", flush=True)

    x = 3**7
    child_mean = Q(21*x + 3, 9*x - 1)
    contraction = Q(2390, 2391)
    tariff = child_mean / contraction
    ratio = tariff / child_tariff
    assert child_mean == Q(22965, 9841) and tariff == Q(10981863, 4703998)
    assert ratio == Q(5622713856, 5647149599)
    assert 1 / (1 - contraction) == 2391 < 2401
    # Change only the tariff in the complete existing 192-bit conservative invoice.
    new_lo, new_hi = (2 * p for p in powers(2, Q(1414569, 2**20) - 1))
    assert hi * ratio < new_lo <= new_hi < lo
    print("PASS_EXACT_TARIFF_TRANSFER", str(tariff), "ord=1414569/2^20", "reserve=256/255", "clock_budget=2401", flush=True)'''),
    ('''    assert TERMINAL.kappa - peer_8094 == Q(5057431, 10**15)
    assert TERMINAL.kappa - peer_8073 == Q(2642571711, 10**15)''',
     '''    peer_8097 = Q(".003900862325217")
    assert peer_8097 - peer_8094 == Q(5057431, 10**15)
    assert peer_8097 - peer_8073 == Q(2642571711, 10**15)
    assert TERMINAL.kappa - peer_8097 == Q(14559, 10**15)'''),
)

SEAM = (
    ('''    ORDINARY = Q(1418665, 2**20)  # periodic-integral suffix at L=1156, 2401/1024 tariff, FULL 256/255 reserve''',
     '''    PEER_ORDINARY = Q(1418665, 2**20)
    PEER_KAPPA = Q(".003900862325217")
    ORDINARY = Q(1414569, 2**20)  # exact tariff, same L=1156 and full 256/255 reserve'''),
    ('assert TERMINAL.kappa == Q(".003900862325217")', 'assert TERMINAL.kappa == Q(".003900862339776")'),
    ('''    assert ordinary_upper(ranks) > paid and gaussian_upper(TERMINAL.complex_log) > paid
    assert TERMINAL.kappa <= ordinary_upper(ranks) - 5 * STOP < TERMINAL.kappa + Q(1, 10**15)''',
     '''    old_upper = ordinary_upper(ranks, debit=PEER_ORDINARY)
    assert PEER_KAPPA < old_upper - 5*STOP <= PEER_KAPPA + Q(1, 10**15)
    assert old_upper < paid < ordinary_upper(ranks) < gaussian_upper(TERMINAL.complex_log)
    assert TERMINAL.kappa < ordinary_upper(ranks) - 5*STOP <= TERMINAL.kappa + Q(1, 10**15)'''),
    ('''    def require_funding(proposed, gaussian, eta=TERMINAL.eta):
        if ordinary_upper(proposed, eta=eta) <= paid or gaussian_upper(gaussian) <= paid:
            raise ArithmeticError("Profile does not fund the terminal price")''',
     '''    def require_funding(proposed, gaussian, eta=TERMINAL.eta, *, debit=ORDINARY, kappa=TERMINAL.kappa):
        threshold = kappa + 5*STOP
        if ordinary_upper(proposed, debit=debit, eta=eta) <= threshold or gaussian_upper(gaussian) <= threshold:
            raise ArithmeticError("Profile does not fund the terminal price")

    def require_peer_funding(proposed, gaussian):
        require_funding(proposed, gaussian, debit=PEER_ORDINARY, kappa=PEER_KAPPA)'''),
    ('''        require_funding(at(i, -(d - 1)), TERMINAL.complex_log)''',
     '''        require_peer_funding(at(i, -(d - 1)), TERMINAL.complex_log)'''),
    ('''        rejected(lambda i=i, d=d: require_funding(at(i, -d), TERMINAL.complex_log), f"ordinary-height-{i}-minus-{d}")''',
     '''        rejected(lambda i=i, d=d: require_peer_funding(at(i, -d), TERMINAL.complex_log),
                 f"peer8097-ordinary-height-{i}-minus-{d}")'''),
    ('''        rejected(lambda: require_funding(ranks, TERMINAL.complex_log - 1), "gaussian-height-minus-one"),''',
     '''        rejected(lambda: require_funding(ranks, TERMINAL.complex_log - 1), "gaussian-height-minus-one"),
        rejected(lambda: require_funding(ranks, TERMINAL.complex_log, debit=PEER_ORDINARY),
                 "peer8097-ordinary-debit-at-new-rate"),
        rejected(lambda: require_funding(ranks, TERMINAL.complex_log, kappa=TERMINAL.kappa + Q(1, 10**15)),
                 "next-displayed-kappa-at-fixed-six-stage-profile"),'''),
    ('''                neighbours.append(ordinary_upper((*t, max_penultimate(t), TOP)))
    assert all(n <= ordinary_upper(ranks) for n in neighbours)''',
     '''                neighbours.append(ordinary_upper((*t, max_penultimate(t), TOP), debit=PEER_ORDINARY))
    assert all(n <= ordinary_upper(ranks, debit=PEER_ORDINARY) for n in neighbours)'''),
    ('''    # Verify all five comparator control tiers under our exact debits (retaining FULL 256/255):''',
     '''    # Preserve all five comparator controls at the original #8097 debits.'''),
    ('''        u = ordinary_upper(c_ranks, eta=c_eta)''',
     '''        u = ordinary_upper(c_ranks, debit=PEER_ORDINARY, eta=c_eta)'''),
    ('''            assert ordinary_upper(c_ranks[:-1] + (c_ranks[-1] - 1,), eta=c_eta) <= c_paid''',
     '''            assert ordinary_upper(c_ranks[:-1] + (c_ranks[-1] - 1,), debit=PEER_ORDINARY, eta=c_eta) <= c_paid'''),
)

EDITS = {
    "receipt.py": RECEIPT,
    "independent_price.py": INDEPENDENT,
    "check_stage_seam.py": SEAM,
}
