"""Price both installed tiers and independently derive the two binding integer heights."""

from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import sys

TARGET, ETA = Q(39, 10000), Q(1, 256)
OB, GB = Q(11239, 8192), Q(1039776, 2**23)
STOP = Q(1, 10**18)
GRID = 10**21


def source_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def rates(profile, cb):
    previous = Q(0)
    result = []
    for i, h in enumerate(profile.rank_logs):
        upper = min(profile.eta, (249 * (cb - OB / h) + previous) / 250)
        booked = (
            profile.ordinary
            if i + 1 == len(profile.rank_logs)
            else Q(int(upper * GRID) - 1, GRID)
        )
        if not previous < booked < upper:
            raise ValueError("Unfunded ordinary stage")
        result.append(
            {
                "height": h,
                "booked": str(booked),
                "upper": str(upper),
                "slack": str(upper - booked),
            }
        )
        previous = booked
    return result


def calculate(tree):
    runtime = tree / "runtime"
    peer = tree / "research/frequency-weighted-native-multiplier"
    sys.argv = [__file__, str(runtime)]
    rc = source_module("weighted_target_receipt", peer / "receipt.py")
    from installations import (
        BINARY_C,
        GAUSSIAN_C,
        ENTRY,
        TERMINAL,
        at_public,
        activation,
    )
    from outer_budget import margins

    assert (
        ENTRY.rank_logs == (3000, 3080)
        and ENTRY.complex_log == 1024
        and ENTRY.kappa == Q(".00345")
    )
    assert (TERMINAL.rank_logs, TERMINAL.complex_log, TERMINAL.kappa, TERMINAL.eta) == (
        (8192, 106000, 1681001),
        85406,
        TARGET,
        ETA,
    )
    assert TERMINAL.ordinary == TARGET + 5 * STOP and GAUSSIAN_C == Q(
        17158764376, 2**42
    )
    assert BINARY_C == Q(4391986206293, 2**50) and rc.DEBIT == GB
    # The price routine takes its tariff from module globals. Use #8072's
    # full-reserve debit for both tiers and keep #8088's larger clock additions.
    rc.ORDINARY_DEBIT = OB
    early, late = rc.bank(ENTRY), rc.bank(TERMINAL)
    for o, profile in ((early, ENTRY), (late, TERMINAL)):
        rs = rates(profile, BINARY_C)
        assert [x["booked"] for x in rs] == o["ordinary_rates"]
        assert Q(o["gaussian_rate"]) == GAUSSIAN_C - GB / profile.complex_log
        strict, functional, positive = margins(
            profile.kappa, STOP, profile.ordinary, Q(o["gaussian_rate"])
        )
        assert (
            len(strict) == 54
            and len(functional) == 4
            and min(strict + functional + [positive]) > 0
        )
        o["ordinary_stage_bounds"] = rs
    G = TERMINAL.complex_log
    H = TERMINAL.rank_logs
    q = TERMINAL.ordinary
    want = GB / (GAUSSIAN_C - q)
    assert want.numerator // want.denominator + 1 == G
    assert margins(TARGET, STOP, q, GAUSSIAN_C - GB / (G - 1))[-1] < 0
    _, _, bad_legacy = margins(
        TARGET, STOP, q, Q(17145637307, 2**42) - Q(64939, 524288) / G
    )
    assert bad_legacy < 0
    previous = Q(late["ordinary_rates"][-2])
    assert (249 * (BINARY_C - OB / (H[-1] - 1)) + previous) / 250 < q
    A = activation(TERMINAL)
    offset = (-pow(2, A, 6)) % 6
    header = (1 << A) + offset
    assert at_public(header) is TERMINAL and at_public(header - 6) is ENTRY
    premium = rc.ceil((TARGET - ENTRY.kappa) * A)
    complete = 1 + max(early["log2_C"] + premium, late["log2_C"])
    # Independent closed-form recomputation of the full terminal and global cost.
    B = 128 + 3 * len(H) + 320 * sum(H)
    assert B == late["log2_B"] and late["log2_C"] == max(84500001, 1602 + 220 * G + B)
    assert late["log2_C"] >= early["log2_C"] + premium
    parent_fixed_ceiling = GAUSSIAN_C - GB / 66037 - 5 * STOP
    # Each new ordinary rate lies below a convex combination of its local
    # ceiling and the previous rate. Induct from zero at the largest 20-bit H.
    parent_20bit_ceiling = BINARY_C - Q(1420718, 2**20) / (2**20 - 1) - 5 * STOP
    assert Q(".003899574328473") < parent_fixed_ceiling < parent_20bit_ceiling < TARGET
    return {
        "parent_fixed_G_public_ceiling": str(parent_fixed_ceiling),
        "parent_any_20bit_ordinary_public_ceiling": str(parent_20bit_ceiling),
        "signed_gain_over_20bit_ceiling": str(TARGET - parent_20bit_ceiling),
        "target": str(TARGET),
        "ordinary_guard": str(q),
        "ordinary_debit": str(OB),
        "gaussian_debit": str(GB),
        "gaussian_raw": str(GAUSSIAN_C),
        "entry": early,
        "terminal": late,
        "G_minus_one_positive_margin": str(
            margins(TARGET, STOP, q, GAUSSIAN_C - GB / (G - 1))[-1]
        ),
        "old_word_positive_margin": str(bad_legacy),
        "entry_conversion_bits": premium,
        "complete_log2_C": complete,
        "public_A": A,
        "public_offset": offset,
        "peak_height": max(*H, G),
        "parent_complete_log2_C": 685495960,
        "delta_from_8088": str(TARGET - Q(".003899574328473")),
    }


if __name__ == "__main__":
    if not __debug__:
        raise ValueError("Enable assertions")
    print(json.dumps(calculate(Path(sys.argv[1]).resolve()), indent=2))
