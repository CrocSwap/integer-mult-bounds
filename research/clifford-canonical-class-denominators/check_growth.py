"""Certify the polynomial LCM for all odd widths from the prior fixed-space census."""
from hashlib import sha256
import json
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECTION = "d7a8465e81f7e20cb87f6bc7b0d7fb7a059e88691fd06df2ec502ee65be62f54"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def trim(p):
    while p and p[-1] == 0:
        p.pop()
    return p


def primitive(p):
    if not p:
        return []
    content = gcd(*p) * (1 if p[-1] > 0 else -1)
    return [a // content for a in p]


def remainder(a, b):
    r = list(a)
    while len(r) >= len(b):
        shift = len(r) - len(b)
        lead = r[-1]
        if b[-1] != 1:
            r = [b[-1] * v for v in r]
        for i, v in enumerate(b):
            r[i+shift] -= lead * v
        trim(r)
        if b[-1] != 1:
            r = primitive(r)
    return r


def polynomial_gcd(a, b):
    while b:
        a, b = b, primitive(remainder(a, b))
    return primitive(a)


def divide_monic(a, b):
    require(b and b[-1] == 1, "Expected a monic divisor")
    r = list(a)
    q = [0] * max(0, len(r) - len(b) + 1)
    while len(r) >= len(b):
        j = len(r) - len(b)
        q[j] = r[-1]
        for i, v in enumerate(b):
            r[i+j] -= q[j] * v
        trim(r)
    require(not r, "Nonexact polynomial division")
    return q


def multiply(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, v in enumerate(a):
        for j, w in enumerate(b):
            result[i+j] += v*w
    return result


def v2(n):
    return (abs(n) & -abs(n)).bit_length() - 1


def main():
    raw = (ROOT / "sources/five-qubit-projection.json").read_bytes()
    require(sha256(raw).hexdigest() == PROJECTION, "Wrong #7806 input")
    rows = json.loads(raw)["S10(2)"]["rows"]
    require(len(rows) == 198, "Full ordinary character census")
    distinct = set()
    for degree, *sums in rows:
        require(len(sums) == 11 and all(v % degree == 0 for v in sums), "Nonintegral central eigenvalue")
        poly = tuple(v // degree for v in sums)
        require(poly[-1] == 1 and poly[0], "Wrong leading or constant coefficient")
        distinct.add(poly)
    common = [1]
    for poly in sorted(distinct):
        factor = divide_monic(poly, polynomial_gcd(common, list(poly)))
        common = multiply(common, factor)
    require(len(distinct) == 113 and len(common) == 273 and common[-1] == 1 and common[0],
            "Wrong polynomial LCM or asymptotic slope")
    for poly in distinct:
        divide_monic(common, poly)
    # The short monic factors make the dyadic valuation threshold inspectable.
    # Their irreducibility is unnecessary for this independent product check.
    factors = json.loads((ROOT / "FACTORS.json").read_text())
    rebuilt = [1]
    threshold = 0
    for factor, exponent in factors:
        require(factor[-1] == 1 and factor[0] and exponent >= 1, "Invalid factor")
        for _ in range(exponent):
            rebuilt = multiply(rebuilt, factor)
        for i, coeff in enumerate(factor[1:], 1):
            if coeff:
                threshold = max(threshold, (v2(factor[0]) - v2(coeff)) // i + 1)
    require(rebuilt == common and v2(common[0]) == 909 and threshold == 17,
            "Factor product or 2-adic stabilization")
    print("PASS v2(P(±2^r)) = 909 for every r >= 17")
    print("PASS 198 monic integral degree-ten eigenvalue polynomials, 113 distinct; "
          "monic LCM degree 272, nonzero at zero; odd-denominator logarithmic slope 136 per width")
    print("LCM coefficient fingerprint:", sha256(",".join(map(str, common)).encode()).hexdigest())


if __name__ == "__main__":
    main()
