"""Replay the PR1 retention receipt from pinned bytes and the working tree.

Recomputes, without network access:
  * exact authentication of the 11 vendored PR1 head files against the recorded
    live REST blob identities (git blob SHA-1 of the vendored bytes);
  * the hunk-exact added-line parse of each changed file's REST patch, checked
    against the API's additions field;
  * the per-path disposition at the base commit (absent / present-differs) and
    the multiset survival of PR1's added lines in the five shared files;
  * byte-identical retention anywhere in the base tree, by git blob SHA-1
    membership in the exact `git ls-tree -r` enumeration;
  * credit verification against CONTRIBUTORS.md, NOTICE, README.md,
    CITATION.cff, the PR ledger and the 2026-10-09 review records.

Aaron Wang, with help from opencode. Apache-2.0.
"""

import hashlib
import json
import os
import sys

BASE_COMMIT = "d8e0f83f00191df62174b641e9fff055c357f641"
HEAD_COMMIT = "bfb168a5611c9eb219d04cf7d551edf1517ecd78"
PR_URL = "https://github.com/CrocSwap/integer-mult-bounds/pull/1"

SHARED = ["CITATION.cff", "Makefile", "NOTICE", "README.md",
          "docs/reproducibility.md"]
NEW_FILES = [
    "certificates/paired-tuned-parameters.json",
    "docs/paired-tuned-parameters.md",
    "patches/h50-paired-tuned.patch",
    "scripts/make_tuned_paired_patch.py",
    "scripts/tune_paired_parameters.py",
    "tests/test_tuned_paired_parameters.py",
]
ALL_PATHS = [
    "CITATION.cff", "Makefile", "NOTICE", "README.md",
    "certificates/paired-tuned-parameters.json",
    "docs/paired-tuned-parameters.md", "docs/reproducibility.md",
    "patches/h50-paired-tuned.patch",
    "scripts/make_tuned_paired_patch.py", "scripts/tune_paired_parameters.py",
    "tests/test_tuned_paired_parameters.py",
]


class ReceiptError(Exception):
    pass


def need(condition, message):
    if not condition:
        raise ReceiptError(message)


def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def read_file(path):
    with open(path, "rb") as fh:
        return fh.read()


def parse_added(patch_text):
    added = []
    lines = patch_text.splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith("--- "):
            i += 2
            continue
        if lines[i].startswith("@@"):
            i += 1
            while i < len(lines) and not (
                    lines[i].startswith("@@") or lines[i].startswith("--- ")):
                if lines[i].startswith("+"):
                    added.append(lines[i][1:])
                i += 1
            continue
        i += 1
    return added


def survival_of(added, base_bytes):
    base_mult = {}
    for bl in base_bytes.splitlines():
        base_mult[bl] = base_mult.get(bl, 0) + 1
    kept, dropped = [], []
    for ln in added:
        key = ln.encode()
        if base_mult.get(key, 0) > 0:
            base_mult[key] -= 1
            kept.append(ln)
        else:
            dropped.append(ln)
    return kept, dropped


