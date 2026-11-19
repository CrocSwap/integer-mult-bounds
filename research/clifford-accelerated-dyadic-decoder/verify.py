"""Generate and check both width-13 schedules using exact rational arithmetic.

apoursh with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256
from math import gcd, lcm, prod
from pathlib import Path
import argparse
import json

ROOT = Path(__file__).resolve().parent


def require(condition, error):
    if not condition:
        raise ValueError(error)


def levels():
    raw = (ROOT / "sources/width13-spectrum.json").read_bytes()
    require(sha256(raw).hexdigest() ==
            "d032d5e63820f4ffe246d21adcd8d272f04dfd635a6fc519c4a81a366ca41d49",
            "Changed PR 7772 spectrum")
    source = json.loads(raw)
    order = source["projective_order"]
    rows = source["rows"]
    values = set()
    for row in rows:
        degree = 16 * row["quotient_degree"]
        value = Fraction(*row["eigenvalue"])
        require(row["clifford_degree"] == degree and row["regular_dimension"] == degree**2,
                "Incorrect Clifford multiplicity")
        require(value == Fraction(order * row["multiplicity"], 16**13 * degree),
                "Incorrect normalized eigenvalue")
        values.add(value)
    require(sum(row["regular_dimension"] for row in rows) == order == 12128668876800,
            "Incomplete regular representation")
    require(source["width"] == 13 and len(rows) == 81 and len(values) == 52,
            "Wrong width or number of levels")
    return sorted(values)


def ceil_log2(value):
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    return exponent + int(value > Fraction(2)**exponent)


def dyadic_factors(values):
    schedule = []
    for x in reversed(values):
        sensitivity = x * prod(abs(1 - x/y) for y in values if y != x)
        separation = max(64*y/abs(1 - y/x) for y in values if y != x)
        bits = max(0, ceil_log2((1 << 128) * sensitivity), ceil_log2(separation))
        schedule.append([round((1 << bits)/x), bits])
    return schedule


def evaluate(coefficients, x):
    result = 0
    for c in coefficients:
        result = result*x + c
    return result


def alternating_polynomial(nodes):
    """Power-basis integer polynomial in t=2^36 x with the prescribed root set."""
    bottom, *positive = nodes
    # The common product and synthetic division give each Lagrange basis.
    product = [1]
    for z in positive:
        product = [a-z*b for a, b in zip(product+[0], [0]+product)]
    coefficients = [Fraction(0)] * len(positive)
    for j, z in enumerate(positive):
        slope = prod(z-w for w in positive if w != z)
        weight = Fraction((-1)**j * bottom, (bottom-z) * slope)
        quotient = [1]
        for c in product[1:-1]:
            quotient.append(c + z * quotient[-1])
        require(product[-1] + z*quotient[-1] == 0, "Synthetic division remainder")
        coefficients = [a + weight*b for a, b in zip(coefficients, quotient)]
    common = lcm(*(c.denominator for c in coefficients))
    integers = [int(c*common) for c in coefficients]
    divisor = gcd(*integers)
    return [a//divisor for a in integers]


def optimal_factors(values):
    scale = lcm(*(x.denominator for x in values))
    nodes = [int(scale*x) for x in values]
    coefficients = alternating_polynomial(nodes)
    require(scale == 2**36 and len(coefficients) == 51 and coefficients[0] != 0,
            "Expected 50 separating roots")
    bits = 192
    unit = scale << bits
    # At u>0 the sign of u^50 R(unit/u) locates the reciprocal root
    # on the 2^-192 grid without evaluating an algebraic number.
    reciprocal = [c * unit**j for j, c in enumerate(reversed(coefficients))]
    numerators = []
    for low, high in zip(nodes[1:], nodes[2:]):
        at_high = evaluate(coefficients, high)
        require(at_high * evaluate(coefficients, low) < 0, "Missing alternating roots")
        left, right = unit//high, -(-unit//low)
        while right-left > 1:
            middle = (left+right)//2
            # Every tested midpoint lies strictly inside (unit/high, unit/low).
            value = evaluate(reciprocal, middle)
            if value == 0:
                left = middle
                break
            if (value > 0) == (at_high > 0):
                left = middle
            else:
                right = middle
        numerators.append(left)
    return list(reversed(numerators))


def representation(values):
    return {
        "width": 13,
        "target_contraction_bits": 128,
        "dyadic_steps_numerator_and_fraction_bits": dyadic_factors(values),
        "norm_optimal_dyadic_fraction_bits": 192,
        "norm_optimal_dyadic_numerators": optimal_factors(values),
        "norm_optimal_final_reciprocal": [values[0].denominator, values[0].numerator],
    }


def residuals(steps, values):
    return [prod(1-alpha*x for alpha in steps) for x in values]


def extrapolation_weight_sum(nodes):
    return sum(prod(abs(y/(y-x)) for y in nodes if y != x) for x in nodes)


def audit(receipt, values):
    first = receipt["dyadic_steps_numerator_and_fraction_bits"]
    steps = [Fraction(n, 1 << b) for n, b in first]
    require(len(steps) == 52 and steps == sorted(steps) and steps[0] > 0,
            "Unstable ordering")
    peak = max(map(abs, residuals(steps, values)))
    require(Fraction(1, 2**130) < peak < Fraction(1, 2**129), "Dyadic residual")
    fractions = [b for _, b in first]
    require((min(fractions), max(fractions), sum(fractions)) == (69, 266, 5676),
            "Dyadic scalar precision")
    used = sum(a.denominator.bit_length()-1 for a in steps)
    require(used == 5627, "Reduced denominator budget")
    optimal = [Fraction(n, 1 << 192) for n in receipt["norm_optimal_dyadic_numerators"]]
    optimal.append(Fraction(*receipt["norm_optimal_final_reciprocal"]))
    require(len(optimal) == 51 and optimal == sorted(optimal) and optimal[0] > 0,
            "Unstable optimum ordering")
    remaining = residuals(optimal, values)
    peak = max(map(abs, remaining))
    require(remaining[0] == 0 and Fraction(1, 2**59) < peak < Fraction(1, 2**58),
            "Norm-optimal residual")
    require(1/values[0] - 1/values[1] > 3 and 1/values[0] < 10,
            "Insufficient gap or wrong norm floor")
    full = extrapolation_weight_sum(values)
    most = extrapolation_weight_sum(values[:21] + values[22:])
    require(2**60 < full < 2**61 and 2**52 < most < 2**53,
            "Polynomial degree lower certificates")
    print("PASS_ACCELERATED_DECODERS dyadic_steps=52 dyadic_residual<2^-129 "
          "dyadic_reduced_fraction_bits_sum=5627 optimal_steps=51 "
          "optimal_residual<2^-58 optimal_odd_denominator=470624175 "
          "degree_51_floor>2^-61 degree_50_floor>2^-53")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-schedule", action="store_true",
                        help="write the reproducible schedule to stdout")
    args = parser.parse_args()
    values = levels()
    receipt = representation(values)
    if args.emit_schedule:
        print(json.dumps(receipt, indent=2))
    else:
        require(json.loads((ROOT / "SCHEDULE.json").read_text()) == receipt,
                "Committed schedule differs from reconstruction")
        audit(receipt, values)


if __name__ == "__main__":
    main()
