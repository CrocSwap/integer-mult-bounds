#!/usr/bin/env python3
"""Offline checker for research/pr636-family-witness-manifest-receipt.

Recomputes, from committed evidence and the local git tree at the base commit:

  A. the larger-gain pin drift identity (two committed MANIFEST copies, their
     digests, their JSON-level diff and the staged package's self-consistency);
  B. every per-PR pin verdict and retention count from the per-PR audit rows;
  C. every changed-path retention class against `git ls-tree -r <base>`;
  D. the cross-PR shared-blob counts.

Meaningful failure controls (run as part of this script): a tampered evidence
digest, an omitted row and a substituted class must each be rejected.

No network access. Standard library only.
"""
import hashlib, json, os, subprocess, sys
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parent.parent
RECEIPT = json.loads((PKG / "RECEIPT.json").read_text(encoding="utf-8"))
BASE = RECEIPT["base_main"]

def sha256(b):
    return hashlib.sha256(b).hexdigest()

def fail(msg):
    raise SystemExit("FAIL " + msg)

def git_show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        fail(f"git show {rev}:{path} unavailable: {r.stderr.decode('utf-8', 'replace')[:200]}")
    return r.stdout

def classify(path, blob_sha, main_path2sha, main_shas, main_sha2paths):
    same_path_sha = main_path2sha.get(path)
    if same_path_sha == blob_sha:
        return "same_path_identical"
    if blob_sha in main_shas:
        return "same_blob_other_path"
    if same_path_sha is not None:
        return "path_present_content_differs"
    return "not_retained"

def main_tree():
    out = git_show  # local git only
    r = subprocess.run(["git", "ls-tree", "-r", BASE], capture_output=True, text=True,
                       cwd=ROOT, encoding="utf-8")
    if r.returncode != 0:
        fail(f"git ls-tree {BASE} unavailable")
    path2sha, sha2paths = {}, {}
    for line in r.stdout.splitlines():
        meta, path = line.split("\t", 1)
        sha = meta.split()[2]
        path2sha[path] = sha
        sha2paths.setdefault(sha, []).append(path)
    return path2sha, sha2paths

def check_drift_identity(receipt):
    d = receipt["larger_gain_pin_drift"]
    a = (PKG / d["evidence_copies"]["pr569_revision"]).read_bytes()
    b = (PKG / d["evidence_copies"]["main_staged"]).read_bytes()
    if sha256(a) != d["pr569_revision_sha256"]:
        fail("pr569 manifest copy digest mismatch")
    if sha256(b) != d["main_staged_sha256"]:
        fail("staged manifest copy digest mismatch")
    if d["registered_manifest_sha256"] != d["pr569_revision_sha256"]:
        fail("registered pin is not the pr569 revision digest")
    if d["pr569_revision_sha256"] == d["main_staged_sha256"]:
        fail("no drift recorded but digests equal")
    ja, jb = json.loads(a), json.loads(b)
    diff = {k: {"pr569": ja["files"].get(k), "main_staged": jb["files"].get(k)}
            for k in sorted(set(ja["files"]) | set(jb["files"]))
            if ja["files"].get(k) != jb["files"].get(k)}
    if diff != d["differing_manifest_entries"]:
        fail(f"manifest diff mismatch: {sorted(diff)} vs {sorted(d['differing_manifest_entries'])}")
    for rel, row in d["staged_package_self_consistency"].items():
        got = sha256(git_show(BASE, "research/larger-gain/" + rel))
        if got != row["sha256"]:
            fail(f"staged {rel} digest mismatch")
        if row["matches_staged_manifest"] != (got == jb["files"][rel]):
            fail(f"staged {rel} self-consistency flag wrong")
        if row["matches_pr569_manifest"] != (got == ja["files"][rel]):
            fail(f"staged {rel} pr569 flag wrong")
    live = sha256((ROOT / "research" / "larger-gain" / "MANIFEST.json").read_bytes())
    if live != d["main_staged_sha256"]:
        fail("working-tree research/larger-gain/MANIFEST.json is not the recorded staged manifest")
    for n, row in d["live_manifest_at_recorded_heads"].items():
        if row["live_manifest_sha256"] != d["main_staged_sha256"]:
            fail(f"PR {n}: recorded live manifest digest differs from staged digest")
    return sorted(diff)

