"""Recompute the flank-rank certificates from two published character tables.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
See the package credit for the character formulas and the original data.
The two positional arguments are PROJECTION.json and CHARACTER-COLUMNS.json.
"""
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement
import json
from pathlib import Path
import sys


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_table(name, digest):
    data = Path(name).read_bytes()
    require(sha256(data).hexdigest() == digest, "Wrong source bytes")
    return json.loads(data)


def multiplicities(rows, order, point):
    values = []
    for index, (degree, *middle) in enumerate(rows):
        bins = [(order if index == 0 else 0) - sum(middle) - degree, *middle, degree]
        total = 0
        for part in reversed(bins):
            total = point * total + part
        m, remainder = divmod(total, order)
        require(m >= 0 and remainder == 0, "Invalid multiplicity")
        values.append(m)
    return values


def strict_cap(weights, total):
    """Return the top-row cardinality and the exact last and next sums.

    Each weight is a pair (a,b) for a+b*sqrt(2), with one entry zero.
    """
    def below(a, b):
        return a < total and (total - a) ** 2 > 2 * b * b

    count, a, b = 0, 0, 0
    for (x, y), copies in sorted(weights.items(), key=lambda item: item[0][0]**2 + 2*item[0][1]**2, reverse=True):
        require(min(x, y) >= 0 and x * y == 0 and copies > 0, "Invalid modulus class")
        if below(a + copies * x, b + copies * y):
            count, a, b = count + copies, a + copies * x, b + copies * y
            continue
        lo, hi = 0, copies
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if below(a + mid * x, b + mid * y):
                lo = mid
            else:
                hi = mid
        last = (a + lo * x, b + lo * y)
        following = (last[0] + x, last[1] + y)
        require(below(*last) and not below(*following), "Invalid strict row cutoff")
        return count + lo, last, following
    raise ValueError("No row cutoff")


