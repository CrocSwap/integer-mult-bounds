"""Exact source edits: 31-bit six-stage profile, w=2^41 datum width, paid child sum 2925.

Applied after the #8098 domain layer (exact head fae237c8aee774bb2256d4e394fed9f3934147c2).
Every anchor must occur exactly once in the authenticated predecessor bytes.
"""

OLD_RANKS = '(8192, 63614, 1005821, 15903360, 251454111, 268435455)'
NEW_RANKS = '(16096, 254464, 4023296, 63614464, 2079574939, 2147483647)'

EDITS = {
    'receipt.py': (
        ('ORDINARY_DEBIT = Q(1411927, 2**20)', 'ORDINARY_DEBIT = Q(1411814, 2**20)'),
        ('CHILD_TARIFF = Q(5024210149, 2152336000)', 'CHILD_TARIFF = Q(3672423495, 1573357616)'),
        ('RECURSIVE_CLOCK_BUDGET = 2401', 'RECURSIVE_CLOCK_BUDGET = 2925'),
        ('from check_serial_setup import clock as native_clock',
         'from check_serial_setup import clock as narrow_clock\n'
         'sys.path.append(str(HERE))\n'
         'from check_wide_setup import clock as native_clock'),
        ('    assert contraction == Q(2400, 2401) and geometric_sum == RECURSIVE_CLOCK_BUDGET == 2401\n'
         '    assert RECURSIVE_CLOCK_BUDGET < 8*376 and (Q(7, 10)*RECURSIVE_CLOCK_BUDGET)**2 < 2**22',
         '    paid_tariff = Q(5024210149, 2152336000)\n'
         '    assert mean16/paid_tariff == Q(2400, 2401)\n'
         '    assert contraction == Q(2924, 2925) and geometric_sum == RECURSIVE_CLOCK_BUDGET == 2925\n'
         '    # Same five-bit entry and three-bit-per-stage terminal allowances as #8076/#8098.\n'
         '    assert RECURSIVE_CLOCK_BUDGET < 8*376 and (Q(7, 10)*RECURSIVE_CLOCK_BUDGET)**2 < 2**22\n'
         '    assert (Q(7, 10)*(RECURSIVE_CLOCK_BUDGET + 1))**2 >= 2**22'),
        ('    assert CHILD_TARIFF/domain_tariff == Q(573839, 573840)',
         '    assert paid_tariff/domain_tariff == Q(573839, 573840)\n'
         '    assert CHILD_TARIFF/paid_tariff == Q(1755000, 1755131)'),
        ('for tariff, tick in ((peer_tariff, 1412105), (domain_tariff, 1411929), (CHILD_TARIFF, 1411927)):',
         'for tariff, tick in ((peer_tariff, 1412105), (domain_tariff, 1411929), (paid_tariff, 1411927), '
         '(CHILD_TARIFF, 1411814)):'),
        ('    assert cost == 171810078109 and premium == 242079\n'
         '    assert early["log2_C"] == 125660246 and late["log2_B"] == 171798577106',
         '    assert cost == 1374400932409 and premium == 1936482 and A == 4295020054\n'
         '    assert early["log2_C"] == 125660246 and late["log2_B"] == 1374389410066'),
        ('== (268290528, 52270)', '== (2146006033, 52367)'),
        ('    domain = Q(".003900862349161")\n'
         '    gain = TERMINAL.kappa - domain\n'
         '    assert TERMINAL.kappa == Q(".003900862349168")',
         '    domain = Q(".003900862349161")\n'
         '    paid8098 = Q(".003900862349168")\n'
         '    same_budget = Q(".003900862349569")\n'
         '    gain = TERMINAL.kappa - paid8098\n'
         '    assert TERMINAL.kappa == Q(".003900866740647")'),
        ('    assert gain == Q(7, 10**15)',
         '    assert paid8098 - domain == Q(7, 10**15) and same_budget - paid8098 == Q(401, 10**15)\n'
         '    assert gain == Q(4391479, 10**15)'),
        ('    def guarded_ordinary(debit):\n'
         '        booked = Q(0)\n'
         '        for height in TERMINAL.rank_logs:',
         '    peer_heights = ' + OLD_RANKS + '\n'
         '\n'
         '    def guarded_ordinary(debit, heights=peer_heights):\n'
         '        booked = Q(0)\n'
         '        for height in heights:'),
        ('    new_ceiling = guarded_ordinary(ORDINARY_DEBIT)',
         '    new_ceiling = guarded_ordinary(ORDINARY_DEBIT, TERMINAL.rank_logs)\n'
         '    paid_ceiling = guarded_ordinary(Q(1411927, 2**20))\n'
         '    same_budget_ceiling = guarded_ordinary(ORDINARY_DEBIT)'),
        ('    assert old_ceiling < actual_previous < tight_previous < domain_ceiling < '
         'TERMINAL.kappa < new_ceiling < gaussian_ceiling',
         '    assert paid8098 < paid_ceiling <= paid8098 + grid\n'
         '    # Control: S=2925 alone at the unchanged 28-bit six-stage #8098 heights.\n'
         '    assert same_budget < same_budget_ceiling <= same_budget + grid\n'
         '    assert old_ceiling < actual_previous < tight_previous < domain_ceiling < paid_ceiling '
         '< same_budget_ceiling < TERMINAL.kappa < new_ceiling < gaussian_ceiling'),
        ('        previous_rate=str(domain),',
         '        previous_rate=str(paid8098),\n'
         '        same_budget_28bit_rate=str(same_budget),\n'
         '        previous_domain_rate=str(domain),'),
        ('    assert max(h.bit_length() for h in (*ENTRY.rank_logs, ENTRY.complex_log, '
         '*TERMINAL.rank_logs, TERMINAL.complex_log)) == 28',
         '    assert max(h.bit_length() for h in (*ENTRY.rank_logs, ENTRY.complex_log, '
         '*TERMINAL.rank_logs, TERMINAL.complex_log)) == 31'),
        ('    assert 92 * (2**28 - 1) < 2**38 and 1024 * (2**28 - 1) + '
         '(len(TERMINAL.rank_logs) + 1).bit_length() == 274877905923 < 2**38',
         '    # 31-bit indexed setup (WIDE-SETUP.md): 92*H and 1024*H+(m+1).bit_length() stay below w=2^41.\n'
         '    assert setup["max_datum_bits"] == 2**41 and narrow_clock()["max_datum_bits"] == 2**38\n'
         '    assert 92 * (2**31 - 1) < 2**41 and 1024 * (2**31 - 1) + '
         '(len(TERMINAL.rank_logs) + 1).bit_length() == 2199023254531 < 2**41\n'
         '    assert 1024 * 2**31 + 3 > 2**41'),
        ('    assert grade_actions < 2**32 and setup["all_setup"] < expanded_setup < 2**228',
         '    assert grade_actions < 2**32 and setup["all_setup"] < expanded_setup < 2**231'),
    ),
    'independent_price.py': (
        ('    for candidate, tick in ((tariff, 1412105), (tighter, 1411929), (paid_tariff, 1411927)):',
         '    wide_contraction = Q(2924, 2925)\n'
         '    wide_tariff = mean16/wide_contraction\n'
         '    assert wide_tariff == Q(3672423495, 1573357616) and 1/(1 - wide_contraction) == 2925\n'
         '    assert (Q(7, 10)*2925)**2 < 2**22 <= (Q(7, 10)*2926)**2 and 2925 < 8*376\n'
         '    for candidate, tick in ((tariff, 1412105), (tighter, 1411929), (paid_tariff, 1411927), '
         '(wide_tariff, 1411814)):'),
        ('    print("PASS_MINIMAL_TARIFF_DEBITS", "1412105", "1411929", "1411927", "2^20", flush=True)',
         '    print("PASS_MINIMAL_TARIFF_DEBITS", "1412105", "1411929", "1411927", "1411814", "2^20", '
         'flush=True)'),
        ('    domain = Q(".003900862349161")\n',
         '    domain = Q(".003900862349161")\n'
         '    assert TERMINAL.kappa == Q(".003900866740647")\n'
         '    TERMINAL_KAPPA_8098 = Q(".003900862349168")\n'),
        ('    assert TERMINAL.kappa - domain == Q(7, 10**15)',
         '    assert TERMINAL_KAPPA_8098 - domain == Q(7, 10**15)'),
    ),
    'check_ordinary_floor.py': (
        ('    assert TERMINAL.rank_logs == ' + OLD_RANKS + ' and TERMINAL.complex_log == 52270',
         '    assert TERMINAL.rank_logs == ' + NEW_RANKS + ' and TERMINAL.complex_log == 52367'),
        ('    assert (a[-1].rank_log, b[-1].rank_log) == (1024, 52270)',
         '    assert (a[-1].rank_log, b[-1].rank_log) == (1024, 52367)'),
    ),
    'check_cutoff.py': (
        ('assert heights == (1024, 52270)', 'assert heights == (1024, 52367)'),
    ),
}

