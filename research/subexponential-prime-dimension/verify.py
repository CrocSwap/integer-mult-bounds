#!/usr/bin/env python3
"""Exact endpoint certificates for a written prime-supply domain proof."""

from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def exponential_lower(value, degree):
    require(isinstance(value, Q) and value > 0, "positive rational required")
    require(type(degree) is int and 1 <= degree <= 10, "series degree outside cap")
    term = Q(1)
    total = term
    for index in range(1, degree + 1):
        term *= value / index
        total += term
    return total


def endpoint(root_bits, slope):
    require(type(root_bits) is int and 1 <= root_bits <= 32, "root size outside cap")
    require(isinstance(slope, Q) and slope > 0, "positive rational slope required")
    root = 1 << root_bits
    log_two_upper = Q(7, 10)
    log_root_upper = root_bits * log_two_upper
    decay = Q(1, 4) - slope * log_two_upper
    error = 7 + 3 * log_root_upper - decay * root
    error_derivative = Q(3, root) - decay
    quota = Q(root * root, 4) - 5 - 2 * slope * log_two_upper * root
    quota -= 2 * log_root_upper
    quota_derivative = Q(root, 2) - 2 * slope * log_two_upper - Q(2, root)
    require(decay > 0, "no positive error decay")
    require(error < 0 and error_derivative < 0, "error endpoint or monotonicity fails")
    require(quota > 0 and quota_derivative > 0, "quota endpoint or monotonicity fails")
    return error, error_derivative, quota, quota_derivative


def containment(root_bits, polynomial_degree):
    require(type(root_bits) is int and 1 <= root_bits <= 32, "root size outside cap")
    require(type(polynomial_degree) is int and 1 <= polynomial_degree <= 1000,
            "polynomial degree outside cap")
    root = 1 << root_bits
    margin = Q(root, 8) - Q(7, 10) - 2 * polynomial_degree * root_bits * Q(7, 10)
    derivative = Q(1, 8) - Q(2 * polynomial_degree, root)
    require(margin > 0 and derivative > 0, "polynomial containment certificate fails")
    return margin, derivative


def check_logarithms():
    bounds = ((Q(7, 10), 3, 2), (Q(7), 6, 480), (Q(5), 3, 24), (Q(1), 4, Q(8, 3)))
    values = []
    for argument, degree, target in bounds:
        value = exponential_lower(argument, degree)
        require(value > target, "strict exponential lower bound failed")
        values.append(str(value))
    # log(2)>1/2 follows in PROOF.md by integrating 1/t>1/2 on [1,2].
    return values


def reject_controls():
    cases = (("small cutoff", 8, Q(1, 4)),
             ("excessive dimension slope", 9, Q(1, 2)),
             ("zero slope", 9, Q(0)),
             ("Boolean root size", True, Q(1, 4)),
             ("oversized root", 33, Q(1, 4)),
             ("inexact slope", 9, 0.25))
    rejected = []
    for label, bits, slope in cases:
        try:
            endpoint(bits, slope)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError("accepted invalid certificate: " + label)
    for bits, degree in ((15, 334), (16, 1000), (16, True)):
        try:
            containment(bits, degree)
        except ValueError:
            rejected.append("containment " + str((bits, degree)))
        else:
            raise ValueError("accepted unsupported containment certificate")
    return rejected


def package_hashes(directory):
    names = ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {}
    for name in names:
        path = directory / name
        require(path.is_file() and not path.is_symlink(), "missing regular package file: " + name)
        require(path.stat().st_size <= 262144, "package file exceeds read cap")
        hashes[name] = sha256(path.read_bytes()).hexdigest()
    return hashes


def verify():
    logs = check_logarithms()
    primary = endpoint(9, Q(1, 4))
    require(primary == (Q(-25, 2), Q(-177, 2560), Q(326696, 5), Q(327227, 1280)),
            "stated endpoint fractions disagree")
    polynomial = containment(16, 334)
    require(polynomial[0] == Q(7097, 10), "stated containment margin disagrees")
    # Separate integer-power checks of the error and quota endpoints.
    require(8 ** 38 > 480 * 512 ** 3 * 3 ** 38, "integer error endpoint failed")
    require(3 * Q(512, 40) > 38, "integer error exponent rounding failed")
    require((1 << 18) - 1 > 5 + 256 + 18, "integer quota endpoint failed")
    # An enlarged-domain witness is encoded by exponents, without forming d or t.
    require(334 * 32 < 12000 <= (1 << 16) // 4, "strict domain enlargement failed")
    corroborated = 0
    for root_bits in range(9, 33):
        endpoint(root_bits, Q(1, 4))
        corroborated += 1
    controls = reject_controls()
    report = {"claim_type": "scoped mathematical proof with exact endpoint certificates",
              "ell_min": 1 << 18, "dimension_cap": "2^floor(sqrt(ell)/4)",
              "endpoint_fractions": [str(value) for value in primary],
              "polynomial_containment": [str(value) for value in polynomial],
              "logarithm_series_lower_values": logs, "dyadic_endpoints": corroborated,
              "rejected_controls": controls, "new_kappa": False,
              "package_sha256": package_hashes(Path(__file__).resolve().parent)}
    print(json.dumps(report, indent=2, sort_keys=True))
    print("PASS_SUBEXPONENTIAL_PRIME_DIMENSION endpoints=" + str(corroborated)
          + " controls=" + str(len(controls)) + " no_new_kappa")


if __name__ == "__main__":
    require(len(sys.argv) == 1, "this read-only verifier accepts no arguments")
    verify()
