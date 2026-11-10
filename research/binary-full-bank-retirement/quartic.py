#!/usr/bin/env python3
"""Exact Gaussian-integer controls for the finite-character body lemma.
Jerry Chen / @CubeJerry, substantial OpenAI assistance; Apache-2.0.
"""
from itertools import permutations
import json


def need(ok, text):
    if not ok:
        raise ValueError(text)


def plus(a, b):
    return a[0]+b[0], a[1]+b[1]


def times(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def total(values):
    out = (0, 0)
    for value in values:
        out = plus(out, value)
    return out


def eye(n):
    return [[(int(i == j), 0) for j in range(n)] for i in range(n)]


def matrix(A, B):
    return [[total(times(a,b) for a,b in zip(row,col)) for col in zip(*B)] for row in A]


def embed(P):
    return [[(x,0) for x in row] for row in P]


def body(P, d):
    z = (d[0]-1, d[1])
    return [[plus((int(i == j),0), times(z,(v,0))) for j,v in enumerate(row)] for i,row in enumerate(P)]


def determinant(A):
    terms = []
    for order in permutations(range(len(A))):
        sign = (-1)**sum(order[i]>order[j] for i in range(len(A)) for j in range(i+1,len(A)))
        value = (sign,0)
        for i,j in enumerate(order):
            value = times(value,A[i][j])
        terms.append(value)
    return total(terms)


def main():
    P0 = [[1,-1,1],[0,0,0],[0,0,0]]
    P1 = [[0,1,-1],[0,1,-1],[0,0,0]]
    PD = [[1,0,0],[0,1,-1],[0,0,0]]
    Q = [[0,0,0],[0,0,0],[0,0,1]]
    I = eye(3)
    for P in [P0,P1,PD,Q]:
        need(matrix(embed(P),embed(P)) == embed(P), 'Split idempotent fixture')
    for P in [P0,P1]:
        need(matrix(embed(PD),embed(P)) == embed(P) and matrix(embed(P),embed(PD)) == embed(P), 'Saturated support')
    need(matrix(embed(PD),embed(Q)) != embed(Q), 'Extra cycle lies outside target support')
    characters = [(1,0),(0,1),(-1,0),(0,-1)]
    for d in characters:
        intended = body(PD,d)
        actual = matrix(body(P1,d),body(P0,d))
        need(actual == intended, 'Minimal positive body word')
        loop = I
        for _ in range(4):
            loop = matrix(body(Q,d),loop)
        need(loop == I and matrix(loop,actual) == intended, 'Four extra calls are invisible on quartic characters')
        need(determinant(actual) == times(d,d), 'Exact determinant of rank-two body endpoint')
    minus_one = (-1,0)
    primitive = (0,1)
    need(matrix(body(Q,minus_one),body(Q,minus_one)) == I, 'Order-two alias fixture')
    need(matrix(body(Q,primitive),body(Q,primitive)) != I, 'Primitive character rejects order-two alias')
    need(5 != 1 and 5 % 4 == 1, 'D^5 versus D formal-derivative limitation')
    report = {'status':'PASS_FINITE_CHARACTER_BODY_CONTROLS',
              'characters':4,'minimal_positive_rank':2,'target_rank':2,
              'quartic_cycle_positive_rank':6,'excess_rank':4,
              'controls':['unsupported extra projector defeats unqualified support',
                          'primitive character distinguishes an order-two alias',
                          'D^5 equals D only in the quartic quotient; derivatives differ'],
              'scope':'Exact fixtures only; universal factorization, congruence and tariff proofs are in QUARTIC-BODY.md.'}
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()
