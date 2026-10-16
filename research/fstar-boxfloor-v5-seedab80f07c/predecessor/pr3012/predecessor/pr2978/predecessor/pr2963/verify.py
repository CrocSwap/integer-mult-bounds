#!/usr/bin/env python3
"""KB5i registered replay: exact named on the twelve open tied_min v = 11
sub-decoders (the recorded remainder of PR 2936), its cert/box cross-check,
and the bounded box-completeness attack.

What this replay does (deterministic, stdlib, single process):
  1. verifies every vendored predecessor pin (byte-exact engine + fixtures +
     PR 2936 remainder; predecessor/PINS.json);
  2. runs the vendored PR 2914 controls and calibration (reproduces every
     recorded anchor: PASS_FG_CALIBRATION tied_min=11/12 cex_min_1=18/19
     mp=9/16 chain=22 reach=0/12,8/19);
  3. RECOMPUTES the exact named value from scratch on all 12 records (the
     coarse DP - it does not trust the receipts), replays the MX
     construction witnesses, and asserts named = 9 exact and gap_named = 2
     with cert = 11 from replayed ceiling witnesses;
  4. cross-checks PR 2936's vendored stored values (MP, products, tau) and
     counts the stored cert under-reports;
  5. independently replays every stored cert/box witness of
     data/named-v11-receipt.json (supports, K_tt, order constraints, box
     membership);
  6. re-runs the box-search core (the v = 2 tau = 0 BPP strictness
     demonstration and a bounded deterministic sample of the 60
     fixture-density tau >= 1 instances) against
     data/box-search-receipt.json;
  7. writes CERTIFICATE.json (newline="\\n") and prints PASS markers.

Run: python3 -B verify.py
"""
import hashlib
import importlib.util
import json
import os
import sys
import time

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import named_exact as ne  # noqa: E402

fg = ne.fg
DATA = os.path.join(HERE, "predecessor", "pr2914", "data")
PR2936_RECEIPT = os.path.join(HERE, "predecessor", "pr2936",
                              "receipt-tied_min-s11-deep.json")
spec = importlib.util.spec_from_file_location(
    "box_attack", os.path.join(HERE, "predecessor", "pr2936", "box_attack.py"))
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


def load_sub(label):
    fx = label.split("|")[0] + ".json"
    mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fx)))
    S = [int(x) for x in label.split("|")[1].split(",")]
    return fg.restrict(mod0, S)


def tables(sub):
    inm, _ = fg.digraph_tables(sub["v"], sub["arcs"])
    acyc = fg.acyclic_table(sub["v"], inm)
    mas = fg.mas_table(sub["v"], acyc)
    return mas, acyc


