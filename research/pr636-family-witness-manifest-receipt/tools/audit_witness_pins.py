"""Audit the seven fourth100 witness-MANIFEST pin failures.

For each recorded PR head:
  1. fetch the witness verify.py and data/SPEC.json at the exact head;
  2. for every pinned source package, fetch its MANIFEST.json raw bytes and
     recompute sha256 against the registered manifest_sha256 pin;
  3. record whether the committed bytes contain CRLF and what the repository's
     text normalization would do to them;
  4. fetch every changed path's head blob sha and classify its retention in
     main at the base commit (exact git-blob identity, local git).

Writes one evidence JSON per PR plus a combined report. Stdlib only.
Usage: audit.py OUTDIR [PR_NUMBER] [BASE_WORKTREE]
"""
import base64, hashlib, json, os, subprocess, sys, time

REPO = "CrocSwap/integer-mult-bounds"
BASE = "1f7a934975e5eacaf83511c9ac870263bf095e05"
OUTDIR = sys.argv[1] if len(sys.argv) > 1 else "audit-out"
ONLY = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2].isdigit() else None
WORKTREE = sys.argv[3] if len(sys.argv) > 3 else "."

PRS = {
    636: "research/combined-cold-ends-20261013/witness635/verify.py",
    638: "research/pr637-improvement-20261013/witness637/verify.py",
    639: "research/pr638-improvement-20261013/witness638/verify.py",
    640: "research/ck-u4-improvement-20261013/witness/verify.py",
    642: "research/selective249-improvement-20261013/witness/verify.py",
    644: "research/pr643-improvement-20261013/witness/verify.py",
    646: "research/signed-root-k480/verify.py",
}

os.makedirs(OUTDIR, exist_ok=True)

def gh_json(args):
    for attempt in range(5):
        r = subprocess.run(["gh", "api"] + args, capture_output=True, text=True, encoding="utf-8")
        if r.returncode == 0:
            return json.loads(r.stdout)
        if "rate limit" in r.stderr.lower():
            time.sleep(30)
            continue
        raise RuntimeError("gh api failed: %s\n%s" % (args[:3], r.stderr[:400]))
    raise RuntimeError("gh api failed after retries: %s" % args[:3])

def contents(path, ref):
    d = gh_json([f"repos/{REPO}/contents/{path}?ref={ref}"])
    if "content" not in d:
        raise RuntimeError(f"no content for {path}@{ref}: {d.get('message')}")
    return base64.b64decode(d["content"]), d["sha"]

def pull_files(number):
    files, page = [], 1
    while True:
        batch = gh_json([f"repos/{REPO}/pulls/{number}/files?per_page=100&page={page}"])
        files.extend(batch)
        if len(batch) < 100:
            return files
        page += 1

def check_attr(path):
    r = subprocess.run(["git", "check-attr", "text", "eol", "--", path],
                       capture_output=True, text=True, cwd=WORKTREE)
    out = {}
    for line in r.stdout.splitlines():
        parts = line.rsplit(": ", 2)
        if len(parts) == 3:
            out[parts[1].strip()] = parts[2].strip()
    return out

