"""Staircase data-entrance corner certificate (stdlib only).

Sparse flag family + staircase cells:
  rows   lambda_b = E(b,b) (b < h-1), lambda_{h-1} = al E(h-1,0) + be E(0,h-1);  E(RC[t]) (staircase rows)
  cols   E(CC[t]) (staircase columns);  mu_j = a_j E(j,j+1) + b_j E(j+1,j) (j < h-1), mu_{h-1} = E(h-1,h-1)
Checks:
 1. the sparse R_b, C_b are flag-family members (supports, zero diagonal entries) with all trace conditions;
    the flag diagonal factors f1..f4 are nonzero on every line at the point (U, V of point(h, 1)) and the inner corners
    of the rank-(h-1) data classes are nonzero, so the flag-basis lemmas (lower-triangular corners, side lemma) apply
    to this family at the SAME U, V where check_lifted.py verifies the side lemma;
 2. upper bound, identically in all parameters: for every north-east block of the (2h-1)x(2h-1) entrance corner,
    rank <= min vertex cut of the rows-terms-cols graph (max flow, cut re-verified);
 3. lower bound at one point: the corner at sampled line pairs has rightmost pivots whose NE rank function equals the
    upper bound on every nontrivial block, and is invertible; its runs are (h-2, h-5, 1^6).
So the entrance compiles to m-4h+2 and runs (h-2, h-5, 1^6) on a Zariski-open set (partial-swap lemma).
Negative control (--control): random elementary cells instead of the staircase must NOT certify.
--ij: fixed explicit axis bases U = V = I + J instead of point(h, 1).
Usage: python3 check_stair.py h [npairs] [--control] [--ij]"""
import sys, random
from itertools import combinations
from collections import deque
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from linalg import inv_mod_matrix, rightmost_pivots
from check_lifted import point_UV

P = 67108859                                   # the prime of round six's draws (sparse parameters depend on it)
def iv(x): return pow(x % P, P - 2, P)


def design(h, kind='stair'):
    if kind == 'stair':
        RC = [(0, 3)] + [(r + 1, r - 1) for r in range(1, h - 1)]
        CC = [(c + 1, c + 3) for c in range(h - 3)] + [(0, h - 3), (0, h - 2)]
        return RC, CC
    reserved = {(b, b) for b in range(h)} | {(h - 1, 0), (0, h - 1)}
    for j in range(h - 1): reserved |= {(j, j + 1), (j + 1, j)}
    free = sorted(set((i, j) for i in range(h) for j in range(h)) - reserved)
    rng = random.Random(kind); cells = rng.sample(free, 2 * h - 2)
    return cells[:h - 1], cells[h - 1:]


def structure(h, RC, CC):
    rows = [{(b, b)} for b in range(h - 1)] + [{(h - 1, 0), (0, h - 1)}] + [{c} for c in RC]
    cols = [{c} for c in CC] + [{(j, j + 1), (j + 1, j)} for j in range(h - 1)] + [{(h - 1, h - 1)}]
    for f in rows:
        for g in cols: assert not (f & g), 'identity term would not vanish'
    assert len(set().union(*rows) | set().union(*cols)) == sum(map(len, rows)) + sum(map(len, cols)), 'cells reused'
    terms = []
    for l in range(h): terms.append(({i for i, f in enumerate(rows) if any(c[1] == l for c in f)},
                                     {j for j, g in enumerate(cols) if any(c[1] == l for c in g)}))
    for k in range(h): terms.append(({i for i, f in enumerate(rows) if any(c[0] == k for c in f)},
                                     {j for j, g in enumerate(cols) if any(c[0] == k for c in g)}))
    terms.append((set(range(len(rows))), set(range(len(cols)))))
    return rows, cols, terms


