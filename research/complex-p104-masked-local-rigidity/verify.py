#!/usr/bin/env python3
"""Exact local rigidity of masked (E-graph) rank-8 complex decoders on every frame-pair puncture.

Masked model (PR717's E-graph exactness): on the live lines, a costly part K must satisfy K_ii = 4 and
K_ij = 0 for orthogonal live pairs; odd entries are free; rank K <= 8.  At K0 = 2G the tangent space is
{Delta = L M^T + N L^T : Delta vanishes on those entries}.  The torus D K0 D^-1 and the GL(8) gauge give
64 + (v - 1) kernel directions.  This script proves the kernel has exactly that dimension (infinitesimal
rigidity) for P120, P112 = P120 - F0 and every P104 = P120 - F0 - F1, F1 one of the 1260 frames disjoint
from F0:

  * upper bound: after eliminating N, the M-system has rank >= 7v - 63 over F_p (p = 2^31 - 1), and
    rank over F_p never exceeds rank over Q;
  * lower bound: the explicit gauge and torus M-vectors lie in the kernel and span 64 + v - 1 over F_p.

Frames are reduced to orbits by explicit Schreier elements of the stabilizer of F0 (products of root
reflections, checked to fix F0 and preserve |G|), so each certified representative covers its orbit.
Standard library only.  Run from the repository root:  python3 -B research/complex-p104-masked-local-rigidity/verify.py
"""
import itertools
import random
import sys
import time
from math import gcd

P = 2 ** 31 - 1
RESULTS = []


def check(tag, ok, info=''):
    RESULTS.append(bool(ok))
    print(('PASS ' if ok else 'FAIL ') + tag + (': ' + info if info else ''), flush=True)
    return bool(ok)


# ---------------------------------------------------------------- geometry
def e8_lines():
    roots = []
    for i, j in itertools.combinations(range(8), 2):
        for si, sj in itertools.product((2, -2), repeat=2):
            v = [0] * 8
            v[i], v[j] = si, sj
            roots.append(tuple(v))
    roots += [s for s in itertools.product((1, -1), repeat=8) if s.count(-1) % 2 == 0]
    return sorted(r for r in roots if next(x for x in r if x) > 0)


LINES = e8_lines()
N = len(LINES)


def ip(x, y):
    return sum(a * b for a, b in zip(x, y))


