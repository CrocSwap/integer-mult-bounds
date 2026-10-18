"""jetfail jf0, jf1, jf2: no-wild configurations with a harmonic line that the first-order jet cannot move, but for which (A) still holds.
Checks (exact): no-wild; first-order tangent test fails (random phi, and the full collapse phi0 over F2: immovable lines 0 / 7 / 0,2); order-2 diagonal Q_t is identically zero as a polynomial on the
first-order tangent space V (the order-2 jet fails structurally); full pattern not CR2 over GF(2), GF(4), GF(8); exact minimum cost by exhaustive enumeration (C program enumall) = 12 (v = 9, 192
minimisers) for jf1 and 14 (v = 9, 12928 minimisers) for jf2; jf0 (v = 11, f = 41 too large to enumerate): the CNF 'cost <= K' is UNSAT for K <= 15 (CaDiCaL, python-sat) so cost >= 16 > v;
B-dependent jet test on the jf1 minimisers (the CR2 status of these 192 is recorded, not re-run)."""
import json, collections, random
import numpy as np
from common import *
from kit import *; from phi import *; from tangent import tangent_cr2; from cr2 import realise, cfg_data; from jet2 import *
exp = {0: dict(v=11, f=41, imm=[0]), 1: dict(v=9, f=27, imm=[7], cost=12, nmin=192), 2: dict(v=9, f=20, imm=[0, 2], cost=14, nmin=12928)}
def polyvec(M):
    d = M.shape[0]; out = []
    for i in range(d):
        for j in range(i, d): out.append(int(M[i, i]) if i == j else int(M[i, j] ^ M[j, i]))
    return int(''.join(map(str, out)), 2) if out else 0
for i in range(3):
    P, Q = json.load(open(PKG + '/data/jf%d.json' % i)); v = len(P); R, A, free = setup(P, Q); pi, sig = cfg_data(P, Q); e = exp[i]
    w, H = classify(P, Q)
    report('F jf%d: v=%d, f=%d, no-wild, harmonic lines %s' % (i, v, len(free), H), (v, len(free), w) == (e['v'], e['f'], 0) and len(H) > 0)
    phi = make_phi(random.Random(1)); Pt = [[phi(x) for x in p] for p in P]; Qt = [[phi(x) for x in q] for q in Q]
    res, dim = tangent_cr2(Pt, Qt, pi, sig, free, H)
    bad = sorted(t for t in H if not res[t])
    an = analyse(P, Q, free, H)
    report('F jf%d: first-order jet test FAILS (phi random z_p: harmonic lines immovable %s; full collapse phi0: %s)' % (i, bad, sorted(an['imm'])), bool(bad) and sorted(an['imm']) == e['imm'])
    E = an['E']
    deps = [polyvec(quad_matrix(an, [E[k] for k in range(len(E)) if z >> k & 1])) for z in an['deps']]
    ok2 = all(polyvec(quad_matrix(an, [(t, t)] + [E[k] for k in range(len(E)) if c >> k & 1])) == 0 for t, c in an['imm'].items())
    report('F jf%d: order-2 diagonal Q_t is identically 0 on the first-order tangent space V (dim V = %d) for every immovable line' % (i, len(an['basis'])), ok2)
    nc = [realise(pi, sig, set(free), k=k, limit=10 ** 6) for k in (1, 2, 3)]
    report('F jf%d: full pattern not CR2 over GF(2), GF(4), GF(8) (exhaustive)' % i, all(r is None for r in nc))
    if i in (1, 2):
        best, ms = enum_raw(v, R, A, free, 0)
        report('F jf%d: exact minimum cost (exhaustive over 2^%d admissible B) = %d, %d minimisers; v = %d, so (A) holds' % (i, len(free), best, len(ms), v), best == e['cost'] and len(ms) == e['nmin'] and best >= v)
        if i == 1:
            cj = 0
            for c_, g in ms:
                ent = [free[k] for k in range(len(free)) if g >> k & 1]
                r_, d_ = tangent_cr2(Pt, Qt, pi, sig, ent, H); cj += all(r_.values())
            report('F jf1: B-dependent: of the 192 minimisers, %d pass the first-order jet test on E = supp B (the other %d do not)' % (cj, 192 - cj), cj == 186, 'RECORDED, not re-run here: exactly these 186 are also CR2 (scripts/ + README)')
    else:
        try:
            from satlib import cost_leq
            import time
            t0 = time.time(); un = all(cost_leq(P, Q, K) is None for K in (15,))
            report('F jf0: CNF "cost <= 15" is UNSAT (and hence <= K for K < 15), so cost(jf0) >= 16 > v = 11', un, '%.0fs' % (time.time() - t0))
        except ImportError:
            print('SKIP F jf0 cost >= 16 (python-sat not installed); RECORDED in the README')
done()
