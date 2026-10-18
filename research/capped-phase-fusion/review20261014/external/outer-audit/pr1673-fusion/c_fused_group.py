"""Part C: one fused group in the DENSE-UNION regime of PR2044 (g*mu >= 1, U ~ whole microbox), exact rationals.

For each of g axes take a random banded (bandwidth W) row-dominant rational matrix Q_i on n coordinates, a capped
carving (W endpoints, B-interiors, W separators, all boundary), and the five-factor forward schedule
   diag(A,I) . E_C . diag(A^-1,I) diag(I,F) . E_B . diag(A,I)          (note line 231, execution right to left)
with three dense tensor stages (each ONE simultaneous global call, regardless of g) and two sparse windows.
Each sparse window is executed (a) as PR1673's per-axis scan of U (PHASE-LAYOUT-AUDIT.md:84-99) and
(b) as PR2044's flag-class rounds (UNION-SCHEDULE.md), with record-visit counts. The final tensor is compared with
the direct per-axis application of Q_1 x ... x Q_g. Counts are reported per record of the microbox.
"""
import itertools, json, math, random, sys
from fractions import Fraction as Q

def eye(n): return [[Q(int(i == j)) for j in range(n)] for i in range(n)]
def mm(a, b): return [[sum(x * y for x, y in zip(r, c)) for c in zip(*b)] for r in a]
def inv(a):
    n = len(a); m = [r[:] + e for r, e in zip(a, eye(n))]
    for j in range(n):
        k = next(i for i in range(j, n) if m[i][j]); m[j], m[k] = m[k], m[j]
        v = m[j][j]; m[j] = [x / v for x in m[j]]
        for i in range(n):
            if i != j and m[i][j]:
                v = m[i][j]; m[i] = [x - v * y for x, y in zip(m[i], m[j])]
    return [r[n:] for r in m]
def sub(h, R, C): return [[h[i][j] for j in C] for i in R]

def carve(n, B, W):
    J = set(range(W)) | set(range(n - W, n)); blocks = []; c = W; stop = n - W
    while stop - c >= B + W:
        blocks.append(list(range(c, c + B))); J.update(range(c + B, c + B + W)); c += B + W
    J.update(range(c, stop))
    return blocks, sorted(J)

def axis_factors(n, W, B, rng):
    H = [[Q(0)] * n for _ in range(n)]
    for i in range(n):
        H[i][i] = Q(1)
        for j in range(max(0, i - W), min(n, i + W + 1)):
            if j != i: H[i][j] = Q(rng.randint(-3, 3), 16 * W)
    blocks, J = carve(n, B, W); I = [i for i in range(n) if i not in J]
    A, Bm, C, D = sub(H, I, I), sub(H, I, J), sub(H, J, I), sub(H, J, J)
    Ai = inv(A); F = [[d - x for d, x in zip(rd, rx)] for rd, rx in zip(D, mm(mm(C, Ai), Bm))]
    def full(blocksmap):
        M = eye(n)
        for (R, Cc), blk in blocksmap:
            for ii, i in enumerate(R):
                for jj, j in enumerate(Cc): M[i][j] = blk[ii][jj]
        return M
    dA = full([((I, I), A)]); dAi = full([((I, I), Ai)]); dF = full([((J, J), F)])
    EB = full([((I, J), Bm)]); EC = full([((J, I), C)])
    for i in I: EB[i][i] = Q(1)
    for j in J: EC[j][j] = Q(1)
    # sanity: product equals H (execution right to left)
    M = eye(n)
    for f in [dA, EB, dF, dAi, EC, dA]: M = mm(f, M)
    assert M == H
    # E_i: coordinates moved or read by the sparse factors
    E = sorted(set(J) | {i for i in I for j in J if Bm[I.index(i)][J.index(j)] or C[J.index(j)][I.index(i)]})
    return dict(H=H, dense=[dA, dAi, dA], win1=mm(dF, EB), win2=EC, E=E, J=J, blocks=len(blocks))

def apply_axis(T, M, ax, n, g):
    out = dict(T)
    for other in itertools.product(range(n), repeat=g - 1):
        idx = [other[:ax] + (i,) + other[ax:] for i in range(n)]
        old = [T[k] for k in idx]
        for i, k in enumerate(idx): out[k] = sum(M[i][j] * old[j] for j in range(n) if M[i][j])
    return out

