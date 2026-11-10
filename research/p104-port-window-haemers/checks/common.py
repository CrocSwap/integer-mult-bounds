"""Shared helpers for the checks: data loading, the F_2 dot product, exact rank over Q and over F_p,
maximal cliques, and ok / FAIL reporting (the driver counts 'ok   ' lines and rejects any 'FAIL')."""
import json, os, itertools, sys
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

PORTS = load('ports_p104.json')['ports']
dot = lambda a, b: bin(a & b).count('1') & 1
wt = lambda a: bin(a).count('1')
P120 = [x for x in range(1 << 9) if wt(x) % 4 == 3]

def rank_mod(A, p):
    """Rank of an integer matrix (list of rows) over the prime field F_p."""
    A = [[x % p for x in r] for r in A]
    if not A:
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

def rank_q(A):
    """Exact rank over the rationals."""
    A = [[Fraction(x) for x in r] for r in A]
    if not A:
        return 0
    r = 0
    for c in range(len(A[0])):
        q = next((i for i in range(r, len(A)) if A[i][c] != 0), None)
        if q is None:
            continue
        A[r], A[q] = A[q], A[r]
        inv = 1 / A[r][c]
        A[r] = [x * inv for x in A[r]]
        for i in range(len(A)):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [x - f * y for x, y in zip(A[i], A[r])]
        r += 1
        if r == len(A):
            break
    return r

def maximal_cliques(vs, related):
    """Bron-Kerbosch with pivoting; vs a list of hashable vertices, related(u, v) a symmetric predicate."""
    vs = list(vs)
    N = {v: {u for u in vs if u != v and related(v, u)} for v in vs}
    out = []
    def bk(R, P, X):
        if not P and not X:
            out.append(tuple(sorted(R)))
            return
        u = max(P | X, key=lambda w: len(P & N[w]))
        for v in list(P - N[u]):
            bk(R | {v}, P & N[v], X & N[v])
            P.discard(v)
            X.add(v)
    bk(set(), set(vs), set())
    return out

def mat_mul(A, B, p):
    Bt = list(zip(*B))
    return [[sum(x * y for x, y in zip(r, c)) % p for c in Bt] for r in A]

def transpose(A):
    return [list(x) for x in zip(*A)] if A else A