def main_tree():
    r = subprocess.run(["git", "ls-tree", "-r", BASE], capture_output=True, text=True,
                       cwd=WORKTREE, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError("git ls-tree failed: " + r.stderr[:300])
    path2sha, sha2paths = {}, {}
    for line in r.stdout.splitlines():
        meta, path = line.split("\t", 1)
        sha = meta.split()[2]
        path2sha[path] = sha
        sha2paths.setdefault(sha, []).append(path)
    return path2sha, sha2paths

print("loading main tree at", BASE, flush=True)
main_path2sha, main_sha2paths = main_tree()
main_shas = set(main_path2sha.values())
print("main tree paths:", len(main_path2sha), flush=True)

report = {}
for number, verify_path in PRS.items():
    if ONLY and str(number) != ONLY:
        continue
    print(f"=== PR {number}", flush=True)
    pr = gh_json([f"repos/{REPO}/pulls/{number}"])
    head = pr["head"]["sha"]
    ev = {"pr": number, "title": pr["title"], "head": head,
          "base_main": BASE, "verify_path": verify_path,
          "created_at": pr["created_at"], "user": pr["user"]["login"]}

    # --- witness pin audit -------------------------------------------------
    verify_bytes, verify_sha = contents(verify_path, head)
    ev["verify_blob_sha"] = verify_sha
    ev["verify_sha256"] = hashlib.sha256(verify_bytes).hexdigest()
    ev["verify_line39"] = verify_bytes.decode("utf-8", "replace").splitlines()[38].strip()
    spec_path = verify_path.rsplit("/", 1)[0] + "/data/SPEC.json"
    spec_bytes, spec_sha = contents(spec_path, head)
    ev["spec_path"], ev["spec_blob_sha"] = spec_path, spec_sha
    spec = json.loads(spec_bytes)
    build = spec["build"]
    ev["spec_name"] = spec.get("name")
    src_root = verify_path.rsplit("/", 2)[0]  # P.parent
    p_dir = verify_path.rsplit("/", 1)[0]     # P (witness package dir)
    pin_rows = []
    for name, src in build["sources"].items():
        candidates = [f"{p_dir}/vendor/{name}", f"{src_root}/{src['dir']}",
                      f"{src_root}/vendor/{name}", f"{p_dir}/{src['dir']}"]
        rel = data = blob_sha = None
        for cand in candidates:
            try:
                data, blob_sha = contents(f"{cand}/MANIFEST.json", head)
                rel = f"{cand}/MANIFEST.json"
                break
            except RuntimeError:
                continue
        if rel is None:
            pin_rows.append({"source": name, "manifest_path": None,
                             "resolved_from_candidates": candidates,
                             "error": "MANIFEST.json not found at any candidate path"})
            print(f"  source {name}: NOT FOUND", flush=True)
            continue
        actual = hashlib.sha256(data).hexdigest()
        registered = src["manifest_sha256"]
        row = {
            "source": name, "manifest_path": rel, "manifest_blob_sha": blob_sha,
            "resolved_candidates": candidates,
            "registered_manifest_sha256": registered,
            "actual_manifest_sha256_raw_bytes": actual,
            "pin_matches_committed_bytes": actual == registered,
            "crlf_count": data.count(b"\r\n"),
            "sha256_after_crlf_to_lf": (normalized_sha := hashlib.sha256(
                data.replace(b"\r\n", b"\n")).hexdigest()),
            "pin_matches_normalized_bytes": normalized_sha == registered,
            "gitattributes": check_attr(rel),
            "full_tree": bool(src.get("full_tree")),
            "pinned_file_count": len(src.get("files", {})),
        }
        file_rows = []
        for frel, fval in src.get("files", {}).items():
            fpath = rel.rsplit("/", 1)[0] + "/" + frel
            try:
                fdata, fblob = contents(fpath, head)
            except RuntimeError:
                file_rows.append({"file": frel, "path": fpath, "error": "not found",
                                  "registered": fval})
                continue
            fraw = hashlib.sha256(fdata).hexdigest()
            fnorm = hashlib.sha256(fdata.replace(b"\r\n", b"\n")).hexdigest()
            file_rows.append({"file": frel, "path": fpath, "blob_sha": fblob,
                              "registered": fval, "raw_match": fraw == fval,
                              "norm_match": fnorm == fval, "crlf_count": fdata.count(b"\r\n")})
        row["pinned_files"] = file_rows
        pin_rows.append(row)
        print(f"  source {name}: raw_match={row['pin_matches_committed_bytes']} "
              f"norm_match={row['pin_matches_normalized_bytes']} crlf={row['crlf_count']}", flush=True)
    ev["source_pins"] = pin_rows

    # --- changed-path retention census ------------------------------------
    files = pull_files(number)
    rows = []
    counts = {"same_path_identical": 0, "same_blob_other_path": 0,
              "path_present_content_differs": 0, "not_retained": 0}
    for f in files:
        path, bsha = f["filename"], f.get("sha")
        same_path_sha = main_path2sha.get(path)
        other_paths = [p for p in main_sha2paths.get(bsha, []) if p != path]
        if same_path_sha == bsha:
            cls = "same_path_identical"
        elif bsha in main_shas:
            cls = "same_blob_other_path"
        elif same_path_sha is not None:
            cls = "path_present_content_differs"
        else:
            cls = "not_retained"
        counts[cls] += 1
        rows.append({"path": path, "status": f["status"], "head_blob_sha": bsha,
                     "bytes": f.get("changes"), "class": cls,
                     "main_same_path_blob_sha": same_path_sha,
                     "main_same_blob_other_paths": other_paths[:8],
                     "main_same_blob_other_path_count": len(other_paths)})
    ev["changed_files"] = rows
    ev["retention_counts"] = counts
    ev["changed_file_count"] = len(rows)
    print("  retention:", counts, flush=True)

    # --- byte-identity overlap with the other PRs of the set ---------------
    with open(os.path.join(OUTDIR, f"pr{number}.json"), "w", encoding="utf-8") as fh:
        json.dump(ev, fh, indent=1)
    report[number] = {k: ev[k] for k in ("head", "verify_path", "spec_name",
                                         "changed_file_count", "retention_counts")}
    report[number]["source_pin_summary"] = [
        {"source": r["source"], "raw_match": r["pin_matches_committed_bytes"],
         "norm_match": r["pin_matches_normalized_bytes"], "crlf": r["crlf_count"]}
        for r in pin_rows]

# cross-PR shared blobs
print("=== cross-PR shared blobs", flush=True)
sets = {}
for number in (report if not ONLY else {int(ONLY): None}):
    ev = json.load(open(os.path.join(OUTDIR, f"pr{number}.json"), encoding="utf-8"))
    sets[number] = {f["head_blob_sha"] for f in ev["changed_files"]}
for a in sorted(sets):
    for b in sorted(sets):
        if a < b:
            shared = len(sets[a] & sets[b])
            if shared:
                report.setdefault("cross", {})[f"{a}-{b}"] = shared
                print(f"  {a} & {b}: {shared} shared blobs", flush=True)

with open(os.path.join(OUTDIR, "report.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1)
print("WROTE", OUTDIR)
