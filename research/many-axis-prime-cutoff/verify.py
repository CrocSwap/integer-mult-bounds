"""Exact endpoint certificates for the new many-axis prime-supply domain."""

from dataclasses import dataclass, replace
from fractions import Fraction
from hashlib import sha256
import json
from math import factorial
from pathlib import Path


@dataclass(frozen=True)
class Certificate:
    power: int
    log2_upper: Fraction
    error_margin: Fraction
    quota_margin: Fraction
    error_derivative_gap: int
    quota_derivative_gap: int


def need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def exp_prefix(value: Fraction, degree: int) -> Fraction:
    need(0 <= value <= 7, "exponential argument outside finite domain")
    need(type(degree) is int and 0 <= degree <= 6, "invalid series degree")
    return sum((value**k / factorial(k) for k in range(degree + 1)), Fraction())


def endpoint(power: int, log2_upper: Fraction) -> Certificate:
    need(type(power) is int and 2 <= power <= 32, "invalid cutoff power")
    need(power % 2 == 0, "integer square-root certificate needs an even power")
    need(isinstance(log2_upper, Fraction), "logarithm bound must be rational")
    need(0 < log2_upper <= 1, "logarithm bound outside finite domain")
    ell = 1 << power
    z = 1 << (power // 2)
    return Certificate(
        power,
        log2_upper,
        Fraction(z, 4) - 7 - 671 * (power // 2) * log2_upper,
        Fraction(ell, 4) - 5 - 669 * power * log2_upper,
        z - 4 * 671,
        ell - 4 * 669,
    )


def validate(certificate: Certificate) -> None:
    expected = endpoint(certificate.power, certificate.log2_upper)
    need(certificate == expected, "altered endpoint certificate")
    need(exp_prefix(certificate.log2_upper, 3) > 2, "unproved log(2) bound")
    need(exp_prefix(Fraction(7), 6) > 480, "unproved log(480) bound")
    need(exp_prefix(Fraction(5), 3) > 24, "unproved log(24) bound")
    need(certificate.error_margin > 0, "prime-count error bound not established")
    need(certificate.quota_margin > 0, "prime quota bound not established")
    need(certificate.error_derivative_gap > 0, "error monotonicity not established")
    need(certificate.quota_derivative_gap > 0, "quota monotonicity not established")


def integer_endpoint(power: int) -> dict[str, int | bool]:
    """A second endpoint calculation uses e > 8/3 and integer powers only."""
    need(type(power) is int and 2 <= power <= 32, "invalid integer cutoff")
    need(power % 2 == 0, "invalid integer square root")
    z_power = power // 2
    exponent = (1 << z_power) // 4
    need(exp_prefix(Fraction(1), 3) == Fraction(8, 3), "wrong e lower bound")
    left = 8**exponent
    right = 480 * (1 << (671 * z_power)) * 3**exponent
    need(left > right, "integer error comparison failed")
    # e > 2 and 24 < 2^5 avoid constructing an ell/4-bit integer.
    need((1 << power) // 4 > 5 + 669 * power, "integer quota comparison failed")
    return {
        "power": power,
        "exponential_power": exponent,
        "left_bits": left.bit_length(),
        "right_bits": right.bit_length(),
        "strict_comparison": True,
    }


def rejected(call, *args) -> None:
    try:
        call(*args)
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def controls(certificate: Certificate) -> int:
    rejected(validate, endpoint(28, Fraction(7, 10)))
    rejected(integer_endpoint, 28)
    rejected(validate, endpoint(30, Fraction(2, 3)))
    rejected(validate, replace(certificate, error_margin=Fraction(1)))
    rejected(validate, replace(certificate, quota_margin=Fraction(1)))
    rejected(validate, replace(certificate, error_derivative_gap=0))
    rejected(validate, replace(certificate, quota_derivative_gap=0))
    rejected(endpoint, True, Fraction(7, 10))
    rejected(endpoint, 29, Fraction(7, 10))
    rejected(endpoint, 34, Fraction(7, 10))
    rejected(endpoint, 30, 0.7)
    rejected(exp_prefix, Fraction(8), 3)
    return 12


def main() -> None:
    certificate = endpoint(30, Fraction(7, 10))
    validate(certificate)
    integer_check = integer_endpoint(30)
    control_count = controls(certificate)
    root = Path(__file__).resolve().parent
    names = ("README.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py")
    hashes = {name: sha256((root / name).read_bytes()).hexdigest() for name in names}
    payload = {
        "status": "PASS_MANY_AXIS_PRIME_CUTOFF",
        "claim_type": "scoped proof with exact endpoint certificates",
        "old_cutoff": 1 << 32,
        "new_cutoff": 1 << certificate.power,
        "cutoff_reduction_factor": 4,
        "log2_upper": str(certificate.log2_upper),
        "error_log_upper": str(-certificate.error_margin),
        "quota_log_margin_lower": str(certificate.quota_margin),
        "error_derivative_gap": certificate.error_derivative_gap,
        "quota_derivative_gap": certificate.quota_derivative_gap,
        "integer_endpoint": integer_check,
        "rejected_controls": control_count,
        "package_sha256": hashes,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
