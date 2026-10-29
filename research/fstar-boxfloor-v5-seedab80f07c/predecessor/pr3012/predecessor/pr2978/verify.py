#!/usr/bin/env python3
"""KB5j registered replay: Lemma BPP's without-loss question at tau >= 1.

Recomputes from scratch (stdlib, deterministic, single process):
  1. vendored predecessor pins (PR 2963's 14-file pin set + every vendored
     file of this package; fixture hashes asserted);
  2. predecessor anchors (PR 2914 controls + calibration; exact named
     RECOMPUTED on the twelve tied_min v = 11 sub-decoders; every stored
     cert/box witness replayed; PR 2936's tau = 0 demo cert = 2 > box = 1);
  3. job A: v = 2 exhaustive (2842 scope-consistent configs, box = cert = 2);
  4. job B: v = 3 combinatorial enumeration (3023 canonical configs, 27 gap
     candidates with the three realized ones asserted by constant);
  5. job C: 360 realizable tau >= 1 instances (0 box violations, 1788 strict
     projection drops, escape classes E1..E4);
  6. job D: candidate realization (3 counterexamples cert = 3 > box = 2 with
     the README's exact P, Q; 3 unrealizable-column; 21 not-found-in-cap);
  7. the escape classification of PR 2963's pool (19 distinct, all E1);
  8. an INDEPENDENT enumeration of cert and box for the delivered
     counterexample written from the section-7 definition (not the vendored
     engine), plus Lemma RT's triangular-rank and shareable-totals checks.

Prints PASS markers and writes CERTIFICATE.json (newline="\\n").
Run: python3 -B verify.py
"""
import hashlib
import importlib.util
import itertools
import json
import os
import sys
import time

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "predecessor", "pr2963"))
import named_exact as ne  # noqa: E402

fg = ne.fg
DATA = os.path.join(HERE, "predecessor", "pr2963", "predecessor", "pr2914",
                    "data")
spec = importlib.util.spec_from_file_location(
    "box_attack",
    os.path.join(HERE, "predecessor", "pr2963", "predecessor", "pr2936",
                 "box_attack.py"))
ba = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ba)


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ------------------------------------------------------------ delivered cex
CEX_P = [[-1, -3, 0], [1, -1, -2], [3, 3, 3]]
CEX_Q = [[1, -3, 2], [3, -1, -2], [3, -1, 2]]
CEX_A0 = [3, 3, 7]
CEX_B0 = [3, 3, 3]


def dot1(x, y):
    return bin(x & y).count("1") & 1


def indep_value(v, M, a_choice, b_choice):
    """Independent max-kept value from the section-7 definition: K_tt = 1 on
    the kept set and K_ts = 0 on every forward zero arc, for some order."""
    K = [[dot1(a_choice[t], b_choice[s]) for s in range(v)] for t in range(v)]
    good = [t for t in range(v) if K[t][t] == 1]
    for r in range(len(good), 0, -1):
        for S in itertools.combinations(good, r):
            for order in itertools.permutations(S):
                pos = {t: i for i, t in enumerate(order)}
                if all(not (M[t][s] == 0 and pos[t] < pos[s] and K[t][s])
                       for t in S for s in S if t != s):
                    return r
    return 0


def indep_cert_box(mod, ad):
    """Independent enumeration of cert and box for v = 3."""
    v = mod["v"]
    M = mod["M"]

    def enum(pi_list, sg_list):
        aopts = [[m for m in range(8) if (m & ~pi_list[t]) == 0]
                 for t in range(v)]
        bopts = [[m for m in range(8) if (m & ~sg_list[t]) == 0]
                 for t in range(v)]
        best = 0
        for a_choice in itertools.product(*aopts):
            for b_choice in itertools.product(*bopts):
                val = indep_value(v, M, a_choice, b_choice)
                if val > best:
                    best = val
                    if best == v:
                        return best
        return best

    cert = enum(mod["pi"], mod["sg"])
    box = enum(ad["a0"], ad["b0"])
    return cert, box


