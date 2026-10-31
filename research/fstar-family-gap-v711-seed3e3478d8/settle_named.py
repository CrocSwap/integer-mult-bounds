#!/usr/bin/env python3
"""One bounded pivot (KB5h): settle named EXACTLY on the deep records whose
Lemma MX construction product is within a raised 3M cap but was scanned under
the 2M cap. If an exhaustive named lands at named_lo while cert = v, the
family gap gap_named = cert - named reaches 2 with both sides exact - the
headline question of the v = 7..11 enumeration. Updates the deep receipts in
place (fields: named, named_detail, named_exhaustive, gap_named) and writes
data/census_v711/receipt-supplement-settle-named.json for traceability.
Run: python3 -B settle_named.py"""
import importlib.util
import json
import os
import sys
import time

T0 = time.time()
HERE = os.path.dirname(os.path.abspath(__file__))
ENG = os.path.join(HERE, "predecessor", "pr2914", "verify.py")
DATA = os.path.join(HERE, "predecessor", "pr2914", "data")
CENSUS = os.path.join(HERE, "data", "census_v711")
CAP = 3000000

spec = importlib.util.spec_from_file_location("pr2914_engine", ENG)
fg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fg)


def log(msg):
    print("[%7.1fs] %s" % (time.time() - T0, msg), flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    todo = []
    for fn in sorted(os.listdir(CENSUS)):
        if not (fn.startswith("receipt-") and fn.endswith("-deep.json")):
            continue
        with open(os.path.join(CENSUS, fn), "r", encoding="utf-8") as fh:
            rec = json.load(fh)
        for r in rec["records"]:
            if (not r.get("named_exhaustive")) and 0 < r["mx_product"] <= CAP:
                todo.append((fn, rec, r))
    log("records with scanned named and mx product <= %d: %d"
        % (CAP, len(todo)))
    supp = []
    for fn, rec, r in todo:
        label = r["label"]
        fx = label.split("|")[0] + ".json"
        S = [int(x) for x in label.split("|")[1].split(",")]
        mod0 = fg.model(*fg.load_decoder(os.path.join(DATA, fx)))
        sub = fg.restrict(mod0, S)
        ad = fg.anchor_data(sub)
        v = sub["v"]
        inm, _ = fg.digraph_tables(v, sub["arcs"])
        acyc = fg.acyclic_table(v, inm)
        mas = fg.mas_table(v, acyc)
        named_val, det = fg.named_exact_small(sub, ad, mas, acyc, cap=CAP,
                                              scan_iters=20000)
        assert det.get("exhaustive"), "expected exhaustive at %s" % label
        old = r["named"]
        r["named"] = named_val
        r["named_detail"] = det
        r["named_exhaustive"] = True
        r["named_settled_cap"] = CAP
        r["gap_named"] = r["cert"] - named_val
        supp.append(dict(label=label, old_named=old, named=named_val,
                         cert=r["cert"], gap_named=r["gap_named"],
                         exhaustive=True, product=r["mx_product"]))
        log("settled %s: named %s -> %d (exhaustive, product %d), "
            "cert=%d gap_named=%d"
            % (label, old, named_val, r["mx_product"], r["cert"],
               r["gap_named"]))
        with open(os.path.join(CENSUS, fn), "w", encoding="utf-8",
                  newline="\n") as fh:
            json.dump(rec, fh, indent=1, sort_keys=True)
            fh.write("\n")
    out = dict(cap=CAP, settled=supp)
    with open(os.path.join(CENSUS,
                           "receipt-supplement-settle-named.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    prov2 = [s for s in supp if s["gap_named"] >= 2]
    log("done: %d settled, %d with proven gap_named >= 2"
        % (len(supp), len(prov2)))
    print("PASS_SETTLE_NAMED settled=%d proven-gap2=%d"
          % (len(supp), len(prov2)))


if __name__ == "__main__":
    main()
