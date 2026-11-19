"""Certify both monic LCM degrees, X-adic orders and stable 2-adic valuations."""
import json
from itertools import combinations
from math import gcd
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(ok, message):
    if not ok:
        raise ValueError(message)


def trim(p):
    while p and p[-1] == 0:
        p.pop()
    return p


def primitive(p):
    if p:
        scale = gcd(*p) * (1 if p[-1] > 0 else -1)
        return [v//scale for v in p]
    return p


def coprime(a,b):
    # Primitive pseudo-remainders compute the gcd in Q[X].
    while b:
        while len(a) >= len(b):
            shift = len(a)-len(b)
            lead = a[-1]
            a = [v*b[-1] for v in a]
            for i,v in enumerate(b):
                a[shift+i] -= lead*v
            a = primitive(trim(a))
        a,b = b,a
    return len(a) == 1


def divide(p,q):
    """Return the quotient for exact division by a monic divisor or None."""
    r = list(p)
    quotient = [0]*(len(r)-len(q)+1)
    while len(r) >= len(q):
        j = len(r)-len(q)
        quotient[j] = r[-1]
        for i,v in enumerate(q):
            r[j+i] -= quotient[j]*v
        trim(r)
    return None if r else quotient


def valuation(v):
    return (abs(v) & -abs(v)).bit_length()-1


def main():
    groups = json.loads((ROOT / "CORNERS.json").read_text())["corners"]
    retained = json.loads((ROOT / "FACTORS.json").read_text())
    factors = [row[0] for row in retained]
    require(all(len(q)>1 and q[-1]==1 for q in factors), "monic nonconstant factors")
    require(all(coprime(a,b) for a,b in combinations(factors,2)), "coprimality")
    for idx, (names, distinct, degree, x_order) in enumerate([
            (("Sp10","P5"),256,592,2), (("O10+","O10-"),156,381,1)]):
        polys = {tuple(p) for name in names for p in groups[name]["polys"]}
        require(len(polys) == distinct, "spectral union")
        maxima = [0]*len(factors)
        for p in polys:
            r = list(p)
            for j,q in enumerate(factors):
                power = 0
                while len(r) >= len(q):
                    next_r = divide(r,q)
                    if next_r is None:
                        break
                    r = next_r
                    power += 1
                maxima[j] = max(maxima[j],power)
            require(r == [1], "incomplete factorization")
        require(maxima == [row[idx+1] for row in retained], "LCM exponent")
        require(sum((len(q)-1)*e for q,e in zip(factors,maxima)) == degree, "LCM degree")
        require(maxima[factors.index([0,1])] == x_order, "zero multiplicity")
        constant_val, threshold = 0,0
        for q,e in zip(factors,maxima):
            if not e or q == [0,1]:
                continue
            require(q[0] != 0, "unexpected zero root")
            constant_val += valuation(q[0])*e
            for i,v in enumerate(q[1:],1):
                if v:
                    threshold = max(threshold, (valuation(q[0])-valuation(v))//i+1)
        print(f"{names} {distinct} polynomials: LCM degree {degree}, X-order {x_order}, "
              f"v2((P/X^{x_order})(±2^r))={constant_val} for r >= {threshold}")
    print("PASS both polynomial LCM certificates")


if __name__ == "__main__":
    main()
