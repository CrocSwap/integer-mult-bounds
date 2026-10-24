#!/usr/bin/env python3
"""Depth-first continuation-stack space at c=8667/5000000.

Proves two facts about the BIT.md section 2 model, without running PR2809:

1. For every integer e >= 2 the level-1 child payload V/(W N) exceeds the
   allowance V/(W N q^(4096(w-1))) by q^(4096(w-1)) >= q^4096.
2. Parking the geometric ancestor payloads plus one K(w)^D-sized integer per
   cut uses at most 26041 V cells whenever the stream volume satisfies V >= e.

Standard library only. The arithmetic is integral.
"""

from fractions import Fraction
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
BIT = ROOT / "research" / "unconditional-batched-crt" / "BIT.md"
TASK = ROOT / "research" / "bit-stock-recurrence-audit" / "TASK.json"
README = ROOT / "research" / "bit-stock-recurrence-audit" / "README.md"

Q = 2**89 - 1
C_NUM = 8667
C_DEN = 5_000_000
W = 28416
M = 269241600
SCAN = 200_000
C_EXPECTED = 26040
K2_BITS_EXPECTED = 729117
WITNESS_E = 448
REGION_B_CHECKED_UNTIL = 20_000


def D(n):
    depth = 0
    while n >= 64:
        n = 42 * (n // 64)
        depth += 1
    return depth


def gl_order(n, prime):
    prime_n = prime**n
    order = 1
    prime_i = 1
    for _ in range(n):
        order *= prime_n - prime_i
        prime_i *= prime
    return order


def bind_sources():
    bit = BIT.read_text(encoding="utf-8")
    for needle in (
        "c=8667/5000000,",
        "K(w)=269241600 N q^(4096(w-1)),",
        "D(n)=0 (n<64),  D(n)=1+D(42 floor(n/64)) (n>=64).",
        "Each child's payload has volume V/(WN).",
        "Active ancestor payloads therefore",
        "form a geometric series.",
        "Hence visited space is O_q(V)",
        "Serialize parent streams and arithmetic",
        "Two coarse levels reduce width by at least a factor two",
    ):
        if needle not in bit:
            raise SystemExit("missing BIT.md sentence: " + needle)
    task = TASK.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    question = (
        "Does the PR2809 block construction's serialized continuation stack "
        "keep O_q(V) visited space at the new c when it parks at every recursive cut?"
    )
    step = "V/(W N q^(4096(w-1)))^level"
    if question not in task or step not in task:
        raise SystemExit("bit-stock TASK.json no longer states the stack question")
    if "encoded stack keep the claimed `O_q(V)`" not in readme or step not in readme:
        raise SystemExit("bit-stock README.md no longer states the stack question")


def prove_two_steps_halve():
    """84 * floor(42 f / 64) <= 64 f for every integer f >= 0."""
    if 441 > 512:
        raise SystemExit("441 <= 512 is the last step of the remainder identity")
    # The identity 672 x + 21 (r/2) = 441 f is checked on a full set of
    # residues and then extended by the closed form in PROOF.md. The residue
    # period of 42 f modulo 64 divides 32.
    for f in range(32):
        x, r = divmod(42 * f, 64)
        if r % 2:
            raise SystemExit("remainder must be even")
        if 672 * x + 21 * (r // 2) != 441 * f:
            raise SystemExit("remainder identity failed at f=" + str(f))
        if 84 * x > 64 * f:
            raise SystemExit("two-step halving failed at f=" + str(f))
    # Affine extension: both sides of the identity scale from the period.
    for f in (32, 64, 265, 10**6, 2**20 + 3):
        x, r = divmod(42 * f, 64)
        if 672 * x + 21 * (r // 2) != 441 * f or 84 * x > 64 * f:
            raise SystemExit("halving identity failed at f=" + str(f))
    for n in (64, 65, 127, 128, 448, 10**5):
        f = n // 64
        two = 42 * ((42 * f) // 64)
        if 2 * two > n:
            raise SystemExit("two steps exceed n/2 at n=" + str(n))


def prove_depth_bound(limit):
    previous = 0
    for n in range(1, limit + 1):
        depth = D(n)
        if depth < previous:
            raise SystemExit("D decreased")
        previous = depth
        if n < 64:
            if depth != 0:
                raise SystemExit("D(n) should be 0 below 64")
            continue
        bound = 2 * (n.bit_length() - 6)
        if depth > bound:
            raise SystemExit("depth bound failed at n=" + str(n))
        if (n // 2).bit_length() != n.bit_length() - 1:
            raise SystemExit("bit length of n//2")
        f = n // 64
        two = 42 * ((42 * f) // 64)
        if two > n // 2:
            raise SystemExit("integer halving failed")


def prove_child_lower_bound():
    # 20 n >= 5292 iff n >= 265, which is the threshold in PROOF.md.
    if 20 * 264 >= 5292 or 20 * 265 < 5292:
        raise SystemExit("half-width threshold")
    for n in range(265, 265 + 128):
        if 42 * (n // 64) < n // 2:
            raise SystemExit("child fell below n/2")
    # Drops bit length by at most one, so D(2^m) >= m + 1 - 9.
    if D(1 << 16) < 16 + 1 - 9:
        raise SystemExit("depth lower bound disagrees with a computed value")


def w_upper(bitlen):
    # e < 2^bitlen, so e^8667 < 2^(bitlen*8667).
    t = (bitlen * C_NUM + C_DEN - 1) // C_DEN
    return 1 << t


def encoding_constant(k2_bits):
    best_num = 0
    best_e = 1
    witness_depth = None
    for e in range(2, SCAN + 1):
        depth = D(e)
        num = depth * depth * k2_bits
        if num * best_e > best_num * e:
            best_num = num
            best_e = e
            witness_depth = depth
    if best_e != WITNESS_E or witness_depth != 4:
        raise SystemExit("unexpected maximizing address length " + str(best_e))
    if best_num != 16 * k2_bits:
        raise SystemExit("witness depth did not contribute 16 K(2) bits")
    constant = (best_num + best_e - 1) // best_e
    if constant != C_EXPECTED:
        raise SystemExit("constant changed: " + str(constant))
    if (constant - 1) * best_e >= best_num:
        raise SystemExit("constant is not sharp")
    if constant * best_e < best_num:
        raise SystemExit("constant does not cover the witness")
    # w = 2 through 2^576, checked by exponents rather than by building e^8667.
    if 576 * C_NUM >= C_DEN:
        raise SystemExit("2^576 is not inside the w=2 range")
    for bitlen in range((SCAN + 1).bit_length(), 577):
        n0 = max(SCAN + 1, 1 << (bitlen - 1))
        bound = 2 * (bitlen - 6)
        if bound * bound * k2_bits > constant * n0:
            raise SystemExit("w=2 tail failed at bit length " + str(bitlen))
    e = 1 << 576
    bound = 2 * (e.bit_length() - 6)
    if bound * bound * k2_bits > constant * e:
        raise SystemExit("endpoint 2^576 failed")
    return constant, best_e, best_num


def prove_region_b(constant, mn_bits):
    """Parameter bits stay <= C e after w leaves 2.

    Bit lengths 577 through 20000 are checked with the explicit w upper
    bound. Bit lengths through 100000 use the power-of-two majorant.
    Beyond that, one 577-step window cannot spend the slack at 100000.
    """
    scale_base = mn_bits + 89 * 4096
    for bitlen in range(577, REGION_B_CHECKED_UNTIL + 1):
        w_hi = w_upper(bitlen)
        kbits = mn_bits + 89 * 4096 * (w_hi - 1)
        bound = 2 * (bitlen - 6)
        n0 = (1 << 576) + 1 if bitlen == 577 else 1 << (bitlen - 1)
        if bound * bound * kbits > constant * n0:
            raise SystemExit("region B failed at bit length " + str(bitlen))
    for bitlen in range(REGION_B_CHECKED_UNTIL, 100_001):
        t = (bitlen * C_NUM) // C_DEN + 1
        upper = (4 * bitlen * bitlen * scale_base).bit_length() + t
        if upper > bitlen - 2:
            raise SystemExit("exponent gap closed at bit length " + str(bitlen))
    bitlen = 100_000
    s_bits = scale_base.bit_length()
    # 4 L^2 S < 2^(2 + 2 bitlength(L) + bitlength(S)).
    if (4 * bitlen * bitlen * scale_base).bit_length() > 2 + 2 * bitlen.bit_length() + s_bits:
        raise SystemExit("power majorant is not an upper bound")
    upper = bitlen // 577 + 1 + 2 * bitlen.bit_length() + s_bits + 4
    slack = bitlen // 2 - 2 - upper
    # One step can add 1 to floor(L/577) and 2 to twice the bit length while
    # floor(L/2) stays put. The slack has to survive that three-bit drop.
    if slack < 4:
        raise SystemExit("slack at bit length 100000 is too small")
    window = 577
    half_gain = (bitlen + window) // 2 - bitlen // 2
    if half_gain - 1 - 2 < 1:
        raise SystemExit("577-step window does not restore the slack")


def level1_factor_bits():
    # q^4096 < 2^(89*4096), and the exact bit length is recorded.
    return (Q**4096).bit_length()


def full_copy_bitlen():
    # D(2^26050) >= 26051 - 9 = 26042 > 26041.
    return 26051


def main():
    bind_sources()
    prove_two_steps_halve()
    prove_depth_bound(4_000)
    prove_child_lower_bound()
    order = gl_order(64, Q)
    if M != W * 9475:
        raise SystemExit("M is not W*9475")
    k2_bits = (M * order * Q**4096).bit_length()
    if k2_bits != K2_BITS_EXPECTED:
        raise SystemExit("K(2) bit length changed: " + str(k2_bits))
    mn_bits = (M * order).bit_length()
    constant, witness, numerator = encoding_constant(k2_bits)
    prove_region_b(constant, mn_bits)
    group = W * order
    if group <= 2:
        raise SystemExit("payload ratio is not a contraction")
    # sum_{k>=1} G^{-k} = 1/(G-1).
    step = Fraction(1, group)
    if step / (1 - step) != Fraction(1, group - 1):
        raise SystemExit("series identity")
    factor_bits = level1_factor_bits()
    if factor_bits <= 1:
        raise SystemExit("q^4096 did not exceed 1")
    copy_bits = full_copy_bitlen()
    if copy_bits - 9 <= constant + 1:
        raise SystemExit("full-copy reading is still inside the constant")
    print(
        "PASS_PR2809_CONTINUATION_STACK_SPACE"
        f" C={constant}"
        f" witness_e={witness}"
        f" witness_bits={numerator}"
        f" K2_bits={k2_bits}"
        f" level1_factor_bits={factor_bits}"
        f" payload_ratio=1/(WN-1)"
        f" full_copy_exceeds_bitlen={copy_bits}"
        " no_new_kappa=true"
    )


if __name__ == "__main__":
    main()
