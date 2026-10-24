#!/usr/bin/env python3
"""Check the reciprocal centre identity on the pinned actual supplier."""
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / 'lanes/new-core-transfer-20261017/CLEAN-J-PROGRAMS.json.gz'
PIN = 'a6c5dc63a47c1fdb0a97314a3b8541035f507beccb1029762f703039465187fa'


def need(value, label):
    if not value:
        raise ValueError(label)


def add(a, b, scale=F(1)):
    out = [dict(row) for row in a]
    for i, row in enumerate(b):
        for j, value in row.items():
            new = out[i].get(j, F(0)) + scale*value
            if new:
                out[i][j] = new
            else:
                out[i].pop(j, None)
    return out


def scale(a, c):
    return [{j: c*v for j, v in row.items() if c*v} for row in a]


def mul(a, b):
    out = [{} for _ in a]
    for i, row in enumerate(a):
        for k, value in row.items():
            for j, other in b[k].items():
                new = out[i].get(j, F(0)) + value*other
                if new:
                    out[i][j] = new
                else:
                    out[i].pop(j, None)
    return out


def identity(n):
    return [{i: F(1)} for i in range(n)]


raw = gzip.decompress(SOURCE.read_bytes())
need(sha256(raw).hexdigest() == PIN, 'Source pin')
data = json.loads(raw)
R = [{int(k): F(v) for k, v in row.items()} for row in data['R']]
K = [{j: R[j][i]/4 for j in range(8) if i in R[j]} for i in range(112)]
I8, I112 = identity(8), identity(112)
need(mul(R, K) == scale(I8, F(14)), 'Actual RK')
J = add(I112, mul(K, R), F(-1))
coefficient = F(12, 13)
coordinate_count = 0
full_cases = []


def bracket(M, N):
    return add(add(scale(I8, F(12)), add(M, N), F(-13)), mul(M, N), F(14))


def check_full(P, label):
    need(mul(P, P) == P, 'Projection '+label)
    M, N = scale(P, coefficient), scale(add(I8, P, F(-1)), coefficient)
    E = add(J, mul(mul(K, M), R))
    G = add(J, mul(mul(K, N), R))
    need(mul(E, G) == I112, 'EG '+label)
    need(mul(G, E) == I112, 'GE '+label)
    full_cases.append({'label': label, 'E_entries': sum(map(len, E)),
                       'G_entries': sum(map(len, G))})


for mask in range(256):
    P = [{i: F(1)} if (mask >> i) & 1 else {} for i in range(8)]
    M, N = scale(P, coefficient), scale(add(I8, P, F(-1)), coefficient)
    need(not any(bracket(M, N)), 'Coordinate reciprocal equation')
    coordinate_count += 1
    if mask in (0, 1, 15, 127, 255):
        check_full(P, 'coordinate-mask-'+str(mask))

P = [{0: F(1), 4: F(3, 2)}, {1: F(1), 5: F(-2)},
     {2: F(1), 6: F(1, 2)}, {3: F(1), 7: F(5)}, {}, {}, {}, {}]
check_full(P, 'noncoordinate-rank-four')
M = scale(P, coefficient)
N = scale(add(I8, P, F(-1)), coefficient)
need(any(bracket(scale(P, F(11, 13)), N)), 'Wrong coefficient mutation')
need(any(bracket(M, M)), 'Repeated response mutation')
need(not any(bracket(I8, I8)), 'Sharp dyadic full-rank example')

proof = HERE / 'RECIPROCAL-CENTRE-RANK-20261018.md'
out = {'status': 'PASS_EXACT_RECIPROCAL_CENTRE_RANK', 'source_sha256': PIN,
       'checker_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
       'proof_sha256': sha256(proof.read_bytes()).hexdigest(),
       'coordinate_projection_checks': coordinate_count,
       'full_112_field_inverse_checks': full_cases,
       'mutation_checks': ['wrong coefficient', 'repeated response'],
       'scope': 'Exact centre algebra. Native words, global phase transport, and supplier pricing are separate obligations.'}
(HERE / 'RECIPROCAL-CENTRE-RANK-20261018.json').write_text(
    json.dumps(out, indent=2, sort_keys=True)+'\n')
print(out['status'])
