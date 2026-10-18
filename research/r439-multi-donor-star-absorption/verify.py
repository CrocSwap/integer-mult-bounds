#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Prepared by Aaron Wang, with help from opencode.
"""Complete multi-donor, multi-writer helper-star absorption linear system and star-leaf-injection gain-0 chaining census under fixed frames.

On the three pinned R439 helper-star words:
  - pr967:  research/r439-helper-stars-seed19/candidate.json.gz (11,783 ADDs, 221 star edges, 157 centres)
  - pr1062: research/r439-bsection-stars-seed01/candidate.json.gz (11,500 ADDs, 236 star edges, 162 centres)
  - pr1122: research/r439-abc-semantic-bridge/inputs/candidate.json.gz (10,652 ADDs, 236 star edges, 162 centres)

For every star centre a and every pre-first-read A write cluster W(a) (1 <= |W(a)| <= 5), this script:
  1. Verifies exact SHA-256 pins of all consumed inputs from SOURCES.json (when present at root).
  2. Constructs the complete frame-legal donor pools P_path(a) (preserving all 661 register frame paths)
     and P_mono(a) (all monotone-climb-legal donors under fixed gate frames) across all writes i in W(a).
  3. Places each donor pool in reduced row echelon form (RREF) over F_2^{661}:
     - For every unsolvable single-leaf target e_b and every two-leaf target e_{b1} + e_{b2}, constructs
       an explicit canonical dual hyperplane functional u in F_2^{661} and verifies <u, target> = 1 mod 2
       and <u, val_i[r]> = 0 mod 2 for every (i, r) in the pool.
     - For the 5 solvable single-leaf edges (506^=374, 507^=355, 514^=367, 264^=536, 326^=530), exhausts
       their complete affine solution spaces A(a, b) = c0 + ker(M_a) to certify the exact minimum net ADD
       delta (-1 for the three PR1868 single-writer edges; 0 for 264^=536 and 326^=530).
  4. Tests cross-centre chaining by adjoining all leaf basis vectors {e_{b'} : (a', b') in E} of any unread
     star centre a' in P_mono(a), proving 0 additional solvable edges or two-leaf subsets on all three words.
     Only these original star-leaf vectors are adjoined: intermediate defect vectors of in-flight multi-write
     corrections at other centres (twist plus partial donor-toggle sums, generally different vectors) are
     not modelled.
  5. Reconstructs and checks the composed 3-edge (-3 ADDs) and 5-edge (3 gain-1 + 2 gain-0, -3 ADDs) words
     on all 661 formal columns in both forward and reverse directions through the literal COPY/ERASE stream,
     verifies H2-tw / H4-tw / K-tw, runs the unchanged xcheck_p.py owner checker, and computes exact F/B
     precision envelopes and paid profiles.
  6. Runs 9 negative/boundary controls and 1 positive valid-dual check. All checks use explicit ValueError guards so -O never weakens them.
"""
import argparse
import copy
import gzip
import hashlib
import importlib.util
import itertools
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

WORD_PATHS = {
    "pr967": "research/r439-helper-stars-seed19/candidate.json.gz",
    "pr1062": "research/r439-bsection-stars-seed01/candidate.json.gz",
    "pr1122": "research/r439-abc-semantic-bridge/inputs/candidate.json.gz",
}
CHECKER_PATH = "research/e8-bit-p111-tuned/code/xcheck_p.py"
EXPECTED_PROFILE = {1: 1323, 2: 1342, 3: 79, 4: 44, 5: 102, 6: 11, 7: 19}
EXPECTED_MASS = 5129


def need(cond, msg):
    if not cond:
        raise ValueError(msg)


def verify_input_pins(root):
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    need(sources.get("schema_version") == 1, "SOURCES.json schema_version")
    checked = 0
    for entry in sources.get("files", []):
        if entry.get("usage") != "input":
            continue
        p = root / entry["path"]
        need(p.is_file(), f"missing pinned input: {entry['path']}")
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        need(digest == entry["sha256"], f"sha256 mismatch for {entry['path']}: {digest} != {entry['sha256']}")
        checked += 1
    need(checked == 5, f"expected 5 pinned inputs, found {checked}")
    return checked


def load_word(root, rel_path):
    raw = (root / rel_path).read_bytes()
    return json.loads(gzip.decompress(raw).decode("utf-8"))


def stream(w):
    out = [("add", d, s) for sec in ("D", "A") for _, d, ss in w[sec] for s in ss]
    tmp = 2 * w["v"] + w["R"]
    for j, centre in enumerate(w["ret"]):
        out.append(("copy", tmp, centre))
        out += [("add", w["v"] + i, tmp) for i, ss in enumerate(w["scatter"]) if j in ss]
        out.append(("erase", tmp, centre))
    out += [("add", d, s) for sec in ("B", "C") for _, d, ss in w[sec] for s in ss]
    return out


