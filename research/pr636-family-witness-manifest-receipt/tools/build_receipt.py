"""Build RECEIPT.json and evidence/ for research/pr636-family-witness-manifest-receipt.

Inputs: the seven per-PR audit records (audit-out/pr{N}.json, produced by
tools/audit_witness_pins.py), local git at the base commit, and the GitHub
contents API for the live manifest at each recorded head. Stdlib only.
"""
import base64, hashlib, json, os, subprocess, sys

WT = sys.argv[1]
AUDIT = sys.argv[2]
PKG = sys.argv[3]
BASE = "1f7a934975e5eacaf83511c9ac870263bf095e05"
PR569_REV = "897213a855b7fb8a1b8b0e552a2f5c42e6c1b326"
NUMBERS = [636, 638, 639, 640, 642, 644, 646]
REPO = "CrocSwap/integer-mult-bounds"

ev_dir = os.path.join(PKG, "evidence")
os.makedirs(ev_dir, exist_ok=True)

def git_show(rev, path):
    r = subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, cwd=WT)
    if r.returncode != 0:
        raise SystemExit(f"git show {rev}:{path} failed")
    return r.stdout

def sha256(b):
    return hashlib.sha256(b).hexdigest()

pr569 = git_show(PR569_REV, "research/larger-gain/MANIFEST.json")
staged = git_show(BASE, "research/larger-gain/MANIFEST.json")
open(os.path.join(ev_dir, "larger-gain-MANIFEST.pr569-rev.json"), "wb").write(pr569)
open(os.path.join(ev_dir, "larger-gain-MANIFEST.main-staged.json"), "wb").write(staged)

ja, jb = json.loads(pr569), json.loads(staged)
diff = {k: {"pr569": ja["files"].get(k), "main_staged": jb["files"].get(k)}
        for k in sorted(set(ja["files"]) | set(jb["files"]))
        if ja["files"].get(k) != jb["files"].get(k)}

# staged package self-consistency: do the staged files match the staged manifest?
staged_self = {}
for rel in ("NOTICE", "README.md"):
    b = git_show(BASE, "research/larger-gain/" + rel)
    staged_self[rel] = {"sha256": sha256(b),
                        "matches_staged_manifest": sha256(b) == jb["files"][rel],
                        "matches_pr569_manifest": sha256(b) == ja["files"][rel]}

# live manifest digest at each recorded head (records the base-tree state there)
live_at_head = {}
for n in NUMBERS:
    ev = json.load(open(os.path.join(AUDIT, f"pr{n}.json"), encoding="utf-8"))
    head = ev["head"]
    r = subprocess.run(["gh", "api",
        f"repos/{REPO}/contents/research/larger-gain/MANIFEST.json?ref={head}"],
        capture_output=True, text=True, encoding="utf-8")
    d = json.loads(r.stdout)
    live_at_head[str(n)] = {"head": head,
                            "live_manifest_sha256": sha256(base64.b64decode(d["content"])),
                            "live_manifest_blob_sha": d["sha"]}
    print(n, live_at_head[str(n)])

