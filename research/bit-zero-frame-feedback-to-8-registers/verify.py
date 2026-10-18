#!/usr/bin/env python3
"""Close every dirty-shear shape with at most eight registers: no target-feedback saving.

Primary checker (PR1306 model and alphabets). Registers h0..h(H-1), y0..y(T-1); a gate
[d, s] is register[d] ^= register[s] at unit cost; restricted = no helper-destination /
target-source gate. The required map is (h, y) -> (h, y + K h) on arbitrary dirty inputs.

Stages (repository root):
  census    2x4, 2x5, 2x6, 3x5 exactly in both alphabets (coset meet-in-the-middle of
            PR1706), attaining restricted witness per orbit on all dirty inputs
  controls  uniform H=1 / T=1 lemma against exhaustive censuses, M -> M^-T duality
            elementwise (2x5 vs 5x2), PR1306 3x3 reproduction, negative witness controls
  --write   regenerate CERTIFICATE.json (deterministic; runs both stages)

Prepared for rtyu193-rgb with Claude Code (Claude Opus 5.5). Apache-2.0.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

import numpy as np

if not __debug__:
    raise SystemExit("checks use assert; run without -O")

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
CERT = PKG / "CERTIFICATE.json"
PR1306 = ROOT / "research/bit-zero-frame-feedback/CERTIFICATE.json"
SHAPES = [(2, 4), (2, 5), (2, 6), (3, 5)]
LEMMA_SHAPES = [(1, 4), (1, 5), (1, 6), (4, 1), (5, 1), (6, 1)]
U64 = np.uint64
ONES = U64(0x0101010101010101)


def log(*a):
    print(*a, flush=True)


def radius(H, T):
    return 4 if H + T <= 6 else 5


def gens(H, T, restricted):
    n = H + T
    return [(d, s) for d in range(n) for s in range(n) if d != s and not (restricted and d < H and s >= H)]


def identity(n):
    return U64(sum(1 << (9 * i) for i in range(n)))


def left_gate(M, d, s):
    return M ^ (((M >> U64(8 * s)) & U64(0xFF)) << U64(8 * d))


def ball(H, T, restricted, R):
    """Exact BFS spheres as (matrices, inverses, last-gate index), each sorted by matrix."""
    G = gens(H, T, restricted)
    I = identity(H + T)
    sph = [(np.array([I], U64), np.array([I], U64), np.array([-1], np.int16))]
    prev = np.array([], U64)
    for _ in range(R):
        cur, inv, _ = sph[-1]
        mats = np.concatenate([left_gate(cur, d, s) for d, s in G])
        invs = np.concatenate([inv ^ (((inv >> U64(d)) & ONES) << U64(s)) for d, s in G])
        gi = np.repeat(np.arange(len(G), dtype=np.int16), len(cur))
        mats, idx = np.unique(mats, return_index=True)
        invs, gi = invs[idx], gi[idx]
        keep = ~np.isin(mats, cur, assume_unique=True) & ~np.isin(mats, prev, assume_unique=True)
        prev = cur
        sph.append((mats[keep], invs[keep], gi[keep]))
    return G, sph


def coset_key(M, H, T):
    rows = [((M >> U64(8 * r)) & U64(0xFF)).astype(np.uint8) for r in range(H + T)]
    h = [r.copy() for r in rows[:H]]
    y = [r.copy() for r in rows[H:]]
    for k in range(H):
        p = h[k] & ((~h[k]) + np.uint8(1))
        assert (p != 0).all(), "dependent helper rows"
        for j in range(H):
            if j != k:
                h[j] ^= np.where((h[j] & p) != 0, h[k], np.uint8(0))
        for i in range(T):
            y[i] ^= np.where((y[i] & p) != 0, h[k], np.uint8(0))
    key = np.zeros(len(M), U64)
    for r in range(H):
        key |= rows[r].astype(U64) << U64(8 * r)
    for i in range(T):
        key |= y[i].astype(U64) << U64(8 * (H + i))
    return key


def shear_label(V, Uinv, H, T):
    out = np.zeros(len(V), np.int64)
    for c in range(H + T):
        row = np.zeros(len(V), U64)
        vrow = (V >> U64(8 * c)) & U64(0xFF)
        for e in range(H + T):
            row ^= ((vrow >> U64(e)) & U64(1)) * ((Uinv >> U64(8 * e)) & U64(0xFF))
        if c < H:
            assert (row == U64(1 << c)).all(), "helper row changed"
        else:
            assert ((row >> U64(H)) == U64(1 << (c - H))).all(), "target block not identity"
            out |= (row & U64((1 << H) - 1)).astype(np.int64) << ((c - H) * H)
    return out


def census(H, T, restricted, R):
    """Exact minimum for every K up to 2R gates (2R+1 = beyond); proof as in PR1706."""
    _, sph = ball(H, T, restricted, R)
    sizes = [len(s[0]) for s in sph]
    M = np.concatenate([s[0] for s in sph]); Minv = np.concatenate([s[1] for s in sph])
    dist = np.concatenate([np.full(len(s[0]), r, np.int16) for r, s in enumerate(sph)])
    key = coset_key(M, H, T)
    order = np.argsort(key, kind="stable")
    key, M, Minv, dist = key[order], M[order], Minv[order], dist[order]
    starts = np.flatnonzero(np.r_[True, key[1:] != key[:-1]])
    counts = np.diff(np.r_[starts, len(key)])
    label = shear_label(M, Minv[np.repeat(starts, counts)], H, T)
    reach = np.zeros((2 * R + 1, 1 << (H * T)), bool)
    for m in np.unique(counts):
        idx = starts[counts == m][:, None] + np.arange(m)[None, :]
        L, D = label[idx], dist[idx]
        for a in range(m):
            ok = np.abs(D[:, a:a + 1] - D[:, a:]) <= 1
            reach[(D[:, a:a + 1] + D[:, a:])[ok], (L[:, a:a + 1] ^ L[:, a:])[ok]] = True
    return np.where(reach.any(0), reach.argmax(0), 2 * R + 1).astype(np.int16), sizes


def perm_images(H, T):
    """For every (row perm p, column perm q): index map K -> K' with K'[i][j] = K[p[i]][q[j]]."""
    ks = np.arange(1 << (H * T), dtype=np.int64)
    for p in itertools.permutations(range(T)):
        for q in itertools.permutations(range(H)):
            img = np.zeros_like(ks)
            for i in range(T):
                for j in range(H):
                    img |= ((ks >> (p[i] * H + q[j])) & 1) << (i * H + j)
            yield img


def canonical(H, T):
    best = np.arange(1 << (H * T), dtype=np.int64)
    for img in perm_images(H, T):
        best = np.minimum(best, img)
    return best


def transpose_index(H, T):
    ks = np.arange(1 << (H * T), dtype=np.int64)
    out = np.zeros_like(ks)
    for i in range(T):
        for j in range(H):            # K is T x H; K^T is H x T with entry (j, i) at bit j*T + i
            out |= ((ks >> (i * H + j)) & 1) << (j * T + i)
    return out


def word_of(M, r, G, sph):
    word = []
    while r > 0:
        arr, _, gi = sph[r]
        pos = int(np.searchsorted(arr, M))
        assert arr[pos] == M, "parent walk left the ball"
        d, s = G[gi[pos]]
        word.append([d, s])
        M = left_gate(np.array([M], U64), d, s)[0]
        r -= 1
    return word[::-1]


def shear(k, X, H, T):
    Y = X.copy()
    for i in range(T):
        for j in range(H):
            if (k >> (i * H + j)) & 1:
                Y ^= ((X >> U64(8 * j)) & U64(0xFF)) << U64(8 * (H + i))
    return Y


def find_word(k, length, H, T, G, sph):
    R = len(sph) - 1
    for a in range(max(0, length - R), min(length, R) + 1):
        X = sph[a][0]
        V = shear(k, X, H, T)
        arr = sph[length - a][0]
        pos = np.minimum(np.searchsorted(arr, V), len(arr) - 1)
        hit = np.flatnonzero(arr[pos] == V)
        if len(hit):
            return word_of(X[hit[0]], a, G, sph)[::-1] + word_of(V[hit[0]], length - a, G, sph)
    return None


def replay_ok(word, k, H, T, restricted):
    n = H + T
    for g in word:
        if (len(g) != 2 or any(type(v) is not int for v in g) or not all(0 <= v < n for v in g)
                or g[0] == g[1] or (restricted and g[0] < H and g[1] >= H)):
            return False
    x = np.arange(1 << n)
    regs = [(x >> r) & 1 for r in range(n)]
    want = [r.copy() for r in regs]
    for i in range(T):
        for j in range(H):
            if (k >> (i * H + j)) & 1:
                want[H + i] = want[H + i] ^ regs[j]
    regs = [r.copy() for r in regs]
    for d, s in word:
        regs[d] = regs[d] ^ regs[s]
    return all((a == b).all() for a, b in zip(regs, want))


def certify(H, T):
    R = radius(H, T)
    res, rs = census(H, T, True, R)
    unr, us = census(H, T, False, R)
    assert np.array_equal(res, unr), f"{H}x{T}: feedback changes a minimum"
    assert (res <= 2 * R).all(), f"{H}x{T}: unresolved K beyond {2 * R} gates"
    canon = canonical(H, T)
    for img in perm_images(H, T):
        assert np.array_equal(res[img], res), f"{H}x{T}: cost not permutation invariant"
    reps, mult = np.unique(canon, return_counts=True)
    G, sph = ball(H, T, True, R)
    orbits = []
    for r, m in zip(reps.tolist(), mult.tolist()):
        w = find_word(r, int(res[r]), H, T, G, sph)
        assert w is not None and len(w) == res[r] and replay_ok(w, r, H, T, True), f"{H}x{T}: witness {r}"
        orbits.append({"k": r, "orbit_size": m, "minimum": int(res[r]), "restricted_witness": w})
    hist = np.bincount(res).tolist()
    log(f"  {H}x{T}: {1 << (H * T)} K, {len(orbits)} orbits, histogram {hist}")
    return dict(helpers=H, targets=T, census_radius=R, restricted_spheres=rs, unrestricted_spheres=us,
                minimum_histogram={str(c): v for c, v in enumerate(hist)}, max_minimum=len(hist) - 1,
                costs_sha256=hashlib.sha256(res.astype(np.uint8).tobytes()).hexdigest(),
                costs_hex="".join("%x" % c for c in res.tolist()), orbit_count=len(orbits), orbits=orbits)


def controls():
    out = {}
    # Uniform lemma: H = 1 or T = 1 -> minimum = weight of K in both alphabets.
    for H, T in LEMMA_SHAPES:
        R = radius(H, T)
        w = np.array([bin(k).count("1") for k in range(1 << (H * T))])
        for restricted in (True, False):
            c, _ = census(H, T, restricted, R)
            assert np.array_equal(c, w), f"lemma fails at {H}x{T}"
    out["lemma_checked_shapes"] = [f"{H}x{T}" for H, T in LEMMA_SHAPES]
    # Duality: cost_{HxT}(K) = cost_{TxH}(K^T), elementwise, both alphabets.
    for restricted in (True, False):
        a, _ = census(2, 5, restricted, 5)
        b, _ = census(5, 2, restricted, 5)
        assert np.array_equal(a, b[transpose_index(2, 5)]), "duality fails"
    out["duality_checked"] = "2x5 vs 5x2, both alphabets, all 1024 K"
    # PR1306 3x3 reproduction (pinned input).
    pred = json.loads(PR1306.read_text(encoding="utf-8"))
    p33 = next(d for d in pred["dimensions"] if d["helpers"] == 3 and d["targets"] == 3)
    want = [p33["minimum_histogram"][str(c)] for c in range(len(p33["minimum_histogram"]))]
    for restricted in (True, False):
        c, _ = census(3, 3, restricted, 4)
        assert np.bincount(c).tolist() == want, "PR1306 3x3 not reproduced"
    out["pr1306_3x3_reproduced"] = want
    # Insufficient radius must leave 3x5 unresolved.
    c, _ = census(3, 5, True, 4)
    assert (c > 8).any()
    out["radius4_leaves_3x5_unresolved"] = int((c > 8).sum())
    # Witness-rule controls on a 2x4 word.
    H, T = 2, 4
    G, sph = ball(H, T, True, 4)
    k = (1 << (H * T)) - 1
    w = find_word(k, 6, H, T, G, sph)
    assert w is not None and replay_ok(w, k, H, T, True)
    assert not replay_ok(w[:-1], k, H, T, True), "truncated"
    assert not replay_ok(w, k ^ 1, H, T, True), "wrong map"
    pair = [[0, 2], [0, 2]] + w
    assert replay_ok(pair, k, H, T, False) and not replay_ok(pair, k, H, T, True), "feedback pair"
    assert not replay_ok([[0, 0]] + w, k, H, T, False), "self XOR"
    assert not replay_ok([[True, 1], [True, 1]] + w, k, H, T, True), "Boolean index"
    out["witness_controls"] = ["truncated", "wrong_map", "feedback_pair_restricted_only", "self_xor", "boolean_index"]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stage", choices=("census", "controls"), default=None)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    cert = None if args.write else json.loads(CERT.read_text(encoding="utf-8"))
    body = {}
    if args.write or args.stage == "census":
        body["shapes"] = [certify(H, T) for H, T in SHAPES]
    if args.write or args.stage == "controls":
        body["controls"] = controls()
    if args.write:
        body = {"schema_version": 1, "kind": "finite-exact-shortest-circuit-certificate", "gate_cost": 1,
                "ancillas": 0, "all_inputs_arbitrary": True, "feedback_gains": 0,
                "gate_convention": "[d, s] means register[d] ^= register[s]; helpers 0..H-1, targets H..H+T-1",
                "k_index": "K[i][j] (target i, helper j) is bit i*H + j", **body}
        CERT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8", newline="\n")
        print("WROTE", CERT.relative_to(ROOT).as_posix())
        return
    for key, value in body.items():
        assert value == cert[key], f"certificate field differs: {key}"
    if args.stage == "census":
        print("PASS_ZERO_FRAME_FEEDBACK_TO_8_REGISTERS shapes=2x4,2x5,2x6,3x5 feedback_gains=0 no_new_kappa")
    else:
        print("PASS_ZERO_FRAME_FEEDBACK_TO_8_REGISTERS_CONTROLS lemma=H1/T1 duality=2x5/5x2 pr1306=3x3")


if __name__ == "__main__":
    main()
