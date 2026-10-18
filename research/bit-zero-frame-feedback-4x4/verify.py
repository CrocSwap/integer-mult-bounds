#!/usr/bin/env python3
"""Exact four-helper/four-target dirty-shear XOR costs with and without target feedback.

Primary checker. Registers are ordered h0..h3, y0..y3; a gate [d, s] is
register[d] ^= register[s] at unit cost. The restricted alphabet omits every
helper-destination/target-source gate; the unrestricted alphabet allows every
ordered pair of distinct registers. The required complete map is
(h, y) -> (h, y + K h) on arbitrary dirty inputs, with no extra registers.

Stages (run from the repository root):
  census  all 65,536 K exactly to ten gates in both alphabets by coset
          meet-in-the-middle; predecessor reproductions; witnesses; controls
  hard    exact resolution of the 408 K beyond ten gates
  --write regenerate CERTIFICATE.json (deterministic) after both stages

Prepared for rtyu193-rgb with Claude Code (Claude Opus 5.5). Apache-2.0.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

import numpy as np

if not __debug__:
    raise SystemExit("checks use assert; run without -O")

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
CERT = PKG / "CERTIFICATE.json"
PREDECESSOR = ROOT / "research/bit-zero-frame-feedback/CERTIFICATE.json"
# PR1557 (bbMisk) head 15e0987e5fa88d1c15699215ac0cd70b47a535a6, three helpers / four targets.
PR1557_HISTOGRAM = [1, 12, 66, 220, 495, 810, 1017, 922, 529, 24]
U64 = np.uint64
ONES = U64(0x0101010101010101)
RADIUS = 5
H4 = T4 = 4
# One gate from each orbit of S4 acting diagonally on (h_a, y_a): hh, yy, y_a<-h_a,
# y_a<-h_b, h_a<-y_a, h_a<-y_b. Orbit sizes 12+12+4+12+4+12 = 56.
GATE_ORBIT_REPS = [(0, 1), (4, 5), (4, 0), (4, 1), (0, 4), (0, 5)]


def log(*args):
    print(*args, flush=True)


def gens(H, T, restricted):
    n = H + T
    return [(d, s) for d in range(n) for s in range(n)
            if d != s and not (restricted and d < H and s >= H)]


def identity(n):
    return U64(sum(1 << (9 * i) for i in range(n)))


def left_gate(M, d, s):
    """(I + e_d e_s^T) M on row-packed matrices: row d ^= row s."""
    return M ^ (((M >> U64(8 * s)) & U64(0xFF)) << U64(8 * d))


def ball(H, T, restricted, R):
    """Exact BFS spheres 0..R as (matrices, inverses, last-gate index), each sorted by matrix."""
    G = gens(H, T, restricted)
    I = identity(H + T)
    spheres = [(np.array([I], U64), np.array([I], U64), np.array([-1], np.int16))]
    prev = np.array([], U64)
    for _ in range(R):
        cur, cur_inv, _ = spheres[-1]
        mats = np.concatenate([left_gate(cur, d, s) for d, s in G])
        # M' = E M gives M'^-1 = M^-1 E: column s ^= column d.
        invs = np.concatenate([cur_inv ^ (((cur_inv >> U64(d)) & ONES) << U64(s)) for d, s in G])
        gi = np.repeat(np.arange(len(G), dtype=np.int16), len(cur))
        mats, idx = np.unique(mats, return_index=True)
        invs, gi = invs[idx], gi[idx]
        keep = ~np.isin(mats, cur, assume_unique=True) & ~np.isin(mats, prev, assume_unique=True)
        prev = cur
        spheres.append((mats[keep], invs[keep], gi[keep]))
    return G, spheres


def coset_key(M, H, T):
    """Key of the coset {T_K M}: exact h rows, y rows reduced modulo the span of the h rows."""
    rows = [((M >> U64(8 * r)) & U64(0xFF)).astype(np.uint8) for r in range(H + T)]
    h = [r.copy() for r in rows[:H]]
    y = [r.copy() for r in rows[H:]]
    for k in range(H):
        p = h[k] & ((~h[k]) + np.uint8(1))
        if not (p != 0).all():
            raise AssertionError("dependent helper rows in an invertible matrix")
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
    """Index sum K[i,j] 2^(iH+j) of the K with V U^-1 = T_K; asserts it is a shear."""
    out = np.zeros(len(V), np.int64)
    for c in range(H):          # helper rows of V U^-1 must be identity rows
        row = np.zeros(len(V), U64)
        vrow = (V >> U64(8 * c)) & U64(0xFF)
        for e in range(H + T):
            row ^= ((vrow >> U64(e)) & U64(1)) * ((Uinv >> U64(8 * e)) & U64(0xFF))
        if not (row == U64(1 << c)).all():
            raise AssertionError("helper row changed: not a shear")
    for i in range(T):
        row = np.zeros(len(V), U64)
        vrow = (V >> U64(8 * (H + i))) & U64(0xFF)
        for e in range(H + T):
            row ^= ((vrow >> U64(e)) & U64(1)) * ((Uinv >> U64(8 * e)) & U64(0xFF))
        if not ((row >> U64(H)) == U64(1 << i)).all():
            raise AssertionError("target block is not the identity: not a shear")
        out |= (row & U64((1 << H) - 1)).astype(np.int64) << (i * H)
    return out


def census(H, T, restricted, R):
    """Exact minimum for every K up to 2R gates (2R+1 marks 'beyond'), plus sphere sizes.

    Words of length L <= 2R split into a prefix of floor(L/2) and suffix of ceil(L/2) gates,
    so pairs whose BFS depths differ by at most one in a common coset of the shear group
    suffice: with U = (prefix)^-1 and V = suffix, V = T_K U and |T_K| <= |U| + |V|.
    """
    _, sph = ball(H, T, restricted, R)
    sizes = [len(s[0]) for s in sph]
    M = np.concatenate([s[0] for s in sph]); Minv = np.concatenate([s[1] for s in sph])
    dist = np.concatenate([np.full(len(s[0]), r, np.int16) for r, s in enumerate(sph)])
    del sph
    key = coset_key(M, H, T)
    order = np.argsort(key, kind="stable")
    key, M, Minv, dist = key[order], M[order], Minv[order], dist[order]
    starts = np.flatnonzero(np.r_[True, key[1:] != key[:-1]])
    counts = np.diff(np.r_[starts, len(key)])
    label = shear_label(M, Minv[np.repeat(starts, counts)], H, T)   # element = T_label * anchor
    del key, M, Minv
    reach = np.zeros((2 * R + 1, 1 << (H * T)), bool)
    for m in np.unique(counts):
        idx = starts[counts == m][:, None] + np.arange(m)[None, :]
        L, D = label[idx], dist[idx]
        for a in range(m):
            ok = np.abs(D[:, a:a + 1] - D[:, a:]) <= 1
            reach[(D[:, a:a + 1] + D[:, a:])[ok], (L[:, a:a + 1] ^ L[:, a:])[ok]] = True
    cost = np.where(reach.any(0), reach.argmax(0), 2 * R + 1).astype(np.int16)
    return cost, sizes


def histogram(cost, horizon):
    return np.bincount(cost[cost <= horizon], minlength=horizon + 1).tolist()


def k_matrix(k, H=H4, T=T4):
    return [[(k >> (i * H + j)) & 1 for j in range(H)] for i in range(T)]


def shear(K, X, H=H4, T=T4):
    Y = X.copy()
    for i in range(T):
        for j in range(H):
            if K[i][j]:
                Y ^= ((X >> U64(8 * j)) & U64(0xFF)) << U64(8 * (H + i))
    return Y


def member(sorted_arr, q):
    pos = np.searchsorted(sorted_arr, q)
    pos[pos == len(sorted_arr)] = 0
    return sorted_arr[pos] == q


def canonical_all(H=H4, T=T4):
    """For every K, the minimum index over its row (target) and column (helper) permutations."""
    ks = np.arange(1 << (H * T), dtype=np.int64)
    best = ks.copy()
    for p in itertools.permutations(range(T)):
        for q in itertools.permutations(range(H)):
            img = np.zeros_like(ks)
            for i in range(T):
                for j in range(H):
                    img |= ((ks >> (p[i] * H + q[j])) & 1) << (i * H + j)
            best = np.minimum(best, img)
    return best


def word_of(M, r, G, sph):
    word = []
    while r > 0:
        arr, _, gi = sph[r]
        pos = int(np.searchsorted(arr, M))
        if arr[pos] != M:
            raise AssertionError("parent walk left the ball")
        d, s = G[gi[pos]]
        word.append([d, s])
        M = left_gate(np.array([M], U64), d, s)[0]
        r -= 1
    return word[::-1]          # chronological order


def find_word(k, length, G, sph):
    """A word of exactly `length` gates for T_K from the ball, or None. T_K = V X^-1."""
    K = k_matrix(k)
    R = len(sph) - 1
    for a in range(max(0, length - R), min(length, R) + 1):
        X = sph[a][0]
        V = shear(K, X)
        hit = np.flatnonzero(member(sph[length - a][0], V))
        if len(hit):
            wx = word_of(X[hit[0]], a, G, sph)
            return wx[::-1] + word_of(V[hit[0]], length - a, G, sph)
    return None


def replay_ok(word, k, restricted, H=H4, T=T4):
    """Complete boundary on all 2^(H+T) dirty inputs; alphabet and index checks."""
    K = k_matrix(k, H, T)
    n = H + T
    for g in word:
        if (len(g) != 2 or any(type(v) is not int for v in g) or not all(0 <= v < n for v in g)
                or g[0] == g[1] or (restricted and g[0] < H and g[1] >= H)):
            return False
    x = np.arange(1 << n)
    regs = [(x >> r) & 1 for r in range(n)]
    want = [regs[r].copy() for r in range(n)]
    for i in range(T):
        for j in range(H):
            if K[i][j]:
                want[H + i] ^= regs[j]
    regs = [r.copy() for r in regs]
    for d, s in word:
        regs[d] ^= regs[s]
    return all((regs[r] == want[r]).all() for r in range(n))


def costs_digest(cost):
    return hashlib.sha256(np.asarray(cost, np.uint8).tobytes()).hexdigest()


def stage_census(cert=None):
    out = {}
    t = time.time()
    # Positive controls: reproduce both predecessor censuses in both alphabets.
    pred = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    p33 = next(d for d in pred["dimensions"] if d["helpers"] == 3 and d["targets"] == 3)
    want33 = [p33["minimum_histogram"][str(c)] for c in range(len(p33["minimum_histogram"]))]
    for restricted in (True, False):
        c33, _ = census(3, 3, restricted, 4)
        assert histogram(c33, 8)[:len(want33)] == want33 and (c33 <= 7).all(), "PR1306 3x3 not reproduced"
        c34, _ = census(3, 4, restricted, 5)
        assert histogram(c34, 10)[:10] == PR1557_HISTOGRAM and (c34 <= 9).all(), "PR1557 3x4 not reproduced"
    log(f"  predecessor 3x3 (PR1306) and 3x4 (PR1557) histograms reproduced in both alphabets ({time.time()-t:.0f}s)")
    # Insufficient-radius control: radius 4 leaves K unresolved; nothing beyond 8 may be claimed.
    c4, _ = census(H4, T4, True, 4)
    assert int((c4 > 8).sum()) > 0, "radius-4 control should leave unresolved K"
    costs = {}
    for name, restricted in (("restricted", True), ("unrestricted", False)):
        t = time.time()
        costs[name], out[name + "_spheres"] = census(H4, T4, restricted, RADIUS)
        log(f"  {name}: spheres {out[name + '_spheres']} ({time.time()-t:.0f}s)")
    res, unr = costs["restricted"], costs["unrestricted"]
    horizon = 2 * RADIUS
    assert np.array_equal(res, unr), "feedback changed a cost within ten gates"
    assert np.array_equal(c4 > 8, res > 8) and (res[c4 <= 8] == c4[c4 <= 8]).all(), "radius 4/5 disagree"
    beyond = np.flatnonzero(res > horizon)
    out["histogram_to_10"] = histogram(res, horizon)
    out["beyond_10"] = beyond.tolist()
    # Symmetry: costs are invariant under helper and target permutations.
    canon = canonical_all()
    reps, mult = np.unique(canon, return_counts=True)
    assert all((res[canon == r] == res[r]).all() for r in reps), "cost not permutation invariant"
    out["orbits"] = len(reps)
    log(f"  4x4 equal in both alphabets for all K within {horizon} gates; {len(beyond)} K beyond; {len(reps)} orbits")
    return out, res, canon, reps, mult


def stage_hard():
    """Resolve K beyond ten gates: restricted exact via sphere 6; unrestricted J-I via S4 normalization."""
    out = {}
    t = time.time()
    G, sph = ball(H4, T4, True, 6)
    B5 = np.sort(np.concatenate([s[0] for s in sph[:6]]))
    S6 = sph[6][0]
    B6 = np.sort(np.concatenate([B5, S6]))
    jmi = sum(1 << (i * 4 + j) for i in range(4) for j in range(4) if i != j)
    out["J_minus_I"] = jmi
    K = k_matrix(jmi)
    # T_K = V X^-1 with X in sphere 6: V in B5 gives <= 11 gates, V in B6 gives <= 12 (<= 10 is the census).
    out["restricted_J_minus_I_words"] = {"le11": int(member(B5, shear(K, S6)).sum()),
                                         "le12": int(member(B6, shear(K, S6)).sum())}
    log(f"  restricted J-I: words<=11 {out['restricted_J_minus_I_words']['le11']}, "
        f"<=12 {out['restricted_J_minus_I_words']['le12']} ({time.time()-t:.0f}s)")
    del B6, S6
    t = time.time()
    _, usph = ball(H4, T4, False, RADIUS)
    U5 = np.sort(np.concatenate([s[0] for s in usph])); del usph
    K = k_matrix(jmi)
    hits = []
    for d, s in GATE_ORBIT_REPS:
        hits.append(int(member(U5, shear(K, left_gate(U5, d, s))).sum()))
    out["unrestricted_J_minus_I_le11_hits_by_first_gate_orbit"] = hits
    # Positive control: the same machinery finds 11-gate words for a known cost-11 K.
    w11 = sum(1 << (i * 4 + j) for i, row in enumerate([[0,1,1,1],[1,0,1,1],[1,1,1,0],[1,1,0,0]])
              for j, v in enumerate(row) if v)
    out["control_cost11_hits_first_gate_hh"] = int(member(U5, shear(k_matrix(w11), left_gate(U5, 0, 1))).sum())
    assert out["control_cost11_hits_first_gate_hh"] > 0
    log(f"  unrestricted J-I words<=11 by first-gate orbit: {hits} ({time.time()-t:.0f}s)")
    return out, G, sph


def check_orbits(entries, cost):
    """Each orbit entry: attaining restricted word, replayed on all dirty inputs, length = minimum."""
    for e in entries:
        k, w = e["k"], e["restricted_witness"]
        if not (e["minimum"] == int(cost[k]) == len(w) and replay_ok(w, k, True)):
            return False
    return True


def assert_hard(h):
    assert sum(h["unrestricted_J_minus_I_le11_hits_by_first_gate_orbit"]) == 0, "feedback word <= 11 for J-I"
    assert h["restricted_J_minus_I_words"]["le11"] == 0 < h["restricted_J_minus_I_words"]["le12"]
    assert h["control_cost11_hits_first_gate_hh"] > 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stage", choices=("census", "hard", "all"), default="all")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--shape", nargs=2, type=int, metavar=("H", "T"),
                    help="exploratory, unregistered: compare both alphabets' census for another shape")
    args = ap.parse_args()
    if args.shape:
        H, T = args.shape
        if not (1 <= H and 1 <= T and H + T <= 8):
            ap.error("--shape needs H, T >= 1 and H + T <= 8")
        R = 4 if H + T <= 6 else 5
        res, _ = census(H, T, True, R)
        unr, _ = census(H, T, False, R)
        print(f"SHAPE {H}x{T} elementwise_equal={np.array_equal(res, unr)} unresolved={int((res > 2 * R).sum())} "
              f"histogram={histogram(res, 2 * R)} (exploratory; no witnesses or independent check)")
        return
    if args.write and args.stage != "all":
        ap.error("--write regenerates every field; use --stage all")
    cert = None if args.write else json.loads(CERT.read_text(encoding="utf-8"))
    hard = None
    if args.stage in ("hard", "all"):
        hard, G, sph = stage_hard()
        assert_hard(hard)
        if cert is not None:
            assert hard == cert["hard"], "hard-stage receipt differs from certificate"
        if args.stage == "hard":
            print("PASS_ZERO_FRAME_FEEDBACK_4X4_HARD jmi_minimum=12 jmi_words_le11=0 both_alphabets no_new_kappa")
            return
    else:
        hard = cert["hard"]               # established by the separate hard stage command
        assert_hard(hard)
        G, sph = ball(H4, T4, True, 6)
    result, res, canon, reps, mult = stage_census(cert)
    # Costs within ten gates come from the census. Beyond ten: both alphabets exceed ten gates;
    # an attaining 11-gate restricted word is replayed below, except on the J-I orbit, where no
    # word of <= 11 gates exists in either alphabet (hard stage) and a 12-gate word is replayed.
    cost = res.copy()
    jmi = hard["J_minus_I"]
    jorbit = canon == canon[jmi]
    for k in result["beyond_10"]:
        cost[k] = 12 if jorbit[k] else 11
    orbits = []
    for r, m in zip(reps.tolist(), mult.tolist()):
        w = find_word(r, int(cost[r]), G, sph)
        assert w is not None, f"no attaining restricted word for K={r}"
        orbits.append({"k": r, "orbit_size": m, "minimum": int(cost[r]), "restricted_witness": w})
    assert check_orbits(orbits, cost)
    hist = np.bincount(cost).tolist()
    assert sum(hist) == 1 << 16 and sum(o["orbit_size"] for o in orbits) == 1 << 16
    # Negative controls on the witness rules.
    e = orbits[-1]
    w = e["restricted_witness"]
    pair = [[0, 4], [0, 4]] + w            # cancelling feedback pair: valid only without H1
    assert replay_ok(pair, e["k"], False) and not replay_ok(pair, e["k"], True), "feedback control"
    assert not replay_ok(w[:-1], e["k"], True), "truncated witness accepted"
    assert not replay_ok(w, e["k"] ^ 1, True), "wrong target map accepted"
    assert not replay_ok([[0, 0]] + w, e["k"], False), "self-XOR accepted"
    assert not replay_ok([[True, 1], [True, 1]] + w, e["k"], True), "Boolean index accepted"
    longer = [dict(o) for o in orbits]
    longer[1] = dict(longer[1], restricted_witness=longer[1]["restricted_witness"] + [[4, 5], [4, 5]])
    assert replay_ok(longer[1]["restricted_witness"], longer[1]["k"], True)
    assert not check_orbits(longer, cost), "valid longer word accepted as optimal"
    tampered = cost.copy(); tampered[orbits[5]["k"]] -= 1
    assert not check_orbits(orbits, tampered), "tampered minimum accepted"
    controls = ["predecessor_3x3_reproduced", "pr1557_3x4_reproduced", "radius4_unresolved",
                "feedback_rejected_in_restricted_alphabet", "truncated_witness", "wrong_target_map",
                "self_xor", "boolean_index", "longer_word_mislabeled_optimal", "tampered_minimum",
                "cost11_positive_search_control"]
    body = {
        "schema_version": 1,
        "kind": "finite-exact-shortest-circuit-certificate",
        "helpers": H4, "targets": T4, "gate_cost": 1, "ancillas": 0, "all_inputs_arbitrary": True,
        "gate_convention": "[d, s] means register[d] ^= register[s]; h0..h3 are 0..3, y0..y3 are 4..7",
        "k_index": "K[i][j] (target i, helper j) is bit 4*i + j",
        "minimum_histogram": {str(c): n for c, n in enumerate(hist)},
        "feedback_gains": 0,
        "costs_sha256": costs_digest(cost),
        "costs_hex": "".join("%x" % c for c in cost.tolist()),
        "census_radius": RADIUS,
        "restricted_spheres": result["restricted_spheres"],
        "unrestricted_spheres": result["unrestricted_spheres"],
        "hard": hard,
        "orbit_count": len(orbits),
        "orbits": orbits,
        "controls": controls,
    }
    if args.write:
        CERT.write_text(json.dumps(body, indent=1) + "\n", encoding="utf-8", newline="\n")
        print("WROTE", CERT.relative_to(ROOT).as_posix())
        return
    for key in set(body) | set(cert):
        assert body.get(key) == cert.get(key), f"certificate field differs: {key}"
    print(f"PASS_ZERO_FRAME_FEEDBACK_4X4 maps={1 << 16} orbits={len(orbits)} max_minimum={len(hist) - 1} "
          f"feedback_gains=0 controls={len(controls)} no_new_kappa")


if __name__ == "__main__":
    sys.exit(main())