def flip(kind):
    return {"copy": "erase", "erase": "copy"}.get(kind, kind)


def literal_bitrows(w, reverse=False):
    n = 2 * w["v"] + w["R"]
    rows = [1 << i for i in range(n)] + [0]
    ins = stream(w)
    for kind, d, s in (reversed(ins) if reverse else ins):
        kind = flip(kind) if reverse else kind
        if kind == "add":
            rows[d] ^= rows[s]
        elif kind == "copy":
            need(rows[d] == 0, "copy into live temporary")
            rows[d] = rows[s]
        else:
            need(rows[d] == rows[s], "erase of modified copy")
            rows[d] = 0
    need(rows[-1] == 0, "temporary not erased")
    return rows[:-1]


def literal_bounds(w):
    peaks = []
    ins = stream(w)
    for reverse in (False, True):
        val = [1] * (2 * w["v"] + w["R"] + 1)
        peak = 1
        for kind, d, s in (reversed(ins) if reverse else ins):
            kind = flip(kind) if reverse else kind
            val[d] = val[d] + val[s] if kind == "add" else (val[s] if kind == "copy" else 0)
            if val[d] > peak:
                peak = val[d]
        peaks.append(peak)
    F, B = peaks
    local_val = 64 * (F ** 3) * (B ** 2)
    nine_val = (1 << 18) * (F ** 5) * (B ** 4)
    need(local_val < (1 << 104), "local 104-bit guard failed")
    need(nine_val < (1 << 192), "nine-stage 192-bit guard failed")
    return {
        "native_ADDs": sum(1 for k, _, _ in ins if k == "add"),
        "D_adds": sum(len(g[2]) for g in w["D"]),
        "A_adds": sum(len(g[2]) for g in w["A"]),
        "F": F,
        "B": B,
        "local_bits": local_val.bit_length(),
        "nine_stage_bits": nine_val.bit_length(),
    }


def frame_paths(w):
    fs = [frozenset(f) for f in w["frames"]]
    ps = [[f] for f in w["start"]]
    for sec in ("D", "A", "B", "C"):
        for f, d, ss in w[sec]:
            for r in (d, *ss):
                if ps[r][-1] != f:
                    need(fs[ps[r][-1]] < fs[f], f"illegal frame climb on register {r}: {ps[r][-1]} -> {f}")
                    ps[r].append(f)
    for r, f in enumerate(w["final"]):
        if ps[r][-1] != f:
            need(fs[ps[r][-1]] < fs[f], f"illegal final frame climb on register {r}: {ps[r][-1]} -> {f}")
            ps[r].append(f)
    return ps


def paid_profile_from_paths(w, ps):
    fdim = [len(set(f)) for f in w["frames"]]
    # Frame closure is checked by xcheck_p; dimension of frame k is rank of its lines.
    # For fast profile extraction after xcheck_p, use xcheck_p's fdim.
    raise NotImplementedError


