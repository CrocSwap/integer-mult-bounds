#!/usr/bin/env python3
"""Finite exact corroboration for HEADER-SATURATION.md; not its universal proof.

Jerry Chen / @CubeJerry, with substantial OpenAI Codex assistance.
Apache-2.0. Canonical query fixtures retain the Cinna Davis / Ali Romman
#6348/#6398 / thu-nmrc #6716 / zxv #6726 binary-header lineage.
"""
from fractions import Fraction as Q
from hashlib import sha256
from math import isqrt
from pathlib import Path
import json


def need(ok, message):
    if not ok:
        raise ValueError(message)


def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def add(A, B, sign=1):
    return [[a+sign*b for a,b in zip(r,s)] for r,s in zip(A,B)]


def mul(A, B):
    return [[sum(a*b for a,b in zip(r,c)) for c in zip(*B)] for r in A]


def rank(A, prime=0):
    A = [[Q(x) if not prime else x % prime for x in row] for row in A]
    k = 0
    for j in range(len(A[0])):
        p = next((p for p in range(k, len(A)) if A[p][j]), None)
        if p is None:
            continue
        A[k], A[p] = A[p], A[k]
        scale = 1/A[k][j] if not prime else pow(A[k][j], -1, prime)
        A[k] = [x*scale if not prime else x*scale % prime for x in A[k]]
        for p in range(len(A)):
            if p != k:
                factor = A[p][j]
                A[p] = [x-factor*y if not prime else (x-factor*y) % prime
                        for x,y in zip(A[p], A[k])]
        k += 1
        if k == len(A):
            break
    return k


def central_product(A, B):
    return (add(mul(A[0],B[0]),mul(A[1],B[1])),
            add(mul(A[0],B[1]),mul(A[1],B[0])))


def lift(A, w):
    return [[A[i//w][j//w]*int(i%w == j%w)
             for j in range(len(A)*w)] for i in range(len(A)*w)]


def power_seven_eighths(n):
    bits = 64
    lo = isqrt(isqrt(isqrt(n**7 << (8*bits))))
    need(lo**8 <= n**7 << (8*bits) < (lo+1)**8, 'Exact eighth-root enclosure')
    return Q(lo, 1 << bits), Q(lo+1, 1 << bits)


def increment(n):
    a,b = power_seven_eighths(n+1), power_seven_eighths(n)
    return a[0]-b[1], a[1]-b[0]


def main():
    source = Path(__file__).with_name('frozen').joinpath('caller6726.py').read_bytes()
    pin = 'e99e4287091c6ce4ec9a563cb9ac6f45be35ff1ef421b4efa8c200cb9d639d6c'
    need(sha256(source).hexdigest() == pin, 'Exact inherited caller bytes')
    base = [
        [[0,1,-1,0],[0,0,0,0],[0,0,0,0],[0,-1,1,0]],
        [[0,1,-1,-1],[0,0,0,0],[0,1,-1,-1],[0,-1,1,1]],
        [[0,1,0,-1],[0,0,0,0],[0,1,0,-1],[0,0,0,0]],
    ]
    Kbase = [[0,1,0,0],[0,0,0,0],[0,0,1,0],[0,0,0,1]]
    receipts, omitted = [], 0
    for w in (1,2,3):
        n = 4*w; I = eye(n); Z = [[0]*n for _ in range(n)]
        Ns = [lift(A,w) for A in base]; K = lift(Kbase,w)
        state = (I,Z)
        aux_state = (eye(2*w), [[0]*(2*w) for _ in range(2*w)])
        As = []
        for N in Ns:
            need(mul(N,N) == Z, 'Whole query square-zero')
            state = central_product((add(I,N,-1),N),state)
            A = [row[2*w:] for row in N[2*w:]]; As.append(A)
            need(mul(A,A) == [[0]*(2*w) for _ in range(2*w)], 'Quotient square-zero')
            aux_state = central_product((add(eye(2*w),A,-1),A),aux_state)
        need(state == (add(I,K,-1),K), 'Actual normalized header identity')
        need(aux_state == ([[0]*(2*w) for _ in range(2*w)],eye(2*w)), 'Formal S quotient identity')
        for prime in (0,2,3,5):
            need(rank(K,prime) == 3*w, 'Saturated header rank')
            need(all(rank(N,prime) == w for N in Ns), 'Native block ranks')
            need(all(rank(A,prime) == w for A in As), 'Quotient block ranks')
            for a,b in ((0,1),(1,2),(2,0)):
                need(rank(As[a]+As[b],prime) == 2*w, 'Every pair of quotient kernels intersects trivially')
            receipts.append({'width':w,'characteristic':prime,'header_rank':3*w,'quotient_ranks':[w,w,w]})
        for lost in range(2*w,4*w):
            P = eye(n); P[lost][lost] = 0
            for N in Ns:
                need(mul(P,N) != N or mul(N,P) != N, 'Missing S direction cannot support the native query')
        for gone in range(3):
            wrong = (eye(2*w),[[0]*(2*w) for _ in range(2*w)])
            for j,A in enumerate(As):
                if j != gone:
                    wrong = central_product((add(eye(2*w),A,-1),A),wrong)
            need(wrong != aux_state, 'Omitted quotient query rejected')
            omitted += 1
    mixed = []
    for a,b in ((1,1),(8,8),(8,16),(8,1024),(8,8*(1<<80))):
        ia,ib,it = increment(a),increment(b),increment(a+b)
        gap = ia[0]+ib[0]-2*it[1], ia[1]+ib[1]-2*it[0]
        need(0 < gap[0] <= gap[1] < 1, 'Exact mixed gain is positive and below one')
        mixed.append({'a':a,'b':b,'gain_interval':list(map(str,gap))})
    a,b = 8,8*(1<<80)
    ia,it = increment(a),increment(a+b)
    equal = 2*(ia[0]-it[1]),2*(ia[1]-it[0])
    need(equal[0] > 1, 'Equal-orientation universal one-query-price inference is false')
    receipt = {'schema':'three-query-saturation-fixtures/1','source_sha256':pin,
               'field_width_fixtures':receipts,'omitted_query_controls':omitted,
               'mixed_power_tariff':'t=7/8','mixed_price_fixtures':mixed,
               'equal_orientation_counterexample':{'a':a,'b':b,'gain_interval':list(map(str,equal))}}
    data = json.dumps(receipt,sort_keys=True,separators=(',',':')).encode()
    print(json.dumps(receipt,sort_keys=True,indent=2))
    print('CERTIFICATE_SHA256',sha256(data).hexdigest())
    print('PASS_THREE_QUERY_BODY_SATURATION_FIXTURES')


if __name__ == '__main__':
    main()
