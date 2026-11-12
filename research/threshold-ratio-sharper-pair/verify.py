#!/usr/bin/env python3
"""Exact checks for the sharper section-6 one-step ratio.

The argument is PROOF.md. Raises are used so python -O still fails closed.
Finite rectangles and the exponent census are not substitutes for the lemma.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SELECTED = ROOT / "certificates/selected-result.json"
REVIEW = ROOT / "docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md"
SENTENCE = (
    "choose an integer j beyond `4d0/\u03b4` with\n"
    "`C(j+1)^d0 <= 2^(\u03b4j)` and freeze the input threshold at least 2^j. "
    "Subsequent\nratios decrease, so the inequality holds thereafter."
)

# Least q with 3^p < 2^q, for p = 1..17. PROOF.md records the same rows.
LEAST_Q = (
    2, 4, 5, 7, 8, 10, 12, 13, 15, 16, 18, 20, 21, 23, 24, 26, 27
)


def die(message):
    raise SystemExit(message)


def ceil_div(numerator, denominator):
    if numerator <= 0 or denominator <= 0:
        die("ceil domain")
    return (numerator + denominator - 1) // denominator


def least_q(exponent):
    """Least positive integer q with 3^exponent < 2^q. Stops by 4^exponent > 3^exponent."""
    if exponent < 1:
        die("exponent")
    three = pow(3, exponent)
    q_value = 1
    limit = 2 * exponent
    while q_value <= limit:
        if (1 << q_value) > three:
            return q_value
        q_value += 1
    die("least q did not terminate")


def step_strict(degree, numerator, denominator, modulus):
    """(m+1)^{d0 b} < m^{d0 b} * 2^a."""
    if modulus < 1 or degree < 1 or numerator < 1 or denominator < 1:
        return False
    exponent = degree * denominator
    return pow(modulus + 1, exponent) < pow(modulus, exponent) * (1 << numerator)


def holds(c_value, degree, numerator, denominator, index):
    if index < 0 or c_value < 1:
        return False
    left = pow(c_value, denominator) * pow(index + 1, degree * denominator)
    return left <= (1 << (numerator * index))


def main():
    selected = json.loads(SELECTED.read_text(encoding="utf-8"))
    if selected.get("kappa") != "363005817/100000000000":
        die("selected kappa changed")
    if selected.get("decimal") != "0.00363005817":
        die("selected decimal changed")
    names = [row.get("id") for row in selected.get("assumptions", [])]
    if names != [
        "native_all_columns",
        "owned_erasure",
        "compiler",
        "precision_tape",
        "analytic_recovery",
    ]:
        die("assumption ids changed")
    review = REVIEW.read_text(encoding="utf-8")
    if review.count(SENTENCE) != 1:
        die("section-6 sentence missing or duplicated")

    # Hand multiplication chain for 3^17 < 2^27. These are the proof's integers.
    three_2 = 3 * 3
    three_4 = three_2 * three_2
    three_8 = three_4 * three_4
    three_16 = three_8 * three_8
    three_17 = three_16 * 3
    two_10 = 1 << 10
    two_20 = two_10 * two_10
    two_27 = two_20 * (1 << 7)
    if (three_2, three_4, three_8, three_16, three_17) != (9, 81, 6561, 43046721, 129140163):
        die("power-of-three chain")
    if (two_10, two_20, two_27) != (1024, 1048576, 134217728):
        die("power-of-two chain")
    if not three_17 < two_27:
        die("pair 3^17 < 2^27")
    if pow(3, 17) != three_17 or (1 << 27) != two_27:
        die("pow disagrees with the chain")
    if (1 << 26) != two_27 // 2 or (1 << 26) != 67108864 or (1 << 26) >= three_17:
        die("2^26 should fail the pair")
    if 27 * 5 >= 17 * 8:
        die("27/17 should be strictly below 8/5")
    if 5 * 8 != 8 * 5:
        die("8/5 boundary")
    if not pow(3, 5) < (1 << 8):
        die("original pair")

    # A smaller ratio is not admissible unless the power comparison holds.
    if pow(3, 12) <= (1 << 19):
        die("3^12 > 2^19 is the rejection control")
    if 19 * 5 >= 12 * 8:
        die("19/12 is numerically below 8/5 and must stay inadmissible")

    # (d0, a, b) = (1, 2, 5). Both rationals induce ceiling 4.
    if ceil_div(8 * 1 * 5, 5 * 2) != 4:
        die("old test ceiling")
    if ceil_div(27 * 1 * 5, 17 * 2) != 4:
        die("new test ceiling")
    if 34 * 3 + 33 != 135 or 135 != 27 * 5:
        die("135/34 split")
    four_5 = ((4 * 4) * (4 * 4)) * 4
    five_5 = ((5 * 5) * (5 * 5)) * 5
    three_5 = ((3 * 3) * (3 * 3)) * 3
    if (four_5, five_5, three_5) != (1024, 3125, 243):
        die("small fifth powers")
    if three_5 * 4 != 972 or four_5 * 4 != 4096:
        die("test-point decimals")
    if four_5 <= three_5 * (1 << 2):
        die("m=3 must fail at (1, 2, 5)")
    if five_5 >= four_5 * (1 << 2):
        die("m=4 must hold at (1, 2, 5)")
    if not step_strict(1, 2, 5, 4) or step_strict(1, 2, 5, 3):
        die("test-point step")
    for modulus in range(4, 12):
        if not step_strict(1, 2, 5, modulus):
            die("test-point tail")

    # 243 > 64 and 243 > 128 feed the ceiling floors in PROOF.md.
    if three_5 <= (1 << 6) or three_5 <= (1 << 7) or three_5 >= (1 << 8):
        die("243 against 64, 128 and 256")

    # (1, 1, 5): every admissible pair has ceiling at least 8; the step holds at 7.
    if ceil_div(8 * 5, 5 * 1) != 8 or ceil_div(27 * 5, 17 * 1) != 8:
        die("(1, 1, 5) ceilings")
    six_5 = ((6 * 6) * (6 * 6)) * 6
    seven_5 = ((7 * 7) * (7 * 7)) * 7
    eight_5 = ((8 * 8) * (8 * 8)) * 8
    if (six_5, seven_5, eight_5) != (7776, 16807, 32768):
        die("sixth through eighth fifth powers")
    if 2 * six_5 != 15552 or 2 * seven_5 != 33614:
        die("(1, 1, 5) decimals")
    if seven_5 <= six_5 * 2:
        die("m=6 must fail at (1, 1, 5)")
    if eight_5 >= seven_5 * 2:
        die("m=7 must hold at (1, 1, 5)")

    # (1, 27, 17): 27/17 lowers the ceiling from 2 to 1, and m=1 holds.
    if 8 * 17 != 136 or 5 * 27 != 135:
        die("136/135 split")
    if ceil_div(8 * 17, 5 * 27) != 2 or ceil_div(27 * 17, 17 * 27) != 1:
        die("permissive witness ceilings")
    if not step_strict(1, 27, 17, 1):
        die("permissive witness step")
    if (1 << 17) != 131072 or (1 << 17) >= three_17 or three_17 >= two_27:
        die("equality-case chain")

    # Further admissible ratios, witnesses only. Not a minimum claim.
    witness_pairs = ((29, 46), (41, 65))
    previous_num, previous_den = 27, 17
    for exponent, q_value in witness_pairs:
        if pow(3, exponent) >= (1 << q_value):
            die("witness pair power")
        if q_value * previous_den >= exponent * previous_num:
            die("witness pair should be strictly sharper than 27/17")
        previous_num, previous_den = q_value, exponent
        if ceil_div(q_value * 5, exponent * 2) != 4:
            die("witness test ceiling")
    if (46 * 17, 29 * 27, 65 * 29, 41 * 46) != (782, 783, 1885, 1886):
        die("witness cross multiplication")

    # Exhaustive census: p = 1..17. Completeness is the bounded loop in least_q.
    if len(LEAST_Q) != 17:
        die("census table width")
    for exponent, expected in enumerate(LEAST_Q, start=1):
        found = least_q(exponent)
        if found != expected:
            die("census mismatch")
        if (1 << (found - 1)) > pow(3, exponent):
            die("census q is not least")
        if exponent <= 16 and 5 * found < 8 * exponent:
            die("unexpected sharper pair below exponent 17")
        if 5 * found <= 6 * exponent:
            die("admissible pair below the 6/5 floor")
        if ceil_div(5 * found, 2 * exponent) < 4:
            die("test ceiling fell below 4")
    if LEAST_Q[16] != 27 or 5 * 27 >= 8 * 17:
        die("least-exponent pair")
    if 5 * 28 <= 8 * 17:
        die("the next q at p=17 is not sharper")

    rectangle_rows = 0
    for degree in range(1, 6):
        for numerator in range(1, 9):
            for denominator in range(1, 9):
                new_ceiling = ceil_div(27 * degree * denominator, 17 * numerator)
                old_ceiling = ceil_div(8 * degree * denominator, 5 * numerator)
                if new_ceiling > old_ceiling:
                    die("27/17 ceiling exceeded 8/5")
                if not step_strict(degree, numerator, denominator, new_ceiling):
                    die("rectangle step")
                if not step_strict(degree, numerator, denominator, old_ceiling):
                    die("old ceiling step")
                rectangle_rows += 1

    # P(j) without the ceiling need not persist. P(0) holds and P(1) fails here.
    if not holds(1, 1, 2, 5, 0) or holds(1, 1, 2, 5, 1):
        die("bare success below the ceiling")
    if ceil_div(27 * 5, 17 * 2) <= 1:
        die("that index is below the ceiling")

    persistence_rows = 0
    for c_value in range(1, 5):
        for degree in range(1, 4):
            for numerator in range(1, 5):
                for denominator in range(1, 5):
                    modulus = ceil_div(27 * degree * denominator, 17 * numerator)
                    if holds(c_value, degree, numerator, denominator, modulus - 1):
                        if not holds(c_value, degree, numerator, denominator, modulus):
                            die("persistence row")
                        persistence_rows += 1
    if persistence_rows < 1:
        die("persistence control was vacuous")

    # (1+1/m)^m < 3 on a finite initial segment. The proof covers every m.
    for modulus in range(1, 49):
        if pow(modulus + 1, modulus) >= 3 * pow(modulus, modulus):
            die("binomial bound")
    if pow(2, 1) < 2 * pow(1, 1):
        die("the constant 2 is already false at m=1")

    print(
        "PASS_THRESHOLD_RATIO_SHARPER_PAIR"
        " rational=27/17"
        " previous=8/5"
        " test=1,2,5"
        " ceiling=4"
        " sharp_below=3"
        " census_p=17"
        " unique_least_exponent=17,27"
        " witness_pairs=2"
        f" rectangle_rows={rectangle_rows}"
        f" persistence_rows={persistence_rows}"
        " binomial_rows=48"
        " kappa=363005817/100000000000"
        " no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
