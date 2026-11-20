"""Independent comparisons on ternary-address quadratic Boolean data."""

import argparse
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from random import Random
import sys


def gf2_rank(rows):
    basis = {}
    for row in rows:
        while row:
            i = row.bit_length()-1
            if i not in basis:
                basis[i] = row
                break
            row ^= basis[i]
    return len(basis)


def graph(m, seed):
    rng = Random(seed)
    rows = [0]*m
    for i,j in combinations(range(m),2):
        if rng.randrange(2):
            rows[i] |= 1 << j
            rows[j] |= 1 << i
    return rows


def cuts(m):
    full = (1 << m)-1
    low = (m+2)//3
    for size in range(low,m//2+1):
        for indices in combinations(range(m),size):
            if 2*size == m and indices[0] != 0:
                continue
            a = sum(1 << i for i in indices)
            yield indices, full ^ a


def minimum_rank(rows):
    n = 0
    best = len(rows)
    for indices, other in cuts(len(rows)):
        best = min(best, gf2_rank([rows[i] & other for i in indices]))
        n += 1
    return best, n


def sign(rows, x):
    # Select only edges below each diagonal entry.
    parity = 0
    for i,row in enumerate(rows):
        if (x >> i) & 1:
            parity ^= (row & x & ((1 << i)-1)).bit_count() & 1
    return 1 - 2*parity


def coordinates(indices):
    positions = [0]
    for j in indices:
        positions += [v | (1 << j) for v in positions]
    return positions


def odd_rank(matrix, p=101):
    a = [[x%p for x in row] for row in matrix]
    rank = 0
    for j in range(len(a[0])):
        pivot = next((i for i in range(rank,len(a)) if a[i][j]),None)
        if pivot is None:
            continue
        a[rank],a[pivot] = a[pivot],a[rank]
        inv = pow(a[rank][j],-1,p)
        for i in range(rank+1,len(a)):
            factor = a[i][j]*inv%p
            if factor:
                for k in range(j,len(a[i])):
                    a[i][k] = (a[i][k]-factor*a[rank][k])%p
        rank += 1
        if rank == len(a):
            break
    return rank


def check_characters():
    rows = graph(8,31)
    signed = [sign(rows,i) for i in range(256)]
    n = 0
    for indices, other in cuts(8):
        left = coordinates(indices)
        right = coordinates([i for i in range(8) if (other >> i) & 1])
        matrix = [[signed[i|j] for j in right] for i in left]
        k = gf2_rank([rows[i] & other for i in indices])
        if odd_rank(matrix) != 1 << k:
            raise ValueError("Incorrect signed tensor rank")
        if odd_rank([[(1-z)//2 for z in row] for row in matrix]) < (1 << k)-1:
            raise ValueError("Incorrect Boolean tensor rank")
        n += 1
    return n


def tensor_karatsuba(left, right, width, meter):
    """Return all coefficients in ternary digit order. Count literal integer operations."""
    if width == 0:
        meter["products"] += 1
        meter["leaf_bits"] += max(1,left[0].bit_length())+max(1,right[0].bit_length())
        return [left[0]*right[0]]
    cut = len(left)//2
    lo_a, hi_a = left[:cut],left[cut:]
    lo_b, hi_b = right[:cut],right[cut:]
    meter["evaluation_adds"] += 2*cut
    mid_a = [a+b for a,b in zip(lo_a,hi_a,strict=True)]
    mid_b = [a+b for a,b in zip(lo_b,hi_b,strict=True)]
    low = tensor_karatsuba(lo_a,lo_b,width-1,meter)
    mid = tensor_karatsuba(mid_a,mid_b,width-1,meter)
    high = tensor_karatsuba(hi_a,hi_b,width-1,meter)
    meter["interpolation_subs"] += 2*len(mid)
    return low + [b-a-c for a,b,c in zip(low,mid,high,strict=True)] + high


def cantor(x):
    result = 0
    power = 1
    while x:
        if x&1:
            result += power
        x >>= 1
        power *= 3
    return result


def karatsuba_check(m):
    left_rows, right_rows = graph(m,1122),graph(m,7221)
    def family(rows):
        return [(x & 1) ^ ((1-sign(rows,x & ~1))//2) for x in range(1 << m)]
    left, right = family(left_rows), family(right_rows)
    meter = dict(products=0,leaf_bits=0,evaluation_adds=0,interpolation_subs=0)
    signal = tensor_karatsuba(left,right,m,meter)
    literal_left = sum(v << cantor(j) for j,v in enumerate(left))
    literal_right = sum(v << cantor(j) for j,v in enumerate(right))
    assembled = sum(v << j for j,v in enumerate(signal))
    if assembled != literal_left*literal_right:
        raise ValueError("Rank-three evaluation or interpolation changed the product")
    if (meter["products"] != 3**m or meter["interpolation_subs"] != 2*m*3**(m-1)
            or meter["evaluation_adds"] != 2*(3**m-2**m)):
        raise ValueError("The arithmetic schedule changed")
    for high in range(3**(m-1)):
        w, digits = 0, high
        while digits:
            digits, tone = divmod(digits,3)
            w += int(tone == 1)
        if sum(signal[3*high:3*high+3]) != 1 << w:
            raise ValueError("The three low-trit coefficients lost an orientation")
    bits = sum(max(1,v.bit_length()) for v in signal)
    return sum(left)*sum(right), bits, meter


def full_sweep_bound(expansion_sizes):
    """At most one support doubling per local H stage in its serialized width class."""
    rows = {}
    for r in expansion_sizes:
        b = (r-1).bit_length()
        rows[b] = max(rows.get(b,0), b)
    return sum(rows.values())


def dense_witness(program):
    """Call the real product on two dense words with selector and all-cut certificates."""
    sys.path.insert(0,str(program))
    from multiply import multiply_bits
    from templates import pack, unpack
    m = 8
    width = 1 << (m//2)
    extent = 3**m
    count = extent//width
    length = count*width
    periods = (0xad6d,0xb34d)
    geometric = ((1 << length)-1)//((1 << width)-1)
    signals, ranks, chosen = [], [], []
    for initial in (30,130):
        for seed in range(initial,initial+100):
            core = graph(m-1,seed)
            rows = [0] + [v << 1 for v in core]
            smallest, examined = minimum_rank(rows)
            if smallest < 2:
                continue
            sign_table = [(x & 1) ^ ((1-sign(rows,x))//2) for x in range(1 << m)]
            signals.append(sign_table)
            ranks.append(smallest)
            chosen.append(seed)
            break
        else:
            raise ValueError("No all-cut certificate for the fixture")
    sparse = [sum(v << cantor(j) for j,v in enumerate(s)) for s in signals]
    operands = [periods[0]*geometric+(sparse[0]<<width),periods[1]*geometric-(sparse[1]<<width)]
    supplied = [unpack(v,length) for v in operands]
    evidence = {}
    output = multiply_bits(*supplied,evidence=evidence)
    if (pack(output) != operands[0]*operands[1] or evidence["route"] != "clifford"
            or evidence["shifts"] != [width,width] or evidence["signs"] != [1,-1]):
        raise ValueError("The hard dense input missed its actual arithmetic route")
    if any(not length//3 < v.bit_count() < 2*length//3 for v in operands):
        raise ValueError("Dense binary words lost the promised finite density")
    receipt = dict(products=0,leaf_bits=0,evaluation_adds=0,interpolation_subs=0)
    coefficient = tensor_karatsuba(*signals,m,receipt)
    for high in range(3**(m-1)):
        w, v = 0, high
        while v:
            v, trit = divmod(v,3)
            w += int(trit == 1)
        if sum(coefficient[3*high:3*high+3]) != 1 << w:
            raise ValueError("Selector-fibre equality failed on the physical witness")
    print("dense-caller",(m,width,count,length),"period words",periods,"graph seeds",chosen,
          "all-cuts",examined,"minimum ranks",ranks,"input ones",[v.bit_count() for v in operands])
    print("defect coefficients",len(coefficient),"nonzero",sum(v>0 for v in coefficient),
          "literal magnitude bits",sum(max(1,v.bit_length()) for v in coefficient),
          "public result bits",len(output),"sha256(low-first literal bits)",sha256(output).hexdigest())
    print("signed defect delivery",evidence["delivery"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--program",type=Path,default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    print("literal character cuts",check_characters())
    for m in (12,16,18):
        g = graph(m,10000+m)
        minrank,count = minimum_rank(g)
        if minrank <= m//12:
            raise ValueError("The hard graph fell below its all-cuts bound")
        edges = sum(row.bit_count() for row in g)//2
        print("hard fixture",m,edges,"edges,",count,"balanced cuts, minimum GF(2) rank",minrank)
    for m in (4,6,8):
        pairs,bits,receipt = karatsuba_check(m)
        print("literal ternary comparator",m,pairs,"positive pairs,",bits,
              "output coefficient bits",receipt)
    if full_sweep_bound([9,25]) != 9:
        raise ValueError("The two serial padded classes need four and five support doublings")
    dense_witness(args.program.resolve())
    print("PASS_TERNARY_ADDRESS_COMPARATORS")
