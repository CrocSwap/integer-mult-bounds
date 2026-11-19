"""Compute five-qubit canonical odd denominators from rational class packets."""
import argparse
from fractions import Fraction
import json
from math import gcd, lcm
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
ORDER = 24815256521932800
D15 = 3893475211724344589772283104450359211356271788394430137298138320180684819953076729962451809990220934288705085671875
# decimal digits of D, D/T, missing factor on the diagonal, all one-entry witnesses
CHECKPOINTS = {
    15: (115, 127575, 39, [7, 36, 41, 55]),
    17: (198, 414315, 295, [11, 37, 38]),
    19: (280, 14175, 1, [1]),
    21: (340, 2168775, 121, [38]),
    23: (436, 23856525, 767, []),
}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def odd(value):
    require(value > 0, "Positive denominator or spectral level required")
    return value // (value & -value)


def read_table():
    table = json.loads((ROOT / "PACKETS.json").read_text())
    classes, packets = table["classes"], table["packets"]
    require(table["order"] == ORDER and len(classes) == len(packets) == 192, "Wrong table")
    ids = list(range(1, 199))
    for partition in (classes, packets):
        require(sorted(i for item in partition for i in item[0]) == ids,
                "Incomplete ATLAS orbit partition")
    weights = [len(indices)*size for indices, size, _ in classes]
    require(sum(weights) == ORDER and classes[0] == [[1], 1, 10], "Conjugacy census")
    require(sum(values[0]**2 // len(orbit) for orbit, values in packets) == ORDER,
            "Degree census")
    # These are character sums, with squared norm equal to the number of summands.
    for i, (orbit, row) in enumerate(packets):
        require(len(row) == len(classes) and row[0] % len(orbit) == 0, "Packet dimensions")
        weighted = [a*b for a, b in zip(weights, row, strict=True)]
        for j, (_, col) in enumerate(packets[:i+1]):
            expected = ORDER*len(orbit) if i == j else 0
            require(sum(a*b for a, b in zip(weighted, col, strict=True)) == expected,
                    "Rational character packet orthogonality")
    return table


def compute(table, width):
    require(width >= 15 and width % 2 == 1, "Use odd width >= 15")
    r = (width - 1) // 2
    t = (-1)**((width + 1)//4) * (1 << r)
    classes, packets = table["classes"], table["packets"]
    weighted = [len(ids)*size*t**k for ids, size, k in classes]
    eigenvalues = []
    coefficients = []
    for orbit, values in packets:
        degree = values[0] // len(orbit)
        total = sum(a*b for a, b in zip(weighted, values, strict=True))
        eigen, rem = divmod(total, values[0])
        require(rem == 0 and eigen > 0, "Incorrect central eigenvalue")
        require(eigen*degree % ORDER == 0, "Nonintegral tensor multiplicity")
        eigenvalues.append(eigen)
        coefficients.append(Fraction(degree, ORDER*eigen))
    # H = F^{-1} in the ordinary group algebra. Sums over Galois packets are integers.
    scale = lcm(*(v.denominator for v in coefficients))
    numer = [v.numerator*(scale//v.denominator) for v in coefficients]
    H = [sum(a*entry[1][j] for a, entry in zip(numer, packets, strict=True))
         for j in range(len(classes))]
    D = odd(scale // gcd(scale, *H))
    per_class = [odd(scale//gcd(scale, value)) for value in H]
    require(lcm(*per_class) == D, "All-class denominator")
    T = lcm(*(odd(v) for v in eigenvalues))
    require(D % T == 0 and odd(ORDER) % (D//T) == 0, "Integral spectral sandwich")
    singletons = [i for (indices, _, _), d in zip(classes, per_class, strict=True)
                  if d == D for i in indices]
    dig = len(str(D))
    if width in CHECKPOINTS:
        require((dig, D//T, D//per_class[0], singletons) == CHECKPOINTS[width],
                "Changed width-dependent certificate")
    if width == 15:
        require(D == D15 and odd(min(eigenvalues)) == 394477183485, "Threshold denominator")
        require(odd(scale) == D, "Unattained coefficientwise upper bound")
    if width == 23:
        require(lcm(per_class[0], per_class[1]) == D, "Missing identity/one-phase witness")
    print(f"f={width} digits={dig} D/T={D//T} diagonal deficit={D//per_class[0]} "
          f"single ATLAS classes={singletons}")
    return D


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, help="Print the full denominator for one odd width")
    parser.add_argument("--gap", type=Path, help="Check JSON output of export_classes.g")
    args = parser.parse_args()
    table = read_table()
    if args.gap:
        G, cl, pk, phase = json.loads(args.gap.read_text())
        require([G, cl, pk] == [table["order"], table["classes"], table["packets"]],
                "Original GAP packet data disagree")
        require(phase == json.loads((ROOT / "sources/phase-column.json").read_text()),
                "Original GAP involution column disagrees")
    if args.width is None:
        for width in CHECKPOINTS:
            compute(table, width)
    else:
        sys.set_int_max_str_digits(0)
        print("D =", compute(table, args.width))
