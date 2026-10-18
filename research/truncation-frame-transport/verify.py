#!/usr/bin/env python3
"""Exact truncation/frame boundary audit. Apache-2.0.

Prepared for jmbarrancoidener with substantial OpenAI Codex assistance.
No supplier implementation is imported. Normal execution writes no files.
"""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ZERO = (F(0), F(0))
ONE = (F(1), F(0))
UNITS = (ONE, (-F(1), F(0)), (F(0), F(1)), (F(0), -F(1)))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def add(a, b):
    return (a[0] + b[0], a[1] + b[1])


def mul(a, b):
    return (a[0] * b[0] - a[1] * b[1],
            a[0] * b[1] + a[1] * b[0])


def scale(a, q):
    return (a[0] * q, a[1] * q)


def trunc(a, p):
    # int(Fraction) truncates toward zero, including negative inputs.
    h = F(1, 2**p)
    return tuple(h * int(v / h) for v in a)


def qvector(x, p):
    return [trunc(z, p) for z in x]


def dot(row, x):
    z = ZERO
    for a, b in zip(row, x, strict=True):
        z = add(z, mul(a, b))
    return z


def disk(x):
    return all(a*a + b*b <= 1 for a, b in x)


def admitted(row):
    nonzero = [z for z in row if z != ZERO]
    return not nonzero or (len(nonzero) == 1 and nonzero[0] in UNITS)


def witness(row, p):
    """Construct the proof's witness for any nonadmitted rational row."""
    h = F(1, 2**p)
    for j, a in enumerate(row):
        if any(v.denominator != 1 for v in a):
            x = [ZERO] * len(row)
            x[j] = (h, F(0))
            return x
    require(not admitted(row), "Requested a counterexample for an admitted row")
    sign = lambda v: (v > 0) - (v < 0)
    return [(3*h*sign(a)/4, -3*h*sign(b)/4) for a, b in row]


def commutes(row, x, p):
    return trunc(dot(row, x), p) == dot(row, qvector(x, p))


def check_error_bound(row, x, p):
    # Component l1 mass bounds the complex induced row norm without roots.
    h = F(1, 2**p)
    mass = sum(abs(a) + abs(b) for a, b in row)
    error = add(trunc(dot(row, x), p), scale(dot(row, qvector(x, p)), -1))
    require(sum(v*v for v in error) < 2*h*h*(1+mass)**2,
            "Charged commutator bound failed")


def source_monomial(x, exponent):
    """Literal y^exponent multiplication modulo y^r+1, including negatives."""
    r = len(x)
    out = [ZERO] * r
    for j, z in enumerate(x):
        quotient, index = divmod(j + exponent, r)
        out[index] = scale(z, -1 if quotient % 2 else 1)
    return out


def split_monomial(x, exponent):
    """Independent split/merge implementation of the retained source recipe."""
    r = len(x)
    e, s = divmod(exponent, r)
    out = [scale(z, -1) for z in x[r-s:]] + x[:r-s] if s else x[:]
    return [scale(z, -1 if e % 2 else 1) for z in out]


def fwht(values):
    values = values[:]
    width = 1
    while width < len(values):
        for start in range(0, len(values), 2*width):
            for j in range(start, start + width):
                a, b = values[j], values[j+width]
                values[j], values[j+width] = a+b, a-b
        width *= 2
    return values


def check_pins():
    sources = json.loads((HERE / "SOURCES.json").read_text())
    checked = 0
    for entry in sources["files"]:
        if entry["usage"] != "input":
            continue
        data = (ROOT / entry["path"]).read_bytes()
        require(sha256(data).hexdigest() == entry["sha256"], "Source drift: " + entry["path"])
        checked += 1
    return checked


