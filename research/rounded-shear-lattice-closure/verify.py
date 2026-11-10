#!/usr/bin/env python3
"""Exact finite corroboration of the written rounded-shear lattice theorem."""

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
import json
from math import gcd
from pathlib import Path


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


@dataclass(frozen=True)
class Lattice:
    """Columns (h,r), (0,k), with bounded canonical Hermite parameters."""

    h: int
    r: int
    k: int

    def __post_init__(self) -> None:
        require(all(type(v) is int for v in (self.h, self.r, self.k)), "integer HNF")
        require(1 <= self.h <= 16 and 1 <= self.k <= 16, "HNF size limit")
        require(0 <= self.r < self.k, "canonical HNF residue")

    def contains(self, x: int, y: int) -> bool:
        return x % self.h == 0 and (y - self.r * (x // self.h)) % self.k == 0


def slope_check(a: Fraction) -> None:
    require(type(a) is Fraction, "exact rational slope required")
    require(a.denominator <= 12 and abs(a.numerator) <= 64, "slope size limit")


def nearest(t: Fraction) -> int:
    """Euclidean quotient/remainder implementation, including signed ties."""
    whole, residue = divmod(t.numerator, t.denominator)
    return whole + int(2 * residue >= t.denominator)


def criterion(lattice: Lattice, a: Fraction) -> tuple[bool, bool]:
    slope_check(a)
    g = gcd(lattice.r, lattice.k)
    horizontal = lattice.h * lattice.k // g
    up = lattice.k == 1 or (a * lattice.h / lattice.k).denominator == 1
    right = horizontal == 1 or (a * g / horizontal).denominator == 1
    return up, right


def period_oracle(lattice: Lattice, a: Fraction) -> tuple[tuple[bool, bool], int]:
    """Apply literal rounded updates to every lattice point modulo q*index.

    Neither gcd, the projected source spacing, nor the closure criterion is
    used here. The finite reduction is justified separately in PROOF.md.
    """
    slope_check(a)
    period = a.denominator * lattice.h * lattice.k
    up, right, comparisons = True, True, 0
    for u in range(period // lattice.h):
        for v in range(period // lattice.k):
            x = lattice.h * u
            y = (lattice.r * u + lattice.k * v) % period
            require(lattice.contains(x, y), "oracle representative outside lattice")
            up = lattice.contains(x, y + nearest(a * x)) and up
            right = lattice.contains(x + nearest(a * y), y) and right
            comparisons += 2
    require(comparisons == 2 * a.denominator**2 * lattice.h * lattice.k,
            "incomplete residue enumeration")
    return (up, right), comparisons


def finite_census() -> tuple[dict[str, int], tuple[Lattice, ...], tuple[Fraction, ...]]:
    lattices = tuple(Lattice(h, r, k) for h in range(1, 6)
                     for k in range(1, 6) for r in range(k))
    slopes = tuple(sorted({Fraction(p, q) for p in range(-5, 6)
                           for q in range(1, 6)}))
    cases = comparisons = 0
    for lattice in lattices:
        for a in slopes:
            observed, work = period_oracle(lattice, a)
            require(observed == criterion(lattice, a),
                    f"closure mismatch: {lattice}, {a}, {observed}")
            cases += 2
            comparisons += work
    return {"lattices": len(lattices), "slopes": len(slopes),
            "one_shear_cases": cases, "point_updates": comparisons}, lattices, slopes


def existence_census(lattices: tuple[Lattice, ...],
                     slopes: tuple[Fraction, ...]) -> dict[str, int]:
    nonintegral = tuple(a for a in slopes if a.denominator > 1)
    pairs = positive = negative = construction_updates = 0
    for a in nonintegral:
        for b in nonintegral:
            predicted = (a * b).denominator == 1
            bounded_exists = any(l.h * l.k > 1 and criterion(l, a)[0]
                                 and criterion(l, b)[1] for l in lattices)
            require(predicted == bounded_exists, "bounded existence disagreement")
            if predicted:
                lattice = Lattice(a.denominator, 0, abs(a.numerator))
                up, work_up = period_oracle(lattice, a)
                right, work_right = period_oracle(lattice, b)
                require(up[0] and right[1], "constructive lattice failed")
                require((a * lattice.h).denominator == 1
                        and (b * lattice.k).denominator == 1, "rounding still active")
                construction_updates += work_up + work_right
                positive += 1
            else:
                negative += 1
            pairs += 1
    return {"nonintegral_slope_pairs": pairs, "integer_products": positive,
            "noninteger_products": negative,
            "construction_point_updates": construction_updates}


def controls() -> int:
    # Unit fibers permit fractional slopes on the unrestricted grid.
    require(criterion(Lattice(1, 0, 1), Fraction(1, 3)) == (True, True), "unit fibers")
    # Removing either nonintegrality hypothesis permits nonintegral products.
    require(criterion(Lattice(1, 0, 2), Fraction(2))[0]
            and criterion(Lattice(1, 0, 2), Fraction(1, 3))[1], "integral first slope")
    require(criterion(Lattice(2, 0, 1), Fraction(1, 3))[0]
            and criterion(Lattice(2, 0, 1), Fraction(2))[1], "integral second slope")
    # Skew lattices have distinct projection and fiber spacings.
    require(criterion(Lattice(1, 1, 2), Fraction(1)) == (False, False), "skew fibers")
    require(criterion(Lattice(1, 1, 2), Fraction(2)) == (True, True), "skew positive")
    require(period_oracle(Lattice(2, 0, 3), Fraction(3, 2))[0][0]
            and period_oracle(Lattice(2, 0, 3), Fraction(2, 3))[0][1], "product positive")
    # An inverse subtracts the same increment; half-up rounding is not odd.
    require(nearest(Fraction(1, 2)) == 1 and nearest(Fraction(-1, 2)) == 0, "signed ties")
    require(nearest(Fraction(-3, 2)) == -1 and nearest(Fraction(3, 2)) == 2, "shifted ties")
    # Completed-word closure is weaker than closure at every stage.
    lattice = Lattice(1, 0, 2)
    x, y = 1, 0
    middle = y + nearest(Fraction(1, 2) * x)
    require(not lattice.contains(x, middle) and lattice.contains(x, middle - 1),
            "completed inverse pair does not require stage closure")
    require(criterion(Lattice(2, 0, 1), Fraction(1, 2))[0]
            and not criterion(Lattice(2, 0, 1), Fraction(-4, 5))[1], "single direction")
    return 10


def invalid_controls() -> int:
    count = 0
    for args in ((0, 0, 1), (1, 0, 0), (1, -1, 2), (1, 2, 2),
                 (17, 0, 1), (1, 0, 17), (True, 0, 1)):
        try:
            Lattice(*args)
        except ValueError:
            count += 1
        else:
            raise ValueError(f"invalid lattice accepted: {args}")
    for a in (Fraction(1, 13), Fraction(65), 0.5):
        try:
            slope_check(a)
        except ValueError:
            count += 1
        else:
            raise ValueError("invalid slope accepted")
    return count


def receipt(counts: dict[str, int]) -> None:
    package = Path(__file__).resolve().parent
    hashes = {}
    for name in ("README.md", "PROOF.md", "TASK.json", "SOURCES.json", "VERIFY.json", "verify.py"):
        payload = (package / name).read_bytes()
        require(len(payload) <= 262144, "package file size limit")
        hashes[name] = sha256(payload).hexdigest()
    print(json.dumps({"status": "PASS_ROUNDED_SHEAR_LATTICE_CLOSURE",
                      "counts": counts, "sha256": hashes}, sort_keys=True))


def main() -> None:
    counts, lattices, slopes = finite_census()
    counts.update(existence_census(lattices, slopes))
    counts["semantic_controls"] = controls()
    counts["invalid_input_rejections"] = invalid_controls()
    receipt(counts)


if __name__ == "__main__":
    main()
