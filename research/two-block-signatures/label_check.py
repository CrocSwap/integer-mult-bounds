#!/usr/bin/env python3
"""Read every six-port labeled witness by a literal integer or binary elimination."""
from collections import Counter
import json
from pathlib import Path
import sys

PACKAGE = Path(__file__).resolve().parent
sys.path.insert(0,str(PACKAGE))
from construction_check import labeled_codes, need
from signatures import witness


def scaled_inverse(matrix):
    """Fraction-free Gauss-Jordan on [P | I]. A common scale suffices for all zero tests."""
    n = len(matrix)
    rows = [list(row) + [int(i == j) for j in range(n)] for i,row in enumerate(matrix)]
    previous = 1
    for k in range(n):
        pivot_row = next((i for i in range(k,n) if rows[i][k]), None)
        need(pivot_row is not None, "integer witness singular")
        rows[k],rows[pivot_row] = rows[pivot_row],rows[k]
        pivot = rows[k][k]
        for i in range(n):
            if i == k:
                continue
            old = rows[i]
            new = [(pivot*x - old[k]*y)//previous for x,y in zip(old,rows[k],strict=True)]
            rows[i] = new
        previous = pivot
    need(all(rows[i][:n] == [previous*int(i == j) for j in range(n)] for i in range(n)),
         "fraction-free left block")
    return previous, [row[n:] for row in rows]


def read_scaled(matrix, scale, right, modulus):
    """Check P times the returned matrix equals scale times the identity over Z."""
    n = len(matrix)
    need(all(sum(x*y for x,y in zip(row,col,strict=True)) == scale*int(i == j)
             for j,col in enumerate(zip(*right,strict=True)) for i,row in enumerate(matrix)),
         "scaled inverse product")
    if modulus:
        need(scale % modulus != 0, "witness singular modulo prime")
    out = []
    for j in range(n):
        s = int(any(matrix[i][j] for i in range(3))) + 2*int(any(matrix[i][j] for i in range(3,n)))
        vals = [x % modulus if modulus else x for x in right[j]]
        r = int(any(vals[:3])) + 2*int(any(vals[3:]))
        out.append(4*s+r)
    return tuple(out)


def binary_masks(matrix):
    rows = [sum(x<<j for j,x in enumerate(vec)) | (1<<(6+i)) for i,vec in enumerate(matrix)]
    for j in range(6):
        i = next((i for i in range(j,6) if (rows[i]>>j)&1), None)
        need(i is not None, "labeled binary witness singular")
        rows[i],rows[j] = rows[j],rows[i]
        for k in range(6):
            if k != j and (rows[k]>>j)&1:
                rows[k] ^= rows[j]
    result = []
    for j in range(6):
        s = int(any(row[j] for row in matrix[:3])) + 2*int(any(row[j] for row in matrix[3:]))
        inverse_row = rows[j] >> 6
        r = int(bool(inverse_row & 7)) + 2*int(bool(inverse_row & 56))
        result.append(4*s+r)
    return tuple(result)


def recount():
    rational = labeled_codes(3,3)
    binary = labeled_codes(3,3,True)
    determinants = Counter()
    for key in sorted(rational):
        symbols = tuple((key >> (4*j)) & 15 for j in range(6))
        for label, modulus in (("Q",0),("F3",3)):
            mat = witness(3,3,symbols,label)
            scale, right = scaled_inverse(mat)
            need(read_scaled(mat,scale,right,modulus) == symbols, "labeled masks differ")
            if not modulus:
                determinants[abs(scale)] += 1
        if key in binary:
            need(binary_masks(witness(3,3,symbols,"F2")) == symbols, "labeled binary masks differ")
    return dict(rational=len(rational), F3=len(rational), F2=len(binary),
                rational_abs_determinants=dict(sorted(determinants.items())))


if __name__ == "__main__":
    actual = json.loads(json.dumps(recount()))
    expected = json.loads((PACKAGE/"RESULT.json").read_bytes())["labeled_witnesses"]
    need(actual == expected, "stored labeled witness receipt differs")
    print(json.dumps({"status":"PASS_TWO_BLOCK_LABELED_WITNESSES","result":actual},sort_keys=True))
