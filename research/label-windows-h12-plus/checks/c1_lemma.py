"""c1: Lemma C on every exceptional pair (numpy; the lemma itself is PROVEN in README section 2, this checks its instance data).
For each of the 144 exceptional (rep, section) pairs recorded in data/exceptional_pairs.json (produced by the census, c2 re-derives the list):
  (i)  omega(R cap A) in the non-orthogonality graph recomputed here by a third, pure-Python exact max-clique (bitset Bron-Kerbosch with pivot);
  (ii) the maximum clique S lies in R cap A and the pattern constraints B_tt = 1, B_ts = 0 (t,s non-orthogonal) restricted to S x S are exactly the identity;
  (iii) 40 random fitting B (free entries random bits) per pair, rank_F2 B[R,A] >= omega.
Also the arithmetic of the statement: omega >= 5 gives 8 * 5 = 40."""
import json, os, random, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
import common
D = common.load(); NO, Z, reps = D['NO'], D['Z'], D['reps']
ex = json.load(open(os.path.join(HERE, '..', 'data', 'exceptional_pairs.json')))
adj = [sum(1 << j for j in range(112) if NO[i, j]) for i in range(112)]
def omega(mask):
    best = [0, 0]
    def bk(R, P, X):
        if not P and not X:
            n = bin(R).count('1')
            if n > best[0]: best[0], best[1] = n, R
            return
        u = max((v for v in range(112) if (P | X) >> v & 1), key=lambda v: bin(P & adj[v]).count('1'))
        Q = P & ~adj[u]
        while Q:
            v = (Q & -Q).bit_length() - 1; Q &= Q - 1
            bk(R | 1 << v, P & adj[v], X & adj[v]); P &= ~(1 << v); X |= 1 << v
    bk(0, mask, 0); return best
def rank2(M):
    rows = [int(''.join('1' if x else '0' for x in r), 2) for r in M]; rk = 0
    while rows:
        p = rows.pop()
        if p:
            rk += 1; lb = p & -p; rows = [r ^ p if r & lb else r for r in rows]
    return rk
rng = random.Random(2026); bad = 0; hist = {}
for (r, i, w) in ex:
    Rm = ~Z[reps[r]]; Am = ~Z[i]                     # R = P112 minus H1, A = P112 minus H2 (rep section is the complement of R)
    RA = Rm & Am; mask = sum(1 << int(t) for t in np.nonzero(RA)[0])
    om, S = omega(mask); Sl = [t for t in range(112) if S >> t & 1]
    ok = om == w and all(RA[t] for t in Sl)
    F = np.array([[1 if a == b else (0 if NO[a, b] else -1) for b in Sl] for a in Sl])     # -1 = free entry
    ok &= bool((F == np.eye(len(Sl), dtype=int)).all())
    Ri = list(np.nonzero(Rm)[0]); Ai = list(np.nonzero(Am)[0])
    for _ in range(40):
        B = np.array([[rng.getrandbits(1) for _ in range(112)] for _ in range(112)])
        for a in range(112):
            B[a, a] = 1
            for b in range(112):
                if NO[a, b]: B[a, b] = 0
        ok &= rank2(B[np.ix_(Ri, Ai)]) >= om
    hist[om] = hist.get(om, 0) + 1
    if not ok: bad += 1; print('FAIL pair', r, i, 'omega', om, 'recorded', w)
print(('FAIL' if bad else 'PASS') + ' c1.a  Lemma C instance data: %d exceptional pairs, omega recomputed (%s), maximum clique inside R cap A with identity pattern, 40 random fittings each rank >= omega' % (len(ex), ', '.join('%d pairs omega %d' % (v, k) for k, v in sorted(hist.items()))))
print(('PASS' if min(hist) == 5 and 8 * min(hist) == 40 else 'FAIL') + ' c1.b  smallest omega over the exceptional pairs is 5; 8 terms of rank >= 5 cost >= 40')
sys.exit(1 if bad else 0)