def cut_bound(rows_, cols_, terms):
    T = [(sr & rows_, sc & cols_) for sr, sc in terms]
    nodes = [('r', r) for r in rows_] + [('t', t) for t in range(len(T))] + [('c', c) for c in cols_]
    idx = {nd: i for i, nd in enumerate(nodes)}
    BIG = 10**6; N = 2 * len(nodes) + 2; S_, K_ = N - 2, N - 1; cap = {}; adj = [[] for _ in range(N)]
    def add(a, b, c):
        if (a, b) not in cap: adj[a].append(b); adj[b].append(a); cap[a, b] = 0; cap.setdefault((b, a), 0)
        cap[a, b] += c
    for nd, k in idx.items(): add(2 * k, 2 * k + 1, 1)
    for r in rows_: add(S_, 2 * idx['r', r], BIG)
    for c in cols_: add(2 * idx['c', c] + 1, K_, BIG)
    for t, (sr, sc) in enumerate(T):
        if not sr or not sc: continue
        for r in sr: add(2 * idx['r', r] + 1, 2 * idx['t', t], BIG)
        for c in sc: add(2 * idx['t', t] + 1, 2 * idx['c', c], BIG)
    flow = 0
    while True:
        par = {S_: None}; dq = deque([S_])
        while dq and K_ not in par:
            a = dq.popleft()
            for b in adj[a]:
                if b not in par and cap[a, b] > 0: par[b] = a; dq.append(b)
        if K_ not in par: break
        b = K_
        while par[b] is not None: a = par[b]; cap[a, b] -= 1; cap[b, a] += 1; b = a
        flow += 1
    reach = set(par)
    cut = [nd for nd, k in idx.items() if 2 * k in reach and 2 * k + 1 not in reach]
    R0 = {x for t_, x in cut if t_ == 'r'}; T0 = {x for t_, x in cut if t_ == 't'}; C0 = {x for t_, x in cut if t_ == 'c'}
    assert len(cut) == flow
    for t, (sr, sc) in enumerate(T):                       # the cut is a certificate: every other term is covered
        if t in T0: continue
        assert not (sr - R0) or not (sc - C0), 'cut misses a term'
    return flow


def sparse_params(h, rng):
    nz = lambda: rng.randrange(1, P)
    return dict(al=nz(), be=nz(), a=[nz() for _ in range(h - 1)], b=[nz() for _ in range(h - 1)])


def runs(pc):
    pts = sorted((i, c) for i, c in enumerate(pc) if c >= 0); out = []; prev = None
    for i, c in pts:
        if prev and i == prev[0] + 1 and c == prev[1] + 1: out[-1] += 1
        else: out.append(1)
        prev = (i, c)
    return out


def mv(A, x): return [sum(a * b for a, b in zip(r, x)) % P for r in A]


def flag_factors(h, sp, U, V, Ui, Vi):
    """check 1: family membership, trace conditions, f1..f4 and inner corners nonzero on every line."""
    R = [[[0] * h for _ in range(h)] for _ in range(h)]; C = [[[0] * h for _ in range(h)] for _ in range(h)]
    for b in range(h - 1): R[b][b][b] = 1
    R[h - 1][h - 1][0] = sp['al']; R[h - 1][0][h - 1] = sp['be']
    for j in range(h - 1): C[j][j][j + 1] = sp['a'][j]; C[j][j + 1][j] = sp['b'][j]
    C[h - 1][h - 1][h - 1] = 1
    for b in range(h):
        assert all(R[b][i][k] == 0 for i in range(h) for k in range(h) if i > b or k > b)
        assert all(C[b][i][k] == 0 for i in range(h) for k in range(h) if i < b or k < b)
        if b < h - 1: assert C[b][b][b] == 0
    assert R[h - 1][h - 1][h - 1] == 0
    for i in range(h):
        for j in range(h):
            assert sum(R[i][a][b] * C[j][a][b] for a in range(h) for b in range(h)) % P == 0, 'trace condition'
    UT = [list(c) for c in zip(*U)]; VT = [list(c) for c in zip(*V)]
    Rrow = [R[k][k] for k in range(h)]; Crow = [C[k][k] for k in range(h)]
    Rcol = [[R[k][i][k] for i in range(h)] for k in range(h)]; Ccol = [[C[k][i][k] for i in range(h)] for k in range(h)]
    zeros = inner = 0; i9 = iv(9); i2 = iv(2); lines = 0
    for t in combinations(range(h), 3):
        tv = [int(q in t) for q in range(h)]; g = [(x - 3 * i9) * i2 % P for x in tv]
        a, b, c, d = mv(VT, tv), mv(Vi, g), mv(UT, tv), mv(Ui, g)
        for M, x in ((Rrow, a), (Crow, b), (Rcol, c), (Ccol, d)):
            zeros += sum(1 for v in mv(M, x) if v == 0)
        inner += (c[0] * d[h - 1] % P == 0) + (a[0] * b[h - 1] % P == 0); lines += 1
    return lines, zeros, inner


