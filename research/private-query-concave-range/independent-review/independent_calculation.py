#!/usr/bin/env python3
"""Check the new scalar inputs without the submitted verifier.

Use the six historical facts as premises. Decimal values are diagnostics
only. Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import json


root = Path(__file__).resolve().parent
relations = [(7, 9, 8, 8), (96, 8, 91, 9), (17, 9, 18, 8)]
results = []
for exponent_l, base_l, exponent_r, base_r in relations:
    lhs = pow(base_l, exponent_l)
    rhs = pow(base_r, exponent_r)
    assert lhs < rhs
    results.append({"lhs": f"{base_l}^{exponent_l}",
                    "rhs": f"{base_r}^{exponent_r}",
                    "gap": str(rhs - lhs)})
assert pow(13, 10) * pow(8, 7) < pow(12, 10) * pow(9, 7)
assert pow(8, 7) * pow(3, 10) < pow(13, 10)
results.insert(2, {"lhs": "13^10 * 8^7", "rhs": "12^10 * 9^7",
                   "gap": str(pow(12, 10) * pow(9, 7)
                              - pow(13, 10) * pow(8, 7))})
results.append({"lhs": "8^7 * 3^10", "rhs": "13^10",
                "gap": str(pow(13, 10) - pow(8, 7) * pow(3, 10))})
assert Fraction(8, 7) * Fraction(91, 96) == Fraction(13, 12)
assert 8 * (1 - Fraction(17, 18)) == Fraction(4, 9)
assert 2 - Fraction(4, 9) * Fraction(13, 3) == Fraction(2, 27)
# Derive the affine charge in x=9^a without the submitted script.
assert Fraction(65, 8) - Fraction(9, 8) == 7
assert -Fraction(65, 8) + Fraction(81, 8) == 2
# Check endpoint values and chord signs at exact sample values.
for x in [Fraction(1), Fraction(2), Fraction(5), Fraction(9)]:
    slope = (x - 1) / 8
    intercept = (9 - x) / 8
    assert slope >= 0 and intercept >= 0
    assert 65 * slope + 9 * intercept == 7 * x + 2
assert (7 + 2 - 8, 7 * 9 + 2 - 8 * 8) == (1, 1)
# Numerical diagnostics do not prove the inequality.
with localcontext() as ctx:
    ctx.prec = 90
    l8 = Decimal(8).ln()
    l9 = Decimal(9).ln()
    a0 = (8 * l8 / (7 * l9)).ln() / (l9 - l8)
    f0 = 7 * (a0 * l9).exp() + 2 - 8 * (a0 * l8).exp()
    assert 0 < a0 < Decimal(7) / 10
    assert f0 > Decimal(2) / 27
    numerical = {"a0": str(a0), "F_a0": str(f0),
                 "proof_gap": str(Decimal(2) / 27)}
report = {
    "status": "PASS",
    "proof_inputs": "Independent integer and Fraction derivations; "
                    "no historical replay and no import of the proposed verifier.",
    "relations": results,
    "numerical_diagnostics_only": numerical,
    "premises_not_verified": [
        "Fixed Gram code rank eight and support at least 53.",
        "Frame rank from one to nine.",
        "Rank at most seven has capacity at most 36.",
        "Total rank at least 64.",
        "Total-64 necessary profiles have maximum rank at most eight.",
        "Eight rank-eight coordinate gathers factor the Gram code.",
    ],
}
(root / "independent-calculation.json").write_text(
    json.dumps(report, indent=2) + "\n")
print(json.dumps(numerical, indent=2))
