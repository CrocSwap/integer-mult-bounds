#!/usr/bin/env python3
"""Crude keyword classifier for PR titles (single process, stdlib only).

Reproduce:  python3 -B classify_titles.py
Reads prs400_titles.json (from `gh pr list --state all --limit 400 --json
number,title,author,createdAt`) and writes classified_titles.csv and
summary.json next to it.  Categories are non-exclusive keyword flags; a title
may match several or none ("other").  Titles are a weak proxy for content.
"""
import csv, json, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
RULES = {
    "scoped_negative": r"scoped negative|obstruction|no new kappa|no new κ|negative result",
    "conditional_kappa": r"conditional (kappa|κ)",
    "prove_lemma": r"\bprove\b|\bproof\b|theorem|lemma",
    "verification_audit": r"independent(ly)? (verification|audit|verify)|\baudit\b|independently",
    "tooling": r"^tooling\b|tooling:",
}
RX = {k: re.compile(v, re.I) for k, v in RULES.items()}

def main():
    prs = json.loads((HERE / "prs400_titles.json").read_text())
    rows, cnt = [], Counter()
    for p in prs:
        flags = [k for k, r in RX.items() if r.search(p["title"])]
        for k in flags: cnt[k] += 1
        if not flags: cnt["other"] += 1
        rows.append({"number": p["number"], "author": p["author"]["login"],
                     "createdAt": p["createdAt"], "categories": "|".join(flags) or "other",
                     "title": p["title"]})
    rows.sort(key=lambda r: r["number"])
    with open(HERE / "classified_titles.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    n = len(rows)
    summ = {"n": n, "pr_range": [rows[0]["number"], rows[-1]["number"]],
            "counts": dict(cnt), "shares": {k: round(v / n, 3) for k, v in cnt.items()},
            "rules": RULES}
    (HERE / "summary.json").write_text(json.dumps(summ, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: summ[k] for k in ("n", "pr_range", "counts", "shares")}, ensure_ascii=False))

if __name__ == "__main__":
    sys.exit(main())
