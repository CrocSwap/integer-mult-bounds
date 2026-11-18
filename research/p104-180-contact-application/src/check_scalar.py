"""Verify the signed integer-tick lowering on the exact 180-CLEAR word."""

import argparse
from fractions import Fraction
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path


OLD_WORD = "375f924e1588893680d39a194d29e5400bec4ab7e0b5db24b05f4cfe6fd05e15"
NEW_WORD = "5f555d6bb6736eb0c98826d9822f077ce1cbc6875c46b0c10731737665dbda6e"
SPLIT_CLOCK = 150834


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_literals(path, expected_word, count):
    raw = gzip.decompress(path.read_bytes())
    require(hashlib.sha256(raw).hexdigest() == expected_word, "decoded word identity")
    ops = json.loads(raw)["program"][SPLIT_CLOCK:SPLIT_CLOCK + count]
    require(len(ops) == count and all(op[:3] == ["ADD", 841, 284] and op[4:] == [127]
                                      for op in ops), "same target, preserved distinct donor and chart")
    return [Fraction(op[3]) for op in ops]


def nearest_even(numerator, divisor):
    floor, rem = divmod(numerator, divisor)
    twice = 2 * rem
    return floor + int(twice > divisor or (twice == divisor and floor % 2 == 1))


def nearest_up(numerator, divisor):
    return (numerator + divisor // 2) // divisor


def check(old_path, new_path):
    (old,) = read_literals(old_path, OLD_WORD, 1)
    integral, tail = read_literals(new_path, NEW_WORD, 2)
    require(integral.denominator == 1 and old == integral + tail and tail > 0,
            "positive two-part coefficient identity")
    whole, n, m, d = integral.numerator, old.numerator, tail.numerator, old.denominator
    require((whole, n, m, d) == (25, 23184221, 144221, 921600), "literal values")
    require(d == tail.denominator and gcd(n, d) == gcd(m, d) == 1,
            "one integral residue and one half-tie residue per period")
    require(n.bit_length() == 25 and max(whole.bit_length(), m.bit_length()) <= 24,
            "wide original and two accepted literal numerators")

    # Reduce only the fractional part to residues. On adding d ticks to the
    # donor, exact divisibility is unchanged. A nearest-even tie needs an even
    # integer translation: at a tie z = d/2 mod d and 25*z is even.
    # Away from a tie both nearest rules commute with every integer shift.
    require(d % 4 == 0, "even whole-part translation at every half tie")
    ties = []
    integral_residues = []
    signed_cases = 0
    for z in range(d):
        num = n * z
        rem_num = m * z
        require(num % d == rem_num % d, "exact-division domain disagreement")
        if num % d == 0:
            integral_residues.append(z)
        if 2 * (num % d) == d:
            ties.append(z)
            require((whole * z) % 2 == 0, "odd whole-part translation at a half tie")
        for sign in (-1, 1):
            shift = sign * whole * z
            for quantize in (nearest_up, nearest_even):
                single = quantize(sign * num, d)
                split = shift + quantize(sign * rem_num, d)
                require(single == split, "quantized one-step and two-step increments differ")
                require(min(0, single) <= shift <= max(0, single), "signed intermediate range")
                # The inverse of y -> y + single subtracts its actual increment.
                restored = split - quantize(sign * rem_num, d) - shift
                require(restored == 0, "inverse did not restore the target")
            signed_cases += 1
    require(integral_residues == [0] and ties == [d // 2], "complete period counts")
    half_num = n * ties[0]
    controls = {
        "changed_tail_numerator": nearest_up(n * d, d) != whole * d + nearest_up((m - 1) * d, d),
        "nearest_up_at_tie_is_not_odd": nearest_up(half_num, d) + nearest_up(-half_num, d) == 1,
        "unrestricted_integer_translation_fails_for_even_ties":
            nearest_even(3, 2) != 1 + nearest_even(1, 2),
    }
    require(all(controls.values()), "a negative control failed")
    return {
        "status": "PASS_ALL_SCALAR_TICK_RESIDUES",
        "old_word": OLD_WORD,
        "new_word": NEW_WORD,
        "clock": SPLIT_CLOCK,
        "source_role": 284,
        "target_role": 841,
        "chart": 127,
        "old": str(old),
        "split": [str(integral), str(tail)],
        "residues": d,
        "signed_cases": signed_cases,
        "rounded_comparisons": 2 * signed_cases,
        "integral_residues": integral_residues,
        "half_tie_residues": ties,
        "controls": controls,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original_combination", type=Path)
    parser.add_argument("lowered_combination", type=Path)
    paths = parser.parse_args()
    print(json.dumps(check(paths.original_combination, paths.lowered_combination), indent=2, sort_keys=True))
