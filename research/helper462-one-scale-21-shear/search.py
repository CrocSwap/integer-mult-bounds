#!/usr/bin/env python3
"""Heuristic beam search that proposed the words in this package.

Provenance only: this is not a registered check and not a census. It reduces
D_r^{-1} S to the identity by row and column shears whose coefficient clears
one entry or sets one diagonal entry to 1, keeps the `beam` matrices closest
to the identity at each depth, and rebuilds a row-operation word. Arithmetic
is binary floating point restricted to a dyadic grid, so every accepted step
is exact; each returned word is rechecked with exact fractions. A run that
returns nothing proves nothing.

Usage: search.py OUTDIR BEAM SEEDS NOISE [EXTRA_COEFFICIENTS [MAXDEPTH [ROWS]]]
"""
import json
import random
import sys
from fractions import Fraction
from multiprocessing import Pool
from pathlib import Path

RESULT = Path(__file__).resolve().parents[2] / "research/bit-completed-backend-api/science/RESULT.json"
S = [[int(entry) for entry in row] for row in json.loads(RESULT.read_text())["matcher"]]
N = 8
GRID = 4096.0
BOUND = 1024.0


def transpose(m):
    return tuple(zip(*m))


def nnz(m):
    return sum(1 for i in range(N) for j in range(N) if m[i][j] != (1.0 if i == j else 0.0))


def row_score(row, t):
    return sum(1 for j in range(N) if row[j] != (1.0 if j == t else 0.0))


def children(m, score, extra):
    """Yield (child, child_score, (t, s, a)) for row operations row_t += a*row_s."""
    for t in range(N):
        rt = m[t]
        base = score - row_score(rt, t)
        for s in range(N):
            if s == t:
                continue
            rs = m[s]
            coefs = set(extra)
            for c in range(N):
                y = rs[c]
                if y == 0.0:
                    continue
                v = rt[c]
                if v != 0.0:
                    coefs.add(-v / y)
                if c == t and v != 1.0:
                    coefs.add((1.0 - v) / y)
            for a in coefs:
                if a == 0.0 or abs(a) > BOUND or (a * GRID) != int(a * GRID):
                    continue
                new = tuple(rt[c] + a * rs[c] for c in range(N))
                ok = True
                for x in new:
                    if abs(x) > BOUND or (x * GRID) != int(x * GRID):
                        ok = False
                        break
                if not ok:
                    continue
                yield m[:t] + (new,) + m[t + 1:], base + row_score(new, t), (t, s, a)


def search(args):
    r, beam, seed, noise, extra, maxdepth = args
    rng = random.Random(seed)
    start = tuple(tuple(float(Fraction(x, -16 if i == r else 1)) for x in row) for i, row in enumerate(S))
    ident = tuple(tuple(1.0 if i == j else 0.0 for j in range(N)) for i in range(N))
    layers = [{start: None}]
    frontier = [(nnz(start), start)]
    seen = {start}
    for depth in range(1, maxdepth + 1):
        cand = {}
        for score, m in frontier:
            for child, cs, mv in children(m, score, extra):
                if child not in seen and child not in cand:
                    cand[child] = (cs, m, ("R",) + mv)
            mt = transpose(m)
            for child, cs, mv in children(mt, score, extra):
                ch = transpose(child)
                if ch not in seen and ch not in cand:
                    cand[ch] = (cs, m, ("C",) + mv)
        if not cand:
            return r, seed, None
        if ident in cand:
            layers.append({ident: cand[ident][1:]})
            path = []
            cur = ident
            for layer in reversed(layers[1:]):
                parent, mv = layer[cur]
                path.append(mv)
                cur = parent
            path.reverse()
            return r, seed, path
        items = sorted(cand.items(), key=lambda kv: kv[1][0] + (rng.random() * noise if noise else 0.0))[:beam]
        layers.append({k: v[1:] for k, v in items})
        frontier = [(v[0], k) for k, v in items]
        seen.update(k for k, _ in items)
    return r, seed, None


def to_word(path):
    """Row-op letters, first to last on I, whose product is D_r^{-1} S."""
    rights = [mv for mv in path if mv[0] == "C"]
    lefts = [mv for mv in path if mv[0] == "R"]
    word = []
    for _, t, s, a in rights:  # col_t += a col_s  ==  M (I + a E_{s,t})
        word.append((s, t, -Fraction(a)))
    for _, t, s, a in reversed(lefts):
        word.append((t, s, -Fraction(a)))
    return word


def check(word, r):
    m = [[Fraction(int(i == j)) for j in range(N)] for i in range(N)]
    for t, s, a in word:
        assert t != s and a != 0
        m[t] = [m[t][c] + a * m[s][c] for c in range(N)]
    m[r] = [x * -16 for x in m[r]]
    return m == [[Fraction(x) for x in row] for row in S]


if __name__ == "__main__":
    outdir = Path(sys.argv[1])
    beam = int(sys.argv[2])
    seeds = int(sys.argv[3])
    noise = float(sys.argv[4])
    extra = tuple(float(x) for x in sys.argv[5].split(",")) if len(sys.argv) > 5 and sys.argv[5] else ()
    maxdepth = int(sys.argv[6]) if len(sys.argv) > 6 else 30
    rows = [int(x) for x in sys.argv[7].split(",")] if len(sys.argv) > 7 else list(range(N))
    jobs = [(r, beam, seed, noise, extra, maxdepth) for seed in range(seeds) for r in rows]
    best = {}
    with Pool() as pool:
        for r, seed, path in pool.imap_unordered(search, jobs):
            if path is None:
                print("row", r, "seed", seed, "none", flush=True)
                continue
            word = to_word(path)
            ok = check(word, r)
            print("row", r, "seed", seed, "len", len(word), "exact", ok, flush=True)
            if ok and (r not in best or len(word) < len(best[r])):
                best[r] = word
                target = outdir / ("best_row%d_len%d.json" % (r, len(word)))
                target.write_text(json.dumps([[t, s, str(a)] for t, s, a in word]) + "\n")
    print({r: len(w) for r, w in sorted(best.items())})
