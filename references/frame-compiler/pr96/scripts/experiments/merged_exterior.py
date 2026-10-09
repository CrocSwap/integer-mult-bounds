#!/usr/bin/env python3
"""Merged auxiliary exteriors: exact physical profiles and per-role selection.

Each auxiliary role pays one exterior residual E = I - I_h (x) B (profile
[h, m-2h]). Because auxiliary source frames are free, E may instead be added
to the role's first residual (entrance edge I - (I_h - A_first) (x) B) or, for
a role that is not an output, to its final cleanup (exit edge I - A_last (x) B).
research/merged-exterior/PROOF.md proves that the fixed-basis profile of such
an edge depends only on ranks of local submatrices X[S, T] (Lemma 1). Every
rank here is computed exactly over Q in integer arithmetic (Lemma 2).

Usage: merged_exterior.py OUTDIR [WORKERS]   (writes merged-exterior-selection.json)
"""
import sys
if sys.flags.optimize:
    raise ValueError('Assertions must remain enabled')
sys.dont_write_bytecode = True

from collections import Counter
from hashlib import sha256
from math import log
from multiprocessing import Pool
from pathlib import Path
import gzip, json, os

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'certificates'
BASE = 'balanced-split'
A_, B_ = 23, 25
M_ = A_ * B_


def corner_labels(h):
    """PR34 reversed (23,25) corner labels (research/copied-fixed/reversed/pr34/independent_controls.py)."""
    d = 2 * h + 1; b = h + 2
    r = list(range(h)) + [h - 1] + list(range(h))
    c = list(range(h)) + [0] + list(range(h))
    return [(r[i], i % b) for i in range(d)], [(c[j], (h * b - d + j) % b) for j in range(d)]


def completion(h, rows, cols):
    """PR34 controlled permutations M_beta: prescribed corner labels, then increasing completion."""
    b = h + 2; m = h * b; d = len(rows)
    partial = [{} for _ in range(b)]
    for seq, offset in [(rows, 0), (cols, m - d)]:
        for k, (label, residue) in enumerate(seq):
            alpha, physical = divmod(offset + k, b)
            assert residue == physical
            partial[residue][alpha] = label
    result = []
    for prescribed in partial:
        remaining = iter(sorted(set(range(h)) - set(prescribed.values())))
        result.append([prescribed[i] if i in prescribed else next(remaining) for i in range(h)])
    return result


PERMS = completion(A_, *corner_labels(A_))


