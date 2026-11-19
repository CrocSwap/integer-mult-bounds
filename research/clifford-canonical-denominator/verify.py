"""Recover the exact width-13 canonical denominator from the reported spectrum.

apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import gcd, isqrt, lcm
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
EXPECTED = 22742436009630709072767882717680300149753125


def require(predicate, message):
    if not predicate:
        raise ValueError(message)


def odd_part(n):
    return n // (n & -n)


def load_spectrum():
    raw = (ROOT / "sources/width13-spectrum.json").read_bytes()
    require(sha256(raw).hexdigest() == "d032d5e63820f4ffe246d21adcd8d272f04dfd635a6fc519c4a81a366ca41d49",
            "Changed PR7772 spectrum")
    data = json.loads(raw)
    levels = []
    for row in data["rows"]:
        degree = row["quotient_degree"]
        level = Fraction(*row["eigenvalue"])
        require(row["clifford_degree"] == 16 * degree, "Wrong defining-representation factor")
        require(row["regular_dimension"] == (16 * degree)**2, "Wrong regular multiplicity")
        require(level == Fraction(data["projective_order"] * row["multiplicity"],
                                  16**13 * 16 * degree), "Wrong normalized eigenvalue")
        levels.append((degree, level))
    require(len(levels) == 81 and len({v for _, v in levels}) == 52, "Width-13 levels")
    order = sum((16*d)**2 for d, _ in levels)
    require(data["width"] == 13 and order == data["projective_order"] == 12128668876800,
            "Incorrect width or projective order")
    return order, levels


def packet_trace(degree, count):
    # This rational packet on an order-17 element restricts to the sum of
    # trivial and complete nontrivial cyclotomic packets. Column orthogonality
    # and Cauchy-Schwarz give the independent absolute-value bound.
    radius = isqrt(17 * count)
    candidates = [v for v in range(-radius, radius+1) if (degree*count-v) % 17 == 0]
    require(len(candidates) == 1, "Packet character is ambiguous")
    return candidates[0]


def main():
    order, levels = load_spectrum()
    spectral_lcm = lcm(*(level.numerator for _, level in levels))
    weights = [Fraction(spectral_lcm * d, level) for d, level in levels]
    require(all(v.denominator == 1 for v in weights), "Nonintegral Fourier weight")
    common = gcd(*(16 * int(v) for v in weights), order * spectral_lcm)
    upper = odd_part(order * spectral_lcm // common)
    diagonal = sum((16*d)**2 / level for d, level in levels) / order

    packets = Counter(levels)
    witness = Fraction(0)
    characters = Counter()
    for (degree, level), count in packets.items():
        trace = packet_trace(degree, count)
        characters[trace] += 1
        # The #6208 actual representative has trace -1.
        witness -= 16 * degree * trace / (order * level)
    require(len(packets) == 80 and characters == {0: 71, 1: 5, -1: 4}, "Order-17 packets")
    require(diagonal == Fraction(8084515602799097617265541791880056776818688,
                                 7580812003210236357589294239226766716584375), "Diagonal entry")
    require(witness == Fraction(-309891064832, 22949540428586199553125), "Order-17 entry")
    lower = lcm(odd_part(diagonal.denominator), odd_part(witness.denominator))
    require(upper == lower == EXPECTED, "Denominator upper and lower certificates disagree")
    require(upper == 3 * odd_part(diagonal.denominator), "Diagonal-only control")
    require(upper == 8505 * spectral_lcm, "Eigenvalues-only control")
    print(f"PASS_CANONICAL_DENOMINATOR levels={len(levels)} packets={len(packets)} "
          f"diagonal={diagonal} order17={witness} odd_denominator={upper}")


if __name__ == "__main__":
    main()
