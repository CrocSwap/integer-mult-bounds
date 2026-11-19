"""Convert a four-qubit binary symplectic map and optional absolute lift to the tape's normal form."""
from itertools import combinations
import argparse
import json
from pathlib import Path

PAIRS = tuple(combinations(range(4),2))
BASIS = (1,2,4,8)


def columns_apply(columns, value):
    result = 0
    for i,col in enumerate(columns):
        if value & (1 << i):
            result ^= col
    return result


def parity(x):
    return x.bit_count() & 1


def pairing(v,w):
    return parity(((v >> 4) & w & 15) ^ ((w >> 4) & v & 15))


def transpose(columns):
    return [sum(((v >> i) & 1) << j for j,v in enumerate(columns)) for i in range(4)]


def quadratic(data,v):
    return (sum(a for i,a in enumerate(data["linear"]) if v & (1 << i)) +
            2*sum((data["cross"] >> k)&1 for k,(i,j) in enumerate(PAIRS)
                  if v&(1<<i) and v&(1<<j))) % 4


def linear(data,v):
    return sum(parity(row & v) << i for i,row in enumerate(data["rows"]))


def mono(matrix_columns, form_columns):
    if transpose(form_columns)!=list(form_columns):
        raise ValueError("Asymmetric monomial phase")
    return dict(rows=transpose(matrix_columns),shift=0,
                linear=[(col>>i)&1 for i,col in enumerate(form_columns)],
                cross=sum(((form_columns[i]>>j)&1)<<k for k,(i,j) in enumerate(PAIRS)))


def factor(sym):
    if len(sym)!=8 or any(type(v) is not int or not 0<=v<256 for v in sym):
        raise ValueError("Expected eight 8-bit symplectic columns")
    if any(pairing(sym[i],sym[j])!=pairing(1<<i,1<<j) for i,j in combinations(range(8),2)):
        raise ValueError("Matrix does not preserve the Pauli pairing")
    # Select a basis of the X projection of SZ and extend to the computational four-space.
    basis, chosen = [], []
    space = {0}
    for s in sym[:4]:
        x=s>>4
        if x not in space:
            basis.append(x)
            chosen.append(s)
            space |= {v^x for v in space}
    h=len(chosen)
    mask=(1<<h)-1
    for x in BASIS:
        if x not in space:
            basis.append(x)
            space |= {v^x for v in space}
    form = [(sum(parity(v & (s&15)) << j for j,v in enumerate(basis)) & mask)
            for s in chosen] + [0]*(4-h)
    # basis columns encode A^{-1}. The symmetric shear is in the output coordinates of A.
    inverse_map = {columns_apply(basis,v):v for v in range(16)}
    a_cols=[inverse_map[v] for v in BASIS]
    a_rows=transpose(a_cols)
    pulled=[columns_apply(a_rows,columns_apply(form,col)) for col in a_cols]
    left=mono(a_cols,pulled)
    def transform(p):
        x = inverse_map[p>>4]
        z = columns_apply(transpose(basis),p&15) ^ columns_apply(form,x)
        swap = (x^z)&mask
        return ((x^swap)<<4) | (z^swap)
    # The right factor H_mask P_left S preserves Z.
    right_columns=list(map(transform,sym))
    if any(col>>4 for col in right_columns[:4]):
        raise ValueError("Lagrangian reduction")
    matrix = [col>>4 for col in right_columns[4:]]
    right=mono(matrix,[columns_apply(transpose(matrix),col&15) for col in right_columns[4:]])
    return dict(left=left,right=right,mask=mask,phase=0)


def rotate(pair,power):
    a,b=pair
    return ((a,b),(-b,a),(-a,-b),(b,-a))[power%4]


def entry_numerator(form,r,c):
    """Absolute matrix element, with common denominator 2**popcount(mask)."""
    left,right,mask=form["left"],form["right"],form["mask"]
    a,b=linear(left,r)^left["shift"],linear(right,c)^right["shift"]
    if (a^b)&~mask:
        return (0,0)
    amplitude=(1,0)
    for _ in range(mask.bit_count()):
        u,v=amplitude
        amplitude=(u-v,u+v)
    return rotate(amplitude,form["phase"]+quadratic(right,c)-quadratic(left,r)+2*parity(a&b&mask))


def compile_lift(sym,entries=None,denominator_bits=0):
    form=factor(sym)
    if entries is None:
        return form
    if type(denominator_bits) is not int or denominator_bits<0 or len(entries)!=256 or any(
            len(v)!=2 or any(type(a) is not int for a in v) for v in entries):
        raise ValueError("Supply 256 Gaussian integer pairs in row-major order and a dyadic scale")
    h=form["mask"].bit_count()
    wanted=[(a<<h,b<<h) for a,b in entries]
    literal=[tuple(u<<denominator_bits for u in entry_numerator(form,r,c))
             for r in range(16) for c in range(16)]
    anchor=next((i for i,x in enumerate(wanted) if x!=(0,0)),None)
    if anchor is None:
        raise ValueError("Zero lift")
    # Compare U with i^g X^x Z^z N; each candidate is fixed by one nonzero entry.
    for x in range(16):
        for z in range(16):
            def candidate(i,g):
                rv=(i//16)^x
                return rotate(literal[rv*16+(i%16)],g+2*parity(z&rv))
            for g in range(4):
                if candidate(anchor,g)!=wanted[anchor] or any(candidate(i,g)!=v for i,v in enumerate(wanted)):
                    continue
                left=form["left"]
                constant=(quadratic(left,x)+2*parity(z&x))%4
                phase_at=lambda v:(quadratic(left,v^x)+2*parity(z&(v^x))-constant)%4
                left["linear"]=[phase_at(v) for v in BASIS]
                # Translation preserves the quadratic cross coefficients.
                left["shift"] ^= linear(left,x)
                form["phase"]=(g-constant)%4
                return form
    raise ValueError("The absolute table is not a Gaussian-dyadic unitary lift of this symplectic map")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path)
    req=json.loads(parser.parse_args().input.read_text())
    print(json.dumps(compile_lift(req["symplectic"],req.get("entries"),req.get("denominator_bits",0))))
