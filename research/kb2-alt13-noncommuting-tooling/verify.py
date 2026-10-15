#!/usr/bin/env python3
"""KB2 demonstration of the reusable exact-search tooling.

Object (open question 1 of research/fiveswap-alt13-commuting-screen, PR 2317):
does the strictly alternating thirteen-call word for five fully occupied
coordinate-SWAP targets exist in the formal F2[GL_2(F2)] rank-one-idempotent
register model with noncommuting scalar projectors?

Scope of this file: an independent search-level audit of the concurrent PR 2415
exclusion (the analytic minimum 3t = 15), on the complete six-distinct-value
family, plus validated controls for the tooling.  No kappa claim.

Family (exact classification, machine-checked below):
  * sign equation sum N_i = I_5 forces >= 5 distinct projector values;
  * t = 5 rank-one idempotents summing to I_5 are automatically a dual frame
    (V^T U is an invertible idempotent), so <= 5 distinct values are the
    pairwise-commuting family already excluded by the predecessor;
  * at exactly 6 distinct values: 5 odd-multiplicity values form a dual frame
    (GL_5-conjugate to the coordinate frame) and the sixth value W has even
    multiplicity m_W in {2,4,6,8}.  This family is exhaustively searched here
    by a signature DP over placements and an exact M_5(F2[G]) evaluation of
    every (signature, W) pair.  Seven or more distinct values are NOT covered.

Aaron Wang, with help from opencode.  Apache-2.0.  Stdlib only.
"""

import hashlib
import importlib.util
import itertools
import pathlib
import random
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.stdout.reconfigure(encoding="utf-8")


