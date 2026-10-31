#!/usr/bin/env python3
"""KB5h: v = 7..11 sub-decoder census extending PR 2914's engine (vendored
byte-exactly at predecessor/pr2914/, hash pins in predecessor/PREDECESSOR-PINS.json).

Modes
-----
cheap : Tier A on every enumerated subset: identity controls, exhaustive MP
        (product <= 3^11 < 200000 cap at v <= 11), reach, named_lo, threshold
        and falsifier screens, plus bounded seeded witness hill-climbs on
        nontrivial records (named_lo < v). Records with named_lo = v close
        their gap exactly (cert = named_lo = v, gap_pr = 0, PROVEN).
deep  : Tier B on flagged records: exact named (exhaustive Lemma MX + CL3
        construction spaces within the product/time caps), exact box and cert
        (exhaustive a-enumeration with exact completion) when affordable,
        deep seeded hill-climbs otherwise; box-completeness comparison
        (cert vs box) on every deep record.

Resumable: a receipt JSON per (fixture, size, mode) is rewritten after every
batch of records (default 10) and at every record in deep mode. Rerunning the
same command continues from the receipt.

Deterministic: fixed strides (vendored subsets_smallest_first), fixed seeds.
Blocking foreground runs only; PYTHONUNBUFFERED=1 recommended.
"""
import argparse
import importlib.util
import json
import os
import random
import sys
import time

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.join(HERE, "predecessor", "pr2914", "verify.py")
DATA = os.path.join(HERE, "predecessor", "pr2914", "data")
CENSUS = os.path.join(HERE, "data", "census_v711")

spec = importlib.util.spec_from_file_location("pr2914_engine", ENG)
fg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fg)


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


def load_fixture(name):
    return fg.model(*fg.load_decoder(os.path.join(DATA, name)))


def receipt_path(fixture, size, mode):
    return os.path.join(CENSUS, "receipt-%s-s%d-%s.json"
                        % (fixture.split(".")[0], size, mode))


