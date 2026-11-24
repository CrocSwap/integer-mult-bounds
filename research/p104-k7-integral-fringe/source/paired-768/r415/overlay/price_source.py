"""Apply the proven fixed-height child tariff to the prepared #8094 prices."""

from hashlib import sha256
from pathlib import Path

BASE_PINS = {
    "receipt.py": "492336828d9139ddfd4017ced7355a5de11b569295f87bde5866d4b3db68d4b8",
    "independent_price.py": "719c13cdd08254f4229c551f3b9263820724f21579d18be76bda4833302812b0",
}

RECEIPT_EDITS = (
    ("ORDINARY_DEBIT = Q(1420718, 2**20)\nCHILD_TARIFF = Q(2401, 1024)",
     "ORDINARY_DEBIT = Q(1414404, 2**20)\nCHILD_TARIFF = Q(2391, 1024)"),
    ('''    ordinary_upper = Q("2.557796525567700799")
    assert tape_factor(134, BINARY_C, 4474, Q(186, 25)) * Q(255, 256) * CHILD_TARIFF < ordinary_upper
    assert ordinary_upper**1048576 < 2**1420718
    assert Q(75, 32) / CHILD_TARIFF == Q(2400, 2401)''',
     '''    ordinary_upper = tape_factor(134, BINARY_C, 4474, Q(186, 25)) * Q(255, 256) * CHILD_TARIFF
    ordinary_allowance = 2 * Q(power_interval(2, ORDINARY_DEBIT - 1)[0], UNIT)
    assert ordinary_upper < ordinary_allowance
    worst_child = Q(2390, 1024)
    rank_guard = 3**7  # N >= 9 and the quotient mean decreases with N.
    assert 21 * rank_guard + 3 <= worst_child * (9 * rank_guard - 1)
    assert all(height >= 4 for profile in (ENTRY, TERMINAL) for height in profile.rank_logs)
    child_ratio = worst_child / CHILD_TARIFF
    assert child_ratio == Q(2390, 2391)
    child_sum = 1 / (1 - child_ratio)
    assert child_sum == 2391 < 8 * 376 and (Q(7, 10) * child_sum)**2 < 2**22'''),
    ("(134145233, 208653)", "(133567098, 208653)"),
    ('''    older = Q(".003898219753506")
    gain = TERMINAL.kappa - older
    assert gain == Q(".003900857267786") - Q(".003898219753506")''',
     '''    older = Q(".003900857267786")
    gain = TERMINAL.kappa - older
    assert TERMINAL.kappa == Q(".003900857269150")
    assert gain == Q(341, 250000000000000)
    old_crossing = Q(
        70271596826947689616436948507028761711,
        18014398375264256000000000000000000000000,
    )
    assert older < old_crossing < TERMINAL.kappa
    assert TERMINAL.complex_log == 208653
    stop = Q(1, TERMINAL.positive_stop_denominator)
    positive_ceiling = GAUSSIAN_C - DEBIT / TERMINAL.complex_log - 5 * stop
    assert TERMINAL.kappa < positive_ceiling <= TERMINAL.kappa + Q(1, 10**15)
    assert GAUSSIAN_C - DEBIT / (TERMINAL.complex_log - 1) - 5 * stop < TERMINAL.kappa
    for invoice in (early, late):
        assert (invoice["signed"]["strict"], invoice["signed"]["functional"]) == (54, 4)'''),
    ('''        ordinary_child_contraction="2400/2401",
        ordinary_child_geometric_sum=2401,''',
     '''        ordinary_child_contraction=str(child_ratio),
        ordinary_child_geometric_sum=int(child_sum),'''),
)

NEW_INDEPENDENT_CONTROLS = '''
    # Use the unchanged suffix at the new tariff on the same finite factor.
    candidate_tariff = Q(2391, 1024)
    candidate_lo, candidate_hi = bounds(4474, Q(186, 25), candidate_tariff)
    lower_allowance = 2 * powers(2, Q(1414403, 2**20) - 1)[1]
    candidate_allowance = 2 * powers(2, Q(1414404, 2**20) - 1)[0]
    assert lower_allowance < candidate_lo < candidate_hi < candidate_allowance
    child_mean = Q(2390, 1024)
    assert 21 * 3**7 + 3 <= child_mean * (9 * 3**7 - 1)
    assert 21 * 3**6 + 3 > child_mean * (9 * 3**6 - 1)
    assert Q(75, 32) / candidate_tariff > 1  # The coarser bound fails here.
    candidate_ratio = child_mean / candidate_tariff
    assert candidate_ratio == Q(2390, 2391)
    candidate_sum = 1 / (1 - candidate_ratio)
    assert candidate_sum == 2391 < 2401
    assert (Q(7, 10) * candidate_sum)**2 < 2**22 and candidate_sum < 8 * 376
    print("PASS_SHARPER_CHILD_TARIFF", 4474, "1414404/1048576", str(candidate_ratio))
'''

INDEPENDENT_EDITS = (
    ('    print("PASS_CHILD_TARIFF", "2401/1024", "volume<=75/32", "sum=2401", "entry+5", "terminal+9")\n',
     '    print("PASS_CHILD_TARIFF", "2401/1024", "volume<=75/32", "sum=2401", "entry+5", "terminal+9")\n'
     + NEW_INDEPENDENT_CONTROLS),
    ('assert TERMINAL.kappa - peer == Q(".003900857267786") - Q(".0038982016137") and TERMINAL.kappa > c',
     '''assert TERMINAL.kappa - Q(".003900857267786") == Q(341, 250000000000000)
    assert TERMINAL.kappa > c'''),
)


def patch_prices(peer: Path) -> None:
    """Authenticate both prepared inputs before writing either edited module."""
    changed = {}
    for name, edits in (("receipt.py", RECEIPT_EDITS), ("independent_price.py", INDEPENDENT_EDITS)):
        path = peer / name
        data = path.read_bytes()
        if sha256(data).hexdigest() != BASE_PINS[name]:
            raise ValueError(f"Unexpected prepared input {name}")
        source = data.decode()
        for before, after in edits:
            if source.count(before) != 1:
                raise ValueError(f"Expected one change point in {name}")
            source = source.replace(before, after, 1)
        compile(source, name, "exec")
        changed[path] = source.encode()
    for path, data in changed.items():
        path.write_bytes(data)
