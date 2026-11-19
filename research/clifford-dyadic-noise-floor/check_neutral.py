"""Exact dense one-qubit calibration of the neutral-sector endpoint transfer.

apoursh, with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from math import gcd


def need(value, message):
    if not value:
        raise ValueError(message)


def rotate(z):
    return -z[1], z[0]


def multiply(z, w):
    return z[0]*w[0] - z[1]*w[1], z[0]*w[1] + z[1]*w[0]


def quarter_gauge(u):
    choices = [u]
    for _ in range(3):
        choices.append(tuple(map(rotate, choices[-1])))
    return min(choices)


def hadamard(u):
    # Left product by (1+i)[[1,1],[1,-1]]/2. Each u stores 2U.
    output = []
    for sign in (1, -1):
        for col in range(2):
            a, b = u[col]
            c, d = u[2+col]
            x, y = a+sign*c, b+sign*d
            need((x-y) % 2 == (x+y) % 2 == 0, "gate left the common grid")
            output.append(((x-y)//2, (x+y)//2))
    return tuple(output)


def alphabet():
    unit = quarter_gauge(((2, 0), (0, 0), (0, 0), (2, 0)))
    seen, todo = {unit}, [unit]
    while todo:
        u = todo.pop()
        s = u[:2] + tuple(map(rotate, u[2:]))
        for candidate in (hadamard(u), s):
            v = quarter_gauge(candidate)
            if v not in seen:
                seen.add(v)
                todo.append(v)
    need(len(seen) == 24, "projective single-qubit alphabet")
    return sorted(seen)


def dense_gram(f):
    # The literal Frobenius product of the stored matrices is 8 times
    # the normalized single-copy Gram entry. Scalar choices are held fixed.
    cols = alphabet()
    rows = []
    common = 8**f
    for u in cols:
        row = []
        for v in cols:
            real = sum(a*c + b*d for (a,b), (c,d) in zip(u,v,strict=True))
            imag = sum(a*d - b*c for (a,b), (c,d) in zip(u,v,strict=True))
            value = (1, 0)
            for _ in range(f):
                value = multiply(value, (real, imag))
            common = gcd(common, *value)
            row.append(value)
        rows.append(row)
    return [[(a//common, b//common) for a,b in row] for row in rows], 8**f//common


def psd_nullity(matrix):
    """Inertia by positive Schur pivots and exact zero rows."""
    nullity = 0
    while matrix:
        pivot, imaginary = matrix[0][0]
        need(imaginary == 0, "non-real diagonal")
        if pivot < 0:
            return None
        if not pivot:
            if any(z != (0, 0) for z in matrix[0]):
                return None
            matrix = [row[1:] for row in matrix[1:]]
            nullity += 1
            continue
        next_rows = []
        common = 0
        for row in matrix[1:]:
            updated = []
            for (a, b), right in zip(row[1:], matrix[0][1:], strict=True):
                c, d = multiply(row[0], right)
                value = (pivot*a-c, pivot*b-d)
                updated.append(value)
                common = gcd(common, *value)
            next_rows.append(updated)
        divisor = common or 1
        matrix = [[(a//divisor, b//divisor) for a,b in row] for row in next_rows]
    return nullity


def difference(rows, den, endpoint, sign):
    num = endpoint * den
    need(num.denominator == 1, "endpoint outside this integer scale")
    return [[(sign*(a-int(num)*(i == j)), sign*b)
             for j, (a,b) in enumerate(row)] for i,row in enumerate(rows)]


def main():
    pairs = [
        ((7, 8), Fraction(21,32), Fraction(45,32)),
        ((11,12), Fraction(465,512), Fraction(561,512)),
        ((15,16), Fraction(8001,8192), Fraction(8385,8192)),
    ]
    for widths, lo, hi in pairs:
        for f in widths:
            rows, den = dense_gram(f)
            need(all(a == rows[j][i][0] and b == -rows[j][i][1]
                     for i,row in enumerate(rows) for j,(a,b) in enumerate(row)),
                 "non-Hermitian literal Gram")
            for value, sign in ((lo,1),(hi,-1)):
                dim = psd_nullity(difference(rows,den,value,sign))
                need(dim is not None and dim > 0, "endpoint fails PSD or attainment")
        print(f"PASS one-qubit widths {widths}: endpoints {lo}, {hi}")
    # Crossing 8 -> 9 has strict contraction at both ends. It detects a
    # check that confuses sector inheritance with equality at every width.
    rows, den = dense_gram(9)
    for value, sign in ((pairs[0][1],1), (pairs[0][2],-1)):
        need(psd_nullity(difference(rows,den,value,sign)) == 0, "adjacent-width control")
    print("PASS strict interior at width 9 on the width-8 interval")


if __name__ == "__main__":
    main()