def check_sources(projection, column_file):
    order = 2**16
    for j in range(1, 5):
        order *= 2**(2*j) - 1
    group = 256 * order
    rows = projection["rows"]
    counts = projection["element_counts"]
    columns = column_file["columns"]
    require(len(rows) == len(columns) == 81 and sum(counts) == order, "Group dimensions")
    require(sum(row[0]**2 for row in rows) == order, "Ordinary degree sum")
    m11 = multiplicities(rows, order, -32)
    m13 = multiplicities(rows, order, -64)
    require(sum(row[0]*m for row, m in zip(rows, m11)) == 2**40, "Width 11 dimension")
    require(sum(row[0]*m for row, m in zip(rows, m13)) == 2**48, "Width 13 dimension")
    missing = [i for i, m in enumerate(m11, 1) if not m]
    require(missing == [9, 22] and min(m13) > 0, "Wrong absent quotient blocks")
    degrees = [rows[i-1][0] for i in missing]
    null12 = sum(e*e for e in degrees)
    null11 = 256 * null12
    spectrum = [(Fraction(order*m, 2**48*row[0]), (16*row[0])**2) for row, m in zip(rows, m13)]
    require(sum(s*d for s,d in spectrum) == group, "Width 13 Gram trace")
    second = group * sum(Fraction(c*2**(12*j), 2**96) for j,c in enumerate(counts))
    require(sum(s*s*d for s,d in spectrum) == second, "Width 13 square trace")
    require(min(s for s,_ in spectrum) == Fraction(470624175, 4294967296), "Width 13 minimum")
    require(max(s for s,_ in spectrum) == Fraction(7841980575, 1073741824), "Width 13 maximum")
    require(len({s for s,_ in spectrum}) == 52, "Width 13 level count")

    which = column_file["one_based_rows"]
    require(which == [5, 6, 9, 22], "Wrong rows for the restriction test")
    bins = [0] * 9
    projected = [[0]*9 for _ in which]
    orthogonal = [[0]*4 for _ in which]
    outside = []
    eleven, twelve = Counter(), Counter()
    for j, col in enumerate(columns, 1):
        require(col["index"] == j, "Invalid class index")
        a,b,c,d = col["values"]
        value = 2 + a + b
        k = value.bit_length() - 1
        size, rem = divmod(order, col["centralizer"])
        require(rem == 0 and k in range(9) and value == 2**k, "Invalid class size or fixed space")
        bins[k] += size
        for t, v in enumerate(col["values"]):
            projected[t][k] += size*v
            for u, w in enumerate(col["values"]):
                orthogonal[t][u] += size*v*w
        if k == 0:
            outside.append((c, d))
        weight = abs(degrees[0]*c + degrees[1]*d)
        twelve[weight,0] += size
        w = 16 * weight * 2**(k//2)
        a11,b11 = (0,w) if k%2 else (w,0)
        eleven[a11,b11] += size*(256//value)
        if value > 1:
            eleven[0,0] += size*(256 - 256//value)
    require(bins == counts, "Mismatched fixed-space census")
    require(all(orthogonal[i][j] == order*int(i == j) for i in range(4) for j in range(4)), "Row orthogonality")
    require(all(values[1:] == [*rows[r-1][1:],rows[r-1][0]] for values,r in zip(projected,which)), "Original projection mismatch")
    require((10,0) in outside and (0,3) in outside, "Missing rank-two outside-stabilizer witness")
    require(sum(eleven.values()) == group and sum(twelve.values()) == order, "Row pair counts")
    n11, last11, next11 = strict_cap(eleven, group)
    n12, last12, next12 = strict_cap(twelve, order)
    require((null11,null12,group) == (2733412864,10677394,12128668876800), "Nullities or dictionary order")
    require((n11, n12) == (447742, 226718), "Strict sparse or fibre cap")
    print("Flank nullities at 11, 12, 13:", null11, null12, 0)
    print("Width 13 rank and least eigenvalue:", group, min(s for s,_ in spectrum))
    print("Width 11 labels, last and next sums (a,b) for a+b*sqrt(2):", n11, last11, next11)
    print("Width 12 full fibres, last and next integer sums:", n12, last12[0], next12[0])
    print("Width 25 arbitrary labels:", 256*(n12+1)-1)


def small_kernel():
    # Exact Gaussian integers as ordered pairs, followed by a rank
    # lower certificate in F17 under i -> 4.
    units = ((1,0),(0,1),(-1,0),(0,-1))
    def norm(z):
        return z[0]**2+z[1]**2
    def add(a,b,sign=1):
        return (a[0]+sign*b[0], a[1]+sign*b[1])
    def times(a,b):
        return (a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0])
    def normalized(v):
        a = next(z for z in v if norm(z))
        scale = norm(a)
        result = []
        for z in v:
            r,i = times(z,(a[0],-a[1]))
            require(r%scale == i%scale == 0, "Nonintegral phase")
            value = (r//scale,i//scale)
            require(value == (0,0) or value in units, "Nonflat Clifford")
            result.append(value)
        return tuple(result)
    def rank_mod17(matrix):
        pivots = {}
        for row in matrix:
            r = [x%17 for x in row]
            for j in sorted(pivots):
                if r[j]:
                    r = [(x-r[j]*y)%17 for x,y in zip(r,pivots[j])]
            pivot = next((j for j,x in enumerate(r) if x),None)
            if pivot is not None:
                inv = pow(r[pivot],-1,17)
                pivots[pivot] = [(inv*x)%17 for x in r]
        return len(pivots)

    identity = (units[0],(0,0),(0,0),units[0])
    todo, group = [identity], {identity}
    while todo:
        a,b,c,d = todo.pop()
        for raw in [(a,b,times(units[1],c),times(units[1],d)),
                    (add(a,c),add(b,d),add(a,c,-1),add(b,d,-1))]:
            U = normalized(raw)
            if U not in group:
                group.add(U)
                todo.append(U)
    group = sorted(group)
    require(len(group) == 24, "One-qubit projective group order")
    rows = []
    for indices in combinations_with_replacement(range(4),4):
        row = []
        for U in group:
            # Four times the fourth power of (1+i)^(-h) is 4 or -1.
            scale = 4 if sum(z!=(0,0) for z in U)==2 else -1
            result = (scale,0)
            for index in indices:
                result = times(result,U[index])
            row.append(result)
        require(tuple(map(sum,zip(*row))) == (0,0), "Constant vector outside the kernel")
        rows.append([(a+4*b)%17 for a,b in row])
    ranks = [rank_mod17([row[:j]+row[j+1:] for row in rows]) for j in range(24)]
    require(ranks == [23]*24, "A proper support is dependent")
    # The real unit vector (1,...,1)/sqrt(24) spans the literal kernel.
    # The projector is J/24; the top 23 entries of a row sum to 23/24.
    require(strict_cap({(1,0):24},24) == (23,(23,0),(24,0)), "Wrong literal projection cap")
    print("One-qubit width 4: all 24 single-column deletions have rank 23; full nullspace is the constant line")


if __name__ == "__main__":
    p = read_table(sys.argv[1], "0a36754668b66480e5f968c117a4532bc3a5eaab5c9d8448f14a5d0321c2efae")
    c = read_table(sys.argv[2], "9b41c7569bb4c425a53eaec10ccba3eb33a7e8d595bbdf9be2041efb073eb384")
    check_sources(p,c)
    small_kernel()
