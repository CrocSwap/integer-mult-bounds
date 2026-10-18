"""Recollect source evidence for the PR1 retention receipt.

Read-only against GitHub and the local checkout. Writes:
  inputs/pr1-files-api.json  -- live REST changed-file record at the pinned head
  inputs/head-tree.txt       -- exact `git ls-tree -r` enumeration of the base tree
  inputs/credit-mentions.txt -- exact `git grep -l` enumeration of tracked files
                               mentioning Paureel / Aurel Prosz
  analysis.json              -- computed dispositions (scratch comparison output)

Aaron Wang, with help from opencode. Apache-2.0.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
BASE_COMMIT = "d8e0f83f00191df62174b641e9fff055c357f641"
HEAD_COMMIT = "bfb168a5611c9eb219d04cf7d551edf1517ecd78"
REPO = "CrocSwap/integer-mult-bounds"


def run(cmd, cwd):
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr


def git_blob_sha1(data):
    header = b"blob " + str(len(data)).encode() + b"\x00"
    return hashlib.sha1(header + data).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", default=os.path.join(HERE, "..", ".."))
    ap.add_argument("--output", default=HERE)
    args = ap.parse_args()
    workdir = os.path.abspath(args.workdir)
    outdir = os.path.abspath(args.output)
    inputs_dir = os.path.join(outdir, "inputs")
    os.makedirs(inputs_dir, exist_ok=True)

    # 1. Live REST changed-file record at the pinned head.
    rc, out, err = run(
        ["gh", "api", "repos/%s/pulls/1/files?per_page=100" % REPO], workdir)
    if rc != 0:
        raise SystemExit("gh api failed: %s" % err.decode("utf-8", "replace"))
    files_api = json.loads(out)
    with open(os.path.join(inputs_dir, "pr1-files-api.json"), "wb") as fh:
        fh.write(out)

    # 2. Exact base-tree enumeration.
    rc, out, err = run(["git", "ls-tree", "-r", BASE_COMMIT], workdir)
    if rc != 0:
        raise SystemExit("git ls-tree failed: %s" % err.decode("utf-8", "replace"))
    with open(os.path.join(inputs_dir, "head-tree.txt"), "wb") as fh:
        fh.write(out)

    # 3. Exact tracked-file credit enumeration at the working tree.
    rc, out, err = run(
        ["git", "grep", "-l", "-e", "Paureel", "-e", "Aurel Prosz"], workdir)
    if rc != 0 and rc != 1:
        raise SystemExit("git grep failed: %s" % err.decode("utf-8", "replace"))
    with open(os.path.join(inputs_dir, "credit-mentions.txt"), "wb") as fh:
        fh.write(out)

    # 4. Authenticate each vendored head file against the REST blob identity
    #    and compute the working-tree disposition.
    vendor_root = os.path.join(inputs_dir, "PR1-HEAD")
    rows = []
    for rec in files_api:
        path = rec["filename"]
        vp = os.path.join(vendor_root, path.replace("/", os.sep))
        with open(vp, "rb") as fh:
            data = fh.read()
        blob = git_blob_sha1(data)
        hp = os.path.join(workdir, path.replace("/", os.sep))
        head_state = "ABSENT"
        head_sha256 = None
        if os.path.isfile(hp):
            with open(hp, "rb") as fh:
                hdata = fh.read()
            head_sha256 = hashlib.sha256(hdata).hexdigest()
            head_state = "IDENTICAL" if hdata == data else "PRESENT_DIFFERS"
        rows.append({
            "path": path,
            "status": rec.get("status"),
            "api_additions": rec.get("additions"),
            "api_deletions": rec.get("deletions"),
            "api_blob_sha": rec.get("sha"),
            "recomputed_blob_sha": blob,
            "blob_matches_api": blob == rec.get("sha"),
            "head_bytes": len(data),
            "head_sha256": hashlib.sha256(data).hexdigest(),
            "base_path_state": head_state,
            "base_sha256": head_sha256,
        })

    # 5. Added-line survival for modified shared files. The parser is
    #    hunk-exact: it walks each file section, skips only its "--- " and
    #    "+++ " header lines, and takes exactly the "+" body lines of hunks.
    #    Self-check: parsed added count must equal the API's additions field.
    def parse_added(patch_text):
        added = []
        lines = patch_text.splitlines()
        i = 0
        while i < len(lines):
            if lines[i].startswith("--- "):
                i += 2  # skip "--- " and "+++ " headers of this file section
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

    survival = {}
    for rec in files_api:
        path = rec["filename"]
        patch = rec.get("patch")
        if not patch:
            survival[path] = {"error": "no patch field in REST record"}
            continue
        added = parse_added(patch)
        hp = os.path.join(workdir, path.replace("/", os.sep))
        if not os.path.isfile(hp):
            survival[path] = {
                "added_lines": len(added),
                "parsed_equals_api_additions": len(added) == rec.get("additions"),
                "surviving": 0,
                "note": "path absent at base"}
            continue
        with open(hp, "rb") as fh:
            base_lines = fh.read().splitlines()
        base_mult = {}
        for bl in base_lines:
            base_mult[bl] = base_mult.get(bl, 0) + 1
        kept, dropped = [], []
        for ln in added:
            key = ln.encode()
            if base_mult.get(key, 0) > 0:
                base_mult[key] -= 1
                kept.append(ln)
            else:
                dropped.append(ln)
        survival[path] = {
            "added_lines": len(added),
            "parsed_equals_api_additions": len(added) == rec.get("additions"),
            "surviving": len(kept),
            "surviving_lines": kept,
            "dropped": len(dropped),
            "dropped_sample": dropped[:20],
        }

    analysis = {
        "head_commit": HEAD_COMMIT,
        "base_commit": BASE_COMMIT,
        "rows": rows,
        "survival": survival,
    }
    with open(os.path.join(outdir, "analysis.json"), "w", encoding="utf-8",
              newline="\n") as fh:
        json.dump(analysis, fh, indent=2, sort_keys=True)
        fh.write("\n")

    for r in rows:
        print("%-45s %-16s blob_ok=%s base=%s" % (
            r["path"], r["base_path_state"], r["blob_matches_api"],
            r["base_path_state"]))
    for p, s in survival.items():
        print("survival %-45s %s" % (p, json.dumps(s)[:120]))
    print("wrote inputs to", inputs_dir)


if __name__ == "__main__":
    main()
