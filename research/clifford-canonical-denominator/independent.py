"""Independent 3-adic obstruction, native order-17 operator and centralizer.

Uses the fixed-space projection from PR7747; does not import the spectrum
checker or read PR7772's eigenvalue table. apoursh with substantial OpenAI
Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import gcd, lcm
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent
EXPECTED = 22742436009630709072767882717680300149753125


def require(ok, problem):
    if not ok:
        raise ValueError(problem)


def parity(bits):
    return bits.bit_count() & 1


def phase_matrix():
    # Entries are exponents of i in 4 U17. The four H_g factors
    # contribute -1/4 times the binary Walsh sign, followed by i S CZ CZ CZ.
    return [[(3 + (r >> 3) + 2*(parity(r & c) + int((r & 9) == 9)
                 + int((r & 6) == 6) + int((r & 12) == 12))) % 4
             for c in range(16)] for r in range(16)]


def weyl_image(phases, x, z):
    # Compare U X^x Z^z and X^a Z^b U entry by entry up to fixed scalar.
    matches = []
    for a in range(16):
        row_zero = [(phases[0][c ^ x] + 2*parity(z & c) - phases[a][c]) % 4
                    for c in range(16)]
        if len(set(row_zero)) != 1:
            continue
        for b in range(16):
            phase = (row_zero[0] - 2*parity(a & b)) % 4
            if all((phases[r][c ^ x] + 2*parity(z & c) - phases[r ^ a][c]
                    - 2*parity((r ^ a) & b) - phase) % 4 == 0
                   for r in range(16) for c in range(16)):
                matches.append(a + 16*b)
    require(len(matches) == 1, "Weyl image was not unique")
    return matches[0]


def apply(columns, v):
    result = 0
    while v:
        bit = v & -v
        result ^= columns[bit.bit_length()-1]
        v ^= bit
    return result


def symplectic(x, y):
    return parity(((x >> 4) & y) ^ ((y >> 4) & x))


def operator_witness():
    phases = phase_matrix()
    roots = ((1, 0), (0, 1), (-1, 0), (0, -1))
    diag = [roots[phases[r][r]] for r in range(16)]
    require(tuple(map(sum, zip(*diag))) == (-4, 0), "Trace of 4 U17")
    binary = [weyl_image(phases, 1 << j, 0) for j in range(4)]
    binary += [weyl_image(phases, 0, 1 << j) for j in range(4)]
    image = tuple(range(256))
    for step in range(1, 18):
        image = tuple(apply(binary, v) for v in image)
        fixed = sum(i == v for i, v in enumerate(image))
        require(fixed == (256 if step == 17 else 1), "Binary order or fixed space")

    # The binary orbit of v=1 supplies a cyclic basis. A commuting map
    # is determined by an arbitrary image w of v. Compute its unique
    # candidate on all 256 points and retain the symplectic candidates.
    def cyclic_basis(v):
        basis = []
        for _ in range(8):
            basis.append(v)
            v = apply(binary, v)
        return basis

    base = cyclic_basis(1)
    coords = {apply(base, code): code for code in range(256)}
    require(len(coords) == 256, "No cyclic basis")
    centralizer = 0
    for w in range(256):
        target = cyclic_basis(w)
        columns = [apply(target, coords[1 << j]) for j in range(8)]
        require(all(apply(binary, c) == apply(columns, s) for c, s in zip(columns, binary)),
                "Candidate fails commutation")
        centralizer += int(all(symplectic(columns[i], columns[j]) == symplectic(1 << i, 1 << j)
                               for i in range(8) for j in range(i+1, 8)))
    require(centralizer == 17, "Wrong symplectic centralizer")
    return centralizer


def levels_from_projection():
    path = ROOT / "sources/sp8-projection.json"
    data = path.read_bytes()
    require(sha256(data).hexdigest() == "0a36754668b66480e5f968c117a4532bc3a5eaab5c9d8448f14a5d0321c2efae",
            "Changed PR7747 projection")
    projection = json.loads(data)
    order = sum(projection["element_counts"])
    rows = []
    for j, (d, *middle) in enumerate(projection["rows"]):
        at_zero = (order if j == 0 else 0) - sum(middle) - d
        coeffs = [at_zero, *middle, d]
        require(len(coeffs) == 9, "Wrong fixed-space projection width")
        weighted = sum(c * (-64)**k for k, c in enumerate(coeffs))
        mult, rem = divmod(weighted, order)
        require(rem == 0 and mult > 0, "Invalid width-13 multiplicity")
        rows.append((d, Fraction(order * mult, 2**48 * d)))
    require(sum(d*d for d, _ in rows) == order == 47377612800, "Irreducible degrees or order")
    return order*256, rows


def main():
    center_size = operator_witness()
    n, rows = levels_from_projection()
    den = lcm(*(val.numerator for _, val in rows))
    weights = [int(d*den/val) for d, val in rows]
    # The common denominator of the scalar Fourier coefficients bounds all
    # entries by integrality. The normalized diagonal gives a first divisor.
    coeff = [Fraction(16*b, den*n) for b in weights]
    upper = lcm(*(v.denominator for v in coeff))
    upper //= upper & -upper
    diag = sum(w * 16*d for w, (d, _) in zip(coeff, rows))
    lower = diag.denominator // (diag.denominator & -diag.denominator)
    live = [(d, b % 3) for (d, _), b in zip(rows, weights) if b % 3]
    require(live == [(35, 1), (238, 1)], "Wrong surviving characters mod 3")
    counts = Counter(d for d, _ in rows)
    residue = 0
    for degree, value in live:
        require(counts[degree] == 1, "Surviving character need not be rational")
        choices = [z for z in range(-degree, degree+1) if z*z <= center_size and (degree-z) % 17 == 0]
        require(len(choices) == 1, "Ambiguous order-17 trace")
        residue -= 16 * value * choices[0]
    require(residue % 3 == 2, "Cancellation of the critical ternary digit")
    power = 1
    scaled = n*den
    while scaled % 3 == 0:
        power *= 3
        scaled //= 3
    require(power == 3**12 and lcm(lower, power) == upper == EXPECTED, "Ternary witness gap")
    require(gcd(upper // lower, lower) == 3, "Diagonal control")
    print(f"PASS_INDEPENDENT_DENOMINATOR symplectic_centralizer={center_size} "
          f"nonzero_mod3_rows={live} critical_power={power} odd_denominator={upper}")


if __name__ == "__main__":
    main()
