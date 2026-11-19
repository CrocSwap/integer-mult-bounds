"""Identify the four-phase gate and certify its exact denominator without PACKETS.json."""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import lcm, prod
from pathlib import Path

ROOT = Path(__file__).resolve().parent
D15 = 3893475211724344589772283104450359211356271788394430137298138320180684819953076729962451809990220934288705085671875


def require(ok, message):
    if not ok:
        raise ValueError(message)


def odd(n):
    return n // (n & -n)


def columns_span(columns):
    span = {0}
    for c in columns:
        span |= {x ^ c for x in span}
    return span


def physical_gate():
    # Diagonal entries of S^tensor4 tensor I as powers of i. Conjugating X_j
    # changes the x-dependent sign precisely by the first four Z labels.
    phases = [(b & 15).bit_count() % 4 for b in range(32)]
    counts = Counter(phases)
    trace = (counts[0]-counts[2], counts[1]-counts[3])
    require(trace == (-8, 0), "Wrong phase-gate trace")
    for j in range(5):
        delta = [(phases[z ^ (1 << j)] - phases[z]) % 4 for z in range(32)]
        expected = [(1+2*((z >> j) & 1)) % 4 if j < 4 else 0 for z in range(32)]
        require(delta == expected, "Conjugation of a generating Pauli")
    fixed = sum((point & 15) == 0 for point in range(1024))
    require(fixed == 64, "Wrong fixed dimension")
    # Enumerate the GL(4,2) orbit of the identity symmetric form A A^t.
    orbit = set()
    bases = 0
    for basis in product(range(1, 16), repeat=4):
        if len(columns_span(basis)) != 16:
            continue
        bases += 1
        rows = [sum(((u >> j) & 1) << i for i, u in enumerate(basis)) for j in range(4)]
        form = tuple(sum(((u & v).bit_count() % 2) << i for i, v in enumerate(rows)) for u in rows)
        orbit.add(form)
    require(bases == 20160 and len(orbit) == 420, "Wrong nonalternating shear orbit")
    frames = prod(2**(10-j)-2**j for j in range(4))
    size = frames * len(orbit) // bases
    require(size == 328689900, "Wrong symplectic class size")
    return trace[0], size


def main():
    trace, size = physical_gate()
    data = (ROOT / "sources/five-qubit-projection.json").read_bytes()
    require(sha256(data).hexdigest() == "d7a8465e81f7e20cb87f6bc7b0d7fb7a059e88691fd06df2ec502ee65be62f54",
            "Wrong prior fixed-dimension projection")
    table = json.loads(data)["S10(2)"]
    G = table["order"]
    require(G // size == 75497472 and G % size == 0, "Class 2F centralizer")
    column = json.loads((ROOT / "sources/phase-column.json").read_text())
    rows = table["rows"]
    require(len(column) == len(rows) == 198, "Ordinary rows")
    # Column orthogonality checks the independent centralizer and its identity inner product.
    require(sum(v*v for v in column) == G//size and
            sum(row[0]*v for row, v in zip(rows, column, strict=True)) == 0,
            "Wrong involution column")
    coeffs = []
    raw_levels = []
    for row in rows:
        dim, *sums = row
        mult, rem = divmod(sum(a*128**k for k, a in enumerate(sums)), G)
        require(rem == 0 and mult > 0, "Invalid multiplicity")
        # raw Gram eigenvalue N*m/(32*d). Raw projector coefficient 32*d/N.
        lam = Fraction(32*G*mult, dim)
        raw_levels.append(lam)
        coeffs.append(Fraction(dim, 32*G) / lam)
    require(min(raw_levels) == 2**32 * 394477183485 and len(set(raw_levels)) == 108,
            "Raw minimum or threshold level count")
    upper = lcm(*(odd(v.denominator) for v in coeffs))
    entry = trace * sum(a*b for a, b in zip(coeffs, column, strict=True))
    diagonal = 32 * sum(a*row[0] for a, row in zip(coeffs, rows, strict=True))
    require(upper == odd(entry.denominator) == D15 and 39*odd(diagonal.denominator) == upper,
            "Phase witness/upper bound/diagonal disagree")
    print("PASS raw four-phase witness:", entry)
    print("PASS exact canonical odd denominator", upper, "least noise-optimal odd denominator", 394477183485)


if __name__ == "__main__":
    main()
