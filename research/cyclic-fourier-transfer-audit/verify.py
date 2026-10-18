#!/usr/bin/env python3
"""Exact evidence for a scoped Fourier-transfer estimate; not a formal proof."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
from math import gcd
import argparse
import importlib.util
import json
import random
import sys

HERE = Path(__file__).resolve().parent
SEED = 60
COEFFICIENT = F(44, 7)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_log2(x):
    """Smallest integer k such that the positive rational x is <= 2**k."""
    x = F(x)
    require(x > 0, "log input must be positive")
    n, d = x.numerator, x.denominator
    k = n.bit_length() - d.bit_length()
    below = n <= (d << k) if k >= 0 else (n << -k) <= d
    return k if below else k + 1


def power2(k):
    return F(2**k) if k >= 0 else F(1, 2**(-k))


def squared_bound(delta, derivative):
    delta, derivative = F(delta), F(derivative)
    require(delta > 0 and derivative >= 0, "invalid circle/derivative bounds")
    return 1 / delta**2 + COEFFICIENT * derivative / delta**3


def inherited_bound(delta, derivative):
    return 1 / delta + 2 * derivative / delta**2


def prime_power(r):
    if type(r) is not int or r < 2:
        return False
    p = next((d for d in range(2, r+1) if r % d == 0), r)
    while r % p == 0:
        r //= p
    return r == 1


def prime_power_budgets():
    out = []
    for r in range(3, 65):
        if not prime_power(r):
            continue
        n = r - 1
        degree = sum(gcd(k, r) == 1 for k in range(1, r))
        height = 2**r - 1
        reciprocal_delta = 2*r*n*height**(n*degree - 1)
        delta = F(1, reciprocal_delta)
        derivative = F(n*height, r)
        old = inherited_bound(delta, derivative)
        square = squared_bound(delta, derivative)
        t = derivative / delta
        require(t > F(4, 7), "outside strict improvement region")
        require(old**2 > square, "new bound is not strictly smaller")
        require(old**2 - square == 4*t*(t-F(4, 7))/delta**2,
                "comparison identity failed")
        old_bits = ceil_log2(old)
        new_bits = (ceil_log2(square)+1)//2
        require(power2(old_bits-1) < old <= power2(old_bits), "old bit ceiling")
        require(power2(2*new_bits-2) < square <= power2(2*new_bits),
                "new square-root bit ceiling")
        out.append(dict(radix=r, cyclotomic_degree=degree,
                        old_log2_ceiling=old_bits, new_log2_ceiling=new_bits,
                        ceiling_reduction=old_bits-new_bits))
    return out


def sequence_check(coefficients, coefficient=COEFFICIENT, include_constant=True,
                   omit_negative_derivative=False):
    """Exact squared comparison for finite nonnegative rational magnitudes."""
    mass = sum(coefficients.values(), F(0))
    energy = sum((a*a for a in coefficients.values()), F(0))
    derivative_energy = sum((k*k*a*a for k, a in coefficients.items()
                             if not omit_negative_derivative or k >= 0), F(0))
    gap = mass**2 - (energy if include_constant else 0)
    return gap <= 0 or gap**2 <= coefficient**2 * energy * derivative_energy


def sequence_evidence():
    fixtures = [{}, {0:F(1)}, {-7:F(3, 5)}, {0:F(1), 1:F(1)}]
    for width in (1, 2, 3, 4, 8, 16, 32, 64):
        for shift in (-3, 0, 2):
            for shape in range(4):
                fixtures.append({k+shift: (F(1) if shape == 0 else
                    F(1, 1+abs(k)) if shape == 1 else
                    F(1, 1+k*k) if shape == 2 else
                    F(1+(k % 3), 2+abs(k))) for k in range(-width, width+1)})
    rng = random.Random(SEED)
    for _ in range(100):
        fixtures.append({k:F(rng.randrange(0, 10), rng.randrange(1, 12))
                         for k in range(-rng.randrange(1, 12), rng.randrange(1, 12))})
    rng.shuffle(fixtures)
    for i, c in enumerate(fixtures):
        require(sequence_check(c), f"finite Fourier inequality failed: {i}")
    require(not sequence_check({0:F(1)}, include_constant=False),
            "omitted zero-mode control was not detected")
    require(not sequence_check({0:F(1), 1:F(1)}, coefficient=F(1)),
            "underpriced derivative control was not detected")
    require(not sequence_check({-1:F(1), 0:F(1)}, omit_negative_derivative=True),
            "negative-frequency derivative omission was not detected")
    return {"finite_sequences":len(fixtures), "coefficient":"44/7",
            "controls_rejected":["omitted_zero_mode", "underpriced_derivative",
                                 "omitted_negative_frequency_derivative"]}


def check_sources(root):
    manifest = json.loads((HERE / 'SOURCE.json').read_text())
    for name, digest in manifest['files'].items():
        require(sha256((root / name).read_bytes()).hexdigest() == digest,
                f"pinned source changed: {name}")
    return len(manifest['files'])


def check_receipt(actual, expected):
    require(json.dumps(actual, sort_keys=True) == json.dumps(expected, sort_keys=True),
            'committed evidence differs')


def run():
    spec = importlib.util.spec_from_file_location('independent_inverse_oracle', HERE / 'oracle.py')
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return {"status":"PASS_CYCLIC_FOURIER_TRANSFER_AUDIT", "assignment_seed":SEED,
            "formula":"norm_squared <= delta^-2 + (44/7)*M*delta^-3",
            "fourier_sequences":sequence_evidence(),
            "prime_power_budgets":prime_power_budgets(),
            "finite_inverse_oracle":module.run(),
            "scope":"Written proof establishes the uniform transfer. Finite evidence tests arithmetic and implementations; no new kappa or paid inversion algorithm."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--output', type=Path, help='Create a new receipt; never overwrite.')
    ap.add_argument('--source-root', type=Path, help='Also verify pinned repository source bytes.')
    args = ap.parse_args()
    require(args.output is None or not args.output.exists(),
            'output already exists; refusing to overwrite')
    if args.source_root is not None:
        check_sources(args.source_root.resolve())
    actual = run()
    if args.output is not None:
        with args.output.open('x') as stream:
            json.dump(actual, stream, indent=2)
            stream.write('\n')
    else:
        expected = json.loads((HERE / 'EXPECTED.json').read_text())
        check_receipt(actual, expected)
    print(actual['status'])
    print(f"{len(actual['prime_power_budgets'])} prime-power budgets; "
          f"{actual['fourier_sequences']['finite_sequences']} exact Fourier sequences")


if __name__ == '__main__':
    main()
