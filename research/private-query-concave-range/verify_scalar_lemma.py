#!/usr/bin/env python3
"""Check exact inputs to the uniform private-cost bound.

Use integer arithmetic and rational arithmetic. Do not import a price
engine. Prepared with OpenAI Codex assistance; Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys
import time


def verify():
    pairs = (
        ("positive_critical_point", 9**7, 8**8),
        ("critical_log_ratio", 8**96, 9**91),
        ("critical_point_below_seven_tenths", 13**10 * 8**7,
         12**10 * 9**7),
        ("minimum_coefficient_below_four_ninths", 9**17, 8**18),
        ("power_below_thirteen_thirds", 8**7 * 3**10, 13**10),
    )
    for name, left, right in pairs:
        if not left < right:
            raise ValueError(name)
    margin = 2 - Fraction(4, 9) * Fraction(13, 3)
    if margin != Fraction(2, 27) or margin <= 0:
        raise ValueError("margin")
    # Sum the chord at q=65 and N=9 as a polynomial in x=9^a.
    slope = (Fraction(-1, 8), Fraction(1, 8))
    intercept = (Fraction(9, 8), Fraction(-1, 8))
    coefficients = tuple(65 * slope[i] + 9 * intercept[i]
                         for i in range(2))
    if coefficients != (2, 7):
        raise ValueError("chord")
    if 7 + 2 - 8 != 1 or 7 * 9 + 2 - 8 * 8 != 1:
        raise ValueError("endpoints")
    return pairs, margin


def main():
    start = time.monotonic()
    output = Path(sys.argv[1]).resolve()
    if output.exists():
        raise ValueError("The output file exists.")
    pairs, margin = verify()
    script = Path(__file__).resolve()
    report = {
        "status": "PASS_EXACT_FULL_CONCAVE_PRIVATE_COST_LEMMA",
        "strict_gap_lower": str(margin),
        "integer_comparisons": [
            {"name": name, "left": str(left), "right": str(right),
             "positive_gap": str(right - left)}
            for name, left, right in pairs
        ],
        "chord_at_rank_total_65_query_count_9": [2, 7],
        "assumptions_not_replayed": [
            "Fixed Gram code has rank eight and minimum support 53.",
            "Source-frame ranks are one through nine.",
            "Rank-seven source capacity is at most 36.",
            "Total private frame rank is at least 64.",
            "Total-64 feasible profiles have no rank-nine frame.",
            "Eight rank-eight coordinate gathers factor the Gram code."
        ],
        "script_sha256": sha256(script.read_bytes()).hexdigest(),
        "proof_sha256": sha256(script.with_name("PROOF.md").read_bytes()).hexdigest(),
        "seconds": time.monotonic() - start,
    }
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(report["status"], report["strict_gap_lower"])


if __name__ == "__main__":
    main()
