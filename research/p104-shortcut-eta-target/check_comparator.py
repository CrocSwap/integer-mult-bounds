"""Compute the directed public-rate ceilings for #8088's literal terminal bookings."""

from fractions import Fraction as Q
from pathlib import Path
import json


def calculate():
    p = json.loads(
        (Path(__file__).resolve().parent / "parent8088/RESULT.json").read_bytes()
    )
    old = p["terminal"]
    gap = Q(5, 10**18)
    target = Q(39, 10000)
    cb = Q(4391986206293, 2**50)
    cg = Q(17158764376, 2**42)
    db = Q(1420718, 2**20)
    dg = Q(1039776, 2**23)
    h = old["ordinary_H"]
    g = old["numerical_H"]
    prev = Q(old["ordinary_rates"][1])
    assert (h, g) == ([62186, 986008, 1048575], 66037) and Q(old["kappa"]) == Q(
        ".003899574328473"
    )
    ordinary = (249 * (cb - db / h[-1]) + prev) / 250
    gaussian = cg - dg / g
    fixed = min(ordinary, gaussian, Q("0.0039")) - gap
    assert Q(old["kappa"]) < fixed < target

    def outward(v):
        n = v.numerator * 10**24 // v.denominator

        def dec(k):
            return f"0.{k:024d}"

        return [dec(n), dec(n + 1)]

    return {
        "parent_public": old["kappa"],
        "fixed_ordinary_public_upper": str(ordinary - gap),
        "fixed_gaussian_public_upper": str(gaussian - gap),
        "fixed_public_upper": str(fixed),
        "fixed_upper_decimal_interval": outward(fixed),
        "both_suppliers_public_shortfall": str(target - fixed),
        "required_saving_interval": outward(target - fixed),
        "native_calls_per_gaussian_word": 48,
        "ordinary_calls": 36,
        "comparison_unit": "Public-rate units on the binding supplier guard after both fixed terminal invoices; positive and ordinary charges are already aggregated. Min of the two stage ceilings, component clamp and subtraction of 5e-18.",
    }


if __name__ == "__main__":
    print(json.dumps(calculate(), sort_keys=True, indent=2))