def canon(v):
    g = 0
    for x in v:
        g = gcd(g, abs(x))
    v = tuple(x // g for x in v)
    return v if next(x for x in v if x) > 0 else tuple(-x for x in v)


INDEX = {canon(v): i for i, v in enumerate(LINES)}
G = [[ip(LINES[i], LINES[j]) // 4 for j in range(N)] for i in range(N)]
REFL = [[INDEX[canon(tuple(4 * a - ip(x, r) * b for a, b in zip(x, r)))] for x in LINES] for r in LINES]


def all_frames():
    out = []

    def grow(cur, cand):
        if len(cur) == 8:
            out.append(frozenset(cur))
            return
        for k, j in enumerate(cand):
            grow(cur + [j], [x for x in cand[k + 1:] if G[j][x] == 0])
    for i in range(N):
        grow([i], [j for j in range(i + 1, N) if G[i][j] == 0])
    return out


# ---------------------------------------------------------------- orbits under Stab(F0)
def stabilizer_orbits(frames, F0, rng, quiet=60):
    """Union frames disjoint from F0 under Schreier elements w_{sF}^-1 s w_F that fix F0."""
    word = {F0: list(range(N))}
    queue = [F0]
    for F in queue:                                  # BFS: word[F] maps F0 onto F
        for s in REFL:
            H = frozenset(s[i] for i in F)
            if H not in word:
                word[H] = [s[word[F][i]] for i in range(N)]
                queue.append(H)
    inv = {}
    for F, w in word.items():
        iv = [0] * N
        for i, x in enumerate(w):
            iv[x] = i
        inv[F] = iv
    disjoint = [F for F in frames if not F & F0]
    pos = {F: k for k, F in enumerate(disjoint)}
    parent = list(range(len(disjoint)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    gens, idle, ok = 0, 0, True
    while idle < quiet:
        F, s = rng.choice(queue), rng.choice(REFL)
        H = frozenset(s[i] for i in F)
        g = [inv[H][s[word[F][i]]] for i in range(N)]
        ok &= frozenset(g[i] for i in F0) == F0 and all(abs(G[g[i]][g[j]]) == abs(G[i][j])
                                                        for i in range(0, N, 7) for j in range(N))
        merged = False
        for F1, k in pos.items():
            a, b = find(k), find(pos[frozenset(g[i] for i in F1)])
            if a != b:
                parent[a] = b
                merged = True
        gens += 1
        idle = 0 if merged else idle + 1
    classes = {}
    for F1, k in pos.items():
        classes.setdefault(find(k), []).append(F1)
    return len(word), disjoint, sorted(classes.values(), key=len, reverse=True), gens, ok


# ---------------------------------------------------------------- exact tangent certificate
def inv_mod(M):
    n = len(M)
    a = [[x % P for x in row] + [int(i == j) for j in range(n)] for i, row in enumerate(M)]
    for c in range(n):
        p = next((r for r in range(c, n) if a[r][c]), None)
        if p is None:
            return None
        a[c], a[p] = a[p], a[c]
        f = pow(a[c][c], P - 2, P)
        a[c] = [x * f % P for x in a[c]]
        for r in range(n):
            if r != c and a[r][c]:
                g = a[r][c]
                a[r] = [(x - g * y) % P for x, y in zip(a[r], a[c])]
    return [row[n:] for row in a]


class Echelon:
    """Sparse row echelon form over F_P; insert() returns True when the row raises the rank."""
    def __init__(self):
        self.rows = {}

    def insert(self, row):
        row = {c: v % P for c, v in row.items() if v % P}
        while row:
            c = min(row)
            if c not in self.rows:
                f = pow(row[c], P - 2, P)
                self.rows[c] = {k: v * f % P for k, v in row.items()}
                return True
            g = row[c]
            for k, v in self.rows[c].items():
                x = (row.get(k, 0) - g * v) % P
                if x:
                    row[k] = x
                else:
                    row.pop(k, None)
        return False


def masked_system(live):
    """Rows of the M-system after eliminating N; unknown (j, d) has column 8 * pos[j] + d."""
    pos = {x: k for k, x in enumerate(live)}
    rows = []
    for i in live:
        E = [i] + [j for j in live if j != i and G[i][j] == 0]
        basis = []
        for j in E:                                  # greedy basis containing i, independence mod P
            trial = basis + [j]
            if rank_mod([LINES[k] for k in trial]) == len(trial):
                basis = trial
            if len(basis) == 8:
                break
        if len(basis) < 8:
            return None, i
        Binv = inv_mod([list(LINES[k]) for k in basis])          # rows of L_B are the basis vectors
        Li = LINES[i]
        for j in E:
            if j in basis:
                continue
            c = [sum(LINES[j][d] * Binv[d][k] for d in range(8)) % P for k in range(8)]   # L_j = c . L_B
            row = {}
            for d in range(8):
                row[8 * pos[j] + d] = (row.get(8 * pos[j] + d, 0) + Li[d]) % P
                for k, b in enumerate(basis):
                    key = 8 * pos[b] + d
                    row[key] = (row.get(key, 0) - c[k] * Li[d]) % P
            rows.append(row)
    return rows, None


def rank_mod(vectors):
    e = Echelon()
    return sum(e.insert({k: x for k, x in enumerate(v) if x}) for v in vectors)


def known_kernel(live):
    """Gauge M = L S (64 unit S) and torus M = -t_i L_i / 2 (one per live line), as sparse M-vectors."""
    half = pow(2, P - 2, P)
    vecs = []
    for a in range(8):
        for b in range(8):
            vecs.append({8 * k + b: LINES[x][a] for k, x in enumerate(live) if LINES[x][a]})
    for k, x in enumerate(live):
        vecs.append({8 * k + d: (-LINES[x][d] * half) % P for d in range(8) if LINES[x][d]})
    return vecs


def certificate(live, full=False):
    """(ok, info): ok when rank_p >= 7v - 63 and the known kernel spans 64 + v - 1 (full: insert every row)."""
    v = len(live)
    t0 = time.time()
    rows, bad = masked_system(live)
    if rows is None:
        return False, 'live line %d has degenerate orthogonal span' % bad
    known = known_kernel(live)
    rng = random.Random(v)
    fixture = True
    for _ in range(2):                               # random combinations of the known kernel vectors
        comb = {}
        for vec in known:
            f = rng.randrange(1, P)
            for k, x in vec.items():
                comb[k] = (comb.get(k, 0) + f * x) % P
        fixture &= all(sum(comb.get(k, 0) * x for k, x in r.items()) % P == 0 for r in rows)
    e = Echelon()
    target = 7 * v - 63
    rank = 0
    for r in rows:
        rank += e.insert(r)
        if rank == target and not full:
            break
    span = rank_mod_sparse(known)
    ok = fixture and rank == target and span == 64 + v - 1
    return ok, ('v = %d, %d equations: rank_p %s %d, known kernel span %d (target %d, %d)%s (%.1f s)'
                % (v, len(rows), '=' if full else '>=', rank, span, target, 64 + v - 1,
                   ', so kernel = gauge 64 + torus %d' % (v - 1) if ok else '', time.time() - t0))


def certify(live, label, full=False):
    return check('C.' + label, *certificate(live, full))


def rank_mod_sparse(vecs):
    e = Echelon()
    return sum(e.insert(dict(x)) for x in vecs)


def main():
    rng = random.Random(20261013)
    frames = all_frames()
    check('A.frames', len(frames) == 2025 and all(sum(1 for F in frames if i in F) == 135 for i in range(N)),
          '2025 frames, each line in 135')
    F0 = min(frames, key=sorted)
    nframes, disjoint, classes, gens, ok = stabilizer_orbits(frames, F0, rng)
    covered = sum(len(c) for c in classes)
    check('B.orbits', nframes == 2025 and len(disjoint) == 1260 and covered == 1260 and ok,
          'W acts transitively on frames (BFS reaches all 2025); %d Schreier elements fixing F0 split the 1260 '
          'frames disjoint from F0 into %d classes of sizes %s' % (gens, len(classes), [len(c) for c in classes]))
    certify(list(range(N)), 'P120')
    certify([i for i in range(N) if i not in F0], 'P112')
    for k, cls in enumerate(classes):
        F1 = min(cls, key=sorted)
        certify([i for i in range(N) if i not in F0 and i not in F1], 'P104.class%d(%d frames)' % (k, len(cls)), full=True)
    # negative control: two mutually orthogonal D4 blocks (24 lines); the torus splits and the test must fail
    supp = lambda v: [k for k, x in enumerate(v) if x]
    blocks = [i for i, v in enumerate(LINES) if max(supp(v)) < 4 or min(supp(v)) >= 4]
    ok, info = certificate(blocks)
    check('D.control', len(blocks) == 24 and not ok, 'D4 + D4 live set is rejected: ' + info)
    # finite seeded sample of deeper random punctures (evidence only, not a theorem about every puncture)
    sample = {}
    for p in (24, 32, 40, 48, 56, 64, 72, 80):
        sample[p] = sum(certificate(sorted(rng.sample(range(N), N - p)))[0] for _ in range(8))
    check('E.sample', all(n == 8 for n in sample.values()),
          'seeded random punctures, certified rigid out of 8 at p = ' + ', '.join('%d: %d' % kv for kv in sample.items()))
    if not all(RESULTS):
        print('FAILED %d of %d checks' % (RESULTS.count(False), len(RESULTS)))
        sys.exit(1)
    print('PASS_P104_MASKED_LOCAL_RIGIDITY: P120, P112 and all %d frame-pair punctures (%d classes) infinitesimally '
          'rigid at 2G; D4+D4 control rejected; seeded sample p=24..80 rigid 64/64; local only, no new kappa'
          % (len(disjoint), len(classes)))


if __name__ == '__main__':
    main()
