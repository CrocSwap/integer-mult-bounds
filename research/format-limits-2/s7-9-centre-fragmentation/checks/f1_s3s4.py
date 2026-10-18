"""F1: S3 packets / S4 slots of the rebuilt #656 word admit no supersolvable (modular-chain) reader order (port of cards B89).
Input inputs/b82-rec.json is a DERIVED record (cards B82 c82.py run on the rebuilt #656 word); the derivation is not re-run here."""
import collections
from common import *
D = jplain('b82-rec.json'); v = D['v']; P = D['ports']; SEQ = [tuple(x) for x in D['seq']]
def rank(vs):
    b = []
    for x in vs:
        for y in b: x = min(x, x ^ y)
        if x: b.append(x)
    return len(b)
def taint(src, seq):
    lab = {src}; T = set()
    for t, s in SEQ[seq:]:
        if s in lab:
            lab.add(t)
            if v <= t < 2 * v: T.add(t - v)
    return T
def fields(r):
    k = r[0]
    return (k,) + ((r[4], r[5], r[6], r[7]) if k == 'S3' else (r[3], r[4], r[5], r[6]))
c = collections.Counter(); dep = collections.Counter(); sets = []
for r in D['rec']:
    k, a, b, seq, F = fields(r)
    T = sorted(taint(a, seq) | taint(b, seq)); ports = [P[t] for t in T]
    c[(k, len(T), rank(ports))] += 1; dep[(k, rank(ports) < len(T))] += 1
    ok = all(((f & p).bit_count() % 2 == 0) for f in F for p in ports)
    sets.append((k, ports, ok))
check('f1.s3s4.counts-S3-156-(8 readers,rank5)-S4-112-(4 readers,rank3)', dict(c) == {('S3', 8, 5): 156, ('S4', 4, 3): 112}, str(dict(c)))
check('f1.s3s4.all-268-dependent', dep == {('S3', True): 156, ('S4', True): 112})
check('f1.s3s4.copy-frame-orthogonal-to-all-reader-ports-at-copy-time', all(o for _, _, o in sets))
import itertools
def analyze(ports):
    pts = []
    for p in ports:
        if p and p not in pts: pts.append(p)
    n = len(pts)
    rk = lambda S: rank([pts[i] for i in S]) if S else 0
    full = rk(range(n)); flats = set()
    for m in range(1 << n):
        S = [i for i in range(n) if m >> i & 1]; r = rk(S)
        flats.add((frozenset(i for i in range(n) if rk(S + [i]) == r), r))
    flats = list(flats)
    mod = lambda F: all(rk(sorted(F[0] | G[0])) + rk(sorted(F[0] & G[0])) == F[1] + G[1] for G in flats)
    M = [f for f in flats if mod(f)]
    def chain(cur):
        if cur[1] == full: return True
        return any(g[1] == cur[1] + 1 and cur[0] <= g[0] and chain(g) for g in M)
    return any(chain(s) for s in M if s[1] == 0)
res = collections.Counter()
for k, ports, _ in sets: res[(k, analyze(ports))] += 1
check('f1.s3s4.supersolvable-0-of-156-S3-0-of-112-S4', dict(res) == {('S3', False): 156, ('S4', False): 112}, str(dict(res)))
done()
