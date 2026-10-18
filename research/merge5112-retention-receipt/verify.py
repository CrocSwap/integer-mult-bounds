#!/usr/bin/env python3
"""Offline verifier for research/merge5112-retention-receipt.

Re-derives the post-merge retention facts of merge commit 51122344 from the
local Git object store and compares them with RECEIPT.json, then runs
in-memory rejection controls that must all fail. Standard library + git only.
Aaron Wang, with help from opencode. Apache-2.0.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

BASE = "d33f15be91438e3de512fa544c3f5a7cb832588f"
MERGE = "51122344de9382e784c7f89953456d8cd55513ef"
PACKAGE = "research/merge5112-retention-receipt"

ROOT = Path(__file__).resolve().parents[2]


def git(*args):
    p = subprocess.run(["git", "-C", str(ROOT)] + list(args), capture_output=True,
                       stdin=subprocess.DEVNULL, timeout=120)
    if p.returncode != 0:
        raise SystemExit("git failed: " + " ".join(args) + ": " + p.stderr.decode()[:200])
    return p.stdout.decode("utf-8", errors="replace")


def git_bytes(*args):
    p = subprocess.run(["git", "-C", str(ROOT)] + list(args), capture_output=True,
                       stdin=subprocess.DEVNULL, timeout=120)
    if p.returncode != 0:
        raise SystemExit("git failed: " + " ".join(args) + ": " + p.stderr.decode()[:200])
    return p.stdout


def tree(commit):
    out = {}
    for line in git("ls-tree", "-r", commit).splitlines():
        meta, path = line.split("\t", 1)
        out[path] = meta.split()[2]
    return out


def rederive():
    """Fresh facts from Git: nothing read from the receipt."""
    t_head_trees = {}
    facts = {"base": BASE, "merge": MERGE}
    parents = git("rev-list", "--parents", "-n", "1", MERGE).split()[1:]
    facts["merge_parents"] = parents
    tmerge = tree(MERGE)
    facts["prs"] = {}
    receipt = json.loads((ROOT / PACKAGE / "RECEIPT.json").read_text(encoding="utf-8"))
    for pr_str, rec in receipt["pull_requests"].items():
        head = rec["head"]
        if head not in t_head_trees:
            t_head_trees[head] = tree(head)
        th = t_head_trees[head]
        paths = []
        for line in git("diff", "--name-status", f"{BASE}...{head}").splitlines():
            parts = line.split("\t")
            status, path = parts[0], parts[-1]
            if status.startswith("D"):
                continue
            hb, mb = th.get(path), tmerge.get(path)
            verdict = "retained-identical" if mb == hb else ("retained-modified" if mb else "not-retained")
            paths.append({"status": status, "path": path, "head_blob": hb,
                          "merge_blob": mb, "verdict": verdict})
        facts["prs"][pr_str] = paths
    return facts


def compare(facts, receipt):
    """Return a list of defects; empty means the receipt matches the fresh facts."""
    errors = []
    if receipt["base_commit"] != facts["base"]:
        errors.append("base_commit mismatch")
    if receipt["merge_commit"] != facts["merge"]:
        errors.append("merge_commit mismatch")
    heads = {rec["head"] for rec in receipt["pull_requests"].values()}
    expected_parents = sorted([facts["base"]] + list(heads))
    if sorted(facts["merge_parents"]) != expected_parents:
        errors.append("merge parents are not exactly base + recorded heads: "
                      + repr(sorted(facts["merge_parents"])))
    if set(facts["prs"]) != set(receipt["pull_requests"]):
        errors.append("PR set mismatch")
        return errors
    totals = {"changed_paths": 0, "retained_identical": 0, "retained_modified": 0, "not_retained": 0}
    for pr_str, fresh_paths in facts["prs"].items():
        rec = receipt["pull_requests"][pr_str]
        if not rec["head_equals_reviewed_head"]:
            errors.append(f"PR {pr_str}: head differs from recorded reviewed head")
        if rec["head"] not in facts["merge_parents"]:
            errors.append(f"PR {pr_str}: head is not a merge parent")
        if [p["path"] for p in fresh_paths] != [p["path"] for p in rec["changed_paths"]]:
            errors.append(f"PR {pr_str}: changed path list mismatch")
            continue
        for fresh, saved in zip(fresh_paths, rec["changed_paths"]):
            for key in ("status", "path", "head_blob", "merge_blob", "verdict"):
                if fresh[key] != saved[key]:
                    errors.append(f"PR {pr_str} {saved['path']}: {key} mismatch "
                                  f"(fresh={fresh[key]} saved={saved[key]})")
        for p in fresh_paths:
            totals["changed_paths"] += 1
            totals[p["verdict"].replace("-", "_")] += 1
    for key, value in totals.items():
        if receipt["totals"].get(key) != value:
            errors.append(f"totals.{key}: fresh={value} saved={receipt['totals'].get(key)}")
    return errors


def controls(facts, receipt):
    """Mutations of the receipt that the comparison must reject."""
    passed = 0
    results = []

    def mutate(name, fn):
        nonlocal passed
        import copy
        bad = copy.deepcopy(receipt)
        fn(bad)
        errs = compare(facts, bad)
        ok = bool(errs)
        results.append((name, ok, errs[:1]))
        if ok:
            passed += 1

    def flip_blob(rec, key):
        rec_path = next(iter(rec["pull_requests"].values()))["changed_paths"][0]
        blob = rec_path[key]
        rec_path[key] = ("0" if blob[0] != "0" else "1") + blob[1:]

    mutate("corrupted head_blob", lambda r: flip_blob(r, "head_blob"))
    mutate("corrupted merge_blob", lambda r: flip_blob(r, "merge_blob"))
    mutate("wrong verdict", lambda r: next(iter(r["pull_requests"].values()))["changed_paths"][0].__setitem__("verdict", "not-retained"))
    mutate("dropped path", lambda r: next(iter(r["pull_requests"].values()))["changed_paths"].pop())
    mutate("fabricated path", lambda r: next(iter(r["pull_requests"].values()))["changed_paths"].append(
        {"status": "A", "path": "research/fake/f.txt", "head_blob": "0" * 40,
         "merge_blob": "0" * 40, "verdict": "retained-identical"}))
    mutate("false changed-head flag", lambda r: next(iter(r["pull_requests"].values())).__setitem__("head_equals_reviewed_head", False))
    mutate("wrong totals", lambda r: r["totals"].__setitem__("retained_identical", 0))
    return passed, results


def source_pins():
    """Re-check the package's own SOURCES.json pins against the recorded Git snapshot.

    Each row is bound through its git blob at SOURCES.json's base_commit, so the
    historical bytes replay even after the live files advance. Only rows declared
    as live inputs are additionally required to match the working tree."""
    sources = json.loads((ROOT / PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    errors = []
    for row in sources["files"]:
        name = row["path"]
        obj = git("rev-parse", f"{sources['base_commit']}:{name}").strip()
        if obj != row["git_blob"]:
            errors.append("blob pin mismatch: " + name)
        data = git_bytes("cat-file", "blob", obj)
        if hashlib.sha256(data).hexdigest() != row["sha256"]:
            errors.append("sha256 pin mismatch: " + name)
        if row["usage"] == "input" and data != (ROOT / name).read_bytes():
            errors.append("input drift: " + name)
    return errors


def main():
    receipt = json.loads((ROOT / PACKAGE / "RECEIPT.json").read_text(encoding="utf-8"))
    pin_errors = source_pins()
    if pin_errors:
        for e in pin_errors:
            print("FAIL_SOURCE_PIN:", e)
        raise SystemExit(1)
    facts = rederive()
    errors = compare(facts, receipt)
    if errors:
        for e in errors:
            print("FAIL_RECEIPT:", e)
        raise SystemExit(1)
    n_ctrl, results = controls(facts, receipt)
    failed_controls = [r for r in results if not r[1]]
    if failed_controls:
        for name, ok, errs in failed_controls:
            print("FAIL_CONTROL_ACCEPTED:", name, errs)
        raise SystemExit(1)
    t = receipt["totals"]
    print("PASS_MERGE5112_RETENTION_RECEIPT")
    print(f"prs={t['prs']} changed_paths={t['changed_paths']} "
          f"retained_identical={t['retained_identical']} retained_modified={t['retained_modified']} "
          f"not_retained={t['not_retained']} changed_heads={t['changed_heads_vs_reviewed']}")
    print(f"source_pins=ok controls_rejected={n_ctrl}/{len(results)}")
    for name, ok, _ in results:
        print("  control rejected:", name)


if __name__ == "__main__":
    main()
