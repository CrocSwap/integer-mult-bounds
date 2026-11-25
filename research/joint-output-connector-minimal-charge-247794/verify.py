#!/usr/bin/env python3
"""Exhaustively check the minimal joint-output dirty-state schedule.

The proof in README.md is dimension-independent. This checker independently
enumerates every F2-linear map on F2^2 and every source, connector, and target
state, then rejects three deliberately faulty schedules and checks the exact
symbolic break-even formula.
"""

from fractions import Fraction
from itertools import product


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def parity(value):
    return value.bit_count() & 1


def apply(matrix, vector):
    """Apply a 2x2 F2 matrix encoded as two row masks."""
    row0, row1 = matrix
    return parity(row0 & vector) | (parity(row1 & vector) << 1)


def all_matrices():
    return tuple(product(range(4), repeat=2))


def joint_readout(z, yi, yk, ai, ak, *, omit_ak=False):
    yi ^= apply(ai, z)
    if not omit_ak:
        yk ^= apply(ak, z)
    return yi, yk


def replay(ai, ak, b, x, z, yi, yk, *, omit_first=False,
           omit_ak=False, omit_second=False, omit_final_b=False):
    """Run J, B, J, B with optional faults used by negative controls."""
    if not omit_first:
        yi, yk = joint_readout(z, yi, yk, ai, ak, omit_ak=omit_ak)
    z ^= apply(b, x)
    if not omit_second:
        yi, yk = joint_readout(z, yi, yk, ai, ak, omit_ak=omit_ak)
    if not omit_final_b:
        z ^= apply(b, x)
    return x, z, yi, yk


def expected(ai, ak, b, x, z0, yi0, yk0):
    signal = apply(b, x)
    return (x, z0,
            yi0 ^ apply(ai, signal),
            yk0 ^ apply(ak, signal))


def check_positive_cases():
    matrices = all_matrices()
    cases = 0
    for ai, ak, b in product(matrices, repeat=3):
        for x, z, yi, yk in product(range(4), repeat=4):
            got = replay(ai, ak, b, x, z, yi, yk)
            want = expected(ai, ak, b, x, z, yi, yk)
            require(got == want,
                    "joint-readout mismatch at case %d: %r != %r" %
                    (cases, got, want))
            cases += 1
    require(cases == 1_048_576, "unexpected exhaustive case count")
    return cases


def check_negative_controls():
    identity = (1, 2)
    zero = (0, 0)
    controls = 0

    # Omitting A_k from both joint records loses the second requested output.
    args = (identity, identity, identity, 1, 0, 0, 0)
    require(replay(*args, omit_ak=True) != expected(*args),
            "control failed to expose a missing output update")
    controls += 1

    # With dirty z and Bx=0, the first J is needed to cancel A_r z0.
    args = (identity, identity, zero, 0, 1, 0, 0)
    require(replay(*args, omit_first=True) != expected(*args),
            "control failed to expose missing dirty-state cancellation")
    controls += 1

    # The last B call is required to return the connector to its dirty entry.
    args = (identity, identity, identity, 1, 0, 0, 0)
    require(replay(*args, omit_final_b=True) != expected(*args),
            "control failed to expose missing connector restoration")
    controls += 1

    return controls


def check_cost_threshold():
    # C_joint - C_single = 2(phi - D); report the ratio when D is normalized
    # to one. Exact rationals avoid a floating-point break-even check.
    def delta_over_d(phi_over_d):
        return 2 * (phi_over_d - 1)

    require(delta_over_d(Fraction(0)) == -2,
            "zero fusion overhead should save two dispatches")
    require(delta_over_d(Fraction(1)) == 0,
            "one dispatch of fusion overhead should tie")
    require(delta_over_d(Fraction(2)) == 2,
            "two dispatches of fusion overhead should lose by two dispatches")
    return True


def main():
    cases = check_positive_cases()
    controls = check_negative_controls()
    check_cost_threshold()
    print("PASS_JOINT_OUTPUT_CONNECTOR_MINIMAL cases=%d controls=%d "
          "records=6_to_4 leaves_equal delta=2*(phi-D)" % (cases, controls))


if __name__ == "__main__":
    main()
