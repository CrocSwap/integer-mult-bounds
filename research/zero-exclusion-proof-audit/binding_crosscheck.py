#!/usr/bin/env python3
"""Binding cross-check: PR1650's criterion() against a second implementation of PR1560's hypotheses.

The second implementation below is written from proof.md section 3's prose, with deliberately different methods:
classes are found by orthogonality (not by sign parity), (D) uses the exact rational rank of the integer Gram
matrix M^T M by fraction-free (Bareiss) elimination (not a modular rank of M), and (G) uses breadth-first search.
It is compared with PR1650's criterion (head d960f8a2, research/complex-rank8-rigidity-p105/verify.py), which this
script imports from a path given on the command line. PR1650 is not on main, so this script is not part of the
registered replay; its output is recorded in the README.

    python3 -I -B research/zero-exclusion-proof-audit/binding_crosscheck.py PATH/TO/PR1650/verify.py [--samples N] [--thin]
"""

import importlib.util
import itertools
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify as mine  # noqa: E402  (this package's model: lines, G, frames)

G, N = mine.G, mine.N


def bareiss_rank(A):
    """Exact rank of an integer matrix by fraction-free elimination."""
    A = [row[:] for row in A]
    rows, cols = len(A), len(A[0]) if A else 0
    r, prev = 0, 1
    for c in range(cols):
        p = next((i for i in range(r, rows) if A[i][c]), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        for i in range(r + 1, rows):
            for j in range(c + 1, cols):
                A[i][j] = (A[i][j] * A[r][c] - A[i][c] * A[r][j]) // prev
            A[i][c] = 0
        prev = A[r][c]
        r += 1
    return r


def rank_q(M):
    """rank over Q of a 0-1 (or integer) matrix M, as the rank of its Gram matrix M^T M."""
    if not M:
        return 0
    n = len(M[0])
    gram = [[0] * n for _ in range(n)]
    for row in M:
        nz = [j for j in range(n) if row[j]]
        for a in nz:
            ga = gram[a]
            for b in nz:
                ga[b] += row[a] * row[b]
    return bareiss_rank(gram)


def hypotheses(L, F, frames):
    """Booleans (blocks_nonempty, W, G, D) for live set L (a set of line IDs), pivot frame F (tuple of IDs) and
    the family of all live frames, straight from proof.md section 3."""
    Fs = set(F)
    S_all = [S for S in frames if set(S) <= L]
    non = sorted(L - Fs)
    T = {i: tuple(k for k in F if G[i][k]) for i in non}
    blocks = {}
    for i in non:
        blocks.setdefault(T[i], []).append(i)
    nonempty = len(blocks) == 14
    # (W): a block is witnessed when one class is complete (all 4 lines live) and the other has a live line.
    # Classes by orthogonality among ALL 8 lines of the block (live or not).
    witnessed_pairs = set()
    allblocks = {}
    for i in range(N):
        if i not in Fs:
            allblocks.setdefault(tuple(k for k in F if G[i][k]), []).append(i)
    for t, lines in allblocks.items():
        a = lines[0]
        c1 = [i for i in lines if i == a or G[a][i] == 0]  # a and the lines orthogonal to it
        c2 = [i for i in lines if i not in c1]
        for C, D in ((c1, c2), (c2, c1)):
            if all(i in L for i in C) and any(j in L for j in D):
                witnessed_pairs.update(itertools.combinations(t, 2))
    W = len(witnessed_pairs) == 28
    # (G)
    Gok = True
    for k, l in itertools.combinations(F, 2):
        I = [i for i in non if G[i][k] and G[i][l]]
        if not I:
            Gok = False
            break
        Iset = set(I)
        adj = {i: set() for i in I}
        for S in S_all:
            hit = [i for i in S if i in Iset]
            if len(hit) == 2:
                adj[hit[0]].add(hit[1])
                adj[hit[1]].add(hit[0])
        seen, todo = {I[0]}, [I[0]]
        while todo:
            for j in adj[todo.pop()] - seen:
                seen.add(j)
                todo.append(j)
        if len(seen) != len(I):
            Gok = False
            break
    # (D)
    Dok = True
    for k in F:
        I = [i for i in non if G[i][k]]
        h = [[G[i][k] * G[i][l] for i in I] for l in F if l != k]
        if rank_q(h) != 7:
            Dok = False
            break
        rows = {tuple(1 if i in S else 0 for i in I) for S in S_all}
        if rank_q(sorted(rows)) != len(I) - 7:
            Dok = False
            break
    return nonempty, W, Gok, Dok


def load_pr1650(path):
    spec = importlib.util.spec_from_file_location('pr1650_verify', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    path = sys.argv[1]
    samples = int(sys.argv[sys.argv.index('--samples') + 1]) if '--samples' in sys.argv else 60
    # --thin: delete 11-40 lines instead of 5-10, so blocks, (G) and (D) also fail (thin live families).
    sizes = list(range(11, 41)) if '--thin' in sys.argv else [5, 6, 7, 8, 9, 10]
    pr = load_pr1650(path)
    assert pr.LINES == mine.V and pr.G == mine.G, 'line IDs / G disagree'
    frames = mine.all_frames()
    assert sorted(frames) == sorted(pr.FRAMES)
    F0 = set(pr.FRAME0)
    P112 = [i for i in range(N) if i not in F0]
    rng = random.Random(1560)
    cases = [
        ('pr1560-fixture', (32, 45, 73, 78, 88), (2, 5, 8, 9, 30, 41, 108, 117)),
        ('pr1560-bad-control', (3, 13, 14, 22, 23), (2, 5, 8, 9, 30, 41, 108, 117)),
        ('s13-full-family-g-without-d', (3, 4, 8, 9, 107, 108, 117, 118), (19, 25, 37, 47, 67, 82, 94, 115)),
    ]
    for n in range(samples):
        size = rng.choice(sizes)
        X = tuple(sorted(rng.sample(P112, size)))
        live = set(P112) - set(X)
        cand = [S for S in frames if set(S) <= live]
        if cand:
            cases.append((f'random-{n}-P{112 - size}', X, rng.choice(cand)))
    # Every live frame as pivot for a few deletion sets: early frames fail blocks / (W), as in PR1650's tally.
    for n in range(max(1, samples // 200) if '--thin' not in sys.argv else 0):
        X = tuple(sorted(rng.sample(P112, 7 + n % 4)))
        live = set(P112) - set(X)
        cases += [(f'allframes-{n}', X, S) for S in frames if set(S) <= live]
    tally = {}
    t0 = time.time()
    for name, X, F in cases:
        reason, _ = pr.criterion(X, F)
        L = set(P112) - set(X)
        ne, W, Gk, Dk = hypotheses(L, F, frames)
        # PR1650 tests in the order support, nonempty-blocks, W, G, D and stops at the first failure.
        expect = None if (ne and W and Gk and Dk) else \
            'nonempty-blocks' if not ne else 'W' if not W else 'G' if not Gk else 'D'
        ok = reason == expect
        tally[(reason, ok)] = tally.get((reason, ok), 0) + 1
        if not name.startswith(('random', 'allframes')) or not ok:
            print(f"{'AGREE' if ok else 'DISAGREE'} {name}: PR1650 {reason}; prose (blocks, W, G, D) = {ne, W, Gk, Dk}")
        if not ok:
            sys.exit(1)
    print('tally (PR1650 verdict, agree):', dict(sorted(tally.items(), key=str)))
    print(f'ALL_AGREE {len(cases)} cases in {time.time() - t0:.0f} s')


if __name__ == '__main__':
    main()
