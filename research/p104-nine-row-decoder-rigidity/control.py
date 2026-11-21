#!/usr/bin/env python3
"""Exact arithmetic stress test of rank-tight P104 decoder rigidity.

Input: data.json extracts labs and gramRows from the pinned PR.  Every decoder
coefficient is represented as twice its rational value, so products have a
common denominator 4.  No floating point, third-party library or solver.
"""
import argparse
import hashlib
import json
import re
from fractions import Fraction
from pathlib import Path

DATA = Path(__file__).with_name('data.json')
SOURCE = Path(__file__).with_name('DecoderWall4Data.lean')
FRAME = [0, 6, 16, 22, 29, 36, 45, 95]


def gf2_rank(rows):
    pivots = {}
    for row in rows:
        x = row
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return len(pivots)


def rational_rank(matrix):
    a = [[Fraction(x) for x in row] for row in matrix]
    m, n = len(a), len(a[0]) if a else 0
    r = 0
    for j in range(n):
        pivot = next((i for i in range(r, m) if a[i][j]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        for i in range(r + 1, m):
            if a[i][j]:
                scale = a[i][j] / a[r][j]
                for k in range(j, n):
                    a[i][k] -= scale * a[r][k]
        r += 1
        if r == m:
            break
    return r


def main(p, a, b):
    data = json.loads(DATA.read_text())
    assert data['source_commit'] == '41beda1d6435760dc99e38bd7e65f36798aad212'
    labels = data['labs']
    packed = [int(x) for x in data['gramRows']]
    raw = SOURCE.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    assert blob == data['source_blob'] == '90949f8d5dbcdee99974de505018768f4f9f640e'
    source = raw.decode()
    def numbers(definition):
        body = re.search(r'def ' + definition + r' : List ℕ := \[([\s\S]*?)\]', source)
        assert body
        return [int(x) for x in re.findall(r'\d+', body.group(1))]
    assert labels == numbers('labs') and packed == numbers('gramRows')
    n = len(labels)
    assert n == len(packed) == 104
    assert 0 <= p < n and p not in FRAME and 0 <= a < b < 8
    gram = [[(packed[i] >> (2*j) & 3) - 1 for j in range(n)] for i in range(n)]
    q = [[(labels[i] & labels[j]).bit_count() & 1 for j in range(n)] for i in range(n)]
    A = [[gram[i][j] for j in FRAME] for i in range(n)]
    assert all(labels[i].bit_count() % 2 == 1 for i in range(n))
    assert all(gram[i][j] == gram[j][i] for i in range(n) for j in range(n))
    assert all(gram[i][j] == (2 if i == j else 0) for i in FRAME for j in FRAME)
    assert all(sum(A[i][k]*A[j][k] for k in range(8)) == 2*gram[i][j]
               for i in range(n) for j in range(n))
    assert all(gram[i][j] == 0 for i in range(n) for j in range(n) if i != j and q[i][j])
    W0, U0 = [r[:] for r in A], [r[:] for r in A]
    W, U = [r[:] + [0] for r in W0], [r[:] + [0] for r in U0]
    # W_a <- W_a+e_p, W_b <- W_b+e_p, W_8 <- e_p,
    # U_8 <- -(U_a+U_b): exact compensating cancellation.
    W[p][a] += 2
    W[p][b] += 2
    W[p][8] = 2
    for i in range(n):
        U[i][8] = -U0[i][a] - U0[i][b]

    def product(X, Y):
        return [[sum(x*y for x, y in zip(X[i], Y[j])) for j in range(n)] for i in range(n)]
    M0, M = product(W0,U0), product(W,U)
    assert M == M0
    assert all(M[i][j] == 2*gram[i][j] for i in range(n) for j in range(n))
    assert all(M[i][i] == 4 for i in range(n))
    assert all(M[i][j] == 0 for i in range(n) for j in range(n) if i != j and q[i][j])

    def analyze(X, Y):
        prices=[]
        support=[]
        for k in range(len(X[0])):
            D=[i for i in range(n) if X[i][k] != 0]
            S=[i for i in range(n) if Y[i][k] != 0]
            rows=[sum(q[i][j] << j for j in S) for i in D]
            prices.append(gf2_rank(rows))
            support.append((len(D),len(S)))
        return prices,support

    base, base_support=analyze(W0,U0)
    changed, support=analyze(W,U)
    # Three different matrices/fields on the exact same 49-by-49 support.
    # Q is the 0/1 binary label pairing, whereas G is the signed E8 Gram.
    s0 = [i for i in range(n) if W0[i][0]]
    q0 = [[q[i][j] for j in s0] for i in s0]
    g0 = [[gram[i][j] for j in s0] for i in s0]
    signed_gram_q_rank = rational_rank(g0)
    pairing_q_rank = rational_rank(q0)
    pairing_f2_rank = gf2_rank([sum(q[i][j] << j for j in s0) for i in s0])
    assert len(s0) == 49 and (signed_gram_q_rank, pairing_q_rank, pairing_f2_rank) == (8, 29, 9)
    assert [i for i in range(n) if W[i][8]] == [p]
    assert all(W[FRAME[i]][8] == 0 for i in range(8))
    # The reference frame is a rational rank-8 principal Gram block in its complement.
    assert all(gram[i][j] == (2 if i == j else 0) for i in FRAME for j in FRAME)
    assert changed[8] <= 1
    # No pair of rank-one terms is a scalar multiple on either factor side.
    def proportional(x, y):
        return all(x[i]*y[j] == x[j]*y[i] for i in range(n) for j in range(n))
    assert all(any(W[i][k] for i in range(n)) and any(U[i][k] for i in range(n)) for k in range(9))
    assert not any(proportional([r[k] for r in U], [r[l] for r in U])
                   for k in range(9) for l in range(k))
    assert not any(proportional([r[k] for r in W], [r[l] for r in W])
                   for k in range(9) for l in range(k))
    # Negative control: reverse the compensating factor's sign.
    bad=[r[:] for r in U]
    for i in range(n): bad[i][8] *= -1
    badM=product(W,bad)
    fails=[(i,j,badM[i][j]) for i in range(n) for j in range(n)
           if (i==j and badM[i][j]!=4) or (i!=j and q[i][j] and badM[i][j]!=0)]
    assert fails
    print(json.dumps({'pin':data['source_commit'], 'source_blob':data['source_blob'],
                      'p':p,'changed_columns':[a,b],'frame':FRAME,
                      'base_row_prices':base,'base_mass':sum(base),'base_support_sizes':base_support,
                      'new_row_prices':changed,'new_mass':sum(changed),'new_support_sizes':support,
                      'new_deposit_support':[p],'frame_complement_gram':'2 I_8',
                      'same_49_by_49_support_ranks':{'signed_gram_over_Q':signed_gram_q_rank,
                                                      'binary_pairing_over_Q':pairing_q_rank,
                                                      'binary_pairing_over_F2':pairing_f2_rank},
                      'equal_completion': True,'all_half_integer':True,
                      'all_terms_nonzero_and_no_proportional_pairs':True,
                      'bad_sign_violations':len(fails),'bad_first_violation_scaled_by_4':fails[0]}, indent=2))

if __name__ == '__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--port',type=int,default=103)
    ap.add_argument('--a',type=int,default=0)
    ap.add_argument('--b',type=int,default=1)
    args=ap.parse_args()
    main(args.port,args.a,args.b)