def rank_f2(rows):
    pivots = {}
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p in pivots:
                x ^= pivots[p]
            else:
                pivots[p] = x
                break
    return len(pivots)


# ------------------------------------------------------------------- checks
def check_pins():
    pins = load_json(os.path.join(HERE, "predecessor", "pr2963",
                                  "predecessor", "PINS.json"))
    n = 0
    for rel, want in sorted(pins["files"].items()):
        p = os.path.join(HERE, "predecessor", "pr2963", "predecessor",
                         *rel.split("/"))
        assert sha256_file(p) == want, "pin mismatch: %s" % rel
        n += 1
    assert pins["files"]["pr2914/data/tied_min.json"] == \
        "670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93"
    assert pins["files"]["pr2914/data/cex_min_1.json"] == \
        "86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7"
    mine = load_json(os.path.join(HERE, "predecessor", "PINS.json"))
    m = 0
    for rel, want in sorted(mine["files"].items()):
        p = os.path.join(HERE, "predecessor", *rel.split("/"))
        assert sha256_file(p) == want, "own pin mismatch: %s" % rel
        m += 1
    print("PASS_KJ_PINS pr2963-pins=%d own-pins=%d" % (n, m))
    return n, m


def load_sub(label):
    fx = label.split("|")[0] + ".json"
    mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fx)))
    S = [int(x) for x in label.split("|")[1].split(",")]
    return fg.restrict(mod0, S)


def check_anchors():
    fg.run_controls()
    fg.run_calibration()
    stored2936 = load_json(os.path.join(HERE, "predecessor", "pr2963",
                                       "predecessor", "pr2936",
                                       "receipt-tied_min-s11-deep.json"))
    labels = sorted(r["label"] for r in stored2936["records"])
    assert len(labels) == 12
    named_receipt = load_json(os.path.join(HERE, "predecessor", "pr2963",
                                          "data", "named-v11-receipt.json"))
    inbox = 0
    for label in labels:
        sub = load_sub(label)
        ad = fg.anchor_data(sub)
        inm, _ = fg.digraph_tables(sub["v"], sub["arcs"])
        acyc = fg.acyclic_table(sub["v"], inm)
        mas = fg.mas_table(sub["v"], acyc)
        named, det = ne.named_exact(sub, ad, mas, acyc, cap=6000000)
        assert named == 9 and det["exhaustive"], label
        rec = named_receipt["records"][label]
        cw = rec["cert_witness"]
        assert fg.replay_witness(sub, cw) and len(cw["kept"]) == 11, label
        inb, _esc = fg.in_box(sub, ad, cw)
        assert inb == rec["cert_witness_in_box"], label
        inbox += 1 if inb else 0
        bw = rec["box_witness"]
        assert fg.replay_witness(sub, bw) and fg.in_box(sub, ad, bw)[0], label
        assert rec["cert"] == 11 and rec["box"] == 11 and rec["named"] == 9
    print("PASS_KJ_ANCHORS named=9x12 box-replay-in-box=%d/12" % inbox)
    P = [(1, 0, 1), (2, 1, 0)]
    Q = [(1, 0, 0), (1, 0, 1)]
    sub = fg.model(P, Q)
    ad = fg.anchor_data(sub)
    ce, cew = fg.cert_exact(sub, max_v=2)
    bx, _ = ba.box_exact_tolerant(sub, ad)
    assert (ce, bx) == (2, 1) and fg.replay_witness(sub, cew)
    print("PASS_KJ_TAU0_DEMO cert=2 box=1")
    return labels


