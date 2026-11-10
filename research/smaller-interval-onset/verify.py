"""Check the new rational onset certificate, without a predecessor replay."""

from fractions import Fraction
from hashlib import sha256
import json
from math import factorial
from pathlib import Path
import sys


ONSET_EXPONENT = 751_000_000
PACKAGE_FILES = (
    "README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json",
    "verify.py", "CODE-SAFETY.md",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def remainder_gates() -> dict[str, str]:
    """Certify endpoint and derivative bounds used on the whole w >= 60 ray."""
    w0 = 60
    width = 5000
    majorant_width = 5001
    u0 = 2**40
    taylor = sum(Fraction(3**j, factorial(j)) for j in range(5))
    gates = {
        "window coefficient": Fraction(width) + Fraction(4, w0)
        < majorant_width,
        "inverse square-root coefficient": 3 * majorant_width
        + Fraction(width**2, 4) < 2**23,
        "positive Taylor lower bound": taylor == Fraction(131, 8)
        and taylor > 16,
        "first logarithmic derivative": Fraction(1, w0) - Fraction(1, 2) < 0,
        "first endpoint": Fraction(w0, 2**17) < Fraction(1, 2048),
        "second logarithmic derivative": Fraction(2, w0) + Fraction(1, 2)
        - Fraction(u0, 640) < 0,
        "auxiliary decreasing function": u0 > 320,
        "second endpoint coefficient": majorant_width * w0**2 < 2**25,
        "second exponential power": Fraction(u0, 320) > 2**31,
        "second endpoint tail": 65 - 2**31 < -11,
        "combined remainder": 2 * Fraction(1, 2048) == Fraction(1, 1024),
        "Gaussian normalizer": 2 * 4 * 3 < 5**2,
        "source domain on ray": 2**80 > 1296,
    }
    for name, passed in gates.items():
        require(passed, name)
    return {
        "taylor_lower": str(taylor),
        "first_endpoint_upper": str(Fraction(w0, 2**17)),
        "scaled_error_coefficient": str(Fraction(1025, 1024)),
        "rational_gates": str(len(gates)),
    }


def onset_gate(exponent: int) -> Fraction:
    """Apply the proved sufficient bound; failure is not a theorem counterexample."""
    require(type(exponent) is int and 100 <= exponent <= 10**12,
            "onset exponent outside the certificate domain")
    log_lower = Fraction(2 * exponent, 3)
    require(log_lower >= 60, "remainder ray is unavailable")
    error_upper = Fraction(5 * 1025, 1024) / log_lower
    require(error_upper < Fraction(1, 10**8),
            "coarse sufficient error estimate exceeds the target")
    return error_upper


def rejecting_controls() -> int:
    for exponent in (99, 750_000_000):
        rejected = False
        try:
            onset_gate(exponent)
        except ValueError:
            rejected = True
        require(rejected, "insufficient onset certificate accepted")
    return 2


def package_hashes() -> dict[str, str]:
    """Bound input reads and report hashes of the actual reviewed artifact."""
    here = Path(__file__).resolve().parent
    hashes = {}
    for name in PACKAGE_FILES:
        with (here / name).open("rb") as source:
            content = source.read(65537)
        require(len(content) <= 65536, "package file exceeds 64 KiB")
        hashes[name] = sha256(content).hexdigest()
    return hashes


def main() -> None:
    require(len(sys.argv) == 1, "this verifier takes no arguments")
    gates = remainder_gates()
    error = onset_gate(ONSET_EXPONENT)
    slack = 2048 * ONSET_EXPONENT - 15375 * 10**8
    require(slack == 548_000_000 and slack > 0, "onset cross-product slack")
    require(10**12 > 1331 * ONSET_EXPONENT, "exponent comparison")
    receipt = {
        "status": "PASS_SMALLER_INTERVAL_ONSET",
        "claim_type": "scoped analytic implication from cited inequalities",
        "onset_encoding": f"2^{ONSET_EXPONENT}",
        "normalized_error_upper": str(error),
        "target": "1/100000000",
        "onset_cross_product_slack": slack,
        "remainder": gates,
        "rejecting_sufficient_certificate_controls": rejecting_controls(),
        "external_premises_replayed": False,
        "package_sha256": package_hashes(),
    }
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
