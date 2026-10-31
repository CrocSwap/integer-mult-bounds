#!/usr/bin/env python3
"""Pull the deep receipts' interesting records: exactness flags, witness
in-box flags, and the corrected gap bookkeeping (cert >= box always, cert = v
is exact by ceiling). Scratch/analysis script."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = os.path.join(HERE, "data", "census_v711")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    want = sys.argv[1:] if len(sys.argv) > 1 else None
    for fn in sorted(os.listdir(CENSUS)):
        if not (fn.startswith("receipt-") and fn.endswith("-deep.json")):
            continue
        with open(os.path.join(CENSUS, fn), "r", encoding="utf-8") as fh:
            rec = json.load(fh)
        for r in rec["records"]:
            if want and r["label"] not in want:
                continue
            cert_exact = bool(r.get("cert_exact")) or r["cert"] == r["v"]
            box_exact = bool(r.get("box_exact")) or r["box"] == r["v"]
            named_exact = bool(r.get("named_exhaustive"))
            print("%-46s v=%2d named=%2d(%s) box=%2d(%s) cert=%2d(%s) "
                  "gap_named=%s gap_box=%s"
                  % (r["label"], r["v"], r["named"], "exh" if named_exact
                     else "scan", r["box"], "exh" if box_exact else "hill",
                     r["cert"], "exh" if cert_exact else "hill",
                     r["gap_named"], r["gap_box"]))
            print("      products: mx=%s box=%s cert=%s | "
                  "cert_in_box=%s box_in_box=%s | thr=%d k_cancel=%d "
                  "tau_min=%d reach=%d MP=%d"
                  % (r["mx_product"], r["box_product"], r["cert_product"],
                     r.get("cert_witness_in_box"), r.get("box_witness_in_box"),
                     r["threshold"], r["k_cancel"], r["tau_min"], r["reach"],
                     r["MP"]))
            nd = r.get("named_detail") or {}
            print("      named_detail: MP=%s reach=%s mx=%s cl3=%s "
                  "exhaustive=%s product=%s"
                  % (nd.get("MP"), nd.get("reach"), nd.get("mx"),
                     nd.get("cl3"), nd.get("exhaustive"), nd.get("product")))


if __name__ == "__main__":
    main()
