"""Recompute the finite supplier prices from the actual installed word."""

from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from invoice import source_module, OB, GB


def verify(tree):
    peer = tree / "research/frequency-weighted-native-multiplier"
    runtime = tree / "runtime"
    sys.argv = [__file__, str(runtime)]
    rc = source_module("target_receipt", peer / "receipt.py")
    independent = source_module(
        "target_independent_price", peer / "independent_price.py"
    )
    lo, hi = rc.prepare_native()
    assert len(lo) == 3 and len(hi) == 4
    for profile, recipes in zip((rc.ENTRY, rc.TERMINAL), (lo, hi), strict=True):
        assert tuple(v.rank_log for v in recipes) == (
            *profile.rank_logs,
            profile.complex_log,
        )
        assert all(
            v.level_floor == 18960 and v.trial == rc.BINARY_C for v in recipes[:-1]
        )
        assert recipes[-1].trial == rc.GAUSSIAN_C
    assert hi[-1].targets is lo[-1].targets and hi[-1].cells is lo[-1].cells
    targets, paid = rc.raw_moments(rc.graph(), rc.caller())
    for recipe in (*lo[:-1], *hi[:-1]):
        assert (Counter(recipe.targets), Counter(recipe.paid)) == (targets, paid)
    om, cells = rc.certify(rc.BINARY_C, (targets, paid))
    assert om > 0 and cells == hi[0].cells and len(cells) == 24
    factor = Q(47, 20) * rc.tape_factor(134, rc.BINARY_C, 18960, suffix=64)
    # Full original 256/255 reserve remains inside tape_factor.
    alo, ahi = independent.powers(2, OB - 1)
    assert factor < 2 * alo and Q(75, 32) / Q(47, 20) == Q(375, 376)
    gp = rc.check_numerical(hi[-1])
    assert (
        rc.DEBIT == GB
        and gp["real_targets"] == [52608, 52608]
        and gp["real_loans"] == [282336, 281328]
    )
    assert gp["grade_cells"] == 51 and gp["typed_cells"] == 88
    independent.weighted()
    return {
        "ordinary_floor": 18960,
        "ordinary_raw_margin": str(om),
        "ordinary_tariff": "47/20",
        "ordinary_reserve": "256/255",
        "ordinary_debit": str(OB),
        "ordinary_factor_upper": str(factor),
        "ordinary_allowance_lower": str(2 * alo),
        "gaussian": gp,
    }


if __name__ == "__main__":
    if not __debug__:
        raise ValueError("Enable assertions")
    print(json.dumps(verify(Path(sys.argv[1]).resolve()), indent=2))
