"""Check geometric class recognition, character orthogonality and integral convolution."""
from fractions import Fraction
from pathlib import Path
from random import Random
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from class_algebra import GROUP_ORDER, IDENTITY, apply_columns, class_index, data, gram_class_matrix, pairing, require


def transvection(axis, vector):
    return vector ^ (axis if pairing(axis, vector) else 0)


def main():
    registry = data()
    cs, rows = registry["classes"], registry["characters"]
    sizes = [c["size"] for c in cs]
    mass = sum(sizes)
    require(len(rows) == len(cs) == 80 and mass == GROUP_ORDER and class_index(IDENTITY) == 0,
            "Incorrect group or identity")
    rng = Random(52)
    for j, c in enumerate(cs):
        for r in c["representatives"]:
            require(class_index(r) == j, "Representative lookup")
            for _ in range(5):
                a = rng.randrange(1,256)
                r = [transvection(a,apply_columns(r,transvection(a,v))) for v in IDENTITY]
                require(class_index(r) == j,"Change of symplectic basis")
    bad = list(IDENTITY)
    bad[0] ^= 2
    try:
        class_index(bad)
    except ValueError:
        pass
    else:
        raise ValueError("Accepted a nonsymplectic matrix")
    shell = [(-64)**c["fixed"] for c in cs]
    matrix = gram_class_matrix()
    require(all(sizes[i]*matrix[i][j] == sizes[j]*matrix[j][i]
                for i in range(80) for j in range(80)),"Central multiplication lacks adjoint symmetry")
    spectrum = set()
    for i,r in enumerate(rows):
        for t in rows[i+1:]:
            require(sum(n*a*b for n,a,b in zip(sizes,r,t,strict=True)) == 0,
                    "Packet orthogonality")
        theta = Fraction(sum(n*c*x for n,c,x in zip(sizes,r,shell,strict=True)), r[0])
        require(theta.denominator == 1 and all(sum(a*b for a,b in zip(row,r,strict=True)) == theta*v
                                               for row,v in zip(matrix,r,strict=True)),
                "Character eigenvector of the actual matrix")
        spectrum.add(theta / 16**12)
    require(len(spectrum)==52 and min(spectrum) == Fraction(470624175,2**32)
            and max(spectrum) == Fraction(7841980575,2**30), "Published width-13 endpoints")
    require(sum(c1*c2 for c1,c2 in zip(matrix[0],shell)) == sum(n*s*s for n,s in zip(sizes,shell)),
            "Literal identity coefficient of the square")
    print("PASS all 81 ordinary classes recognized, 405 conjugations, 80 rational packets,"
          " exact adjoint symmetry, 52 levels and both width-13 endpoints")


if __name__ == "__main__":
    main()
