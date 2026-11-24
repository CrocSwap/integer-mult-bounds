"""Apply the exact sharper-period price to the frozen ordinary-tariff image."""

from hashlib import sha256
from pathlib import Path

BASE_PINS = {
    "positive_debit.py": "32ee6a20e8f7fe6e2d1a3852b232179b0c6736c816f5bfd7bd9ec62cbffa9eb8",
    "receipt.py": "5d647aea991322addecbbb68565f20cf585badc3dadc82e392ce2feb86986c62",
    "independent_price.py": "f7e9c7f697c8af121bdaa7a8dffed21bb86f077a76d12cfc660b79c64d7df39d",
}

POSITIVE_EDITS = (
    ("POSITIVE_DEBIT = Q(1039776, 2**23)", "POSITIVE_DEBIT = Q(1039701, 2**23)"),
    ('''    # Keep the upper physical period, complete group padding, both endpoint
    # roundings, and the endpoint of the integral's chosen upper band.
    finite_factor = (
        (1 + DELTA)
        * (1 + Q(4 * max(targets), scale))
        * Q(power_interval(scale * lower, c)[1], UNIT)
        * (1 + fringe / lower + DELTA)
        / (1 - DELTA) ** 4
    )
    assert UNIT * finite_factor < power_interval(2, POSITIVE_DEBIT)[0]''',
     '''    # The literal four-aligned period gives ceil(x)/x for x=M/(4s).
    # Here s <= max(targets)*upper and upper <= M/scale.
    x_lower = Q(scale, 4 * max(targets))
    period_upper = Q(257, 256)
    assert 255 < x_lower < 256 and 256 / x_lower < period_upper
    # For x <= 256 the first ratio covers ceil(x)/x. For x > 256,
    # m=ceil(x)-1 is at least 256, and ceil(x)/x < 1+1/m.
    common_factor = (
        (1 + DELTA)
        * Q(power_interval(scale * lower, c)[1], UNIT)
        * (1 + fringe / lower + DELTA)
        / (1 - DELTA) ** 4
    )
    finite_factor = period_upper * common_factor
    assert UNIT * finite_factor < power_interval(2, POSITIVE_DEBIT)[0]
    assert power_interval(2, POSITIVE_DEBIT - Q(1, 2**23))[1] < UNIT * finite_factor
    coarse_factor = (1 + 1 / x_lower) * common_factor
    assert power_interval(2, POSITIVE_DEBIT)[1] < UNIT * coarse_factor'''),
)

RECEIPT_EDITS = (
    ("DEBIT = Q(1039776, 2**23)", "DEBIT = Q(1039701, 2**23)"),
    ("== (133567098, 208653)", "== (134136243, 208653)"),
    ('assert TERMINAL.kappa == Q(".003900857269150")',
     'assert TERMINAL.kappa == Q(".003900857312000")'),
    ("assert gain == Q(341, 250000000000000)",
     "assert gain == Q(22107, 500000000000000)"),
    ('''    stop = Q(1, TERMINAL.positive_stop_denominator)
    positive_ceiling = GAUSSIAN_C - DEBIT / TERMINAL.complex_log - 5 * stop''',
     '''    stop = Q(1, TERMINAL.positive_stop_denominator)
    frozen_tariff = Q(".003900857269150")
    frozen_positive_ceiling = GAUSSIAN_C - Q(1039776, 2**23) / TERMINAL.complex_log - 5 * stop
    assert frozen_tariff < frozen_positive_ceiling < TERMINAL.kappa
    assert TERMINAL.kappa - frozen_tariff == Q(857, 20000000000000)
    positive_ceiling = GAUSSIAN_C - DEBIT / TERMINAL.complex_log - 5 * stop'''),
)

INDEPENDENT_EDITS = (
    ('''    upper = (
        (1 + delta)
        * (1 + Q(4 * 258, scale))
        * powers(scale * LOWER, c)[1]
        * (1 + fringe / LOWER + delta)
        / (1 - delta) ** 4
    )
    lower = powers(2, Q(1039776, 2**23))[0]
    assert lower - upper > 0 and lower - upper > Q("0.000000019")
    assert powers(2, Q(1039775, 2**23))[0] < upper''',
     '''    assert max(recipe.targets.histogram) == 258
    x_lower = Q(scale, 4 * 258)
    period_upper = Q(257, 256)
    assert 255 < x_lower < 256 and 256 / x_lower < period_upper
    common_factor = (
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
    print("PASS_SHARPER_POSITIVE_PERIOD", "257/256", "1039701/8388608")'''),
    ('assert TERMINAL.kappa - Q(".003900857267786") == Q(341, 250000000000000)',
     'assert TERMINAL.kappa - Q(".003900857267786") == Q(22107, 500000000000000)'),
)

EDITS = {
    "positive_debit.py": POSITIVE_EDITS,
    "receipt.py": RECEIPT_EDITS,
    "independent_price.py": INDEPENDENT_EDITS,
}


def patch_price(peer: Path) -> None:
    """Apply the debit with the exact Round 417 receipt as the preimage."""
    changed = {}
    for name, changes in EDITS.items():
        path = peer / name
        raw = path.read_bytes()
        if sha256(raw).hexdigest() != BASE_PINS[name]:
            raise ValueError(f"Unexpected prepared input {name}")
        text = raw.decode()
        for before, after in changes:
            if text.count(before) != 1:
                raise ValueError(f"Expected one change point in {name}")
            text = text.replace(before, after, 1)
        compile(text, name, "exec")
        changed[path] = text.encode()
    for path, data in changed.items():
        path.write_bytes(data)
