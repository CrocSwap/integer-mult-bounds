#!/usr/bin/env python3
"""Check the reciprocal family with an independent vector interpreter."""
from fractions import Fraction as F
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
CAMPAIGN = HERE.parents[2]
SOURCE = CAMPAIGN / 'lanes/new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz'
PIN = 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa'
PROOF_PIN = 'd2209a60d45d52b6b1d8fed622820acd3468330cc0af926719c3a8747a2606b9'


def need(test, label):
    if not test:
        raise ValueError(label)


def eye(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def add(a, b, factor=F(1)):
    return [[x + factor*y for x, y in zip(u, v)] for u, v in zip(a, b)]


def scale(a, factor):
    return [[factor*x for x in row] for row in a]


def vector(a, x):
    return [sum((value*x[j] for j, value in enumerate(row) if value), F(0))
            for row in a]


def product(a, b):
    columns = list(zip(*b))
    return [[sum((u*v for u, v in zip(row, col)), F(0))
             for col in columns] for row in a]


def rank(a):
    work = [list(row) for row in a]
    pivot = 0
    for col in range(len(work[0])):
        hit = next((i for i in range(pivot, len(work)) if work[i][col]), None)
        if hit is None:
            continue
        work[pivot], work[hit] = work[hit], work[pivot]
        divisor = work[pivot][col]
        work[pivot] = [x/divisor for x in work[pivot]]
        for i in range(len(work)):
            if i != pivot and work[i][col]:
                amount = work[i][col]
                work[i] = [x-amount*y for x, y in zip(work[i], work[pivot])]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


def inverse(a):
    n = len(a)
    work = [list(row)+unit for row, unit in zip(a, eye(n))]
    for col in range(n):
        hit = next(i for i in range(col, n) if work[i][col])
        work[col], work[hit] = work[hit], work[col]
        divisor = work[col][col]
        work[col] = [x/divisor for x in work[col]]
        for i in range(n):
            if i != col:
                amount = work[i][col]
                work[i] = [x-amount*y for x, y in zip(work[i], work[col])]
    return [row[n:] for row in work]


def reduction13(a):
    return [[int(x.numerator)*pow(int(x.denominator), -1, 13) % 13
             for x in row] for row in a]


raw = gzip.decompress(SOURCE.read_bytes())
need(sha256(raw).hexdigest() == PIN, 'Actual source pin')
proof = CAMPAIGN / 'root/RECIPROCAL-CENTRE-RANK-20261018.md'
need(sha256(proof.read_bytes()).hexdigest() == PROOF_PIN, 'Reviewed proof pin')
source = json.loads(raw)
R = [[F(row.get(str(i), 0)) for i in range(112)] for row in source['R']]
need(len(R) == 8, 'Eight actual centre rows')
K = [[R[j][i]/4 for j in range(8)] for i in range(112)]
I8 = eye(8)
need(product(R, K) == scale(I8, 14), 'Actual RK=14I')
need(rank(R) == rank(K) == 8, 'Actual two full ranks')
need(all(sum(abs(x) for x in row) == 56 for row in R), 'R row norm')
need(all(sum(abs(x) for x in row) == 1 for row in K), 'K row norm')


def response(m, x):
    centre = vector(R, x)
    correction = [a-b for a, b in zip(vector(m, centre), centre)]
    return [a+b for a, b in zip(x, vector(K, correction))]


def bracket(m, n):
    return add(add(scale(I8, 12), add(m, n), F(-13)), product(m, n), F(14))


def zero(a):
    return all(not x for row in a for x in row)


full_cases = []


def check_pair(m, n, label):
    need(zero(bracket(m, n)), label+' ordered bracket')
    need(zero(bracket(n, m)), label+' reverse bracket')
    need(product(m, n) == product(n, m), label+' consequent commutation')
    for col in range(112):
        x = [F(i == col) for i in range(112)]
        need(response(m, response(n, x)) == x, label+' EG column '+str(col))
        need(response(n, response(m, x)) == x, label+' GE column '+str(col))
    need(rank(product(m, R)) == rank(m), label+' query rank M')
    need(rank(product(n, R)) == rank(n), label+' query rank N')
    full_cases.append({'label': label, 'rank_M': rank(m), 'rank_N': rank(n),
                       'basis_columns_per_order': 112})


coefficient = F(12, 13)
rank_counts = {}
for mask in range(256):
    p = [[F(i == j and (mask >> i) & 1) for j in range(8)] for i in range(8)]
    m, n = scale(p, coefficient), scale(add(I8, p, F(-1)), coefficient)
    need(zero(bracket(m, n)), 'Coordinate bracket '+str(mask))
    rm, rn = rank(m), rank(n)
    need(rm+rn == 8, 'Coordinate sharp rank sum')
    rank_counts[str(rm)] = rank_counts.get(str(rm), 0)+1
    if mask in (0, 1, 15, 127, 255):
        check_pair(m, n, 'coordinate-'+str(mask))

p = [[F(i == j and i < 4) for j in range(8)] for i in range(8)]
for i in range(4):
    for j in range(4, 8):
        p[i][j] = F((i+1)*(j-3)-3, 2**(i+j-3))
need(product(p, p) == p, 'Noncoordinate projection')
need(p != list(map(list, zip(*p))), 'Projection need not be self-adjoint')
m, n = scale(p, coefficient), scale(add(I8, p, F(-1)), coefficient)
check_pair(m, n, 'noncoordinate-rank-four')

unit = eye(8)
unit[0][0], unit[0][1], unit[1][1] = F(2), F(3), F(5)
m = scale(add(unit, scale(I8, 13)), F(1, 14))
n = scale(add(inverse(unit), scale(I8, 13)), F(1, 14))
check_pair(m, n, 'general-centre-unit')

nilpotent = [[F(0) for _ in range(8)] for _ in range(8)]
nilpotent[0][1] = F(3, 8)
need(zero(product(nilpotent, nilpotent)), 'Square-zero example')
m, n = add(I8, nilpotent), add(I8, nilpotent, F(-1))
check_pair(m, n, 'nontrivial-dyadic-full-rank')
reduced_product = product(reduction13(m), reduction13(n))
need([[x % 13 for x in row] for row in reduced_product] == eye(8),
     'Reduction gives two units')

m = [[F(i == j and i < 4) for j in range(8)] for i in range(8)]
t = add(scale(m, 14), scale(I8, 13), F(-1))
n = product(inverse(t), add(scale(m, 13), scale(I8, 12), F(-1)))
check_pair(m, n, '13-integral-rank-four-forces-full-rank-partner')
need(rank(m) == 4 and rank(n) == 8, 'Integral-side consequence')

left = scale(I8, F(1, 2))
right = eye(8)
left[0][1], right[1][0] = F(3, 2), F(2)
need(product(left, right) != product(right, left), 'Noncommuting test input')
ordered = bracket(left, right)
reverse = bracket(right, left)
need(ordered != reverse, 'Order affects the centre residual')
for col in range(112):
    x = [F(i == col) for i in range(112)]
    lhs = [a-b for a, b in zip(response(left, response(right, x)), x)]
    rhs = vector(K, vector(ordered, vector(R, x)))
    need(lhs == rhs, 'Ordered identity on actual column '+str(col))

p = [[F(i == j and i < 4) for j in range(8)] for i in range(8)]
m = scale(p, coefficient)
n = scale(add(I8, p, F(-1)), coefficient)
need(not zero(bracket(scale(p, F(11, 13)), n)), 'Wrong coefficient rejected')
need(not zero(bracket(m, m)), 'Repeated response rejected')
need(not zero(bracket(left, right)), 'Arbitrary pair is not reciprocal')

out = {
    'status': 'PASS_INDEPENDENT_RECIPROCAL_CENTRE_RANK',
    'source_decompressed_sha256': PIN,
    'source_proof_sha256': PROOF_PIN,
    'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
    'method': 'Independent dense centre algebra and 112-column vector interpreter; no producer imports.',
    'actual_R_row_l1': 56,
    'actual_K_row_l1': 1,
    'coordinate_projection_checks': 256,
    'coordinate_rank_distribution': rank_counts,
    'full_inverse_cases': full_cases,
    'ordered_noncommuting_identity_columns': 112,
    'negative_controls': ['wrong coefficient', 'repeated response', 'arbitrary noncommuting pair'],
    'scope': 'Exact scalar family and query ranks. No full native word, phase terminal, controller, or complete supplier price is certified here.'
}
(HERE / 'CHECKS.json').write_text(json.dumps(out, indent=2, sort_keys=True)+'\n')
print(out['status'])
