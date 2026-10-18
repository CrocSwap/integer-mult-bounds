"""Regenerate a bounded source/retention receipt from immutable Git objects.

Reads only; it neither fetches sources nor imports/runs their research programs.
This checks source inventory and reported fields, not solver correctness.
"""

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
BASE = "b4560d9e7216f72b73c5aa940ac099c05e33ccf9"
REFRESH = "1884c509efc004524786e9b7cfcc4aca572316d5"
P1957 = "e6a4d34874bb1aeba192c62629ebb633a6b5c424"
OLD2142 = "0c5516bf5bfb5c9c4d09446d3b21028032060fec"
P2142 = "5f2f608451252f3330e0d0d5fc7bca63be9d0400"
LATER = "23b9ce546f6978bc017d2a970a7fc2b1f96ef6b0"
A = "research/t74-k554-local-exhaustion/"
B = "research/t74-split-key-kernel-search/"
C = "research/t74-local-word-rounds4-7/r6/agents/I-resolve/"
TARGETS = ("B822", "B840", "B858", "B876")


def git(*args):
    proc = subprocess.run(
        ["git", "-C", str(REPO), "--no-replace-objects", *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if proc.returncode:
        raise RuntimeError("Required Git object unavailable; see README fetch commands.\n"
                           + proc.stderr.decode("utf-8", errors="replace"))
    return proc.stdout


def tree(commit, prefix=""):
    rows = {}
    for entry in git("ls-tree", "-rz", commit, "--", prefix or ".").split(b"\0"):
        if not entry:
            continue
        info, path = entry.split(b"\t", 1)
        mode, kind, oid = info.decode("ascii").split()
        rows[path.decode("utf-8")] = {"mode": mode, "kind": kind, "oid": oid}
    return rows


def comparison(source, target):
    exact, changed, absent = [], [], []
    for path, entry in source.items():
        (absent if path not in target else
         exact if target[path] == entry else changed).append(path)
    return {"exact_paths": exact, "changed_paths": changed, "absent_paths": absent}


def generate():
    for commit in (BASE, REFRESH, P1957, OLD2142, P2142, LATER):
        if git("rev-parse", commit + "^{commit}").decode().strip() != commit:
            raise ValueError("commit identity mismatch")
    base = tree(BASE)
    refreshed = tree(REFRESH)
    sources = {}
    bound_files = []

    def read(commit, path):
        payload = git("show", commit + ":" + path)
        oid = git("rev-parse", commit + ":" + path).decode().strip()
        computed = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
        if oid != computed:
            raise ValueError("Git blob hash mismatch: " + path)
        bound_files.append({"commit": commit, "path": path, "git_blob": oid,
                            "sha256": hashlib.sha256(payload).hexdigest(), "bytes": len(payload)})
        return payload

    for name, commit, prefix in (("pr1957", P1957, A), ("pr2142", P2142, B),
                                 ("later_I_resolve", LATER, C)):
        inventory = tree(commit, prefix)
        if not inventory:
            raise ValueError("empty source inventory")
        same_elsewhere = []
        for path, entry in inventory.items():
            paths = [p for p, value in base.items() if value == entry and p != path]
            if paths:
                same_elsewhere.append({"source_path": path, "base_paths": paths})
        sources[name] = {"commit": commit, "prefix": prefix,
                         "subtree": git("rev-parse", commit + ":" + prefix.rstrip("/")).decode().strip(),
                         "file_count": len(inventory), "inventory": inventory,
                         "base_path_comparison": comparison(inventory, base),
                         "identical_mode_and_blob_elsewhere_in_base": same_elsewhere}

    dispositions = json.loads(read(BASE, "research/community-efficient1000-audit/DISPOSITIONS.json"))
    disposition = next(x for x in dispositions["pull_requests"] if x["number"] == 1957)
    # Keep the complete existing disposition rather than silently selecting a
    # favorable subset of its pending-review fields.
    read(BASE, "research/community-efficient1000-audit/checks/check-1957.json")
    read(BASE, "research/community-efficient1000-audit/packets/1957.json")
    for path in (A + "README.md", A + "tools/costorc.py", A + "tools/akernel.py", B + "README.md"):
        read(P1957 if path.startswith(A) else P2142, path)
    old = {}
    for target in TARGETS:
        record = json.loads(read(P2142, B + "data/strict/sk-" + target + ".json"))
        old[target] = {key: record[key] for key in ("ddel", "shape", "ncand", "res")}
    evidence = json.loads(read(LATER, C + "EVIDENCE.json"))
    read(LATER, C + "FINDINGS.md")
    read(LATER, "research/t74-local-word-rounds4-7/INPUTS.json")
    corrected = {}
    for target in TARGETS:
        record = evidence["targets"][target]
        corrected[target] = {
            "ddel": record["ddel"], "budget": record["budget"],
            "sentinel": {key: record["sentinel"][key] for key in
                         ("n", "within_budget", "provably_over_budget", "statuses")},
            "reported_variants": {
                variant: {key: record[variant][key] for key in
                          ("status", "iterations", "final_rows", "final_cand", "excluded", "verify")}
                for variant in ("D", "C")},
        }
    return {
        "schema": 1,
        "coverage": "Exact-path and exact-mode/blob retention; source-reported solver fields only. No solver replay or semantic incorporation inference.",
        "base": BASE, "sources": sources,
        "newer_main_compatibility": {
            "commit": REFRESH,
            "source_path_and_blob_comparisons": {
                name: {"original_paths_present": sorted(set(source["inventory"]) & set(refreshed)),
                       "exact_mode_blob_matches_anywhere": [path for path, entry in source["inventory"].items()
                                                           if entry in refreshed.values()]}
                for name, source in sources.items()},
            "pr1957_disposition_file_unchanged": git("show", BASE + ":research/community-efficient1000-audit/DISPOSITIONS.json") == git("show", REFRESH + ":research/community-efficient1000-audit/DISPOSITIONS.json"),
        },
        "pr1957_disposition_at_base": disposition,
        "pr1957_tree_equal_in_pr2142": tree(P1957, A) == tree(P2142, A),
        "pr2142_changed_head": {"old": OLD2142, "new": P2142,
                               "pr1957_tree_equal": tree(OLD2142, A) == tree(P2142, A),
                               "split_key_tree_equal": tree(OLD2142, B) == tree(P2142, B)},
        "pr2142_reported_shape_records": old,
        "later_reported_model": evidence["model"],
        "later_reported_variants": evidence["variants"],
        "later_reported_targets": corrected,
        "later_reported_no_cost_diagnostic": evidence["B822_variant_A"],
        "bound_files": bound_files,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="create RECEIPT.json; refuses overwrite")
    args = parser.parse_args()
    receipt = HERE / "RECEIPT.json"
    if args.write and receipt.exists():
        raise SystemExit("Refusing to overwrite the frozen receipt")
    actual = generate()
    if args.write:
        with receipt.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(json.dumps(actual, indent=2, ensure_ascii=False) + "\n")
    elif json.dumps(json.loads(receipt.read_text(encoding="utf-8")), sort_keys=True, allow_nan=False) != json.dumps(actual, sort_keys=True, allow_nan=False):
        raise SystemExit("FAIL_T74_LOCAL_SEARCH_RETENTION: receipt differs from pinned source objects")
    print("PASS_T74_LOCAL_SEARCH_RETENTION source_files="
          + str(sum(x["file_count"] for x in actual["sources"].values()))
          + " targets=4 solver_replay=not_run")


if __name__ == "__main__":
    main()