def load_receipt(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    return None


def save_receipt(path, rec):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(rec, fh, indent=1, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def restricted_engine(sub):
    inm, _ = fg.digraph_tables(sub["v"], sub["arcs"])
    acyc = fg.acyclic_table(sub["v"], inm)
    mas = fg.mas_table(sub["v"], acyc)
    return mas, acyc


def cheap_record(sub, ad, mas, S, label, hill_iters):
    """Tier A record. gap_pr = 0 is PROVEN when named_lo = v (cert <= v)."""
    v = sub["v"]
    thr = (2 * v) // 3
    mp, _mpmap, mp_exh, mp_prod = fg.matched_pivot(sub, mas)
    named_lo = max(mp, len(ad["reach"]))
    rec = dict(label=label, S=list(S), v=v, threshold=thr,
               tau=list(ad["tau"]), tau_min=min(ad["tau"]),
               k_cancel=len(ad["cancel"]), reach=len(ad["reach"]),
               MP=mp, MP_exhaustive=mp_exh, MP_product=mp_prod,
               named_lo=named_lo,
               named_ge_threshold=(named_lo >= thr))
    if named_lo >= v:
        rec.update(gap_pr=0, gap_pr_proven=True,
                   cert=v, cert_exact=True, box=None,
                   trivial_full=True, flagged=False, falsifier=None,
                   falsifier_possible=False)
        return rec
    rec["trivial_full"] = False
    t1 = time.time()
    ce_val, ce_wit = fg.cert_hillclimb(sub, iters=hill_iters, seed=2025)
    bx_val, bx_wit = fg.cert_hillclimb(sub, iters=hill_iters, seed=2024,
                                       box=True, ad=ad)
    assert ce_wit is None or fg.replay_witness(sub, ce_wit), "cert witness"
    assert bx_wit is None or fg.replay_witness(sub, bx_wit), "box witness"
    rec.update(cert=ce_val, cert_exact=False, box=bx_val, box_exact=False,
               gap_pr=ce_val - named_lo, gap_pr_proven=False,
               cert_witness_kept=(len(ce_wit["kept"]) if ce_wit else 0),
               box_witness_kept=(len(bx_wit["kept"]) if bx_wit else 0),
               hill_s=round(time.time() - t1, 2))
    # falsifier screens (PR 2901 criterion, armed)
    rec["falsifier"] = None
    if named_lo >= thr and ce_val >= thr:
        rec["falsifier_possible"] = False  # cost >= cert >= named_lo >= thr
    else:
        rec["falsifier_possible"] = True
        cc, _B, hit = fg.chain_scan(sub, thr, tries=1500)
        rec["chain_scan_best"] = cc
        if hit:
            rec["falsifier"] = ("admissible B with chain cost %d < "
                                "threshold %d" % (cc, thr))
    # deep flagging: nontrivial gap risk or falsifier risk
    rec["flagged"] = bool(
        rec["falsifier_possible"] or rec["gap_pr"] >= 1
        or ce_val < thr)
    rec["witness_cert_a"] = (ce_wit["a"] if ce_wit else None)
    rec["witness_cert_b"] = (ce_wit["b"] if ce_wit else None)
    rec["witness_cert_order"] = (ce_wit["order"] if ce_wit else None)
    rec["witness_box_a"] = (bx_wit["a"] if bx_wit else None)
    rec["witness_box_b"] = (bx_wit["b"] if bx_wit else None)
    rec["witness_box_order"] = (bx_wit["order"] if bx_wit else None)
    return rec


def product_est(sub, ad, kind):
    if kind == "cert":
        ch = [2 ** bin(sub["pi"][t]).count("1") for t in range(sub["v"])]
    elif kind == "box":
        ch = [2 ** bin(ad["a0"][t]).count("1") for t in range(sub["v"])]
    else:  # named MX: 1 anchor + repairs != a0 + pivots in D
        ch = []
        for t in range(sub["v"]):
            n = 1
            for a in range(8):
                if (a & ~sub["pi"][t]) == 0 and fg.dot1(a, ad["b0"][t]) == 1 \
                        and a != ad["a0"][t]:
                    n += 1
            for j in range(3):
                if sub["D"][t] & (1 << j):
                    n += 1
            ch.append(n)
    p = 1
    for c in ch:
        p *= c
    return p


def deep_record(sub, ad, mas, S, label, budget_s):
    """Tier B record: exact named where the construction product allows,
    exact box/cert where the a-enumeration product allows (time-guarded),
    deep seeded hill-climbs otherwise. Box-completeness comparison always."""
    v = sub["v"]
    thr = (2 * v) // 3
    t0 = time.time()
    mx_prod = product_est(sub, ad, "named")
    box_prod = product_est(sub, ad, "box")
    cert_prod = product_est(sub, ad, "cert")
    rec = dict(label=label, S=list(S), v=v, threshold=thr,
               tau=list(ad["tau"]), tau_min=min(ad["tau"]),
               k_cancel=len(ad["cancel"]), reach=len(ad["reach"]),
               mx_product=mx_prod, box_product=box_prod,
               cert_product=cert_prod)
    # exact named: exhaustive construction spaces within a product cap
    named_cap = 2000000
    named_val, named_det = fg.named_exact_small(
        sub, ad, mas, acyc=fg.acyclic_table(v, fg.digraph_tables(v, sub["arcs"])[0]),
        cap=named_cap, scan_iters=20000)
    rec["named"] = named_val
    rec["named_detail"] = named_det
    rec["named_exhaustive"] = bool(named_det.get("exhaustive"))
    mp, _m, _e, _p = fg.matched_pivot(sub, mas)
    rec["MP"] = mp
    rec["named_lo"] = max(mp, len(ad["reach"]))
    # exact box / cert with per-record time budget
    est_s_box = box_prod * 25e-6
    est_s_cert = cert_prod * 120e-6
    bx_val = ce_val = None
    bx_exact = ce_exact = False
    # ceiling shortcut: a witness of size v pins cert = v (and box = v if a
    # box witness of size v exists) without enumeration
    ce_wit = fg.cert_hillclimb(sub, iters=200, seed=2025)
    bx_wit = fg.cert_hillclimb(sub, iters=200, seed=2024, box=True, ad=ad)
    ce_wit = ce_wit[1]
    bx_wit = bx_wit[1]
    if ce_wit is not None and len(ce_wit["kept"]) == v:
        ce_val, ce_exact = v, True
        rec["cert_exact_reason"] = "witness of size v + ceiling"
    if bx_wit is not None and len(bx_wit["kept"]) == v:
        bx_val, bx_exact = v, True
        rec["box_exact_reason"] = "box witness of size v + ceiling"
    if est_s_box <= budget_s * 0.4 and bx_val is None:
        bx_val, bx_wit = fg.box_exact(sub, ad, max_v=v)
        bx_exact = True
        if bx_wit is not None:
            assert fg.replay_witness(sub, bx_wit), "box witness"
            rec["box_witness_in_box"] = fg.in_box(sub, ad, bx_wit)[0]
    if est_s_cert <= budget_s and ce_val is None:
        ce_val, ce_wit = fg.cert_exact(sub, max_v=v)
        ce_exact = True
        if ce_wit is not None:
            assert fg.replay_witness(sub, ce_wit), "cert witness"
            rec["cert_witness_in_box"] = fg.in_box(sub, ad, ce_wit)[0]
            rec["cert_witness_diff"] = fg.diff_labels(sub, ad, ce_wit)
    if bx_val is None:
        bx_val, bx_wit = fg.cert_hillclimb(sub, iters=400, seed=910,
                                           box=True, ad=ad)
        if bx_wit is not None:
            assert fg.replay_witness(sub, bx_wit), "box witness"
    if ce_val is None:
        ce_val, ce_wit = fg.cert_hillclimb(sub, iters=400, seed=911)
        if ce_wit is not None:
            assert fg.replay_witness(sub, ce_wit), "cert witness"
            rec["cert_witness_in_box"] = fg.in_box(sub, ad, ce_wit)[0]
    rec.update(box=bx_val, box_exact=bx_exact,
               cert=ce_val, cert_exact=ce_exact,
               gap_named=ce_val - named_val,
               gap_pr=ce_val - rec["named_lo"],
               gap_box=ce_val - bx_val)
    rec["falsifier"] = None
    if ce_exact and ce_val < thr:
        rec["falsifier"] = "exact cert %d < threshold %d" % (ce_val, thr)
    elif rec["named_lo"] < thr or ce_val < thr:
        cc, _B, hit = fg.chain_scan(sub, thr, tries=1500)
        rec["chain_scan_best"] = cc
        if hit:
            rec["falsifier"] = ("admissible B with chain cost %d < "
                                "threshold %d" % (cc, thr))
    rec["deep_s"] = round(time.time() - t0, 2)
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True,
                    choices=["tied_min.json", "cex_min_1.json"])
    ap.add_argument("--size", type=int, required=True)
    ap.add_argument("--cap", type=int, default=240)
    ap.add_argument("--mode", choices=["cheap", "deep"], default="cheap")
    ap.add_argument("--hill-iters", type=int, default=120)
    ap.add_argument("--budget-s", type=float, default=300.0)
    ap.add_argument("--labels", default="",
                    help="deep mode: semicolon-separated record labels to run")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    path = receipt_path(args.fixture, args.size, args.mode)
    rec = load_receipt(path) or dict(
        fixture=args.fixture, size=args.size, mode=args.mode, cap=args.cap,
        records=[], done_subsets=[], started_utc=None)
    if rec["started_utc"] is None:
        rec["started_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                           time.gmtime())
    mod0 = load_fixture(args.fixture)
    if args.mode == "deep" and args.labels:
        # deep records are driven by the labels of cheap receipts
        wanted = set(x for x in args.labels.split(";") if x)
        allrec = []
        for sz in range(3, 12):
            p2 = receipt_path(args.fixture, sz, "cheap")
            rr = load_receipt(p2)
            if rr:
                allrec.extend(rr["records"])
        done = set(tuple(x) for x in rec["done_subsets"])
        todo = [r for r in allrec if r["label"] in wanted
                and tuple(r["S"]) not in done]
    else:
        subs, total, thinned = fg.subsets_smallest_first(
            mod0["v"], args.size, args.cap)
        rec["total_subsets"] = total
        rec["thinned"] = thinned
        rec["enumerated"] = len(subs)
        done = set(tuple(x) for x in rec["done_subsets"])
        todo = [S for S in subs if tuple(S) not in done]
    log("fixture=%s size=%d mode=%s todo=%d (receipt %s)"
        % (args.fixture, args.size, args.mode, len(todo),
           os.path.basename(path)))
    if args.mode == "cheap":
        for i, S in enumerate(todo):
            sub = fg.restrict(mod0, list(S))
            ad = fg.anchor_data(sub)
            assert fg.tie_parity(sub, ad) and fg.scope_identity(sub, ad), \
                "identity controls must hold on every sub-decoder"
            label = "%s|%s" % (args.fixture.split(".")[0],
                               ",".join(map(str, S)))
            r = cheap_record(sub, ad, fg.mas_table(
                sub["v"], fg.acyclic_table(
                    sub["v"], fg.digraph_tables(sub["v"], sub["arcs"])[0])),
                S, label, args.hill_iters)
            rec["records"].append(r)
            rec["done_subsets"].append(list(S))
            if (i + 1) % 10 == 0 or r["flagged"] or r["falsifier"]:
                save_receipt(path, rec)
                log("  %d/%d done; last %s named_lo=%d cert=%s flagged=%s "
                    "falsifier=%s"
                    % (i + 1, len(todo), label, r["named_lo"], r["cert"],
                       r["flagged"], r["falsifier"]))
                if r["falsifier"]:
                    log("EARLY KILL: falsifier found; stopping cell")
                    rec["early_kill"] = r["label"]
                    save_receipt(path, rec)
                    return
        save_receipt(path, rec)
    else:
        for i, src in enumerate(todo):
            S = src["S"]
            sub = fg.restrict(mod0, list(S))
            ad = fg.anchor_data(sub)
            assert fg.tie_parity(sub, ad) and fg.scope_identity(sub, ad)
            label = src["label"]
            mas, _acy = restricted_engine(sub)
            r = deep_record(sub, ad, mas, S, label, args.budget_s)
            rec["records"].append(r)
            rec["done_subsets"].append(list(S))
            save_receipt(path, rec)
            log("  deep %d/%d %s named=%s(%s) box=%s(%s) cert=%s(%s) "
                "gap_named=%s gap_box=%s falsifier=%s in %.1fs"
                % (i + 1, len(todo), label, r["named"], r["named_exhaustive"],
                   r["box"], r["box_exact"], r["cert"], r["cert_exact"],
                   r["gap_named"], r["gap_box"], r["falsifier"],
                   r["deep_s"]))
            if r["falsifier"]:
                log("EARLY KILL: falsifier found; stopping")
                rec["early_kill"] = label
                save_receipt(path, rec)
                return
        save_receipt(path, rec)
    rec["finished_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save_receipt(path, rec)
    log("cell complete: %d records -> %s" % (len(rec["records"]),
                                             os.path.basename(path)))


if __name__ == "__main__":
    main()