def corner_at(h, rows, cols, p, xi, v, nu):
    """rows . (q1 (x) q2) . cols, (q1 (x) q2) vec G = vec(q1 G q2^T), q1 = I - p xi^T, q2 = I - v nu^T."""
    q1 = [[(int(i == k) - p[i] * xi[k]) % P for k in range(h)] for i in range(h)]
    q2 = [[(int(i == k) - v[i] * nu[k]) % P for k in range(h)] for i in range(h)]
    out = [[0] * len(cols) for _ in rows]
    for j, col in enumerate(cols):
        G = [[0] * h for _ in range(h)]
        for (a, b), val in col.items(): G[a][b] = val % P
        qG = [[sum(q1[i][k] * G[k][l] for k in range(h)) % P for l in range(h)] for i in range(h)]
        Y = [[sum(qG[i][l] * q2[k][l] for l in range(h)) % P for k in range(h)] for i in range(h)]
        for i, row in enumerate(rows):
            out[i][j] = sum(val * Y[a][b] for (a, b), val in row.items()) % P
    return out


def main(h, npairs=20, kind='stair', seed=1, ij=False):
    RC, CC = design(h, kind); n = 2 * h - 1
    _, _, terms = structure(h, RC, CC)
    U, V = point_UV(h, seed)
    if ij: U = [[1 + int(i == k) for k in range(h)] for i in range(h)]; V = [r[:] for r in U]   # fixed U = V = I + J
    U = [[x % P for x in r] for r in U]; V = [[x % P for x in r] for r in V]
    Ui, Vi = inv_mod_matrix(U, P), inv_mod_matrix(V, P)
    sp = sparse_params(h, random.Random(1000 + seed))
    lines, zeros, inner = flag_factors(h, sp, U, V, Ui, Vi)
    print('1. sparse flag family: trace conditions OK; f1..f4 zeros %d over %d lines x %d rows; inner-corner zeros %d'
          % (zeros, lines, h, inner), flush=True)
    rows = [{(b, b): 1} for b in range(h - 1)] + [{(h - 1, 0): sp['al'], (0, h - 1): sp['be']}] + [{c: 1} for c in RC]
    cols = [{c: 1} for c in CC] + [{(j, j + 1): sp['a'][j], (j + 1, j): sp['b'][j]} for j in range(h - 1)] + [{(h - 1, h - 1): 1}]
    trip = list(combinations(range(h), 3)); prng = random.Random(seed + 7); UT = [list(c) for c in zip(*U)]; VT = [list(c) for c in zip(*V)]
    i9 = iv(9); i2 = iv(2); pats = {}
    def line(t, AT, Ai):
        tv = [int(i in t) for i in range(h)]; g = [(x - 3 * i9) * i2 % P for x in tv]
        return mv(AT, tv), mv(Ai, g)
    for _ in range(npairs):
        t1, t2 = prng.choice(trip), prng.choice(trip)
        p, xi = line(t1, UT, Ui); v, nu = line(t2, VT, Vi)
        pc = tuple(rightmost_pivots(corner_at(h, rows, cols, p, xi, v, nu), P)); pats[pc] = pats.get(pc, 0) + 1
    pc = list(max(pats, key=pats.get))
    rho = [[sum(1 for r in range(i + 1) if pc[r] >= j) for j in range(n)] for i in range(n)]
    certs = above = 0
    for i in range(n):
        for j in range(n):
            if rho[i][j] == min(i + 1, n - j): continue
            ub = cut_bound(set(range(i + 1)), set(range(j, n)), terms); certs += 1
            assert ub >= rho[i][j]
            above += ub > rho[i][j]
    ok = above == 0 and -1 not in pc and len(pats) == 1 and zeros == 0 and inner == 0
    print('2-3. %d pairs, distinct pivot patterns %d; runs %s invertible %s; nontrivial NE blocks %d, symbolic bound '
          'above evaluated rank on %d' % (npairs, len(pats), runs(pc), -1 not in pc, certs, above), flush=True)
    print('RESULT h=%d kind=%s runs=%s certified=%s' % (h, kind, sorted(runs(pc), reverse=True), ok), flush=True)
    return ok, sorted(runs(pc), reverse=True)


if __name__ == '__main__':
    h = int(sys.argv[1]); npairs = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 20
    ok, _ = main(h, npairs, 'rand1' if '--control' in sys.argv else 'stair', ij='--ij' in sys.argv)
    sys.exit(0 if ok or '--control' in sys.argv else 1)
