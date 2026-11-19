"""Exact spectral projectors, canonical denominators, and endpoint certificates."""
import argparse
import json
import sys
from fractions import Fraction
from hashlib import sha256
from functools import reduce
from math import comb, gcd, lcm
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SP_ORDER = 24815256521932800
SECTORS = {0: ("Sp10", "P5"), 2: ("O10+", "O10-")}
SIZES = {"Sp10": (1, 198, 113, 191), "P5": (1023, 322, 143, 320),
         "O10+": (528, 155, 94, 150), "O10-": (496, 164, 96, 160)}


def require(ok, detail):
    if not ok:
        raise ValueError(detail)


def load():
    return json.loads((ROOT / "CORNERS.json").read_text())


def value(coeffs, t):
    return reduce(lambda x, c: x*t+c, reversed(coeffs), 0)


def odd(x):
    return abs(x) // (abs(x) & -abs(x))


def validation(groups):
    for name, data in groups.items():
        idx, nrows, nlevels, ncols = SIZES[name]
        order = SP_ORDER // idx
        polys, counts, cols = data["polys"], data["counts"], data["columns"]
        require(len(polys) == len(counts) == nlevels and sum(counts) == nrows, name)
        require(polys == sorted(polys) and all(len(p) == 11 and p[-1] == 1 for p in polys),
                "spectral ordering and leading coefficient")
        require(len(cols) == ncols and all(len(c) == nlevels+2 for c in cols), "column shape")
        require(sum(c[0] for c in cols) == order, "group order")
        identity, = [c for c in cols if c[1] == 10]
        require(identity[0] == 1 and sum(identity[2:]) == order, "regular representation")
        require(all(c[0] > 0 and sum(c[2:]) == 0 for c in cols if c[1] < 10), "regular character")
        weights = [c[0] for c in cols]
        characters = list(zip(*(c[2:] for c in cols), strict=True))
        for i, (p, h) in enumerate(zip(polys, characters, strict=True)):
            wh = [mass*v for mass,v in zip(weights,h,strict=True)]
            by_fix = [0]*11
            for linked, v in zip(cols, wh, strict=True):
                by_fix[linked[1]] += v
            h0 = identity[i+2]
            require(by_fix == [h0*x for x in p], "class moments")
            require(sum(a*b for a,b in zip(wh,h,strict=True)) == order*h0, "packet norm")
            for prev in characters[:i]:
                require(sum(a*b for a,b in zip(wh,prev,strict=True)) == 0, "packet orthogonality")
        print(name, nrows, "irreducibles,", nlevels, "polynomials,", ncols, "projector columns")


def at_width(f, groups):
    require(f >= 15, "Expected a full-rank width >= 15")
    if f % 2:
        r = (f-1)//2
        t = (-1)**((f+1)//4) * 2**r
        names = ("Sp10",)
    else:
        r = (f-2)//2
        t = (-1)**(f//4) * 2**r
        names = SECTORS[f%4]
    block_denoms = []
    spectra = []
    for name in names:
        data = groups[name]
        levels = [value(p,t) for p in data["polys"]]
        require(min(levels) > 0, "Gram singularity or phase error")
        spectra.extend(levels)
        order = sum(c[0] for c in data["columns"])
        common = lcm(*levels)
        numerators = [common//v for v in levels]
        divisor = order*common
        for col in data["columns"]:
            numerator = sum(c*v for c,v in zip(col[2:],numerators,strict=True))
            divisor = gcd(divisor,numerator)
        block_denoms.append(odd(order*common//divisor))
    return (t, Fraction(min(spectra), t**10), Fraction(max(spectra), t**10),
            odd(min(spectra)), block_denoms, lcm(*block_denoms))


def endpoint_check(groups):
    # Rows here use the retained #7806 ordering and are resolved by polynomial.
    prior = json.loads((ROOT / "sources/five-qubit-projection.json").read_text())
    for residue, first, tag in [(0,16,"S10(2)"), (2,18,"O10-(2).2")]:
        raw = prior[tag]["rows"][:2]
        top, bottom = [[z//row[0] for z in row[1:]] for row in raw]
        for sign, (lo, hi), offset in [(1, (bottom,top), 0),(-1, (top,bottom), 4)]:
            first_magnitude = 2**((first+offset-2)//2)
            threshold = 2**18
            for name in SECTORS[residue]:
                for p in groups[name]["polys"]:
                    # All coefficients of (p-lo)(sign*(threshold+Y)) and
                    # (hi-p)(sign*(threshold+Y)) are nonnegative.
                    for upper,lower in [(p,lo),(hi,p)]:
                        diff = [(a-b)*sign**i for i,(a,b) in enumerate(zip(upper,lower,strict=True))]
                        point = first_magnitude
                        while point < threshold:
                            require(value(diff,point) >= 0, "small-width endpoint")
                            point *= 16
                        for j in range(len(diff)):
                            coeff = sum(diff[i]*comb(i,j)*threshold**(i-j) for i in range(j,len(diff)))
                            require(coeff >= 0, f"global endpoint inequality {name} sign={sign} j={j}")
            named = groups[SECTORS[residue][0 if residue == 0 else 1]]["polys"]
            require(lo in named and hi in named, "endpoint attained")
    # At odd f, the only quotient is Sp10 and sign = (-1)^floor((f+1)/4).
    # Its high-magnitude inequalities have already been proved for both signs.
    trivial, least = [[z//row[0] for z in row[1:]] for row in prior["S10(2)"]["rows"][:2]]
    for f in range(15, 37, 2):
        r = (f-1)//2
        t = (-1)**((f+1)//4) * 2**r
        levels = [value(p,t) for p in groups["Sp10"]["polys"]]
        proposed = [value(p,t) for p in ((least,trivial) if t>0 else (trivial,least))]
        require(0 < min(levels) and proposed == [min(levels),max(levels)], "odd-width endpoint")
    print("PASS sharp normalized endpoints at every five-qubit width >=15")


# Scalar-only denominators and the two separate corners miss odd factors.
BENCHMARKS = {
    16: (25515, "3ad5a2ff7918e520a62990e369b36e93fc87acb24b1319acbf9cede3e2e0c5f5"),
    18: (309825, "8beb117bae2b49daf01df006aac4acde31d1d62464409c9719a4a47acece5f24"),
    20: (2835, "624c1a6d7830e67688c5694d5b76f3c24a92965811ce619e826088fecbd6ac8f"),
    22: (42525, "a57ad201b00d9581bd14154a9df842d1e7c5ecf2cb85098ed5cc06bf4d1c7f92"),
}


def main():
    sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int)
    args = parser.parse_args()
    groups = load()["corners"]
    if args.width is None:
        validation(groups)
        endpoint_check(groups)
    for f in ([16,18,20,22] if args.width is None else [args.width]):
        t, smallest, largest, opt, blocks, D = at_width(f, groups)
        if f in BENCHMARKS:
            relative, fingerprint = BENCHMARKS[f]
            scalar = odd(lcm(*(value(p,t) for name in SECTORS[f%4] for p in groups[name]["polys"])))
            require(D == relative*scalar and D > max(blocks), "corner or scalar ablation")
            require(sha256(str(D).encode()).hexdigest() == fingerprint, "canonical denominator digits")
        print(f"f={f} t={t} normalized=[{smallest}, {largest}] optimal odd denominator={opt}")
        print(f"  component digits={[len(str(x)) for x in blocks]} canonical digits={len(str(D))} bits={D.bit_length()}")
        print(f"  D={D}")


if __name__ == "__main__":
    main()
