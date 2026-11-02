#!/usr/bin/env python3
"""Local SAT search for k-source depth-two blocks of the unsigned dirty connector.

NOT part of the registered replay: it needs python-sat (tested with
python-sat 1.8.dev*, CaDiCaL 1.9.5 and CaDiCaL 1.0.3 backends) and minutes of
CPU. verify.py is the standard-library check of every word this script found.

Model (PR4248 definitions, unchanged interface). A word w of length k*c calls
each source exactly c times. q_t is the count vector of its first t calls.
w has depth two when every nonzero binary mask m in {0,1}^k satisfies
m == q_s + q_t (mod c) for some boundaries 0 <= s <= t <= k*c - 1. Boundary
k*c is dropped because q_{kc} = c*1 == q_0; s = 0 is a single read.

Encoding.
  x[p][j]   position p calls source j (exactly one per p; exactly c per j).
  e[t][j][v] q_t[j] mod c == v (one-hot), with e[0][j][0] and the transition
             e[t+1][j][v+x] from e[t][j][v].
  first-occurrence symmetry breaking: source j may appear only after j-1 has.
  y[m][s][t] the pair (s, t) realizes m:  y & e[s][j][v] -> e[t][j][m_j - v].
  each mask: OR of its y.
Pruning (sound): by the weight identity of PR6107 (coordinate sum of q_t is
t), a pair can realize m only if s + t == |m| (mod c); other y are omitted.
--no-weight-prune keeps every pair (a second, larger encoding).
--weights 2,6 restricts the masks to those weights (a relaxation: UNSAT for a
subset of masks implies UNSAT for all masks).

Usage: python search_sat.py K C [--solver cadical195] [--no-weight-prune] [--weights 2,6]
Prints 'SAT k=.. c=.. word=...' or 'UNSAT k=.. c=..'.
"""
import argparse
import itertools
import time

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Solver


def build(k, c, weight_prune=True, weights=None):
    L = k * c
    pool = IDPool()
    X = lambda p, j: pool.id(('x', p, j))
    E = lambda t, j, v: pool.id(('e', t, j, v))
    F = lambda p, j: pool.id(('f', p, j))
    cnf = CNF()
    for p in range(L):
        lits = [X(p, j) for j in range(k)]
        cnf.append(lits)
        cnf.extend([[-a, -b] for a, b in itertools.combinations(lits, 2)])
    for j in range(k):
        enc = CardEnc.equals(lits=[X(p, j) for p in range(L)], bound=c,
                             vpool=pool, encoding=EncType.seqcounter)
        cnf.extend(enc.clauses)
    for t in range(L + 1):
        for j in range(k):
            lits = [E(t, j, v) for v in range(c)]
            cnf.append(lits)
            cnf.extend([[-a, -b] for a, b in itertools.combinations(lits, 2)])
    for j in range(k):
        cnf.append([E(0, j, 0)])
    for t in range(L):
        for j in range(k):
            for v in range(c):
                cnf.append([-X(t, j), -E(t, j, v), E(t + 1, j, (v + 1) % c)])
                cnf.append([X(t, j), -E(t, j, v), E(t + 1, j, v)])
    for p in range(L):
        for j in range(k):
            prev = [F(p - 1, j)] if p > 0 else []
            cnf.append([-F(p, j), X(p, j)] + prev)
            cnf.append([F(p, j), -X(p, j)])
            if p > 0:
                cnf.append([F(p, j), -F(p - 1, j)])
            if j > 0:
                cnf.append([-X(p, j)] if p == 0 else [-X(p, j), F(p - 1, j - 1)])
    for m in range(1, 1 << k):
        bits = [(m >> j) & 1 for j in range(k)]
        if weights is not None and sum(bits) not in weights:
            continue
        ys = []
        for s in range(L):
            for t in range(s, L):
                if weight_prune and (s + t - sum(bits)) % c:
                    continue
                y = pool.id(('y', m, s, t))
                ys.append(y)
                for j in range(k):
                    for v in range(c):
                        cnf.append([-y, -E(s, j, v), E(t, j, (bits[j] - v) % c)])
        cnf.append(ys)
    return cnf, pool, X


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('k', type=int)
    ap.add_argument('c', type=int)
    ap.add_argument('--solver', default='cadical195')
    ap.add_argument('--no-weight-prune', action='store_true')
    ap.add_argument('--weights', default=None)
    a = ap.parse_args()
    weights = None if a.weights is None else {int(x) for x in a.weights.split(',')}
    cnf, pool, X = build(a.k, a.c, not a.no_weight_prune, weights)
    print(f'k={a.k} c={a.c} solver={a.solver} prune={not a.no_weight_prune} '
          f'weights={a.weights or "all"} vars={pool.top} clauses={len(cnf.clauses)}', flush=True)
    t0 = time.time()
    with Solver(name=a.solver, bootstrap_with=cnf.clauses) as S:
        ok = S.solve()
        dt = time.time() - t0
        if ok:
            model = {l for l in S.get_model() if l > 0}
            word = ''.join(str(next(j for j in range(a.k) if X(p, j) in model))
                           for p in range(a.k * a.c))
            print(f'SAT k={a.k} c={a.c} time={dt:.1f}s word={word}', flush=True)
        else:
            print(f'UNSAT k={a.k} c={a.c} time={dt:.1f}s', flush=True)


if __name__ == '__main__':
    main()
