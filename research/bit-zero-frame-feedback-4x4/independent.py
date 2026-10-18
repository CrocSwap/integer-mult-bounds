#!/usr/bin/env python3
"""Independent check of the 4x4 dirty-shear certificate; imports no primary or predecessor code.

Different representation and decomposition from verify.py:
  * matrices are column-packed (byte c holds column c; bit r is row r);
  * lower bounds are per orbit representative, by direct lookup of T_K X in a ball, with no
    coset grouping: no unrestricted word of (minimum - 1) gates exists;
  * the J-I orbit's 11-gate exclusion normalizes the *last* gate under the diagonal S4
    stabilizer (verify.py normalizes the first gate);
  * every one of the 65,536 labeled K receives its orbit witness transported by register
    renaming, replayed on all 256 dirty inputs, and checked against costs_hex.

Prepared for rtyu193-rgb with Claude Code (Claude Opus 5.5). Apache-2.0.
"""
import itertools
import json
from pathlib import Path
import time

import numpy as np

if not __debug__:
    raise SystemExit("checks use assert; run without -O")

CERT = Path(__file__).resolve().parent / "CERTIFICATE.json"
H = T = 4
N = H + T
U64 = np.uint64
ONES = U64(0x0101010101010101)
LAST_GATE_REPS = [(1, 0), (5, 4), (4, 0), (5, 0), (0, 4), (0, 5)]   # one per diagonal-S4 gate orbit


def gate(X, d, s):
    """Left multiplication by I + e_d e_s^T on column-packed matrices: in every column, bit d ^= bit s."""
    return X ^ (((X >> U64(s)) & ONES) << U64(d))


def shear(k, X):
    """T_K X: in every column, bit (H+i) ^= bit j for each K[i][j] = 1."""
    Y = X.copy()
    for i in range(T):
        for j in range(H):
            if (k >> (i * H + j)) & 1:
                Y ^= ((X >> U64(j)) & ONES) << U64(H + i)
    return Y


def balls(radius):
    """Unrestricted balls B_0..B_radius as sorted arrays (cumulative)."""
    G = [(d, s) for d in range(N) for s in range(N) if d != s]
    seen = np.array([sum(1 << (9 * c) for c in range(N))], U64)
    frontier = seen.copy()
    out = [seen.copy()]
    for _ in range(radius):
        nxt = np.unique(np.concatenate([gate(frontier, d, s) for d, s in G]))
        frontier = nxt[~np.isin(nxt, seen)]
        seen = np.union1d(seen, frontier)
        out.append(seen)
    return out


def contains(ball, q):
    """Boolean membership of q in a sorted ball, by binary search."""
    i = np.minimum(np.searchsorted(ball, q), len(ball) - 1)
    return ball[i] == q


def orbit_map():
    """For every K: (canonical index, (p, q)) with canon[i][j] = K[p[i]][q[j]]."""
    ks = np.arange(1 << (H * T), dtype=np.int64)
    best = np.full(len(ks), 1 << 20, np.int64)
    arg = np.zeros(len(ks), np.int64)
    perms = [(p, q) for p in itertools.permutations(range(T)) for q in itertools.permutations(range(H))]
    for n, (p, q) in enumerate(perms):
        img = np.zeros_like(ks)
        for i in range(T):
            for j in range(H):
                img |= ((ks >> (p[i] * H + q[j])) & 1) << (i * H + j)
        better = img < best
        best[better], arg[better] = img[better], n
    return best, arg, perms


def replay(word, k):
    x = np.arange(1 << N)
    regs = [(x >> r) & 1 for r in range(N)]
    want = [r.copy() for r in regs]
    for i in range(T):
        for j in range(H):
            if (k >> (i * H + j)) & 1:
                want[H + i] = want[H + i] ^ regs[j]
    for d, s in word:
        regs[d] = regs[d] ^ regs[s]
    return all((a == b).all() for a, b in zip(regs, want))


def main():
    cert = json.loads(CERT.read_text(encoding="utf-8"))
    assert (cert["helpers"], cert["targets"], cert["gate_cost"], cert["ancillas"]) == (H, T, 1, 0)
    costs = np.array([int(c, 16) for c in cert["costs_hex"]])
    assert len(costs) == 1 << 16
    t = time.time()
    canon, arg, perms = orbit_map()
    reps = sorted(set(canon.tolist()))
    entries = {e["k"]: e for e in cert["orbits"]}
    assert sorted(entries) == reps, "orbit representatives differ"
    # Upper bounds: transport each witness to every labeled K; replay all 256 dirty inputs.
    for k in range(1 << 16):
        e = entries[int(canon[k])]
        p, q = perms[arg[k]]
        rename = [q[j] for j in range(H)] + [H + p[i] for i in range(T)]
        word = [(rename[d], rename[s]) for d, s in e["restricted_witness"]]
        assert all(not (d < H and s >= H) and d != s for d, s in word), "restricted alphabet violated"
        assert len(word) == e["minimum"] == costs[k], f"cost mismatch at {k}"
        assert replay(word, k), f"transported witness fails at K={k}"
    hist = np.bincount(costs).tolist()
    assert {str(c): n for c, n in enumerate(hist)} == cert["minimum_histogram"]
    assert sum(e["orbit_size"] for e in cert["orbits"]) == 1 << 16
    print(f"  65,536 transported restricted witnesses replayed on 256 dirty inputs ({time.time()-t:.0f}s)", flush=True)
    # Lower bounds in the unrestricted alphabet (hence also restricted): exclude minimum - 1 gates.
    t = time.time()
    B = balls(5)
    assert [len(b) for b in B] == list(np.cumsum(cert["unrestricted_spheres"])), "sphere sizes differ"
    print(f"  unrestricted balls {[len(b) for b in B]} ({time.time()-t:.0f}s)", flush=True)
    jmi = cert["hard"]["J_minus_I"]
    checked = 0
    for r in reps:
        L = int(costs[r]) - 1
        if L < 0:
            continue
        if L <= 10:
            a = max(0, L - 5)
            assert not contains(B[min(L, 5)], shear(r, B[a])).any(), f"shorter word exists for K={r}"
            checked += 1
        else:
            assert L == 11 and canon[jmi] == r, "only the J-I orbit needs an 11-gate exclusion"
    # J-I itself: <= 10 excluded directly, then exactly 11 by last-gate normalization.
    assert not contains(B[5], shear(jmi, B[5])).any()
    for d, s in LAST_GATE_REPS:
        assert not contains(B[5], gate(shear(jmi, B[5]), d, s)).any(), f"11-gate word, last gate {(d, s)}"
    # Positive controls: the same lookups find attained words one gate longer.
    for r in reps[:40]:
        L = int(costs[r])
        if 1 <= L <= 10:
            assert contains(B[min(L, 5)], shear(r, B[max(0, L - 5)])).any(), f"control miss at {r}"
    print(f"  {checked} orbit lower bounds + J-I 11-gate exclusion ({time.time()-t:.0f}s)", flush=True)
    print(f"PASS_INDEPENDENT_ZERO_FRAME_FEEDBACK_4X4 labeled_maps=65536 orbits={len(reps)} "
          f"dirty_inputs_per_map=256 max_minimum={len(hist) - 1} feedback_gains=0")


if __name__ == "__main__":
    main()
