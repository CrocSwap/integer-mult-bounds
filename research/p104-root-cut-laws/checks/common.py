"""Shared helpers: exact rank over Q and F_p, data loading, and ok / FAIL reporting.
The driver counts lines that start with 'ok   ' and rejects any 'FAIL' line."""
import json, os, sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), 'data')
FAILS = []


def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)


def ok(msg):
    print('ok   ' + msg, flush=True)


def fail(msg):
    FAILS.append(msg)
    print('FAIL ' + msg, flush=True)


def req(cond, msg):
    (ok if cond else fail)(msg)


def finish(marker):
    if FAILS:
        print('FAILED %d' % len(FAILS))
        sys.exit(1)
    print(marker)


def fr_matrix(M):
    return [[Fraction(v) for v in row] for row in M]


def rank_q(A):
    """Exact rank of a matrix (list of rows) over the rationals."""
    A = [[Fraction(x) for x in r] for r in A]
    if not A or not A[0]:
        return 0
    r = 0
    for c in range(len(A[0])):
        q = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if q is None:
            continue
        A[r], A[q] = A[q], A[r]
        for i in range(r + 1, len(A)):
            if A[i][c] != 0:
                f = A[i][c] / A[r][c]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        r += 1
        if r == len(A):
            break
    return r


def rank_p(A, p):
    """Rank over the prime field F_p of an integer matrix."""
    A = [[x % p for x in r] for r in A]
    if not A or not A[0]:
        return 0
    r = 0
    for c in range(len(A[0])):
        q = next((i for i in range(r, len(A)) if A[i][c]), None)
        if q is None:
            continue
        A[r], A[q] = A[q], A[r]
        inv = pow(A[r][c], -1, p)
        A[r] = [x * inv % p for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c]:
                f = A[i][c]
                A[i] = [(x - f * y) % p for x, y in zip(A[i], A[r])]
        r += 1
        if r == len(A):
            break
    return r
