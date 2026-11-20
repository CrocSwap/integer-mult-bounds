"""Check the actual generated gate path against independent integer arithmetic."""

from fractions import Fraction
from math import prod
from pathlib import Path
from random import Random
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from product import Multiplier, digits, multiply_uniform, ordinal, production_precision
from root_gate_plan import compile_padded_root, load_compiler
from spectral import polar_root
from tensor_word import axis_packs
from word_product import word_product


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_control():
    rng = Random(7847)
    for k in (0, 1, 191, 192, 193, 256, 512, 1025):
        x, y = rng.getrandbits(k), rng.getrandbits(k)
        for a,b in ((x,y),(-x,y),(x,-y),(-x,-y),(0,-y)):
            require(word_product(a,b) == a*b, "Short signed product differs")
    sides = [32,64]*256
    packs = list(axis_packs(sides, 1536))
    require(sorted(j for pack in packs for j in pack) == list(range(512)), "Axis coverage differs")
    require(max(map(len,packs)) <= 512//(1537).bit_length(), "Native pack reserve is too small")
    require(all(len({sides[i] for i in pack}) == 1 for pack in packs), "Mixed H targets in one pack")
    require(multiply_uniform(-8198,175) == -1434650, "Finite uniform branch differs")
    require(production_precision(768,[12]*8) > 4*768, "Missing production guard")
    c = load_compiler(Path(__file__).resolve().parents[2])
    for turns,grid in (([Fraction(i,3) for i in range(3)],3),
                       ([Fraction(0),Fraction(1,2),Fraction(2,7)],None)):
        root,_ = polar_root(c,[Fraction(1)]*3,turns,30,phase_grid=grid)
        compile_padded_root(c,root.column,4,30,margin=root.accretivity)
    print("PASS_CONTROL_SIGNED_WORDS_AND_CUTS")


def regression(sides, full=False):
    m = Multiplier(sides)
    left, right = 741503,466013
    expected = [11811,10996,4152,868,77] + [0]*(m.size-5)
    result, coeff = m.multiply(left,right)
    require(result == 345550037539 and coeff == expected, "Pre-carry regression differs")
    require(m.transform.h_calls > 0, "The diagnostic omitted the physical transform")
    print(f"{left} x {right} = {result}; sides {sides}; records {prod(m.widths)}; "
          f"H calls/transform {m.transform.h_calls}; coefficients {coeff[:5]} + {m.size-5} zeros")
    if not full:
        return
    # Measure the error before integer rounding on an independent digit sequence.
    base = m.base
    a_digits, b_digits = [255,0,23], [193,245]
    a = sum(z*base**k for k,z in enumerate(a_digits))
    b = sum(z*base**k for k,z in enumerate(b_digits))
    xa,_ = m.operand(a)
    xb,_ = m.operand(b)
    raw = m.crt(m.convolution_grid(xa, xb), reverse=True)
    gain = (4*base*m.size)**2
    delta = 0
    for k in range(m.size):
        ref = sum(x*y for i,x in enumerate(a_digits) for j,y in enumerate(b_digits) if i+j == k)
        re, im = raw[ordinal(digits(k,m.sides),m.widths)]
        delta = max(delta, abs(re*gain - ref*m.grid.unit), abs(im*gain))
    require(2*delta < m.grid.unit, "An unrounded coefficient misses its integer")
    require(m.multiply(-a,b)[0] == -a*b and m.multiply(0,-7)[0] == 0,
            "Zero, sign or carry differs")
    try:
        m.multiply(base**(m.size-1),base)
    except ValueError as e:
        require("wrap" in str(e), "Unexpected wrap-control failure")
    else:
        raise ValueError("Accepted a wrapped linear convolution")
    print("Pre-round maximum real or imaginary coordinate error", Fraction(delta, m.grid.unit))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--odd-squares", action="store_true",
                        help="run the larger single product with 512 physical records")
    args = parser.parse_args()
    if args.odd_squares:
        regression((9,25))
    else:
        check_control()
        regression((3,5),full=True)
        regression((4,9))
        regression((5,7))
    print("PASS_DIRECT_CIRCULANT_PRODUCT")