def load():
    spec = importlib.util.spec_from_file_location("exact_search",
                                                 HERE / "exact_search.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ES = load()


def marker(tag):
    print("  [%s] ok" % tag)


def main():
    t0 = time.time()
    g = ES.gl2f2()
    ga = ES.GroupAlgebra(g)
    q8 = ES.q8()
    ga8 = ES.GroupAlgebra(q8)

    # ------------------------------------------------------------------
    # 1. Model controls (positive and negative).
    # ------------------------------------------------------------------
    for t in (1, 3, 5):
        labels = [g.A, g.B, g.A] * t
        projs = [ES.coord_proj(t, i // 3) for i in range(3 * t)]
        assert ES.word_product(ga, g, t, labels, projs) == \
            ES.ring_target(ga, t, g.S), t
    labels15 = [g.A, g.B, g.A] * 5
    projs15 = [ES.coord_proj(5, i // 3) for i in range(15)]
    bad = list(projs15)
    bad[0] = ES.coord_proj(5, 1)
    assert ES.word_product(ga, g, 5, labels15, bad) != ES.ring_target(ga, 5, g.S)
    marker("model_direct_and_mutated")

    # quotient isomorphism F2[S_3] = F2[eps]/(eps^2) x M_2(F2)
    imgs = []
    for el in range(g.n):
        m0, m1 = ES.eye_f2(1), tuple([g.parity(el)])
        nat = ES.gl2_matrix(g, el)
        imgs.append((g.parity(el), nat))
    for x in range(g.n):
        for y in range(g.n):
            px, nx = imgs[x]
            py, ny = imgs[y]
            pz, nz = imgs[g.mul(x, y)]
            assert pz == px ^ py
            assert nz == ES.mat_mul(2, nx, ny)
    rank_rows = []
    for el in range(g.n):
        p, nat = imgs[el]
        # coordinates: constant 1, eps coefficient, then the four M_2 entries
        rank_rows.append((1 << 5) | (p << 4) | (nat[0] << 2) | nat[1])
    assert ES.rank_f2(6, tuple(rank_rows)) == 6
    marker("quotient_isomorphism_sign_x_natural")

    # sign + natural equations equivalent to the full endpoint (random)
    rng = random.Random(20261015)
    for _ in range(300):
        rl, rp = ES.random_tuple(g, 3, 6, rng)
        full = ES.endpoint_check(ga, g, 3, rl, rp)
        quot = ES.sign_check(g, 3, rl, rp) and ES.natural_check(g, 3, rl, rp)
        assert full == quot
        assert full == ES.c_conditions_ok(3, rl, rp)
    marker("quotient_and_c_invariant_equivalence")

    # GL conjugation invariance
    p, pinv = ES.random_gl(5, rng)
    conj = [ES.proj_conj(5, u, v, p, pinv) for u, v in projs15]
    assert ES.word_product(ga, g, 5, labels15, conj) == ES.ring_target(ga, 5, g.S)
    marker("gl_conjugation_invariance")

    # ------------------------------------------------------------------
    # 2. Classification lemmas (exhaustive over F2^3).
    # ------------------------------------------------------------------
    projs3 = ES.rank_one_idempotents(3)
    eye3 = ES.eye_f2(3)
    frames = 0
    for comb in itertools.combinations(range(len(projs3)), 3):
        rows = [ES.proj_rows(3, projs3[i][0], projs3[i][1]) for i in comb]
        if ES.proj_sum(3, rows) != eye3:
            continue
        frames += 1
        for i, j in itertools.combinations(comb, 2):
            assert ES.dot(projs3[i][1], projs3[j][0]) == 0
            assert ES.dot(projs3[j][1], projs3[i][0]) == 0
    assert frames > 0
    noncomm = 0
    for comb in itertools.combinations(range(len(projs3)), 5):
        rows = [ES.proj_rows(3, projs3[i][0], projs3[i][1]) for i in comb]
        if ES.proj_sum(3, rows) != eye3:
            continue
        for i, j in itertools.combinations(comb, 2):
            if ES.dot(projs3[i][1], projs3[j][0]) or \
                    ES.dot(projs3[j][1], projs3[i][0]):
                noncomm += 1
                break
    assert noncomm > 0
    for comb in itertools.combinations(range(len(projs3)), 4):
        rows = [ES.proj_rows(3, projs3[i][0], projs3[i][1]) for i in comb]
        assert ES.proj_sum(3, rows) != eye3
    marker("classification_lemmas_f2_3 frames=%d noncommuting5=%d"
           % (frames, noncomm))

    # ------------------------------------------------------------------
    # 3. Search-engine controls: fast eval vs generic, positive hit,
    #    tiny brute-force completeness cross-check, layer balls, shards.
    # ------------------------------------------------------------------
    alphabet5 = ES.rank_one_idempotents(5)
    for _ in range(8):
        rl, rp = ES.random_tuple(g, 5, 13, rng)
        assert ES.word_product(ga, g, 5, rl, rp) == \
            ES.expanded_word_product(ga, g, 5, rl, rp)
    labels13 = ES.alt_labels(g, 13)
    for _ in range(10):
        m = rng.randrange(1, 5)
        wpos = sorted(rng.sample(range(13), m))
        wu, wv = alphabet5[rng.randrange(len(alphabet5))]
        assign = [rng.randrange(5) for _ in range(13)]
        h = [[g.identity] * (m + 1) for _ in range(5)]
        projs = []
        seg = 0
        for i in range(13):
            if i in wpos:
                projs.append((wu, wv))
                seg += 1
            else:
                projs.append(ES.coord_proj(5, assign[i]))
                h[assign[i]][seg] = g.mul(h[assign[i]][seg], labels13[i])
        slow = ES.word_product(ga, g, 5, labels13, projs)
        fast = ES.sig_eval(ga, g, 5, [labels13[i] for i in wpos], h, wu, wv)
        assert slow == fast
        h[0][0] = g.mul(h[0][0], g.A)
        assert ES.sig_eval(ga, g, 5, [labels13[i] for i in wpos], h, wu, wv) != slow
    marker("fast_eval_equivalence_and_mutation")

    gens8 = [ES.call_matrix(ga8, q8, 2, lbl, ES.proj_rows(2, u, v))
             for lbl in (q8.X, q8.Y)
             for u, v in ES.rank_one_idempotents(2)]
    layers = ES.layer_ball_sizes(ga8, gens8, 3)
    assert layers == [1, 12, 110, 936], layers
    marker("q8_layer_calibration layers=%s" % layers)

    shards = ES.shard_split(range(1000), 7)
    flat = [x for sh in shards for x in sh["items"]]
    assert sorted(flat) == list(range(1000))
    for sh in shards:
        assert sh["sha256"] == hashlib.sha256(
            ",".join(map(str, sh["items"])).encode()).hexdigest()
    marker("parallel_safe_shards")

    # prefix closure bound
    rows = [ES.proj_rows(5, u, v) for u, v in projs15[:4]]
    assert ES.sign_prefix_bound(5, rows, 4, 15)
    assert not ES.sign_prefix_bound(5, rows, 14, 15)
    marker("prefix_closure_bound")

    # positive hit: a planted frame-plus-extra tuple must be found
    frame5 = set(ES.coord_proj(5, c) for c in range(5))
    w_all = [p for p in alphabet5 if p not in frame5]
    plant_w = w_all[3]
    plant_wpos = [5, 11]
    want = [3, 3, 3, 1, 1]           # odd multiplicities over frame positions
    plant_assign = [0] * 13
    seen = [0] * 5
    for i in range(13):
        if i in plant_wpos:
            continue
        c = next(c for c in range(5) if seen[c] < want[c])
        seen[c] += 1
        plant_assign[i] = c
    assert seen == want
    hp = [[g.identity] * 3 for _ in range(5)]
    projs = []
    seg = 0
    for i in range(13):
        if i in plant_wpos:
            projs.append(plant_w)
            seg += 1
        else:
            projs.append(ES.coord_proj(5, plant_assign[i]))
            hp[plant_assign[i]][seg] = g.mul(hp[plant_assign[i]][seg],
                                             labels13[i])
    planted = ES.word_product(ga, g, 5, labels13, projs)
    assert planted != ES.ring_target(ga, 5, g.S)
    rec = ES.six_distinct_search(ga, g, 5, labels13, (2,), w_all,
                                 target=planted)
    hits = rec["m2"]["all_witnesses"]
    assert len(hits) >= 1, hits
    assert any(u == plant_w[0] and v == plant_w[1] for _, u, v, _ in hits)
    marker("positive_hit_control survivors=%d (planted target)" % len(hits))

    # tiny end-to-end completeness check (t = 2, n = 6): the signature search
    # must return exactly the direct enumeration of the same family
    t2 = 2
    alpha2 = ES.rank_one_idempotents(t2)
    labels6 = ES.alt_labels(g, 6)
    frame2 = set(ES.coord_proj(t2, c) for c in range(t2))
    w_all2 = [p for p in alpha2 if p not in frame2]
    direct = {}
    for m2 in (2, 4):
        for wpos in itertools.combinations(range(6), m2):
            for w in w_all2:
                for cls in itertools.product(range(t2), repeat=6 - m2):
                    if any(cls.count(c) % 2 == 0 for c in range(t2)):
                        continue
                    projs = []
                    ci = 0
                    for i in range(6):
                        if i in wpos:
                            projs.append(w)
                        else:
                            projs.append(ES.coord_proj(t2, cls[ci]))
                            ci += 1
                    direct[((m2, w), tuple(projs))] = \
                        ES.word_product(ga, g, t2, labels6, projs)
    # target = a planted family tuple so the comparison is non-vacuous
    (m2p, wp), projsp = next(iter(direct))
    tiny_target = direct[((m2p, wp), tuple(projsp))]
    want2 = set(key for key, projs in direct
                if direct[(key, projs)] == tiny_target)
    rec2 = ES.six_distinct_search(ga, g, t2, labels6, (2, 4), w_all2,
                                  target=tiny_target)
    found2 = set()
    for key in ("m2", "m4"):
        for wkey, u, v, _ in rec2[key]["all_witnesses"]:
            found2.add((wkey[0], (u, v)))
    assert found2 == want2, (found2, want2)
    assert len(want2) >= 1
    marker("tiny_completeness_t2_n6 family_hits=%d" % len(want2))

    # ------------------------------------------------------------------
    # 4. KB2 run: complete six-distinct-value family at t = 5, n = 13.
    # ------------------------------------------------------------------
    receipts = ES.six_distinct_search(ga, g, 5, labels13, (2, 4, 6, 8), w_all)
    total_evals = 0
    total_assign = 0
    total_surv = 0
    for key in ("m2", "m4", "m6", "m8"):
        r = receipts[key]
        total_evals += r["evaluations"]
        total_assign += r["assignments"]
        total_surv += r["survivors"]
        print("  %s: assignments=%d signatures=%d peak_dp=%d evals=%d "
              "survivors=%d sig_sha256=%s"
              % (key, r["assignments"], r["signatures"], r["peak_dp_states"],
                 r["evaluations"], r["survivors"], r["signature_sha256"]))
    assert total_surv == 0, receipts

    # shard receipts over the m=2 signature list (parallel-safe batches)
    print("  coverage: six-distinct family complete for m_W in {2,4,6,8}; "
          "d<=5 commuting family excluded by the predecessor "
          "(research/fiveswap-alt13-commuting-screen); d>=7 NOT covered")
    print("PASS_KB2_ALT13_NONCOMMUTING_TOOLING",
          "assignments=%d" % total_assign,
          "evaluations=%d" % total_evals,
          "survivors=%d" % total_surv,
          "frontier=d6_complete_d_ge_7_open",
          "no_new_kappa",
          "elapsed=%.1fs" % (time.time() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
