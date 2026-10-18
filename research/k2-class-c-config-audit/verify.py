#!/usr/bin/env python3
"""Audit of the class-C 4-flat covering-config census (Discussion #2954 help package).

Scope: audits only the PUBLISHED TABLES and the PUBLISHED g-table / pair-count
table. It does NOT touch the E8/P112 geometry, does NOT verify the kill
criterion (Lemma B), and does NOT verify relative root counting (RRC, which the
help post itself marks as under audit). No kappa, decoder, supplier or
exclusion claim is made or implied.

Inputs (pinned, read-only, package-local copies of the upstream help package):
  inputs/rows70.csv, inputs/rows17.csv, from DreamingOfClouds/integer-mult-bounds
  branch research/k2-class-c-help, path research/k2-class-c-help/, help-package
  source commit 1b25759bff5486293a9083ebbe0097b5f6642e08.
  g-table and pair counts are quoted from the same help post / README.

Outputs: printed report + RESULT.json. Exit status 0 iff every check passed and
every rejecting control was rejected.

muatfannajm-dot, with substantial OpenCode (Space Bunny Free) assistance.
Apache-2.0. Credit DreamingOfClouds for the audited help package.
"""

import csv
import json
import os
import sys
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))

# sha256 of the pinned inputs, checked on every run (byte-equality receipt for
# inputs that are not Git objects in this repository).
INPUT_SHA256 = {
    "rows70.csv": "c0eb6bb88498bf39a8b2020b1d0d600181f6e13eb9dd6a6e5f90794f0895754a",
    "rows17.csv": "9ebe7fc1ecd74148e7bdefa1f6bb2ed00551884b1a4a6558d7f129f7eef4efd5",
}

# Published in Discussion #2954: "a weight-w piece has supp in a w-dim flat, so
# |Lambda(V)| <= g(w), g(1..7) = 1,2,4,8,12,20,36".
G = {1: 1, 2: 2, 3: 4, 4: 8, 5: 12, 6: 20, 7: 36}

# Published in the same post: "Lemma B needs sum g <= 52".
SUM_G_BOUND = 52

# Published in the help README, verbatim pair counts (scientific base
# 1b25759bff5486293a9083ebbe0097b5f6642e08). Only these exact strings are used
# for the savings figure; anything else is reported as unstated.
README_PAIRS = {
    "6543": 2.6e7,   # (6,5,4,3) a=3 b=6 c=4 d=5
    "6544": 1.1e8,   # (6,5,4,4) a=4 b=6
    "6554": 1.1e8,   # (6,5,5,4) a=4 b=6
    "5554": 3.3e8,   # (5,5,5,4) a=5 b=5
    "5555": 3.3e8,   # (5,5,5,5) a=5 b=5
}


def parse_config(tok):
    """'6554' -> (6,5,5,4); raise on malformed input."""
    if not tok or not tok.isdigit() or len(tok) != 4:
        raise ValueError("malformed config token %r" % (tok,))
    dims = tuple(int(c) for c in tok)
    if list(dims) != sorted(dims, reverse=True):
        raise ValueError("config %r is not in non-increasing order" % (tok,))
    if any(d not in G for d in dims):
        raise ValueError("config %r uses a dimension outside g(1..7)" % (tok,))
    return dims


def config_cost(tok):
    """X = sum of g over the four flat dimensions."""
    return sum(G[d] for d in parse_config(tok))


def load_rows(path):
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for rec in csv.DictReader(fh):
            cfgs = (rec.get("covering_4flat_configs") or "").split()
            out.append(
                {
                    "row_idx": int(rec["row_idx"]),
                    "d": int(rec["d"]),
                    "s": int(rec["s"]),
                    "e": int(rec["e"]),
                    "weights": json.loads(rec["weights"]),
                    "rrc_status": (rec.get("rrc_status") or "").strip(),
                    "configs": cfgs,
                }
            )
    return out


