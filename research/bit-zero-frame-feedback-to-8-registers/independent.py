#!/usr/bin/env python3
"""Independent check of the up-to-eight-register certificate; imports no primary or predecessor code.

Column-packed matrices (byte c = column c, bit r = row r); per-orbit lower bounds by direct
lookup of T_K X in unrestricted balls (no coset grouping): no word of (minimum - 1) gates;
every labeled K receives its orbit witness transported by register renaming, replayed on
all 2^(H+T) dirty inputs and checked against costs_hex.

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
U64 = np.uint64
ONES = U64(0x0101010101010101)


def gate(X, d, s):
    return X ^ (((X >> U64(s)) & ONES) << U64(d))


def shear(k, X, H, T):
    Y = X.copy()
    for i in range(T):
        for j in range(H):
            if (k >> (i * H + j)) & 1:
                Y ^= ((X >> U64(j)) & ONES) << U64(H + i)
    return Y


def balls(n, radius):
    G = [(d, s) for d in range(n) for s in range(n) if d != s]
    seen = np.array([sum(1 << (9 * c) for c in range(n))], U64)
    frontier, out = seen.copy(), [seen.copy()]
    for _ in range(radius):
        nxt = np.unique(np.concatenate([gate(frontier, d, s) for d, s in G]))
        frontier = nxt[~np.isin(nxt, seen)]
        seen = np.union1d(seen, frontier)
        out.append(seen)
    return out


def contains(ball, q):
    i = np.minimum(np.searchsorted(ball, q), len(ball) - 1)
    return ball[i] == q


def orbit_map(H, T):
    ks = np.arange(1 << (H * T), dtype=np.int64)
    best = np.full(len(ks), 1 << 40, np.int64)
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


def replay(word, k, H, T):
    n = H + T
    x = np.arange(1 << n)
    regs = [(x >> r) & 1 for r in range(n)]
    want = [r.copy() for r in regs]
    for i in range(T):
        for j in range(H):
            if (k >> (i * H + j)) & 1:
                want[H + i] = want[H + i] ^ regs[j]
    for d, s in word:
        regs[d] = regs[d] ^ regs[s]
    return all((a == b).all() for a, b in zip(regs, want))


def check_shape(sh):
    H, T = sh["helpers"], sh["targets"]
    n = H + T
    costs = np.array([int(c, 16) for c in sh["costs_hex"]])
    assert len(costs) == 1 << (H * T)
    canon, arg, perms = orbit_map(H, T)
    reps = sorted(set(canon.tolist()))
    entries = {e["k"]: e for e in sh["orbits"]}
    assert sorted(entries) == reps, "orbit representatives differ"
    for k in range(1 << (H * T)):
        e = entries[int(canon[k])]
        p, q = perms[arg[k]]
        rename = [q[j] for j in range(H)] + [H + p[i] for i in range(T)]
        word = [(rename[d], rename[s]) for d, s in e["restricted_witness"]]
        assert all(d != s and not (d < H and s >= H) for d, s in word), "restricted alphabet"
        assert len(word) == e["minimum"] == costs[k] and replay(word, k, H, T), f"witness fails at {k}"
    hist = np.bincount(costs).tolist()
    assert {str(c): v for c, v in enumerate(hist)} == sh["minimum_histogram"]
    B = balls(n, 5)
    assert [len(b) for b in B][:len(sh["unrestricted_spheres"])] == list(np.cumsum(sh["unrestricted_spheres"]))
    for r in reps:
        L = int(costs[r]) - 1
        if L < 0:
            continue
        assert L <= 10
        a = max(0, L - 5)
        assert not contains(B[min(L, 5)], shear(r, B[a], H, T)).any(), f"shorter word for K={r}"
    for r in reps[:30]:                # positive controls: the same lookup finds attained words
        L = int(costs[r])
        if L >= 1:
            assert contains(B[min(L, 5)], shear(r, B[max(0, L - 5)], H, T)).any()
    return len(reps)


def main():
    cert = json.loads(CERT.read_text(encoding="utf-8"))
    parts = []
    for sh in cert["shapes"]:
        t = time.time()
        orbits = check_shape(sh)
        parts.append(f"{sh['helpers']}x{sh['targets']}:{orbits}")
        print(f"  {sh['helpers']}x{sh['targets']}: {1 << (sh['helpers'] * sh['targets'])} labeled K, "
              f"{orbits} orbit lower bounds ({time.time() - t:.0f}s)", flush=True)
    print("PASS_INDEPENDENT_ZERO_FRAME_FEEDBACK_TO_8_REGISTERS " + " ".join(parts) + " feedback_gains=0")


if __name__ == "__main__":
    main()
