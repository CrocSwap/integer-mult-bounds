"""Compute the pointed permutation character and the exact spectral support independently."""
from fractions import Fraction
from math import lcm
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pointed import HERE, NFLAGS, ORDER, geometry, orbital_kernels
from compile_row import apply


def statistics():
    table = json.loads((HERE/"predecessor/source/CLASS-ALGEBRA.json").read_text())
    spaces, elements, orbital_counts, _ = geometry()
    fixed = []
    for cl in table["classes"]:
        vals = []
        for s in cl["representatives"]:
            transform = [apply(s,v) for v in range(256)]
            n = 0
            for space, points in zip(spaces,elements,strict=True):
                if all((space >> transform[v]) & 1 for v in points):
                    n += sum(transform[v]==v for v in points if v)
            vals.append(n)
        if len(set(vals)) != 1:
            raise ArithmeticError("Fused rational classes have distinct fixed-flag counts")
        fixed.append(vals[0])
    if fixed[0] != NFLAGS:
        raise ArithmeticError("Flags fixed by identity")
    shell = [Fraction((-64)**cl["fixed"],16**12) for cl in table["classes"]]
    sizes = [cl["size"] for cl in table["classes"]]
    eigenvalues = {}
    constituents = []
    for row in table["characters"]:
        orbit = Fraction(sum(n*v*v for n,v in zip(sizes,row,strict=True)),ORDER)
        mult = Fraction(sum(n*f*v for n,f,v in zip(sizes,fixed,row,strict=True)),ORDER)/orbit
        if orbit.denominator!=1 or mult.denominator!=1 or mult<0:
            raise ArithmeticError("Nonintegral packet data")
        if mult:
            scalar = sum(n*k*v for n,k,v in zip(sizes,shell,row,strict=True))/row[0]
            constituents.append((row[0]//int(orbit),int(mult),int(orbit),scalar))
            eigenvalues[scalar] = eigenvalues.get(scalar,0)+row[0]*int(mult)
    if sum(eigenvalues.values())!=NFLAGS or sum(o*m*m for _,m,o,_ in constituents)!=len(orbital_counts):
        raise ArithmeticError("Permutation dimension or commutant dimension")
    return constituents, eigenvalues


def main():
    constituents, levels = statistics()
    level = (0,1,1,1,0)
    a,b = orbital_kernels()
    if a[level]*NFLAGS != sum(x*n for x,n in levels.items()):
        raise ArithmeticError("Orbital Gram trace")
    if b[level]*NFLAGS != sum(n/x for x,n in levels.items()):
        raise ArithmeticError("Orbital inverse trace")
    denominator=lcm(*(x.denominator for x in b.values()))
    if denominator!=4073770240465467939271875 or b[(1,0,1,1,0)].denominator!=denominator:
        raise ArithmeticError("Full flag inverse denominator and one-entry witness")
    print("PASS fixed-flag character, constituents",sorted(constituents), "and",len(levels),"levels; both traces")


if __name__ == "__main__":
    main()