receipt = {
    "schema_version": 1,
    "name": "pr636-family-witness-manifest-receipt",
    "claim_type": "source-bound disposition receipt (finite blob-identity certificate); no kappa, no construction",
    "base_main": BASE,
    "family": {
        "description": "the seven fourth100 reconciliation entries whose contributed-package "
                       "replay fails at verify.py line 39 with 'AssertionError: larger_gain manifest pin'",
        "prs": NUMBERS,
        "audited_receipt": [
            "research/community-reconciliation-fourth100-audit/DISPOSITIONS.json",
            "research/community-reconciliation-fourth100-audit/ARCHIVE.json",
            "research/community-reconciliation-fourth100-audit/REVIEW.json",
            "docs/research/community-reconciliation-fourth100-review.md",
            "docs/research/pr-ledger.json",
        ],
    },
    "larger_gain_pin_drift": {
        "pinned_source": "larger_gain (PR569, pinned commit " + PR569_REV + ")",
        "registered_manifest_sha256": "54d67f45ad520f4a134e069336bd0ff639aaeada28d13539298e4f2655c9692d",
        "pr569_revision_sha256": sha256(pr569),
        "main_staged_sha256": sha256(staged),
        "main_staged_by_commit": "df417acd (Stage frozen PR family through 588 and initial review evidence)",
        "differing_manifest_entries": diff,
        "staged_package_self_consistency": staged_self,
        "evidence_copies": {
            "pr569_revision": "evidence/larger-gain-MANIFEST.pr569-rev.json",
            "main_staged": "evidence/larger-gain-MANIFEST.main-staged.json",
        },
        "live_manifest_at_recorded_heads": live_at_head,
    },
    "per_pr": {},
    "cross_pr_shared_blobs": {},
    "credit": {
        "authors": {
            "636/638/639/640/642/644": "vectorsss (Chi Zhao)",
            "646": "jeremydiviney (Jeremy Diviney)",
        },
        "contributors_md_entries": [
            "CONTRIBUTORS.md line 835 credits vectorsss for 636/638/639/640/642/644",
            "CONTRIBUTORS.md line 833 credits jeremydiviney for 627/646/658",
        ],
        "attribution_status": "retained; no missing predecessor attribution found for this family",
    },
    "limitations": [
        "Head-side blob identities rest on the GitHub pulls/contents APIs at the recorded head SHAs; "
        "the PR trees are not fetched into the reviewer's git.",
        "The multicold sources declare full_tree=true; their whole-tree manifests were not recomputed file by file.",
        "The seven contributed packages' full runtime replays were not executed; only the pin block "
        "(verify.py lines 36-42) and the changed-path retention census were checked.",
        "Why the fourth100 harness resolved the sources to live packages instead of the vendored "
        "copies is inferred from the recorded 'larger_gain manifest pin' assertion, not directly reproduced.",
        "Retention matching is byte identity of git blobs; equivalent-but-rewritten content is reported "
        "as not retained (path_present_content_differs was empty for all seven).",
    ],
}

for n in NUMBERS:
    ev = json.load(open(os.path.join(AUDIT, f"pr{n}.json"), encoding="utf-8"))
    rows = ev["changed_files"]
    import collections
    counts = collections.Counter(r["class"] for r in rows)
    entry = {
        "pr": n, "title": ev["title"], "head": ev["head"], "user": ev["user"],
        "created_at": ev["created_at"],
        "verify_path": ev["verify_path"], "spec_name": ev["spec_name"],
        "ledger_unresolved": "Required contributed-package replay has not completed successfully. "
                             "Latest direct evidence: ... AssertionError: larger_gain manifest pin",
        "pin_verdict": {
            row["source"]: {
                "manifest_path": row["manifest_path"],
                "registered_manifest_sha256": row.get("registered_manifest_sha256"),
                "actual_manifest_sha256_raw_bytes": row.get("actual_manifest_sha256_raw_bytes"),
                "pin_matches_committed_bytes": row.get("pin_matches_committed_bytes"),
                "pin_matches_normalized_bytes": row.get("pin_matches_normalized_bytes"),
                "crlf_count": row.get("crlf_count"),
                "pinned_files_all_raw_match": all(f.get("raw_match") for f in row.get("pinned_files", []))
                    if row.get("pinned_files") else None,
            } for row in ev["source_pins"]},
        "changed_file_count": ev["changed_file_count"],
        "retention_counts": dict(counts),
        "evidence_file": f"evidence/pr{n}-audit.json",
    }
    receipt["per_pr"][str(n)] = entry
    json.dump(ev, open(os.path.join(ev_dir, f"pr{n}-audit.json"), "w", encoding="utf-8"), indent=1)

# cross-PR shared blobs, recomputed from rows
sets = {}
for n in NUMBERS:
    ev = json.load(open(os.path.join(AUDIT, f"pr{n}.json"), encoding="utf-8"))
    sets[n] = {r["head_blob_sha"] for r in ev["changed_files"]}
for i, a in enumerate(NUMBERS):
    for b in NUMBERS[i+1:]:
        receipt["cross_pr_shared_blobs"][f"{a}-{b}"] = len(sets[a] & sets[b])

json.dump(receipt, open(os.path.join(PKG, "RECEIPT.json"), "w", encoding="utf-8"), indent=1)
print("wrote RECEIPT.json and evidence/")