def check_counterexample():
    mod = fg.model([tuple(p) for p in CEX_P], [tuple(q) for q in CEX_Q])
    ad = fg.anchor_data(mod)
    assert list(ad["a0"]) == CEX_A0 and list(ad["b0"]) == CEX_B0
    assert list(ad["tau"]) == [2, 2, 2]
    assert fg.tie_parity(mod, ad) and fg.scope_identity(mod, ad)
    assert mod["M"] == [[8, 0, 0], [0, 8, 0], [0, 0, 12]]
    assert len(mod["arcs"]) == 6  # every off-diagonal pair zero
    # shareable totals (Corollary): r_box = #{j : c_j = gamma} = 2
    c = [ad["m"][j] + ad["n"][j] for j in range(3)]
    r_box = sum(1 for j in range(3) if c[j] == ad["gamma"])
    assert c == [0, 0, 1] and r_box == 2
    # Lemma RT on the counterexample: full labels keep 3 only via rank 3
    a_w = [1, 2, 4]
    b_w = [1, 2, 4]
    Krows = [sum((dot1(a_w[t], b_w[s]) << s) for s in range(3))
             for t in range(3)]
    assert rank_f2(Krows) == 3
    # every box K has rank <= 2 (bit 2 never on a b-side)
    for at in itertools.product(*[[m for m in range(8)
                                   if (m & ~ad["a0"][t]) == 0]
                                  for t in range(3)]):
        for bt in itertools.product(*[[m for m in range(8)
                                       if (m & ~ad["b0"][t]) == 0]
                                      for t in range(3)]):
            rows = [sum((dot1(at[t], bt[s]) << s) for s in range(3))
                    for t in range(3)]
            assert rank_f2(rows) <= 2
    # engine values + replayed witnesses
    ce, cew = fg.cert_exact(mod, max_v=3)
    bx, bxw = ba.box_exact_tolerant(mod, ad)
    assert (ce, bx) == (3, 2)
    assert fg.replay_witness(mod, cew) and len(cew["kept"]) == 3
    assert fg.in_box(mod, ad, cew)[0] is False
    assert bxw is not None and fg.replay_witness(mod, bxw) \
        and fg.in_box(mod, ad, bxw)[0] and len(bxw["kept"]) == 2
    # independent enumeration from the section-7 definition
    ice, ibx = indep_cert_box(mod, ad)
    assert (ice, ibx) == (3, 2), (ice, ibx)
    print("PASS_KJ_COUNTEREXAMPLE v=3 tau=2/2/2 cert=3 box=2 r_box=2 "
          "independent=3/2")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    check_pins()
    check_anchors()
    check_counterexample()

    # jobs A/B/C recomputed (they rewrite their deterministic receipts)
    import box_search_kj as bk
    bk.main()
    kj = load_json(os.path.join(HERE, "data", "box-search-kj-receipt.json"))
    assert kj["job_a"]["configs"] == 2842 and kj["job_a"]["gaps"] == 0
    assert kj["job_b"]["configs"] == 3023 and len(kj["job_b"]["candidates"]) \
        == 27
    want = {(tuple([3, 3, 7]), tuple([3, 3, 3])),
            (tuple([3, 7, 7]), tuple([3, 3, 3])),
            (tuple([7, 7, 7]), tuple([3, 3, 3]))}
    got = {(tuple(c["a0"]), tuple(c["b0"]))
           for c in kj["job_b"]["candidates"]}
    assert want <= got
    jc = kj["job_c"]
    assert len(jc["instances"]) == 360 and len(jc["gaps"]) == 0
    assert len(jc["drops"]) == 1788
    assert jc["escape_classes"] == {"E2": 1768, "E1": 466, "E4": 18, "E3": 6}
    print("PASS_KJ_JOBS v2-configs=2842 v3-configs=3023 candidates=27 "
          "realizable=360 violations=0 drops=1788")

    # escape classification recomputed
    import escape_classify as ec
    ec.main()
    er = load_json(os.path.join(HERE, "data", "escape-receipt.json"))
    assert er["escapes_seen"] == 19 and len(er["records"]) == 19
    assert all(r["escape_kind"] == "E1" for r in er["records"])
    assert not any(r["projected_value"] < r["value"] for r in er["records"])
    assert not any(r["box"] < r["cert"] for r in er["records"])
    print("PASS_KJ_ESCAPE escapes=19 kinds=E1x19 drops=0 box-gaps=0")

    # realization recomputed (deterministic rng)
    import realize_kj as rk
    rk.main()
    rr = load_json(os.path.join(HERE, "data", "realize-kj-receipt.json"))
    assert rr["status_counts"] == {"not-found-in-cap": 21,
                                  "unrealizable-column": 3,
                                  "realized": 3}
    assert len(rr["counterexamples"]) == 3
    first = rr["counterexamples"][0]
    assert first["P"] == CEX_P and first["Q"] == CEX_Q
    for cex in rr["counterexamples"]:
        assert cex["cert"] == 3 and cex["box"] == 2
        mod = fg.model([tuple(p) for p in cex["P"]],
                       [tuple(q) for q in cex["Q"]])
        ad = fg.anchor_data(mod)
        assert fg.replay_witness(mod, cex["cert_witness"])
        assert fg.tie_parity(mod, ad) and fg.scope_identity(mod, ad)
        assert min(ad["tau"]) >= 1
        ce, _ = fg.cert_exact(mod, max_v=3)
        bx, _ = ba.box_exact_tolerant(mod, ad)
        assert (ce, bx) == (3, 2)
    log("realization replayed: 3 counterexamples cert=3 box=2 exact both")
    print("PASS_KJ_REALIZE candidates=27 realized=3 unrealizable-column=3 "
          "not-found-in-cap=21 counterexamples=3")
    print("PASS_KJ_WITHOUTLOSS verdict=counterexample v=3 tau>=1 cert=3>box=2")

    files = ["README.md", "TASK.json", "TASK-CARD.md", "verify.py",
             "box_search_kj.py", "escape_classify.py", "realize_kj.py",
             "data/box-search-kj-receipt.json", "data/escape-receipt.json",
             "data/realize-kj-receipt.json", "predecessor/PINS.json"]
    digests = {}
    for f in files:
        p = os.path.join(HERE, *f.split("/"))
        if os.path.exists(p):
            digests[f] = sha256_file(p)
    cert = dict(schema_version=1,
                package="fstar-box-withoutloss-seed7f3a1c",
                base_commit="0614abaef427f123d9b844f85a759e64ee3ab29c",
                markers=["PASS_KJ_PINS", "PASS_FG_CONTROLS",
                         "PASS_FG_CALIBRATION", "PASS_KJ_ANCHORS",
                         "PASS_KJ_TAU0_DEMO", "PASS_KJ_COUNTEREXAMPLE",
                         "PASS_KJ_JOBS", "PASS_KJ_ESCAPE",
                         "PASS_KJ_REALIZE", "PASS_KJ_WITHOUTLOSS"],
                headline=dict(
                    verdict="box-completeness for tau >= 1 REFUTED; minimal "
                            "counterexample v = 3, cert = 3 > box = 2",
                    v2_proven="box = cert = 2 at v = 2, tau >= 1",
                    counterexample_P=CEX_P, counterexample_Q=CEX_Q,
                    cex_cert=3, cex_box=2, cex_tau=[2, 2, 2], cex_r_box=2,
                    v2_configs=2842, v3_configs=3023, v3_candidates=27,
                    realized_counterexamples=3,
                    realizable_instances=360, box_violations=0,
                    projection_drops=1788,
                    escape_classes={"E2": 1768, "E1": 466, "E4": 18,
                                    "E3": 6},
                    pr2963_pool_escapes=19),
                files=digests)
    body = json.dumps(cert, indent=1, sort_keys=True)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    cert["digest"] = digest
    with open(os.path.join(HERE, "CERTIFICATE.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(cert, fh, indent=1, sort_keys=True)
        fh.write("\n")
    log("certificate digest %s" % digest)


if __name__ == "__main__":
    main()