def run_checks(rows70, rows17):
    """Return (checks, derived). Split out so mutants can be run through the
    identical check logic (rejecting controls)."""
    checks = []

    def check(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": detail})
        return ok

    import hashlib
    for fname, want in sorted(INPUT_SHA256.items()):
        with open(os.path.join(HERE, "inputs", fname), "rb") as fh:
            got = hashlib.sha256(fh.read()).hexdigest()
        check("input %s matches its pinned sha256" % fname, got == want,
              "" if got == want else "got %s want %s" % (got, want))

    all_cfgs = sorted({c for r in rows70 for c in r["configs"]})
    cost = {c: config_cost(c) for c in all_cfgs}

    check("rows70 has 70 rows", len(rows70) == 70, "got %d" % len(rows70))
    check("rows17 has 17 rows", len(rows17) == 17, "got %d" % len(rows17))

    bad = {c: v for c, v in cost.items() if v > SUM_G_BOUND}
    check("all listed configs satisfy sum g <= %d" % SUM_G_BOUND,
          not bad, "violations=%s" % (bad or "none"))
    check("6554 saturates the bound exactly (sum g = 52)",
          cost.get("6554") == SUM_G_BOUND, "6554 -> %s" % cost.get("6554"))

    rrc_killed = {r["row_idx"] for r in rows70
                  if r["rrc_status"].upper().startswith("RRC-KILLED")}
    surviving = {r["row_idx"] for r in rows70} - rrc_killed
    idx17 = {r["row_idx"] for r in rows17}
    check("rows17 == rows70 minus RRC-killed rows", surviving == idx17,
          "symmetric_difference=%s" % (sorted(surviving ^ idx17) or "empty"))
    check("RRC kills 53 of 70 rows (as published)",
          len(rrc_killed) == 53, "killed=%d" % len(rrc_killed))

    by70 = {r["row_idx"]: r for r in rows70}
    mism = []
    for r in rows17:
        b = by70.get(r["row_idx"])
        if b is None:
            mism.append((r["row_idx"], "absent from rows70"))
            continue
        for k in ("d", "s", "e", "weights", "configs"):
            if r[k] != b[k]:
                mism.append((r["row_idx"], k))
    check("rows17 fields agree with rows70 for every shared row",
          not mism, "mismatches=%s" % (mism or "none"))

    return checks, all_cfgs, cost, rrc_killed


def self_test(rows70, rows17):
    """Rejecting controls: each mutant must make at least one check FAIL."""
    def clone(rows):
        return [dict(r) for r in rows]

    mutants = []

    # M1: inject a config that violates the sum-g <= 52 admissibility bound
    #     (6,5,5,5) -> 20+12+12+12 = 56 > 52.
    m = clone(rows70)
    for r in m:
        if r["row_idx"] == 7:
            r["configs"] = sorted(r["configs"] + ["6555"])
    mutants.append(("inject inadmissible config 6555 (sum g = 56)", m, rows17))

    # M2: drop a surviving row from rows17.
    m17 = [r for r in clone(rows17) if r["row_idx"] != 62]
    mutants.append(("drop row 62 from rows17", rows70, m17))

    # M3: flip one row's RRC status so the kill count is no longer 53.
    m = clone(rows70)
    for r in m:
        if r["row_idx"] == 3:
            r["rrc_status"] = "open"
    mutants.append(("flip row 3 RRC status (kill count 53 -> 52)", m, rows17))

    # M4: silently desynchronise rows17 configs from rows70 for one row.
    m17 = clone(rows17)
    for r in m17:
        if r["row_idx"] == 35:
            r["configs"] = ["5555", "6544"]
    mutants.append(("edit row 35 configs in rows17 only", rows70, m17))

    out = []
    for name, a, b in mutants:
        checks, _, _, _ = run_checks(a, b)
        failed = [c["name"] for c in checks if not c["ok"]]
        out.append({"mutant": name, "rejected": bool(failed),
                    "failed_checks": failed})
        print("[%s] control: %s%s"
              % ("PASS" if failed else "FAIL", name,
                 ("  -> " + "; ".join(failed)) if failed else "  -> NOT REJECTED"))
    return out


def main():
    rows70 = load_rows(os.path.join(HERE, "inputs", "rows70.csv"))
    rows17 = load_rows(os.path.join(HERE, "inputs", "rows17.csv"))

    checks, all_cfgs, cost, rrc_killed = run_checks(rows70, rows17)
    surviving = {r["row_idx"] for r in rows70} - rrc_killed

    def ok(name):
        return next(c["ok"] for c in checks if c["name"] == name)

    # ---- E. minimal config set covering the 17 surviving rows ---------
    need = [r["row_idx"] for r in rows17]
    universe = sorted({c for r in rows17 for c in r["configs"]})
    cover_of = {
        c: {r["row_idx"] for r in rows17 if c in r["configs"]} for c in universe
    }
    uncoverable = [i for i in need if not any(i in cover_of[c] for c in universe)]

    def min_cover(targets, pool):
        """Exact minimum set cover by brute force. Callers must pass only
        targets that some pool member actually covers."""
        targets = set(targets)
        if not targets:
            return []
        best = None
        for k in range(1, len(pool) + 1):
            for combo in combinations(sorted(pool), k):
                got = set()
                for c in combo:
                    got |= cover_of[c]
                if targets <= got:
                    best = list(combo)
                    break
            if best:
                break
        return best or []

    minimal = min_cover([i for i in need if i not in uncoverable], universe)
    redundant = [c for c in universe if c not in minimal]

    # ---- F. coverage of all 70 rows by the minimal set -----------------
    allrows = [r["row_idx"] for r in rows70]
    uncoverable70 = [i for i in allrows if not any(i in cover_of[c] for c in universe)]
    minimal70 = min_cover([i for i in allrows if i not in uncoverable70], universe)
    redundant70 = [c for c in universe if c not in minimal70]

    # ---- G. which configs are reachable only from RRC-killed rows -----
    killed_only_configs = sorted(
        {
            c
            for r in rows70
            if r["row_idx"] in rrc_killed
            for c in r["configs"]
        }
        - set(universe)
    )

    # ---- H. rows with no covering config at all ------------------------
    none70 = sorted(r["row_idx"] for r in rows70 if not r["configs"])
    none17 = sorted(r["row_idx"] for r in rows17 if not r["configs"])

    # ---- I. cost of the dropped configs (README numbers only) ----------
    stated_min = {c: README_PAIRS[c] for c in minimal if c in README_PAIRS}
    stated_redundant = {c: README_PAIRS[c] for c in redundant if c in README_PAIRS}
    stated_redundant70 = {
        c: README_PAIRS[c] for c in redundant70 if c in README_PAIRS
    }
    saving_pairs = sum(stated_redundant.values())
    saving_pairs70 = sum(stated_redundant70.values())
    unstated = [c for c in universe if c not in README_PAIRS]

    controls = self_test(rows70, rows17)
    all_controls_rejected = all(c["rejected"] for c in controls)

    result = {
        "scope": (
            "Audit of the published class-C 4-flat covering-config census only. "
            "No E8/P112 geometry re-derived; no verification of kill criterion "
            "Lemma B; no verification of relative root counting (RRC). No kappa, "
            "decoder, supplier or residue-exclusion claim."
        ),
        "not_verified": [
            "Completeness of the config list: only admissibility (sum g <= 52) of "
            "each listed config is checked. Whether the author's piece-packing "
            "rule admits further configs is NOT checked; that rule is only "
            "sketched in Discussion #2954.",
            "The kill criterion itself (Lemma B) and span_H <= d-1.",
            "RRC (relative root counting), which the help post marks under audit; "
            "the 53-of-70 kill count is taken as given and only checked for "
            "internal consistency between the two CSVs.",
            "Pair counts and CPU-hour ETAs are the README's published figures, "
            "reused verbatim, not re-measured.",
        ],
        "checks": checks,
        "all_checks_passed": all(c["ok"] for c in checks),
        "controls": controls,
        "all_controls_rejected": all_controls_rejected,
        "g_table": {str(k): v for k, v in G.items()},
        "sum_g_bound": SUM_G_BOUND,
        "configs_listed_anywhere": all_cfgs,
        "config_costs": cost,
        "rrc_killed_count": len(rrc_killed),
        "surviving_row_indices": sorted(surviving),
        "configs_appearing_in_17_rows": universe,
        "cover_of_config": {c: sorted(cover_of[c]) for c in universe},
        "rows17_with_no_config": none17,
        "rows70_with_no_config": none70,
        "rows_not_coverable_by_any_listed_config": uncoverable,
        "minimal_config_set_for_17_rows": minimal,
        "redundant_configs_for_17_rows": redundant,
        "minimal_config_set_for_70_rows": minimal70,
        "redundant_configs_for_70_rows": redundant70,
        "rows70_coverable_by_some_listed_config": sorted(
            i for i in allrows if i not in uncoverable70
        ),
        "rows70_not_coverable_by_any_listed_config": uncoverable70,
        "configs_only_on_rrc_killed_rows": killed_only_configs,
        "readme_stated_pairs": README_PAIRS,
        "stated_pairs_for_minimal_17": stated_min,
        "stated_pairs_dropped_for_17": stated_redundant,
        "stated_pairs_dropped_for_70": stated_redundant70,
        "pairs_saved_by_minimal_set_17": saving_pairs,
        "pairs_saved_by_minimal_set_70": saving_pairs70,
        "configs_with_no_stated_pair_count": unstated,
    }

    # ---- report --------------------------------------------------------
    print("=" * 72)
    print("class-C 4-flat covering-config census audit (Discussion #2954)")
    print("=" * 72)
    for c in checks:
        print("[%s] %s%s" % ("PASS" if c["ok"] else "FAIL", c["name"],
                             ("  -- " + c["detail"]) if c["detail"] else ""))
    print("-" * 72)
    print("sum g per listed config (bound %d):" % SUM_G_BOUND)
    for c in all_cfgs:
        print("   %s -> %2d   %s" % (c, cost[c],
              "  [README pairs %g]" % README_PAIRS[c] if c in README_PAIRS
              else "  [pair count NOT stated in README]"))
    print("-" * 72)
    print("configs appearing on the 17 surviving rows:", universe)
    print("rows among the 17 with NO config at all   :", none17)
    print("rows among the 70 with NO config at all   :", none70)
    print("cover the 16 rows that have a config    :", minimal)
    print("configs redundant for those 16 rows      :", redundant)
    print("cover all 64 rows that have a config    :", minimal70)
    print("configs redundant for all 70 rows       :", redundant70)
    print("configs only ever seen on RRC-killed rows :", killed_only_configs)
    print("-" * 72)
    print("stated pair counts dropped for the 17-row campaign: %g pairs"
          % saving_pairs)
    print("stated pair counts dropped for the 70-row campaign: %g pairs"
          % saving_pairs70)
    print("configs with NO stated pair count (excluded from the above):", unstated)
    print("-" * 72)
    print("RESULT: %s ; controls all rejected: %s"
          % ("all checks passed" if result["all_checks_passed"]
             else "SOME CHECKS FAILED", all_controls_rejected))

    # newline="\n" so the emitted bytes match the repository's canonical
    # LF index form (*.gitattributes: * text=auto eol=lf); otherwise a Windows
    # run would write CRLF and `check_research_commit.py` would report a
    # working/commit byte difference with an empty `git diff`.
    with open(os.path.join(HERE, "RESULT.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(result, fh, indent=2, sort_keys=True)
        fh.write("\n")
    if result["all_checks_passed"] and all_controls_rejected:
        print("PASS_K2_CLASS_C_CONFIG_AUDIT")
    return 0 if (result["all_checks_passed"] and all_controls_rejected) else 1


if __name__ == "__main__":
    sys.exit(main())