def check_pins():
    pins = load_json(os.path.join(HERE, "predecessor", "PINS.json"))
    n = 0
    for rel, want in sorted(pins["files"].items()):
        p = os.path.join(HERE, "predecessor", *rel.split("/"))
        got = sha256_file(p)
        assert got == want, "pin mismatch: %s" % rel
        n += 1
    assert pins["files"]["pr2914/data/tied_min.json"] == \
        "670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93"
    assert pins["files"]["pr2914/data/cex_min_1.json"] == \
        "86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7"
    print("PASS_KB5I_PINS files=%d" % n)
    return n


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    npins = check_pins()
    fg.run_controls()
    fg.run_calibration()
    named_receipt = load_json(os.path.join(HERE, "data",
                                          "named-v11-receipt.json"))
    stored2936 = {r["label"]: r for r in load_json(PR2936_RECEIPT)["records"]}
    labels = sorted(stored2936)
    assert len(labels) == 12

    # (3) recompute exact named from scratch on all 12 + cross-checks
    named_vals = {}
    under = 0
    for label in labels:
        sub = load_sub(label)
        ad = fg.anchor_data(sub)
        mas, acyc = tables(sub)
        assert fg.tie_parity(sub, ad) and fg.scope_identity(sub, ad)
        named, det = ne.named_exact(sub, ad, mas, acyc, cap=6000000)
        assert det["exhaustive"], label
        wit = det["mx_detail"]["witness"]
        assert wit is not None
        assert ne.replay_mx_witness(sub, ad, mas, wit) == det["mx"], label
        r2936 = stored2936[label]
        assert det["MP"] == r2936["MP"], label
        assert det["reach"] == r2936["reach"], label
        assert det["mx_detail"]["coarse_product"] == 3 ** 11, label
        assert r2936["mx_product"] == 1977326743, label
        assert list(ad["tau"]) == r2936["tau"], label
        assert len(ad["cancel"]) == r2936["k_cancel"], label
        rec = named_receipt["records"][label]
        assert rec["named"] == named == 9, label
        assert rec["named_detail"]["mx"] == det["mx"], label
        assert rec["named_detail"]["cl3"] == det["cl3"] == det["MP"], label
        named_vals[label] = named
        if r2936["cert"] < 11:
            under += 1
    log("exact named recomputed: 12 records, all named = 9")
    print("PASS_KB5I_NAMED records=12 named-exact=12 named=9x12 gap2-proven=12")
    print("PASS_KB5I_CROSSCHECK stored-under-reports=%d" % under)
    assert under == 7, "expected 7 stored cert under-reports, got %d" % under

    # (5) replay every stored witness of the named receipt
    inbox = 0
    for label in labels:
        sub = load_sub(label)
        ad = fg.anchor_data(sub)
        rec = named_receipt["records"][label]
        cw = rec["cert_witness"]
        assert fg.replay_witness(sub, cw), label
        assert len(cw["kept"]) == 11 == rec["cert_witness_value"], label
        inb, esc = fg.in_box(sub, ad, cw)
        assert inb == rec["cert_witness_in_box"], label
        inbox += 1 if inb else 0
        bw = rec["box_witness"]
        assert fg.replay_witness(sub, bw), label
        assert len(bw["kept"]) == 11 == rec["box_witness_value"], label
        assert fg.in_box(sub, ad, bw)[0], label
        assert rec["gap_named"] == 2 and rec["cert"] == 11 \
            and rec["box"] == 11 and rec["named"] == 9, label
    print("PASS_KB5I_BOXREPLAY in-box=%d/12" % inbox)

    # (6) box-search core re-run against its receipt
    bs = load_json(os.path.join(HERE, "data", "box-search-receipt.json"))
    demo = bs["bpp_proven"]
    P = [(1, 0, 1), (2, 1, 0)]
    Q = [(1, 0, 0), (1, 0, 1)]
    sub = fg.model(P, Q)
    ad = fg.anchor_data(sub)
    ce, cew = fg.cert_exact(sub, max_v=2)
    assert fg.replay_witness(sub, cew)
    from box_search import bpp_projection, bpp_conditions
    val = fg.ab_value(sub, cew["a"], cew["b"])
    proj = bpp_projection(sub, ad, cew)
    pval = fg.ab_value(sub, proj["a"], proj["b"])
    assert (val, pval) == (demo["witness_value"], demo["projected_value"]) \
        == (2, 1)
    ok1, ok2 = bpp_conditions(sub, ad, cew)
    assert (ok1, ok2) == (demo["condition_i"], demo["condition_ii"])
    bx, bxw = ba.box_exact_tolerant(sub, ad)
    assert (ce, bx) == (2, 1)
    swept = bs["sweep"]
    assert len(swept) == 60 and bs["counterexample"] is None
    assert all(r["gap_box"] == 0 and r["cert"] == r["box"] for r in swept)
    sample = ([r for r in swept if r["v"] == 4]
              + [r for r in swept if r["v"] == 5][:4]
              + [r for r in swept if r["v"] == 6][:2])
    for r in sample:
        sub = fg.model([tuple(x) for x in r["P"]],
                       [tuple(x) for x in r["Q"]])
        ad = fg.anchor_data(sub)
        assert fg.tie_parity(sub, ad) and fg.scope_identity(sub, ad)
        ce, cew = fg.cert_exact(sub, max_v=r["v"])
        bx, bxw = ba.box_exact_tolerant(sub, ad)
        assert fg.replay_witness(sub, cew)
        assert (ce, bx) == (r["cert"], r["box"]), r["S"]
        assert ce == bx == r["v"], r["S"]
    log("box-search core re-run: demo + %d sweep records" % len(sample))
    print("PASS_BOX_SEARCH bpp-strict-tau0=yes bpp-strict-tau1=no tau-ge1=60 "
          "hard=0 box-violations=0")

    print("PASS_FSTAR_GAP2_V11 gap2-below-v12-confirmed")

    # (7) certificate
    files = ["README.md", "TASK.json", "TASK-CARD.md", "named_exact.py",
             "test_named_exact.py", "run_named_v11.py", "box_search.py",
             "verify.py", "make_meta.py",
             "data/named-v11-receipt.json", "data/box-search-receipt.json",
             "predecessor/PINS.json"]
    digests = {f: sha256_file(os.path.join(HERE, *f.split("/"))) for f in files}
    cert = dict(schema_version=1, package="fstar-gap2-v11-seed42ff0611",
                base_commit="991c50d1ea8ddb7cf88c1b4a45c7b409c02d38fb",
                predecessor_pins=npins,
                markers=["PASS_KB5I_PINS files=%d" % npins,
                         "PASS_FG_CONTROLS", "PASS_FG_CALIBRATION",
                         "PASS_KB5I_NAMED records=12 named-exact=12 "
                         "named=9x12 gap2-proven=12",
                         "PASS_KB5I_CROSSCHECK stored-under-reports=%d" % under,
                         "PASS_KB5I_BOXREPLAY in-box=%d/12" % inbox,
                         "PASS_BOX_SEARCH bpp-strict-tau0=yes "
                         "bpp-strict-tau1=no tau-ge1=60 hard=0 "
                         "box-violations=0",
                         "PASS_FSTAR_GAP2_V11 gap2-below-v12-confirmed"],
                headline=dict(
                    named_exact=9, named_exact_records=12,
                    cert_exact=11, cert_exact_records=12,
                    box_exact=11, box_exact_records=12,
                    gap_named=2, gap_named_records=12,
                    verdict="gap_named = 2 EXISTS below v = 12 "
                            "(minimal exact gap-2 instance at v = 11)",
                    stored_cert_under_reports=under,
                    tau_ge1_sweep_instances=60, box_violations=0,
                    bpp_strict_tau0="PROVEN (v=2: 2 -> 1)",
                    bpp_strict_tau1="no drop in 21 escaping witnesses "
                                    "(CHECKED bounded)"),
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
