#!/usr/bin/env python3
"""Separate Fourier-character and rational matrix audit; imports no primary code."""
from fractions import Fraction as F
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def add(a, b):
    return a[0] + b[0], a[1] + b[1]


def times(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def polynomial(a, b):
    out = [(F(0), F(0)) for _ in range(4)]
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            k = (i+j) % 4
            out[k] = add(out[k], times(x, y))
    return out


def audit():
    # Recover the spatial convolution kernel from its independent characters.
    # Orthogonality is proved for every width in PROOF.md. This loop is finite.
    kernels = coefficients = 0
    for dimension in range(1, 7):
        size = 2**dimension
        for mask in range(1, size):
            for sign in (-1, 1):
                for shift in range(size):
                    real = imaginary = 0
                    for frequency in range(size):
                        character = -1 if (frequency & shift).bit_count() % 2 else 1
                        if (frequency & mask).bit_count() % 2:
                            imaginary += sign * character
                        else:
                            real += character
                    expected = ((size//2, sign*size//2) if shift == 0 else
                                (size//2, -sign*size//2) if shift == mask else (0, 0))
                    require((real, imaginary) == expected, "inverse Walsh kernel")
                    coefficients += 1
                kernels += 1

    zero = (F(0), F(0)); one = (F(1), F(0))
    q = [zero, one, zero, zero]
    qi = [zero, zero, zero, one]
    unit = [one, zero, zero, zero]
    lambdas = {}
    for sign in (-1, 1):
        lambdas[sign] = [(F(1,2), F(sign,2)), zero,
                         (F(1,2), F(-sign,2)), zero]
        normalized = polynomial(lambdas[sign], qi)
        require(polynomial(normalized, normalized) == unit, "normalized central involution")
    require(polynomial(lambdas[1], lambdas[-1]) == unit, "normalizer inverse")

    # Independent dense real matrix for the two-point butterfly. Its first two
    # rows are exactly the eight real arithmetic operations in the lowering.
    numerical_cases = 0
    for sign in (-1, 1):
        matrix = [[F(1,2), F(-sign,2), F(1,2), F(sign,2)],
                  [F(sign,2), F(1,2), F(-sign,2), F(1,2)],
                  [F(1,2), F(sign,2), F(1,2), F(-sign,2)],
                  [F(-sign,2), F(1,2), F(sign,2), F(1,2)]]
        require(all(sum(abs(x) for x in row) == 2 for row in matrix), "real sup norm two")
        require(all(sum(abs(x) for x in row[2:]) == 1 for row in matrix[:2]), "scratch residual norm one")
        for a in range(-2, 3):
            for b in range(-2, 3):
                for c in range(-2, 3):
                    for d in range(-2, 3):
                        out = [sum(x*y for x,y in zip(row, (a,b,c,d))) for row in matrix]
                        lowered = [F(a-sign*b+c+sign*d, 2), F(b+sign*a+d-sign*c, 2),
                                   F(c-sign*d+a+sign*b, 2), F(d+sign*c+b-sign*a, 2)]
                        require(out == lowered, "independent Gaussian pair arithmetic")
                        # Round only final halves down to an integer grid.
                        rounded = [x.numerator // x.denominator for x in lowered]
                        require(max(abs(x-y) for x,y in zip(out, rounded)) < 1, "final-grid rounding error")
                        numerical_cases += 1

    # Tensoring the width-one normalizers would return -1 on two odd central
    # factors. The global normalizer returns +1 on their product -1.
    local_odd = (0, 1)
    tensor_value = times(local_odd, local_odd)
    global_value = (1, 0)
    require(tensor_value == (-1, 0) and tensor_value != global_value, "two-factor tensor trap")
    # Misdeclaring i as a columnwise phase also fails at width two.
    require(times((0,1), (0,1)) != (0,1), "scalar phase stays outside tensor powers")
    result = {"fourier_kernels": kernels, "fourier_coefficients": coefficients,
              "exact_pair_inputs": numerical_cases, "real_sup_norm": 2,
              "scratch_residual_sup_norm": 1, "tensor_trap": True,
              "global_phase_trap": True, "normalizer_inverse": True,
              "normalized_involutions": 2}
    expected = HERE / "RESULT.json"
    if expected.exists():
        require(result == json.loads(expected.read_text())["independent"], "frozen independent result")
    print(json.dumps(result, sort_keys=True))
    print("PASS_INDEPENDENT_GLOBAL_LAMBDA")
    return result


if __name__ == "__main__":
    try:
        audit()
    except Exception as exc:
        print("FAIL_INDEPENDENT_GLOBAL_LAMBDA:", exc, file=sys.stderr)
        raise SystemExit(1) from exc