def local_index(h):
    """Local coordinate of physical index i = 25*alpha + beta for the axis of dimension h."""
    if h == A_:
        return [PERMS[i % B_][i // B_] for i in range(M_)]
    assert h == B_
    return [i % B_ for i in range(M_)]


def flags(lam):
    """prefix[i] = local coordinates of physical rows < i; suffix[j] = of physical columns >= j."""
    prefix = [0]
    for x in lam:
        prefix.append(prefix[-1] | 1 << x)
    suffix = [0] * (len(lam) + 1)
    for j in range(len(lam) - 1, -1, -1):
        suffix[j] = suffix[j + 1] | 1 << lam[j]
    return prefix, suffix


def projector(core, cover, h):
    """Fixed-I+J envelope projector A = diag(o) + U V^T / d in exact integers.

    Same entries as binary_frame_profiles.cpp. Coordinates fall in three classes
    (core, cover minus core, outside cover); U and V rows depend only on the class.
    """
    full = (1 << h) - 1
    c = core.bit_count(); out = cover & ~core; nn = out.bit_count()
    classes = (core, out, full & ~cover)
    w = (4, 3, 3); z = (3 * (h + 1) - 10, -10, -10); o = (0, 1, 0)
    if c == 3:
        assert core == cover, 'three-point cores are source lines'
        return classes, [(w[k],) for k in range(3)], [(z[k],) for k in range(3)], 6 * (h + 1), out
    assert c in (1, 2) and core & ~cover == 0
    s = 3 - c
    d = 3 * (h + 1) * (s * s + (c - 1) * nn)
    U = [(o[k], w[k]) for k in range(3)]
    V = [(s * z[k] - 3 * (h + 1) * (c - 1) * o[k], 3 * (h + 1) * s * o[k] + nn * z[k]) for k in range(3)]
    return classes, U, V, d, out


def operator(core, cover, h, complement):
    """X = A (mask o, +UV^T/d) or X = I - A (mask 1-o, -UV^T/d)."""
    classes, U, V, d, out = projector(core, cover, h)
    full = (1 << h) - 1
    return (classes, U, V, d, full & ~out, -1) if complement else (classes, U, V, d, out, 1)


def kernel(rows, k):
    """Integer basis of {x in Q^k : r.x = 0 for every row r}, k <= 2."""
    rows = [r for r in rows if any(r)]
    if not rows:
        return [(1,)] if k == 1 else [(1, 0), (0, 1)]
    if k == 1:
        return []
    a, b = rows[0]
    if any(a * y - b * x for x, y in rows[1:]):
        return []
    return [(-b, a)]


def small_rank(M):
    """Rank of an at most 2x2 integer matrix."""
    if not M or not M[0] or not any(any(r) for r in M):
        return 0
    if len(M) == 2 and len(M[0]) == 2 and M[0][0] * M[1][1] - M[0][1] * M[1][0]:
        return 2
    return 1


def rank(X, S, T):
    """Exact rank over Q of X[S, T] for X = diag(mask) + sigma U V^T / d (PROOF.md, Lemma 2)."""
    classes, U, V, d, mask, sigma = X
    if not S or not T:
        return 0
    P = S & T & mask
    S0, T0 = S & ~P, T & ~P
    k = len(U[0])
    counts = [(P & cls).bit_count() for cls in classes]
    C = [[d * (a == b) + sigma * sum(n * V[c][a] * U[c][b] for c, n in enumerate(counts))
          for b in range(k)] for a in range(k)]
    Z = kernel([U[c] for c, cls in enumerate(classes) if S0 & cls], k)
    Y = kernel([V[c] for c, cls in enumerate(classes) if T0 & cls], k)
    C22 = [[sum(y[a] * C[a][b] * z[b] for a in range(k) for b in range(k)) for z in Z] for y in Y]
    return P.bit_count() + (k - len(Z)) + (k - len(Y)) + small_rank(C22) - k


def runs(pivots):
    """Maximal runs of consecutive pivots (i,j),(i+1,j+1) in row order."""
    out, run = [], 0
    for k, (i, j) in enumerate(pivots):
        if k and i == pivots[k - 1][0] + 1 and j == pivots[k - 1][1] + 1:
            run += 1
        else:
            if run:
                out.append(run)
            run = 1
    if run:
        out.append(run)
    return sorted(out, reverse=True)


def merged_profile(X, h, fl):
    """NE profile of I - Y, Y the physical image of the local idempotent X (x) any line (Lemma 1)."""
    prefix, suffix = fl
    m = len(prefix) - 1
    full = (1 << h) - 1
    cache = {}

    def R(S, T):
        key = (S, T)
        if key not in cache:
            cache[key] = rank(X, S, T)
        return cache[key]

    r = R(full, full)

    def rho(i, j):
        if i < 0 or j >= m:
            return 0
        if j <= i + 1:
            return (i - j + 1) - r + R(prefix[j], full) + R(full, suffix[i + 1])
        return R(prefix[i + 1], suffix[j])

    def piv(i, j):
        z = rho(i, j) - rho(i - 1, j) - rho(i, j + 1) + rho(i - 1, j + 1)
        assert z in (0, 1)
        return z

    # Second differences vanish below the band j in {i, i+1}; above it they are
    # nonzero only where a new local row and a new local column first appear.
    pivots = {(i, j) for i in range(m) for j in (i, i + 1) if j < m and piv(i, j)}
    rows = [i for i in range(m) if prefix[i + 1] != prefix[i]]
    cols = [j for j in range(m) if suffix[j] != suffix[j + 1]]
    pivots |= {(i, j) for i in rows for j in cols if j >= i + 2 and piv(i, j)}
    assert len(pivots) == m - r, (len(pivots), m, r)
    return m - r, runs(sorted(pivots))


def local_profile(X, h):
    """Inherited local NE profile of an h x h residual, with rank <= 2 charged as singletons."""
    rows = [(1 << (i + 1)) - 1 for i in range(h)]
    cols = [((1 << h) - 1) & ~((1 << j) - 1) for j in range(h)] + [0]
    rho = [[rank(X, rows[i], cols[j]) for j in range(h + 1)] for i in range(h)]
    pivots = [(i, j) for i in range(h) for j in range(h)
              if rho[i][j] - (rho[i - 1][j] if i else 0) - rho[i][j + 1] + (rho[i - 1][j + 1] if i else 0)]
    rr = rank(X, (1 << h) - 1, (1 << h) - 1)
    assert len(pivots) == rr
    return rr, ([1] * rr if rr <= 2 else runs(pivots))


def cost(blocks):
    return sum(t * log(M_ / t) for t in blocks)


def load_word(h):
    path = OUT / f'{BASE}-word-{h}.json.gz'
    raw = path.read_bytes()
    d = json.loads(gzip.decompress(raw))
    assert d['h'] == h
    first, last = {}, {}
    for s, a, b in d['events']:
        first.setdefault(s, b)
        last[s] = b
    outputs = {s for s, g, c, t in d['outputs']}
    assert sorted(first) == list(range(d['R']))
    return d, first, last, outputs, sha256(raw).hexdigest()


def evaluate(job):
    """Exact costs for one (kind, frame) key: removed local edge, merged edge."""
    h, kind, frame, core, cover = job
    if kind == 'entrance':
        removed = local_profile(operator(core, cover, h, False), h)       # 0 -> A_first
        merged = merged_profile(operator(core, cover, h, True), h, FLAGS[h])   # I - (I - A_first) (x) B
    else:
        removed = local_profile(operator(core, cover, h, True), h)        # A_last -> I_h
        merged = merged_profile(operator(core, cover, h, False), h, FLAGS[h])  # I - A_last (x) B
    return (kind, frame), removed, merged


FLAGS = {h: flags(local_index(h)) for h in (A_, B_)}


def select(h, workers):
    d, first, last, outputs, digest = load_word(h)
    F, R = d['frames'], d['R']
    keys = {('entrance', first[s]) for s in range(R)} | {('exit', last[s]) for s in range(R) if s not in outputs}
    jobs = [(h, k, g, *F[g]) for k, g in sorted(keys)]
    with Pool(workers) as pool:
        result = {key: (removed, merged) for key, removed, merged in pool.map(evaluate, jobs, chunksize=8)}
    exterior = cost([h, M_ - 2 * h])
    choice = {}
    for s in range(R):
        options = [(0.0, 'standard')]
        for kind, g in (('entrance', first[s]), ('exit', last[s])):
            if kind == 'exit' and s in outputs:
                continue
            (rr, removed), (mr, merged) = result[kind, g]
            assert mr == rr + M_ - h
            options.append((cost(removed) + exterior - cost(merged), kind))
        gain, kind = max(options)
        if kind != 'standard' and gain > 1e-9:
            choice[s] = kind
    used = sorted({(choice[s], first[s] if choice[s] == 'entrance' else last[s]) for s in choice})
    return dict(h=h, R=R, word_sha256=digest,
                entrance=sorted(s for s in choice if choice[s] == 'entrance'),
                exit=sorted(s for s in choice if choice[s] == 'exit'),
                merged_edges={f'{k}:{g}': dict(rank=result[k, g][1][0], runs=result[k, g][1][1]) for k, g in used},
                candidate_edges=len(keys))


def selection(workers=None):
    workers = workers or (len(os.sched_getaffinity(0)) if hasattr(os, 'sched_getaffinity') else os.cpu_count())
    return {str(h): select(h, workers) for h in (A_, B_)}


if __name__ == '__main__':
    outdir = Path(sys.argv[1])
    record = selection(int(sys.argv[2]) if len(sys.argv) > 2 else None)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / 'merged-exterior-selection.json').write_text(json.dumps(record, sort_keys=True, separators=(',', ':')) + '\n')
    for h, r in record.items():
        print(f'h={h}: roles {r["R"]}, entrance {len(r["entrance"])}, exit {len(r["exit"])}, '
              f'merged edges {len(r["merged_edges"])} of {r["candidate_edges"]} candidates', flush=True)
