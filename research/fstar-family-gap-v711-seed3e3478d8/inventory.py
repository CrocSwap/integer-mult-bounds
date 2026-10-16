#!/usr/bin/env python3
"""Inventory of the v = 7..11 cheap census receipts: cell coverage, trivial
gap-0 closures, flagged records, gap-pr distribution, falsifier screen, and
the prioritized deep-tier label lists. Scratch/analysis script."""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CENSUS = os.path.join(HERE, "data", "census_v711")


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cells = []
    all_recs = []
    for fn in sorted(os.listdir(CENSUS)):
        if not (fn.startswith("receipt-") and fn.endswith("-cheap.json")):
            continue
        with open(os.path.join(CENSUS, fn), "r", encoding="utf-8") as fh:
            rec = json.load(fh)
        rs = rec["records"]
        cells.append((fn, len(rs), rec.get("enumerated"), rec.get("total_subsets"),
                      rec.get("thinned")))
        all_recs.extend(rs)
    print("cells:")
    for fn, n, en, tot, th in cells:
        print("  %-44s records=%d enumerated=%s of %s thinned=%s"
              % (fn, n, en, tot, th))
    n = len(all_recs)
    trivial = [r for r in all_recs if r.get("trivial_full")]
    flagged = [r for r in all_recs if r.get("flagged")]
    fals = [r for r in all_recs if r.get("falsifier")]
    gap2 = [r for r in all_recs if (r.get("gap_pr") or 0) >= 2]
    gap1 = [r for r in all_recs if (r.get("gap_pr") or 0) == 1]
    below = [r for r in all_recs if not r["named_ge_threshold"]]
    certltv = [r for r in all_recs if r["cert"] < r["v"]]
    print("\ntotals: records=%d trivial_full(gap0 proven)=%d flagged=%d "
          "falsifiers=%d gap_pr>=2=%d gap_pr==1=%d named_lo<thr=%d "
          "cert_witness<v=%d" % (n, len(trivial), len(flagged), len(fals),
                                 len(gap2), len(gap1), len(below),
                                 len(certltv)))
    potential = [r for r in all_recs if r["v"] - r["named_lo"] >= 2]
    print("gap2-POSSIBLE (v - named_lo >= 2, true gap could reach 2): %d"
          % len(potential))
    for r in sorted(potential, key=lambda r: (r["v"], r["label"])):
        print("  v=%2d %-42s named_lo=%2d cert=%2d box=%s"
              % (r["v"], r["label"], r["named_lo"], r["cert"], r.get("box")))
    print("min named_lo/v = %.4f" % min(r["named_lo"] / r["v"]
                                        for r in all_recs))
    print("\ngap_pr >= 2 records (cert exact when cert = v):")
    for r in sorted(gap2, key=lambda r: (r["v"], r["label"])):
        print("  v=%2d %-42s named_lo=%2d cert=%2d cert_exact=%s "
              "tau_min=%d reach=%d MP=%d"
              % (r["v"], r["label"], r["named_lo"], r["cert"],
                 r.get("cert_exact"), r["tau_min"], r["reach"], r["MP"]))
    print("\ncert_witness < v records (box-completeness testbed):")
    for r in sorted(certltv, key=lambda r: (r["v"], r["label"])):
        print("  v=%2d %-42s named_lo=%2d cert=%2d box=%s tau_min=%d"
              % (r["v"], r["label"], r["named_lo"], r["cert"], r.get("box"),
                 r["tau_min"]))
    # deep priorities: gap2 first, then cert<v, then one gap1 per cell
    gap2_labels = [r["label"] for r in sorted(gap2, key=lambda r: r["v"])]
    certltv_labels = [r["label"] for r in sorted(certltv, key=lambda r: r["v"])]
    seen = set()
    gap1_sample = []
    for r in sorted(gap1, key=lambda r: (r["v"], r["label"])):
        key = (r["label"].split("|")[0], r["v"])
        if key not in seen:
            seen.add(key)
            gap1_sample.append(r["label"])
    out = dict(gap2=gap2_labels, certltv=certltv_labels,
               gap1_sample=gap1_sample,
               potential=[r["label"] for r in sorted(potential,
                                                     key=lambda r: r["v"])])
    with open(os.path.join(CENSUS, "deep-priorities.json"), "w",
              encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print("\ndeep priorities written: gap2=%d certltv=%d gap1_sample=%d"
          % (len(gap2_labels), len(certltv_labels), len(gap1_sample)))


if __name__ == "__main__":
    main()
