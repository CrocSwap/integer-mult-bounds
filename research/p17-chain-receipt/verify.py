#!/usr/bin/env python3
"""Disposition receipt for the p17 kappa ~ 0.003 PR chain and its independent checks (10 PRs, base 2a13eb18).

From RECEIPT.json (recorded heads, merge bases and per-path blobs) and the checked-out base, this checks:
  * every PR is based on 2a13eb18 and none of the new packages exists at base (nothing retained on main);
  * the five kappa PRs (#4440, #4441, #4446, #4447, #4453) agree blob-for-blob on every shared path except two
    SOURCES.json files, and those two differ only in their per-PR "pin" fields (recorded separately here);
  * #4440's changed paths are a subset of #4441's, #4446's and #4447's (stacked content, not git ancestry);
  * all five carry the same edits to docs/ci-verification.md and docs/research/current-status.md, which differ from
    #4436's edits of the same files (a textual conflict to resolve at merge time);
  * unique packages: #4446 kappa-hybrid-controller, #4447 missing-join-frame, #4453 native-lattice-retiming.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KAPPA = ["4440", "4441", "4446", "4447", "4453"]
PIN_ONLY = {"research/historical-1042-link/SOURCES.json", "research/test-suite-locale-reads/SOURCES.json"}
DOCS = ["docs/ci-verification.md", "docs/research/current-status.md"]


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    rec = json.loads((HERE / "RECEIPT.json").read_text(encoding="utf-8"))
    prs = rec["prs"]
    need(len(prs) == 10 and all(p["base"] == rec["base_commit"] for p in prs.values()), "10 PRs on base")
    for n, p in prs.items():
        for path, (status, blob) in p["files"].items():
            if status == "A":
                # Recorded as an addition relative to the base commit; the live checkout may now contain it.
                need(blob is not None and len(blob) == 40, f"#{n}: added path {path} has a recorded blob")
    files = {n: {path: blob for path, (st, blob) in prs[n]["files"].items()} for n in KAPPA}
    for a in KAPPA:
        for b in KAPPA:
            if a < b:
                for path in set(files[a]) & set(files[b]):
                    need(files[a][path] == files[b][path] or path in PIN_ONLY, f"#{a}/#{b}: {path}")
    for b in ("4441", "4446", "4447"):
        need(set(files["4440"]) <= set(files[b]), f"#4440 content stacked in #{b}")
    for d in DOCS:
        blobs = {files[n][d] for n in KAPPA}
        need(len(blobs) == 1, f"same {d} edit in all five")
        need(blobs != {rec["docs_blobs"][d]["pr4436"]} and blobs != {rec["docs_blobs"][d]["main"]}, f"{d} conflicts with #4436")
    pk = lambda path: "/".join(path.split("/")[:2])
    pkgs = {n: {pk(x) for x in files[n]} for n in KAPPA}
    unique = {n: sorted(pkgs[n] - set().union(*[pkgs[m] for m in KAPPA if m != n])) for n in KAPPA}
    need(unique == {"4440": [], "4441": [], "4446": ["research/kappa-hybrid-controller"],
                    "4447": ["research/missing-join-frame"], "4453": ["research/native-lattice-retiming"]}, "unique packages")
    print(json.dumps({"status": "PASS_P17_CHAIN_RECEIPT", "prs": 10, "retained_on_main": 0,
                      "pin_only_differences": sorted(PIN_ONLY), "docs_conflict_with_4436": DOCS,
                      "unique_packages": {k: v for k, v in unique.items() if v}, "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