def check_per_pr(receipt, main_path2sha, main_shas, main_sha2paths):
    sets = {}
    for n, entry in receipt["per_pr"].items():
        ev = json.loads((PKG / entry["evidence_file"]).read_text(encoding="utf-8"))
        if ev["head"] != entry["head"]:
            fail(f"PR {n}: head mismatch between receipt and evidence")
        rows = ev["changed_files"]
        counts = {}
        for row in rows:
            cls = classify(row["path"], row["head_blob_sha"], main_path2sha, main_shas, main_sha2paths)
            if cls != row["class"]:
                fail(f"PR {n} {row['path']}: class {row['class']} != recomputed {cls}")
            if row["main_same_path_blob_sha"] != main_path2sha.get(row["path"]):
                fail(f"PR {n} {row['path']}: main same-path blob sha mismatch")
            counts[cls] = counts.get(cls, 0) + 1
        if counts != entry["retention_counts"]:
            fail(f"PR {n}: retention counts {counts} != {entry['retention_counts']}")
        if len(rows) != entry["changed_file_count"]:
            fail(f"PR {n}: changed-file count mismatch")
        for src, pv in entry["pin_verdict"].items():
            actual, registered = pv["actual_manifest_sha256_raw_bytes"], pv["registered_manifest_sha256"]
            if pv["pin_matches_committed_bytes"] != (actual == registered):
                fail(f"PR {n} {src}: pin verdict inconsistent with digests")
            if pv["pin_matches_normalized_bytes"] is None:
                fail(f"PR {n} {src}: missing normalized verdict")
        sets[int(n)] = {r["head_blob_sha"] for r in rows}
        if "larger_gain manifest pin" not in entry["ledger_unresolved"]:
            fail(f"PR {n}: audited ledger question not quoted")
    for pair, want in receipt["cross_pr_shared_blobs"].items():
        a, b = (int(x) for x in pair.split("-"))
        if len(sets[a] & sets[b]) != want:
            fail(f"cross-PR shared blob count mismatch for {pair}")
    return sum(entry["changed_file_count"] for entry in receipt["per_pr"].values())

def positive_fixture():
    """The classification rule itself, on synthetic trees."""
    p2s = {"a": "s1", "b": "s2"}
    shas = {"s1", "s2"}
    s2p = {"s1": ["a"], "s2": ["b"]}
    cases = [("a", "s1", "same_path_identical"), ("c", "s1", "same_blob_other_path"),
             ("a", "s9", "path_present_content_differs"), ("d", "s9", "not_retained")]
    for path, sha, want in cases:
        got = classify(path, sha, p2s, shas, s2p)
        if got != want:
            fail(f"positive fixture: {path}/{sha} -> {got}, expected {want}")

def failure_controls(receipt, main_path2sha, main_shas, main_sha2paths):
    import copy, tempfile
    # (1) tampered evidence digest must be rejected
    tampered = copy.deepcopy(receipt)
    tampered["larger_gain_pin_drift"]["main_staged_sha256"] = "0" * 64
    try:
        check_drift_identity(tampered)
    except SystemExit:
        pass
    else:
        fail("control 1: tampered staged digest was not rejected")
    # (2) substituted diff entry must be rejected
    tampered = copy.deepcopy(receipt)
    tampered["larger_gain_pin_drift"]["differing_manifest_entries"] = {"NOTICE": {"pr569": "x", "main_staged": "y"}}
    try:
        check_drift_identity(tampered)
    except SystemExit:
        pass
    else:
        fail("control 2: substituted manifest diff was not rejected")
    # (3) a dropped changed-file row must be rejected through count mismatch
    ev_path = PKG / receipt["per_pr"]["636"]["evidence_file"]
    original = ev_path.read_text(encoding="utf-8")
    ev = json.loads(original)
    ev["changed_files"] = ev["changed_files"][1:]
    ev_path.write_text(json.dumps(ev), encoding="utf-8")
    try:
        check_per_pr(receipt, main_path2sha, main_shas, main_sha2paths)
    except SystemExit:
        pass
    else:
        ev_path.write_text(original, encoding="utf-8")
        fail("control 3: omitted row was not rejected")
    ev_path.write_text(original, encoding="utf-8")
    # (4) a substituted class must be rejected
    ev = json.loads(original)
    for row in ev["changed_files"]:
        if row["class"] == "not_retained":
            row["class"] = "same_path_identical"
            break
    ev_path.write_text(json.dumps(ev), encoding="utf-8")
    try:
        check_per_pr(receipt, main_path2sha, main_shas, main_sha2paths)
    except SystemExit:
        pass
    else:
        ev_path.write_text(original, encoding="utf-8")
        fail("control 4: substituted class was not rejected")
    ev_path.write_text(original, encoding="utf-8")
    if ev_path.read_text(encoding="utf-8") != original:
        fail("control restore: evidence file not restored byte-identically")

def main():
    positive_fixture()
    main_path2sha, main_sha2paths = main_tree()
    main_shas = set(main_path2sha.values())
    diff = check_drift_identity(RECEIPT)
    total = check_per_pr(RECEIPT, main_path2sha, main_shas, main_sha2paths)
    failure_controls(RECEIPT, main_path2sha, main_shas, main_sha2paths)
    print("PASS drift identity: entries", diff)
    print("PASS per-PR pins and retention re-derived against", BASE, f"({total} changed paths)")
    print("PASS cross-PR shared-blob counts")
    print("PASS positive fixture and 4 failure controls")
    print("PASS pr636-family-witness-manifest-receipt")

if __name__ == "__main__":
    main()
