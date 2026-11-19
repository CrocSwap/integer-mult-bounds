"""Exhaust the one/two-qubit Clifford quotients using literal Gaussian matrices."""
from collections import deque
from itertools import product
from fractions import Fraction
from pathlib import Path
from random import Random
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from coordinate_support import census


def require(ok, detail):
    if not ok:
        raise ValueError(detail)


def act(g, p, n):
    kind, i, j = g
    x, z = p >> n, p & ((1 << n)-1)
    if kind == "H":
        bit = ((x ^ z) >> i) & 1
        x ^= bit << i
        z ^= bit << i
    elif kind == "S":
        z ^= x & (1 << i)
    else:
        x ^= ((x >> i) & 1) << j
        z ^= ((z >> j) & 1) << i
    return (x << n) | z


def matrix_step(g, matrix):
    # Gaussian integers are stored in Python complex values. The small integer
    # sums and sign changes here stay exact; check the component range at each step.
    kind,i,j = g
    q = len(matrix)
    result = []
    for r in range(q):
        b = (r >> i) & 1
        if kind == "H":
            lo, hi = matrix[r & ~(1 << i)], matrix[r | (1 << i)]
            row = tuple(a-x if b else a+x for a,x in zip(lo,hi,strict=True))
        elif kind == "S":
            row = tuple(v*(1j if b else 1) for v in matrix[r])
        else:
            row = matrix[r ^ (b << j)]
        require(all(abs(v.real) < 2**30 and abs(v.imag) < 2**30 and
                    v.real == int(v.real) and v.imag == int(v.imag) for v in row),"integer range")
        result.append(row)
    return tuple(result)


def native(n):
    q = 1 << n
    gens = [(kind,i,0) for kind in ("H","S") for i in range(n)]
    gens += [("CX",i,j) for i in range(n) for j in range(n) if i != j]
    ident = tuple(1 << j for j in range(2*n))
    eye = tuple(tuple(complex(r==c) for c in range(q)) for r in range(q))
    seen = {ident}
    todo = deque([(ident,eye)])
    support = []
    while todo:
        sym, matrix = todo.popleft()
        h = sum(row[0] != 0 for row in matrix).bit_length()-1
        masks = tuple(sum(1 << x for x in range(q) if matrix[r ^ x][c])
                      for r in range(q) for c in range(q))
        support.append((h,masks))
        for g in gens:
            partner = tuple(act(g,p,n) for p in sym)
            if partner not in seen:
                seen.add(partner)
                todo.append((partner,matrix_step(g,matrix)))
    require(len(support)=={1:6,2:720}[n],"incomplete small group")
    return support


def direct(n, records, addresses):
    q = 1 << n
    hits = [0]*(n+1)
    coeffs = [0]*(n+1)
    for h,masks in records:
        mask = (1 << q)-1
        for r,c in addresses:
            mask &= masks[r*q+c]
        if mask:
            hits[h] += 1
            coeffs[h] += q*mask.bit_count()
    return tuple(zip(hits,coeffs,strict=True))


def main():
    small = 0
    rng = Random(1701)
    for n in [1,2]:
        native_group = native(n)
        q = 1 << n
        sites = list(product(range(q),repeat=2))
        examples = list(product(sites,repeat=2))
        examples += [tuple(rng.choice(sites) for _ in range(rng.randrange(3,10))) for _ in range(120)]
        for a in examples:
            require(census(n,a)==direct(n,native_group,a),("support mismatch",n,a))
            small += 1
    min_pattern = [(0,0),(1,0),(2,0),(4,0),(8,0)]+[(0,0)]*8
    max_pattern = [(0,0)]*13
    for label,pat in [("minimum",min_pattern),("maximum",max_pattern)]:
        table=census(4,pat)
        norm=sum(Fraction(ncoeff,2**((4+h)*13)) for h,(_,ncoeff) in enumerate(table))
        print(label,table,"total fibres and coefficients",tuple(map(sum,zip(*table))),"adjoint squared norm",norm)
    require(sum(n for n,_ in census(4,max_pattern))==47377612800,"full Sp(8,2)")
    require(census(4,min_pattern)[:4]==((0,0),)*4,"lower ranks survive separating coordinate")
    extrema = [tuple(map(sum,zip(*census(4,pat)))) for pat in (min_pattern,max_pattern)]
    require(extrema==[(21139292160,5411658792960),(47377612800,8338459852800)],"global extrema")
    print("PASS literal small-rank matrix support on",small,"coordinate lists")


if __name__ == "__main__":
    main()
