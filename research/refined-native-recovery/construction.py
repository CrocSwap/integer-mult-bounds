"""Explicit source-sized rank-four mode-preserving shear.

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This module constructs a mathematical integer map, not a physical cost claim.
"""
from itertools import product

SELECTORS = (0, 1, 2, 4)
COLUMNS = (
    ((64, 1), (65, -1), (96, -1), (97, 1)),
    ((10, 1), (11, -1), (62, 1), (63, -1)),
    ((14, 1), (15, -1), (41, 1), (42, -1)),
    ((18, 1), (19, -1), (39, 1), (40, -1)),
)
DUAL_ROWS = ((4, 64), (10, 70), (14, 52), (18, 54))


def require(value, message):
    if not value:
        raise ValueError(message)


def matrices():
    e = [[int(i == k) for i in range(112)] for k in SELECTORS]
    v = [[0] * 4 for _ in range(112)]
    l = [[int(i in pair) for i in range(112)] for pair in DUAL_ROWS]
    for j, column in enumerate(COLUMNS):
        for i, value in column:
            v[i][j] = value
    return e, v, l


def transpose(m):
    return list(map(list, zip(*m)))


def multiply(a, b):
    cols = transpose(b)
    return [[sum(x*y for x,y in zip(row,col)) for col in cols] for row in a]


def f2rank(rows):
    pivots = {}
    for row in rows:
        value = sum((x & 1) << j for j,x in enumerate(row))
        while value:
            pivot = value.bit_length()-1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def validate(m, e, v, l):
    require(len(m) == 112 and all(len(row) == 8 for row in m), 'matrix shape')
    require(len(e) == len(l) == 4 and all(len(row) == 112 for row in e+l), 'row shapes')
    require(len(v) == 112 and all(len(row) == 4 for row in v), 'column shape')
    require(all(type(x) is int for a in (m,e,v,l) for row in a for x in row), 'integer matrices')
    require(multiply(transpose(m),m) == [[56*int(i==j) for j in range(8)] for i in range(8)], 'source Gram')
    require(multiply(transpose(m),v) == [[0]*4 for _ in range(8)], 'exact native-mode kernel')
    require(multiply(e,v) == [[0]*4 for _ in range(4)], 'nilpotent shear')
    require(all(x%2 == 0 for row in multiply(l,m) for x in row), 'dual annihilator')
    require(multiply(l,v) == [[int(i==j) for j in range(4)] for i in range(4)], 'dual quotient basis')
    require(f2rank(m) == 4 and f2rank(multiply(e,m)) == 4, 'full code row space')
    require(f2rank([a+b for a,b in zip(m,v)]) == 8, 'quotient independence')
    code = [mask for mask in range(256) if all(sum(x*((mask>>j)&1) for j,x in enumerate(row))%2==0 for row in m)]
    em = [sum((x&1)<<j for j,x in enumerate(row)) for row in multiply(e,m)]
    rowcode = {0}
    for row in em:
        rowcode |= {x^row for x in rowcode}
    require(set(code) == rowcode and len(code) == 16, 'self-dual Hamming code equality')
    require(all((x&y).bit_count()%2 == 0 for x,y in product(code,repeat=2)), 'code orthogonality')
    return code


def apply_u(x, inverse=False):
    require(len(x) == 112 and all(type(a) is int for a in x), 'integer owner vector')
    out = list(x)
    sign = -1 if inverse else 1
    for source, column in zip(SELECTORS,COLUMNS):
        for destination,value in column:
            out[destination] += sign*value*x[source]
    return out


def project(m,x):
    return [sum(row[j]*a for row,a in zip(m,x)) for j in range(8)]


def lift(m,q):
    return [sum(a*b for a,b in zip(row,q)) for row in m]


def nearest(n):
    require(type(n) is int, 'round exact integer')
    return ((abs(n)+26)//52)*(1 if n>=0 else -1)


def kernel(m,x):
    correction=lift(m,[nearest(a) for a in project(m,x)])
    return [a-b for a,b in zip(x,correction)]


def forward(m,x):
    return kernel(m,apply_u(kernel(m,[2*a for a in x])))


def scalar_step(s,t):
    return t-nearest(s+56*t)


def inverse_from_total(m,y,total):
    require(len(y)==112 and len(total)==8 and all(type(a) is int for a in y+total), 'exact inverse dimensions')
    s=project(m,y)
    q2=[scalar_step(a,t) for a,t in zip(s,total)]
    require(all(scalar_step(a,q)==0 for a,q in zip(s,q2)), 'scalar total outside two-step inverse')
    q1=[t-q for t,q in zip(total,q2)]
    back=apply_u([a+b for a,b in zip(y,lift(m,q2))],inverse=True)
    numerator=[a+b for a,b in zip(back,lift(m,q1))]
    require(all(a%2==0 for a in numerator), 'nonintegral inverse')
    x=[a//2 for a in numerator]
    require(forward(m,x)==y, 'literal two-step inverse replay')
    return x


def total_for_input(m,x,y):
    delta=[2*a-b for a,b in zip(project(m,x),project(m,y))]
    require(all(a%56==0 for a in delta), 'integer total quotient')
    return [a//56 for a in delta]