def window_pr1673(T, mats, Es, n, g):
    U = [x for x in T if any(x[i] in Es[i] for i in range(g))]
    visits = len(U)                       # one scan forming U
    S = {x: T[x] for x in U}
    for i in range(g):
        visits += len(U)                  # PHASE-LAYOUT-AUDIT step 1: scan U once per axis
        Ui = [x for x in U if x[i] in Es[i]]
        lines = {}
        for x in Ui: lines.setdefault(x[:i] + x[i + 1:], []).append(x)
        for key, xs in lines.items():
            xs.sort(key=lambda x: x[i]); old = [S[x] for x in xs]; Ei = [x[i] for x in xs]
            for a, x in enumerate(xs): S[x] = sum(mats[i][x[i]][Ei[b]] * old[b] for b in range(len(xs)))
        visits += len(Ui)                 # merge back
    T = dict(T); T.update(S)
    return T, visits, len(U)

def window_radix(T, mats, Es, n, g):
    F = {x: [i for i in range(g) if x[i] in Es[i]] for x in T}
    S = {x: T[x] for x in T if F[x]}
    visits = len(S); r = 1
    while True:
        Sr = [x for x in S if len(F[x]) >= r]
        if not Sr: break
        visits += len(Sr)
        groups = {}
        for x in Sr:
            f = F[x][r - 1]; groups.setdefault((f, x[:f] + x[f + 1:]), []).append(x)
        new = {}
        for (f, key), xs in groups.items():
            xs.sort(key=lambda x: x[f]); old = [S[x] for x in xs]; Ef = [x[f] for x in xs]
            for x in xs: new[x] = sum(mats[f][x[f]][Ef[b]] * old[b] for b in range(len(xs)))
        S.update(new); r += 1
    T = dict(T); T.update(S)
    return T, visits

rng = random.Random(2044)
res = []
for g, n, W, B in [(2, 12, 1, 2), (3, 10, 1, 2), (4, 8, 1, 2), (3, 12, 1, 4), (4, 9, 1, 4), (5, 6, 1, 2)]:
    ax = [axis_factors(n, W, B, rng) for _ in range(g)]
    V = n**g
    X = {x: Q(rng.randint(-50, 50)) for x in itertools.product(range(n), repeat=g)}
    ref = X
    for i in range(g): ref = apply_axis(ref, ax[i]['H'], i, n, g)
    def run(window):
        T = X; vis = 0; dense_calls = 0; scans = 0
        T = {**T}
        for i in range(g): T = apply_axis(T, ax[i]['dense'][0], i, n, g)
        dense_calls += 1
        for w, key in [(1, 'win1'), (2, 'win2')]:
            mats = [a[key] for a in ax]; Es = [a['E'] for a in ax]
            out = window(T, mats, Es, n, g); T = out[0]; vis += out[1]; scans += 2   # gather + scatter
            if w == 1:
                for i in range(g): T = apply_axis(T, ax[i]['dense'][1], i, n, g)
                dense_calls += 1
        for i in range(g): T = apply_axis(T, ax[i]['dense'][2], i, n, g)
        dense_calls += 1
        assert T == ref
        return vis, dense_calls, scans
    v1, dc, sc = run(lambda T, m, E, n_, g_: window_pr1673(T, m, E, n, g))
    v2, _, _ = run(lambda T, m, E, n_, g_: window_radix(T, m, E, n, g))
    mu = max(len(a['E']) for a in ax) / n
    U = sum(1 for x in X if any(x[i] in ax[i]['E'] for i in range(g)))
    sumF = sum(sum(x[i] in ax[i]['E'] for i in range(g)) for x in X)
    res.append(dict(g=g, n=n, W=W, B=B, V=V, mu=round(mu, 3), g_mu=round(g * mu, 3), U_over_V=round(U / V, 3),
                    dense_global_calls=dc, full_scans_for_windows=sc,
                    pr1673_union_visits_per_record=round(v1 / V, 3), radix_union_visits_per_record=round(v2 / V, 3),
                    sumF_over_V=round(sumF / V, 3), exact_match=True))
    print(json.dumps(res[-1])); sys.stdout.flush()
json.dump(res, open(sys.argv[1], 'w'), indent=1)