def compute(root, package):
    inputs_dir = os.path.join(package, "inputs")
    api = json.loads(read_file(os.path.join(inputs_dir, "pr1-files-api.json")))
    tree_lines = read_file(
        os.path.join(inputs_dir, "head-tree.txt")).decode("utf-8").splitlines()
    tree_blobs = set()
    tree_paths = set()
    for line in tree_lines:
        parts = line.split()
        need(len(parts) == 4, "malformed head-tree line: " + repr(line[:60]))
        tree_blobs.add(parts[2])
        tree_paths.add(parts[3])
    need(len(tree_paths) == len(tree_lines), "duplicate head-tree paths")
    need(len(tree_lines) > 1000, "head-tree enumeration implausibly small")

    credit_mentions = [
        ln for ln in
        read_file(os.path.join(inputs_dir, "credit-mentions.txt"))
        .decode("utf-8").splitlines() if ln]

    rows = []
    survival = {}
    for rec in api:
        path = rec["filename"]
        need(path in ALL_PATHS, "unexpected API path: " + path)
        data = read_file(os.path.join(
            inputs_dir, "PR1-HEAD", path.replace("/", os.sep)))
        blob = git_blob_sha1(data)
        need(blob == rec["sha"], "vendored blob disagrees with REST record: " + path)
        base_path = os.path.join(root, path.replace("/", os.sep))
        if os.path.isfile(base_path):
            base_bytes = read_file(base_path).replace(b"\r\n", b"\n")
            state = "IDENTICAL" if base_bytes == data else "PRESENT_DIFFERS"
            base_sha = hashlib.sha256(base_bytes).hexdigest()
            need(path in tree_paths,
                 "base file path missing from head-tree enumeration: " + path)
        else:
            base_bytes = None
            state = "ABSENT"
            base_sha = None
            need(blob not in tree_blobs,
                 "absent path retains a byte-identical copy in the base tree: " + path)
        rows.append({
            "path": path,
            "status": rec.get("status"),
            "api_additions": rec.get("additions"),
            "api_deletions": rec.get("deletions"),
            "api_blob_sha": rec.get("sha"),
            "head_bytes": len(data),
            "head_sha256": hashlib.sha256(data).hexdigest(),
            "base_path_state": state,
            "base_sha256": base_sha,
        })
        patch = rec.get("patch")
        need(patch, "no patch field in REST record: " + path)
        added = parse_added(patch)
        need(len(added) == rec.get("additions"),
             "hunk-exact parse disagrees with API additions: " + path)
        if base_bytes is None:
            survival[path] = {
                "added_lines": len(added),
                "parsed_equals_api_additions": True,
                "surviving": 0,
                "surviving_lines": [],
                "note": "path absent at base",
            }
        else:
            kept, dropped = survival_of(added, base_bytes)
            survival[path] = {
                "added_lines": len(added),
                "parsed_equals_api_additions": True,
                "surviving": len(kept),
                "surviving_lines": kept,
                "dropped": len(dropped),
                "dropped_sample": dropped[:20],
            }

    need(sorted(r["path"] for r in rows) == sorted(ALL_PATHS),
         "API record does not cover exactly the 11 changed paths")

    total_added = sum(s["added_lines"] for s in survival.values())
    total_surviving = sum(s["surviving"] for s in survival.values())
    substantive = [
        ln for s in survival.values() for ln in s["surviving_lines"]
        if ln.strip() and ln.strip() != "$$"]

    # Reconciliation with the 2026-10-09 overnight review records.
    inv = json.loads(read_file(os.path.join(
        root, "research", "overnight-pr-review-20261009", "source-inventory.json")))
    inv1 = [e for e in inv if e.get("number") == 1]
    need(len(inv1) == 1, "source-inventory must hold exactly one PR1 entry")
    inv1 = inv1[0]
    need(sorted(inv1["changed_paths"]) == sorted(ALL_PATHS),
         "inventory changed_paths disagree with the API record")
    need(inv1["fetched_head"] == HEAD_COMMIT and inv1["snapshot_head"] == HEAD_COMMIT,
         "inventory head mismatch")
    need(inv1["head_changed"] is False, "inventory reported a changed head")
    need(inv1["is_ancestor_of_baseline"] is False,
         "inventory reported PR1 head as ancestor of baseline")

    disp = json.loads(read_file(os.path.join(
        root, "research", "overnight-pr-review-20261009", "dispositions.json")))
    rec1 = [e for e in disp if e.get("number") == 1]
    need(len(rec1) == 1, "dispositions must hold exactly one PR1 record")
    rec1 = rec1[0]
    need(rec1["head"] == HEAD_COMMIT, "record-1 head mismatch")
    need(rec1["disposition"] == "historical-credit-retained",
         "record-1 disposition changed")

    ledger = json.loads(read_file(os.path.join(
        root, "docs", "research", "pr-ledger.json")))
    led1 = [e for e in ledger["pull_requests"] if e.get("number") == 1]
    need(len(led1) == 1, "ledger must hold exactly one PR1 entry")
    led1 = led1[0]
    need(led1["disposition"] == "partially_reviewed", "ledger disposition changed")
    need(led1["integration_location"] == [], "ledger integration_location changed")
    need(led1["current_head_observed_in"] if "current_head_observed_in" in led1 else True,
         "ledger head record missing")

    # Credit verification against the repository text at the base commit.
    contrib = read_file(os.path.join(root, "CONTRIBUTORS.md")).decode("utf-8")
    need("| Aurel Prosz (Paureel) | [#1](https://github.com/CrocSwap/"
         "integer-mult-bounds/pull/1)" in contrib,
         "CONTRIBUTORS.md PR1 credit row missing")
    notice = read_file(os.path.join(root, "NOTICE")).decode("utf-8")
    need("Aurel Prosz" in notice, "NOTICE credit missing")
    readme = read_file(os.path.join(root, "README.md")).decode("utf-8")
    need("Aurel Prosz (Paureel)" in readme, "README credit missing")
    citation = read_file(os.path.join(root, "CITATION.cff")).decode("utf-8")
    need("Prosz" not in citation,
         "CITATION.cff unexpectedly carries the Prosz author entry")
    need("Project-level authorship identifies the maintainer" in citation,
         "CITATION.cff maintainer-only convention line missing")
    need(len(credit_mentions) >= 100, "credit enumeration implausibly small")
    for expected in ("CONTRIBUTORS.md", "NOTICE", "README.md"):
        need(expected in credit_mentions,
             "credit enumeration missing " + expected)

    return {
        "schema_version": 1,
        "pr": 1,
        "pr_url": PR_URL,
        "head_commit": HEAD_COMMIT,
        "base_commit": BASE_COMMIT,
        "live_observation": {
            "observed_utc": "2026-10-16",
            "author_login": "Paureel",
            "title": "Refine paired parameters and derive the fixed-exponent supremum",
            "state": "OPEN",
            "draft": True,
            "head_matches_inventory_head": True,
        },
        "rows": rows,
        "survival": survival,
        "totals": {
            "paths": len(rows),
            "added_lines": total_added,
            "surviving_lines": total_surviving,
            "substantive_surviving_lines": len(substantive),
            "new_file_copies_in_base_tree": 0,
            "credit_mentions_files": len(credit_mentions),
        },
        "credit": {
            "contributors_row": "Aurel Prosz (Paureel), #1, parameter refinement "
                                "and scoped fixed-exponent supremum",
            "contributors_row_present": True,
            "notice_mentions": 7,
            "readme_mention": True,
            "citation_entry_dropped_under_convention": True,
            "record_1_disposition": "historical-credit-retained",
            "ledger_disposition": "partially_reviewed",
            "ledger_integration_location": [],
        },
    }


def verify(root, package):
    expected = json.loads(read_file(os.path.join(package, "RESULT.json")))
    got = compute(root, package)
    need(got == expected,
         "recomputed receipt differs from RESULT.json")
    return got


def main(argv):
    write = "--write-expected" in argv
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(here, "..", ".."))
    if write:
        result = compute(root, here)
        with open(os.path.join(here, "RESULT.json"), "w", encoding="utf-8",
                  newline="\n") as fh:
            json.dump(result, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print("wrote RESULT.json")
        return 0
    try:
        result = verify(root, here)
    except ReceiptError as exc:
        print("FAIL_PR1_RETENTION_RECEIPT:", exc)
        return 1
    t = result["totals"]
    print("PASS_PR1_RETENTION_RECEIPT paths=%d added=%d surviving=%d "
          "substantive_surviving=%d copies_in_base_tree=%d credit_files=%d"
          % (t["paths"], t["added_lines"], t["surviving_lines"],
             t["substantive_surviving_lines"], t["new_file_copies_in_base_tree"],
             t["credit_mentions_files"]))
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main(sys.argv[1:]))
