"""Check both suppliers and their shared conditional application."""

from fractions import Fraction
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0, str(PACKAGE))
from bit_application import verify as verify_bit


def compare(actual, path):
    expected = json.loads(path.read_bytes())
    if json.loads(json.dumps(actual)) != expected:
        raise ValueError("finite evidence differs from " + path.name)


def check_price(application):
    """Check the claimed gain and the raw crossing with directed integer roots."""
    sys.path.insert(0, str(PACKAGE.parents[1] / "scripts"))
    from evaluate_recursive_power import power_bounds
    paid = application["invoice"]["paid"]
    targets = application["invoice"]["targets"]
    # The comparator is PR 7756's upper endpoint plus its previous full gain.
    previous = Fraction("0.00382063778177")
    threshold = previous + Fraction("0.00003312268681")
    one_percent = previous * Fraction(101, 100)
    if Fraction(application["claim"]) <= max(threshold, one_percent):
        raise ValueError("the full application must exceed the round target")
    left, right = map(Fraction, application["bracket"])
    for point, positive in ((threshold, True), (one_percent, True), (left, True), (right, False)):
        lower = upper = Fraction(0)
        for rank in targets.keys() | paid.keys():
            count = targets.get(rank, 0) - paid.get(rank, 0)
            lo, hi = power_bounds(int(rank), 1 - point, 256)
            lower += count * (lo if count >= 0 else hi)
            upper += count * (hi if count >= 0 else lo)
        if not (lower > 0 if positive else upper < 0):
            raise ValueError("the independent directed price has the wrong sign")


def main():
    binary = verify_bit(PACKAGE.parents[1])
    compare(binary, PACKAGE / "BIT-RESULT.json")
    cap = binary["compiler"]["ordinary_admitted"]
    sys.path.insert(0, str(PACKAGE / "complex"))
    from supplier import verify
    complete = verify(cap)
    compare(complete, PACKAGE / "complex/RESULT.json")
    check_price(complete["application"])
    print("PASS_DUAL_SUPPLIER_APPLICATION", complete["application"]["claim"], cap)


if __name__ == "__main__":
    main()