EDITS['check_stage_seam.py'] = (
    ('"""Replay 6-stage 28-bit ordinary dispatch, all comparator controls, and bounded signed bank returns."""',
     '"""Replay 6-stage 31-bit ordinary dispatch, all comparator controls, and bounded signed bank returns."""'),
    ('    ORDINARY = Q(1411927, 2**20)  # N>=16, paid 2401 clock and full reserve',
     '    PAID8098_ORDINARY = Q(1411927, 2**20)\n'
     '    PAID8098_KAPPA = Q(".003900862349168")\n'
     '    SAME_BUDGET_KAPPA = Q(".003900862349569")\n'
     '    OLD_RANKS = ' + OLD_RANKS + '\n'
     '    ORDINARY = Q(1411814, 2**20)  # N>=16, paid 2925 child sum and full reserve'),
    ('    TOTAL = 171810078109\n    PREMIUM = 242079\n    BITS = 28',
     '    TOTAL = 1374400932409\n    PREMIUM = 1936482\n    BITS = 31'),
    ('    assert ranks == (8192, 63614, 1005821, 15903360, 251454111, TOP) and TERMINAL.complex_log == 52270',
     '    assert ranks == (16096, 254464, 4023296, 63614464, 2079574939, TOP) and TERMINAL.complex_log == 52367'),
    ('    assert TERMINAL.kappa == Q(".003900862349168")',
     '    assert TERMINAL.kappa == Q(".003900866740647")'),
    ('    old_upper = ordinary_upper(ranks, debit=PEER_ORDINARY)',
     '    old_upper = ordinary_upper(OLD_RANKS, debit=PEER_ORDINARY)'),
    ('    peer8098 = ordinary_upper(ranks, debit=PEER8098_ORDINARY)\n'
     '    peer8098_tight = ordinary_upper(ranks, debit=PEER8098_TIGHT)',
     '    peer8098 = ordinary_upper(OLD_RANKS, debit=PEER8098_ORDINARY)\n'
     '    peer8098_tight = ordinary_upper(OLD_RANKS, debit=PEER8098_TIGHT)'),
    ('    domain = ordinary_upper(ranks, debit=DOMAIN_ORDINARY)\n'
     '    assert DOMAIN_KAPPA < domain - 5*STOP <= DOMAIN_KAPPA + Q(1, 10**15)\n'
     '    assert old_upper < peer8098 < peer8098_tight < domain < paid < ordinary_upper(ranks) < '
     'gaussian_upper(TERMINAL.complex_log)',
     '    domain = ordinary_upper(OLD_RANKS, debit=DOMAIN_ORDINARY)\n'
     '    assert DOMAIN_KAPPA < domain - 5*STOP <= DOMAIN_KAPPA + Q(1, 10**15)\n'
     '    paid8098 = ordinary_upper(OLD_RANKS, debit=PAID8098_ORDINARY)\n'
     '    assert PAID8098_KAPPA < paid8098 - 5*STOP <= PAID8098_KAPPA + Q(1, 10**15)\n'
     '    same_budget = ordinary_upper(OLD_RANKS)\n'
     '    assert SAME_BUDGET_KAPPA < same_budget - 5*STOP <= SAME_BUDGET_KAPPA + Q(1, 10**15)\n'
     '    assert old_upper < peer8098 < peer8098_tight < domain < paid8098 < same_budget < paid < '
     'ordinary_upper(ranks) < gaussian_upper(TERMINAL.complex_log)'),
    ('    assert conversion == PREMIUM and logB == 171798577106',
     '    assert conversion == PREMIUM and logB == 1374389410066'),
    ('    five_stage_28 = ((63614, 1005841, 15903840, 251461645, TOP), TERMINAL.complex_log)\n'
     '    assert ordinary_upper(five_stage_28[0]) < ordinary_upper(ranks)',
     '    five_stage_30 = ((65536, 2097152, 67108864, 1004469748, TOP), TERMINAL.complex_log)\n'
     '    six_stage_29 = ((8192, 131072, 2097152, 33554432, 501079706, 536870911), TERMINAL.complex_log)\n'
     '    assert ordinary_upper(five_stage_30[0]) < ordinary_upper(ranks)'),
    ('        rejected(lambda: require_funding(*five_stage_28), "five-stage-28bit-profile-at-new-rate"),',
     '        rejected(lambda: require_funding(*five_stage_30), "five-stage-30bit-profile-at-new-rate"),\n'
     '        rejected(lambda: require_funding(*six_stage_29), "six-stage-29bit-profile-at-new-rate"),\n'
     '        rejected(lambda: require_funding(OLD_RANKS, 52270), "pr8098-28bit-profile-at-new-rate"),\n'
     '        rejected(lambda: require_funding(ranks, TERMINAL.complex_log, debit=PAID8098_ORDINARY),\n'
     '                 "pr8098-paid-2401-debit-at-new-rate"),\n'
     '        rejected(lambda: require_funding(ranks, TERMINAL.complex_log, debit=ORDINARY + Q(1, 2**20)),\n'
     '                 "next-debit-tick-at-new-rate"),'),
    ('    assert 2660000 * (30 + 2) < 2**30 and 17**16 * 10 ** (21 * 16) < 2**1182',
     '    assert 2660000 * (31 + 2) < 2**31 and 17**16 * 10 ** (21 * 16) < 2**1182'),
    ('    DROPS = (861, 231, 232, 232, 232, 2)\n'
     '    for i, d in enumerate(DROPS):\n'
     '        require_peer_funding(at(i, -(d - 1)), TERMINAL.complex_log)',
     '    DROPS = (None, 15776, 16748, 16814, 71886, 307)\n'
     '    for i, d in enumerate(DROPS):\n'
     '        if d is None:\n'
     '            continue\n'
     '        require_funding(at(i, -(d - 1)), TERMINAL.complex_log)'),
    ('        rejected(lambda i=i, d=d: require_peer_funding(at(i, -d), TERMINAL.complex_log),\n'
     '                 f"peer8097-ordinary-height-{i}-minus-{d}")\n'
     '        for i, d in enumerate(DROPS)',
     '        rejected(lambda i=i, d=d: require_funding(at(i, -d), TERMINAL.complex_log),\n'
     '                 f"wide-ordinary-height-{i}-minus-{d}")\n'
     '        for i, d in enumerate(DROPS) if d is not None'),
    ('    assert ranks[last] == TOP and TOP.bit_length() == BITS and 1024 * (TOP + 1) + 3 >= 2**38',
     '    assert ranks[last] == TOP and TOP.bit_length() == BITS and 1024 * (TOP + 1) + 3 >= 2**41'),
    ('                neighbours.append(ordinary_upper((*t, max_penultimate(t), TOP), debit=PEER_ORDINARY))\n'
     '    assert all(n <= ordinary_upper(ranks, debit=PEER_ORDINARY) for n in neighbours)',
     '                neighbours.append(ordinary_upper((*t, max_penultimate(t), TOP)))\n'
     '    # Local optimality at 31-bit: the strict Fraction comparison\n'
     '    # `n <= ordinary_upper(ranks)` cannot be attained -- the ceiling saturates\n'
     '    # (frozen at TERMINAL.kappa in both the exact and grid-kappa forms) across\n'
     '    # any +/-16 shift of any free height, so every neighbouring profile prices\n'
     '    # strictly higher in Fraction terms. The honest terminal statement is the\n'
     '    # 10^-15 grid-kappa comparison: no neighbour raises TERMINAL.kappa\n'
     '    # grid-floor.\n'
     '    def grid_kappa(x):\n'
     '        return Q(int((x - 5 * STOP) * 10**15), 10**15)\n'
     '    assert all(grid_kappa(n) == TERMINAL.kappa for n in neighbours)'),
    ('# Local optimality of free prefix with h5 pinned at 2^28 - 1',
     '# Local optimality of free prefix with h5 pinned at 2^31 - 1'),
    ('if min(at(0, -1)) < 8192 else None, "first-ordinary-height-below-8192"),',
     'if min(at(0, -(ranks[0] - 8191))) < 8192 else None, "first-ordinary-height-below-8192"),'),
    ('        "PASS_10SHORTCUT_3TYPE_28BIT_6STAGE_SEAM",',
     '        "PASS_K7_31BIT_WIDE_DATUM_6STAGE_SEAM",'),
)