def verify():
    pins = check_pins()
    # This full rational alphabet includes integer amplification, nonunit
    # Gaussian integers, fractional contractions and coordinate mixing.
    real = tuple(map(F, (-2, -1, 0, 1, 2))) + (F(-1, 2), F(1, 2))
    alphabet = tuple(product(real, repeat=2))
    accepted = rejected = 0
    for row in product(alphabet, repeat=2):
        if admitted(row):
            accepted += 1
            for p in (1, 3):
                h = F(1, 2**p)
                for coords in product((F(-5, 4), F(-1), F(-3, 4), F(0), F(3, 4), F(1), F(5, 4)), repeat=4):
                    x = [(h*coords[0], h*coords[1]), (h*coords[2], h*coords[3])]
                    require(commutes(row, x, p), "Admitted row failed")
        else:
            rejected += 1
            for p in (1, 3):
                x = witness(row, p)
                require(disk(x), "Witness leaves input disk")
                require(not commutes(row, x, p), "Invalid row escaped witness")
                check_error_bound(row, x, p)
    require((accepted, rejected) == (9, 2392), "Incomplete rational-row census")

    monomials = 0
    for r in (2, 4, 8, 16):
        for p in (1, 2, 5):
            h = F(1, 2**p)
            x = [(h*F((3*j) % 9 - 4, 4), h*F((5*j) % 9 - 4, 4)) for j in range(r)]
            for exponent in range(-2*r, 2*r+1):
                y = source_monomial(x, exponent)
                require(y == split_monomial(x, exponent), "Source split/merge differs")
                require(source_monomial(y, -exponent) == x, "Inverse monomial differs")
                require(disk(x) and disk(y), "Source monomial leaves disk")
                require(qvector(y, p) == source_monomial(qvector(x, p), exponent), "Source rounding move failed")
                monomials += 1

    # A max-norm isometry already fails outside the Gaussian units.
    phase = (F(3, 5), F(4, 5))
    x = [(F(1, 2), F(0))]
    require(sum(v*v for v in phase) == 1, "Phase is not unit length")
    before = dot([phase], qvector(x, 1))
    after = trunc(dot([phase], x), 1)
    require(before == (F(3, 10), F(2, 5)) and after == ZERO, "Phase counterexample changed")
    require(disk(x) and disk([before]), "Phase example leaves disk")

    hadamard = []
    for k in range(1, 5):
        n, root, p = 4**k, 2**k, k+1
        h = F(1, 2**p)
        # Every pair of distinct rows has zero dot product. XOR reduces the
        # full Gram check to n independent character sums, each of length n.
        sums = [sum(-1 if (a & j).bit_count() % 2 else 1 for j in range(n)) for a in range(n)]
        require(sums == [n] + [0]*(n-1), "Hadamard orthogonality failed")
        v = [3*h/4]*n
        direct = [sum((-z if (a & j).bit_count() % 2 else z) for j, z in enumerate(v))/root for a in range(n)]
        require(direct == [z/root for z in fwht(v)], "Independent Hadamard engines differ")
        rounded = [h*int(z/h) for z in direct]
        require(all(int(z/h) == 0 for z in v), "Pre-frame truncation is nonzero")
        require(max(map(abs, v)) <= 1 and max(map(abs, direct)) <= 1, "Hadamard fixture leaves disk")
        units = int(F(3*root, 4))
        require(rounded == [units*h] + [F(0)]*(n-1), "Dimension-growth witness differs")
        hadamard.append({"dimension": n, "precision": p, "error_in_grid_units": units})

    # Meaningful weakened-contract controls, separate from the full census.
    controls = {
        "unit_phase_isometry": ([phase], x, 1),
        "gaussian_integer_amplification": ([(F(2), F(0))], [(F(3, 8), F(0))], 1),
        "fractional_contraction": ([(F(1, 2), F(0))], [(F(1, 2), F(0))], 1),
        "coordinate_sum": ([ONE, ONE], [(F(3, 8), F(0))]*2, 1),
        "real_imaginary_mix": ([(F(1), F(1))], [(F(3, 8), F(-3, 8))], 1),
    }
    for name, (row, v, p) in controls.items():
        require(not commutes(row, v, p), "Weakened contract escaped: " + name)
    # Wrong floor rounding would invalidate even the source sign operation.
    h = F(1, 2)
    floor_q = lambda z: h*(z//h)
    require(floor_q(F(-1, 4)) != -floor_q(F(1, 4)), "Floor control failed")

    # The proof gives (sqrt(2)*(1+sqrt(n)))^2 <= 8n < 4^g.
    for n in range(1, 4097):
        c = 0
        while 4**c < n:
            c += 1
        g = c+2
        require(8*n < 4**g, "Extra-grid-width bound failed")
        require(c == 0 or 4**(c-1) < n, "Nonminimal ceiling computation")

    return {"status": "PASS_TRUNCATION_FRAME_TRANSPORT", "source_pins": pins,
            "rational_rows": 2401, "admitted_rows": accepted, "rejected_rows": rejected,
            "source_monomials": monomials, "hadamard": hadamard,
            "weakened_contract_controls": len(controls)+1,
            "guard_dimensions": 4096, "kappa": "unchanged"}


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
