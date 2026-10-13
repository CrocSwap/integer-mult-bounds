"""Re-issue the PR626 mixed invoice with signed-read CK scalar counts.

Run only through admission.py (which supplies the pinned witness environment).
The retained invoice_allcold.py runs unchanged: its own recount first checks
every original hash-bound provider byte and the original Horner count. Only
then are the CK local scalar counts and prefix replaced by this package's
EXPECTED.json receipt. Every finite inequality is then recomputed by the
retained code. Apache-2.0. Joseph / AmazedBot with Anthropic Claude assistance.
"""
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/complex-k492-owner-repair/code"))
import invoice_allcold as inv  # noqa: E402

assert __debug__, "Assertions required"
EXPECTED = json.loads((HERE / "EXPECTED.json").read_text())["programs"]
original_recount = inv.recount_provider


def signed_recount(local_dir, registry):
    p = original_recount(local_dir, registry)
    if Path(local_dir).name != "ck":
        return p
    for orientation, row in p["local"].items():
        receipt = EXPECTED[orientation]
        old = row["real_component_primitives"]
        new = receipt["real_primitives"]["signed"]
        # Bind the substitution to the exact original count it replaces.
        assert old == receipt["real_primitives"]["original"], "CK original count binding"
        assert row["macros"] == receipt["scalar_macros"], "CK macro binding"
        assert 0 < new < old and (old - new) % 2 == 0
        row["real_component_primitives"] = new
        # Every saved primitive is coefficient work inside an addition macro.
        row["coefficient_work_primitive_count"] -= (old - new) // 2
        row["prefix_l1"] = receipt["literal_positive_prefix"]
        row["prefix_bits"] = receipt["literal_positive_prefix_bits"]
        row["scalar_lowering"] = "PR860 signed-read runs (live work cleared at run end)"
    p["local_primitive_bound"] = (max(r["real_component_primitives"] for r in p["local"].values())
                                  + p["local_adapters"] * p["compiler"])
    return p


inv.recount_provider = signed_recount

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    for name in ("base", "hosted", "audit", "out", "retained-invoice"):
        ap.add_argument("--" + name, type=Path, required=True)
    a = ap.parse_args()
    inv.run(a.base, a.hosted, a.audit, a.out, a.retained_invoice)