def load_owner_checker(root):
    spec = importlib.util.spec_from_file_location("r439_owner_xcheck", root / CHECKER_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def owner_check(mod, w):
    W, _, fl, H, C, _ = mod.check(w)
    ps = frame_paths(w)
    prof = Counter(W.fdim[b] - W.fdim[a] for p in ps for a, b in itertools.pairwise(p))
    prof.update(t["rank"] for t in fl["totals"])
    profile = {int(k): int(prof[k]) for k in sorted(prof)}
    mass = sum(r * c for r, c in profile.items())
    return {
        "hypotheses": H,
        "conclusions": C,
        "profile": profile,
        "paid_mass": mass,
    }


def rref_and_nullspace(pool):
    """Given pool = [(i, r, in_ss, vec), ...], compute RREF basis over F_2 and nullspace basis."""
    pivots = {}  # lsb_bit -> [rref_vec, comb_mask]
    null_basis = []
    for idx_p, (_, _, _, vec) in enumerate(pool):
        x = vec
        c = 1 << idx_p
        while x:
            lsb = x & -x
            b_idx = lsb.bit_length() - 1
            if b_idx in pivots:
                x ^= pivots[b_idx][0]
                c ^= pivots[b_idx][1]
            else:
                # Eliminate b_idx from all existing pivots to maintain RREF
                for p_idx, pv in pivots.items():
                    if (pv[0] >> b_idx) & 1:
                        pv[0] ^= x
                        pv[1] ^= c
                # Also reduce x by any higher-bit pivots already in pivots
                for p_idx in sorted(pivots.keys()):
                    if p_idx > b_idx and ((x >> p_idx) & 1):
                        x ^= pivots[p_idx][0]
                        c ^= pivots[p_idx][1]
                for p_idx, pv in pivots.items():
                    if p_idx != b_idx and ((pv[0] >> b_idx) & 1):
                        pv[0] ^= x
                        pv[1] ^= c
                pivots[b_idx] = [x, c]
                break
        else:
            null_basis.append(c)
    return pivots, null_basis


def solve_or_dual(target_vec, pivots, pool):
    """Either return (True, c0_mask, None) if target_vec in span, or (False, None, dual_support_list)."""
    x = target_vec
    c0 = 0
    for p_idx, (p_vec, p_comb) in pivots.items():
        if (x >> p_idx) & 1:
            x ^= p_vec
            c0 ^= p_comb
    if x == 0:
        # Verify c0
        chk = 0
        for k in range(len(pool)):
            if (c0 >> k) & 1:
                chk ^= pool[k][3]
        need(chk == target_vec, "RREF particular solution mismatch")
        return True, c0, None
    # Construct canonical dual functional from lowest 1-bit f of residual x
    lsb = x & -x
    f_bit = lsb.bit_length() - 1
    dual_bits = [f_bit]
    for p_idx, (p_vec, _) in pivots.items():
        if (p_vec >> f_bit) & 1:
            dual_bits.append(p_idx)
    dual_bits.sort()
    dual_mask = 0
    for b in dual_bits:
        dual_mask |= (1 << b)
    # Verify <dual_mask, target_vec> == 1 and <dual_mask, v> == 0 for all v in pool
    need((dual_mask & target_vec).bit_count() & 1 == 1, "dual functional fails on target")
    for _, _, _, vec in pool:
        need((dual_mask & vec).bit_count() & 1 == 0, "dual functional not orthogonal to donor pool")
    return False, None, dual_bits


def build_mono_pool(w, a):
    """Rebuild the real monotone_all donor pool P_mono(a), exactly as analyze_single_word does.

    Returns [(i, r, r in S_i, val_i[r]), ...] over pre-first-read writes i to centre a.
    """
    v, R = w["v"], w["R"]
    n = 2 * v + R
    fs = [frozenset(f) for f in w["frames"]]
    cur = list(w["start"])
    for f, d, ss in w["D"]:
        for r in (d, *ss):
            cur[r] = f
    val = [1 << r for r in range(n)]
    a_vals_before = []
    pre_frames = []
    for f, d, ss in w["A"]:
        pre_frames.append(list(cur))
        for r in (d, *ss):
            cur[r] = f
        a_vals_before.append(list(val))
        acc = 0
        for s in ss:
            acc ^= val[s]
        val[d] ^= acc
    nxt = list(w["final"])
    next_touch = [[0] * n for _ in range(len(w["A"]))]
    for sec in ("C", "B"):
        for f, d, ss in reversed(w[sec]):
            for r in (d, *ss):
                nxt[r] = f
    for i in range(len(w["A"]) - 1, -1, -1):
        f, d, ss = w["A"][i]
        next_touch[i] = list(nxt)
        for r in (d, *ss):
            nxt[r] = f
    first_read = len(w["A"])
    for i, (_, _, ss) in enumerate(w["A"]):
        if a in ss:
            first_read = i
            break
    pool = []
    for i in range(first_read):
        f_i, d_i, ss_i = w["A"][i]
        if d_i != a:
            continue
        for r in range(n):
            if r == a or (v <= r < 2 * v):
                continue
            f_pre = pre_frames[i][r]
            f_nxt = next_touch[i][r]
            if (fs[f_pre] <= fs[f_i]) and (fs[f_i] <= fs[f_nxt]):
                pool.append((i, r, r in ss_i, a_vals_before[i][r]))
    return pool


def dual_witness_verdict(dual_bits, target_mask, pool):
    """Real dual-hyperplane predicate over a donor pool: target parity first, then
    orthogonality to every pool vector. Returns a pass summary, or raises ValueError
    at the first failed check (never unconditionally)."""
    dmask = 0
    for b in dual_bits:
        dmask |= 1 << b
    need((dmask & target_mask).bit_count() & 1 == 1, "dual fails target parity")
    for i, r, _, vec in pool:
        need((dmask & vec).bit_count() & 1 == 0, f"dual not orthogonal to donor ({i},{r})")
    return f"pass: target parity 1; orthogonal to {len(pool)} pool donors"


def verify_twisted_contract(w_parent, w_abs, omitted_edges):
    """Verify H2-tw, H4-tw (C U' diag(I_x, T) = I), K-tw (N = K' T), and full 661-column dirty boundary."""
    v, R = w_abs["v"], w_abs["R"]
    n = 2 * v + R
    want = [(1 << i) | (1 << (i - v)) if v <= i < 2 * v else (1 << i) for i in range(n)]
    for rev in (False, True):
        got = literal_bitrows(w_abs, reverse=rev)
        need(got == want, f"absorbed word fails 661-column dirty boundary (reverse={rev})")

    # Compute D boundary on w_abs: should be (x, y + N h, T h) with source-free, H1-compliant frame-0 gates
    smask = ((1 << R) - 1) << (2 * v)
    d_state = [1 << i for i in range(n)]
    for f, d, ss in w_abs["D"]:
        need(f == 0 and d >= v and all(s >= v for s in ss), "D gate shape violation")
        if d >= 2 * v:
            need(all(s >= 2 * v for s in ss), "H1 violation in D: target feeds helper")
        for s in ss:
            d_state[d] ^= d_state[s]
    for s_idx in range(v):
        need(d_state[s_idx] == (1 << s_idx), f"D modified source {s_idx}")
    for t_idx in range(v):
        n_t = d_state[v + t_idx] ^ (1 << (v + t_idx))
        need((n_t & ~smask) == 0, f"D target {t_idx} residual has non-helper bits")
    # Expected twist T on helpers: for each omitted (a, b), T(a) ^= 1 << b
    exp_h = {r: (1 << r) for r in range(2 * v, n)}
    for a, b in omitted_edges:
        exp_h[a] ^= (1 << b)
    for r in range(2 * v, n):
        need(d_state[r] == exp_h[r], f"H2-tw helper twist mismatch on {r}")

    # Raw W0 = (A, scatter, B) on w_abs
    raw = [1 << i for i in range(n)]
    for _, d, ss in w_abs["A"]:
        for s in ss:
            raw[d] ^= raw[s]
    copies = [raw[q] for q in w_abs["ret"]]
    for t_idx, row in enumerate(w_abs["scatter"]):
        for k in row:
            raw[v + t_idx] ^= copies[k]
    for _, d, ss in w_abs["B"]:
        for s in ss:
            raw[d] ^= raw[s]

    # Check K-tw: for each target t, helper part of raw[v+t] composed with T equals N_t = d_state[v+t] ^ (1 << (v+t))
    smask = ((1 << R) - 1) << (2 * v)
    for t_idx in range(v):
        n_t = d_state[v + t_idx] ^ (1 << (v + t_idx))
        kp_t = raw[v + t_idx] & smask
        kpt_composed = 0
        for h_r in range(2 * v, n):
            if (kp_t >> h_r) & 1:
                kpt_composed ^= exp_h[h_r]
        need(kpt_composed == n_t, f"K-tw failed on target {t_idx}")

    # Check H4-tw: applying C to U' diag(I_x, T) restores all z registers (sources < v and helpers >= 2*v)
    z_twisted = [1 << r if r < 2 * v else exp_h[r] for r in range(n)]
    u_prime_t = [0] * n
    for r in range(n):
        if r < v or r >= 2 * v:
            row = raw[r]
            acc = 0
            for c_idx in range(n):
                if (row >> c_idx) & 1:
                    acc ^= z_twisted[c_idx]
            u_prime_t[r] = acc
    for _, d, ss in w_abs["C"]:
        for s in ss:
            u_prime_t[d] ^= u_prime_t[s]
    for r in range(n):
        if r < v or r >= 2 * v:
            need(u_prime_t[r] == (1 << r), f"H4-tw failed on z register {r}")


def apply_absorptions(w, edits):
    """Apply a list of (a, b, writer_idx, new_ss) absorptions to a deep copy of w."""
    w2 = copy.deepcopy(w)
    for a, b, writer_idx, new_ss in edits:
        half = len(w2["D"]) // 2
        gate = [0, a, [b]]
        need(gate in w2["D"][half:], f"missing terminal D restoration {gate}")
        idx = w2["D"].index(gate, half)
        w2["D"].pop(idx)
        need(w2["A"][writer_idx][1] == a, f"writer A[{writer_idx}] does not write {a}")
        w2["A"][writer_idx][2] = list(new_ss)
    return w2


def analyze_single_word(wname, w, owner_mod):
    v, R = w["v"], w["R"]
    n = 2 * v + R
    fs = [frozenset(f) for f in w["frames"]]
    parent_paths = frame_paths(w)
    parent_bill = literal_bounds(w)
    parent_own = owner_check(owner_mod, w)
    need(parent_own["profile"] == EXPECTED_PROFILE and parent_own["paid_mass"] == EXPECTED_MASS, f"{wname} parent profile")

    cur = list(w["start"])
    for f, d, ss in w["D"]:
        for r in (d, *ss):
            cur[r] = f
    val = [1 << r for r in range(n)]
    a_vals_before = []
    pre_frames = []
    for f, d, ss in w["A"]:
        pre_frames.append(list(cur))
        for r in (d, *ss):
            cur[r] = f
        a_vals_before.append(list(val))
        acc = 0
        for s in ss:
            acc ^= val[s]
        val[d] ^= acc

    nxt = list(w["final"])
    next_touch = [[0] * n for _ in range(len(w["A"]))]
    for sec in ("C", "B"):
        for f, d, ss in reversed(w[sec]):
            for r in (d, *ss):
                nxt[r] = f
    for i in range(len(w["A"]) - 1, -1, -1):
        f, d, ss = w["A"][i]
        next_touch[i] = list(nxt)
        for r in (d, *ss):
            nxt[r] = f

    restorations = [(idx, g[1], g[2][0]) for idx, g in enumerate(w["D"]) if idx >= len(w["D"]) // 2 and g[1] >= 2 * v]
    by_center = {}
    for _, a, b in restorations:
        by_center.setdefault(a, []).append(b)

    first_read_A = {}
    for a in range(2 * v, n):
        fr = len(w["A"])
        for i, (_, _, ss) in enumerate(w["A"]):
            if a in ss:
                fr = i
                break
        first_read_A[a] = fr

    modes_out = {}
    for mode in ("same_path", "monotone_all"):
        zero_bit_edges = 0
        nonzero_unsolvable_edges = 0
        solvable_single_edges = 0
        solvable_two_leaf_pairs = 0
        chained_extra_solvable = 0
        total_pool_pairs = 0
        solvable_details = {}
        dual_witnesses = []

        # Per-edge analysis
        for _, a, b in restorations:
            writers = [i for i in range(first_read_A[a]) if w["A"][i][1] == a]
            pool = []
            for i in writers:
                f_i, _, ss_i = w["A"][i]
                for r in range(n):
                    if r == a or (v <= r < 2 * v):
                        continue
                    f_pre = pre_frames[i][r]
                    f_nxt = next_touch[i][r]
                    if mode == "monotone_all":
                        ok = (fs[f_pre] <= fs[f_i]) and (fs[f_i] <= fs[f_nxt])
                    else:
                        ok = (f_pre == f_i) or (r in ss_i) or (fs[f_pre] < fs[f_i] and f_nxt == f_i)
                    if ok:
                        pool.append((i, r, r in ss_i, a_vals_before[i][r]))
            total_pool_pairs += len(pool)
            union_bits = 0
            for _, _, _, vec in pool:
                union_bits |= vec
            pivots, null_basis = rref_and_nullspace(pool)
            in_sp, c0, dual_bits = solve_or_dual(1 << b, pivots, pool)
            if in_sp:
                solvable_single_edges += 1
                best_delta = 999
                best_count = 0
                best_witness = None
                for m_nb in range(1 << len(null_basis)):
                    sol = c0
                    for bit_i, nb in enumerate(null_basis):
                        if (m_nb >> bit_i) & 1:
                            sol ^= nb
                    used = [pool[k] for k in range(len(pool)) if (sol >> k) & 1]
                    d_a = -1 + sum(-1 if u[2] else 1 for u in used)
                    if d_a < best_delta:
                        best_delta = d_a
                        best_count = 1
                        best_witness = [[u[0], u[1], u[2]] for u in used]
                    elif d_a == best_delta:
                        best_count += 1
                solvable_details[f"{a}^={b}"] = {
                    "writers": writers,
                    "pool_size": len(pool),
                    "rank": len(pivots),
                    "null_dim": len(null_basis),
                    "affine_solutions": 1 << len(null_basis),
                    "min_net_add_delta": best_delta,
                    "min_cost_solution_count": best_count,
                    "canonical_witness": best_witness,
                }
            else:
                if not ((union_bits >> b) & 1):
                    zero_bit_edges += 1
                    need(dual_bits == [b], "zero-bit edge must have unit dual functional [b]")
                else:
                    nonzero_unsolvable_edges += 1
                    need(len(dual_bits) >= 2, "nonzero-bit unsolvable edge must have multi-bit dual functional")
                if mode == "monotone_all":
                    dual_witnesses.append({"center": a, "leaves": [b], "dual_support": dual_bits})

        # Two-leaf simultaneous omission analysis + cross-centre chaining analysis
        for a, leaves in sorted(by_center.items()):
            writers = [i for i in range(first_read_A[a]) if w["A"][i][1] == a]
            pool = []
            chained_pool = []
            for i in writers:
                f_i, _, ss_i = w["A"][i]
                for r in range(n):
                    if r == a or (v <= r < 2 * v):
                        continue
                    f_pre = pre_frames[i][r]
                    f_nxt = next_touch[i][r]
                    if mode == "monotone_all":
                        ok = (fs[f_pre] <= fs[f_i]) and (fs[f_i] <= fs[f_nxt])
                    else:
                        ok = (f_pre == f_i) or (r in ss_i) or (fs[f_pre] < fs[f_i] and f_nxt == f_i)
                    if ok:
                        pool.append((i, r, r in ss_i, a_vals_before[i][r]))
                        chained_pool.append((i, r, r in ss_i, a_vals_before[i][r]))
                        if r in by_center and i < first_read_A[r]:
                            for b_other in by_center[r]:
                                chained_pool.append((i, r, False, 1 << b_other))
            pivots, _ = rref_and_nullspace(pool)
            c_pivots, _ = rref_and_nullspace(chained_pool)
            if len(leaves) == 2:
                b1, b2 = leaves
                in_sp2, _, dual2 = solve_or_dual((1 << b1) ^ (1 << b2), pivots, pool)
                if in_sp2:
                    solvable_two_leaf_pairs += 1
                elif mode == "monotone_all":
                    dual_witnesses.append({"center": a, "leaves": [b1, b2], "dual_support": dual2})
                in_c2, _, _ = solve_or_dual((1 << b1) ^ (1 << b2), c_pivots, chained_pool)
                if in_c2:
                    chained_extra_solvable += 1
            for b in leaves:
                in_c1, _, _ = solve_or_dual(1 << b, c_pivots, chained_pool)
                if in_c1 and f"{a}^={b}" not in solvable_details:
                    chained_extra_solvable += 1

        modes_out[mode] = {
            "total_pool_pairs": total_pool_pairs,
            "zero_bit_edges": zero_bit_edges,
            "nonzero_unsolvable_edges": nonzero_unsolvable_edges,
            "solvable_single_edges": solvable_single_edges,
            "solvable_two_leaf_pairs": solvable_two_leaf_pairs,
            "chained_extra_solvable": chained_extra_solvable,
            "solvable_details": solvable_details,
        }
        if mode == "monotone_all":
            modes_out[mode]["dual_witnesses"] = dual_witnesses

    # Build and verify composed 3-edge (gain-1) and 5-edge (3 gain-1 + 2 gain-0 same_path) words
    edits_3 = [
        (506, 374, 288, [69]),
        (507, 355, 290, [72]),
        (514, 367, 304, [360]),
    ]
    edits_5 = edits_3 + [
        (264, 536, 346, [416, 536]),
        (326, 530, 334, [59, 530]),
    ]
    composed = {}
    for label, ed_list in (("composed_gain1_3", edits_3), ("composed_all_5", edits_5)):
        w_abs = apply_absorptions(w, ed_list)
        need(frame_paths(w_abs) == parent_paths, f"{wname} {label} frame paths changed")
        verify_twisted_contract(w, w_abs, [(a, b) for a, b, _, _ in ed_list])
        bill = literal_bounds(w_abs)
        own = owner_check(owner_mod, w_abs)
        need(own["profile"] == EXPECTED_PROFILE and own["paid_mass"] == EXPECTED_MASS, f"{wname} {label} paid profile")
        false_h = sorted(k for k, v_flag in own["hypotheses"].items() if not v_flag)
        false_c = sorted(k for k, v_flag in own["conclusions"].items() if not v_flag)
        need(
            false_h == ["H2_D_frame0_targets_from_helpers", "H4_C_literal_reverse_at_full"],
            f"{wname} {label} unexpected false hypotheses: {false_h}",
        )
        need(
            false_c == ["C_is_U_inverse", "K_equals_D"],
            f"{wname} {label} unexpected false conclusions: {false_c}",
        )
        composed[label] = {
            "omitted_edges": len(ed_list),
            "native_ADDs": bill["native_ADDs"],
            "net_add_delta": bill["native_ADDs"] - parent_bill["native_ADDs"],
            "D_adds": bill["D_adds"],
            "A_adds": bill["A_adds"],
            "F": bill["F"],
            "B": bill["B"],
            "local_bits": bill["local_bits"],
            "nine_stage_bits": bill["nine_stage_bits"],
            "paid_mass": own["paid_mass"],
            "same_frame_paths": True,
        }

    return {
        "edges": len(restorations),
        "centers": len(by_center),
        "one_leaf_centers": sum(1 for v_l in by_center.values() if len(v_l) == 1),
        "two_leaf_centers": sum(1 for v_l in by_center.values() if len(v_l) == 2),
        "baseline": parent_bill,
        "modes": modes_out,
        "composed_gain1_3": composed["composed_gain1_3"],
        "composed_all_5": composed["composed_all_5"],
    }


def run_controls(w1062, cert_pr1062, owner_mod):
    controls = []

    def expect_reject(name, fn):
        try:
            fn()
        except ValueError as exc:
            controls.append([name, str(exc)[:80]])
            return
        raise ValueError(f"negative control accepted: {name}")

    # 1. Omitted restoration without A edit fails 661-column dirty boundary
    w_no_a = copy.deepcopy(w1062)
    half = len(w_no_a["D"]) // 2
    w_no_a["D"].pop(w_no_a["D"].index([0, 506, [374]], half))
    expect_reject(
        "omitted_restoration_without_a_edit",
        lambda: verify_twisted_contract(w1062, w_no_a, [(506, 374)]),
    )

    # 2. Twisted A edit with rebuilt literal cleanup C fails dirty helper restoration
    w_rebuilt_c = apply_absorptions(w1062, [(506, 374, 288, [69])])
    v = w_rebuilt_c["v"]
    full_id = next(k for k, f in enumerate(w_rebuilt_c["frames"]) if len(f) == v)
    zg = [[full_id, g[1], list(g[2])] for sec in ("A", "B") for g in w_rebuilt_c[sec] if not (v <= g[1] < 2 * v)]
    w_rebuilt_c["C"] = list(reversed(zg))
    expect_reject(
        "twisted_a_with_rebuilt_literal_cleanup",
        lambda: verify_twisted_contract(w1062, w_rebuilt_c, [(506, 374)]),
    )

    # 3. PR1913 two-writer scalar witness (231^=459, +109 @ A[9], -459 @ A[527]) passes scalar boundary but fails frame climb
    w_pr1913 = copy.deepcopy(w1062)
    w_pr1913["D"].pop(w_pr1913["D"].index([0, 231, [459]], half))
    w_pr1913["A"][9][2] = sorted(set(w_pr1913["A"][9][2]) ^ {109})
    w_pr1913["A"][527][2] = sorted(set(w_pr1913["A"][527][2]) ^ {459})
    verify_twisted_contract(w1062, w_pr1913, [(231, 459)])
    expect_reject("pr1913_two_writer_frame_climb", lambda: frame_paths(w_pr1913))

    # 4. Absorption after first read of 506 (at A[1041]) fails dirty boundary
    w_late = apply_absorptions(w1062, [(506, 374, 1033, [286, 69])])
    expect_reject(
        "wrong_writer_or_donor_506",
        lambda: verify_twisted_contract(w1062, w_late, [(506, 374)]),
    )

    # 5. Wrong substitute donor at A[288] (375 instead of 69) is frame-legal but fails dirty boundary
    w_wrong_sub = apply_absorptions(w1062, [(506, 374, 288, [375])])
    need(frame_paths(w_wrong_sub) != [], "frame_paths check")
    expect_reject(
        "frame_legal_wrong_donor_at_a288",
        lambda: verify_twisted_contract(w1062, w_wrong_sub, [(506, 374)]),
    )

    # 6. Early monotone-climb-legal gain-0 move (264^=536 @ A[38]) passes monotone climbs and dirty boundary
    #    but alters frame_paths(w) and splits an H_2 climb into 2 H_1
    w_early_g0 = apply_absorptions(w1062, [(264, 536, 38, [19, 536])])
    verify_twisted_contract(w1062, w_early_g0, [(264, 536)])
    own_early = owner_check(owner_mod, w_early_g0)
    need(own_early["paid_mass"] == EXPECTED_MASS, "early gain-0 mass")
    expect_reject(
        "early_monotone_gain0_alters_frame_path_and_profile",
        lambda: need(own_early["profile"] == EXPECTED_PROFILE, "paid profile changed from H2 to 2*H1"),
    )

    # 7. Real target-parity/donor-orthogonality dual predicate over the actual P_mono(a)
    #    donor pool of the chosen witness centre: the certified valid dual passes both
    #    checks, and corrupted duals fail the same predicate at a specific check
    #    (target parity or donor orthogonality) -- never an unconditional throw.
    multi_dual = next(d for d in cert_pr1062["modes"]["monotone_all"]["dual_witnesses"] if len(d["dual_support"]) >= 2)
    valid_bits = list(multi_dual["dual_support"])
    target_mask = 0
    for b in multi_dual["leaves"]:
        target_mask |= (1 << b)
    pool = build_mono_pool(w1062, multi_dual["center"])
    controls.append(["valid_dual_hyperplane_witness", dual_witness_verdict(valid_bits, target_mask, pool)])

    def check_bad_dual():
        # Shipped corruption: drop the last support bit; fails the predicate at its
        # first failed check (target parity on the pinned witness).
        dual_witness_verdict(valid_bits[:-1], target_mask, pool)

    expect_reject("corrupted_dual_hyperplane_witness", check_bad_dual)

    # Parity-preserving corruption: add a pool-carried non-leaf bit, so the dual keeps
    # target parity 1 and must be rejected by the donor-orthogonality check itself.
    n_regs = 2 * w1062["v"] + w1062["R"]
    extra = next(
        (
            b
            for b in range(n_regs)
            if b not in valid_bits and b not in multi_dual["leaves"] and any((vec >> b) & 1 for _, _, _, vec in pool)
        ),
        None,
    )
    need(extra is not None, "no pool bit available for a parity-preserving dual corruption")

    def check_bad_dual_orthogonal():
        dual_witness_verdict(sorted(valid_bits + [extra]), target_mask, pool)

    expect_reject("corrupted_dual_orthogonality_witness", check_bad_dual_orthogonal)

    # 8. Original untwisted D spliced with absorbed A' and C fails helper restoration
    w_untwisted_d = apply_absorptions(w1062, [(506, 374, 288, [69])])
    w_untwisted_d["D"] = copy.deepcopy(w1062["D"])
    expect_reject(
        "untwisted_d_splice_with_absorbed_a",
        lambda: verify_twisted_contract(w1062, w_untwisted_d, []),
    )

    return controls


def check_certificate_matches(expected, actual):
    need(json.loads(json.dumps(expected)) == json.loads(json.dumps(actual)), "certificate mismatch against CERTIFICATE.json")


def run(root=ROOT, check_expected=True):
    pinned_inputs = verify_input_pins(root)
    owner_mod = load_owner_checker(root)
    words_loaded = {k: load_word(root, p) for k, p in WORD_PATHS.items()}
    words_rep = {k: analyze_single_word(k, w, owner_mod) for k, w in words_loaded.items()}
    controls = run_controls(words_loaded["pr1062"], words_rep["pr1062"], owner_mod)
    sources = json.loads((HERE / "SOURCES.json").read_text(encoding="utf-8"))
    report = {
        "status": "PASS_R439_MULTI_DONOR_STAR_ABSORPTION",
        "base_commit": sources["base_commit"],
        "pinned_inputs_checked": pinned_inputs,
        "words": words_rep,
        "controls": controls,
        "new_kappa_claim": False,
    }
    if check_expected:
        cert_path = HERE / "CERTIFICATE.json"
        need(cert_path.is_file(), "missing CERTIFICATE.json")
        expected = json.loads(cert_path.read_text(encoding="utf-8"))
        check_certificate_matches(expected, report)
    return report


def main():
    if not __debug__:
        # The pinned owner checker xcheck_p.py uses internal assertions; re-invoke without -O so they run.
        raise SystemExit(subprocess.call([sys.executable, "-I", "-B", __file__, *sys.argv[1:]]))
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write-certificate", action="store_true")
    args = ap.parse_args()
    rep = run(Path.cwd(), check_expected=not args.write_certificate)
    if args.write_certificate:
        (HERE / "CERTIFICATE.json").write_text(json.dumps(rep, indent=2) + "\n", encoding="utf-8", newline="\n")
    w1062 = rep["words"]["pr1062"]
    m_path = w1062["modes"]["same_path"]
    m_mono = w1062["modes"]["monotone_all"]
    print(
        "PASS_R439_MULTI_DONOR_STAR_ABSORPTION "
        f"words=3 edges=221,236,236 pr1062_pools={m_path['total_pool_pairs']}/{m_mono['total_pool_pairs']} "
        f"solvable={m_mono['solvable_single_edges']} two_leaf={m_mono['solvable_two_leaf_pairs']} "
        f"chained_extra={m_mono['chained_extra_solvable']} duals={len(m_mono['dual_witnesses'])} "
        f"ADDs={w1062['baseline']['native_ADDs']}->{w1062['composed_gain1_3']['native_ADDs']} "
        f"controls={len(rep['controls'])} no_new_kappa"
    )


if __name__ == "__main__":
    main()
